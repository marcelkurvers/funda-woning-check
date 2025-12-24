import React, { useRef } from 'react';
import {
    BarChart3, BookOpen, Database, Users,
    AlertTriangle, CheckCircle2, XCircle, Info,
    TrendingUp, TrendingDown, Minus
} from 'lucide-react';
import type {
    ChapterPlaneComposition,
    PlaneAVisualModel,
    PlaneBNarrativeModel,
    PlaneCFactModel,
    PlaneDPreferenceModel,
    ChartConfig,
    FactualKPI,
    PreferenceComparison
} from '../types/planes';

interface FourPlaneChapterProps {
    chapter: ChapterPlaneComposition;
    chapterIndex: number;
    media?: { url: string }[];
}

/**
 * FourPlaneChapter - 4-Plane Cognitive Model Layout
 * 
 * UI LAYOUT SPEC (MANDATORY):
 * ┌───────────────┬──────────────────────────────┬──────────────────────┬───────────────────────┐
 * │ PLANE A       │ PLANE B                      │ PLANE C              │ PLANE D               │
 * │ Visuals       │ Narrative (300+ words)       │ KPIs & Data          │ Marcel / Petra        │
 * │ (Left)        │ (Center–Upper)               │ (Center–Lower)       │ (Right)               │
 * └───────────────┴──────────────────────────────┴──────────────────────┴───────────────────────┘
 * 
 * SCROLL BEHAVIOR:
 * - Planes scroll vertically in sync
 * - No plane may collapse another
 * - Narrative must remain visible independently of KPIs
 */
