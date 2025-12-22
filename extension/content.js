/**
 * Multi-Check Pro: Funda Content Script
 * 
 * This script runs in the context of the Funda.nl page and has access to the DOM.
 */

console.log("🏠 Multi-Check Pro: Ready to extract data");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "ping") {
        sendResponse({ status: "ready" });
        return true;
    }

    const logs = [];
    const log = (msg) => {
        const entry = `[${new Date().toLocaleTimeString()}] ${msg}`;
        console.log("🏠 Multi-Check Pro:", entry);
        logs.push(entry);
    };

    try {
        log(`Actie gestart: ${request.action}`);
        if (request.action === "extract_all") {
            const data = extractListingData(log);
            const photos = data.photos; // Already extracted inside extractListingData
            log(`Full extraction compleet. Gevonden: ${photos.length} foto's.`);
            sendResponse({ ...data, logs });
        } else if (request.action === "get_photos") {
            const photos = extractPhotos(log);
            log(`Foto-extractie compleet. Gevonden: ${photos.length} foto's.`);
            sendResponse({
                url: window.location.href,
                timestamp: new Date().toISOString(),
                photos,
                logs
            });
        }
    } catch (e) {
        log(`ERROR: ${e.message}`);
        sendResponse({ error: e.message, logs });
    }
    return true; // Keep message channel open for async response
});

/**
 * Extracts comprehensive information about the listing
 */
function extractListingData(log) {
    return {
        url: window.location.href,
        timestamp: new Date().toISOString(),
        html: document.documentElement.outerHTML,
        title: document.title,
        // Extract __NEXT_DATA__ if it exists (modern Funda)
        nextData: getNextData(),
        photos: extractPhotos(log)
    };
}

/**
 * Specifically finds and structures all property photos
 */
