import { motion } from 'framer-motion';

interface WidgetCardProps {
    title: React.ReactNode;
    children: React.ReactNode;
    delay?: number;
}

export const WidgetCard = ({ title, children, delay = 0 }: WidgetCardProps) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay }}
            className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 hover:shadow-md transition-shadow"
        >
            <h4 className="font-bold text-slate-800 text-sm uppercase tracking-wide mb-3 flex items-center gap-2">
                {title}
            </h4>
            <div className="text-sm text-slate-600">
                {children}
            </div>
        </motion.div>
    );
};
