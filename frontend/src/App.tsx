import { useState, useEffect } from 'react';
import { BentoGrid, BentoCard } from './components/layout/BentoLayout';
import { Target, ListChecks, ChevronRight, Loader2, AlertCircle, Sparkles, AlertTriangle, CheckCircle2, TrendingUp, BookOpen, Plus } from 'lucide-react';
import { LandingPage } from './components/LandingPage';
import { AIStatusIndicator } from './components/AIStatusIndicator';
import type { ReportData } from './types';

function App() {
  const [activeChapterId, setActiveChapterId] = useState("0");
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchLatestRun() {
      try {
        const runsRes = await fetch('/runs');
        if (!runsRes.ok) throw new Error('Failed to fetch runs');
        const runs = await runsRes.json();

        if (runs && runs.length > 0) {
          const latestRunId = runs[0].id;
          const reportRes = await fetch(`/runs/${latestRunId}/report`);
          if (!reportRes.ok) throw new Error('Failed to fetch report');
          const data = await reportRes.json();

          setReport({
            address: data.property_core?.address || "Onbekend Adres",
            chapters: data.chapters || {}
          });
        } else {
          setReport(null);
        }
      } catch (err: any) {
        console.error(err);
        setError(err.message || 'Er is een fout opgetreden bij het laden van de gegevens.');
      } finally {
        setLoading(false);
      }
    }

    fetchLatestRun();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-slate-500">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <p className="font-medium">Rapport laden...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-xl shadow-xl max-w-md w-full border border-red-100">
          <div className="flex items-center gap-3 text-red-600 mb-4">
            <AlertCircle className="w-6 h-6" />
            <h3 className="font-bold text-lg">Foutmelding</h3>
          </div>
          <p className="text-slate-600 mb-6">{error}</p>
          <button onClick={() => window.location.reload()} className="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium py-2 px-4 rounded-lg transition-colors">
            Opnieuw proberen
          </button>
        </div>
      </div>
    );
  }

  const handleStartAnalysis = async (type: 'url' | 'paste', content: string) => {
    setLoading(true);
    setError(null);
    try {
      const runBody = type === 'paste'
        ? { funda_url: "manual-paste", funda_html: content }
        : { funda_url: content, funda_html: null };

      const createRes = await fetch('/runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(runBody)
      });

      if (!createRes.ok) throw new Error('Kon geen nieuwe analyse starten');
      const { run_id } = await createRes.json();

      const startRes = await fetch(`/runs/${run_id}/start`, { method: 'POST' });
      if (!startRes.ok) throw new Error('Kon de analyse niet uitvoeren');

      const reportRes = await fetch(`/runs/${run_id}/report`);
      if (!reportRes.ok) throw new Error('Kon het rapport niet ophalen');
      const data = await reportRes.json();

      setReport({
        address: data.property_core?.address || "Onbekend Adres",
        chapters: data.chapters || {}
      });

      setActiveChapterId("0");

    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Er ging iets mis bij het starten.');
    } finally {
      setLoading(false);
    }
  };

  if (!report) {
    return (
      <LandingPage
        onStartAnalysis={handleStartAnalysis}
        isLoading={loading}
        error={error}
      />
    );
  }

  const currentChapter = report.chapters[activeChapterId];
  const content = currentChapter?.chapter_data || currentChapter;
  const sortedChapters = Object.values(report.chapters).sort((a: any, b: any) => parseInt(a.id) - parseInt(b.id));

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">

      {/* Sidebar Navigation - Fixed Width */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex-shrink-0 h-full flex flex-col z-50 shadow-xl">
        <div className="p-6 border-b border-slate-800">
          <button
            onClick={() => setReport(null)}
            className="text-left group w-full"
          >
            <div className="text-white font-bold text-lg mb-1 tracking-tight group-hover:text-blue-400 transition-colors">AI Woning Rapport</div>
            <div className="text-xs text-slate-500 font-mono truncate" title={report.address}>{report.address}</div>
          </button>
        </div>

        <div className="px-4 py-4">
          <button
            onClick={() => setReport(null)}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 hover:bg-blue-600 hover:text-white transition-all duration-200 group font-bold shadow-lg shadow-blue-900/20"
          >
            <Plus className="w-5 h-5 text-blue-400 group-hover:text-white" />
            <span>Nieuwe Analyse</span>
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
          {sortedChapters.map((chapter: any) => (
            <button
              key={chapter.id}
              onClick={() => setActiveChapterId(chapter.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group ${activeChapterId === chapter.id
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                : 'hover:bg-slate-800 hover:text-white'
                }`}
            >
              <span className={`flex-shrink-0 w-6 h-6 flex items-center justify-center rounded text-xs font-bold transition-colors ${activeChapterId === chapter.id ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-500 group-hover:bg-slate-700 group-hover:text-slate-300'
                }`}>
                {chapter.id}
              </span>
              <span className="truncate text-left">{chapter.title || `Hoofdstuk ${chapter.id}`}</span>
              {activeChapterId === String(chapter.id) && <ChevronRight className="w-4 h-4 ml-auto opacity-75" />}

            </button>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-800">
          <a href="/preferences" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-all">
            <span>Instellingen</span>
          </a>
        </div>
      </aside>

      {/* Main Content - No Window Scroll */}
      <main className="flex-1 min-w-0 flex flex-col h-full overflow-hidden bg-slate-100/50">

        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between shadow-sm shrink-0 z-40">
          <div className="flex items-center gap-4">
            <div className="bg-blue-100 text-blue-700 font-bold px-3 py-1 rounded-md text-sm border border-blue-200 shadow-sm">
              Hfdst {currentChapter?.id || 0}
            </div>
            <h1 className="text-xl font-bold text-slate-800">{content?.title || currentChapter?.title || "Analyse"}</h1>
          </div>
          <div className="flex items-center gap-6">
            <AIStatusIndicator />
            <div className="flex items-center gap-2 px-3 py-1 bg-slate-100 rounded-md border border-slate-200">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-500"></div>
              <div className="text-[10px] uppercase font-bold text-slate-500 tracking-tighter">Live Versie</div>
            </div>
          </div>
        </header>

        {/* Dashboard Grid Area */}
        {currentChapter && content ? (
          <div className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">

            {/* THE BENTO GRID */}
            <BentoGrid>

              {/* 1. Intro Box - Wide Top Left */}
              {content.intro && (
                <BentoCard className="col-span-1 md:col-span-2 lg:col-span-2 row-span-1" title="Samenvatting" icon={<BookOpen className="w-5 h-5 text-blue-600" />}>
                  <div className="text-lg text-slate-700 leading-relaxed font-medium">
                    {content.intro}
                  </div>
                </BentoCard>
              )}

              {/* 2. AI Insight / Hero - Prominent Top Right / Center */}
              {content.interpretation && (
                <BentoCard
                  className="col-span-1 md:col-span-3 lg:col-span-3 row-span-1"
                  variant="primary"
                  title="AI Interpretatie"
                  icon={<Sparkles className="w-5 h-5 text-yellow-300" />}
                >
                  <div
                    className="prose prose-invert prose-lg leading-snug !max-w-none"
                    dangerouslySetInnerHTML={{ __html: content.interpretation }}
                  />
                </BentoCard>
              )}

              {/* 3. Metrics & Scores (From Sidebar Items) - 1x1 Tiles */}
              {content.sidebar_items?.map((item: any, idx: number) => {
                if (item.type === 'advisor_score') {
                  return (
                    <BentoCard key={'score-' + idx} className="col-span-1 md:col-span-1" title={item.title} icon={<TrendingUp className="w-5 h-5 text-blue-600" />}>
                      <div className="flex items-end gap-2 mt-2">
                        <span className="text-5xl font-black text-blue-600 tracking-tighter">{item.score}</span>
                        <span className="text-sm font-medium text-slate-500 mb-2">/ 100</span>
                      </div>
                      <p className="mt-4 text-sm text-slate-500 line-clamp-3">{item.content}</p>
                    </BentoCard>
                  );
                }
                if (item.type === 'advisor_card' || item.type === 'advisor') {
                  return (
                    <BentoCard key={'advisor-' + idx} className="col-span-1 md:col-span-1" title={item.title} icon={<Sparkles className="w-5 h-5 text-blue-500" />}>
                      <div className="text-sm text-slate-600 leading-relaxed" dangerouslySetInnerHTML={{ __html: item.content }} />
                    </BentoCard>
                  );
                }
                return null;
              })}

              {/* 3.1 Key Property Metrics */}
              {content.metrics?.filter((m: any) => m.id !== 'default_metric').map((metric: any, idx: number) => (
                <BentoCard
                  key={'metric-' + idx}
                  className="col-span-1"
                  title={metric.label}
                  variant={metric.color === 'red' ? 'alert' : metric.color === 'orange' ? 'highlight' : 'default'}
                >
                  <div className="flex flex-col">
                    <span className="text-2xl font-black text-slate-900">{metric.value}</span>
                    {metric.explanation && <p className="mt-2 text-xs text-slate-500 font-medium leading-tight">{metric.explanation}</p>}
                    {metric.trend_text && <span className="mt-1 text-[10px] font-bold uppercase text-blue-600 tracking-wider">{metric.trend_text}</span>}
                  </div>
                </BentoCard>
              ))}


              {/* 4. Strengths - Vertical or Square */}
              {content.strengths && content.strengths.length > 0 && (
                <BentoCard className="col-span-1 md:col-span-1 lg:col-span-1 row-span-2" title="Sterke Punten" icon={<CheckCircle2 className="w-5 h-5 text-emerald-600" />}>
                  <div className="flex flex-col gap-3">
                    {content.strengths.map((str: string, i: number) => (
                      <div key={i} className="flex items-start gap-2 p-2 rounded bg-emerald-50 border border-emerald-100/50">
                        <div className="min-w-[4px] h-4 mt-1.5 rounded-full bg-emerald-500" />
                        <span className="text-sm font-medium text-emerald-900">{str}</span>
                      </div>
                    ))}
                  </div>
                </BentoCard>
              )}

              {/* 5. Main Analysis - The 'Meat' - Large Block */}
              {content.main_analysis && (
                <BentoCard
                  className="col-span-1 md:col-span-2 lg:col-span-2 row-span-2"
                  title="Diepte Analyse"
                  icon={<TrendingUp className="w-5 h-5 text-blue-600" />}
                >
                  <div
                    className="prose prose-slate max-w-none text-sm md:text-base leading-relaxed
                                   prose-p:mb-4 prose-headings:text-slate-800 prose-headings:font-bold prose-headings:text-sm prose-headings:uppercase prose-headings:tracking-wider"
                    dangerouslySetInnerHTML={{ __html: content.main_analysis }}
                  />
                </BentoCard>
              )}

              {/* 6. Risks / Advice - 1x1 or Vert */}
              {content.advice && (
                <BentoCard className="col-span-1 md:col-span-1 lg:col-span-1" title="Aandachtspunten" icon={<AlertTriangle className="w-5 h-5 text-amber-500" />} variant="alert">
                  <div className="prose prose-sm prose-ul:pl-4 prose-li:marker:text-amber-500" dangerouslySetInnerHTML={{ __html: typeof content.advice === 'string' ? content.advice : '' }} />
                  {Array.isArray(content.advice) && (
                    <div className="flex flex-col gap-2">
                      {content.advice.map((adv: string, i: number) => (
                        <div key={i} className="text-sm text-amber-900 bg-amber-50 p-2 rounded border border-amber-100">{adv}</div>
                      ))}
                    </div>
                  )}
                </BentoCard>
              )}

              {/* 7. Action Items (Sidebar) */}
              {content.sidebar_items?.map((item: any, idx: number) => {
                if (item.type === 'action_list') {
                  return (
                    <BentoCard key={'action-' + idx} className="col-span-1" title={item.title} icon={<ListChecks className="w-5 h-5 text-slate-500" />}>
                      <ul className="space-y-2 mt-2">
                        {item.items.map((act: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                            <input type="checkbox" className="mt-1 rounded border-slate-300 text-blue-600" />
                            <span>{act}</span>
                          </li>
                        ))}
                      </ul>
                    </BentoCard>
                  )
                }
                return null;
              })}

              {/* 8. Conclusion - Full Width Bottom Banner style */}
              {content.conclusion && (
                <BentoCard
                  className="col-span-1 md:col-span-3 lg:col-span-5 !bg-slate-900 !border-slate-800"
                  variant="default" // Overridden by class
                >
                  <div className="flex flex-col md:flex-row items-center gap-6 text-center md:text-left h-full justify-center">
                    <div className="p-3 bg-white/10 rounded-full">
                      <Target className="w-8 h-8 text-yellow-400" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-yellow-500 uppercase tracking-widest mb-2">Conclusie van de Expert</h4>
                      <p className="text-xl md:text-2xl font-serif italic text-white leading-relaxed">"{content.conclusion}"</p>
                    </div>
                  </div>
                </BentoCard>
              )}

            </BentoGrid>

          </div>
        ) : (
          <div className="flex items-center justify-center flex-1 h-full text-slate-400">
            <div className="text-center">
              <p className="text-lg font-medium">Selecteer een hoofdstuk</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
