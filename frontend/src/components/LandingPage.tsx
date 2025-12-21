import { useState, useEffect } from 'react';
import {
    UploadCloud, ArrowRight, Loader2, ClipboardType,
    Plus, AlertCircle, Zap, ShieldCheck,
    X, ImageIcon, Clipboard, Info, FileText, TrendingUp
} from 'lucide-react';

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
    const [uploadedImages, setUploadedImages] = useState<string[]>([]);
    const [uploadError, setUploadError] = useState<string | null>(null);

    // Global paste listener for images as seen in zip file
    useEffect(() => {
        const handleGlobalPaste = async (e: ClipboardEvent) => {
            const items = e.clipboardData?.items;
            if (!items) return;

            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const blob = items[i].getAsFile();
                    if (!blob) continue;

                    try {
                        const formData = new FormData();
                        formData.append('file', blob, `paste-${Date.now()}.png`);

                        const response = await fetch('/api/upload/image', {
                            method: 'POST',
                            body: formData
                        });

                        if (!response.ok) throw new Error('Upload failed');

                        const { url } = await response.json();
                        setMediaUrls(prev => prev ? `${prev}\n${url}` : url);
                        setUploadedImages(prev => [...prev, url]);
                        setUploadError(null);
                    } catch (err: any) {
                        setUploadError(`Failed to upload image: ${err.message}`);
                    }
                }
            }
        };

        window.addEventListener('paste', handleGlobalPaste);
        return () => window.removeEventListener('paste', handleGlobalPaste);
    }, []);

    const handlePaste = async () => {
        // The global listener handles this if it's an image.
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim() && uploadedImages.length === 0) return;

        const urls = mediaUrls.split('\n')
            .map(u => u.trim())
            .filter(u => u.startsWith('http') || u.startsWith('/uploads/'));

        onStartAnalysis('paste', content, urls, extraFacts);
    };

    return (
        <div className="min-h-screen bg-[#101922] text-white font-sans selection:bg-blue-600/30 overflow-x-hidden">

            {/* Background Ambience */}
            <div className="absolute top-0 left-0 w-full h-[600px] overflow-hidden pointer-events-none opacity-40">
                <div
                    className="absolute inset-0 bg-cover bg-center bg-no-repeat"
                    style={{
                        backgroundImage: `linear-gradient(rgba(16, 25, 34, 0.7) 0%, rgba(16, 25, 34, 1) 100%), url("https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=2070")`
                    }}
                />
            </div>

            <main className="relative z-10 container mx-auto px-4 py-12 flex flex-col items-center">

                {/* Header Section */}
                <div className="text-center mb-12 space-y-6 max-w-4xl animate-in fade-in slide-in-from-top-4 duration-700">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-600/20 border border-blue-500/30 backdrop-blur-sm shadow-xl shadow-blue-900/10">
                        <Zap className="w-4 h-4 text-blue-400 animate-pulse" />
                        <span className="text-xs font-black text-blue-300 uppercase tracking-widest leading-none">Real-time Funda Analysis</span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter leading-[0.95] drop-shadow-2xl">
                        Vastgoed Inzichten <br />
                        <span className="text-blue-500">Direct Gedecodeerd.</span>
                    </h1>

                    <p className="text-lg md:text-xl text-slate-400 font-medium max-w-2xl mx-auto leading-relaxed">
                        Plak de broncode van een Funda.nl pagina en voeg foto's toe voor een diepgaande AI analyse van de woning, de buurt en de waarde.
                    </p>
                </div>

                {/* Main Action Area */}
                <div className="w-full max-w-3xl space-y-8 animate-in fade-in slide-in-from-bottom-6 duration-1000">

                    {/* The Magic Input Box */}
                    <div className="bg-[#192633] rounded-[32px] shadow-2xl border border-slate-800 overflow-hidden ring-1 ring-white/5 transition-all hover:shadow-blue-900/10 active:scale-[0.998]">

                        {/* Box Header */}
                        <div className="border-b border-slate-800/50 bg-slate-900/50 px-8 py-5 flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-blue-600 rounded-2xl shadow-xl shadow-blue-900/30">
                                    <ClipboardType className="w-5 h-5 text-white" />
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-md font-black text-white tracking-tight leading-none">Plak Broncode</span>
                                    <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest mt-1">Stap 1: HTML Data</span>
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={() => setShowAdvanced(!showAdvanced)}
                                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${showAdvanced ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                            >
                                <Plus className={`w-3 h-3 transition-transform ${showAdvanced ? 'rotate-45' : ''}`} />
                                Geavanceerd
                            </button>
                        </div>

                        {/* Input Area */}
                        <div className="p-8">
                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div className="relative group/input">
                                    <textarea
                                        value={content}
                                        onChange={(e) => setContent(e.target.value)}
                                        onPaste={handlePaste}
                                        placeholder="Ga naar Funda -> Rechtsklik 'Paginabron' -> Alles selecteren -> Kopiëren -> Hier plakken..."
                                        className="w-full h-48 bg-slate-900/50 border-2 border-slate-800 focus:border-blue-500 rounded-2xl p-6 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-8 focus:ring-blue-500/10 transition-all resize-none text-[13px] font-mono leading-relaxed"
                                    />
                                    <div className="absolute top-5 left-5 pointer-events-none opacity-20 group-focus-within/input:opacity-0 transition-opacity">
                                        <Clipboard className="w-6 h-6 text-slate-400" />
                                    </div>
                                    {!content && (
                                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                            <div className="flex flex-col items-center gap-2 text-slate-600">
                                                <Info className="w-5 h-5" />
                                                <span className="text-[11px] font-bold uppercase tracking-widest">Wacht op data input...</span>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Multi-Check Pro / Media Zone integration */}
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between px-1">
                                        <div className="flex items-center gap-2">
                                            <ImageIcon className="w-4 h-4 text-blue-500" />
                                            <span className="text-xs font-black uppercase tracking-widest text-slate-400">Media & Foto's</span>
                                        </div>
                                        {uploadedImages.length > 0 && (
                                            <button
                                                type="button"
                                                onClick={() => { setUploadedImages([]); setMediaUrls(''); }}
                                                className="text-[10px] font-bold text-slate-500 hover:text-red-400 transition-colors uppercase tracking-widest"
                                            >
                                                Wis alle foto's
                                            </button>
                                        )}
                                    </div>

                                    {uploadedImages.length > 0 ? (
                                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-slate-900/30 rounded-2xl border border-slate-800/50">
                                            {uploadedImages.map((url, idx) => (
                                                <div key={idx} className="relative group aspect-square rounded-xl overflow-hidden border border-slate-700 shadow-xl bg-slate-800">
                                                    <img src={url} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" alt="Uploaded" />
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            setUploadedImages(prev => prev.filter((_, i) => i !== idx));
                                                            setMediaUrls(prev => prev.split('\n').filter(u => u !== url).join('\n'));
                                                        }}
                                                        className="absolute top-2 right-2 p-1.5 bg-red-500/80 hover:bg-red-500 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-all backdrop-blur-sm"
                                                    >
                                                        <X className="w-3 h-3" />
                                                    </button>
                                                </div>
                                            ))}
                                            <div
                                                className="flex flex-col items-center justify-center border-2 border-dashed border-slate-700/50 rounded-xl bg-slate-800/20 hover:bg-slate-800/40 transition-all cursor-pointer aspect-square text-slate-500 group"
                                                onClick={() => alert("Plak simpelweg meer foto's met Ctrl+V op de pagina!")}
                                            >
                                                <Plus className="w-6 h-6 group-hover:scale-110 transition-transform" />
                                                <span className="text-[10px] font-bold uppercase tracking-widest mt-1">Plak meer</span>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="w-full rounded-2xl border-2 border-dashed border-slate-800 bg-slate-900/20 p-8 flex flex-col items-center justify-center text-center gap-4 transition-all hover:bg-slate-900/30 hover:border-slate-700 group">
                                            <div className="w-16 h-16 rounded-full bg-slate-800/50 flex items-center justify-center group-hover:scale-110 transition-transform">
                                                <UploadCloud className="w-8 h-8 text-slate-500 group-hover:text-blue-500 transition-colors" />
                                            </div>
                                            <div className="space-y-1">
                                                <p className="text-sm font-bold text-slate-300">Kopieer & Plak Foto's</p>
                                                <p className="text-[11px] text-slate-500 max-w-[240px]">Plak direct afbeeldingen van Funda (Ctrl+V) om ze toe te voegen aan de Visuele Audit.</p>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {showAdvanced && (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-4 duration-500">
                                        <div className="space-y-2">
                                            <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">
                                                Media URLs
                                            </label>
                                            <textarea
                                                value={mediaUrls}
                                                onChange={(e) => setMediaUrls(e.target.value)}
                                                placeholder="Handmatige URLs..."
                                                className="w-full h-24 bg-slate-900/50 border-2 border-slate-800 rounded-2xl p-4 text-slate-300 text-[10px] font-mono focus:border-blue-500 focus:outline-none transition-all"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500 ml-1">
                                                Extra Feiten
                                            </label>
                                            <textarea
                                                value={extraFacts}
                                                onChange={(e) => setExtraFacts(e.target.value)}
                                                placeholder="Bijv: Nieuwe vloer 2024..."
                                                className="w-full h-24 bg-slate-900/50 border-2 border-slate-800 rounded-2xl p-4 text-slate-300 text-[10px] focus:border-blue-500 focus:outline-none transition-all"
                                            />
                                        </div>
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    disabled={isLoading || (!content && uploadedImages.length === 0)}
                                    className={`
                                        w-full py-5 rounded-2xl font-black text-xl flex items-center justify-center gap-4 transition-all transform shadow-2xl relative overflow-hidden group/btn
                                        ${isLoading || (!content && uploadedImages.length === 0)
                                            ? 'bg-slate-800 text-slate-600 cursor-not-allowed shadow-none'
                                            : 'bg-blue-600 hover:bg-blue-500 text-white hover:scale-[1.02] active:scale-[0.98] shadow-blue-900/20'
                                        }
                                    `}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="w-6 h-6 animate-spin" />
                                            <span>Analyseren...</span>
                                        </>
                                    ) : (
                                        <>
                                            <span className="relative z-10 flex items-center gap-3">
                                                Start Analyse
                                                <ArrowRight className="w-6 h-6 transition-transform group-hover/btn:translate-x-1" />
                                            </span>
                                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover/btn:animate-shimmer" />
                                        </>
                                    )}
                                </button>

                                {error && (
                                    <div className="flex items-center gap-3 text-rose-400 bg-rose-500/10 p-5 rounded-2xl border border-rose-500/30 text-sm font-bold animate-in fade-in zoom-in">
                                        <AlertCircle className="w-5 h-5 shrink-0" />
                                        {error}
                                    </div>
                                )}

                                {uploadError && (
                                    <div className="flex items-center gap-3 text-amber-400 bg-amber-500/10 p-5 rounded-2xl border border-amber-500/30 text-sm font-bold animate-in fade-in zoom-in">
                                        <ShieldCheck className="w-5 h-5 shrink-0" />
                                        {uploadError}
                                    </div>
                                )}
                            </form>
                        </div>
                    </div>

                    {/* Features Grill - Matching zip vibe */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 opacity-80">
                        <div className="bg-slate-900/50 p-6 rounded-[24px] border border-slate-800/50 flex flex-col items-center text-center gap-4 hover:bg-slate-900 transition-colors">
                            <div className="p-3 bg-emerald-600 rounded-xl shadow-lg shadow-emerald-900/20">
                                <TrendingUp className="w-5 h-5 text-white" />
                            </div>
                            <div className="space-y-1">
                                <h4 className="text-sm font-black text-white uppercase tracking-widest">Marktwaarde</h4>
                                <p className="text-[11px] text-slate-500">Real-time benchmarks op basis van m² prijs en buurtdata.</p>
                            </div>
                        </div>
                        <div className="bg-slate-900/50 p-6 rounded-[24px] border border-slate-800/50 flex flex-col items-center text-center gap-4 hover:bg-slate-900 transition-colors">
                            <div className="p-3 bg-orange-600 rounded-xl shadow-lg shadow-orange-900/20">
                                <ShieldCheck className="w-5 h-5 text-white" />
                            </div>
                            <div className="space-y-1">
                                <h4 className="text-sm font-black text-white uppercase tracking-widest">Risico Scan</h4>
                                <p className="text-[11px] text-slate-500">Detecteer verborgen gebreken en energielabel impact.</p>
                            </div>
                        </div>
                        <div className="bg-slate-900/50 p-6 rounded-[24px] border border-slate-800/50 flex flex-col items-center text-center gap-4 hover:bg-slate-900 transition-colors">
                            <div className="p-3 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-900/20">
                                <FileText className="w-5 h-5 text-white" />
                            </div>
                            <div className="space-y-1">
                                <h4 className="text-sm font-black text-white uppercase tracking-widest">PDF Rapport</h4>
                                <p className="text-[11px] text-slate-500">Exporteer direct naar een premium 12-pagina tellend dossier.</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer Status */}
                <div className="mt-20 flex flex-wrap justify-center gap-8 text-slate-600 text-[10px] font-black uppercase tracking-[0.3em]">
                    <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></div>
                        <span>Phase 4 Vision Active</span>
                    </div>
                    <span>•</span>
                    <span>AI Model: Local Mistral / GPT-4o</span>
                    <span>•</span>
                    <span>Kurvers Property Consulting v3.0</span>
                </div>
            </main>
        </div>
    );
}
