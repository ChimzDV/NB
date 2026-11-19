/**
 * NovaBridge Enterprise — Main Interactive Engine (js/main.js)
 * Handles navigation, ScrollSpy, HUD physics, calculators, rate deep-links,
 * idempotent API form submissions, and zero-PII storage security.
 */

document.addEventListener('DOMContentLoaded', () => {
    'use strict';

    const navbar = document.querySelector('.navbar');
    const navCollapse = document.getElementById('navbarNav');

    // 1. Purge any legacy sensitive storage & hydrate site data from backend if configured/reachable
    if (window.NovaBridgeAPI) {
        window.NovaBridgeAPI.purgeSensitiveStorage();
    }

    if (window.NovaBridgeAPI && window.NovaBridgeComponents) {
        if (window.NovaBridgeAPI.getBaseUrl() !== null) {
            window.NovaBridgeAPI.getSiteData()
                .then(response => {
                    if (response && response.status === 'ok' && response.data) {
                        window.NovaBridgeComponents.hydrateFromData(response.data);
                    }
                })
                .catch(() => {
                    window.NovaBridgeComponents.hydrateFromData();
                });
        } else {
            window.NovaBridgeComponents.hydrateFromData();
        }
    }

    // 2. Navigation glass & ScrollSpy active link highlighter
    const trackedSections = Array.from(document.querySelectorAll('header[id], section[id]'));
    const navSectionLinks = Array.from(document.querySelectorAll('.navbar-nav .nav-link[href^="#"]'));

    const updateNavbarAndScrollSpy = () => {
        if (navbar) {
            if (window.scrollY > 30) {
                navbar.classList.add('scrolled', 'navbar-glass-active');
            } else {
                navbar.classList.remove('scrolled', 'navbar-glass-active');
            }
        }

        if (trackedSections.length > 0 && navSectionLinks.length > 0) {
            const scrollPos = window.scrollY + (navbar ? navbar.offsetHeight + 80 : 150);
            let currentSectionId = trackedSections[0].id;

            for (const sec of trackedSections) {
                if (sec.offsetTop <= scrollPos) {
                    currentSectionId = sec.id;
                }
            }

            navSectionLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href === `#${currentSectionId}`) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }
    };

    window.addEventListener('scroll', updateNavbarAndScrollSpy, { passive: true });
    updateNavbarAndScrollSpy();

    // 3. Mobile Navbar: Auto-close collapse on link tap
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link, .nav-cta-btn');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (navCollapse && navCollapse.classList.contains('show')) {
                if (typeof bootstrap !== 'undefined' && bootstrap.Collapse) {
                    const bsCollapse = bootstrap.Collapse.getInstance(navCollapse) || new bootstrap.Collapse(navCollapse, { toggle: false });
                    bsCollapse.hide();
                } else {
                    navCollapse.classList.remove('show');
                }
            }
        });
    });

    // 4. Telemetry and Numerical Counter on Viewport Intersection
    const counters = document.querySelectorAll('.counter');
    if ('IntersectionObserver' in window) {
        const countObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = +counter.getAttribute('data-target') || 0;
                    const duration = 1600;
                    const startTime = performance.now();

                    const animateCount = (now) => {
                        const elapsed = now - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        const easeOut = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
                        const currentVal = Math.floor(easeOut * target);
                        counter.innerText = currentVal;

                        if (progress < 1) {
                            requestAnimationFrame(animateCount);
                        } else {
                            counter.innerText = target;
                        }
                    };

                    requestAnimationFrame(animateCount);
                    observer.unobserve(counter);
                }
            });
        }, { threshold: 0.2 });

        counters.forEach(counter => countObserver.observe(counter));
    } else {
        counters.forEach(counter => {
            counter.innerText = counter.getAttribute('data-target') || '0';
        });
    }

    // 5. Subtle Interactive Holographic HUD Tilt (Desktop Mouse Only, disabled on Touch)
    const isTouchDevice = () => {
        return ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (window.innerWidth < 992);
    };

    if (!isTouchDevice()) {
        const hudCards = document.querySelectorAll('.hud-main-terminal, .hud-telemetry-window, .bento-card');
        hudCards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                const rotateX = (-y / rect.height) * 4;
                const rotateY = (x / rect.width) * 4;
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });
    }

    // 6. Smooth Anchor Scrolling & Prevention of href="#" Page Jumps
    document.addEventListener('click', function (e) {
        const anchor = e.target.closest('a[href^="#"]');
        if (!anchor) return;
        const targetId = anchor.getAttribute('href');

        if (!targetId || targetId === '#') {
            e.preventDefault();
            if (anchor.classList.contains('badge-gold-outline') && window.NovaBridgeComponents) {
                window.NovaBridgeComponents.showNotification({
                    title: 'NovaBridge Mobile App',
                    message: 'Enterprise mobile builds (iOS & Android) are provisioned upon facility onboarding. You may apply online immediately.',
                    type: 'success',
                    duration: 5000
                });
            }
            return;
        }

        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            e.preventDefault();
            const navHeight = navbar ? navbar.offsetHeight : 70;
            const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
            const offsetPosition = elementPosition - navHeight + 6;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });

    // 7. Rate Card Hover, Touch Feedback & Deep-Linking to apply.html?period=...
    const rateCards = document.querySelectorAll('.replica-rate-card');
    rateCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.borderColor = 'rgba(0, 232, 148, 0.65)';
            card.style.boxShadow = '0 12px 36px rgba(0, 0, 0, 0.7), 0 0 24px rgba(0, 232, 148, 0.25)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.borderColor = '';
            card.style.boxShadow = '';
        });

        const navigateToRate = () => {
            const period = card.getAttribute('data-period');
            if (period) {
                window.location.href = `apply.html?period=${encodeURIComponent(period)}`;
            }
        };

        card.addEventListener('click', navigateToRate);
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                navigateToRate();
            }
        });
    });

    const interactiveTiles = document.querySelectorAll('.replica-rate-card, .logo-symbol-tile');
    interactiveTiles.forEach(tile => {
        tile.addEventListener('touchstart', () => {
            tile.style.borderColor = 'rgba(0, 232, 148, 0.75)';
        }, { passive: true });
        tile.addEventListener('touchend', () => {
            setTimeout(() => {
                tile.style.borderColor = '';
            }, 300);
        }, { passive: true });
    });

    // 8. Private Inquiry Terminal Form Submission (index.html #contact)
    const inquiryForm = document.getElementById('contactInquiryForm');
    if (inquiryForm) {
        let inquirySubmitting = false;
        let currentInquiryIdemKey = window.NovaBridgeAPI ? window.NovaBridgeAPI.generateIdempotencyKey('inq') : null;

        inquiryForm.addEventListener('input', () => {
            if (window.NovaBridgeAPI) {
                currentInquiryIdemKey = window.NovaBridgeAPI.generateIdempotencyKey('inq');
            }
        });

        inquiryForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            if (inquirySubmitting) return;

            const nameInput = document.getElementById('inquiryFullName');
            const emailInput = document.getElementById('inquiryEmail');
            const messageInput = document.getElementById('inquiryMessage');
            const submitBtn = this.querySelector('button[type="submit"]');

            const fullName = nameInput ? nameInput.value.trim() : '';
            const email = emailInput ? emailInput.value.trim() : '';
            const message = messageInput ? messageInput.value.trim() : '';

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (fullName.length < 2 || !emailRegex.test(email) || message.length < 5) {
                if (window.NovaBridgeComponents) {
                    window.NovaBridgeComponents.showNotification({
                        title: 'Validation Required',
                        message: 'Please enter a valid Full Legal Name, Corporate Email Address, and Inquiry Details (minimum 5 characters).',
                        type: 'error'
                    });
                }
                return;
            }

            inquirySubmitting = true;
            const originalBtnHtml = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>ENCRYPTING & TRANSMITTING...';
            }

            try {
                const res = await window.NovaBridgeAPI.submitInquiry({
                    full_name: fullName,
                    email: email,
                    message: message
                }, currentInquiryIdemKey);

                window.NovaBridgeComponents.showNotification({
                    title: res.duplicate ? 'Inquiry Already Logged' : 'Inquiry Transmitted',
                    message: res.message || 'Your private inquiry has been logged with our Lusaka advisory desk.',
                    referenceId: res.reference_id,
                    type: 'success'
                });

                inquiryForm.reset();
                currentInquiryIdemKey = window.NovaBridgeAPI.generateIdempotencyKey('inq');
            } catch (err) {
                // Do NOT store customer PII in localStorage and do NOT wipe the form on error.
                window.NovaBridgeComponents.showNotification({
                    title: err.status ? 'Submission Error' : 'Backend Service Unreachable',
                    message: err.status
                        ? err.message
                        : 'Unable to reach the NovaBridge API server. Your typed information has been kept on screen so you can retry or contact our Lusaka desk at +260 970 970 307.',
                    type: 'error',
                    duration: 9000
                });
            } finally {
                inquirySubmitting = false;
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnHtml;
                }
            }
        });
    }

    // 9. Loan Application Page Logic (apply.html #loanApplicationForm)
    const loanForm = document.getElementById('loanApplicationForm');
    if (loanForm) {
        let appSubmitting = false;
        let currentAppIdemKey = window.NovaBridgeAPI ? window.NovaBridgeAPI.generateIdempotencyKey('app') : null;

        loanForm.addEventListener('input', () => {
            if (window.NovaBridgeAPI) {
                currentAppIdemKey = window.NovaBridgeAPI.generateIdempotencyKey('app');
            }
        });

        // 9a. Proof of Ownership Switch Toggle
        const proofSwitch = document.getElementById('proofSwitch');
        const proofLabel = proofSwitch ? proofSwitch.nextElementSibling : null;

        if (proofSwitch && proofLabel) {
            proofSwitch.addEventListener('change', function () {
                proofLabel.textContent = this.checked ? 'Yes, I have proof' : "No, I don't have proof";
            });
        }

        // 9b. Employment Status Dynamic Fields
        const employmentRadios = document.querySelectorAll('input[name="employment_status"]');
        const employerNameRow = document.getElementById('employerNameRow');
        const employerNameLabel = document.getElementById('employerNameLabel');
        const employerNameInput = document.getElementById('employerNameInput');

        function updateEmploymentFields() {
            const checkedRadio = document.querySelector('input[name="employment_status"]:checked');
            if (!checkedRadio || !employerNameRow) return;
            const selected = checkedRadio.value;

            if (selected === 'employed') {
                employerNameRow.style.display = 'block';
                if (employerNameLabel) employerNameLabel.textContent = 'Employer Name';
                if (employerNameInput) employerNameInput.placeholder = 'Company Name';
            } else if (selected === 'business-owner') {
                employerNameRow.style.display = 'block';
                if (employerNameLabel) employerNameLabel.textContent = 'Business Name';
                if (employerNameInput) employerNameInput.placeholder = 'Your Registered Business Name';
            } else if (selected === 'self-employed') {
                employerNameRow.style.display = 'none';
                if (employerNameInput) employerNameInput.value = '';
            }
        }

        employmentRadios.forEach(radio => {
            radio.addEventListener('change', updateEmploymentFields);
        });
        updateEmploymentFields();

        // 9c. Repayment Calculation Logic
        const loanAmountInput = document.getElementById('loanAmount');
        const repaymentRadios = document.querySelectorAll('input[name="repayment_period"]');
        const totalRepaymentDisplay = document.getElementById('totalRepayment');
        const interestBreakdownDisplay = document.getElementById('interestBreakdown');

        function calculateRepayment() {
            if (!loanAmountInput || !totalRepaymentDisplay || !interestBreakdownDisplay) return;
            const amount = parseFloat(loanAmountInput.value) || 0;
            const selectedRadio = document.querySelector('input[name="repayment_period"]:checked');
            const rate = selectedRadio ? (parseFloat(selectedRadio.dataset.rate) || 0) : 0;
            const periodKey = selectedRadio ? selectedRadio.value : '1_week';

            const total = amount + (amount * rate);
            const interestPercent = Math.round(rate * 100);

            totalRepaymentDisplay.textContent = `ZMW ${total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            interestBreakdownDisplay.textContent = `Incl. ${interestPercent}% interest`;

            if (amount > 0 && window.NovaBridgeAPI && window.NovaBridgeAPI.getBaseUrl() !== null) {
                window.NovaBridgeAPI.calculateRepayment(amount, periodKey)
                    .then(res => {
                        if (res && res.status === 'ok' && res.calculation) {
                            const srvTotal = Number(res.calculation.total_repayment);
                            totalRepaymentDisplay.textContent = `ZMW ${srvTotal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                            interestBreakdownDisplay.textContent = `Incl. ${res.calculation.interest_percent}% interest`;
                        }
                    })
                    .catch(() => {});
            }
        }

        // Pre-select repayment period from URL query string (?period=1_week|2_weeks|3_weeks|4_weeks)
        const urlParams = new URLSearchParams(window.location.search);
        const preselectedPeriod = urlParams.get('period');
        if (preselectedPeriod) {
            const matchingRadio = document.querySelector(`input[name="repayment_period"][value="${preselectedPeriod}"]`);
            if (matchingRadio) {
                matchingRadio.checked = true;
            }
        }

        if (loanAmountInput) {
            loanAmountInput.addEventListener('input', calculateRepayment);
        }
        repaymentRadios.forEach(radio => {
            radio.addEventListener('change', calculateRepayment);
        });
        calculateRepayment();

        // 9d. Form Submission to Flask Backend API (/api/applications)
        loanForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            if (appSubmitting) return;

            const submitBtn = this.querySelector('.btn-submit-application');
            const originalText = submitBtn ? submitBtn.textContent : 'Submit Loan Application';

            const getVal = (id) => {
                const el = document.getElementById(id);
                return el ? el.value.trim() : '';
            };

            const selectedEmp = document.querySelector('input[name="employment_status"]:checked');
            const selectedPeriod = document.querySelector('input[name="repayment_period"]:checked');
            const empStatus = selectedEmp ? selectedEmp.value : 'employed';

            const payload = {
                full_name: getVal('applicantFullName'),
                nrc_id: getVal('applicantNrcId'),
                phone: getVal('applicantPhone'),
                email: getVal('applicantEmail'),
                residential_address: getVal('applicantAddress'),
                next_of_kin_name: getVal('applicantNokName'),
                next_of_kin_phone: getVal('applicantNokPhone'),
                employment_status: empStatus,
                employer_or_business_name: empStatus === 'self-employed' ? '' : getVal('employerNameInput'),
                monthly_income: parseFloat(getVal('monthlyIncomeInput')) || 0,
                loan_amount: parseFloat(getVal('loanAmount')) || 0,
                purpose: getVal('loanPurposeInput'),
                repayment_period: selectedPeriod ? selectedPeriod.value : '1_week',
                asset_description: getVal('assetDescriptionInput'),
                estimated_asset_value: parseFloat(getVal('estimatedAssetValueInput')) || 0,
                proof_of_ownership: proofSwitch ? proofSwitch.checked : true
            };

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (payload.full_name.length < 2 || payload.nrc_id.length < 4 || payload.phone.length < 7 || !emailRegex.test(payload.email) || payload.loan_amount <= 0) {
                if (window.NovaBridgeComponents) {
                    window.NovaBridgeComponents.showNotification({
                        title: 'Validation Required',
                        message: 'Please verify your Full Name, NRC/ID Number, Phone Number, Email Address, and a Loan Amount greater than ZMW 0.',
                        type: 'error'
                    });
                }
                return;
            }

            appSubmitting = true;
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>SUBMITTING...';
            }

            const confirmBox = document.getElementById('applicationConfirmationBox');

            try {
                const res = await window.NovaBridgeAPI.submitLoanApplication(payload, currentAppIdemKey);

                window.NovaBridgeComponents.showNotification({
                    title: res.duplicate ? 'Application Already Registered' : 'Application Registered',
                    message: `${res.message} Total Repayment: ZMW ${Number(res.summary.total_repayment).toLocaleString(undefined, { minimumFractionDigits: 2 })}.`,
                    referenceId: res.reference_id,
                    type: 'success',
                    duration: 9000
                });

                if (confirmBox) {
                    document.getElementById('confirmMessage').textContent = `${res.message} Total Repayment: ZMW ${Number(res.summary.total_repayment).toLocaleString(undefined, { minimumFractionDigits: 2 })}.`;
                    document.getElementById('confirmReferenceId').textContent = res.reference_id;
                    document.getElementById('confirmStatusBadge').textContent = res.summary.application_status;
                    confirmBox.classList.add('active');
                }

                loanForm.reset();
                if (proofLabel) proofLabel.textContent = 'Yes, I have proof';
                updateEmploymentFields();
                calculateRepayment();
                currentAppIdemKey = window.NovaBridgeAPI.generateIdempotencyKey('app');
            } catch (err) {
                // Security: Never store sensitive PII (NRC/ID, income, address, collateral) in localStorage.
                // Keep form values intact on screen so the applicant can retry.
                window.NovaBridgeComponents.showNotification({
                    title: err.status ? 'Application Error' : 'Backend Service Unreachable',
                    message: err.status
                        ? err.message
                        : 'Unable to reach the NovaBridge underwriting server. Your application details have been kept on screen (never stored in insecure browser storage) so you can retry or contact our Lusaka desk at +260 970 970 307.',
                    type: 'error',
                    duration: 9000
                });
            } finally {
                appSubmitting = false;
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            }
        });
    }
});
