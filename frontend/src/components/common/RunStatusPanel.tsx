import { useState, useEffect, useCallback } from 'react';
import {
    Loader2, CheckCircle2, XCircle, AlertTriangle, Clock,
    Cpu, FileText, Database, Shield, Zap, Activity
} from 'lucide-react';

interface StepStatus {
    name: string;
    status: 'pending' | 'running' | 'done' | 'error' | 'skipped';
    elapsed_ms?: number;
    message?: string;
}

interface RunLiveStatus {
    run_id: string;
    status: string;
    provider: string;
    model: string;
    mode: string;
    current_step: string | null;
    current_chapter: string | null;
    current_plane: string | null;
    progress_percent: number;
    total_elapsed_ms: number | null;
    steps: Record<string, StepStatus>;
    planes: Record<string, any>;
    warnings: string[];
    errors: string[];
    source: 'realtime' | 'database';
}

interface Props {
    runId: string;
    onComplete?: () => void;
    compact?: boolean;
}

const stepIcons: Record<string, React.ComponentType<any>> = {
    scrape_funda: FileText,
    dynamic_extraction: Database,
    registry_build: Database,
    plane_generation: Zap,
    validation: Shield,
    render: FileText,
};

const stepLabels: Record<string, string> = {
    scrape_funda: 'Scrape & Parse',
    dynamic_extraction: 'Dynamische Extractie',
    registry_build: 'Registry Opbouw',
    plane_generation: '4-Vlak Generatie',
    validation: 'Validatie Gate',
    render: 'Render Output',
};

