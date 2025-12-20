import type { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface BentoGridProps {
    children: ReactNode;
    className?: string;
}

interface BentoCardProps {
    children: ReactNode;
    className?: string; // For Tailwind col-span/row-span overrides
    title?: string | ReactNode;
    icon?: ReactNode;
    delay?: number;
    variant?: 'default' | 'primary' | 'highlight' | 'alert' | 'ghost';
}

export const BentoGrid = ({ children, className = "" }: BentoGridProps) => {
    return (
        <div className={`grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3 auto-rows-[minmax(120px,auto)] p-0 max-w-[2560px] mx-auto ${className}`}>
            {children}
        </div>
    );
};

export const BentoCard = ({ children, className = "", title, icon, delay = 0, variant = 'default' }: BentoCardProps) => {
    // Determine base styles based on variant
    const variants = {
        default: "bg-white border-slate-200",
        primary: "bg-gradient-to-br from-blue-600 to-indigo-700 text-white border-transparent",
        highlight: "bg-amber-50 border-amber-200",
        alert: "bg-red-50 border-red-200",
        ghost: "bg-transparent border-transparent shadow-none !p-0"
    };

    const textColors = variant === 'primary' ? "text-white" : "text-slate-800";

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay }}
            className={`
                group relative overflow-hidden rounded-2xl border p-6 shadow-sm hover:shadow-md transition-shadow
                flex flex-col
                ${variants[variant] || variants.default}
                ${className}
            `}
        >
            {/* Header */}
            {(title || icon) && (
                <div className="flex items-center gap-3 mb-4">
                    {icon && (
                        <div className={`p-2 rounded-lg ${variant === 'primary' ? 'bg-white/20' : 'bg-slate-100'}`}>
                            {icon}
                        </div>
                    )}
                    {title && (
                        <h3 className={`font-bold text-lg tracking-tight ${textColors}`}>
                            {title}
                        </h3>
                    )}
                </div>
            )}

            {/* Content */}
            <div className={`flex-1 ${variant === 'primary' ? 'text-blue-50' : 'text-slate-600'}`}>
                {children}
            </div>
        </motion.div>
    );
};