export const FourPlaneChapter: React.FC<FourPlaneChapterProps> = ({
    chapter,
    chapterIndex,
    media = []
}) => {
    // Refs for synchronized scrolling
    const containerRef = useRef<HTMLDivElement>(null);
    const planeARref = useRef<HTMLDivElement>(null);
    const planeBRef = useRef<HTMLDivElement>(null);
    const planeCRef = useRef<HTMLDivElement>(null);
    const planeDRef = useRef<HTMLDivElement>(null);

    // Hero image selection
    const heroImage = media[chapterIndex % Math.max(1, media.length)]?.url ||
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1600";

    return (
        <div className="four-plane-chapter w-full min-h-screen bg-slate-50" ref={containerRef}>
            {/* === CHAPTER HEADER === */}
            <header className="relative h-48 flex items-end overflow-hidden bg-gradient-to-r from-slate-900 to-slate-800">
                <div className="absolute inset-0 opacity-30">
                    <img
                        src={heroImage}
                        className="w-full h-full object-cover"
                        alt=""
                    />
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent" />

                <div className="relative z-10 w-full max-w-[1800px] mx-auto px-6 pb-8">
                    <div className="flex items-center gap-3 mb-2">
                        <span className="text-[10px] font-bold text-blue-400 uppercase tracking-[0.4em]">
                            Hoofdstuk {String(chapter.chapter_id).padStart(2, '0')}
                        </span>
                        <div className="flex gap-1">
                            <span className="w-2 h-2 rounded-full bg-blue-500" title="Plane A" />
                            <span className="w-2 h-2 rounded-full bg-emerald-500" title="Plane B" />
                            <span className="w-2 h-2 rounded-full bg-amber-500" title="Plane C" />
                            <span className="w-2 h-2 rounded-full bg-red-500" title="Plane D" />
                        </div>
                    </div>
                    <h1 className="text-3xl font-serif font-bold text-white">
                        {chapter.chapter_title}
                    </h1>
                </div>
            </header>

            {/* === 4-PLANE GRID LAYOUT === */}
            <div className="four-plane-grid grid grid-cols-12 gap-4 p-4 max-w-[1800px] mx-auto">

                {/* 🟦 PLANE A — VISUAL INTELLIGENCE (Left Column - 3 cols) */}
                <div
                    ref={planeARref}
                    className="plane-a col-span-12 lg:col-span-3 bg-white rounded-2xl shadow-sm border-2 border-blue-100 overflow-hidden"
                >
                    <div className="plane-header bg-blue-50 px-4 py-3 border-b border-blue-100 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-blue-600" />
                        <span className="font-bold text-blue-900 text-sm">Plane A — Visuele Analyse</span>
                    </div>
                    <div className="plane-content p-4 min-h-[400px]">
                        <PlaneAContent plane={chapter.plane_a} />
                    </div>
                </div>

                {/* CENTER COLUMN - Planes B & C stacked (6 cols) */}
                <div className="col-span-12 lg:col-span-6 flex flex-col gap-4">

                    {/* 🟩 PLANE B — NARRATIVE REASONING (Center-Upper) */}
                    <div
                        ref={planeBRef}
                        className="plane-b flex-1 bg-white rounded-2xl shadow-sm border-2 border-emerald-100 overflow-hidden"
                    >
                        <div className="plane-header bg-emerald-50 px-4 py-3 border-b border-emerald-100 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <BookOpen className="w-5 h-5 text-emerald-600" />
                                <span className="font-bold text-emerald-900 text-sm">Plane B — Narratieve Duiding</span>
                            </div>
                            {chapter.plane_b.word_count > 0 && (
                                <span className="text-xs text-emerald-600 font-medium">
                                    {chapter.plane_b.word_count} woorden
                                </span>
                            )}
                        </div>
                        <div className="plane-content p-6 min-h-[500px]">
                            <PlaneBContent plane={chapter.plane_b} />
                        </div>
                    </div>

                    {/* 🟨 PLANE C — FACTUAL ANCHOR (Center-Lower) */}
                    <div
                        ref={planeCRef}
                        className="plane-c bg-white rounded-2xl shadow-sm border-2 border-amber-100 overflow-hidden"
                    >
                        <div className="plane-header bg-amber-50 px-4 py-3 border-b border-amber-100 flex items-center gap-2">
                            <Database className="w-5 h-5 text-amber-600" />
                            <span className="font-bold text-amber-900 text-sm">Plane C — Feitelijke Data</span>
                        </div>
                        <div className="plane-content p-4 min-h-[300px]">
                            <PlaneCContent plane={chapter.plane_c} />
                        </div>
                    </div>
                </div>

                {/* 🟥 PLANE D — HUMAN PREFERENCE (Right Column - 3 cols) */}
                <div
                    ref={planeDRef}
                    className="plane-d col-span-12 lg:col-span-3 bg-white rounded-2xl shadow-sm border-2 border-red-100 overflow-hidden"
                >
                    <div className="plane-header bg-red-50 px-4 py-3 border-b border-red-100 flex items-center gap-2">
                        <Users className="w-5 h-5 text-red-600" />
                        <span className="font-bold text-red-900 text-sm">Plane D — Marcel & Petra</span>
                    </div>
                    <div className="plane-content p-4 min-h-[400px]">
                        <PlaneDContent plane={chapter.plane_d} />
                    </div>
                </div>
            </div>
        </div>
    );
};

// =============================================================================
// 🟦 PLANE A CONTENT - Visual Intelligence
// =============================================================================

