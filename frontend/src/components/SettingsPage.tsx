import { useState, useEffect, useCallback } from 'react';
import {
    Settings, Server, Cpu, Key, Shield, Clock, Activity,
    CheckCircle2, XCircle, AlertCircle, RefreshCw, Loader2,
    Wifi, WifiOff, ChevronDown, ChevronRight, Eye, EyeOff,
    Zap, Database, Play, ArrowLeft, Save
} from 'lucide-react';

// Types
interface KeyStatus {
    present: boolean;
    source: 'env' | 'config' | 'secret' | 'none';
    last_updated: string | null;
    fingerprint: string | null;
}

interface ProviderInfo {
    name: string;
    label: string;
    models: string[];
    available: boolean;
    key_present: boolean;
    key_source: string;
    requires_key: boolean;
    is_current?: boolean;
}

interface HealthStatus {
    status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
    latency_ms: number | null;
    message: string | null;
}

interface ConfigStatus {
    provider: string;
    model: string;
    mode: string;
    mode_display: string;
    can_use_provider: boolean;
    provider_error: string | null;
    key_status: Record<string, KeyStatus>;
    providers: Record<string, ProviderInfo>;
    timeout: number;
    temperature: number;
    max_tokens: number;
    backend_health: HealthStatus;
    ollama_health: HealthStatus | null;
    computed_at: string;
}

interface ModeInfo {
    value: string;
    label: string;
    description: string;
    ai_required: boolean;
}

interface ProviderTestResult {
    success: boolean;
    provider: string;
    model: string;
    message: string;
    latency_ms?: number;
    response_preview?: string;
}

