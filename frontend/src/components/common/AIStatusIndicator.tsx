import { useState, useEffect } from 'react';
import { Cpu, Wifi, WifiOff, ChevronDown, Check, AlertCircle } from 'lucide-react';

interface AIStatus {
    provider: string;
    model: string;
    status: 'online' | 'offline' | 'error' | 'unconfigured';
    latency_ms?: number;
    error_message?: string;
    available_providers: string[];
    configured_providers: Record<string, boolean>;
}

interface Props {
    onOpenSettings?: () => void;
}

export function AIStatusIndicator({ onOpenSettings }: Props) {
    const [status, setStatus] = useState<AIStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [showDropdown, setShowDropdown] = useState(false);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await fetch('/api/ai/status');
                if (res.ok) {
                    const data = await res.json();
                    setStatus(data);
                }
            } catch (e) {
                console.error('Failed to fetch AI status:', e);
            } finally {
                setLoading(false);
            }
        };

        fetchStatus();
        // Poll every 30 seconds
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading || !status) {
        return (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-lg animate-pulse">
                <div className="w-2 h-2 rounded-full bg-slate-300" />
                <div className="w-16 h-4 bg-slate-200 rounded" />
            </div>
        );
    }

    const statusColors = {
        online: 'bg-emerald-500',
        offline: 'bg-red-500',
        error: 'bg-amber-500',
        unconfigured: 'bg-slate-400',
    };

    const statusLabels = {
        online: 'Online',
        offline: 'Offline',
        error: 'Error',
        unconfigured: 'Niet geconfigureerd',
    };

    const providerLabels: Record<string, string> = {
        ollama: 'Ollama (Lokaal)',
        openai: 'OpenAI',
        anthropic: 'Anthropic',
        gemini: 'Google Gemini',
    };

    const StatusIcon = status.status === 'online' ? Wifi : WifiOff;

    return (
        <div className="relative">
            <button
                onClick={() => setShowDropdown(!showDropdown)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all hover:bg-white ${status.status === 'online'
                        ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                        : status.status === 'offline' || status.status === 'error'
                            ? 'bg-red-50 border-red-200 text-red-700'
                            : 'bg-slate-50 border-slate-200 text-slate-600'
                    }`}
            >
                <div className={`w-2 h-2 rounded-full ${statusColors[status.status]} animate-pulse`} />
                <Cpu className="w-3.5 h-3.5" />
                <span className="text-xs font-medium">
                    {providerLabels[status.provider] || status.provider}
                </span>
                <span className="text-xs text-slate-400">•</span>
                <span className="text-xs font-mono">{status.model}</span>
                {status.latency_ms && (
                    <>
                        <span className="text-xs text-slate-400">•</span>
                        <span className="text-[10px] text-slate-500">{status.latency_ms}ms</span>
                    </>
                )}
                <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>

            {showDropdown && (
                <>
                    <div className="fixed inset-0 z-40" onClick={() => setShowDropdown(false)} />
                    <div className="absolute right-0 top-full mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 p-4 z-50">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-sm font-bold text-slate-800">AI Provider Status</h3>
                            <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold ${status.status === 'online' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
                                }`}>
                                <StatusIcon className="w-3 h-3" />
                                {statusLabels[status.status]}
                            </div>
                        </div>

                        <div className="space-y-2 mb-4">
                            <div className="flex justify-between text-xs">
                                <span className="text-slate-500">Provider</span>
                                <span className="font-medium">{providerLabels[status.provider] || status.provider}</span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-slate-500">Model</span>
                                <span className="font-mono font-medium">{status.model}</span>
                            </div>
                            {status.latency_ms && (
                                <div className="flex justify-between text-xs">
                                    <span className="text-slate-500">Latency</span>
                                    <span className="font-medium">{status.latency_ms}ms</span>
                                </div>
                            )}
                            {status.error_message && (
                                <div className="flex items-start gap-2 p-2 bg-red-50 rounded-lg text-xs text-red-600">
                                    <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                                    <span>{status.error_message}</span>
                                </div>
                            )}
                        </div>

                        <div className="border-t border-slate-100 pt-3 mb-3">
                            <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                                Beschikbare Providers
                            </h4>
                            <div className="grid grid-cols-2 gap-2">
                                {status.available_providers.map((provider) => (
                                    <div
                                        key={provider}
                                        className={`flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs ${status.configured_providers[provider]
                                                ? 'bg-emerald-50 text-emerald-700'
                                                : 'bg-slate-50 text-slate-400'
                                            }`}
                                    >
                                        {status.configured_providers[provider] ? (
                                            <Check className="w-3 h-3" />
                                        ) : (
                                            <div className="w-3 h-3 rounded-full border border-slate-300" />
                                        )}
                                        <span className="font-medium">{providerLabels[provider] || provider}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <button
                            onClick={() => {
                                setShowDropdown(false);
                                if (onOpenSettings) onOpenSettings();
                                else window.location.href = '/static/preferences.html';
                            }}
                            className="w-full px-3 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            AI Instellingen Wijzigen
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}
