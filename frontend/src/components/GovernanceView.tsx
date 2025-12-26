import { useState, useEffect } from 'react';
import { Shield, Lock, AlertTriangle, Check, RefreshCw, Server } from 'lucide-react';

interface ClassificationEntry {
    guardrail_id: string;
    name: string;
    category: string;
    allowed_scope: string;
}

interface GovernanceStatus {
    environment: string;
    effective_truth_policy: Record<string, string>;
    classification: ClassificationEntry[];
    config_candidates: string[];
    current_governance_config: any;
    last_audit: any;
}

export function GovernanceView() {
    const [status, setStatus] = useState<GovernanceStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Local state for toggles (before applying)
    const [toggles, setToggles] = useState<Record<string, boolean>>({});

    useEffect(() => {
        fetchStatus();
    }, []);

    const fetchStatus = async () => {
        try {
            setLoading(true);
            const res = await fetch('/api/governance/status');
            if (!res.ok) throw new Error('Failed to fetch governance status');
            const data = await res.json();
            setStatus(data);

            // Initialize toggles from current config
            const current = data.current_governance_config || {};
            const initialToggles: Record<string, boolean> = {};
            data.config_candidates.forEach((key: string) => {
                initialToggles[key] = !!current[key];
            });
            setToggles(initialToggles);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleChange = (key: string) => {
        setToggles(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const handleApply = async () => {
        if (!status) return;
        try {
            setLoading(true);
            const payload = {
                environment: status.environment,
                ...toggles
            };

            const res = await fetch('/api/governance/apply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Apply failed');
            }

            await fetchStatus();
        } catch (err: any) {
            setError(err.message);
            setLoading(false);
        }
    };

    const handleReset = async () => {
        if (!confirm("Reset to default Strict Policy?")) return;
        try {
            setLoading(true);
            const res = await fetch('/api/governance/reset', { method: 'POST' });
            if (!res.ok) throw new Error('Reset failed');
            await fetchStatus();
        } catch (err: any) {
            setError(err.message);
            setLoading(false);
        }
    };

    if (loading && !status) return <div className="p-8">Loading Governance...</div>;
    if (error) return <div className="p-8 text-red-600">Error: {error}</div>;
    if (!status) return null;

    const isProd = status.environment === 'PRODUCTION';
    const isLocked = isProd; // Simply locked if Prod

    return (
        <div className="max-w-7xl mx-auto p-8 space-y-8 animate-in fade-in duration-500">

            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-black text-slate-800 tracking-tight flex items-center gap-3">
                        <Shield className="w-8 h-8 text-emerald-600" />
                        Governance Console
                    </h1>
                    <p className="text-slate-500 mt-2">
                        The Constitution of the System. Non-negotiable guardrails are legally binding.
                    </p>
                </div>

                <div className={`px-4 py-2 rounded-lg font-mono font-bold text-sm tracking-wider flex items-center gap-2 ${isProd ? 'bg-red-100 text-red-800 ring-2 ring-red-500' : 'bg-blue-100 text-blue-800 ring-2 ring-blue-500'
                    }`}>
                    <Server className="w-4 h-4" />
                    ENV: {status.environment}
                </div>
            </div>

            {/* Config Area (Dev Only) */}
            {!isProd && (
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                            <RefreshCw className="w-5 h-5 text-blue-600" />
                            Runtime Configuration (DEV/TEST ONLY)
                        </h2>
                        <div className="flex gap-2">
                            <button
                                onClick={handleReset}
                                className="px-4 py-2 text-slate-600 font-medium hover:bg-slate-100 rounded-lg transition-colors border border-transparent hover:border-slate-300"
                            >
                                Reset Defaults
                            </button>
                            <button
                                onClick={handleApply}
                                className="px-4 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
                            >
                                Apply Config
                            </button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {status.config_candidates.map(key => (
                            <label key={key} className="flex items-start gap-3 p-4 border rounded-lg hover:bg-slate-50 cursor-pointer transition-colors border-slate-200">
                                <input
                                    type="checkbox"
                                    checked={!!toggles[key]}
                                    onChange={() => handleToggleChange(key)}
                                    className="mt-1 w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                                />
                                <div>
                                    <div className="font-mono font-bold text-slate-700 text-sm mb-1">{key}</div>
                                    <div className="text-xs text-slate-500">
                                        {getKeyDescription(key)}
                                    </div>
                                </div>
                            </label>
                        ))}
                    </div>
                </div>
            )}

            {/* Policy Table */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
                    <h2 className="font-bold text-slate-700">Effective Truth Policy & Classification</h2>
                    <span className="text-xs font-mono text-slate-400">Last Audit: {status.last_audit?.timestamp || 'N/A'}</span>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
                            <tr>
                                <th className="px-6 py-3 w-20">Status</th>
                                <th className="px-6 py-3">Guardrail ID</th>
                                <th className="px-6 py-3">Property Name</th>
                                <th className="px-6 py-3">Classification</th>
                                <th className="px-6 py-3">Effective Level</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {status.classification.map((entry) => {
                                const effectiveLevel = status.effective_truth_policy[entry.name];
                                const isStrict = effectiveLevel === 'STRICT';
                                const isNonNegotiable = entry.category === 'NON-NEGOTIABLE';

                                return (
                                    <tr key={entry.guardrail_id} className="hover:bg-slate-50/50 transition-colors">
                                        <td className="px-6 py-4">
                                            {isStrict ? (
                                                <div className="flex justify-center" title="Locked & Active">
                                                    <Lock className="w-4 h-4 text-emerald-500" />
                                                </div>
                                            ) : (
                                                <div className="flex justify-center" title="Relaxed">
                                                    <AlertTriangle className="w-4 h-4 text-amber-500" />
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 font-mono text-xs text-slate-500">{entry.guardrail_id}</td>
                                        <td className="px-6 py-4 font-medium text-slate-900">{entry.name}</td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2 py-0.5 rounded textxs font-bold uppercase tracking-wider ${isNonNegotiable
                                                    ? 'bg-slate-100 text-slate-600 border border-slate-200'
                                                    : 'bg-indigo-50 text-indigo-700 border border-indigo-100'
                                                }`}>
                                                {entry.category}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`font-mono font-bold ${isStrict ? 'text-emerald-700' : 'text-amber-600'
                                                }`}>
                                                {effectiveLevel}
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    );
}

function getKeyDescription(key: string): string {
    switch (key) {
        case 'allow_partial_generation': return 'Allows narrative generation to fail gracefully (only for layout testing).';
        case 'offline_structural_mode': return 'Runs pipeline without AI provider (for CI structural checks).';
        default: return 'Configuration candidate.';
    }
}
