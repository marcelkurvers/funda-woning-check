
import { useState } from 'react';
import { UploadCloud, ArrowRight, Loader2, ClipboardType, Plus } from 'lucide-react';

interface LandingPageProps {
    onStartAnalysis: (type: 'url' | 'paste', content: string, mediaUrls?: string[], extraFacts?: string) => Promise<void>;
    isLoading: boolean;
    error?: string | null;
}

export function LandingPage({ onStartAnalysis, isLoading, error }: LandingPageProps) {
    const [content, setContent] = useState('');
    const [mediaUrls, setMediaUrls] = useState('');
    const [extraFacts, setExtraFacts] = useState('');
    const [showAdvanced, setShowAdvanced] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim()) return;
        const urls = mediaUrls.split('\n').filter(u => u.trim().startsWith('http'));
        onStartAnalysis('paste', content, urls, extraFacts);
    };

    return (
        <div className="min-h-screen bg-slate-900 relative overflow-hidden font-sans selection:bg-blue-500/30">

            {/* Background Ambience */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/20 rounded-full blur-[120px] mix-blend-screen animate-pulse-slow" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[60%] bg-emerald-500/10 rounded-full blur-[100px] mix-blend-screen" />
            </div>

            <div className="relative z-10 container mx-auto px-6 h-screen flex flex-col items-center justify-center">

                {/* Header */}
                <div className="text-center mb-8 space-y-4 max-w-2xl">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/50 border border-slate-700/50 text-blue-400 text-xs font-bold uppercase tracking-widest backdrop-blur-md">
                        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                        Kurvers Property Consulting
                    </div>
                    <h1 className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400 tracking-tight leading-tight">
                        Vastgoed Intelligentie <br />
                        <span className="text-blue-500">Gedecodeerd.</span>
                    </h1>
                </div>

                {/* Card Component */}
                <div className="w-full max-w-2xl bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl overflow-hidden transition-all duration-300 hover:shadow-blue-900/10 hover:border-slate-600/50 group flex flex-col max-h-[85vh]">

                    {/* Header Strip */}
                    <div className="border-b border-slate-700/50 bg-slate-800/30 px-6 py-3 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-500/10 rounded-lg">
                                <ClipboardType className="w-5 h-5 text-blue-400" />
                            </div>
                            <span className="text-xs font-bold text-slate-200 uppercase tracking-widest">
                                Directe Analyse Module
                            </span>
                        </div>
                        <button
                            type="button"
                            onClick={() => setShowAdvanced(!showAdvanced)}
                            className="text-[10px] font-bold text-slate-400 hover:text-blue-400 uppercase tracking-widest transition-colors flex items-center gap-2"
                        >
                            {showAdvanced ? "Simpele Modus" : "Extra Context Toevoegen (Foto's)"}
                            <Plus className={`w-3 h-3 transition-transform ${showAdvanced ? 'rotate-45' : ''}`} />
                        </button>
                    </div>

                    {/* Form Area */}
                    <div className="p-6 overflow-y-auto custom-scrollbar">
                        <form onSubmit={handleSubmit} className="space-y-6">

                            <div className="space-y-2">
                                <label className="block text-[10px] font-bold uppercase tracking-widest text-slate-500 ml-1">
                                    Broncode / Tekst (Funda)
                                </label>

                                <div className="relative group/input">
                                    <textarea
                                        value={content}
                                        onChange={(e) => setContent(e.target.value)}
                                        placeholder="Selecteer alles (Cmd+A), kopieer en plak hier..."
                                        className="w-full h-40 bg-slate-900/50 border-2 border-slate-700 rounded-xl p-4 text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all resize-none text-xs font-mono leading-relaxed"
                                    />
                                    <div className="absolute bottom-3 right-3 pointer-events-none">
                                        <UploadCloud className="w-5 h-5 text-slate-600 group-focus-within/input:text-blue-500 transition-colors" />
                                    </div>
                                </div>
                            </div>

                            {showAdvanced && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2 duration-300">
                                    <div className="space-y-2">
                                        <label className="block text-[10px] font-bold uppercase tracking-widest text-slate-500 ml-1">
                                            Media URLs (Per regel)
                                        </label>
                                        <textarea
                                            value={mediaUrls}
                                            onChange={(e) => setMediaUrls(e.target.value)}
                                            placeholder="https://..."
                                            className="w-full h-24 bg-slate-900/50 border-2 border-slate-700 rounded-xl p-3 text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 text-xs font-mono"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="block text-[10px] font-bold uppercase tracking-widest text-slate-500 ml-1">
                                            Extra Feiten
                                        </label>
                                        <textarea
                                            value={extraFacts}
                                            onChange={(e) => setExtraFacts(e.target.value)}
                                            placeholder="Bijv: Nieuwe CV ketel 2023..."
                                            className="w-full h-24 bg-slate-900/50 border-2 border-slate-700 rounded-xl p-3 text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 text-xs"
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Action Button */}
                            <button
                                type="submit"
                                disabled={isLoading || !content}
                                className={`
                                    w-full py-4 px-6 rounded-xl font-bold flex items-center justify-center gap-3 transition-all transform
                                    ${isLoading || !content
                                        ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-blue-900/20 hover:scale-[1.01] active:scale-[0.99]'
                                    }
                                `}
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Intelligentie Verwerken...
                                    </>
                                ) : (
                                    <>
                                        Start Analyse
                                        <ArrowRight className="w-5 h-5" />
                                    </>
                                )}
                            </button>

                            {error && (
                                <div className="text-center text-red-100 bg-red-900/20 p-3 rounded-lg border border-red-500/20 text-xs font-medium animate-pulse">
                                    {error}
                                </div>
                            )}

                        </form>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 flex gap-8 text-slate-600 text-[10px] font-mono opacity-60 hover:opacity-100 transition-opacity">
                    <span>v2.6.0-Premium</span>
                    <span>•</span>
                    <span>Kurvers Property Consulting</span>
                    <span>•</span>
                    <span>Private & Secure</span>
                </div>

            </div>
        </div>
    );
}
