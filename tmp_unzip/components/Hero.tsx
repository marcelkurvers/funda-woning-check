
import React from 'react';

interface HeroProps {
  value: string;
  onChange: (val: string) => void;
  onAnalyze: () => void;
  loading: boolean;
  onClear: () => void;
}

const Hero: React.FC<HeroProps> = ({ value, onChange, onAnalyze, loading, onClear }) => {
  return (
    <section className="w-full max-w-7xl px-4 py-8 md:py-12">
      <div className="@container">
        <div 
          className="relative overflow-hidden rounded-2xl bg-cover bg-center bg-no-repeat min-h-[540px] flex flex-col items-center justify-center text-center p-6 md:p-12 gap-8 shadow-2xl"
          style={{
            backgroundImage: `linear-gradient(rgba(16, 25, 34, 0.7) 0%, rgba(16, 25, 34, 0.95) 100%), url("https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&q=80&w=2070")`
          }}
        >
          <div className="flex flex-col gap-4 max-w-2xl relative z-10">
            <div className="inline-flex items-center justify-center gap-2 self-center rounded-full bg-primary/20 px-4 py-1.5 backdrop-blur-sm border border-primary/30">
              <span className="material-symbols-outlined text-primary text-sm">bolt</span>
              <span className="text-xs font-bold uppercase tracking-wide text-primary">Real-time Analysis</span>
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black leading-tight tracking-tight text-white drop-shadow-sm">
              Instant Funda Property Insights
            </h1>
            <p className="text-slate-300 text-lg md:text-xl font-normal leading-relaxed max-w-xl mx-auto">
              Paste the full page content from Funda.nl below to extract high-res media, analyze price history, and view hidden details.
            </p>
          </div>

          <div className="w-full max-w-2xl relative z-10">
            <div className={`flex flex-col w-full shadow-2xl shadow-primary/10 rounded-xl overflow-hidden ring-4 ring-white/10 focus-within:ring-primary/50 transition-all bg-surface-dark border border-border-dark group ${loading ? 'opacity-70 pointer-events-none' : ''}`}>
              <div className="relative flex-1">
                <div className="absolute top-5 left-4 text-slate-400 pointer-events-none">
                  <span className="material-symbols-outlined text-2xl">content_paste_go</span>
                </div>
                <textarea 
                  value={value}
                  onChange={(e) => onChange(e.target.value)}
                  className="w-full h-32 md:h-40 bg-transparent border-0 text-white placeholder:text-slate-500 focus:ring-0 text-base pl-14 pr-4 py-5 resize-none leading-relaxed" 
                  placeholder="Go to Funda.nl property page.&#10;Select All (Ctrl+A) and Copy (Ctrl+C).&#10;Paste (Ctrl+V) the content here..."
                ></textarea>
              </div>
              <div className="p-2 bg-[#141f2b] border-t border-border-dark flex items-center justify-between">
                <div className="hidden sm:flex items-center gap-2 px-2">
                  <span className="material-symbols-outlined text-slate-500 text-sm">info</span>
                  <span className="text-xs text-slate-400">Paste text & images directly</span>
                </div>
                <div className="flex gap-2 ml-auto">
                  {value && (
                    <button 
                      onClick={onClear}
                      className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg font-bold text-sm transition-colors"
                    >
                      Clear
                    </button>
                  )}
                  <button 
                    onClick={onAnalyze}
                    disabled={loading}
                    className="bg-primary hover:bg-blue-600 disabled:bg-blue-800 text-white px-6 py-2 rounded-lg font-bold text-sm transition-colors flex items-center justify-center gap-2 whitespace-nowrap"
                  >
                    {loading ? (
                      <>
                        <span className="animate-spin material-symbols-outlined">sync</span>
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <span>Analyze Data</span>
                        <span className="material-symbols-outlined text-[20px]">analytics</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
            <p className="mt-3 text-slate-400 text-sm">Supported: Koop, Huur, Nieuwbouw pages</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
