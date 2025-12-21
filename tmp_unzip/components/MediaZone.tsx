
import React, { useEffect, useRef } from 'react';
import { ImagePreview } from '../types';

interface MediaZoneProps {
  images: ImagePreview[];
  onPaste: (images: ImagePreview[]) => void;
  onRemove: (id: string) => void;
}

const MediaZone: React.FC<MediaZoneProps> = ({ images, onPaste, onRemove }) => {
  const zoneRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleGlobalPaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      const newImages: Promise<ImagePreview>[] = [];

      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const file = items[i].getAsFile();
          if (file) {
            newImages.push(new Promise((resolve) => {
              const reader = new FileReader();
              reader.onload = (event) => {
                resolve({
                  id: Math.random().toString(36).substr(2, 9),
                  base64: event.target?.result as string,
                  mimeType: file.type
                });
              };
              reader.readAsDataURL(file);
            }));
          }
        }
      }

      if (newImages.length > 0) {
        Promise.all(newImages).then(onPaste);
      }
    };

    window.addEventListener('paste', handleGlobalPaste);
    return () => window.removeEventListener('paste', handleGlobalPaste);
  }, [onPaste]);

  return (
    <section className="w-full">
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between px-2">
          <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">perm_media</span>
            Media & Photos {images.length > 0 && `(${images.length})`}
          </h3>
        </div>

        {images.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {images.map((img) => (
              <div key={img.id} className="relative group aspect-square rounded-xl overflow-hidden border border-border-dark bg-surface-dark">
                <img src={img.base64} alt="Pasted" className="w-full h-full object-cover" />
                <button 
                  onClick={() => onRemove(img.id)}
                  className="absolute top-2 right-2 p-1 bg-red-500 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <span className="material-symbols-outlined text-sm">close</span>
                </button>
              </div>
            ))}
            <div 
              className="flex flex-col items-center justify-center border-2 border-dashed border-border-dark rounded-xl bg-surface-dark/30 hover:bg-surface-dark transition-colors cursor-pointer aspect-square"
              onClick={() => alert("Just press Ctrl+V to paste more images from your clipboard!")}
            >
              <span className="material-symbols-outlined text-slate-500">add</span>
              <span className="text-xs text-slate-500 mt-1 font-bold">Paste More</span>
            </div>
          </div>
        ) : (
          <div 
            ref={zoneRef}
            className="w-full rounded-2xl border-2 border-dashed border-slate-300 dark:border-border-dark bg-slate-50 dark:bg-surface-dark/50 p-12 md:p-16 flex flex-col items-center justify-center text-center gap-6 hover:border-primary/50 hover:bg-slate-100 dark:hover:bg-surface-dark transition-all cursor-pointer group"
          >
            <div className="w-20 h-20 rounded-full bg-slate-200 dark:bg-surface-dark flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <span className="material-symbols-outlined text-4xl text-slate-400 dark:text-slate-500 group-hover:text-primary transition-colors">add_photo_alternate</span>
            </div>
            <div className="max-w-md space-y-2">
              <p className="text-lg font-bold text-slate-900 dark:text-white">Paste Photos Directly</p>
              <p className="text-slate-500 dark:text-slate-400">Copy specific images from the Funda listing and paste them here (Ctrl+V) to include them in the analysis.</p>
            </div>
            <button className="text-primary hover:text-blue-400 font-semibold text-sm flex items-center gap-1 transition-colors">
              <span className="material-symbols-outlined text-base">content_paste</span>
              <span>Paste from clipboard</span>
            </button>
          </div>
        )}
      </div>
    </section>
  );
};

export default MediaZone;
