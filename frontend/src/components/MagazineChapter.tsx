import React from 'react';
import { Quote, User, Info, Layers, Check, Target, Zap, ShieldCheck, Heart, ArrowRight } from 'lucide-react';

interface MagazineChapterProps {
    content: any;
    chapterId: string;
    media: any[];
    provenance?: any;
}

export const MagazineChapter: React.FC<MagazineChapterProps> = ({ content, chapterId, media, provenance }) => {
    // 1. Data Sanitization & Prep
    const chapterNumber = parseInt(chapterId);
    const photoIndex = chapterNumber % Math.max(1, media.length);
    const chapterHeroImage = media[photoIndex]?.url;

    const marcelData = content.comparison?.marcel;
    const petraData = content.comparison?.petra;

    const hasVariables = content.variables && Object.keys(content.variables).length > 0;
    const analysisHTML = content.main_analysis || "";

    // 2. Logic: Actionable Items
    const viewingMissions = content.advice || [];
    const strengths = content.strengths || [];

    return (
        <div className="w-full mx-auto bg-white shadow-[0_0_100px_rgba(0,0,0,0.1)] overflow-visible min-h-screen flex flex-col font-sans text-emerald-900 border-x border-emerald-100 selection:bg-emerald-100">

            {/* --- TOP MASTHEAD (The 'Expert Ribbon') --- */}
            <div className="bg-emerald-50 py-4 px-12 flex justify-between items-center text-[10px] font-black text-emerald-900 uppercase tracking-[0.5em] border-b border-emerald-200 z-50">
                <div className="flex items-center gap-4">
                    <Layers className="w-5 h-5 text-blue-600" />
                    <span className="hidden md:inline">Expert Advisory Dossier — Private Edition</span>
                </div>
                <div className="flex items-center gap-8">
                    {provenance && (
                        <div className="flex items-center gap-6">
                            <span className="text-blue-600">{provenance.provider} {provenance.model}</span>
                            <div className="h-4 w-px bg-emerald-200" />
                            <span className="text-emerald-600">{provenance.request_count || 0} Enrichments</span>
                        </div>
                    )}
                    <div className="h-4 w-px bg-emerald-200" />
                    <span className="flex items-center gap-3">
                        <Target className="w-3 h-3 text-blue-600" /> Segment {chapterId.padStart(2, '0')}
                    </span>
                </div>
            </div>

            {/* --- DRAMATIC HERO COVER (Ken Burns Effect) --- */}
            <header className="relative h-[65vh] flex items-center justify-center overflow-hidden">
                <div className="absolute inset-0 bg-emerald-950">
                    <img
                        src={chapterHeroImage || "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1600"}
                        className="absolute inset-0 w-full h-full object-cover opacity-40 animate-ken-burns"
                        alt="Hero"
                    />
                    <div className="absolute inset-0 bg-gradient-to-b from-slate-950/60 via-transparent to-slate-950" />
                </div>

                <div className="relative z-10 text-center max-w-7xl px-6">
                    <div className="mb-8 animate-fade-in-up">
                        <span className="text-white text-[12px] font-black tracking-[0.6em] uppercase">{content.segment || "Proprietary Insight Matrix"}</span>
                    </div>

                    <h1 className="text-6xl md:text-8xl 2xl:text-[10rem] font-serif font-black text-white leading-[0.85] tracking-tighter mb-12 drop-shadow-[0_25px_25px_rgba(0,0,0,0.5)]">
                        {content.title || `Chapter ${chapterId}`}
                    </h1>

                    <p className="text-2xl md:text-3xl text-white/95 font-serif font-light italic max-w-3xl mx-auto leading-relaxed drop-shadow-lg grayscale-[50%]">
                        {content.intro || "Strategische exploratie van object-identiteit en marktwaarde."}
                    </p>
                </div>
            </header>

            {/* --- MAIN EDITORIAL BODY --- */}
            <main className="flex-1 bg-white">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-0">

                    {/* === COLUMN 1: THE ANALYSIS (75%) === */}
                    <div className="lg:col-span-9 2xl:col-span-9 border-r border-slate-100">

                        {/* Section Header */}
                        <div className="p-16 md:p-24 lg:p-32 border-b border-slate-50 relative overflow-hidden">
                            <span className="absolute -top-10 -right-10 text-[20rem] font-serif font-black text-slate-50 select-none italic leading-none opacity-50">
                                {chapterId.padStart(2, '0')}
                            </span>
                            <div className="relative z-10 max-w-4xl">
                                <h2 className="text-xs font-black text-blue-600 uppercase tracking-[0.7em] mb-8">Redactionele Analyse</h2>
                                <p className="text-5xl md:text-7xl font-serif font-bold text-slate-800 leading-[1.05] tracking-tighter">
                                    Een ongefilterde evaluatie van wat dit object voor Marcel & Petra betekent.
                                </p>
                            </div>
                        </div>

                        {/* The Narrative Text (Storytelling Mode) */}
                        <div className="p-16 md:p-24 lg:p-32 lg:px-44 relative">
                            <div className="absolute left-16 top-32 bottom-32 w-px bg-gradient-to-b from-blue-500/50 via-slate-100 to-transparent hidden 2xl:block" />

                            <div
                                className="prose prose-slate prose-2xl max-w-none text-slate-700 leading-relaxed font-sans magazine-drop-cap columns-1 md:columns-2 2xl:columns-3 gap-24 prose-headings:font-serif prose-headings:text-slate-900 prose-strong:text-slate-950 prose-p:mb-12"
                                dangerouslySetInnerHTML={{ __html: analysisHTML }}
                            />
                        </div>

                        {/* HET KIJKPLAN (Viewing Mission) */}
                        <div className="p-16 md:p-24 lg:p-32 bg-emerald-50 text-slate-900 relative border-y-8 border-emerald-100">
                            <div className="absolute inset-0 opacity-5 pointer-events-none">
                                <Target className="w-[30rem] h-[30rem] -bottom-20 -right-20 absolute text-emerald-900" />
                            </div>
                            <div className="relative z-10">
                                <div className="flex items-center gap-6 mb-16">
                                    <div className="w-16 h-16 bg-blue-600 rounded-3xl flex items-center justify-center shadow-xl">
                                        <Target className="w-8 h-8 text-white" />
                                    </div>
                                    <h3 className="text-xs font-black uppercase tracking-[0.8em] text-blue-600">Viewing Missions: Het Kijkplan</h3>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-16">
                                    {(Array.isArray(viewingMissions) ? viewingMissions : []).map((m: string, i: number) => (
                                        <div key={i} className="flex gap-6 group">
                                            <span className="text-5xl font-serif italic text-emerald-200 font-black group-hover:text-emerald-400 transition-colors shrink-0">
                                                {(i + 1).toString().padStart(2, '0')}
                                            </span>
                                            <p className="text-lg font-bold text-slate-700 leading-relaxed pt-2">
                                                {m}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* DATA MATRIX (Validated Specs) */}
                        {hasVariables && (
                            <div className="p-16 md:p-24 lg:p-32 bg-slate-50 border-b border-slate-100 relative">
                                <div className="flex justify-between items-center mb-20">
                                    <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.6em]">Gevalideerde Data Matrix</h3>
                                    <ShieldCheck className="w-16 h-16 text-slate-200" />
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-12">
                                    {Object.entries(content.variables).map(([key, data]: [string, any]) => (
                                        <div key={key} className="bg-white p-10 rounded-[2.5rem] shadow-sm border border-slate-100 hover:shadow-xl transition-all group">
                                            <div className="flex items-center gap-3 mb-6">
                                                <div className={`w-3 h-3 rounded-full ${data.status === 'fact' ? 'bg-emerald-500 shadow-emerald-200' : 'bg-blue-400 shadow-blue-200'} shadow-lg`} />
                                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{key.replace(/_/g, ' ')}</span>
                                            </div>
                                            <div className="text-2xl md:text-3xl lg:text-4xl font-black text-slate-900 leading-tight mb-6 break-words">
                                                {data.value || "—"}
                                            </div>
                                            <div className="pt-6 border-t border-slate-50 flex items-center gap-2 text-[10px] font-bold text-slate-400 italic">
                                                <Info className="w-3 h-3" /> {data.reasoning || "Gevalideerde bron"}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* PLUSPUNTEN (Strengths) */}
                        {strengths.length > 0 && (
                            <div className="p-16 md:p-24 lg:p-32 flex flex-col md:flex-row gap-20 items-center">
                                <div className="w-32 h-32 bg-emerald-50 rounded-full flex items-center justify-center border-4 border-emerald-100 shadow-inner">
                                    <Check className="w-16 h-16 text-emerald-500" />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-4xl font-serif font-black text-slate-900 mb-8 italic">Waarom dit object uitblinkt.</h3>
                                    <div className="flex flex-wrap gap-4">
                                        {strengths.map((s: string, i: number) => (
                                            <span key={i} className="px-8 py-3 bg-emerald-600 text-white font-bold text-sm rounded-2xl shadow-lg hover:bg-emerald-700 transition-colors">
                                                {s}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                    </div>

                    {/* === COLUMN 2: THE ADVISORY SIDEBAR (25%) === */}
                    <aside className="lg:col-span-3 2xl:col-span-3 bg-slate-50/20 p-12 space-y-20">
                        <div className="sticky top-12 space-y-16">

                            {/* MARCEL CARD */}
                            <div className="bg-white rounded-[3.5rem] p-12 shadow-2xl border border-blue-100 relative overflow-hidden group border-l-[16px] border-l-blue-600">
                                <div
                                    className="absolute inset-0 bg-blue-600/5 origin-bottom transition-transform duration-1000"
                                    style={{ transform: `scaleY(${(content.marcel_match_score || 0) / 100})` }}
                                />
                                <div className="absolute top-0 right-0 p-8 opacity-[0.03] text-blue-900">
                                    <Zap className="w-48 h-48" />
                                </div>
                                <div className="relative z-10">
                                    <div className="flex items-center justify-between mb-12">
                                        <div className="w-20 h-20 bg-blue-600 rounded-[2rem] flex items-center justify-center shadow-xl rotate-3">
                                            <User className="w-10 h-10 text-white" />
                                        </div>
                                        <div className="text-right">
                                            <div className="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-1">Match Index</div>
                                            <div className="text-4xl font-black text-slate-900">{content.marcel_match_score ? `${Math.round(content.marcel_match_score)}%` : "—"}</div>
                                        </div>
                                    </div>
                                    <h3 className="text-4xl font-serif font-black text-slate-900 mb-2">Marcel</h3>
                                    <p className="text-[11px] font-black text-blue-500 uppercase tracking-[0.4em] mb-12">Strategische Portfolio Check</p>
                                    <p className="text-base text-slate-600 leading-relaxed italic border-t border-slate-100 pt-10 font-medium">
                                        {marcelData || "Analyse van technische parameters..."}
                                    </p>
                                </div>
                            </div>

                            {/* PETRA CARD */}
                            <div className="bg-white rounded-[3.5rem] p-12 shadow-2xl border border-pink-100 relative overflow-hidden group border-l-[16px] border-l-pink-500">
                                <div
                                    className="absolute inset-0 bg-pink-500/5 origin-bottom transition-transform duration-1000"
                                    style={{ transform: `scaleY(${(content.petra_match_score || 0) / 100})` }}
                                />
                                <div className="absolute top-0 right-0 p-8 opacity-[0.03] text-pink-900">
                                    <Heart className="w-48 h-48" />
                                </div>
                                <div className="relative z-10">
                                    <div className="flex items-center justify-between mb-12">
                                        <div className="w-20 h-20 bg-pink-500 rounded-[2rem] flex items-center justify-center shadow-xl -rotate-3">
                                            <User className="w-10 h-10 text-white" />
                                        </div>
                                        <div className="text-right">
                                            <div className="text-[10px] font-black text-pink-500 uppercase tracking-widest mb-1">Mood Score</div>
                                            <div className="text-4xl font-black text-slate-900">{content.petra_match_score ? `${Math.round(content.petra_match_score)}%` : "—"}</div>
                                        </div>
                                    </div>
                                    <h3 className="text-4xl font-serif font-black text-slate-900 mb-2">Petra</h3>
                                    <p className="text-[11px] font-black text-pink-500 uppercase tracking-[0.4em] mb-12">Aesthetic Comfort Index</p>
                                    <p className="text-base text-slate-600 leading-relaxed italic border-t border-slate-100 pt-10 font-medium">
                                        {petraData || "Evaluatie van atmosferische kwaliteiten..."}
                                    </p>
                                </div>
                            </div>

                            {/* NAV ANCHOR */}
                            <button className="w-full py-10 bg-emerald-100 text-emerald-900 rounded-[2.5rem] font-black uppercase tracking-[0.6em] text-[10px] shadow-sm border border-emerald-200 flex items-center justify-center gap-4 group hover:bg-emerald-200 transition-all">
                                scroll voor het verdict
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-3 transition-transform text-emerald-600" />
                            </button>

                        </div>
                    </aside>
                </div>
            </main>

            {/* --- THE SIGNATURE FOOTER --- */}
            <footer className="bg-emerald-50 p-24 text-center relative overflow-hidden border-t-[12px] border-emerald-200">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[600px] bg-blue-100/30 rounded-full blur-[150px] -translate-y-1/2" />
                <div className="relative z-10 max-w-5xl mx-auto">
                    <Quote className="w-56 h-56 text-emerald-900/5 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                    <span className="text-xs font-black text-blue-600 uppercase tracking-[1em] mb-16 block">The Strategic Verdict</span>
                    <h2 className="text-6xl md:text-[6.5rem] font-serif font-black text-slate-900 leading-tight tracking-tight mb-20 italic">
                        {content.conclusion ? content.conclusion.replace(/^"(.*)"$/, '$1') : "Een object van uitzonderlijke statuur."}
                    </h2>
                    {content.interpretation && (
                        <p className="text-2xl md:text-3xl text-slate-600 max-w-4xl mx-auto leading-relaxed italic mb-24 px-12 border-l-4 border-blue-500/30 font-serif">
                            {content.interpretation.replace(/<[^>]*>?/gm, '')}
                        </p>
                    )}
                    <div className="pt-20 border-t border-emerald-200 flex flex-col md:flex-row items-center justify-between gap-12 opacity-80">
                        <div className="flex items-center gap-5 text-left text-slate-900">
                            <Target className="w-8 h-8 text-blue-600" />
                            <div>
                                <div className="text-[10px] font-black uppercase tracking-[0.3em]">Authorized Document</div>
                                <div className="text-sm font-bold">Expert Multi-Check Analyst</div>
                            </div>
                        </div>
                        <div className="h-px w-24 bg-emerald-300 hidden md:block" />
                        <div className="text-[10px] font-black text-slate-500 uppercase tracking-[0.5em]">2024 (c) Global Expertise Dossier</div>
                    </div>
                </div>
            </footer>
        </div>
    );
};