const PlaneAContent: React.FC<{ plane: PlaneAVisualModel }> = ({ plane }) => {
    if (plane.not_applicable) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 py-12">
                <Info className="w-8 h-8 mb-2 opacity-50" />
                <p className="text-sm text-center">{plane.not_applicable_reason || 'Geen visuele data beschikbaar'}</p>
            </div>
        );
    }

    if (plane.charts.length === 0 && plane.trends.length === 0 && plane.comparisons.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 py-12">
                <BarChart3 className="w-8 h-8 mb-2 opacity-50" />
                <p className="text-sm">Visuele analyse wordt geladen...</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Render Charts */}
            {plane.charts.map((chart, idx) => (
                <ChartRenderer key={idx} chart={chart} />
            ))}

            {/* Render Trends */}
            {plane.trends.length > 0 && (
                <div className="space-y-2">
                    <h4 className="text-xs font-bold text-blue-600 uppercase tracking-wider">Trends</h4>
                    {plane.trends.map((trend, idx) => (
                        <div key={idx} className="bg-blue-50 rounded-lg p-3">
                            <div className="flex items-center gap-2">
                                {(trend as any).direction === 'up' && <TrendingUp className="w-4 h-4 text-emerald-500" />}
                                {(trend as any).direction === 'down' && <TrendingDown className="w-4 h-4 text-red-500" />}
                                {(trend as any).direction === 'neutral' && <Minus className="w-4 h-4 text-slate-400" />}
                                <span className="text-sm font-medium text-slate-700">{(trend as any).label}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Data Source Attribution */}
            {plane.data_source_ids.length > 0 && (
                <div className="pt-4 border-t border-blue-50">
                    <p className="text-[10px] text-blue-400 uppercase tracking-wider">
                        Databronnen: {plane.data_source_ids.length} registry items
                    </p>
                </div>
            )}
        </div>
    );
};

// Simple chart renderer (can be extended with actual charting library)
const ChartRenderer: React.FC<{ chart: ChartConfig }> = ({ chart }) => {
    const maxValue = chart.max_value || Math.max(...chart.data.map(d => d.value), 100);

    return (
        <div className="chart-container">
            <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-3">
                {chart.title}
            </h4>

            {chart.chart_type === 'bar' && (
                <div className="space-y-2">
                    {chart.data.map((point, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                            <span className="text-xs text-slate-500 w-20 truncate">{point.label}</span>
                            <div className="flex-1 bg-slate-100 rounded-full h-4 overflow-hidden">
                                <div
                                    className="h-full bg-blue-500 rounded-full transition-all duration-500"
                                    style={{ width: `${(point.value / maxValue) * 100}%` }}
                                />
                            </div>
                            <span className="text-xs font-medium text-slate-700 w-12 text-right">
                                {point.value}{point.unit || ''}
                            </span>
                        </div>
                    ))}
                </div>
            )}

            {chart.chart_type === 'radar' && (
                <RadarChart data={chart.data} maxValue={maxValue} />
            )}

            {chart.chart_type === 'gauge' && chart.data[0] && (
                <GaugeChart value={chart.data[0].value} max={maxValue} label={chart.data[0].label} />
            )}

            {!['bar', 'radar', 'gauge'].includes(chart.chart_type) && (
                <div className="bg-blue-50 rounded-lg p-4 text-center text-sm text-blue-600">
                    {chart.chart_type} chart: {chart.data.length} datapunten
                </div>
            )}
        </div>
    );
};

// Simple SVG Radar Chart
const RadarChart: React.FC<{ data: { label: string; value: number }[]; maxValue: number }> = ({ data, maxValue }) => {
    const center = 75;
    const radius = 60;
    const angleStep = (2 * Math.PI) / data.length;

    const points = data.map((d, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const r = (d.value / maxValue) * radius;
        return {
            x: center + r * Math.cos(angle),
            y: center + r * Math.sin(angle),
            labelX: center + (radius + 15) * Math.cos(angle),
            labelY: center + (radius + 15) * Math.sin(angle),
            label: d.label
        };
    });

    const pathData = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';

    return (
        <svg viewBox="0 0 150 150" className="w-full max-w-[200px] mx-auto">
            {/* Background circles */}
            {[0.25, 0.5, 0.75, 1].map((scale, i) => (
                <circle
                    key={i}
                    cx={center}
                    cy={center}
                    r={radius * scale}
                    fill="none"
                    stroke="#E2E8F0"
                    strokeWidth="1"
                />
            ))}
            {/* Axes */}
            {points.map((_p, i) => (
                <line
                    key={i}
                    x1={center}
                    y1={center}
                    x2={center + radius * Math.cos(i * angleStep - Math.PI / 2)}
                    y2={center + radius * Math.sin(i * angleStep - Math.PI / 2)}
                    stroke="#E2E8F0"
                    strokeWidth="1"
                />
            ))}
            {/* Data polygon */}
            <path d={pathData} fill="rgba(59, 130, 246, 0.3)" stroke="#3B82F6" strokeWidth="2" />
            {/* Data points */}
            {points.map((p, i) => (
                <circle key={i} cx={p.x} cy={p.y} r="3" fill="#3B82F6" />
            ))}
            {/* Labels */}
            {points.map((point, i) => (
                <text
                    key={i}
                    x={point.labelX}
                    y={point.labelY}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="text-[8px] fill-slate-500"
                >
                    {point.label.substring(0, 10)}
                </text>
            ))}
        </svg>
    );
};

// Simple Gauge Chart
const GaugeChart: React.FC<{ value: number; max: number; label: string }> = ({ value, max, label }) => {
    const percentage = Math.min((value / max) * 100, 100);
    const rotation = (percentage / 100) * 180 - 90;

    return (
        <div className="flex flex-col items-center">
            <div className="relative w-32 h-16 overflow-hidden">
                <div className="absolute inset-0 rounded-t-full bg-slate-100" />
                <div
                    className="absolute inset-0 rounded-t-full bg-blue-500 origin-bottom transition-transform duration-700"
                    style={{
                        clipPath: 'polygon(50% 100%, 0 0, 100% 0)',
                        transform: `rotate(${rotation}deg)`
                    }}
                />
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2 h-16 bg-slate-800 origin-bottom" style={{ transform: `rotate(${rotation}deg)` }} />
            </div>
            <div className="mt-2 text-center">
                <div className="text-xl font-bold text-slate-800">{value}%</div>
                <div className="text-xs text-slate-500">{label}</div>
            </div>
        </div>
    );
};

// =============================================================================
// 🟩 PLANE B CONTENT - Narrative Reasoning
// =============================================================================

const PlaneBContent: React.FC<{ plane: PlaneBNarrativeModel }> = ({ plane }) => {
    if (plane.not_applicable) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 py-12">
                <Info className="w-8 h-8 mb-2 opacity-50" />
                <p className="text-sm text-center">{plane.not_applicable_reason || 'Geen narratief beschikbaar'}</p>
            </div>
        );
    }

    if (!plane.narrative_text || plane.narrative_text.length === 0) {
        return (
            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
                <div className="flex items-start gap-3">
                    <AlertTriangle className="w-6 h-6 text-red-500 shrink-0" />
                    <div>
                        <h3 className="font-bold text-red-700 mb-1">PLANE VIOLATION ERROR</h3>
                        <p className="text-red-600 text-sm">
                            Output attempted to cross cognitive planes.<br />
                            Narratief ontbreekt. Elk hoofdstuk vereist minimaal 300 woorden.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    // Parse narrative into paragraphs
    const paragraphs = plane.narrative_text.split('\n\n').filter(p => p.trim().length > 0);

    return (
        <article className="prose prose-slate prose-lg max-w-none">
            {paragraphs.map((paragraph, idx) => (
                <p
                    key={idx}
                    className={`text-base leading-relaxed text-slate-700 mb-4 ${idx === 0
                        ? 'first-letter:text-4xl first-letter:font-serif first-letter:font-bold first-letter:float-left first-letter:mr-3 first-letter:leading-none first-letter:text-emerald-600'
                        : ''
                        }`}
                >
                    {paragraph.trim()}
                </p>
            ))}

            {/* AI Provenance */}
            {plane.ai_generated && (
                <div className="mt-6 pt-4 border-t border-emerald-100 flex items-center gap-2 text-xs text-emerald-500">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>
                        AI-gegenereerd
                        {plane.ai_provider && ` door ${plane.ai_provider}`}
                        {plane.ai_model && ` (${plane.ai_model})`}
                    </span>
                </div>
            )}
        </article>
    );
};

// =============================================================================
// 🟨 PLANE C CONTENT - Factual Anchor
// =============================================================================

const PlaneCContent: React.FC<{ plane: PlaneCFactModel }> = ({ plane }) => {
    if (plane.not_applicable) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 py-12">
                <Info className="w-8 h-8 mb-2 opacity-50" />
                <p className="text-sm text-center">{plane.not_applicable_reason || 'Geen data beschikbaar'}</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* KPIs Grid */}
            {plane.kpis.length > 0 && (
                <div className="grid grid-cols-2 gap-3">
                    {plane.kpis.map((kpi, idx) => (
                        <KPICard key={idx} kpi={kpi} />
                    ))}
                </div>
            )}

            {/* Missing Data Indicators */}
            {plane.missing_data.length > 0 && (
                <div className="bg-amber-50 rounded-lg p-3 border border-amber-200">
                    <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="w-4 h-4 text-amber-600" />
                        <span className="text-xs font-bold text-amber-700 uppercase">Ontbrekende Data</span>
                    </div>
                    <ul className="space-y-1">
                        {plane.missing_data.map((item, idx) => (
                            <li key={idx} className="text-xs text-amber-700 flex items-center gap-2">
                                <span className="w-1.5 h-1.5 bg-amber-400 rounded-full" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Uncertainties */}
            {plane.uncertainties.length > 0 && (
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs font-bold text-slate-500 uppercase mb-2">Onzekerheden</div>
                    <ul className="space-y-1">
                        {plane.uncertainties.map((item, idx) => (
                            <li key={idx} className="text-xs text-slate-600">{item}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Data Sources */}
            {plane.data_sources.length > 0 && (
                <div className="pt-3 border-t border-amber-50">
                    <p className="text-[10px] text-amber-400 uppercase tracking-wider">
                        Bronnen: {plane.data_sources.join(', ')}
                    </p>
                </div>
            )}
        </div>
    );
};

const KPICard: React.FC<{ kpi: FactualKPI }> = ({ kpi }) => (
    <div className="bg-amber-50/50 rounded-lg p-3 border border-amber-100">
        <div className="flex items-center gap-2 mb-1">
            <span className={`w-2 h-2 rounded-full ${kpi.provenance === 'fact' ? 'bg-emerald-500' :
                kpi.provenance === 'inferred' ? 'bg-blue-400' :
                    'bg-slate-300'
                }`} />
            <span className="text-[10px] font-bold text-amber-700 uppercase tracking-wider truncate">
                {kpi.label}
            </span>
        </div>
        <div className="text-lg font-bold text-slate-800">
            {kpi.value === null || kpi.value === undefined ? (
                <span className="text-slate-400">—</span>
            ) : (
                <>
                    {String(kpi.value)}
                    {kpi.unit && <span className="text-sm text-slate-500 ml-1">{kpi.unit}</span>}
                </>
            )}
        </div>
        {!kpi.completeness && kpi.missing_reason && (
            <p className="text-[10px] text-amber-600 mt-1 italic">{kpi.missing_reason}</p>
        )}
    </div>
);

// =============================================================================
// 🟥 PLANE D CONTENT - Human Preference
// =============================================================================

const PlaneDContent: React.FC<{ plane: PlaneDPreferenceModel }> = ({ plane }) => {
    if (plane.not_applicable) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 py-12">
                <Info className="w-8 h-8 mb-2 opacity-50" />
                <p className="text-sm text-center">{plane.not_applicable_reason || 'Geen voorkeursdata beschikbaar'}</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Marcel Score Card */}
            <PersonaCard
                name="Marcel"
                score={plane.marcel}
                colorClass="blue"
            />

            {/* Petra Score Card */}
            <PersonaCard
                name="Petra"
                score={plane.petra}
                colorClass="pink"
            />

            {/* Overlap Points */}
            {plane.overlap_points.length > 0 && (
                <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-200">
                    <div className="flex items-center gap-2 mb-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span className="text-xs font-bold text-emerald-700 uppercase">Overeenstemming</span>
                    </div>
                    <ul className="space-y-1">
                        {plane.overlap_points.map((point, idx) => (
                            <li key={idx} className="text-xs text-emerald-700">{point}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Tension Points */}
            {plane.tension_points.length > 0 && (
                <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                    <div className="flex items-center gap-2 mb-2">
                        <XCircle className="w-4 h-4 text-red-500" />
                        <span className="text-xs font-bold text-red-700 uppercase">Spanningspunten</span>
                    </div>
                    <ul className="space-y-1">
                        {plane.tension_points.map((point, idx) => (
                            <li key={idx} className="text-xs text-red-700">{point}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Comparisons */}
            {plane.comparisons.length > 0 && (
                <div className="space-y-2">
                    <div className="text-xs font-bold text-red-600 uppercase tracking-wider">Vergelijkingen</div>
                    {plane.comparisons.map((comparison, idx) => (
                        <ComparisonCard key={idx} comparison={comparison} />
                    ))}
                </div>
            )}

            {/* Joint Synthesis */}
            {plane.joint_synthesis && (
                <div className="bg-gradient-to-br from-red-50 to-pink-50 rounded-lg p-4 border border-red-100">
                    <div className="text-xs font-bold text-red-600 uppercase tracking-wider mb-2">
                        Gezamenlijke Synthese
                    </div>
                    <p className="text-sm text-slate-700">{plane.joint_synthesis}</p>
                </div>
            )}
        </div>
    );
};

const PersonaCard: React.FC<{
    name: string;
    score: { match_score?: number; mood?: string; key_values: string[]; concerns: string[]; summary?: string };
    colorClass: 'blue' | 'pink';
}> = ({ name, score, colorClass }) => {
    const colors = colorClass === 'blue'
        ? { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', accent: 'text-blue-600' }
        : { bg: 'bg-pink-50', border: 'border-pink-200', text: 'text-pink-700', accent: 'text-pink-600' };

    return (
        <div className={`${colors.bg} rounded-lg p-3 border ${colors.border}`}>
            <div className="flex items-center justify-between mb-2">
                <span className={`font-bold ${colors.text}`}>{name}</span>
                {score.match_score !== undefined && (
                    <span className={`text-lg font-bold ${colors.accent}`}>
                        {Math.round(score.match_score)}%
                    </span>
                )}
            </div>

            {score.mood && (
                <div className="flex items-center gap-1 mb-2">
                    <span className={`text-xs ${colors.text}`}>Stemming:</span>
                    <span className={`text-xs font-medium ${score.mood === 'positive' ? 'text-emerald-600' :
                        score.mood === 'negative' ? 'text-red-600' :
                            score.mood === 'mixed' ? 'text-amber-600' :
                                'text-slate-500'
                        }`}>
                        {score.mood === 'positive' ? '😊 Positief' :
                            score.mood === 'negative' ? '😟 Negatief' :
                                score.mood === 'mixed' ? '🤔 Gemengd' :
                                    '😐 Neutraal'}
                    </span>
                </div>
            )}

            {score.key_values.length > 0 && (
                <div className="mb-2">
                    <span className={`text-[10px] font-bold ${colors.text} uppercase`}>Waardeert:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                        {score.key_values.slice(0, 3).map((value, idx) => (
                            <span key={idx} className={`text-[10px] px-2 py-0.5 ${colors.bg} ${colors.text} rounded-full border ${colors.border}`}>
                                {value}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {score.summary && (
                <p className="text-xs text-slate-600 italic">{score.summary}</p>
            )}
        </div>
    );
};

const ComparisonCard: React.FC<{ comparison: PreferenceComparison }> = ({ comparison }) => {
    const alignmentColors = {
        aligned: 'bg-emerald-100 text-emerald-700',
        divergent: 'bg-red-100 text-red-700',
        tension: 'bg-amber-100 text-amber-700',
        complementary: 'bg-blue-100 text-blue-700',
    };

    return (
        <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
            <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-700">{comparison.aspect}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${alignmentColors[comparison.alignment]}`}>
                    {comparison.alignment === 'aligned' ? 'Aligned' :
                        comparison.alignment === 'divergent' ? 'Divergent' :
                            comparison.alignment === 'tension' ? 'Spanning' :
                                'Aanvullend'}
                </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-blue-50 rounded p-2">
                    <div className="font-bold text-blue-600 mb-1">Marcel</div>
                    <div className="text-slate-600">{comparison.marcel_view}</div>
                </div>
                <div className="bg-pink-50 rounded p-2">
                    <div className="font-bold text-pink-600 mb-1">Petra</div>
                    <div className="text-slate-600">{comparison.petra_view}</div>
                </div>
            </div>
            {comparison.requires_discussion && (
                <div className="mt-2 flex items-center gap-1 text-[10px] text-amber-600">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Bespreking vereist</span>
                </div>
            )}
        </div>
    );
};

export default FourPlaneChapter;
