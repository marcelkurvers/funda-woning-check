import type { ReactNode } from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import type { ConsistencyItem } from '../../types';

interface DataVerifierProps {
    field: string;
    children: ReactNode;
    consistency?: ConsistencyItem[];
    debugMode: boolean;
    className?: string; // Wrapper classes
}

export const DataVerifier = ({ field, children, consistency, debugMode, className = "" }: DataVerifierProps) => {
    if (!debugMode || !consistency) {
        return <>{children}</>;
    }

    const item = consistency.find(c => c.field === field);

    // Status Logic
    const isMismatch = item?.status === 'mismatch';
    const isOk = item?.status === 'ok';

    if (isMismatch) {
        return (
            <div className={`relative group border-2 border-red-500 border-dashed rounded-lg p-1 bg-red-50/50 ${className}`}>
                {children}
                <div className="absolute -top-3 -right-3 bg-red-500 text-white rounded-full p-1 shadow-sm">
                    <AlertCircle className="w-3 h-3" />
                </div>

                {/* Tooltip */}
                <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-white rounded-lg shadow-xl border border-red-100 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity text-xs">
                    <p className="font-bold text-red-600 mb-1">Data Inconsistentie</p>
                    <p className="text-slate-600 mb-2">{item?.message}</p>
                    <div className="grid grid-cols-2 gap-2 text-[10px]">
                        <div className="bg-slate-50 p-1 rounded">
                            <span className="font-bold block text-slate-400">BRON</span>
                            <span className="font-mono">{item?.source}</span>
                        </div>
                        <div className="bg-red-50 p-1 rounded">
                            <span className="font-bold block text-red-400">RAPPORT</span>
                            <span className="font-mono">{item?.parsed}</span>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (isOk) {
        return (
            <div className={`relative group border border-emerald-400/30 rounded-lg p-0.5 bg-emerald-50/10 ${className}`}>
                {children}
                <div className="absolute -top-1.5 -right-1.5 bg-emerald-500 text-white rounded-full p-[2px] shadow-sm opacity-50 group-hover:opacity-100 transition-opacity">
                    <CheckCircle2 className="w-2 h-2" />
                </div>
            </div>
        );
    }

    return <>{children}</>;
};
