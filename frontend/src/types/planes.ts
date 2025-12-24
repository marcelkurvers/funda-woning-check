/**
 * 4-PLANE COGNITIVE MODEL - TypeScript Types
 * 
 * This module defines the frontend types for the 4-Plane Enforced Analytical Report System.
 * Each plane has EXCLUSIVE responsibility. No output may cross planes. EVER.
 * 
 * PLANES:
 * 🟦 PLANE A — VISUAL INTELLIGENCE PLANE (LEFT)
 *     Purpose: Pattern recognition & pre-verbal insight
 * 
 * 🟩 PLANE B — NARRATIVE REASONING PLANE (CENTER–UPPER)
 *     Purpose: Meaning, interpretation, judgment (300+ words)
 * 
 * 🟨 PLANE C — FACTUAL ANCHOR PLANE (CENTER–LOWER)
 *     Purpose: Verifiable truth & completeness
 * 
 * 🟥 PLANE D — HUMAN PREFERENCE PLANE (RIGHT)
 *     Purpose: Personal relevance & divergence (Marcel vs Petra)
 */

// =============================================================================
// 🟦 PLANE A — VISUAL INTELLIGENCE PLANE
// =============================================================================

export interface VisualDataPoint {
    label: string;
    value: number;
    unit?: string;
    color?: string;
}

export interface ChartConfig {
    chart_type: 'radar' | 'bar' | 'line' | 'heatmap' | 'area' | 'comparison' | 'delta' | 'sparkline' | 'gauge';
    title: string;
    data: VisualDataPoint[];
    max_value?: number;
    show_legend?: boolean;
}

export interface PlaneAVisualModel {
    plane: 'A';
    plane_name: 'visual_intelligence';
    charts: ChartConfig[];
    trends: Record<string, unknown>[];
    comparisons: Record<string, unknown>[];
    data_source_ids: string[];
    not_applicable: boolean;
    not_applicable_reason?: string;
}

// =============================================================================
// 🟩 PLANE B — NARRATIVE REASONING PLANE
// =============================================================================

export interface PlaneBNarrativeModel {
    plane: 'B';
    plane_name: 'narrative_reasoning';
    narrative_text: string;
    word_count: number;
    not_applicable: boolean;
    not_applicable_reason?: string;
    ai_generated: boolean;
    ai_provider?: string;
    ai_model?: string;
}

// =============================================================================
// 🟨 PLANE C — FACTUAL ANCHOR PLANE
// =============================================================================

export interface FactualKPI {
    key: string;
    label: string;
    value: unknown;
    unit?: string;
    provenance: 'fact' | 'inferred' | 'unknown';
    registry_id?: string;
    completeness: boolean;
    missing_reason?: string;
}

export interface PlaneCFactModel {
    plane: 'C';
    plane_name: 'factual_anchor';
    kpis: FactualKPI[];
    parameters: Record<string, unknown>;
    data_sources: string[];
    missing_data: string[];
    uncertainties: string[];
    not_applicable: boolean;
    not_applicable_reason?: string;
}

// =============================================================================
// 🟥 PLANE D — HUMAN PREFERENCE PLANE
// =============================================================================

export interface PersonaScore {
    match_score?: number;
    mood?: 'positive' | 'neutral' | 'negative' | 'mixed';
    key_values: string[];
    concerns: string[];
    summary?: string;
}

export interface PreferenceComparison {
    aspect: string;
    marcel_view: string;
    petra_view: string;
    alignment: 'aligned' | 'divergent' | 'tension' | 'complementary';
    requires_discussion: boolean;
}

export interface PlaneDPreferenceModel {
    plane: 'D';
    plane_name: 'human_preference';
    marcel: PersonaScore;
    petra: PersonaScore;
    comparisons: PreferenceComparison[];
    overlap_points: string[];
    tension_points: string[];
    joint_synthesis?: string;
    not_applicable: boolean;
    not_applicable_reason?: string;
}

// =============================================================================
// CHAPTER PLANE COMPOSITION
// =============================================================================

export interface ChapterPlaneComposition {
    chapter_id: number;
    chapter_title: string;
    plane_a: PlaneAVisualModel;
    plane_b: PlaneBNarrativeModel;
    plane_c: PlaneCFactModel;
    plane_d: PlaneDPreferenceModel;
}

// =============================================================================
// FULL REPORT STRUCTURE
// =============================================================================

export interface FourPlaneReport {
    chapter_0: ChapterPlaneComposition;
    chapters: Record<number, ChapterPlaneComposition>;
    property_address: string;
    generated_at: string;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

export type PlaneType = 'A' | 'B' | 'C' | 'D';

export interface PlaneViolation {
    chapter_id: number;
    plane: PlaneType;
    violation_type: string;
    description: string;
    severity: 'error' | 'warning';
}

// Helper to check if a plane is applicable
export function isPlaneApplicable(plane: PlaneAVisualModel | PlaneBNarrativeModel | PlaneCFactModel | PlaneDPreferenceModel): boolean {
    return !plane.not_applicable;
}

// Helper to get plane color
export function getPlaneColor(plane: PlaneType): string {
    const colors: Record<PlaneType, string> = {
        'A': '#3B82F6', // Blue
        'B': '#10B981', // Green/Emerald
        'C': '#F59E0B', // Yellow/Amber
        'D': '#EF4444', // Red
    };
    return colors[plane];
}

// Helper to get plane label
export function getPlaneLabel(plane: PlaneType): string {
    const labels: Record<PlaneType, string> = {
        'A': 'Visuele Analyse',
        'B': 'Narratieve Duiding',
        'C': 'Feitelijke Data',
        'D': 'Marcel & Petra',
    };
    return labels[plane];
}
