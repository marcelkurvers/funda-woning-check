// Extension Settings - Full Configuration Parity
// Syncs with backend config endpoints for provider/model/mode selection

const DEFAULT_API_URL = 'http://localhost:8000';

// Model lists per provider
const PROVIDER_MODELS = {
    ollama: ['llama3', 'llama3.1', 'mistral', 'phi3', 'qwen2'],
    openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'o1-preview'],
    anthropic: ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
    gemini: ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash']
};

// State
let currentSettings = {
    apiUrl: DEFAULT_API_URL,
    provider: 'ollama',
    model: 'llama3',
    mode: 'full'
};

let serverConfig = null;

// DOM Elements
document.addEventListener('DOMContentLoaded', async () => {
    const loadingEl = document.getElementById('loading');
    const contentEl = document.getElementById('content');
    const apiUrlInput = document.getElementById('api-url');
    const providerSelect = document.getElementById('provider');
    const modelSelect = document.getElementById('model');
    const modeGrid = document.getElementById('mode-grid');
    const btnSave = document.getElementById('btn-save');
    const btnReset = document.getElementById('btn-reset');
    const statusEl = document.getElementById('status');
    const serverDot = document.getElementById('server-dot');
    const serverStatusText = document.getElementById('server-status-text');
    const keyStatusList = document.getElementById('key-status-list');

    // Show loading
    loadingEl.classList.add('active');

    // Load saved settings from Chrome storage
    const saved = await chrome.storage.sync.get(['apiUrl', 'provider', 'model', 'mode']);
    currentSettings = {
        apiUrl: saved.apiUrl || DEFAULT_API_URL,
        provider: saved.provider || 'ollama',
        model: saved.model || 'llama3',
        mode: saved.mode || 'full'
    };

    // Set form values
    apiUrlInput.value = currentSettings.apiUrl;
    providerSelect.value = currentSettings.provider;
    updateModelDropdown(currentSettings.provider, currentSettings.model);
    updateModeSelection(currentSettings.mode);

    // Try to fetch server config
    await fetchServerConfig();

    // Hide loading, show content
    loadingEl.classList.remove('active');
    contentEl.style.display = 'block';

    // === Event Listeners ===

    // Provider change
    providerSelect.addEventListener('change', (e) => {
        const provider = e.target.value;
        currentSettings.provider = provider;
        updateModelDropdown(provider);
        updateKeyStatusList();
    });

    // Model change
    modelSelect.addEventListener('change', (e) => {
        currentSettings.model = e.target.value;
    });

    // Mode selection
    modeGrid.querySelectorAll('.mode-option').forEach(option => {
        option.addEventListener('click', () => {
            const mode = option.dataset.mode;
            currentSettings.mode = mode;
            updateModeSelection(mode);
        });
    });

    // API URL change - re-fetch config
    apiUrlInput.addEventListener('blur', async () => {
        const url = apiUrlInput.value.trim().replace(/\/$/, '');
        if (url !== currentSettings.apiUrl) {
            currentSettings.apiUrl = url;
            await fetchServerConfig();
        }
    });

    // Save button
    btnSave.addEventListener('click', async () => {
        let url = apiUrlInput.value.trim().replace(/\/$/, '');

        if (!url) {
            showStatus('error', 'URL mag niet leeg zijn');
            return;
        }

        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            showStatus('error', 'URL moet beginnen met http:// of https://');
            return;
        }

        // Save to Chrome storage
        await chrome.storage.sync.set({
            apiUrl: url,
            provider: currentSettings.provider,
            model: currentSettings.model,
            mode: currentSettings.mode
        });

        // Optionally push settings to server
        try {
            await pushSettingsToServer(url);
            showStatus('success', '✓ Instellingen opgeslagen en gesynchroniseerd!');
        } catch (e) {
            // Still saved locally
            showStatus('success', '✓ Lokaal opgeslagen (server sync mislukt)');
        }
    });

    // Reset button
    btnReset.addEventListener('click', async () => {
        currentSettings = {
            apiUrl: DEFAULT_API_URL,
            provider: 'ollama',
            model: 'llama3',
            mode: 'full'
        };

        apiUrlInput.value = DEFAULT_API_URL;
        providerSelect.value = 'ollama';
        updateModelDropdown('ollama', 'llama3');
        updateModeSelection('full');

        await chrome.storage.sync.set(currentSettings);
        await fetchServerConfig();

        showStatus('success', '✓ Gereset naar standaardinstellingen');
    });

    // === Helper Functions ===

    function updateModelDropdown(provider, selectedModel = null) {
        const models = PROVIDER_MODELS[provider] || [];
        modelSelect.innerHTML = '';

        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            if (model === selectedModel) {
                option.selected = true;
            }
            modelSelect.appendChild(option);
        });

        // Set current model
        if (!selectedModel && models.length > 0) {
            currentSettings.model = models[0];
        }
    }

    function updateModeSelection(mode) {
        modeGrid.querySelectorAll('.mode-option').forEach(option => {
            option.classList.toggle('selected', option.dataset.mode === mode);
        });
    }

    async function fetchServerConfig() {
        const url = currentSettings.apiUrl;

        try {
            // Check health - use the dedicated config-status endpoint
            const healthRes = await fetch(`${url}/api/config-status/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(5000)
            });

            if (healthRes.ok) {
                serverDot.className = 'status-dot online';
                serverStatusText.textContent = 'Verbonden';

                // Fetch full config status
                const statusRes = await fetch(`${url}/api/config-status/status`);
                if (statusRes.ok) {
                    serverConfig = await statusRes.json();
                    updateKeyStatusList();
                }
            } else {
                serverDot.className = 'status-dot offline';
                serverStatusText.textContent = 'Server error';
            }
        } catch (e) {
            serverDot.className = 'status-dot offline';
            serverStatusText.textContent = 'Niet bereikbaar';
            serverConfig = null;
            updateKeyStatusList();
        }
    }

    function updateKeyStatusList() {
        if (!serverConfig || !serverConfig.key_status) {
            keyStatusList.innerHTML = `
                <div class="key-status">
                    <span class="provider">Status niet beschikbaar</span>
                    <span class="status missing">Server niet verbonden</span>
                </div>
            `;
            return;
        }

        const providers = ['openai', 'anthropic', 'gemini'];
        keyStatusList.innerHTML = providers.map(provider => {
            const status = serverConfig.key_status[provider] || { present: false };
            return `
                <div class="key-status">
                    <span class="provider">${provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
                    <span class="status ${status.present ? 'present' : 'missing'}">
                        ${status.present ? '✓ Geconfigureerd' : '✗ Ontbreekt'}
                        ${status.present && status.source ? ` (${status.source})` : ''}
                    </span>
                </div>
            `;
        }).join('');
    }

    async function pushSettingsToServer(url) {
        const res = await fetch(`${url}/api/config-status/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                provider: currentSettings.provider,
                model: currentSettings.model,
                mode: currentSettings.mode
            }),
            signal: AbortSignal.timeout(5000)
        });

        if (!res.ok) throw new Error('Server sync failed');
        return await res.json();
    }

    function showStatus(type, message) {
        statusEl.className = type;
        statusEl.textContent = message;
        setTimeout(() => {
            statusEl.className = '';
            statusEl.style.display = 'none';
        }, 5000);
    }
});
