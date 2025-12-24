import React, { useState } from 'react';
import {
    Quote, Info, Target, ShieldCheck, BookOpen, AlertTriangle,
    ChevronDown, ChevronUp, Lightbulb
} from 'lucide-react';

interface MagazineChapterProps {
    content: any;
    chapterId: string;
    media: any[];
    provenance?: any;
}

/**
 * MagazineChapter - Chapters 1-12 Editorial View
 * 
 * ARCHITECTURAL PURPOSE:
 * - Narrative is the PRIMARY content (impossible to miss)
 * - KPIs and tables are SUPPORTING evidence (secondary)
 * - Infoboxes are narrative-derived or hidden
 * 
 * This is an ANALYTICAL ESSAY, not a dashboard.
 */
export const MagazineChapter: React.FC<MagazineChapterProps> = ({ content, chapterId, media, provenance }) => {
    // State for collapsible sections
    const [showSupportingData, setShowSupportingData] = useState(false);
    const [showSidebar, setShowSidebar] = useState(false);

    // 1. Data Sanitization & Prep
    const chapterNumber = parseInt(chapterId);
    const photoIndex = chapterNumber % Math.max(1, media.length);
    const chapterHeroImage = media[photoIndex]?.url;

    // 2. MANDATORY NARRATIVE (chapters 1-12)
    const narrative = content.narrative || content.chapter_data?.narrative;
    const narrativeText = narrative?.text || "";
    const narrativeWordCount = narrative?.word_count || 0;
    const hasNarrative = narrativeText.length > 0;
    const narrativeMissing = !hasNarrative;

    // 3. Supporting data (secondary - collapsed by default)
    const hasVariables = content.variables && Object.keys(content.variables).length > 0;
    const advice = content.advice || [];

    // 4. Derive meaningful sidebar content from narrative
    const sidebarInsights = deriveSidebarInsights(content, narrativeText);

    return (
        <div className="w-full mx-auto bg-white min-h-screen flex flex-col font-sans text-slate-800">

            {/* === COMPACT CHAPTER HEADER === */}
            <header className="relative h-[35vh] flex items-end overflow-hidden">
                <div className="absolute inset-0">
                    <img
                        src={chapterHeroImage || "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1600"}
                        className="absolute inset-0 w-full h-full object-cover"
                        alt="Chapter visual"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/50 to-transparent" />
                </div>

                <div className="relative z-10 w-full max-w-5xl mx-auto px-8 pb-10">
                    <div className="flex items-center gap-2 mb-3">
                        <span className="text-[10px] font-bold text-blue-400 uppercase tracking-[0.4em]">
                            Hoofdstuk {chapterId.padStart(2, '0')}
                        </span>
                        {provenance && (
                            <span className="text-[10px] text-slate-400">
                                · {provenance.provider} {provenance.model}
                            </span>
                        )}
                    </div>

                    <h1 className="text-3xl md:text-4xl font-serif font-bold text-white leading-tight">
                        {content.title || `Analyse Hoofdstuk ${chapterId}`}
                    </h1>
                </div>
            </header>

            {/* === PRIMARY CONTENT: THE NARRATIVE === */}
            <main className="flex-1 w-full max-w-5xl mx-auto px-8">

                {/* NARRATIVE SECTION - MANDATORY, PRIMARY, IMPOSSIBLE TO MISS */}
                <section className="py-12 md:py-16">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 bg-blue-600 rounded-xl">
                            <BookOpen className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-slate-900">Redactionele Analyse</h2>
                            {hasNarrative && (
                                <span className="text-xs text-slate-500">{narrativeWordCount} woorden</span>
                            )}
                        </div>
                    </div>

                    {narrativeMissing ? (
                        /* === ERROR STATE: Narrative Missing === */
                        <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8">
                            <div className="flex items-start gap-4">
                                <AlertTriangle className="w-8 h-8 text-red-500 shrink-0" />
                                <div>
                                    <h3 className="text-xl font-bold text-red-700 mb-2">
                                        Narratief Ontbreekt
                                    </h3>
                                    <p className="text-red-600 mb-4">
                                        Dit hoofdstuk heeft geen redactionele analyse. Dit is een systeemfout.
                                        Elk hoofdstuk (1-12) moet een narratief van minimaal 300 woorden bevatten.
                                    </p>
                                    <p className="text-sm text-red-500">
                                        Foutcode: NARRATIVE_MISSING | Hoofdstuk: {chapterId}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        /* === NARRATIVE CONTENT - THE ESSAY === */
                        <article className="prose prose-lg prose-slate max-w-none">
                            {narrativeText.split('\n\n').map((paragraph: string, idx: number) => (
                                <p
                                    key={idx}
                                    className={`text-lg leading-relaxed text-slate-700 mb-6 ${idx === 0
                                        ? 'first-letter:text-5xl first-letter:font-serif first-letter:font-bold first-letter:float-left first-letter:mr-3 first-letter:leading-none first-letter:text-blue-600'
                                        : ''
                                        }`}
                                >
                                    {paragraph.trim()}
                                </p>
                            ))}
                        </article>
                    )}
                </section>

                {/* === NARRATIVE-DERIVED INSIGHTS (Replaces empty infoboxes) === */}
                {sidebarInsights.length > 0 && (
                    <section className="py-8 border-t border-slate-100">
                        <button
                            onClick={() => setShowSidebar(!showSidebar)}
                            className="w-full flex items-center justify-between py-3 text-left group"
                        >
                            <div className="flex items-center gap-3">
                                <Lightbulb className="w-5 h-5 text-amber-500" />
                                <span className="font-bold text-slate-700">
                                    Kernpunten uit deze analyse
                                </span>
                            </div>
                            {showSidebar ? (
                                <ChevronUp className="w-5 h-5 text-slate-400" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-slate-400" />
                            )}
                        </button>

                        {showSidebar && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                {sidebarInsights.map((insight, idx) => (
                                    <div
                                        key={idx}
                                        className={`p-5 rounded-xl border-l-4 ${insight.type === 'takeaway'
                                            ? 'bg-blue-50 border-blue-500'
                                            : insight.type === 'tension'
                                                ? 'bg-amber-50 border-amber-500'
                                                : 'bg-slate-50 border-slate-300'
                                            }`}
                                    >
                                        <p className={`text-[10px] font-bold uppercase tracking-wider mb-2 ${insight.type === 'takeaway' ? 'text-blue-600'
                                            : insight.type === 'tension' ? 'text-amber-600'
                                                : 'text-slate-500'
                                            }`}>
                                            {insight.label}
                                        </p>
                                        <p className="text-sm text-slate-700 font-medium">
                                            {insight.text}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>
                )}

                {/* === SUPPORTING DATA (KPIs, Variables) - COLLAPSED BY DEFAULT === */}
                {hasVariables && (
                    <section className="py-8 border-t border-slate-100">
                        <button
                            onClick={() => setShowSupportingData(!showSupportingData)}
                            className="w-full flex items-center justify-between py-3 text-left group"
                        >
                            <div className="flex items-center gap-3">
                                <ShieldCheck className="w-5 h-5 text-slate-400" />
                                <span className="font-bold text-slate-700">
                                    Ondersteunende gegevens
                                </span>
                                <span className="text-xs text-slate-400">
                                    ({Object.keys(content.variables).length} datapunten)
                                </span>
                            </div>
                            {showSupportingData ? (
                                <ChevronUp className="w-5 h-5 text-slate-400" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-slate-400" />
                            )}
                        </button>

                        {showSupportingData && (
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-4">
                                {Object.entries(content.variables).map(([key, data]: [string, any]) => (
                                    <div
                                        key={key}
                                        className="bg-slate-50 p-4 rounded-xl border border-slate-100"
                                    >
                                        <div className="flex items-center gap-2 mb-2">
                                            <div className={`w-2 h-2 rounded-full ${data.status === 'fact' ? 'bg-emerald-500' : 'bg-blue-400'
                                                }`} />
                                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wide truncate">
                                                {key.replace(/_/g, ' ')}
                                            </span>
                                        </div>
                                        <div className="text-lg font-bold text-slate-800 break-words">
                                            {data.value || "—"}
                                        </div>
                                        {data.reasoning && (
                                            <div className="mt-2 pt-2 border-t border-slate-100 flex items-start gap-1">
                                                <Info className="w-3 h-3 text-slate-300 shrink-0 mt-0.5" />
                                                <span className="text-[10px] text-slate-400 italic">
                                                    {data.reasoning}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>
                )}

                {/* === VIEWING MISSIONS (if any) === */}
                {advice.length > 0 && (
                    <section className="py-8 border-t border-slate-100">
                        <div className="flex items-center gap-3 mb-6">
                            <Target className="w-5 h-5 text-emerald-600" />
                            <span className="font-bold text-slate-700">Actiepunten</span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {advice.map((item: string, idx: number) => (
                                <div
                                    key={idx}
                                    className="flex items-start gap-3 p-4 bg-emerald-50 rounded-xl border border-emerald-100"
                                >
                                    <span className="text-sm font-bold text-emerald-400 shrink-0">
                                        {(idx + 1).toString().padStart(2, '0')}
                                    </span>
                                    <p className="text-sm text-emerald-800 font-medium">{item}</p>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {/* === CONCLUSION (if present in content) === */}
                {content.conclusion && (
                    <section className="py-12 border-t border-slate-100">
                        <div className="bg-slate-50 rounded-2xl p-8 relative overflow-hidden">
                            <Quote className="absolute top-4 right-4 w-16 h-16 text-slate-100" />
                            <div className="relative z-10">
                                <p className="text-[10px] font-bold text-blue-600 uppercase tracking-wider mb-4">
                                    Conclusie
                                </p>
                                <p className="text-xl md:text-2xl font-serif italic text-slate-800 leading-relaxed">
                                    {content.conclusion.replace(/^"(.*)"$/, '$1')}
                                </p>
                            </div>
                        </div>
                    </section>
                )}
            </main>

            {/* === MINIMAL FOOTER === */}
            <footer className="py-8 px-8 border-t border-slate-100 mt-auto">
                <div className="max-w-5xl mx-auto flex items-center justify-between text-xs text-slate-400">
                    <div className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-blue-400" />
                        <span>Hoofdstuk {chapterId} van 12</span>
                    </div>
                    {provenance && (
                        <span>
                            {provenance.timestamp && new Date(provenance.timestamp).toLocaleString('nl-NL')}
                        </span>
                    )}
                </div>
            </footer>
        </div>
    );
};

/**
 * Derive meaningful sidebar insights from narrative content.
 * These replace empty/factual infoboxes with interpretive statements.
 */
function deriveSidebarInsights(content: any, narrativeText: string): Array<{
    label: string;
    text: string;
    type: 'takeaway' | 'tension' | 'relevance';
}> {
    const insights: Array<{ label: string; text: string; type: 'takeaway' | 'tension' | 'relevance' }> = [];

    // Key takeaway from conclusion
    if (content.conclusion) {
        insights.push({
            label: 'Kernpunt',
            text: content.conclusion.replace(/^"(.*)"$/, '$1').substring(0, 150) + (content.conclusion.length > 150 ? '...' : ''),
            type: 'takeaway'
        });
    }

    // Primary tension from interpretation
    if (content.interpretation) {
        const cleanInterpretation = content.interpretation.replace(/<[^>]*>/g, '');
        if (cleanInterpretation.length > 30) {
            insights.push({
                label: 'AI Interpretatie',
                text: cleanInterpretation.substring(0, 150) + (cleanInterpretation.length > 150 ? '...' : ''),
                type: 'tension'
            });
        }
    }

    // Persona relevance from comparison
    if (content.comparison?.marcel) {
        insights.push({
            label: 'Voor Marcel',
            text: typeof content.comparison.marcel === 'string'
                ? content.comparison.marcel.substring(0, 120)
                : 'Strategische overwegingen beschikbaar.',
            type: 'relevance'
        });
    }

    if (content.comparison?.petra) {
        insights.push({
            label: 'Voor Petra',
            text: typeof content.comparison.petra === 'string'
                ? content.comparison.petra.substring(0, 120)
                : 'Leefbaarheidsaspecten beschikbaar.',
            type: 'relevance'
        });
    }

    // Extract tension from narrative if no other insights
    if (insights.length === 0 && narrativeText.length > 100) {
        // Find sentences with tension indicators
        const sentences = narrativeText.split(/[.!?]+/).filter(s => s.trim().length > 20);
        const tensionSentence = sentences.find(s =>
            s.toLowerCase().includes('echter') ||
            s.toLowerCase().includes('maar') ||
            s.toLowerCase().includes('ondanks') ||
            s.toLowerCase().includes('hoewel')
        );

        if (tensionSentence) {
            insights.push({
                label: 'Spanning',
                text: tensionSentence.trim().substring(0, 150),
                type: 'tension'
            });
        }
    }

    // Only return insights if they add meaning
    return insights.filter(i => i.text.length > 20);
}

export default MagazineChapter;
