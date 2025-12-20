import React, { useState, useEffect } from 'react';
import { X, Save, RotateCcw, Cpu, Globe, Scale, Shield, Loader2, AlertCircle, CheckCircle2, Bug } from 'lucide-react';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    debugMode: boolean;
    setDebugMode: (val: boolean) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, debugMode, setDebugMode }) => {
    const [config, setConfig] = useState<any>(null);
    const [providers, setProviders] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchData();
        }
    }, [isOpen]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [configRes, providersRes] = await Promise.all([
                fetch('/api/config/'),
                fetch('/api/ai/providers')
            ]);

            if (!configRes.ok || !providersRes.ok) throw new Error('Kon instellingen niet ophalen');

            const configData = await configRes.json();
            const providersData = await providersRes.json();

            setConfig(configData);
            setProviders(Object.values(providersData));
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        setError(null);
        setSuccess(false);
        try {
            const res = await fetch('/api/config/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            if (!res.ok) throw new Error('Opslaan mislukt');

            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    };

    const updateSection = (section: string, field: string, value: any) => {
        setConfig((prev: any) => ({
            ...prev,
            [section]: {
                ...prev[section],
                [field]: value
            }
        }));
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white w-full max-w-2xl rounded-2xl shadow-2xl border border-slate-200 flex flex-col max-h-[90vh] overflow-hidden animate-in zoom-in-95 duration-200">

                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-100 bg-slate-50/50">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-600 rounded-lg shadow-lg shadow-blue-200">
                            <Shield className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-black text-slate-800 tracking-tight">System Settings</h2>
                            <p className="text-xs text-slate-500 font-medium">Beheer AI providers, marktdata en validatie</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-200 rounded-full transition-colors">
                        <X className="w-6 h-6 text-slate-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-12 gap-4">
                            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                            <p className="text-slate-500 font-medium tracking-tight">Configuratie laden...</p>
                        </div>
                    ) : error ? (
                        <div className="flex items-center gap-3 p-4 bg-red-50 text-red-700 rounded-xl border border-red-100">
                            <AlertCircle className="w-5 h-5" />
                            <p className="font-medium">{error}</p>
                        </div>
                    ) : (
                        <>
                            {/* AI Section */}
                            <section className="space-y-4">
                                <div className="flex items-center gap-2 text-slate-800 mb-2">
                                    <Cpu className="w-5 h-5 text-blue-600" />
                                    <h3 className="font-bold tracking-tight">AI Provider Abstraction</h3>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Actieve Provider</label>
                                        <select
                                            value={config.ai.provider}
                                            onChange={(e) => updateSection('ai', 'provider', e.target.value)}
                                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                        >
                                            {providers.map(p => (
                                                <option key={p.name} value={p.name}>{p.name.charAt(0).toUpperCase() + p.name.slice(1)}</option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Model</label>
                                        <input
                                            type="text"
                                            value={config.ai.model}
                                            onChange={(e) => updateSection('ai', 'model', e.target.value)}
                                            placeholder="e.g. llama3, gpt-4o"
                                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                        />
                                    </div>
                                </div>

                                <div className="flex items-center gap-6 pt-2">
                                    <label className="flex items-center gap-3 cursor-pointer group">
                                        <div className="relative">
                                            <input
                                                type="checkbox"
                                                checked={config.ai.fallback_enabled}
                                                onChange={(e) => updateSection('ai', 'fallback_enabled', e.target.checked)}
                                                className="sr-only"
                                            />
                                            <div className={`w-10 h-5 rounded-full transition-colors ${config.ai.fallback_enabled ? 'bg-blue-600' : 'bg-slate-300'}`} />
                                            <div className={`absolute top-1 left-1 bg-white w-3 h-3 rounded-full transition-transform ${config.ai.fallback_enabled ? 'translate-x-5' : 'translate-x-0'}`} />
                                        </div>
                                        <span className="text-sm font-medium text-slate-700 group-hover:text-slate-900 transition-colors">Fallback bij fouten</span>
                                    </label>

                                    <div className="flex items-center gap-3">
                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Timeout</label>
                                        <input
                                            type="number"
                                            value={config.ai.timeout}
                                            onChange={(e) => updateSection('ai', 'timeout', parseInt(e.target.value))}
                                            className="w-16 bg-slate-50 border border-slate-200 rounded px-2 py-1 text-sm outline-none"
                                        />
                                        <span className="text-xs text-slate-400 font-medium">sec</span>
                                    </div>
                                </div>
                            </section>

                            {/* Market Section */}
                            <section className="space-y-4 pt-4 border-t border-slate-100">
                                <div className="flex items-center gap-2 text-slate-800 mb-2">
                                    <Globe className="w-5 h-5 text-emerald-600" />
                                    <h3 className="font-bold tracking-tight">Markt & Benchmarks</h3>
                                </div>

                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Gemiddelde m² Prijs (Nederland)</label>
                                            <span className="text-sm font-black text-emerald-600">€ {config.market.avg_price_m2} / m²</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="3000"
                                            max="10000"
                                            step="100"
                                            value={config.market.avg_price_m2}
                                            onChange={(e) => updateSection('market', 'avg_price_m2', parseInt(e.target.value))}
                                            className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                                        />
                                        <div className="flex justify-between text-[10px] text-slate-400 font-bold uppercase tracking-tighter">
                                            <span>Starter (€3000)</span>
                                            <span>Gemiddeld</span>
                                            <span>Top Segment (€10000+)</span>
                                        </div>
                                    </div>
                                </div>
                            </section>

                            {/* Validation Section */}
                            <section className="space-y-4 pt-4 border-t border-slate-100">
                                <div className="flex items-center gap-2 text-slate-800 mb-2">
                                    <Scale className="w-5 h-5 text-amber-500" />
                                    <h3 className="font-bold tracking-tight">Parser Validatie</h3>
                                </div>

                                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                    {[
                                        { label: 'Max Kamers', section: 'validation', field: 'max_total_rooms' },
                                        { label: 'Max Slaapkamers', section: 'validation', field: 'max_bedrooms' },
                                        { label: 'Min Oppervlak', section: 'validation', field: 'min_living_area' },
                                        { label: 'Max Oppervlak', section: 'validation', field: 'max_living_area' },
                                        { label: 'Min Bouwjaar', section: 'validation', field: 'min_build_year' },
                                        { label: 'Max Bouwjaar', section: 'validation', field: 'max_build_year' },
                                    ].map((item: any) => (
                                        <div key={item.field} className="space-y-1">
                                            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{item.label}</label>
                                            <input
                                                type="number"
                                                value={config[item.section][item.field]}
                                                onChange={(e) => updateSection(item.section, item.field, parseInt(e.target.value))}
                                                className="w-full bg-slate-50 border border-slate-200 rounded px-2 py-1.5 text-sm outline-none focus:border-amber-400 transition-colors"
                                            />
                                        </div>
                                    ))}
                                </div>
                            </section>

                            {/* Advanced Section */}
                            <section className="space-y-4 pt-4 border-t border-slate-100">
                                <div className="flex items-center gap-2 text-slate-800 mb-2">
                                    <Bug className="w-5 h-5 text-slate-500" />
                                    <h3 className="font-bold tracking-tight">Geavanceerd</h3>
                                </div>

                                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
                                    <div className="flex flex-col">
                                        <span className="text-sm font-medium text-slate-700">Debug Modus</span>
                                        <span className="text-xs text-slate-400 leading-tight">Toon data inconsistenties en ruwe payloads</span>
                                    </div>
                                    <button
                                        onClick={() => setDebugMode(!debugMode)}
                                        className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${debugMode ? 'bg-blue-600 justify-end' : 'bg-slate-300 justify-start'}`}
                                    >
                                        <div className="w-4 h-4 bg-white rounded-full shadow-sm" />
                                    </button>
                                </div>
                            </section>
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-100 bg-slate-50/50 flex flex-col gap-4">
                    {success && (
                        <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-3 py-2 rounded-lg border border-emerald-100 animate-in fade-in slide-in-from-bottom-2">
                            <CheckCircle2 className="w-4 h-4" />
                            <span className="text-sm font-bold">Instellingen succesvol opgeslagen!</span>
                        </div>
                    )}

                    <div className="flex items-center justify-between">
                        <button
                            onClick={fetchData}
                            disabled={loading || saving}
                            className="px-4 py-2 text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 transition-colors disabled:opacity-50"
                        >
                            <RotateCcw className="w-4 h-4" />
                            Reset naar Huidige
                        </button>
                        <button
                            onClick={handleSave}
                            disabled={loading || saving}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-blue-200 transition-all active:scale-95 disabled:opacity-50"
                        >
                            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                            Save Configuration
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
