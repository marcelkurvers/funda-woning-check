// Extension Settings - Full Configuration Parity
// Syncs with backend /api/ai/runtime-status for provider/model selection
// NO HARDCODED PROVIDER/MODEL LISTS - everything comes from backend

const DEFAULT_API_URL = 'http://localhost:8000';

// State - providers will be populated from backend
let currentSettings = {
    apiUrl: DEFAULT_API_URL,
    provider: 'openai',  // Default per hierarchy
    model: 'gpt-4o-mini',
    mode: 'full'
};

let serverConfig = null;
let runtimeStatus = null;  // NEW: Runtime status from AIAuthority

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
    const providerStatusEl = document.getElementById('provider-status');
    const modelStatusEl = document.getElementById('model-status');

    // Show loading
    loadingEl.classList.add('active');

    // Load saved settings from Chrome storage
    const saved = await chrome.storage.sync.get(['apiUrl', 'provider', 'model', 'mode']);
    currentSettings = {
        apiUrl: saved.apiUrl || DEFAULT_API_URL,
        provider: saved.provider || 'openai',  // Default to OpenAI per hierarchy
        model: saved.model || 'gpt-4o-mini',
        mode: saved.mode || 'full'
    };

    // Set form values
    apiUrlInput.value = currentSettings.apiUrl;

    // Fetch runtime status from backend (single source of truth)
    await fetchRuntimeStatus();

    // Hide loading, show content
    loadingEl.classList.remove('active');
    contentEl.style.display = 'block';

    // === Event Listeners ===

    // Provider change
    providerSelect.addEventListener('change', (e) => {
        const provider = e.target.value;
        currentSettings.provider = provider;
        updateModelDropdownFromRuntime(provider);
        updateTrafficLights();
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
            await fetchRuntimeStatus();
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

        // Push settings to server
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
            provider: 'openai',  // Default per hierarchy
            model: 'gpt-4o-mini',
            mode: 'full'
        };

        apiUrlInput.value = DEFAULT_API_URL;
        await fetchRuntimeStatus();
        updateModeSelection('full');

        await chrome.storage.sync.set(currentSettings);

        showStatus('success', '✓ Gereset naar standaardinstellingen');
    });

    // === Helper Functions ===

    function updateProviderDropdownFromRuntime() {
        if (!runtimeStatus || !runtimeStatus.providers) {
            return;
        }

        providerSelect.innerHTML = '';

        // Use provider_hierarchy from backend for ordering
        const hierarchy = runtimeStatus.provider_hierarchy || ['openai', 'gemini', 'anthropic', 'ollama'];

        for (const providerName of hierarchy) {
            const provider = runtimeStatus.providers[providerName];
            if (!provider) continue;

            const option = document.createElement('option');
            option.value = provider.name;
            option.textContent = `${provider.label}${provider.configured ? '' : ' (niet geconfigureerd)'}`;
            option.disabled = !provider.configured && provider.name !== 'ollama';

            if (provider.name === currentSettings.provider) {
                option.selected = true;
            }
            providerSelect.appendChild(option);
        }

        // If current provider is not available, switch to active provider from runtime
        if (runtimeStatus.active_provider && currentSettings.provider !== runtimeStatus.active_provider) {
            const currentProviderState = runtimeStatus.providers[currentSettings.provider];
            if (!currentProviderState || !currentProviderState.configured) {
                currentSettings.provider = runtimeStatus.active_provider;
                providerSelect.value = runtimeStatus.active_provider;
            }
        }
    }

    function updateModelDropdownFromRuntime(provider) {
        if (!runtimeStatus || !runtimeStatus.providers) {
            return;
        }

        const providerState = runtimeStatus.providers[provider];
        if (!providerState) return;

        const models = providerState.models || [];
        modelSelect.innerHTML = '';

        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            if (model === currentSettings.model || model === runtimeStatus.active_model) {
                option.selected = true;
            }
            modelSelect.appendChild(option);
        });

        // Set current model
        if (models.length > 0 && !models.includes(currentSettings.model)) {
            currentSettings.model = runtimeStatus.active_model || models[0];
        }
    }

    function updateModeSelection(mode) {
        modeGrid.querySelectorAll('.mode-option').forEach(option => {
            option.classList.toggle('selected', option.dataset.mode === mode);
        });
    }

    function updateTrafficLights() {
        if (!runtimeStatus || !runtimeStatus.providers) {
            setTrafficLight(providerStatusEl, 'gray', 'Onbekend');
            setTrafficLight(modelStatusEl, 'gray', 'Onbekend');
            return;
        }

        const provider = currentSettings.provider;
        const providerState = runtimeStatus.providers[provider];

        if (!providerState) {
            setTrafficLight(providerStatusEl, 'gray', 'Onbekend');
            setTrafficLight(modelStatusEl, 'gray', 'Onbekend');
            return;
        }

        // Provider status based on operational state
        if (providerState.operational) {
            setTrafficLight(providerStatusEl, 'green', 'Operationeel');
        } else if (providerState.configured) {
            // Configured but not operational
            if (providerState.status === 'quota_exceeded') {
                setTrafficLight(providerStatusEl, 'yellow', 'Quota bereikt');
            } else if (providerState.status === 'offline') {
                setTrafficLight(providerStatusEl, 'yellow', 'Offline');
            } else {
                setTrafficLight(providerStatusEl, 'yellow', providerState.reason || 'Beperkt');
            }
        } else {
            setTrafficLight(providerStatusEl, 'red', 'Niet geconfigureerd');
        }

        // Model status follows provider
        if (providerState.operational) {
            setTrafficLight(modelStatusEl, 'green', 'Klaar');
        } else if (providerState.configured) {
            setTrafficLight(modelStatusEl, 'yellow', 'Beperkt');
        } else {
            setTrafficLight(modelStatusEl, 'red', 'Niet beschikbaar');
        }
    }

    function setTrafficLight(element, color, tooltip) {
        const light = element.querySelector('.light');
        light.className = `light ${color}`;
        element.title = tooltip;
    }

    async function fetchRuntimeStatus() {
        const url = currentSettings.apiUrl;

        try {
            // Use the NEW unified runtime-status endpoint
            const statusRes = await fetch(`${url}/api/ai/runtime-status`, {
                method: 'GET',
                signal: AbortSignal.timeout(5000)
            });

            if (statusRes.ok) {
                serverDot.className = 'status-dot online';
                serverStatusText.textContent = 'Verbonden';

                runtimeStatus = await statusRes.json();

                // Update UI from runtime status
                updateProviderDropdownFromRuntime();
                updateModelDropdownFromRuntime(currentSettings.provider);
                updateKeyStatusList();
                updateTrafficLights();
                updateModeSelection(currentSettings.mode);

                // Show active provider info
                if (runtimeStatus.user_message) {
                    console.log('[Extension] AI Status:', runtimeStatus.user_message);
                }
            } else {
                serverDot.className = 'status-dot offline';
                serverStatusText.textContent = 'Server error';
                runtimeStatus = null;
            }
        } catch (e) {
            serverDot.className = 'status-dot offline';
            serverStatusText.textContent = 'Niet bereikbaar';
            runtimeStatus = null;
            updateKeyStatusList();
            updateTrafficLights();
        }
    }

    function updateKeyStatusList() {
        if (!runtimeStatus || !runtimeStatus.providers) {
            keyStatusList.innerHTML = `
                <div class="key-status">
                    <span class="provider">Status niet beschikbaar</span>
                    <span class="status missing">Server niet verbonden</span>
                </div>
            `;
            return;
        }

        // Show providers in hierarchy order
        const hierarchy = runtimeStatus.provider_hierarchy || ['openai', 'gemini', 'anthropic', 'ollama'];

        keyStatusList.innerHTML = hierarchy
            .filter(name => name !== 'ollama')  // Skip Ollama (no key needed)
            .map(providerName => {
                const provider = runtimeStatus.providers[providerName];
                if (!provider) return '';

                const statusClass = provider.configured ? 'present' : 'missing';
                const statusText = provider.configured
                    ? (provider.operational ? '✓ Operationeel' : `⚠ ${provider.reason || 'Beperkt'}`)
                    : '✗ Ontbreekt';

                return `
                    <div class="key-status">
                        <span class="provider">${provider.label}</span>
                        <span class="status ${statusClass}">${statusText}</span>
                    </div>
                `;
            }).join('');

        // Add Ollama status if configured
        const ollamaState = runtimeStatus.providers?.ollama;
        if (ollamaState) {
            const ollamaStatus = ollamaState.operational ? '✓ Beschikbaar' : '✗ Offline';
            keyStatusList.innerHTML += `
                <div class="key-status">
                    <span class="provider">${ollamaState.label}</span>
                    <span class="status ${ollamaState.operational ? 'present' : 'missing'}">${ollamaStatus}</span>
                </div>
            `;
        }
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

        // Invalidate cache and refresh
        try {
            await fetch(`${url}/api/ai/invalidate-cache`, { method: 'POST' });
            await fetchRuntimeStatus();
        } catch (e) {
            console.warn('Cache invalidation failed:', e);
        }

        return await res.json();
    }

    function showStatus(type, message) {
        statusEl.className = type;
        statusEl.textContent = message;
        statusEl.style.display = 'block';
        setTimeout(() => {
            statusEl.className = '';
            statusEl.style.display = 'none';
        }, 5000);
    }
});

