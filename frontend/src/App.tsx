import { useState, useEffect } from 'react';
import { SplitLayout, NarrativeColumn, ContextRail } from './components/layout/SplitLayout';
import { InsightHero } from './components/visuals/InsightHero';
import { StatusBadge } from './components/visuals/StatusBadge';
import { WidgetCard } from './components/visuals/WidgetCard';
import { Target, ListChecks, ChevronRight, Loader2, AlertCircle } from 'lucide-react';
import { LandingPage } from './components/LandingPage';
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

          // Transform backend data to frontend model
          setReport({
            address: data.property_core?.address || "Onbekend Adres",
            chapters: data.chapters || {}
          });
        } else {
          // No runs exist
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
      // 1. Create Run
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

      // 2. Start Processing
      const startRes = await fetch(`/runs/${run_id}/start`, { method: 'POST' });
      if (!startRes.ok) throw new Error('Kon de analyse niet uitvoeren');

      // 3. Fetch Result
      const reportRes = await fetch(`/runs/${run_id}/report`);
      if (!reportRes.ok) throw new Error('Kon het rapport niet ophalen');
      const data = await reportRes.json();

      setReport({
        address: data.property_core?.address || "Onbekend Adres",
        chapters: data.chapters || {}
      });

      // Select first chapter by default
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
        isLoading={loading} // Re-using loading state here might need care if we want separate 'submitting' state, but acceptable for now
        error={error}
      />
    );
  }

  // Fallback if the selected chapter doesn't exist in the data (e.g. if we add new chapters to UI that aren't in DB yet)
  const currentChapter = report.chapters[activeChapterId];

  // Unwrap chapter_data if it exists (Backend Pydantic model structure), otherwise use direct fields (Legacy/Demo structure)
  const content = currentChapter?.chapter_data || currentChapter;

  // Sort chapters numerically
  const sortedChapters = Object.values(report.chapters).sort((a: any, b: any) => parseInt(a.id) - parseInt(b.id));

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans text-slate-900">

      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex-shrink-0 h-screen sticky top-0 overflow-y-auto flex flex-col shadow-2xl z-40">
        <div className="p-6 border-b border-slate-800">
          <div className="text-white font-bold text-lg mb-1 tracking-tight">AI Woning Rapport</div>
          <div className="text-xs text-slate-500 font-mono truncate" title={report.address}>{report.address}</div>
        </div>
        <nav className="flex-1 p-4 space-y-1">
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
              {activeChapterId === chapter.id && <ChevronRight className="w-4 h-4 ml-auto opacity-75" />}
            </button>
          ))}
        </nav>


        <div className="p-4 border-t border-slate-800">
          <a
            href="/preferences"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-all group"
          >
            <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded bg-slate-800 text-slate-500 group-hover:bg-slate-700 group-hover:text-slate-300">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </span>
            <span>Instellingen</span>
          </a>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 min-w-0 flex flex-col">
        {currentChapter && content ? (
          <>
            {/* Header Strip */}
            <header className="bg-white border-b border-slate-200 sticky top-0 z-30 px-8 py-4 flex items-center justify-between shadow-sm/50 backdrop-blur-md bg-white/90">
              <div className="flex items-center gap-4">
                <div className="bg-blue-100 text-blue-700 font-bold px-3 py-1 rounded-md text-sm border border-blue-200">
                  Hfdst {currentChapter.id}
                </div>
                <h1 className="text-xl font-bold text-slate-800">{content.title || currentChapter.title}</h1>
              </div>
              <div className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
                <div className="text-sm text-slate-500 font-medium">Live Versie</div>
              </div>
            </header>

            {/* Main Magazine Layout */}
            <div className="flex-1 pb-20">
              <SplitLayout>

                {/* LEFT COLUMN: Narrative */}
                <NarrativeColumn>
                  {/* Intro */}
                  {content.intro && (
                    <div className="text-xl md:text-2xl font-medium text-slate-700 leading-relaxed border-l-4 border-blue-500 pl-6 py-1 mb-8">
                      {content.intro}
                    </div>
                  )}

                  {/* Prose Analysis */}
                  {content.main_analysis ? (
                    <div
                      className="prose prose-lg prose-slate max-w-none 
                    prose-headings:font-bold prose-headings:text-slate-800 
                    prose-p:text-slate-600 prose-p:leading-8
                    prose-li:text-slate-600 mb-12"
                      dangerouslySetInnerHTML={{ __html: content.main_analysis }}
                    />
                  ) : (
                    // Fallback for Legacy/HTML-Blob Chapters
                    currentChapter.grid_layout?.main?.content && (
                      <div
                        className="prose prose-lg prose-slate max-w-none mb-12 legacy-content"
                        dangerouslySetInnerHTML={{ __html: currentChapter.grid_layout.main.content }}
                      />
                    )
                  )}

                  {/* Conclusion */}
                  {content.conclusion && (
                    <div className="bg-slate-900 text-slate-50 rounded-xl p-6 flex gap-4 items-start shadow-xl shadow-slate-200/50 mt-auto">
                      <div className="bg-white/10 p-2 rounded-full shrink-0">
                        <Target className="w-6 h-6 text-yellow-400" />
                      </div>
                      <div>
                        <h4 className="font-bold text-yellow-400 uppercase tracking-wider text-xs mb-2">Conclusie</h4>
                        <p className="font-medium text-lg text-slate-100 italic">"{content.conclusion}"</p>
                      </div>
                    </div>
                  )}
                </NarrativeColumn>

                {/* RIGHT COLUMN: Context Rail */}
                <ContextRail>

                  {/* 1. Hero Insight (Primary Visual) */}
                  {content.interpretation && (
                    <InsightHero content={content.interpretation} />
                  )}

                  {/* 2. Pros (Badge Grid) */}
                  {content.strengths && content.strengths.length > 0 && (
                    <WidgetCard title={<><span className="text-emerald-600">●</span> Sterke Punten</>} delay={0.1}>
                      <div className="grid gap-3">
                        {content.strengths.map((str: string, i: number) => (
                          <StatusBadge key={i} type="success" label={str} />
                        ))}
                      </div>
                    </WidgetCard>
                  )}

                  {/* 3. Cons (Badge Grid) */}
                  {content.advice && (
                    <WidgetCard title={<><span className="text-amber-500">●</span> Aandachtspunten</>} delay={0.2}>
                      <div className="grid gap-3">
                        {(Array.isArray(content.advice) ? content.advice : [content.advice]).map((adv: string, i: number) => (
                          <StatusBadge key={i} type="warning" label={adv} />
                        ))}
                      </div>
                    </WidgetCard>
                  )}

                  {/* 4. Sidebar Dynamic Widgets (Scores, Actions) */}
                  {content.sidebar_items && content.sidebar_items.map((item: any, idx: number) => {
                    if (item.type === 'advisor_score') {
                      return (
                        <WidgetCard key={idx} title={item.type === 'advisor_score' ? item.title : ''} delay={0.3}>
                          <div className="flex items-end gap-2 mb-2">
                            <span className="text-4xl font-black text-blue-600">{item.score}</span>
                            <span className="text-sm font-medium text-slate-400 mb-1.5">/ 100</span>
                          </div>
                          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-600 rounded-full" style={{ width: `${item.score}%` }} />
                          </div>
                          <p className="mt-3 text-sm text-slate-500">{item.content}</p>
                        </WidgetCard>
                      );
                    }
                    if (item.type === 'action_list') {
                      return (
                        <WidgetCard key={idx} title={<><ListChecks className="w-4 h-4" /> {item.title}</>} delay={0.4}>
                          <ul className="space-y-3">
                            {item.items.map((act: string, i: number) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                                <input type="checkbox" className="mt-1 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
                                <span>{act}</span>
                              </li>
                            ))}
                          </ul>
                        </WidgetCard>
                      )
                    }
                    return null;
                  })}

                </ContextRail>

              </SplitLayout>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center flex-1 h-full text-slate-400">
            <div className="text-center">
              <p className="text-lg font-medium">Selecteer een hoofdstuk</p>
            </div>
          </div>
        )}
      </main>
    </div >
  )
}

export default App
