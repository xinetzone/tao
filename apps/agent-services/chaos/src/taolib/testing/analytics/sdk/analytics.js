/**
 * TaoAnalytics - 轻量级用户行为分析 SDK
 *
 * 使用方式:
 *   <script src="https://your-server/sdk/analytics.js"></script>
 *   <script>
 *     TaoAnalytics.init({
 *       apiUrl: 'https://your-server',
 *       appId: 'your-app-id',
 *       apiKey: 'optional-api-key'
 *     });
 *   </script>
 *
 * 手动追踪:
 *   TaoAnalytics.track('custom', { key: 'value' });
 *   TaoAnalytics.trackFeature('dark-mode-toggle', 'settings');
 *   TaoAnalytics.identify('user-123');
 *   TaoAnalytics.flush();
 *
 * 自动追踪 data 属性:
 *   <button data-track-feature="save-btn" data-track-category="editor">Save</button>
 *   <section data-track-section="hero">...</section>
 */
(function (window) {
    'use strict';

    var SDK_VERSION = '0.1.0';
    var SESSION_KEY = '_tao_sid';
    var SESSION_TS_KEY = '_tao_sts';
    var USER_KEY = '_tao_uid';
    var SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes
    var FLUSH_INTERVAL = 5000; // 5 seconds
    var BATCH_SIZE = 20;

    // --- Utilities ---

    function generateId() {
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
            return crypto.randomUUID();
        }
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = (Math.random() * 16) | 0;
            var v = c === 'x' ? r : (r & 0x3) | 0x8;
            return v.toString(16);
        });
    }

    function getTimestamp() {
        return new Date().toISOString();
    }

    function getDeviceType() {
        var ua = navigator.userAgent;
        if (/tablet|ipad|playbook|silk/i.test(ua)) return 'tablet';
        if (/mobile|iphone|ipod|android|blackberry|opera mini|iemobile/i.test(ua)) return 'mobile';
        return 'desktop';
    }

    function getCssSelector(el) {
        if (!el || el === document.body) return 'body';
        if (el.id) return '#' + el.id;
        var path = [];
        while (el && el !== document.body) {
            var tag = el.tagName.toLowerCase();
            if (el.id) {
                path.unshift('#' + el.id);
                break;
            }
            if (el.className && typeof el.className === 'string') {
                var cls = el.className.trim().split(/\s+/).slice(0, 2).join('.');
                if (cls) tag += '.' + cls;
            }
            path.unshift(tag);
            el = el.parentElement;
        }
        return path.join(' > ');
    }

    function getElementText(el) {
        var text = (el.innerText || el.textContent || '').trim();
        return text.substring(0, 100);
    }

    // --- Session Management ---

    function getOrCreateSession() {
        var sid = null;
        var lastTs = null;
        try {
            sid = localStorage.getItem(SESSION_KEY);
            lastTs = localStorage.getItem(SESSION_TS_KEY);
        } catch (e) { /* localStorage unavailable */ }

        var now = Date.now();
        if (sid && lastTs && (now - parseInt(lastTs, 10)) < SESSION_TIMEOUT) {
            try { localStorage.setItem(SESSION_TS_KEY, String(now)); } catch (e) { }
            return sid;
        }

        // New session
        sid = generateId();
        try {
            localStorage.setItem(SESSION_KEY, sid);
            localStorage.setItem(SESSION_TS_KEY, String(now));
        } catch (e) { }
        return sid;
    }

    function getUserId() {
        try { return localStorage.getItem(USER_KEY); } catch (e) { return null; }
    }

    // --- Core ---

    var config = null;
    var queue = [];
    var flushTimer = null;
    var sessionId = null;
    var sectionObserver = null;
    var sectionTimers = {};

    function buildBaseEvent(eventType, metadata) {
        sessionId = getOrCreateSession();
        return {
            event_type: eventType,
            app_id: config.appId,
            session_id: sessionId,
            user_id: getUserId(),
            timestamp: getTimestamp(),
            page_url: window.location.pathname + window.location.search,
            page_title: document.title,
            referrer: document.referrer || null,
            device_type: getDeviceType(),
            user_agent: navigator.userAgent,
            screen_width: window.screen.width,
            screen_height: window.screen.height,
            metadata: metadata || {}
        };
    }

    function enqueue(event) {
        queue.push(event);
        if (queue.length >= BATCH_SIZE) {
            flush();
        }
    }

    function flush() {
        if (queue.length === 0) return;

        var events = queue.splice(0, queue.length);
        var payload = JSON.stringify({ events: events });
        var url = config.apiUrl + '/api/v1/events/batch';

        // Try sendBeacon first for reliability, fallback to fetch
        var sent = false;
        if (navigator.sendBeacon) {
            var blob = new Blob([payload], { type: 'application/json' });
            sent = navigator.sendBeacon(url, blob);
        }

        if (!sent) {
            var headers = { 'Content-Type': 'application/json' };
            if (config.apiKey) {
                headers['X-API-Key'] = config.apiKey;
            }
            fetch(url, {
                method: 'POST',
                headers: headers,
                body: payload,
                keepalive: true
            }).catch(function () { /* silently fail */ });
        }
    }

    // --- Auto-Tracking: Page Views ---

    function trackPageView() {
        enqueue(buildBaseEvent('page_view'));
    }

    function setupPageViewTracking() {
        // Patch pushState and replaceState
        var origPush = history.pushState;
        var origReplace = history.replaceState;

        history.pushState = function () {
            origPush.apply(this, arguments);
            trackPageView();
        };
        history.replaceState = function () {
            origReplace.apply(this, arguments);
            trackPageView();
        };

        window.addEventListener('popstate', function () {
            trackPageView();
        });

        // Initial page view
        trackPageView();
    }

    // --- Auto-Tracking: Clicks ---

    function setupClickTracking() {
        document.addEventListener('click', function (e) {
            var target = e.target;

            // Walk up to find the nearest trackable element
            var el = target;
            var featureName = null;
            var featureCategory = null;
            while (el && el !== document.body) {
                if (el.dataset && el.dataset.trackFeature) {
                    featureName = el.dataset.trackFeature;
                    featureCategory = el.dataset.trackCategory || '';
                    break;
                }
                el = el.parentElement;
            }

            // Track feature use if data-track-feature found
            if (featureName) {
                enqueue(buildBaseEvent('feature_use', {
                    feature_name: featureName,
                    feature_category: featureCategory,
                    element_selector: getCssSelector(el),
                    element_text: getElementText(el)
                }));
                return;
            }

            // Track click on interactive elements
            var tagName = target.tagName.toLowerCase();
            if (tagName === 'a' || tagName === 'button' || tagName === 'input' ||
                target.getAttribute('role') === 'button' || target.onclick) {
                enqueue(buildBaseEvent('click', {
                    element_selector: getCssSelector(target),
                    element_text: getElementText(target),
                    element_id: target.id || null,
                    element_tag: tagName,
                    click_x: e.clientX,
                    click_y: e.clientY
                }));
            }
        }, true);
    }

    // --- Auto-Tracking: Section Time ---

    function setupSectionTracking() {
        if (typeof IntersectionObserver === 'undefined') return;

        sectionObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                var sectionId = entry.target.dataset.trackSection;
                if (!sectionId) return;

                if (entry.isIntersecting) {
                    sectionTimers[sectionId] = Date.now();
                } else if (sectionTimers[sectionId]) {
                    var duration = Date.now() - sectionTimers[sectionId];
                    delete sectionTimers[sectionId];
                    if (duration > 500) { // Only track if > 500ms
                        enqueue(buildBaseEvent('time_on_section', {
                            section_id: sectionId,
                            duration_ms: duration
                        }));
                    }
                }
            });
        }, { threshold: 0.5 });

        // Observe existing sections
        document.querySelectorAll('[data-track-section]').forEach(function (el) {
            sectionObserver.observe(el);
        });

        // Observe dynamically added sections via MutationObserver
        if (typeof MutationObserver !== 'undefined') {
            var mutationObserver = new MutationObserver(function (mutations) {
                mutations.forEach(function (mutation) {
                    mutation.addedNodes.forEach(function (node) {
                        if (node.nodeType === 1) {
                            if (node.dataset && node.dataset.trackSection) {
                                sectionObserver.observe(node);
                            }
                            if (node.querySelectorAll) {
                                node.querySelectorAll('[data-track-section]').forEach(function (el) {
                                    sectionObserver.observe(el);
                                });
                            }
                        }
                    });
                });
            });
            mutationObserver.observe(document.body, { childList: true, subtree: true });
        }
    }

    // --- Session Events ---

    function setupSessionTracking() {
        // Session start
        enqueue(buildBaseEvent('session_start'));

        // Session end on page hide/unload
        function onSessionEnd() {
            // Flush remaining section timers
            Object.keys(sectionTimers).forEach(function (sectionId) {
                var duration = Date.now() - sectionTimers[sectionId];
                if (duration > 500) {
                    enqueue(buildBaseEvent('time_on_section', {
                        section_id: sectionId,
                        duration_ms: duration
                    }));
                }
            });
            sectionTimers = {};

            enqueue(buildBaseEvent('session_end'));
            flush();
        }

        document.addEventListener('visibilitychange', function () {
            if (document.visibilityState === 'hidden') {
                onSessionEnd();
            }
        });

        window.addEventListener('beforeunload', function () {
            onSessionEnd();
        });
    }

    // --- Navigation Tracking ---

    function setupNavigationTracking() {
        var lastPage = window.location.pathname + window.location.search;

        var origPush = history.pushState;
        history.pushState = function () {
            var fromPage = lastPage;
            origPush.apply(this, arguments);
            var toPage = window.location.pathname + window.location.search;
            if (fromPage !== toPage) {
                enqueue(buildBaseEvent('navigation', {
                    from_page: fromPage,
                    to_page: toPage
                }));
                lastPage = toPage;
            }
        };

        window.addEventListener('popstate', function () {
            var fromPage = lastPage;
            var toPage = window.location.pathname + window.location.search;
            if (fromPage !== toPage) {
                enqueue(buildBaseEvent('navigation', {
                    from_page: fromPage,
                    to_page: toPage
                }));
                lastPage = toPage;
            }
        });
    }

    // --- Public API ---

    var TaoAnalytics = {
        /**
         * Initialize the SDK.
         * @param {Object} options - { apiUrl, appId, apiKey?, flushInterval?, batchSize? }
         */
        init: function (options) {
            if (!options || !options.apiUrl || !options.appId) {
                console.error('[TaoAnalytics] apiUrl and appId are required');
                return;
            }

            config = {
                apiUrl: options.apiUrl.replace(/\/$/, ''),
                appId: options.appId,
                apiKey: options.apiKey || null
            };

            FLUSH_INTERVAL = options.flushInterval || FLUSH_INTERVAL;
            BATCH_SIZE = options.batchSize || BATCH_SIZE;

            sessionId = getOrCreateSession();

            // Setup auto-tracking
            setupPageViewTracking();
            setupClickTracking();
            setupSectionTracking();
            setupSessionTracking();
            setupNavigationTracking();

            // Periodic flush
            flushTimer = setInterval(flush, FLUSH_INTERVAL);
        },

        /**
         * Track a custom event.
         * @param {string} eventType - Event type
         * @param {Object} metadata - Additional data
         */
        track: function (eventType, metadata) {
            if (!config) { console.warn('[TaoAnalytics] SDK not initialized'); return; }
            enqueue(buildBaseEvent(eventType, metadata));
        },

        /**
         * Track feature usage.
         * @param {string} featureName - Feature name
         * @param {string} category - Feature category
         */
        trackFeature: function (featureName, category) {
            if (!config) { console.warn('[TaoAnalytics] SDK not initialized'); return; }
            enqueue(buildBaseEvent('feature_use', {
                feature_name: featureName,
                feature_category: category || ''
            }));
        },

        /**
         * Associate a user ID with the current session.
         * @param {string} userId - User ID
         */
        identify: function (userId) {
            if (!userId) return;
            try { localStorage.setItem(USER_KEY, userId); } catch (e) { }
        },

        /**
         * Force flush queued events.
         */
        flush: function () {
            flush();
        },

        /** SDK version */
        version: SDK_VERSION
    };

    // Export global
    window.TaoAnalytics = TaoAnalytics;

})(window);
