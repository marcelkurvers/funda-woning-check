// Default API URL
const DEFAULT_API_URL = 'http://localhost:8000';

// Load saved settings
document.addEventListener('DOMContentLoaded', async () => {
    const apiUrlInput = document.getElementById('api-url');
    const btnSave = document.getElementById('btn-save');
    const btnReset = document.getElementById('btn-reset');
    const status = document.getElementById('status');

    // Load current setting
    const settings = await chrome.storage.sync.get(['apiUrl']);
    apiUrlInput.value = settings.apiUrl || DEFAULT_API_URL;

    // Save settings
    btnSave.addEventListener('click', async () => {
        let url = apiUrlInput.value.trim();

        // Validate URL
        if (!url) {
            showStatus('error', 'URL mag niet leeg zijn');
            return;
        }

        // Remove trailing slash
        url = url.replace(/\/$/, '');

        // Basic validation
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            showStatus('error', 'URL moet beginnen met http:// of https://');
            return;
        }

        // Test connection
        try {
            const response = await fetch(`${url}/health`, { method: 'GET' });
            if (response.ok) {
                // Save to storage
                await chrome.storage.sync.set({ apiUrl: url });
                showStatus('success', '✓ Opgeslagen en verbinding succesvol!');
            } else {
                showStatus('error', 'Server bereikbaar maar geeft foutmelding');
            }
        } catch (e) {
            // Still save, but warn user
            await chrome.storage.sync.set({ apiUrl: url });
            showStatus('error', 'Opgeslagen, maar kan server niet bereiken');
        }
    });

    // Reset to default
    btnReset.addEventListener('click', async () => {
        apiUrlInput.value = DEFAULT_API_URL;
        await chrome.storage.sync.set({ apiUrl: DEFAULT_API_URL });
        showStatus('success', '✓ Gereset naar standaard (localhost)');
    });

    function showStatus(type, message) {
        status.className = type;
        status.textContent = message;
        setTimeout(() => {
            status.style.display = 'none';
        }, 5000);
    }
});