function extractPhotos(log = console.log) {
    const photos = [];
    const seenUrls = new Set();

    function addPhoto(url, caption, order, type) {
        if (!url || typeof url !== 'string') return;

        // Ensure protocol
        if (url.startsWith('//')) url = 'https:' + url;

        // 1. DEDUPLICATION BY MEDIA ID
        const idMatch = url.match(/(\d{3}\/\d{3}\/\d{3})/);
        const dedupKey = idMatch ? idMatch[1] : url.split('?')[0].split('#')[0];

        if (seenUrls.has(dedupKey)) return;
        seenUrls.add(dedupKey);

        // 2. CLEAN & UPSAMPLE URL
        let cleanUrl = url.split('?')[0].split('#')[0];
        if (cleanUrl.includes('cloud.funda.nl')) {
            cleanUrl += '?options=width=1440';
        } else if (cleanUrl.includes('media.funda.nl')) {
            cleanUrl = cleanUrl.replace(/_[0-9]+x[0-9]+/, '_1440x960');
        }

        // 3. REJECTION OF TECHNICAL VARIANTS
        const lowerUrl = cleanUrl.toLowerCase();
        if (lowerUrl.includes('/tile/') || lowerUrl.includes('marker.') || lowerUrl.includes('favicon')) return;

        // 4. DOMAIN & BRANDING CHECK
        const isMediaDomain = cleanUrl.includes('media.funda.nl') || cleanUrl.includes('cloud.funda.nl');
        if (!isMediaDomain) return;

        const badWords = ['logo', 'icon', 'avatar', 'funda-logo', 'branding', 'social', 'favicon', 'agent', 'profile'];
        if (badWords.some(word => lowerUrl.includes(word))) return;

        photos.push({
            url: cleanUrl,
            caption: (caption || "Hoofdfoto").trim(),
            order: order,
            type: type
        });
        log(`CAPTURED: ${dedupKey} (${type})`);
    }

    // Method 0: Specific Hero Image (Critical for main page)
    const heroImg = document.querySelector('img.object-header-media-viewer__image, [data-test="media-viewer-main-image"] img');
    if (heroImg && (heroImg.src || heroImg.getAttribute('data-src'))) {
        addPhoto(heroImg.src || heroImg.getAttribute('data-src'), heroImg.alt, -1000, 'main-hero');
    }

    // Method 1: Data Scan (__NEXT_DATA__ or __NUXT_DATA__)
    log("Scanning page data for media...");
    const dataBlock = getNextData();
    if (dataBlock) {
        try {
            let mediaCount = 0;
            if (dataBlock.type === 'nuxt') {
                // Nuxt patterns (valentina_media IDs)
                const ids = dataBlock.raw.match(/\d{3}\/\d{3}\/\d{3}/g) || [];
                // Filter out non-media segments (Nuxt often includes empty/small ID-like strings)
                const uniqueIds = Array.from(new Set(ids));
                uniqueIds.forEach((id, idx) => {
                    addPhoto(`https://cloud.funda.nl/valentina_media/${id}.jpg`, null, idx, 'nuxt-pattern');
                    mediaCount++;
                });
            } else {
                // Legacy Next.js recursive scan
                function findMediaRecursive(obj) {
                    if (!obj) return;
                    if (typeof obj === 'string') {
                        if (obj.includes('media.funda.nl') || obj.includes('cloud.funda.nl')) {
                            addPhoto(obj, null, photos.length, 'json-deep');
                            mediaCount++;
                        }
                        return;
                    }
                    if (typeof obj === 'object') {
                        if (obj.url && typeof obj.url === 'string' && (obj.url.includes('media.funda.nl') || obj.url.includes('cloud.funda.nl'))) {
                            addPhoto(obj.url, obj.caption || obj.description, photos.length, 'json-obj');
                            mediaCount++;
                        }
                        Object.values(obj).forEach(val => findMediaRecursive(val));
                    }
                }
                findMediaRecursive(dataBlock);
            }
            log(`Data Scan completed. Found ${mediaCount} candidates.`);
        } catch (e) {
            log(`Data Scan Error: ${e.message}`);
        }
    }

    // Method 2: Target specific property images (Hero, Gallery)
    log("Scanning DOM for targeted media elements...");
    const selectors = [
        '.object-media-viewer-image',
        '.media-viewer-item img',
        '[class*="Hero"] img',
        '.listing-main-photo img',
        'img[class*="Media"]',
        'img[class*="Gallery"]'
    ];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach((img, idx) => {
            const src = img.src || img.getAttribute('data-src');
            if (src) addPhoto(src, img.alt, idx - 100, 'target-dom');
        });
    });

    // Method 3: Generic Scan of ALL images on media domains
    if (photos.length < 5) {
        log("Insufficient photos found. Running generic DOM fallback scan...");
        document.querySelectorAll('img[src*="funda.nl"], img[data-src*="funda.nl"], source[srcset*="funda.nl"]').forEach((el, idx) => {
            const src = el.src || el.getAttribute('data-src') || (el.srcset ? el.srcset.split(' ')[0] : null);
            if (!src) return;

            const alt = (el.alt || "").toLowerCase();
            if (alt.includes('logo') || alt.includes('funda')) return;

            // Only large images or items in containers
            if (el.width > 200 || el.height > 150 || el.closest('[class*="media"]') || el.closest('[class*="gallery"]') || el.closest('a[class*="thumbnail"]')) {
                addPhoto(src, el.alt, idx + 500, 'generic-dom');
            }
        });
    }

    // Sort: Hero/Target first, then JSON order
    photos.sort((a, b) => a.order - b.order);
    log(`Extraction Finished. Total unique photos: ${photos.length}`);
    return photos;
}

function getNextData() {
    // Modern Funda uses Nuxt (__NUXT_DATA__) or Next (__NEXT_DATA__)
    const next = document.getElementById('__NEXT_DATA__');
    const nuxt = document.getElementById('__NUXT_DATA__');

    if (next) {
        try { return JSON.parse(next.textContent); } catch (e) { return null; }
    }
    if (nuxt) {
        try {
            // Nuxt data is often a flat list. We just want the raw string for pattern matching if needed,
            // or a basic object for recursion.
            return { raw: nuxt.textContent, type: 'nuxt' };
        } catch (e) { return null; }
    }
    return null;
}

/**
 * Utility to deep-find keys in nested objects
 */
function findKeysInObject(obj, targetKey) {
    if (!obj || typeof obj !== 'object') return null;
    if (obj[targetKey]) return obj[targetKey];

    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            const found = findKeysInObject(obj[key], targetKey);
            if (found) return found;
        }
    }
    return null;
}