// Settings Page Component
export function SettingsPage() {
    const [config, setConfig] = useState<ConfigStatus | null>(null);
    const [modes, setModes] = useState<ModeInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState<ProviderTestResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [showFingerprints, setShowFingerprints] = useState(false);
    const [expandedSections, setExpandedSections] = useState<string[]>(['provider', 'mode']);

    // Form state for changes
    const [selectedProvider, setSelectedProvider] = useState<string>('');
    const [selectedModel, setSelectedModel] = useState<string>('');
    const [selectedMode, setSelectedMode] = useState<string>('');
    const [timeout, setTimeout] = useState<number>(60);

    const fetchConfig = useCallback(async () => {
        setLoading(true);
        try {
            const [statusRes, modesRes] = await Promise.all([
                fetch(`/api/config/status?show_fingerprint=${showFingerprints}`),
                fetch('/api/config/modes')
            ]);

            if (!statusRes.ok) throw new Error('Failed to fetch configuration');
            if (!modesRes.ok) throw new Error('Failed to fetch modes');

            const statusData: ConfigStatus = await statusRes.json();
            const modesData = await modesRes.json();

            setConfig(statusData);
            setModes(modesData.modes);

            // Initialize form state
            setSelectedProvider(statusData.provider);
            setSelectedModel(statusData.model);
            setSelectedMode(statusData.mode);
            setTimeout(statusData.timeout);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    }, [showFingerprints]);

    useEffect(() => {
        fetchConfig();
    }, [fetchConfig]);

    const handleProviderChange = (provider: string) => {
        setSelectedProvider(provider);
        // Auto-select first model for new provider
        const providerInfo = config?.providers[provider];
        if (providerInfo?.models?.length) {
            setSelectedModel(providerInfo.models[0]);
        }
        setTestResult(null);
    };

    const handleTestProvider = async () => {
        setTesting(true);
        setTestResult(null);
        try {
            const res = await fetch('/api/config/test-provider', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    provider: selectedProvider,
                    model: selectedModel
                })
            });
            const result = await res.json();
            setTestResult(result);
        } catch (err) {
            setTestResult({
                success: false,
                provider: selectedProvider,
                model: selectedModel,
                message: 'Test failed: Network error'
            });
        } finally {
            setTesting(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const res = await fetch('/api/config/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    provider: selectedProvider,
                    model: selectedModel,
                    mode: selectedMode,
                    timeout: timeout
                })
            });
            if (!res.ok) throw new Error('Save failed');
            await fetchConfig();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Save failed');
        } finally {
            setSaving(false);
        }
    };

    const toggleSection = (section: string) => {
        setExpandedSections(prev =>
            prev.includes(section)
                ? prev.filter(s => s !== section)
                : [...prev, section]
        );
    };

    const hasChanges =
        selectedProvider !== config?.provider ||
        selectedModel !== config?.model ||
        selectedMode !== config?.mode ||
        timeout !== config?.timeout;

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
                    <p className="text-slate-400 font-medium">Configuratie laden...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
                <div className="bg-red-900/50 border border-red-500 rounded-xl p-6 max-w-md">
                    <div className="flex items-center gap-3 text-red-400 mb-4">
                        <AlertCircle className="w-6 h-6" />
                        <h3 className="font-bold">Fout bij laden</h3>
                    </div>
                    <p className="text-red-300 mb-4">{error}</p>
                    <button
                        onClick={() => { setError(null); fetchConfig(); }}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                        Opnieuw proberen
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
            {/* Header */}
            <header className="border-b border-slate-700 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <a href="/" className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
                            <ArrowLeft className="w-5 h-5 text-slate-400" />
                        </a>
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-600 rounded-xl">
                                <Settings className="w-5 h-5" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold tracking-tight">Configuratie</h1>
                                <p className="text-xs text-slate-500">AI Woning Rapport Pro</p>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={fetchConfig}
                            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                            title="Vernieuwen"
                        >
                            <RefreshCw className="w-5 h-5 text-slate-400" />
                        </button>

                        {hasChanges && (
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50"
                            >
                                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                                <span>Opslaan</span>
                            </button>
                        )}
                    </div>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
                {/* Status Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {/* Backend Health */}
                    <div className={`p-4 rounded-xl border ${config?.backend_health.status === 'healthy'
                        ? 'bg-emerald-900/30 border-emerald-700'
                        : 'bg-red-900/30 border-red-700'
                        }`}>
                        <div className="flex items-center gap-2 mb-2">
                            <Server className="w-4 h-4 text-slate-400" />
                            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Backend</span>
                        </div>
                        <div className="flex items-center gap-2">
                            {config?.backend_health.status === 'healthy' ? (
                                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                            ) : (
                                <XCircle className="w-5 h-5 text-red-400" />
                            )}
                            <span className="font-bold">
                                {config?.backend_health.status === 'healthy' ? 'Online' : 'Offline'}
                            </span>
                            {config?.backend_health.latency_ms && (
                                <span className="text-xs text-slate-500">{config.backend_health.latency_ms}ms</span>
                            )}
                        </div>
                    </div>

                    {/* Ollama Health (if applicable) */}
                    {config?.ollama_health && (
                        <div className={`p-4 rounded-xl border ${config.ollama_health.status === 'healthy'
                            ? 'bg-emerald-900/30 border-emerald-700'
                            : config.ollama_health.status === 'unknown'
                                ? 'bg-slate-800 border-slate-700'
                                : 'bg-red-900/30 border-red-700'
                            }`}>
                            <div className="flex items-center gap-2 mb-2">
                                <Cpu className="w-4 h-4 text-slate-400" />
                                <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Ollama</span>
                            </div>
                            <div className="flex items-center gap-2">
                                {config.ollama_health.status === 'healthy' ? (
                                    <Wifi className="w-5 h-5 text-emerald-400" />
                                ) : (
                                    <WifiOff className="w-5 h-5 text-red-400" />
                                )}
                                <span className="font-bold capitalize">{config.ollama_health.status}</span>
                                {config.ollama_health.latency_ms && (
                                    <span className="text-xs text-slate-500">{config.ollama_health.latency_ms}ms</span>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Current Mode */}
                    <div className="p-4 rounded-xl border bg-slate-800 border-slate-700">
                        <div className="flex items-center gap-2 mb-2">
                            <Zap className="w-4 h-4 text-slate-400" />
                            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Modus</span>
                        </div>
                        <span className="font-bold">{config?.mode_display}</span>
                    </div>

                    {/* Provider Status */}
                    <div className={`p-4 rounded-xl border ${config?.can_use_provider
                        ? 'bg-emerald-900/30 border-emerald-700'
                        : 'bg-amber-900/30 border-amber-700'
                        }`}>
                        <div className="flex items-center gap-2 mb-2">
                            <Activity className="w-4 h-4 text-slate-400" />
                            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Provider</span>
                        </div>
                        <div className="flex items-center gap-2">
                            {config?.can_use_provider ? (
                                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                            ) : (
                                <AlertCircle className="w-5 h-5 text-amber-400" />
                            )}
                            <span className="font-bold">{config?.provider}</span>
                        </div>
                        {config?.provider_error && (
                            <p className="text-xs text-amber-400 mt-1">{config.provider_error}</p>
                        )}
                    </div>
                </div>

                {/* Provider Section */}
                <section className="bg-slate-800/50 rounded-2xl border border-slate-700 overflow-hidden">
                    <button
                        onClick={() => toggleSection('provider')}
                        className="w-full p-6 flex items-center justify-between hover:bg-slate-800/50 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-600/20 rounded-lg">
                                <Cpu className="w-5 h-5 text-blue-400" />
                            </div>
                            <div className="text-left">
                                <h2 className="font-bold text-lg">AI Provider Selectie</h2>
                                <p className="text-sm text-slate-500">Kies je AI provider en model</p>
                            </div>
                        </div>
                        {expandedSections.includes('provider') ? (
                            <ChevronDown className="w-5 h-5 text-slate-400" />
                        ) : (
                            <ChevronRight className="w-5 h-5 text-slate-400" />
                        )}
                    </button>

                    {expandedSections.includes('provider') && (
                        <div className="px-6 pb-6 space-y-6">
                            {/* Provider Grid */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                {Object.values(config?.providers || {}).map((provider) => (
                                    <button
                                        key={provider.name}
                                        onClick={() => handleProviderChange(provider.name)}
                                        className={`p-4 rounded-xl border-2 transition-all text-left ${selectedProvider === provider.name
                                            ? 'border-blue-500 bg-blue-900/20'
                                            : 'border-slate-700 hover:border-slate-600 bg-slate-800/50'
                                            } ${!provider.available && provider.name !== 'ollama' ? 'opacity-60' : ''}`}
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-bold">{provider.label}</span>
                                            {provider.available || provider.name === 'ollama' ? (
                                                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                            ) : (
                                                <XCircle className="w-4 h-4 text-red-400" />
                                            )}
                                        </div>
                                        <div className="flex items-center gap-2 text-xs text-slate-500">
                                            {provider.requires_key ? (
                                                <>
                                                    <Key className="w-3 h-3" />
                                                    <span>{provider.key_present ? 'Key ✓' : 'Key missing'}</span>
                                                </>
                                            ) : (
                                                <>
                                                    <Database className="w-3 h-3" />
                                                    <span>Lokaal</span>
                                                </>
                                            )}
                                        </div>
                                    </button>
                                ))}
                            </div>

                            {/* Model Selection */}
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-400">Model</label>
                                <select
                                    value={selectedModel}
                                    onChange={(e) => { setSelectedModel(e.target.value); setTestResult(null); }}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
                                >
                                    {config?.providers[selectedProvider]?.models.map((model) => (
                                        <option key={model} value={model}>{model}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Test Button */}
                            <div className="flex items-center gap-4">
                                <button
                                    onClick={handleTestProvider}
                                    disabled={testing}
                                    className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors disabled:opacity-50"
                                >
                                    {testing ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <Play className="w-4 h-4" />
                                    )}
                                    <span>Test Verbinding</span>
                                </button>

                                {testResult && (
                                    <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${testResult.success ? 'bg-emerald-900/40 text-emerald-400' : 'bg-red-900/40 text-red-400'
                                        }`}>
                                        {testResult.success ? (
                                            <CheckCircle2 className="w-4 h-4" />
                                        ) : (
                                            <XCircle className="w-4 h-4" />
                                        )}
                                        <span className="text-sm">{testResult.message}</span>
                                        {testResult.latency_ms && (
                                            <span className="text-xs opacity-70">({testResult.latency_ms}ms)</span>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </section>

                {/* Mode Section */}
                <section className="bg-slate-800/50 rounded-2xl border border-slate-700 overflow-hidden">
                    <button
                        onClick={() => toggleSection('mode')}
                        className="w-full p-6 flex items-center justify-between hover:bg-slate-800/50 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-emerald-600/20 rounded-lg">
                                <Zap className="w-5 h-5 text-emerald-400" />
                            </div>
                            <div className="text-left">
                                <h2 className="font-bold text-lg">Uitvoeringsmodus</h2>
                                <p className="text-sm text-slate-500">FAST / FULL / DEBUG / OFFLINE</p>
                            </div>
                        </div>
                        {expandedSections.includes('mode') ? (
                            <ChevronDown className="w-5 h-5 text-slate-400" />
                        ) : (
                            <ChevronRight className="w-5 h-5 text-slate-400" />
                        )}
                    </button>

                    {expandedSections.includes('mode') && (
                        <div className="px-6 pb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                            {modes.map((mode) => (
                                <button
                                    key={mode.value}
                                    onClick={() => setSelectedMode(mode.value)}
                                    className={`p-4 rounded-xl border-2 text-left transition-all ${selectedMode === mode.value
                                        ? 'border-emerald-500 bg-emerald-900/20'
                                        : 'border-slate-700 hover:border-slate-600'
                                        }`}
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="font-bold text-lg">{mode.label}</span>
                                        {mode.ai_required ? (
                                            <span className="text-xs px-2 py-1 bg-blue-900/50 text-blue-400 rounded-full">AI vereist</span>
                                        ) : (
                                            <span className="text-xs px-2 py-1 bg-slate-700 text-slate-400 rounded-full">Geen AI</span>
                                        )}
                                    </div>
                                    <p className="text-sm text-slate-400">{mode.description}</p>
                                </button>
                            ))}
                        </div>
                    )}
                </section>

                {/* Keys & Security Section */}
                <section className="bg-slate-800/50 rounded-2xl border border-slate-700 overflow-hidden">
                    <button
                        onClick={() => toggleSection('keys')}
                        className="w-full p-6 flex items-center justify-between hover:bg-slate-800/50 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-amber-600/20 rounded-lg">
                                <Key className="w-5 h-5 text-amber-400" />
                            </div>
                            <div className="text-left">
                                <h2 className="font-bold text-lg">API Keys & Beveiliging</h2>
                                <p className="text-sm text-slate-500">Status van je API keys (nooit zichtbaar)</p>
                            </div>
                        </div>
                        {expandedSections.includes('keys') ? (
                            <ChevronDown className="w-5 h-5 text-slate-400" />
                        ) : (
                            <ChevronRight className="w-5 h-5 text-slate-400" />
                        )}
                    </button>

                    {expandedSections.includes('keys') && (
                        <div className="px-6 pb-6 space-y-4">
                            {/* Security Notice */}
                            <div className="p-4 bg-amber-900/20 border border-amber-800 rounded-xl flex items-start gap-3">
                                <Shield className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="text-sm text-amber-300 font-medium">API keys worden nooit weergegeven</p>
                                    <p className="text-xs text-amber-400/70 mt-1">
                                        Keys moeten worden ingesteld via omgevingsvariabelen (OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY).
                                    </p>
                                </div>
                            </div>

                            {/* Key Status Grid */}
                            <div className="space-y-3">
                                {Object.entries(config?.key_status || {}).map(([provider, status]) => (
                                    <div
                                        key={provider}
                                        className={`p-4 rounded-xl border flex items-center justify-between ${status.present
                                            ? 'bg-emerald-900/20 border-emerald-800'
                                            : 'bg-slate-800 border-slate-700'
                                            }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            {status.present ? (
                                                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                                            ) : (
                                                <XCircle className="w-5 h-5 text-slate-500" />
                                            )}
                                            <div>
                                                <span className="font-medium capitalize">{provider}</span>
                                                <span className="text-sm text-slate-500 ml-2">
                                                    {status.present ? `via ${status.source}` : 'niet geconfigureerd'}
                                                </span>
                                            </div>
                                        </div>

                                        {status.present && showFingerprints && status.fingerprint && (
                                            <span className="text-xs font-mono text-slate-500">{status.fingerprint}</span>
                                        )}
                                    </div>
                                ))}
                            </div>

                            {/* Fingerprint Toggle */}
                            <button
                                onClick={() => setShowFingerprints(!showFingerprints)}
                                className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-300 transition-colors"
                            >
                                {showFingerprints ? (
                                    <EyeOff className="w-4 h-4" />
                                ) : (
                                    <Eye className="w-4 h-4" />
                                )}
                                <span>{showFingerprints ? 'Vingerafdruk verbergen' : 'Vingerafdruk tonen (laatste 4 tekens)'}</span>
                            </button>
                        </div>
                    )}
                </section>

                {/* Performance Settings */}
                <section className="bg-slate-800/50 rounded-2xl border border-slate-700 overflow-hidden">
                    <button
                        onClick={() => toggleSection('performance')}
                        className="w-full p-6 flex items-center justify-between hover:bg-slate-800/50 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-purple-600/20 rounded-lg">
                                <Clock className="w-5 h-5 text-purple-400" />
                            </div>
                            <div className="text-left">
                                <h2 className="font-bold text-lg">Performance & Timeouts</h2>
                                <p className="text-sm text-slate-500">Timeout, retries en concurrency instellingen</p>
                            </div>
                        </div>
                        {expandedSections.includes('performance') ? (
                            <ChevronDown className="w-5 h-5 text-slate-400" />
                        ) : (
                            <ChevronRight className="w-5 h-5 text-slate-400" />
                        )}
                    </button>

                    {expandedSections.includes('performance') && (
                        <div className="px-6 pb-6 space-y-6">
                            {/* Timeout Slider */}
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <label className="text-sm font-medium text-slate-400">Provider Timeout</label>
                                    <span className="text-lg font-bold">{timeout}s</span>
                                </div>
                                <input
                                    type="range"
                                    min="5"
                                    max="180"
                                    step="5"
                                    value={timeout}
                                    onChange={(e) => setTimeout(parseInt(e.target.value))}
                                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
                                />
                                <div className="flex justify-between text-xs text-slate-500">
                                    <span>5s (Snel)</span>
                                    <span>60s (Normaal)</span>
                                    <span>180s (Lang)</span>
                                </div>
                            </div>

                            {/* Other Settings */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-slate-900 rounded-xl">
                                    <span className="text-xs text-slate-500 uppercase tracking-wider">Temperature</span>
                                    <p className="text-xl font-bold">{config?.temperature}</p>
                                </div>
                                <div className="p-4 bg-slate-900 rounded-xl">
                                    <span className="text-xs text-slate-500 uppercase tracking-wider">Max Tokens</span>
                                    <p className="text-xl font-bold">{config?.max_tokens}</p>
                                </div>
                            </div>
                        </div>
                    )}
                </section>

                {/* Config Timestamp */}
                <div className="text-center text-xs text-slate-600">
                    Configuratie geladen: {config?.computed_at ? new Date(config.computed_at).toLocaleString('nl-NL') : 'Onbekend'}
                </div>
            </main>
        </div>
    );
}
