/**
 * NovaBridge Enterprise — Reusable Data & UI Components (js/components.js)
 * Provides authoritative site data, dynamic DOM hydration, and notification UI.
 */

(function (window) {
    'use strict';

    const DEFAULT_SITE_DATA = {
        hero: {
            sub_title: "SECURED FINANCIAL SOLUTIONS",
            title: "NOVABRIDGE ENTERPRISE",
            description: "Empowering individuals and businesses through structured, responsible, and asset-backed financial support systems."
        },
        services: [
            {
                title: "Structured Financing",
                desc: "Evaluation-led asset-backed loans designed to meet diverse client needs with clearly defined terms.",
                img: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=800&q=80"
            },
            {
                title: "Asset Assessment",
                desc: "Careful assessment and secured frameworks that ensure mutual confidence, stability, and growth.",
                img: "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=800&q=80"
            },
            {
                title: "Financial Advisory",
                desc: "Guided by professionalism and accountability, we set new standards in how financial solutions are delivered.",
                img: "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=800&q=80"
            }
        ],
        solutions: {
            title: "Why Choose",
            highlight: "NovaBridge Enterprise",
            description: "We are a growing institution built on purpose, precision, and vision, focused on long-term relationships and sustainable growth.",
            stats: [
                { value: 100, label: "Transparency" },
                { value: 100, label: "Reliable Systems" },
                { value: 100, label: "Trusted Partnership" },
                { value: 24, label: "Professional Care" }
            ]
        },
        about: {
            sub_title: "OUR PRINCIPLES",
            title: "Trust through",
            highlight: "Innovation & Discipline",
            description_p1: "Novabridge Enterprise is a forward-thinking financial services company dedicated to providing structured and responsible asset-backed financial solutions.",
            description_p2: "Our approach is centered on careful assessment, clear agreements, and consistent follow-through, guided by integrity and professionalism.",
            image: "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1200&q=80"
        },
        contact: {
            title: "Request a",
            highlight: "call back",
            sub_title: "CONNECT WITH OUR LUSAKA OFFICE FOR SECURED ADVISORY",
            email: "info.novabridge@gmail.com",
            location: "Lusaka, Zambia",
            phones: ["+260 970 970 307", "076 083 1392"]
        },
        rates: {
            "1_week": { label: "1 Week", rate: 0.15, percent: 15 },
            "2_weeks": { label: "2 Weeks", rate: 0.20, percent: 20 },
            "3_weeks": { label: "3 Weeks", rate: 0.25, percent: 25 },
            "4_weeks": { label: "4 Weeks", rate: 0.30, percent: 30 }
        },
        footer: {
            name: "NovaBridge Enterprise",
            company_desc: "A forward-thinking financial services company committed to setting a new standard in structured and responsible financial support systems.",
            useful_links: ["Integrity", "Discipline", "Trust", "Innovation"],
            additional_pages: ["Our Approach", "Vision & Mission", "Quick Support", "Contact Us", "Privacy Policy"],
            copyright: "Copyright © 2026 NovaBridge. - Design: ChimzDv"
        }
    };

    function getNestedValue(obj, path) {
        return String(path || '').split('.').reduce((acc, part) => (acc && acc[part] !== undefined ? acc[part] : undefined), obj);
    }

    function ensureToastContainer() {
        let container = document.getElementById('nbToastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'nbToastContainer';
            container.className = 'nb-toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    const NovaBridgeComponents = {
        siteData: DEFAULT_SITE_DATA,

        hydrateFromData: function (data) {
            const activeData = data || this.siteData;
            this.siteData = activeData;

            // 1. Text bindings
            document.querySelectorAll('[data-nb-bind]').forEach(el => {
                const key = el.getAttribute('data-nb-bind');
                const val = getNestedValue(activeData, key);
                if (val !== undefined && val !== null) {
                    el.textContent = Array.isArray(val) ? val.join(' / ') : String(val);
                }
            });

            // 2. Mailto & Tel href bindings
            document.querySelectorAll('[data-nb-href-mailto]').forEach(el => {
                const key = el.getAttribute('data-nb-href-mailto');
                const val = getNestedValue(activeData, key);
                if (val) el.setAttribute('href', `mailto:${val}`);
            });

            document.querySelectorAll('[data-nb-href-tel]').forEach(el => {
                const key = el.getAttribute('data-nb-href-tel');
                const val = getNestedValue(activeData, key);
                if (val) el.setAttribute('href', `tel:${val}`);
            });

            // 3. Bento Card Background Image bindings
            document.querySelectorAll('[data-nb-bg]').forEach(el => {
                const key = el.getAttribute('data-nb-bg');
                const imgUrl = getNestedValue(activeData, key);
                const grad = el.getAttribute('data-nb-gradient') || 'linear-gradient(135deg, rgba(6, 12, 22, 0.9) 0%, rgba(3, 7, 14, 0.96) 100%)';
                if (imgUrl) {
                    el.style.backgroundImage = `${grad}, url('${imgUrl}')`;
                }
            });

            // 4. Footer Useful Links loop hydration
            const usefulLinksList = document.getElementById('footerUsefulLinks');
            if (usefulLinksList && activeData.footer && Array.isArray(activeData.footer.useful_links)) {
                usefulLinksList.innerHTML = activeData.footer.useful_links.map(link => `
                    <li class="mb-2">
                        <a href="#about" class="footer-nav-link d-inline-flex align-items-center gap-2">
                            <i class="bi bi-chevron-right smaller text-emerald"></i>
                            <span>${link}</span>
                        </a>
                    </li>
                `).join('');
            }
        },

        showNotification: function ({ title, message, referenceId, type = 'success', duration = 7000 }) {
            const container = ensureToastContainer();
            const toast = document.createElement('div');
            toast.className = `nb-toast ${type === 'error' ? 'nb-toast-error' : ''}`;

            const iconClass = type === 'error'
                ? 'bi-exclamation-triangle-fill text-danger'
                : 'bi-shield-check text-emerald';

            let refHtml = '';
            if (referenceId) {
                refHtml = `<div class="nb-toast-ref"><i class="bi bi-hash me-1"></i>REF: ${referenceId}</div>`;
            }

            toast.innerHTML = `
                <div class="nb-toast-header">
                    <div class="d-flex align-items-center gap-2">
                        <i class="bi ${iconClass}"></i>
                        <span class="nb-toast-title">${title || 'NOVABRIDGE PROTOCOL'}</span>
                    </div>
                    <button type="button" class="btn-close btn-close-white" style="font-size: 0.65rem;" aria-label="Close"></button>
                </div>
                <div class="small text-secondary">${message || ''}</div>
                ${refHtml}
            `;

            container.appendChild(toast);

            requestAnimationFrame(() => {
                toast.classList.add('show');
            });

            const closeBtn = toast.querySelector('.btn-close');
            const dismiss = () => {
                toast.classList.remove('show');
                setTimeout(() => {
                    if (toast.parentNode) toast.parentNode.removeChild(toast);
                }, 350);
            };

            if (closeBtn) closeBtn.addEventListener('click', dismiss);
            if (duration > 0) setTimeout(dismiss, duration);
        }
    };

    window.NovaBridgeComponents = NovaBridgeComponents;
})(window);
