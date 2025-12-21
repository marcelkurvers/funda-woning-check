
import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import MediaZone from './components/MediaZone';
import DeepDive from './components/DeepDive';
import AnalysisDisplay from './components/AnalysisDisplay';
import Footer from './components/Footer';
import { PropertyAnalysis, ImagePreview } from './types';
import { analyzeProperty } from './services/geminiService';

const App: React.FC = () => {
  const [pastedText, setPastedText] = useState('');
  const [images, setImages] = useState<ImagePreview[]>([]);
  const [analysis, setAnalysis] = useState<PropertyAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!pastedText && images.length === 0) {
      alert("Please paste listing text or images first.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await analyzeProperty(pastedText, images);
      setAnalysis(result);
      // Smooth scroll to results
      setTimeout(() => {
        document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err: any) {
      console.error(err);
      setError("Failed to analyze data. Please ensure the API key is valid and try again.");
    } finally {
      setLoading(false);
    }
  };

  const handlePasteImage = useCallback((newImages: ImagePreview[]) => {
    setImages(prev => [...prev, ...newImages]);
  }, []);

  const clearData = () => {
    setPastedText('');
    setImages([]);
    setAnalysis(null);
    setError(null);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <main className="flex-grow flex flex-col items-center">
        <Hero 
          value={pastedText} 
          onChange={setPastedText} 
          onAnalyze={handleAnalyze} 
          loading={loading}
          onClear={clearData}
        />

        <div className="w-full max-w-7xl px-4 py-8 space-y-12">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl text-red-400 flex items-center gap-3">
              <span className="material-symbols-outlined">error</span>
              <p>{error}</p>
            </div>
          )}

          <MediaZone 
            images={images} 
            onPaste={handlePasteImage} 
            onRemove={(id) => setImages(prev => prev.filter(img => img.id !== id))}
          />

          {analysis ? (
            <div id="results-section">
              <AnalysisDisplay analysis={analysis} />
            </div>
          ) : (
            <DeepDive />
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default App;
