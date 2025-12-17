import React from 'react';
import { motion } from 'framer-motion';

export const splitLayoutVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.2
        }
    }
};

export const SplitLayout = ({ children }: { children: React.ReactNode }) => {
    return (
        <motion.div
            initial="hidden"
            animate="visible"
            variants={splitLayoutVariants}
            className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-8 xl:gap-12 items-start w-full max-w-[95vw] 2xl:max-w-[1800px] mx-auto px-4 md:px-6 py-8"
        >
            {children}
        </motion.div>
    );
};

export const NarrativeColumn = ({ children }: { children: React.ReactNode }) => {
    return (
        <motion.div
            variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
            className="flex flex-col gap-8"
        >
            {children}
        </motion.div>
    );
};

export const ContextRail = ({ children }: { children: React.ReactNode }) => {
    return (
        <motion.aside
            variants={{ hidden: { opacity: 0, x: 20 }, visible: { opacity: 1, x: 0 } }}
            className="flex flex-col gap-5 sticky top-6 w-full"
        >
            {children}
        </motion.aside>
    );
};
