import React from 'react';
import { BentoGrid, BentoCard } from '../layout/BentoLayout';
import {
    ShieldCheck,
    Zap,
    Euro,
    Construction,
    Ruler,
    Info,
    Scale,
    MapPin,
    Sparkles,
    HelpCircle
} from 'lucide-react';
import type { DiscoveryAttribute } from '../../types';

interface DiscoveryBentoProps {
    attributes: DiscoveryAttribute[];
}

const namespaceIcons: Record<string, React.ReactNode> = {
    financial: <Euro className="w-5 h-5 text-emerald-600" />,
    energy: <Zap className="w-5 h-5 text-amber-600" />,
    physical: <Ruler className="w-5 h-5 text-blue-600" />,
    technical: <Construction className="w-5 h-5 text-slate-600" />,
    legal: <Scale className="w-5 h-5 text-indigo-600" />,
    location: <MapPin className="w-5 h-5 text-rose-600" />,
    features: <Sparkles className="w-5 h-5 text-purple-600" />,
    narrative: <Info className="w-5 h-5 text-slate-500" />
};

const namespaceTitles: Record<string, string> = {
    financial: 'Financieel & Kosten',
    energy: 'Energie & Duurzaamheid',
    physical: 'Afmetingen & Ruimte',
    technical: 'Technische Staat',
    legal: 'Juridisch & Erfpacht',
    location: 'Locatie & Omgeving',
    features: 'Kenmerken & Extra\'s',
    narrative: 'Beschrijving & Sfeer'
};

export const DiscoveryBento: React.FC<DiscoveryBentoProps> = ({ attributes }) => {
    if (!attributes || attributes.length === 0) return null;

    // Group attributes by namespace
    const groups = attributes.reduce((acc, attr) => {
        const ns = attr.namespace || 'others';
        if (!acc[ns]) acc[ns] = [];
        acc[ns].push(attr);
        return acc;
    }, {} as Record<string, DiscoveryAttribute[]>);

    return (
        <div className="mt-12 space-y-8 animate-in fade-in slide-in-from-bottom-6 duration-700">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-blue-600 rounded-lg shadow-lg shadow-blue-500/20">
                    <ShieldCheck className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h2 className="text-2xl font-black text-slate-900 tracking-tight leading-none">AI Dynamic Discovery</h2>
                    <p className="text-sm text-slate-500 font-medium">Automatisch ontdekte feiten uit de brontekst.</p>
                </div>
            </div>

            <BentoGrid>
                {Object.entries(groups).map(([ns, attrs]) => (
                    <BentoCard
                        key={ns}
                        title={namespaceTitles[ns] || ns}
                        icon={namespaceIcons[ns] || <HelpCircle className="w-5 h-5 text-slate-400" />}
                        className="col-span-1 md:col-span-1 lg:col-span-1"
                    >
                        <div className="space-y-4">
                            {attrs.map((attr, idx) => (
                                <div key={idx} className="group relative">
                                    <div className="flex justify-between items-start gap-2">
                                        <div className="flex flex-col">
                                            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 leading-none mb-1">
                                                {attr.display_name}
                                            </span>
                                            <span className="text-sm font-bold text-slate-800 break-words">
                                                {attr.value}
                                            </span>
                                        </div>
                                        {attr.confidence > 0 && (
                                            <div
                                                className={`px-1.5 py-0.5 rounded text-[8px] font-black uppercase tracking-tighter ${attr.confidence > 0.8 ? 'bg-emerald-100 text-emerald-700' :
                                                    attr.confidence > 0.5 ? 'bg-amber-100 text-amber-700' :
                                                        'bg-rose-100 text-rose-700'
                                                    }`}
                                                title={`Vertrouwen: ${Math.round(attr.confidence * 100)}%`}
                                            >
                                                {Math.round(attr.confidence * 100)}%
                                            </div>
                                        )}
                                    </div>

                                    {/* Tooltip for explainability */}
                                    {attr.source_snippet && (
                                        <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-full left-0 mb-2 w-48 p-2 bg-slate-900 text-white text-[9px] rounded-lg shadow-xl z-20 pointer-events-none border border-slate-700">
                                            <div className="font-bold text-blue-400 mb-1 leading-none uppercase tracking-widest text-[8px]">Bron Fragment</div>
                                            "{attr.source_snippet}"
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </BentoCard>
                ))}
            </BentoGrid>
        </div>
    );
};