export function RunStatusPanel({ runId, onComplete, compact = false }: Props) {
    const [status, setStatus] = useState<RunLiveStatus | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchStatus = useCallback(async () => {
        try {
            const res = await fetch(`/api/runs/${runId}/live-status`);
            if (res.ok) {
                const data = await res.json();
                setStatus(data);

                // Check if complete
                if (data.status === 'done' || data.status === 'error' || data.status === 'validation_failed') {
                    if (onComplete) onComplete();
                }
            }
        } catch (e) {
            console.error('Failed to fetch run status:', e);
        } finally {
            setLoading(false);
        }
    }, [runId, onComplete]);

    useEffect(() => {
        fetchStatus();

        // Poll every 750ms for smooth updates
        const interval = setInterval(fetchStatus, 750);
        return () => clearInterval(interval);
    }, [fetchStatus]);

    if (loading && !status) {
        return (
            <div className="flex items-center justify-center p-8">
                <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
            </div>
        );
    }

    if (!status) return null;

    const statusColors = {
        initializing: 'bg-blue-500',
        running: 'bg-blue-500',
        done: 'bg-emerald-500',
        error: 'bg-red-500',
        validation_failed: 'bg-amber-500',
    };

    const statusLabels = {
        initializing: 'Initialiseren...',
        running: 'Analyseren...',
        done: 'Voltooid',
        error: 'Fout',
        validation_failed: 'Validatie Mislukt',
    };

    if (compact) {
        return (
            <div className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                {/* Progress Circle */}
                <div className="relative w-16 h-16 flex-shrink-0">
                    <svg className="w-16 h-16 transform -rotate-90">
                        <circle
                            cx="32"
                            cy="32"
                            r="28"
                            stroke="currentColor"
                            strokeWidth="4"
                            fill="transparent"
                            className="text-slate-700"
                        />
                        <circle
                            cx="32"
                            cy="32"
                            r="28"
                            stroke="currentColor"
                            strokeWidth="4"
                            fill="transparent"
                            strokeDasharray={`${status.progress_percent * 1.76} 176`}
                            strokeLinecap="round"
                            className={status.status === 'done' ? 'text-emerald-500' : 'text-blue-500'}
                        />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-lg font-bold">{status.progress_percent}%</span>
                    </div>
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <div className={`w-2 h-2 rounded-full ${statusColors[status.status as keyof typeof statusColors] || 'bg-slate-500'} animate-pulse`} />
                        <span className="font-bold text-sm truncate">
                            {statusLabels[status.status as keyof typeof statusLabels] || status.status}
                        </span>
                    </div>
                    {status.current_step && (
                        <p className="text-xs text-slate-400 truncate">
                            {stepLabels[status.current_step] || status.current_step}
                            {status.current_plane && ` (Vlak ${status.current_plane})`}
                        </p>
                    )}
                    <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                        <Cpu className="w-3 h-3" />
                        <span>{status.provider} / {status.model}</span>
                    </div>
                </div>

                {/* Elapsed */}
                {status.total_elapsed_ms && (
                    <div className="text-right">
                        <div className="text-xs text-slate-500">Elapsed</div>
                        <div className="font-mono text-sm">{(status.total_elapsed_ms / 1000).toFixed(1)}s</div>
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-slate-800">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${statusColors[status.status as keyof typeof statusColors] || 'bg-slate-500'} animate-pulse`} />
                        <h3 className="font-bold text-lg">
                            {statusLabels[status.status as keyof typeof statusLabels] || status.status}
                        </h3>
                    </div>

                    <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-2 px-3 py-1 bg-slate-800 rounded-full">
                            <Cpu className="w-4 h-4 text-blue-400" />
                            <span className="text-slate-300">{status.provider}</span>
                            <span className="text-slate-500">•</span>
                            <span className="font-mono text-xs text-slate-400">{status.model}</span>
                        </div>
                        <div className="flex items-center gap-2 px-3 py-1 bg-slate-800 rounded-full">
                            <Zap className="w-4 h-4 text-amber-400" />
                            <span className="uppercase text-xs font-bold">{status.mode}</span>
                        </div>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-slate-500">Voortgang</span>
                        <span className="font-bold">{status.progress_percent}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div
                            className={`h-full transition-all duration-500 ease-out ${status.status === 'done'
                                ? 'bg-emerald-500'
                                : status.status === 'error'
                                    ? 'bg-red-500'
                                    : 'bg-blue-500'
                                }`}
                            style={{ width: `${status.progress_percent}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Steps */}
            <div className="p-6 space-y-3">
                {Object.entries(status.steps).map(([stepId, step]) => {
                    const Icon = stepIcons[stepId] || Activity;
                    const label = stepLabels[stepId] || step.name;

                    return (
                        <div
                            key={stepId}
                            className={`flex items-center gap-4 p-3 rounded-lg transition-colors ${step.status === 'running'
                                ? 'bg-blue-900/30 border border-blue-800'
                                : step.status === 'done'
                                    ? 'bg-emerald-900/20'
                                    : step.status === 'error'
                                        ? 'bg-red-900/20'
                                        : 'bg-slate-800/30'
                                }`}
                        >
                            {/* Status Icon */}
                            <div className="w-8 h-8 flex items-center justify-center">
                                {step.status === 'running' ? (
                                    <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
                                ) : step.status === 'done' ? (
                                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                                ) : step.status === 'error' ? (
                                    <XCircle className="w-5 h-5 text-red-400" />
                                ) : step.status === 'skipped' ? (
                                    <span className="text-slate-600">—</span>
                                ) : (
                                    <div className="w-5 h-5 rounded-full border-2 border-slate-600" />
                                )}
                            </div>

                            {/* Step Icon */}
                            <div className={`p-2 rounded-lg ${step.status === 'running'
                                ? 'bg-blue-500/20'
                                : step.status === 'done'
                                    ? 'bg-emerald-500/20'
                                    : 'bg-slate-700/50'
                                }`}>
                                <Icon className={`w-4 h-4 ${step.status === 'running'
                                    ? 'text-blue-400'
                                    : step.status === 'done'
                                        ? 'text-emerald-400'
                                        : 'text-slate-500'
                                    }`} />
                            </div>

                            {/* Label */}
                            <div className="flex-1">
                                <span className={`font-medium ${step.status === 'running' ? 'text-white' : 'text-slate-300'
                                    }`}>
                                    {label}
                                </span>
                                {step.message && (
                                    <p className="text-xs text-slate-500 mt-0.5">{step.message}</p>
                                )}
                            </div>

                            {/* Elapsed Time */}
                            {step.elapsed_ms && (
                                <div className="flex items-center gap-1 text-xs text-slate-500">
                                    <Clock className="w-3 h-3" />
                                    <span className="font-mono">{(step.elapsed_ms / 1000).toFixed(1)}s</span>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Current Plane Info */}
            {status.current_chapter && status.current_plane && (
                <div className="px-6 pb-4">
                    <div className="p-4 bg-blue-900/30 border border-blue-800 rounded-xl">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-500/20 rounded-lg">
                                <Activity className="w-5 h-5 text-blue-400 animate-pulse" />
                            </div>
                            <div>
                                <div className="text-sm font-medium text-blue-300">
                                    Hoofdstuk {status.current_chapter} - Vlak {status.current_plane}
                                </div>
                                <div className="text-xs text-blue-400/70">
                                    Genereren van {status.current_plane === 'A' ? 'Feiten' :
                                        status.current_plane === 'B' ? 'Narratief' :
                                            status.current_plane === 'C' ? 'KPIs' : 'Layout'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Warnings */}
            {status.warnings.length > 0 && (
                <div className="px-6 pb-4">
                    <div className="p-4 bg-amber-900/20 border border-amber-800 rounded-xl">
                        <div className="flex items-center gap-2 text-amber-400 mb-2">
                            <AlertTriangle className="w-4 h-4" />
                            <span className="text-sm font-medium">Waarschuwingen</span>
                        </div>
                        <ul className="space-y-1">
                            {status.warnings.map((warning, idx) => (
                                <li key={idx} className="text-xs text-amber-300/80">{warning}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}

            {/* Errors */}
            {status.errors.length > 0 && (
                <div className="px-6 pb-4">
                    <div className="p-4 bg-red-900/20 border border-red-800 rounded-xl">
                        <div className="flex items-center gap-2 text-red-400 mb-2">
                            <XCircle className="w-4 h-4" />
                            <span className="text-sm font-medium">Fouten</span>
                        </div>
                        <ul className="space-y-1">
                            {status.errors.map((error, idx) => (
                                <li key={idx} className="text-xs text-red-300/80">{error}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="px-6 pb-6 pt-2 border-t border-slate-800">
                <div className="flex items-center justify-between text-xs text-slate-600">
                    <span>Run ID: {status.run_id.substring(0, 8)}...</span>
                    {status.total_elapsed_ms && (
                        <span>Totaal: {(status.total_elapsed_ms / 1000).toFixed(1)}s</span>
                    )}
                    <span className="capitalize">{status.source}</span>
                </div>
            </div>
        </div>
    );
}
