
import { useState } from 'react';
import { UploadCloud, ArrowRight, Loader2, ClipboardType, Plus, AlertCircle } from 'lucide-react';

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

    const handlePaste = async (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
        const items = e.clipboardData.items;

        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                if (!blob) continue;

                // Prevent default paste behavior for images
                e.preventDefault();

                try {
                    // Upload to backend
                    const formData = new FormData();
                    formData.append('file', blob, `paste-${Date.now()}.png`);

                    const response = await fetch('/api/upload/image', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error('Upload failed');
                    }

                    const { url } = await response.json();

                    // Add to media URLs
                    setMediaUrls(prev => prev ? `${prev}\n${url}` : url);
                    setUploadedImages(prev => [...prev, url]);
                    setUploadError(null);

                } catch (err: any) {
                    setUploadError(`Failed to upload image: ${err.message}`);
                }
            }
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!content.trim()) return;
        const urls = mediaUrls.split('\n').filter(u => u.trim().startsWith('http'));
        onStartAnalysis('paste', content, urls, extraFacts);
    };

    return (
        <div className="min-h-screen bg-slate-50 relative overflow-hidden font-sans selection:bg-blue-100">

            {/* Background Ambience - Light Mode */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-100/50 rounded-full blur-[120px] mix-blend-multiply animate-pulse-slow" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[40%] h-[60%] bg-emerald-100/50 rounded-full blur-[100px] mix-blend-multiply" />
            </div>

            <div className="relative z-10 container mx-auto px-6 h-screen flex flex-col items-center justify-center">

                {/* Header */}
                <div className="text-center mb-10 space-y-6 max-w-2xl">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-blue-100 text-blue-600 text-xs font-bold uppercase tracking-widest shadow-sm">
                        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                        Kurvers Property Consulting
                    </div>
                    <h1 className="text-5xl md:text-6xl font-black text-slate-900 tracking-tight leading-[1.1]">
                        Vastgoed Intelligentie <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Gedecodeerd.</span>
                    </h1>
                    <p className="text-lg text-slate-600 font-medium max-w-lg mx-auto leading-relaxed">
                        Genereer direct een premium analyse rapport door simpelweg de broncode te plakken.
                    </p>
                </div>

                {/* Card Component - White Glass */}
                <div className="w-full max-w-2xl bg-white/80 backdrop-blur-xl border border-white/50 rounded-3xl shadow-2xl shadow-blue-900/5 overflow-hidden ring-1 ring-slate-900/5 flex flex-col max-h-[85vh]">

                    {/* Header Strip */}
                    <div className="border-b border-slate-100 bg-white/50 px-8 py-5 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="p-2.5 bg-blue-600 rounded-xl shadow-lg shadow-blue-600/20">
                                <ClipboardType className="w-5 h-5 text-white" />
                            </div>
                            <div className="flex flex-col">
                                <span className="text-sm font-bold text-slate-900">
                                    Directe Analyse
                                </span>
                                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                                    Plak & Go
                                </span>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <a
                                href="/preferences"
                                className="text-xs font-bold text-slate-500 hover:text-blue-600 bg-slate-50 hover:bg-blue-50 px-3 py-1.5 rounded-lg transition-all flex items-center gap-2 border border-slate-200 hover:border-blue-200"
                            >
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                                Instellingen
                            </a>
                            <button
                                type="button"
                                onClick={() => setShowAdvanced(!showAdvanced)}
                                className="text-xs font-bold text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition-all flex items-center gap-2"
                            >
                                {showAdvanced ? "Simpele Modus" : "Extra Opties"}
                                <Plus className={`w-3 h-3 transition-transform ${showAdvanced ? 'rotate-45' : ''}`} />
                            </button>
                        </div>
                    </div>

                    {/* Form Area */}
                    <div className="p-8 overflow-y-auto custom-scrollbar">
                        <form onSubmit={handleSubmit} className="space-y-6">

                            <div className="space-y-2">
                                <label className="block text-xs font-bold uppercase tracking-widest text-slate-500 ml-1">
                                    Plak hier HTML / Broncode
                                </label>

                                <div className="relative group/input">
                                    <textarea
                                        value={content}
                                        onChange={(e) => setContent(e.target.value)}
                                        onPaste={handlePaste}
                                        placeholder="Ga naar Funda -> Rechtermuisknop 'Bron weergeven' -> Selecteer alles (Cmd+A) -> Kopiëren -> Hier plakken. Je kunt ook afbeeldingen plakken (Cmd+V)..."
                                        className="w-full h-48 bg-slate-50 border-2 border-slate-200 hover:border-blue-200 focus:border-blue-500 rounded-2xl p-5 text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-blue-50 transition-all resize-none text-xs font-mono leading-relaxed shadow-inner"
                                    />
                                    <div className="absolute bottom-4 right-4 pointer-events-none">
                                        <UploadCloud className="w-6 h-6 text-slate-300 group-focus-within/input:text-blue-500 transition-colors" />
                                    </div>
                                </div>
                            </div>

                            {uploadedImages.length > 0 && (
                                <div className="space-y-2">
                                    <label className="block text-xs font-bold uppercase tracking-widest text-slate-500 ml-1">
                                        Geüploade Afbeeldingen ({uploadedImages.length})
                                    </label>
                                    <div className="grid grid-cols-3 gap-2">
                                        {uploadedImages.map((url, idx) => (
                                            <div key={idx} className="relative group">
                                                <img
                                                    src={url}
                                                    className="w-full h-24 object-cover rounded-lg border-2 border-slate-200"
                                                    alt={`Upload ${idx + 1}`}
                                                />
                                                <button
                                                    onClick={() => {
                                                        setUploadedImages(prev => prev.filter((_, i) => i !== idx));
                                                        setMediaUrls(prev => prev.split('\n').filter(u => u !== url).join('\n'));
                                                    }}
                                                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-xs font-bold"
                                                    type="button"
                                                >
                                                    ×
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {uploadError && (
                                <div className="flex items-center gap-3 text-amber-600 bg-amber-50 p-3 rounded-xl border border-amber-100 text-xs font-medium">
                                    <AlertCircle className="w-4 h-4 shrink-0" />
                                    {uploadError}
                                </div>
                            )}

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
                                            className="w-full h-24 bg-slate-50 border-2 border-slate-200 rounded-xl p-3 text-slate-700 text-xs font-mono focus:border-blue-500 focus:outline-none"
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
                                            className="w-full h-24 bg-slate-50 border-2 border-slate-200 rounded-xl p-3 text-slate-700 text-xs focus:border-blue-500 focus:outline-none"
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Action Button */}
                            <button
                                type="submit"
                                disabled={isLoading || !content}
                                className={`
                                    w-full py-5 px-6 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all transform shadow-xl
                                    ${isLoading || !content
                                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed shadow-none'
                                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-blue-600/30 hover:shadow-blue-600/40 hover:scale-[1.01] active:scale-[0.99]'
                                    }
                                `}
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        <span>Analyseren...</span>
                                    </>
                                ) : (
                                    <>
                                        <span>Start Analyse</span>
                                        <ArrowRight className="w-5 h-5 opacity-80" />
                                    </>
                                )}
                            </button>

                            {error && (
                                <div className="flex items-center gap-3 text-rose-600 bg-rose-50 p-4 rounded-xl border border-rose-100 text-sm font-medium animate-in fade-in slide-in-from-top-1">
                                    <AlertCircle className="w-5 h-5 shrink-0" />
                                    {error}
                                </div>
                            )}

                        </form>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 flex gap-8 text-slate-400 text-[10px] font-bold uppercase tracking-widest opacity-80">
                    <span>v2.7.0 Premium</span>
                    <span>•</span>
                    <span>Kurvers Consulting</span>
                    <span>•</span>
                    <span>Secure</span>
                </div>

            </div>
        </div>
    );
}
