
import React from 'react';
import { PropertyAnalysis } from '../types';

interface AnalysisDisplayProps {
  analysis: PropertyAnalysis;
}

const AnalysisDisplay: React.FC<AnalysisDisplayProps> = ({ analysis }) => {
  return (
    <div className="w-full space-y-12 animate-in fade-in duration-700">
      <div className="bg-surface-dark border border-border-dark p-8 rounded-2xl">
        <h2 className="text-3xl font-bold text-white mb-4">{analysis.title}</h2>
        <p className="text-slate-400 text-lg leading-relaxed mb-6">{analysis.summary}</p>
        
        <div className="flex flex-wrap gap-2">
          {analysis.hiddenDetails.map((detail, idx) => (
            <span key={idx} className="px-3 py-1 bg-primary/10 border border-primary/20 text-primary text-xs font-bold rounded-full uppercase">
              {detail}
            </span>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Price History */}
        <div className="bg-surface-dark border border-border-dark p-6 rounded-xl">
          <div className="flex items-center gap-3 mb-6">
            <span className="material-symbols-outlined text-primary">euro_symbol</span>
            <h3 className="text-lg font-bold text-white">Price History</h3>
          </div>
          <div className="space-y-4">
            {analysis.priceHistory.length > 0 ? analysis.priceHistory.map((item, idx) => (
              <div key={idx} className="border-l-2 border-primary/30 pl-4 py-1">
                <p className="text-xs text-slate-500">{item.date}</p>
                <p className="text-sm font-bold text-white">{item.event}</p>
                <p className="text-primary font-bold">{item.price}</p>
              </div>
            )) : <p className="text-slate-500 italic">No price history found in listing.</p>}
          </div>
        </div>

        {/* Sustainability */}
        <div className="bg-surface-dark border border-border-dark p-6 rounded-xl">
          <div className="flex items-center gap-3 mb-6">
            <span className="material-symbols-outlined text-green-500">energy_savings_leaf</span>
            <h3 className="text-lg font-bold text-white">Sustainability</h3>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-500 text-sm">Energy Label</span>
              <span className="px-2 py-0.5 bg-green-500 text-white text-xs font-black rounded">{analysis.sustainability.label}</span>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Insulation</p>
              <p className="text-sm text-slate-300">{analysis.sustainability.insulation}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Potential Improvements</p>
              <p className="text-sm text-slate-300">{analysis.sustainability.potential}</p>
            </div>
          </div>
        </div>

        {/* Neighborhood */}
        <div className="bg-surface-dark border border-border-dark p-6 rounded-xl">
          <div className="flex items-center gap-3 mb-6">
            <span className="material-symbols-outlined text-orange-500">location_on</span>
            <h3 className="text-lg font-bold text-white">Neighborhood</h3>
          </div>
          <div className="space-y-4">
             <div>
              <p className="text-xs text-slate-500 mb-1">Safety & Vibe</p>
              <p className="text-sm text-slate-300">{analysis.neighborhood.safety}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-2">Amenities Nearby</p>
              <div className="flex flex-wrap gap-1">
                {analysis.neighborhood.amenities.map((item, idx) => (
                  <span key={idx} className="px-2 py-0.5 bg-slate-800 text-slate-400 text-[10px] rounded uppercase font-bold border border-slate-700">{item}</span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Demographics</p>
              <p className="text-sm text-slate-300">{analysis.neighborhood.demographics}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisDisplay;
