import { useState, useEffect } from 'react';
import { BentoGrid, BentoCard } from './components/layout/BentoLayout';
import { Target, ListChecks, ChevronRight, Loader2, AlertCircle, Sparkles, AlertTriangle, CheckCircle2, TrendingUp, BookOpen, Plus, FileText, Home, Settings, Zap, BarChart3, ShieldAlert, Bug } from 'lucide-react';
import { LandingPage } from './components/LandingPage';
import { DataVerifier } from './components/common/DataVerifier';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ScatterChart, Scatter, ZAxis } from 'recharts';

import type { ReportData } from './types';

function App() {
  const [activeChapterId, setActiveChapterId] = useState("0");
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [debugMode, setDebugMode] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => {
    // We intentionally do NOT auto-load the latest run anymore.
    // This ensures the user always sees the Landing Page first.
    setLoading(false);
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

  const handleStartAnalysis = async (type: 'url' | 'paste', content: string, mediaUrls?: string[], extraFacts?: string) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Create run
      const runBody = type === 'paste'
        ? { funda_url: "manual-paste", funda_html: content, media_urls: mediaUrls, extra_facts: extraFacts }
        : { funda_url: content, funda_html: null };

      const createRes = await fetch('/runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(runBody)
      });

      if (!createRes.ok) throw new Error('Kon geen nieuwe analyse starten');
      const { run_id } = await createRes.json();

      // 2. Start processing (non-blocking)
      const startRes = await fetch(`/runs/${run_id}/start`, { method: 'POST' });
      if (!startRes.ok) throw new Error('Kon de analyse niet uitvoeren');

      // 3. Poll for completion
      const pollStatus = async () => {
        const statusRes = await fetch(`/runs/${run_id}/status`);
        if (!statusRes.ok) throw new Error('Status ophalen mislukt');

        const { status } = await statusRes.json();

        // Update UI with progress (optional)
        // const { progress } = statusData;
        // console.log(`Progress: ${progress.percent}%`);

        if (status === 'done') {
          // Fetch final report
          const reportRes = await fetch(`/runs/${run_id}/report`);
          if (!reportRes.ok) throw new Error('Rapport ophalen mislukt');
          const data = await reportRes.json();

          setReport({
            runId: run_id,
            address: data.property_core?.address || "Onbekend Adres",
            chapters: data.chapters || {}
          });
          setActiveChapterId("0");
          setLoading(false);

        } else if (status === 'failed') {
          throw new Error('Analyse is mislukt');
        } else {
          // Still processing, poll again after 2 seconds
          setTimeout(pollStatus, 2000);
        }
      };

      // Start polling
      pollStatus();

    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Er ging iets mis bij het starten.');
      setLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    if (!report?.runId) return;
    window.open(`/runs/${report.runId}/pdf`, '_blank');
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
      {/* Sidebar Navigation - Light Premium Theme */}
      <aside className="w-64 bg-white border-r border-slate-200 flex-shrink-0 h-full flex flex-col z-50 shadow-sm relative">
        <div className="p-6 border-b border-slate-100">
          <button
            onClick={() => setReport(null)}
            className="text-left group w-full"
          >
            <div className="flex items-center gap-2 mb-1">
              <div className="p-1.5 bg-blue-600 rounded-lg">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div className="text-slate-900 font-bold text-lg tracking-tight group-hover:text-blue-600 transition-colors">AI Woning</div>
            </div>
            <div className="text-xs text-slate-500 font-medium truncate pl-9" title={report.address}>{report.address}</div>
          </button>
        </div>

        <div className="px-4 py-4">
          <button
            onClick={() => setReport(null)}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-xl bg-blue-600 text-white hover:bg-blue-700 transition-all duration-200 group font-bold shadow-lg shadow-blue-200 hover:shadow-blue-300 transform hover:-translate-y-0.5"
          >
            <Plus className="w-5 h-5 text-white/90" />
            <span>Nieuwe Analyse</span>
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
          {sortedChapters.map((chapter: any) => (
            <button
              key={chapter.id}
              onClick={() => setActiveChapterId(chapter.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group ${activeChapterId === chapter.id
                ? 'bg-blue-50 text-blue-700 border border-blue-100'
                : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
            >
              <span className={`flex-shrink-0 w-6 h-6 flex items-center justify-center rounded text-xs font-bold transition-colors ${activeChapterId === chapter.id ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-500 group-hover:bg-slate-200 group-hover:text-slate-700'
                }`}>
                {chapter.id}
              </span>
              <span className="truncate text-left">{chapter.title || `Hoofdstuk ${chapter.id}`}</span>
              {activeChapterId === String(chapter.id) && <ChevronRight className="w-4 h-4 ml-auto text-blue-400" />}

            </button>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-100 bg-slate-50/50">
          <button onClick={() => setSettingsOpen(!settingsOpen)} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-500 hover:text-slate-800 hover:bg-white border border-transparent hover:border-slate-200 hover:shadow-sm transition-all">
            <Settings className="w-4 h-4" />
            <span>Instellingen</span>
          </button>
        </div>
      </aside>

      {/* Main Content - No Window Scroll */}
      <main className="flex-1 min-w-0 flex flex-col h-full overflow-hidden bg-slate-100/50">

        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-8 h-16 flex items-center justify-between shadow-sm shrink-0 z-40">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setReport(null)}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-400 hover:text-blue-600"
              title="Terug naar Startpagina"
            >
              <Home className="w-5 h-5" />
            </button>
            <div className="h-6 w-px bg-slate-200 mx-2" />
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 text-white font-bold px-2.5 py-1 rounded-md text-xs shadow-sm shadow-blue-200">
                Hfdst {currentChapter?.id || 0}
              </div>
              <h1 className="text-lg font-bold text-slate-800 tracking-tight">
                {content?.title || currentChapter?.title || "Analyse"}
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3 relative">
            <button
              onClick={() => setSettingsOpen(!settingsOpen)}
              className={`p-2 rounded-lg transition-all ${settingsOpen || debugMode ? 'bg-blue-50 text-blue-600' : 'bg-slate-50 text-slate-400 hover:text-slate-600 hover:bg-slate-100'}`}
              title="Instellingen"
            >
              {debugMode ? <Bug className="w-5 h-5" /> : <Settings className="w-5 h-5" />}
            </button>

            {/* Settings Popover */}
            {settingsOpen && (
              <div className="absolute top-full right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-slate-100 p-4 z-50 animate-in slide-in-from-top-2">
                <h3 className="font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2">Instellingen</h3>

                {/* Debug Toggle */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-slate-700">Debug Modus</span>
                    <span className="text-xs text-slate-400 leading-tight">Toon data inconsistenties</span>
                  </div>
                  <button
                    onClick={() => setDebugMode(!debugMode)}
                    className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${debugMode ? 'bg-blue-600 justify-end' : 'bg-slate-200 justify-start'}`}
                  >
                    <div className="w-4 h-4 bg-white rounded-full shadow-sm" />
                  </button>
                </div>

                {/* Preference Navigation */}
                <a href="/preferences" className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50 transition-colors group">
                  <div className="p-1.5 bg-slate-100 text-slate-500 rounded group-hover:bg-white group-hover:text-blue-600 shadow-sm transition-all">
                    <Settings className="w-4 h-4" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-slate-700 group-hover:text-blue-700">Persoonlijke Voorkeuren</span>
                    <span className="text-[10px] text-slate-400">Marcel & Petra profiel beheren</span>
                  </div>
                </a>
              </div>
            )}

            <button
              onClick={handleDownloadPdf}
              className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-all font-bold text-xs shadow-lg shadow-slate-200"
            >
              <FileText className="w-4 h-4 text-blue-400" />
              <span>PDF Rapport</span>
            </button>
          </div>
        </header>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">

          {/* Property Header - Ultra Compact for 4K */}
          <div className="mb-4 bg-white rounded-xl border border-slate-100 shadow-sm p-3 flex flex-col md:flex-row items-center gap-4 animate-in slide-in-from-top-2">

            {/* Thumbnail */}
            <div className="relative shrink-0 w-full md:w-40 h-24 rounded-lg overflow-hidden shadow-inner ring-1 ring-slate-100 group">
              <img
                src={(report.chapters["0"] as any)?.property_core?.media_urls?.[0] || "https://images.unsplash.com/photo-1600596542815-27b88e360290?q=80&w=2000&auto=format&fit=crop"}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                alt=""
                onError={(e) => {
                  (e.target as HTMLImageElement).src = "https://images.unsplash.com/photo-1600596542815-27b88e360290?q=80&w=2000&auto=format&fit=crop";
                }}
              />
              <div className="absolute inset-0 bg-blue-900/0 group-hover:bg-blue-900/10 transition-colors" />
            </div>

            {/* Info & Stats */}
            <div className="flex-1 min-w-0 grid grid-cols-1 md:grid-cols-3 gap-4 w-full">

              {/* Address & Status */}
              <div className="md:col-span-1 flex flex-col justify-center">
                <div className="inline-flex items-center gap-2 mb-2">
                  <div className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 text-[10px] font-bold uppercase tracking-wider border border-blue-100">
                    Te Koop
                  </div>
                  <div className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 text-[10px] font-bold uppercase tracking-wider border border-emerald-100">
                    Beschikbaar
                  </div>
                </div>
                <h1 className="text-xl font-black text-slate-900 tracking-tight leading-snug truncate" title={report.address}>{report.address}</h1>
                <div className="text-xs text-slate-500 font-medium mt-1 truncate">
                  Funda Analyse Rapport • 100% AI Generated
                </div>
              </div>

              {/* Key Stats Row */}
              <div className="md:col-span-2 flex items-center justify-between md:justify-end gap-2 md:gap-8 bg-slate-50/50 rounded-xl p-3 border border-slate-100">

                {/* Logic: Rescue Data from AI Summary if Backend failed */}
                {(() => {
                  const core = (report.chapters["0"] as any)?.property_core || {};
                  const summary = (report.chapters["0"] as any)?.chapter_data?.summary || "";

                  // 1. Price
                  let price = core.asking_price_eur;
                  if (!price || price === "€ N/B" || price === "€ TBD") {
                    const m = summary.match(/€\s?([\d.,]+)/);
                    if (m) price = `€ ${m[1]}`;
                    else price = "€ N/B";
                  }

                  // 2. Area
                  let area = core.living_area_m2;
                  if (!area || area === "0" || area === "N/B") {
                    const m = summary.match(/(\d+)\s?m[²2]/);
                    if (m) area = m[1];
                    else area = "N/B";
                  }

                  // 3. Label
                  let label = core.energy_label;
                  if (!label || label === "?" || label === "N/B") {
                    const m = summary.match(/Label:?\s?([A-G][\+]*)/i);
                    if (m) label = m[1].toUpperCase();
                    else label = "?";
                  }

                  return (
                    <>
                      {/* Price Display */}
                      <DataVerifier field="asking_price_eur" consistency={report.consistency} debugMode={debugMode}>
                        <div className="flex flex-col items-center md:items-start min-w-[80px]">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Vraagprijs</span>
                          <div className="text-lg font-black text-slate-900 tracking-tight">{price}</div>
                        </div>
                      </DataVerifier>

                      <div className="w-px h-8 bg-slate-200" />

                      {/* Area Display */}
                      <DataVerifier field="living_area_m2" consistency={report.consistency} debugMode={debugMode}>
                        <div className="flex flex-col items-center md:items-start min-w-[80px]">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Woonopp.</span>
                          <div className="flex items-center gap-1.5">
                            <Home className="w-4 h-4 text-blue-500" />
                            <span className="text-lg font-black text-slate-900 tracking-tight">{area}</span>
                          </div>
                        </div>
                      </DataVerifier>

                      <div className="w-px h-8 bg-slate-200" />

                      {/* Label Display */}
                      <DataVerifier field="energy_label" consistency={report.consistency} debugMode={debugMode}>
                        <div className="flex flex-col items-center md:items-start min-w-[60px]">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Label</span>
                          <div className="flex items-center gap-1.5">
                            <Target className="w-4 h-4 text-emerald-500" />
                            <span className="text-lg font-black text-slate-900 tracking-tight">{label}</span>
                          </div>
                        </div>
                      </DataVerifier>
                    </>
                  );
                })()}

              </div>

            </div>
          </div>

          {content ? (
            <BentoGrid>

              {/* SPECIALIZED VISUAL CARDS PER CHAPTER */}

              {/* CHAPTER 4: Energy Radar */}
              {activeChapterId === "4" && (
                <BentoCard className="col-span-1 md:col-span-2 lg:col-span-2 row-span-1" variant="highlight" title="Duurzaamheids-Potentieel" icon={<Zap className="w-5 h-5 text-amber-600" />}>
                  <div className="flex flex-col h-full justify-between">
                    <div className="flex items-end gap-4 h-32 mb-4">
                      <div className="flex-1 bg-slate-200 rounded-xl relative group">
                        <div className="absolute bottom-0 w-full bg-emerald-500 rounded-xl transition-all duration-1000" style={{ height: '40%' }}></div>
                        <span className="absolute -top-6 left-0 right-0 text-center text-[10px] font-bold text-slate-400">HUIDIG</span>
                      </div>
                      <div className="flex-1 bg-slate-200 rounded-xl relative border-2 border-dashed border-emerald-500/30">
                        <div className="absolute bottom-0 w-full bg-emerald-400 opacity-40 rounded-xl animate-pulse" style={{ height: '90%' }}></div>
                        <span className="absolute -top-6 left-0 right-0 text-center text-[10px] font-bold text-emerald-600">POTENTIEEL</span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-500 italic">"Met spouwmuurisolatie en een hybride pomp stijgt de woning direct naar label A."</p>
                  </div>
                </BentoCard>
              )}

              {/* CHAPTER 10: Financial Waterfall (Recharts) */}
              {activeChapterId === "10" && (
                <BentoCard className="col-span-1 md:col-span-3 lg:col-span-3 min-h-[250px]" title="Investerings Overzicht" icon={<BarChart3 className="w-5 h-5 text-blue-600" />}>
                  <div className="h-56 w-full mt-4">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={[
                          { name: 'Aankoop', value: parseInt((report.chapters["0"] as any)?.property_core?.asking_price_eur?.replace(/\D/g, '') || "400000"), fill: '#2563eb' },
                          { name: 'K.K.', value: parseInt((report.chapters["0"] as any)?.property_core?.asking_price_eur?.replace(/\D/g, '') || "400000") * 0.02, fill: '#f43f5e' },
                          { name: 'Verbouwing', value: 45000, fill: '#f59e0b' },
                          { name: 'Totaal', value: parseInt((report.chapters["0"] as any)?.property_core?.asking_price_eur?.replace(/\D/g, '') || "400000") * 1.02 + 45000, fill: '#0f172a' },
                        ]}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                      >
                        <XAxis dataKey="name" tick={{ fontSize: 12, fontWeight: 600 }} stroke="#94a3b8" />
                        <YAxis hide />
                        <Tooltip
                          cursor={{ fill: 'transparent' }}
                          contentStyle={{ backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
                        />
                        <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                          {[{ name: 'Aankoop', color: '#2563eb' }, { name: 'K.K.', color: '#f43f5e' }, { name: 'Verbouwing', color: '#f59e0b' }, { name: 'Totaal', color: '#0f172a' }].map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </BentoCard>
              )}

              {/* CHAPTER 12: Risk Matrix (Recharts Scatter) */}
              {(activeChapterId === "12" || activeChapterId === "9") && (
                <BentoCard className="col-span-1 md:col-span-2 lg:col-span-2 row-span-1" variant="alert" title="Risico Matrix" icon={<ShieldAlert className="w-5 h-5 text-rose-600" />}>
                  <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <ScatterChart
                        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                      >
                        <XAxis type="number" dataKey="x" name="Impact" unit="" domain={[0, 4]} hide />
                        <YAxis type="number" dataKey="y" name="Kans" unit="" domain={[0, 4]} hide />
                        <ZAxis type="number" dataKey="z" range={[100, 400]} />
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                        <Scatter name="Risicos" data={[
                          { x: 1, y: 1, z: 100, label: 'Laag', fill: '#22c55e' },
                          { x: 3, y: 3, z: 300, label: 'Kritiek', fill: '#f43f5e' },
                          { x: 2, y: 3, z: 200, label: 'Let op', fill: '#f59e0b' },
                        ]} fill="#8884d8">
                          {
                            [{ fill: '#22c55e' }, { fill: '#f43f5e' }, { fill: '#f59e0b' }].map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.fill} />
                            ))
                          }
                        </Scatter>
                      </ScatterChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-10">
                      <div className="w-full h-full grid grid-cols-3 grid-rows-3 gap-1">
                        {[...Array(9)].map((_, i) => <div key={i} className="border border-slate-300 rounded" />)}
                      </div>
                    </div>
                  </div>
                </BentoCard>
              )}

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
          ) : (
            <div className="flex items-center justify-center flex-1 h-full text-slate-400">
              <div className="text-center">
                <p className="text-lg font-medium">Selecteer een hoofdstuk</p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div >
  );
}

export default App;
