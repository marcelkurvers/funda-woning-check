import { motion } from 'framer-motion';
import { CheckCircle2, AlertTriangle, Info } from 'lucide-react';

export type BadgeType = 'success' | 'warning' | 'neutral';

interface BadgeProps {
    type: BadgeType;
    label: string;
}

export const StatusBadge = ({ type, label }: BadgeProps) => {
    const styles = {
        success: 'bg-emerald-50 text-emerald-900 border-emerald-100',
        warning: 'bg-amber-50 text-amber-900 border-amber-100',
        neutral: 'bg-slate-50 text-slate-700 border-slate-100',
    };

    const icons = {
        success: <CheckCircle2 className="w-5 h-5 text-emerald-600" />,
        warning: <AlertTriangle className="w-5 h-5 text-amber-600" />,
        neutral: <Info className="w-5 h-5 text-slate-500" />,
    };

    return (
        <motion.div
            whileHover={{ scale: 1.01, x: 2 }}
            className={`flex items-start gap-3 p-3.5 rounded-xl border transition-all ${styles[type]}`}
        >
            <div className={`p-1 mt-0.5 rounded-md bg-white/60 shrink-0`}>
                {icons[type]}
            </div>
            <span className="text-sm font-semibold leading-snug pt-0.5">{label}</span>
        </motion.div>
    );
};
