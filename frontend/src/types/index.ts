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
    chapter_data?: ChapterData; // Recursive or just Any to handle backend envelope
    grid_layout?: any; // For legacy backend support
}

export type SidebarItem =
    | { type: 'advisor_score'; title: string; score: number; content: string }
    | { type: 'advisor_card'; title: string; content: string; icon?: string }
    | { type: 'action_list'; title: string; items: string[] };

export interface ReportData {
    address: string;
    chapters: Record<string, ChapterData>;
}
