/**
 * Multi-Check Pro: Background Service Worker
 * 
 * Future use cases:
 * - Badge updates
 * - Background sync of large media batches
 * - Context menu integration
 */

chrome.runtime.onInstalled.addListener(() => {
    console.log("🏠 Multi-Check Pro Extension Installed");
});

// Listener for potential messages from other parts of the extension
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "LOG") {
        console.log("[Extension Log]:", request.message);
        sendResponse({ ok: true });
    }
    return true;
});
