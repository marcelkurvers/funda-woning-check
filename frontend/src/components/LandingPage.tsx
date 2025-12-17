
import { useState } from 'react';
import { UploadCloud, ArrowRight, CheckCircle2, Loader2, ClipboardType } from 'lucide-react';

interface LandingPageProps {
    onStartAnalysis: (type: 'url' | 'paste', content: string) => Promise<void>;
    isLoading: boolean;
    error?: string | null;
}

export function LandingPage({ onStartAnalysis, isLoading, error }: LandingPageProps) {
    const [content, setContent] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim()) return;
        // Always use 'paste' mode as URL scraping is disabled
        onStartAnalysis('paste', content);
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
                <div className="text-center mb-12 space-y-4 max-w-2xl">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/50 border border-slate-700/50 text-blue-400 text-xs font-bold uppercase tracking-widest backdrop-blur-md">
                        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                        AI Woning Analist
                    </div>
                    <h1 className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400 tracking-tight leading-tight">
                        Vastgoed Intelligentie <br />
                        <span className="text-blue-500">Gedecodeerd.</span>
                    </h1>
                    <p className="text-lg text-slate-400 font-medium leading-relaxed">
                        Genereer in enkele seconden een diepgaand aankoopadvies.
                        Plak de woninginformatie en krijg direct inzicht.
                    </p>
                </div>

                {/* Card Component */}
                <div className="w-full max-w-xl bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl overflow-hidden transition-all duration-300 hover:shadow-blue-900/10 hover:border-slate-600/50 group">

                    {/* Header Strip (Visual only now) */}
                    <div className="border-b border-slate-700/50 bg-slate-800/30 px-6 py-4 flex items-center gap-3">
                        <div className="p-2 bg-blue-500/10 rounded-lg">
                            <ClipboardType className="w-5 h-5 text-blue-400" />
                        </div>
                        <span className="text-sm font-bold text-slate-200">
                            Directe Analyse Module
                        </span>
                    </div>

                    {/* Form Area */}
                    <div className="p-6 md:p-8">
                        <form onSubmit={handleSubmit} className="space-y-6">

                            <div className="space-y-2">
                                <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 ml-1">
                                    Plak Woning Informatie (HTML/Tekst)
                                </label>

                                <div className="relative group/input">
                                    <textarea
                                        value={content}
                                        onChange={(e) => setContent(e.target.value)}
                                        placeholder="Selecteer alle tekst (Ctrl+A) op de Funda pagina, kopieer en plak het hier..."
                                        className="w-full h-48 bg-slate-900/50 border-2 border-slate-700 rounded-xl p-4 text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all resize-none text-sm font-mono leading-relaxed"
                                    />
                                    <div className="absolute bottom-3 right-3 pointer-events-none">
                                        <UploadCloud className="w-5 h-5 text-slate-600 group-focus-within/input:text-blue-500 transition-colors" />
                                    </div>
                                </div>
                            </div>

                            {/* Info Note */}
                            <div className="flex gap-3 bg-slate-900/30 p-4 rounded-lg border border-slate-700/50">
                                <div className="mt-0.5 shrink-0">
                                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                                </div>
                                <p className="text-xs text-slate-400 leading-relaxed">
                                    Voor het beste resultaat: open de woningpagina op Funda, selecteer alles (Ctrl+A / Cmd+A), kopieer en plak hier.
                                </p>
                            </div>

                            {/* Action Button */}
                            <button
                                type="submit"
                                disabled={isLoading || !content}
                                className={`
                  w-full py-4 px-6 rounded-xl font-bold flex items-center justify-center gap-3 transition-all transform
                  ${isLoading || !content
                                        ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-blue-900/20 hover:scale-[1.02] active:scale-[0.98]'
                                    }
                `}
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        Analyseren...
                                    </>
                                ) : (
                                    <>
                                        Start Analyse
                                        <ArrowRight className="w-5 h-5" />
                                    </>
                                )}
                            </button>

                            {error && (
                                <div className="text-center text-red-400 text-sm font-medium animate-fade-in">
                                    {error}
                                </div>
                            )}

                        </form>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-12 flex gap-8 text-slate-600 text-xs font-mono opacity-60 hover:opacity-100 transition-opacity">
                    <span>v2.5.0-PasteOnly</span>
                    <span>•</span>
                    <span>Powered by Deepseek R1</span>
                    <span>•</span>
                    <span>Local Privacy</span>
                </div>

            </div>
        </div>
    );
}
