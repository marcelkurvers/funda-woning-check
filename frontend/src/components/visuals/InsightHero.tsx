import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

interface InsightHeroProps {
    content: string;
    title?: string;
    variant?: 'blue' | 'purple' | 'indigo';
}

export const InsightHero = ({ content, title = "AI Interpretatie", variant = 'blue' }: InsightHeroProps) => {
    const gradients = {
        blue: 'bg-gradient-to-br from-blue-600 to-indigo-700',
        purple: 'bg-gradient-to-br from-purple-600 to-fuchsia-700',
        indigo: 'bg-gradient-to-br from-indigo-600 to-violet-700',
    };

    return (
        <motion.div
            layout
            whileHover={{ y: -2 }}
            className={`rounded-2xl p-6 shadow-lg text-white ${gradients[variant]}`}
        >
            <div className="flex items-center gap-3 mb-4 border-b border-white/20 pb-3">
                <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
                    <Sparkles className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-lg tracking-wide uppercase">{title}</h3>
            </div>

            <div
                className="text-white/95 leading-relaxed font-medium prose prose-invert prose-p:my-0"
                dangerouslySetInnerHTML={{ __html: content }}
            />
        </motion.div>
    );
};
