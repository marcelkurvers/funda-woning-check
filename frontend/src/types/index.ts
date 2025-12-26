/**
 * BACKBONE CONTRACT: CoreSummary
 * 
 * This is the MANDATORY top-level object in every report.
 * It contains core property data that is ALWAYS available,
 * independent of AI, chapters, or planes.
 * 
 * The UI MUST read dashboard KPIs from this object ONLY.
 */

export type DataStatus = 'present' | 'unknown' | 'n/a';

export interface CoreField {
    value: string;              // Human-readable formatted value
    raw_value?: any;            // Raw value for programmatic use
    status: DataStatus;         // Data availability status
    source: string;             // Registry key or source identifier
    unit?: string;              // Unit for display (e.g., m², €)
}

export interface CoreSummary {
    // === REQUIRED FIELDS (always present) ===
    asking_price: CoreField;
    living_area: CoreField;
    location: CoreField;
    match_score: CoreField;

    // === OPTIONAL FIELDS (present if available) ===
    property_type?: CoreField;
    build_year?: CoreField;
    energy_label?: CoreField;
    plot_area?: CoreField;
    bedrooms?: CoreField;

    // === METADATA ===
    completeness_score: number;     // 0.0-1.0
    registry_entry_count: number;
    provenance: Record<string, string>;
}

/**
 * Mandatory narrative contract for each chapter.
 * 
 * Every chapter (0-12) MUST produce a narrative of at least 300 words.
 * This is NOT optional. Frontend MUST render this.
 */
export interface NarrativeContract {
    text: string;
    word_count: number;
}

export interface ChapterData {
    id: string;
    title: string;
    intro?: string;
    main_analysis?: string; // HTML string
    conclusion?: string;
    interpretation?: string;
    strengths?: string[];
    advice?: string[] | string;
    sidebar_items?: SidebarItem[];
    metrics?: any[]; // Array of metric objects
    hero?: any;      // Hero section data
    chapter_data?: ChapterData;
    grid_layout?: any;
    provenance?: {
        provider: string;
        model: string;
        timestamp: string;
        confidence: 'low' | 'medium' | 'high';
        inferred_variables?: string[];
        factual_variables?: string[];
    };
    missing_critical_data?: string[];
    // MANDATORY NARRATIVE FIELD (chapters 0-12)
    narrative?: NarrativeContract;

    // 4-PLANE STRUCTURE (MANDATORY for chapters 0-12)
    plane_structure?: boolean;
    plane_a?: {
        plane: 'A';
        charts: any[];
        trends: any[];
        comparisons: any[];
        data_source_ids: string[];
        not_applicable: boolean;
        not_applicable_reason?: string;
    };
    plane_b?: {
        plane: 'B';
        narrative_text: string;
        word_count: number;
        not_applicable: boolean;
        ai_generated: boolean;
        ai_provider?: string;
        ai_model?: string;
    };
    plane_c?: {
        plane: 'C';
        kpis: any[];
        missing_data: string[];
        uncertainties: string[];
        not_applicable: boolean;
    };
    plane_d?: {
        plane: 'D';
        marcel: any;
        petra: any;
        comparisons: any[];
        overlap_points: string[];
        tension_points: string[];
        joint_synthesis?: string;
        not_applicable: boolean;
    };
}

export type SidebarItem =
    | { type: 'advisor_score'; title: string; score: number; content: string }
    | { type: 'advisor_card'; title: string; content: string; icon?: string }
    | { type: 'action_list'; title: string; items: string[] };

export interface ConsistencyItem {
    field: string;
    status: 'ok' | 'mismatch' | 'missing_source';
    source?: string;
    parsed?: string;
    message?: string;
}

export interface PropertyCore {
    media_urls?: string[];
    asking_price_eur?: string;
    living_area_m2?: number;
    plot_area_m2?: number;
    build_year?: number;
    energy_label?: string;
    address?: string;
    [key: string]: any;
}

export interface DiscoveryAttribute {
    namespace: string;
    key: string;
    display_name: string;
    value: string;
    confidence: number;
    source_snippet?: string;
}

export interface MediaItem {
    url: string;
    caption?: string;
    ordering: number;
    provenance: string;
}

export interface ReportData {
    runId: string;
    address: string;
    chapters: Record<string, ChapterData>;
    consistency?: ConsistencyItem[];
    property_core?: PropertyCore;
    discovery?: DiscoveryAttribute[];
    media_from_db?: MediaItem[];
    // === BACKBONE CONTRACT: CoreSummary is MANDATORY ===
    core_summary: CoreSummary;
}

// Re-export 4-Plane Cognitive Model types
export * from './planes';

