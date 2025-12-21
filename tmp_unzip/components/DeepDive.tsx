
import React from 'react';

const DeepDive: React.FC = () => {
  return (
    <section className="w-full py-12 mb-12">
      <div className="flex flex-col gap-8">
        <div className="px-2">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">Deep Dive Data</h2>
          <p className="text-slate-500 dark:text-slate-400 mt-2 max-w-2xl text-lg">Get comprehensive insights beyond the standard listing page.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="group p-6 rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-surface-dark hover:border-primary/50 transition-colors shadow-sm dark:shadow-none">
            <div className="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-primary mb-4 group-hover:scale-110 transition-transform">
              <span className="material-symbols-outlined text-3xl">euro_symbol</span>
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Price History</h3>
            <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
              Track listing price changes over time. See original asking prices and adjustments made by the seller.
            </p>
          </div>
          <div className="group p-6 rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-surface-dark hover:border-primary/50 transition-colors shadow-sm dark:shadow-none">
            <div className="w-12 h-12 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400 mb-4 group-hover:scale-110 transition-transform">
              <span className="material-symbols-outlined text-3xl">energy_savings_leaf</span>
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Energy & Sustainability</h3>
            <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
              Detailed breakdown of energy labels, insulation quality, and potential sustainability improvements.
            </p>
          </div>
          <div className="group p-6 rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-surface-dark hover:border-primary/50 transition-colors shadow-sm dark:shadow-none">
            <div className="w-12 h-12 rounded-lg bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600 dark:text-orange-400 mb-4 group-hover:scale-110 transition-transform">
              <span className="material-symbols-outlined text-3xl">location_on</span>
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Neighborhood Stats</h3>
            <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
              Demographics, safety scores, and amenities nearby. Understand the area before you visit.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DeepDive;
