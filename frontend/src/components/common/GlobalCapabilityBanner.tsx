/**
 * GlobalCapabilityBanner - AI Capability Status Indicator
 * 
 * This component displays the global AI capability status in the header.
 * 
 * CRITICAL DISTINCTION:
 * - OPERATIONAL LIMIT: External constraint (quota, outage) - system is correctly configured
 * - IMPLEMENTATION ERROR: Configuration issue - requires user action
 * 
 * When an operational limit is active, the banner shows a reassuring message
 * that confirms the system works and will resume automatically.
 */

import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle2, Clock, Settings, Info, X } from 'lucide-react';

interface CapabilityStatus {
    state: string;
    category: string;
    message: string | null;
    user_message: string | null;
    is_operational_limit: boolean;
    is_implementation_error: boolean;
    resume_hint: string | null;
}

interface GlobalCapabilityResponse {
    overall: {
        state: string;
        category: string;
        summary: string;
        user_message: string;
        is_operational_limit: boolean;
        is_implementation_valid: boolean;
    };
    capabilities: Record<string, CapabilityStatus>;
    timestamp: number;
}

interface Props {
    onOpenSettings?: () => void;
}

export function GlobalCapabilityBanner({ onOpenSettings }: Props) {
    const [capabilities, setCapabilities] = useState<GlobalCapabilityResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [dismissed, setDismissed] = useState(false);
    const [expanded, setExpanded] = useState(false);

    useEffect(() => {
        const fetchCapabilities = async () => {
            try {
                const res = await fetch('/api/ai/capabilities');
                if (res.ok) {
                    const data = await res.json();
                    setCapabilities(data);
                }
            } catch (e) {
                console.error('Failed to fetch AI capabilities:', e);
            } finally {
                setLoading(false);
            }
        };

        fetchCapabilities();
        // Poll every 30 seconds
        const interval = setInterval(fetchCapabilities, 30000);
        return () => clearInterval(interval);
    }, []);

    // Don't show anything while loading or if dismissed
    if (loading || dismissed) {
        return null;
    }

    // Don't show banner if everything is operational
    if (!capabilities || capabilities.overall.state === 'available' || capabilities.overall.state === 'unknown') {
        return null;
    }

    const { overall } = capabilities;
    const isOperationalLimit = overall.is_operational_limit;
    const isValid = overall.is_implementation_valid;

    // Find the limited capabilities for detailed display
    const limitedCaps = Object.entries(capabilities.capabilities).filter(
        ([_, cap]) => cap.state !== 'available' && cap.state !== 'unknown'
    );

    // Determine banner style based on type
    const bannerStyle = isOperationalLimit
        ? 'bg-amber-50 border-amber-200 text-amber-900'
        : 'bg-red-50 border-red-200 text-red-900';

    const iconColor = isOperationalLimit ? 'text-amber-600' : 'text-red-600';

    return (
        <div className={`border-b-2 ${bannerStyle}`}>
            {/* Compact Banner */}
            <div className="px-4 py-2 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    {isOperationalLimit ? (
                        <Clock className={`w-5 h-5 ${iconColor}`} />
                    ) : (
                        <AlertCircle className={`w-5 h-5 ${iconColor}`} />
                    )}

                    <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">
                            {isOperationalLimit ? 'Operational Limit' : 'Configuration Required'}
                        </span>
                        <span className="text-xs text-slate-500">—</span>
                        <span className="text-sm">
                            {overall.summary}
                        </span>
                    </div>

                    {isValid && isOperationalLimit && (
                        <div className="flex items-center gap-1.5 bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full text-xs font-bold">
                            <CheckCircle2 className="w-3 h-3" />
                            System Correctly Configured
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setExpanded(!expanded)}
                        className="text-xs font-medium text-slate-600 hover:text-slate-800 px-2 py-1 rounded hover:bg-white/50 transition-colors"
                    >
                        {expanded ? 'Less' : 'Details'}
                    </button>

                    {!isValid && (
                        <button
                            onClick={onOpenSettings}
                            className="flex items-center gap-1 text-xs font-medium bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700 transition-colors"
                        >
                            <Settings className="w-3 h-3" />
                            Configure
                        </button>
                    )}

                    {isOperationalLimit && (
                        <button
                            onClick={() => setDismissed(true)}
                            className="p-1 hover:bg-white/50 rounded transition-colors"
                            title="Dismiss"
                        >
                            <X className="w-4 h-4 text-slate-400" />
                        </button>
                    )}
                </div>
            </div>

            {/* Expanded Details */}
            {expanded && (
                <div className="px-4 py-3 border-t border-amber-100/50 bg-white/30">
                    <div className="max-w-4xl">
                        {/* User Message */}
                        <p className="text-sm mb-3">
                            {overall.user_message}
                        </p>

                        {/* Capability Details */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {limitedCaps.map(([name, cap]) => (
                                <div
                                    key={name}
                                    className="bg-white rounded-lg p-3 border border-slate-200 shadow-sm"
                                >
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="font-medium text-sm text-slate-800">
                                            {name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                        </span>
                                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cap.state === 'quota_exceeded'
                                                ? 'bg-amber-100 text-amber-700'
                                                : cap.state === 'offline'
                                                    ? 'bg-red-100 text-red-700'
                                                    : 'bg-slate-100 text-slate-600'
                                            }`}>
                                            {cap.state.replace('_', ' ')}
                                        </span>
                                    </div>

                                    <p className="text-xs text-slate-600">
                                        {cap.user_message}
                                    </p>

                                    {cap.is_operational_limit && (
                                        <div className="mt-2 flex items-center gap-1 text-xs text-emerald-600">
                                            <Info className="w-3 h-3" />
                                            This is NOT an implementation error
                                        </div>
                                    )}

                                    {cap.resume_hint && (
                                        <p className="mt-1 text-xs text-slate-500 italic">
                                            {cap.resume_hint}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>

                        {isOperationalLimit && (
                            <div className="mt-3 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                                <div className="flex items-start gap-2">
                                    <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5" />
                                    <div>
                                        <p className="text-sm font-medium text-emerald-800">
                                            Implementation Status: Valid
                                        </p>
                                        <p className="text-xs text-emerald-700 mt-1">
                                            The system is correctly configured. This limitation is due to external
                                            resource constraints (e.g., API quota) and will resume automatically
                                            when resources become available.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
