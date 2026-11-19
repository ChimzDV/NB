/**
 * NovaBridge Enterprise — Production REST API Client (js/api.js)
 * Connects the static GitHub Pages frontend (https://chimzdv.github.io/NB/)
 * to the Flask backend API with HTTPS enforcement, Idempotency-Key deduplication,
 * and zero-PII localStorage security.
 */

(function (window) {
    'use strict';

    // Default Deployment Configuration
    window.NOVABRIDGE_CONFIG = Object.assign({
        PRODUCTION_API_URL: '', // Set to your deployed HTTPS Flask API origin (e.g. 'https://api.novabridge.example.com')
        LOCAL_API_URL: 'http://127.0.0.1:5000',
        GITHUB_PAGES_ORIGIN: 'https://chimzdv.github.io',
        GITHUB_PAGES_BASE_PATH: '/NB/'
    }, window.NOVABRIDGE_CONFIG || {});

    /**
     * Security Purge: Ensure no sensitive customer PII or legacy offline queues
     * ever remain in browser localStorage or sessionStorage.
     */
    function purgeSensitiveStorage() {
        const forbiddenKeys = ['NB_PENDING_INQUIRIES', 'NB_PENDING_APPLICATIONS'];
        for (const key of forbiddenKeys) {
            try { localStorage.removeItem(key); } catch (e) {}
            try { sessionStorage.removeItem(key); } catch (e) {}
        }
    }

    purgeSensitiveStorage();

    function isLocalEnvironment() {
        const host = window.location.hostname;
        const protocol = window.location.protocol;
        return protocol === 'file:' || host === 'localhost' || host === '127.0.0.1' || host === '';
    }

    function resolveBaseUrl() {
        let candidate = '';

        if (window.NOVABRIDGE_API_URL && String(window.NOVABRIDGE_API_URL).trim() !== '') {
            candidate = String(window.NOVABRIDGE_API_URL).trim();
        } else {
            const metaTag = document.querySelector('meta[name="novabridge-api-url"]');
            if (metaTag && metaTag.content && metaTag.content.trim() !== '') {
                candidate = metaTag.content.trim();
            } else if (window.NOVABRIDGE_CONFIG && window.NOVABRIDGE_CONFIG.PRODUCTION_API_URL) {
                candidate = String(window.NOVABRIDGE_CONFIG.PRODUCTION_API_URL).trim();
            }
        }

        if (candidate) {
            return candidate.replace(/\/+$/, '');
        }

        // In local development, connect to local Flask server
        if (isLocalEnvironment()) {
            if (window.location.port === '5000' && window.location.protocol !== 'file:') {
                return '';
            }
            return window.NOVABRIDGE_CONFIG.LOCAL_API_URL.replace(/\/+$/, '');
        }

        // On remote HTTPS host (e.g. https://chimzdv.github.io) without a configured production API URL,
        // return null rather than calling a visitor's localhost.
        return null;
    }

    function generateIdempotencyKey(prefix = 'nb') {
        const rand = (window.crypto && window.crypto.randomUUID)
            ? window.crypto.randomUUID()
            : (Date.now().toString(36) + '-' + Math.random().toString(36).substring(2, 10));
        return `${prefix}-${rand}`;
    }

    async function request(endpoint, options = {}) {
        const baseUrl = resolveBaseUrl();

        if (baseUrl === null) {
            const err = new Error(
                'Production Backend API URL is not configured. Set <meta name="novabridge-api-url" content="https://your-api-domain.com"> or contact our Lusaka desk at +260 970 970 307.'
            );
            err.code = 'API_NOT_CONFIGURED';
            throw err;
        }

        // HTTPS Mixed-Content Protection
        if (window.location.protocol === 'https:' && baseUrl.startsWith('http://') && !baseUrl.includes('localhost') && !baseUrl.includes('127.0.0.1')) {
            const err = new Error('Security Error: HTTPS frontend cannot connect to an insecure HTTP backend endpoint.');
            err.code = 'INSECURE_ENDPOINT';
            throw err;
        }

        const url = `${baseUrl}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), options.timeout || 8000);

        const headers = Object.assign({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }, options.headers || {});

        if (options.idempotencyKey) {
            headers['X-Idempotency-Key'] = options.idempotencyKey;
        }

        const fetchOptions = {
            method: options.method || 'GET',
            headers: headers,
            signal: controller.signal
        };

        if (options.body) {
            const bodyObj = typeof options.body === 'object' ? Object.assign({}, options.body) : options.body;
            if (options.idempotencyKey && typeof bodyObj === 'object' && !bodyObj.idempotency_key) {
                bodyObj.idempotency_key = options.idempotencyKey;
            }
            fetchOptions.body = typeof bodyObj === 'string' ? bodyObj : JSON.stringify(bodyObj);
        }

        try {
            const response = await fetch(url, fetchOptions);
            clearTimeout(timeoutId);
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                const err = new Error(data.message || `API Error (HTTP ${response.status})`);
                err.status = response.status;
                err.payload = data;
                throw err;
            }
            return data;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                const timeoutErr = new Error('Connection to NovaBridge API timed out. Please verify backend availability and try again.');
                timeoutErr.code = 'TIMEOUT';
                throw timeoutErr;
            }
            throw error;
        }
    }

    const NovaBridgeAPI = {
        getBaseUrl: resolveBaseUrl,
        isLocalEnvironment: isLocalEnvironment,
        generateIdempotencyKey: generateIdempotencyKey,
        purgeSensitiveStorage: purgeSensitiveStorage,

        setBaseUrl: function (newUrl) {
            const clean = String(newUrl || '').trim().replace(/\/+$/, '');
            window.NOVABRIDGE_API_URL = clean;
            if (window.NOVABRIDGE_CONFIG) {
                window.NOVABRIDGE_CONFIG.PRODUCTION_API_URL = clean;
            }
        },

        checkHealth: async function () {
            return await request('/api/health', { method: 'GET', timeout: 4000 });
        },

        getSiteData: async function () {
            return await request('/api/site-data', { method: 'GET', timeout: 5000 });
        },

        calculateRepayment: async function (loanAmount, repaymentPeriod) {
            return await request('/api/calculate-repayment', {
                method: 'POST',
                body: {
                    loan_amount: parseFloat(loanAmount) || 0,
                    repayment_period: repaymentPeriod || '1_week'
                }
            });
        },

        submitInquiry: async function (inquiryData, idempotencyKey) {
            return await request('/api/inquiries', {
                method: 'POST',
                idempotencyKey: idempotencyKey || generateIdempotencyKey('inq'),
                body: {
                    full_name: inquiryData.full_name,
                    email: inquiryData.email,
                    message: inquiryData.message
                }
            });
        },

        submitLoanApplication: async function (applicationData, idempotencyKey) {
            return await request('/api/applications', {
                method: 'POST',
                idempotencyKey: idempotencyKey || generateIdempotencyKey('app'),
                body: applicationData
            });
        },

        getApplicationStatus: async function (referenceId) {
            const encoded = encodeURIComponent(String(referenceId || '').trim());
            return await request(`/api/applications/${encoded}`, { method: 'GET' });
        }
    };

    window.NovaBridgeAPI = NovaBridgeAPI;
})(window);
