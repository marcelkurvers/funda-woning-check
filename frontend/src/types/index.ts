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

export interface ReportData {
    runId: string;
    address: string;
    chapters: Record<string, ChapterData>;
    consistency?: ConsistencyItem[];
    property_core?: PropertyCore;
}
