import React from 'react';
import {
    Compass, Layers, AlertTriangle,
    CheckCircle2, XCircle, MapPin, Home, TrendingUp,
    BookOpen, ChevronRight, Sparkles
} from 'lucide-react';

interface OrientationChapterProps {
    content: any;
    chapters: any[];
    media: any[];
    address: string;
    provenance?: any;
    onNavigate: (chapterId: string) => void;
}

/**
 * OrientationChapter - Chapter 0 Special View
 *
 * ARCHITECTURAL PURPOSE:
 * - Frames the report
 * - Previews key tensions
 * - Points to chapters 1-12
 *
 * NOT for long narrative content.
 * NOT for KPI dashboards.
 *
 * This is an ORIENTATION page.
 */
export const OrientationChapter: React.FC<OrientationChapterProps> = ({
    content,
    chapters,
    media,
    address,
    provenance,
    onNavigate
}) => {
    const heroImage = media[0]?.url || "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1600";

    // Extract key tensions from content
    const keyTensions = extractKeyTensions(content);
    const chapterRecommendations = generateChapterRecommendations(content, chapters);

    // Validation state
    const validationState = content?.validation_error || null;

    return (
        <div className="w-full bg-white min-h-screen font-sans text-slate-800">

            {/* === COMPACT ORIENTATION HEADER === */}
            <header className="relative h-[40vh] flex items-end overflow-hidden">
                <div className="absolute inset-0">
                    <img
                        src={heroImage}
                        className="absolute inset-0 w-full h-full object-cover"
                        alt="Property"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/60 to-transparent" />
                </div>

                <div className="relative z-10 w-full max-w-6xl mx-auto px-8 pb-12">
                    <div className="flex items-center gap-2 mb-3">
                        <Compass className="w-4 h-4 text-blue-400" />
                        <span className="text-[10px] font-bold text-blue-400 uppercase tracking-[0.4em]">
                            Rapport Oriëntatie
                        </span>
                    </div>

                    <h1 className="text-4xl md:text-5xl font-serif font-bold text-white leading-tight mb-3">
                        {address || "Analyse Overzicht"}
                    </h1>

                    <p className="text-lg text-white/80 max-w-2xl">
                        {content?.intro || "Uw gepersonaliseerde analyse-routekaart met aandachtspunten."}
                    </p>
                </div>
            </header>

            {/* === VALIDATION STATE (if applicable) === */}
            {validationState && (
                <div className="bg-red-50 border-b-2 border-red-200 px-8 py-4">
                    <div className="max-w-6xl mx-auto flex items-center gap-4">
                        <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
                        <div>
                            <p className="font-bold text-red-700">Validatiefout</p>
                            <p className="text-sm text-red-600">{validationState}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* === MAIN ORIENTATION CONTENT === */}
            <main className="max-w-6xl mx-auto px-8 py-16">

                {/* FRAMING TEXT - Short, not narrative-heavy */}
                <section className="mb-16">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-blue-600 rounded-xl">
                            <Layers className="w-5 h-5 text-white" />
                        </div>
                        <h2 className="text-xl font-bold text-slate-900">Wat vindt u in dit rapport?</h2>
                    </div>

                    <p className="text-lg text-slate-600 leading-relaxed max-w-3xl mb-8">
                        Dit rapport bevat {chapters.length} hoofdstukken met diepgaande analyses.
                        Elk hoofdstuk onderzoekt een specifiek aspect van het object.
                        Hieronder vindt u de belangrijkste spanningspunten en aanbevelingen voor waar te beginnen.
                    </p>
                </section>

                {/* === KEY TENSIONS GRID === */}
                {keyTensions.length > 0 && (
                    <section className="mb-16">
                        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-[0.3em] mb-6">
                            Kernspanningen in dit object
                        </h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {keyTensions.map((tension, idx) => (
                                <div
                                    key={idx}
                                    className={`p-6 rounded-2xl border-2 ${tension.type === 'positive'
                                        ? 'bg-emerald-50 border-emerald-200'
                                        : tension.type === 'negative'
                                            ? 'bg-red-50 border-red-200'
                                            : 'bg-amber-50 border-amber-200'
                                        }`}
                                >
                                    <div className="flex items-start gap-3">
                                        {tension.type === 'positive' && <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />}
                                        {tension.type === 'negative' && <XCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />}
                                        {tension.type === 'neutral' && <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />}
                                        <div>
                                            <p className={`font-bold mb-1 ${tension.type === 'positive' ? 'text-emerald-800'
                                                : tension.type === 'negative' ? 'text-red-800'
                                                    : 'text-amber-800'
                                                }`}>
                                                {tension.title}
                                            </p>
                                            <p className={`text-sm ${tension.type === 'positive' ? 'text-emerald-700'
                                                : tension.type === 'negative' ? 'text-red-700'
                                                    : 'text-amber-700'
                                                }`}>
                                                {tension.description}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {/* === CHAPTER NAVIGATION: "What to read next and why" === */}
                <section className="mb-16">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 bg-slate-900 rounded-xl">
                            <BookOpen className="w-5 h-5 text-white" />
                        </div>
                        <h2 className="text-xl font-bold text-slate-900">Wat te lezen en waarom</h2>
                    </div>

                    <div className="space-y-3">
                        {chapterRecommendations.map((rec) => (
                            <button
                                key={rec.id}
                                onClick={() => onNavigate(rec.id)}
                                className={`w-full text-left p-5 rounded-2xl border transition-all group ${rec.priority === 'high'
                                    ? 'bg-blue-50 border-blue-200 hover:border-blue-400 hover:shadow-lg'
                                    : 'bg-slate-50 border-slate-200 hover:border-slate-300 hover:shadow-md'
                                    }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <span className={`w-10 h-10 flex items-center justify-center rounded-xl font-bold text-sm ${rec.priority === 'high'
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-slate-200 text-slate-600'
                                            }`}>
                                            {rec.id}
                                        </span>
                                        <div>
                                            <h3 className="font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                                                {rec.title}
                                            </h3>
                                            <p className="text-sm text-slate-500">
                                                {rec.reason}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        {rec.priority === 'high' && (
                                            <span className="px-3 py-1 bg-blue-600 text-white text-[10px] font-bold uppercase rounded-full">
                                                Aanbevolen
                                            </span>
                                        )}
                                        <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </section>

                {/* === QUICK METRICS (Compact, not dominant) === */}
                <section className="mb-16">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-[0.3em] mb-6">
                        Kerngegevens op een rij
                    </h3>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { label: 'Vraagprijs', value: content?.variables?.asking_price?.value || '—', icon: TrendingUp },
                            { label: 'Woonoppervlak', value: content?.variables?.woonoppervlakte?.value || '—', icon: Home },
                            { label: 'Locatie', value: address?.split(',')[1]?.trim() || '—', icon: MapPin },
                            { label: 'Match Score', value: content?.marcel_match_score ? `${Math.round((content.marcel_match_score + (content.petra_match_score || 0)) / 2)}%` : '—', icon: Sparkles },
                        ].map((metric, idx) => (
                            <div key={idx} className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                                <div className="flex items-center gap-2 mb-2 text-slate-400">
                                    <metric.icon className="w-4 h-4" />
                                    <span className="text-[10px] font-bold uppercase tracking-wider">{metric.label}</span>
                                </div>
                                <p className="text-lg font-bold text-slate-800">{metric.value}</p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* === PROVENANCE (Subtle) === */}
                {provenance && (
                    <div className="text-center text-xs text-slate-400 pt-8 border-t border-slate-100">
                        <p>
                            Gegenereerd door <span className="font-bold text-blue-500">{provenance.provider} {provenance.model}</span>
                            {provenance.timestamp && ` · ${new Date(provenance.timestamp).toLocaleString('nl-NL')}`}
                        </p>
                    </div>
                )}
            </main>
        </div>
    );
};

// === HELPER FUNCTIONS ===

function extractKeyTensions(content: any): Array<{ title: string; description: string; type: 'positive' | 'negative' | 'neutral' }> {
    const tensions: Array<{ title: string; description: string; type: 'positive' | 'negative' | 'neutral' }> = [];

    // Extract from strengths
    const strengths = content?.strengths || [];
    strengths.slice(0, 2).forEach((s: string) => {
        tensions.push({
            title: 'Pluspunt',
            description: s,
            type: 'positive'
        });
    });

    // Extract from advice (often contains concerns)
    const advice = content?.advice || [];
    advice.slice(0, 2).forEach((a: string) => {
        // Determine if advice implies a concern or neutral observation
        const isNegative = a.toLowerCase().includes('let op') ||
            a.toLowerCase().includes('risico') ||
            a.toLowerCase().includes('controleer') ||
            a.toLowerCase().includes('vraag');
        tensions.push({
            title: isNegative ? 'Aandachtspunt' : 'Onderzoekspunt',
            description: a,
            type: isNegative ? 'negative' : 'neutral'
        });
    });

    // Add interpretation-based tension if available
    if (content?.interpretation) {
        const interpretation = content.interpretation.replace(/<[^>]*>/g, '');
        if (interpretation.length > 50) {
            tensions.push({
                title: 'AI Observatie',
                description: interpretation.substring(0, 150) + '...',
                type: 'neutral'
            });
        }
    }

    return tensions.slice(0, 6);
}

function generateChapterRecommendations(_content: any, chapters: any[]): Array<{ id: string; title: string; reason: string; priority: 'high' | 'normal' }> {
    // Filter to chapters 1-12 only
    const analysisChapters = chapters.filter(c => {
        const id = parseInt(c.id);
        return id >= 1 && id <= 12;
    }).sort((a, b) => parseInt(a.id) - parseInt(b.id));

    return analysisChapters.map((chapter: any) => {
        const id = parseInt(chapter.id);
        const title = chapter.title || chapter.chapter_data?.title || `Hoofdstuk ${id}`;

        // Generate contextual reasons based on chapter type
        let reason = 'Gedetailleerde analyse van dit onderwerp.';
        let priority: 'high' | 'normal' = 'normal';

        // Priority logic based on chapter type
        if (id === 1) {
            reason = 'Fundamentele woningkenmerken en specificaties.';
            priority = 'high';
        } else if (id === 2) {
            reason = 'Buurt, voorzieningen en locatiekwaliteit.';
        } else if (id === 3) {
            reason = 'Marktpositie en prijsvergelijking.';
            priority = 'high';
        } else if (id === 4) {
            reason = 'Energieprestatie en verduurzaming.';
        } else if (id === 5) {
            reason = 'Onderhoudsstaat en renovatiebehoeften.';
        } else if (id === 6) {
            reason = 'Bouwkundige aspecten en constructie.';
        } else if (id === 7) {
            reason = 'Juridische en administratieve zaken.';
        } else if (id === 8) {
            reason = 'Financiële doorrekening en scenario\'s.';
            priority = 'high';
        } else if (id === 9) {
            reason = 'Toekomstperspectief en ontwikkelpotentieel.';
        } else if (id === 10) {
            reason = 'Risico-analyse en mitigatie.';
        } else if (id === 11) {
            reason = 'Onderhandelingsstrategie en tactieken.';
        } else if (id === 12) {
            reason = 'Eindoordeel en aanbevelingen.';
            priority = 'high';
        }

        return {
            id: chapter.id,
            title: title.replace(/^\d+\.\s*/, ''), // Remove leading number
            reason,
            priority
        };
    });
}

export default OrientationChapter;
