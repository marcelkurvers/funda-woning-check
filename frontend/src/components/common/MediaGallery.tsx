import React from 'react';
import { Image as ImageIcon, ExternalLink, ShieldCheck, Camera } from 'lucide-react';


interface MediaItem {
    url: string;
    caption?: string;
    ordering: number;
    provenance: string;
}

interface MediaGalleryProps {
    media: MediaItem[];
}

export const MediaGallery: React.FC<MediaGalleryProps> = ({ media }) => {
    if (!media || media.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-12 bg-white rounded-2xl border border-dashed border-slate-200">
                <ImageIcon className="w-12 h-12 text-slate-300 mb-4" />
                <p className="text-slate-500 font-medium">Geen media gevonden voor deze woning.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                        <Camera className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-slate-800">Media Bibliotheek</h2>
                        <p className="text-sm text-slate-500">Geëxtraheerd via Multi-Check Pro Link</p>
                    </div>
                </div>
                <div className="flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-bold rounded-full border border-emerald-100">
                    <ShieldCheck className="w-3 h-3" />
                    VERIFIEERD
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {media.map((item, idx) => (
                    <div
                        key={idx}
                        className="group relative bg-white rounded-xl overflow-hidden border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300"
                    >
                        <div className="aspect-[4/3] overflow-hidden">
                            <img
                                src={item.url}
                                alt={item.caption || `Foto ${idx + 1}`}
                                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                loading="lazy"
                                onError={(e) => {
                                    (e.target as HTMLImageElement).src = "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?q=80&w=800&auto=format&fit=crop";
                                }}
                            />
                        </div>

                        {/* Overlay Info */}
                        <div className="p-3">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
                                    {item.provenance} • #{item.ordering}
                                </span>
                                <a
                                    href={item.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="p-1 hover:bg-slate-100 rounded-md transition-colors"
                                >
                                    <ExternalLink className="w-3 h-3 text-slate-400" />
                                </a>
                            </div>
                            <p className="text-sm text-slate-700 font-medium line-clamp-1 h-5">
                                {item.caption || "Geen beschrijving"}
                            </p>
                        </div>

                        {/* Hover Effects */}
                        <div className="absolute inset-x-0 bottom-0 top-[auto] h-1 bg-blue-600 scale-x-0 group-hover:scale-x-100 transition-transform origin-left" />
                    </div>
                ))}
            </div>
        </div>
    );
};
