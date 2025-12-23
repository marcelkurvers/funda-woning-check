import { useState, useEffect } from 'react';
import { BentoGrid, BentoCard } from './components/layout/BentoLayout';
import { MagazineChapter } from './components/MagazineChapter';
import {
  ChevronRight, Loader2, AlertCircle, Sparkles,
  Plus, FileText, Home, Settings, Zap, Bug, BookOpen
} from 'lucide-react';
import { LandingPage } from './components/LandingPage';
import { SettingsModal } from './components/common/SettingsModal';
import { DiscoveryBento } from './components/common/DiscoveryBento';
import { MediaGallery } from './components/common/MediaGallery';


import type { ReportData } from './types';

function App() {
  const [activeChapterId, setActiveChapterId] = useState("0");
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [debugMode, setDebugMode] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    const init = async () => {
      const pathParts = window.location.pathname.split('/');
      const queryParams = new URLSearchParams(window.location.search);
      let runIdFromUrl = queryParams.get('runId');

      if (!runIdFromUrl && pathParts.length >= 3 && pathParts[1] === 'runs') {
        runIdFromUrl = pathParts[2];
      }

      if (runIdFromUrl) {
        setLoading(true);
        try {
          await pollStatus(runIdFromUrl);
        } catch (e) {
          console.error("Auto-load failed", e);
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    };

    init();
  }, []);

  const pollStatus = async (runId: string) => {
    try {
      const statusRes = await fetch(`/api/runs/${runId}/status`);
      if (!statusRes.ok) throw new Error('Status ophalen mislukt');

      const data = await statusRes.json();
      if (data.status === 'done') {
        const reportRes = await fetch(`/api/runs/${runId}/report`);
        if (!reportRes.ok) throw new Error('Rapport ophalen mislukt');
        const reportData = await reportRes.json();

        setReport({
          runId: runId,
          address: reportData.property_core?.address || reportData.address || "Onbekend Adres",
          chapters: reportData.chapters || {},
          property_core: reportData.property_core,
          discovery: reportData.discovery || [],
          media_from_db: reportData.media_from_db || [],
          consistency: reportData.consistency
        });
        setActiveChapterId("0");
        setLoading(false);
      } else if (data.status === 'error') {
        setError(`Analyse mislukt: ${data.steps ? JSON.stringify(data.steps) : 'onbekende fout'}`);
        setLoading(false);
      } else {
        setTimeout(() => pollStatus(runId), 2000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  };

  const handleStartAnalysis = async (type: 'url' | 'paste', content: string, mediaUrls?: string[], extraFacts?: string) => {
    setLoading(true);
    setError(null);
    try {
      const runBody = type === 'paste'
        ? { funda_url: "manual-paste", funda_html: content, media_urls: mediaUrls, extra_facts: extraFacts }
        : { funda_url: content, funda_html: null };

      const createRes = await fetch('/api/runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(runBody)
      });

      if (!createRes.ok) throw new Error('Kon geen nieuwe analyse starten');
      const { run_id } = await createRes.json();

      const startRes = await fetch(`/api/runs/${run_id}/start`, { method: 'POST' });
      if (!startRes.ok) throw new Error('Kon de analyse niet uitvoeren');

      await pollStatus(run_id);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Er ging iets mis bij het starten.');
      setLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    if (!report?.runId) return;
    window.open(`/api/runs/${report.runId}/pdf`, '_blank');
  };

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

  if (!report) {
    return (
      <LandingPage onStartAnalysis={handleStartAnalysis} isLoading={loading} error={error} />
    );
  }

  const currentChapter = report.chapters[activeChapterId];
  const content = (currentChapter as any)?.chapter_data || currentChapter;
  const sortedChapters = Object.values(report.chapters).sort((a: any, b: any) => parseInt(a.id) - parseInt(b.id));

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden text-[13px] md:text-sm">
      <aside className="w-64 bg-white border-r border-slate-200 flex-shrink-0 h-full flex flex-col z-50 shadow-sm relative">
        <div className="p-6 border-b border-slate-100">
          <button onClick={() => setReport(null)} className="text-left group w-full">
            <div className="flex items-center gap-2 mb-1">
              <div className="p-1.5 bg-blue-600 rounded-lg">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div className="text-slate-900 font-serif font-bold text-lg tracking-tight group-hover:text-blue-600 transition-colors">AI Woning</div>
            </div>
            <div className="text-xs text-slate-500 font-medium truncate pl-9" title={report.address}>{report.address}</div>
          </button>
        </div>

        <div className="px-4 py-4">
          <button onClick={() => setReport(null)} className="w-full flex items-center gap-3 px-3 py-3 rounded-xl bg-blue-600 text-white hover:bg-blue-700 transition-all shadow-lg hover:shadow-blue-300 transform hover:-translate-y-0.5">
            <Plus className="w-5 h-5 text-white/90" />
            <span className="font-bold">Nieuwe Analyse</span>
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
          {sortedChapters.map((chapter: any) => (
            <button
              key={chapter.id}
              onClick={() => setActiveChapterId(chapter.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-all group ${activeChapterId === chapter.id ? 'bg-blue-50 text-blue-700 border border-blue-100' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}
            >
              <span className={`flex-shrink-0 w-6 h-6 flex items-center justify-center rounded text-[10px] font-bold ${activeChapterId === chapter.id ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-500'}`}>
                {chapter.id}
              </span>
              <span className="truncate text-left">{chapter.title || `Hoofdstuk ${chapter.id}`}</span>
              {activeChapterId === String(chapter.id) && <ChevronRight className="w-4 h-4 ml-auto text-blue-400" />}
            </button>
          ))}

        </nav>

        <div className="p-4 border-t border-slate-100 bg-slate-50/50 space-y-2">
          <button
            onClick={() => window.location.href = '/static/preferences.html'}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-500 hover:text-blue-600 hover:bg-white border border-transparent hover:border-slate-200 transition-all font-medium"
          >
            <Zap className="w-4 h-4 text-blue-500" />
            <span>Voorkeuren</span>
          </button>
          <button onClick={() => setSettingsOpen(true)} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-white border border-transparent hover:border-slate-200 transition-all">
            <Settings className="w-4 h-4" />
            <span>Instellingen</span>
          </button>
          <div className="mt-4 px-3 flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-widest">
            <span>Version</span>
            <span className="text-blue-500">v6.0.0-PREMIUM-DYNAMIC</span>
          </div>
        </div>
      </aside>

      <main className="flex-1 min-w-0 flex flex-col h-full overflow-hidden bg-slate-100/50">
        <header className="bg-white border-b border-slate-200 px-8 h-16 flex items-center justify-between shrink-0 z-40">
          <div className="flex items-center gap-4">
            <button onClick={() => setReport(null)} className="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-400 hover:text-blue-600">
              <Home className="w-5 h-5" />
            </button>
            <div className="h-6 w-px bg-slate-200 mx-2" />
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 text-white font-bold px-2.5 py-1 rounded-md text-[10px] shadow-sm shadow-blue-200 uppercase tracking-wider">
                Hfdst {currentChapter?.id || 0}
              </div>
              <h1 className="text-lg font-bold text-slate-800 tracking-tight">
                {content?.title || currentChapter?.title || "Analyse"}
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => setSettingsOpen(true)} className={`p-2 rounded-lg transition-all ${debugMode ? 'bg-blue-50 text-blue-600' : 'bg-slate-50 text-slate-400 hover:bg-slate-100'}`}>
              {debugMode ? <Bug className="w-5 h-5" /> : <Settings className="w-5 h-5" />}
            </button>
            <button onClick={handleDownloadPdf} className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-all font-bold text-xs shadow-lg shadow-slate-200">
              <FileText className="w-4 h-4 text-blue-400" />
              <span>PDF Rapport</span>
            </button>
          </div>
        </header>

        <SettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} debugMode={debugMode} setDebugMode={setDebugMode} />

        <div className="flex-1 overflow-y-auto p-0 md:p-6 custom-scrollbar">
          {/* AI Provenance Status Bar (Global) - Hide when in Magazine View */}
          {!activeChapterId && (
            <div className="mb-6 bg-slate-900 text-white rounded-xl shadow-lg p-4 flex flex-wrap items-center justify-between gap-4 border border-white/10 mx-6">
              <div className="flex items-center gap-4">
                <div className={`p-2 rounded-lg ${currentChapter?.provenance ? 'bg-blue-600' : 'bg-slate-700'}`}>
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    {currentChapter?.provenance ? 'AI Enrichment Status' : 'AI Offline / Cached'}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm">
                      {currentChapter?.provenance ? 'AI-Geresumeerd' : 'Geen AI Data'}
                    </span>
                    {currentChapter?.provenance && (
                      <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase ${currentChapter.provenance.confidence === 'high' ? 'bg-emerald-500 text-white' : 'bg-amber-500 text-white'}`}>
                        {currentChapter.provenance.confidence} Confidence
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="flex flex-col items-end">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Provider & Model</span>
                  <span className="text-xs font-medium text-blue-300">
                    {currentChapter?.provenance?.provider || "Local"} / {currentChapter?.provenance?.model || "Mock/Cached"}
                  </span>
                </div>
                <div className="w-px h-8 bg-white/10" />
                <div className="flex flex-col items-end">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Laatste Update</span>
                  <span className="text-xs font-medium text-slate-300">
                    {currentChapter?.provenance?.timestamp
                      ? new Date(currentChapter.provenance.timestamp).toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })
                      : "Onbekend"}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Property Summary Header - Hide when in Magazine View */}
          {!activeChapterId && (
            <div className="mb-6 bg-white rounded-xl border border-slate-100 shadow-sm p-3 flex flex-col md:flex-row items-center gap-4 mx-6">
              <div className="relative shrink-0 w-full md:w-40 h-24 rounded-lg overflow-hidden ring-1 ring-slate-100 group">
                <img
                  src={report.property_core?.media_urls?.[0] || report.media_from_db?.[0]?.url || "https://images.unsplash.com/photo-1600596542815-27b88e360290?auto=format&fit=crop&w=800"}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  alt=""
                  onError={(e) => { (e.target as HTMLImageElement).src = "https://images.unsplash.com/photo-1600596542815-27b88e360290?auto=format&fit=crop&w=800" }}
                />
              </div>
              <div className="flex-1 min-w-0 flex flex-col md:flex-row items-center justify-between w-full gap-4">
                <div>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight truncate">{report.address}</h2>
                  <div className="text-xs text-slate-500 font-medium">Multi-Check Pro Analysis Report</div>
                </div>
                <div className="flex items-center gap-6 bg-slate-50 rounded-xl p-3 border border-slate-100">
                  <div className="flex flex-col">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Inhoud</span>
                    <span className="text-lg font-black">{report.media_from_db?.length || 0} Foto's</span>
                  </div>
                  <div className="w-px h-8 bg-slate-200" />
                  <div className="flex flex-col">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Status</span>
                    <span className="text-lg font-black text-emerald-600">Compleet</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeChapterId === "13" ? (
            <div className="space-y-6">
              <MediaGallery media={report.media_from_db || []} />
              {content && (
                <div className="mt-8">
                  <BentoGrid>
                    <BentoCard className="col-span-1 md:col-span-3" title="AI Visie Analyse" icon={<Sparkles className="w-5 h-5 text-yellow-500" />}>
                      <div className="prose prose-slate prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: content.interpretation || "" }} />
                    </BentoCard>
                  </BentoGrid>
                </div>
              )}
            </div>
          ) : content ? (
            <div className="animate-in fade-in duration-700">
              {/* MAGAZINE VIEW */}
              <MagazineChapter
                content={content}
                chapterId={activeChapterId}
                media={report.media_from_db || []}
                provenance={currentChapter?.provenance || content._provenance}
              />

              {activeChapterId === "0" && report.discovery && report.discovery.length > 0 && (
                <div className="max-w-5xl mx-auto px-4 md:px-8 pb-12">
                  <DiscoveryBento attributes={report.discovery} />
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-20 text-slate-300">
              <BookOpen className="w-16 h-16 mb-4 opacity-20" />
              <p className="font-medium">Pagina wordt geladen of geen data beschikbaar.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
