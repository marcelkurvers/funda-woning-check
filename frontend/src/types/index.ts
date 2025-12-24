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
}
