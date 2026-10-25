import React from 'react';
import { X, ExternalLink } from 'lucide-react';

interface ImageModalProps {
  imageUrl: string | null;
  onClose: () => void;
}

export const ImageModal: React.FC<ImageModalProps> = ({ imageUrl, onClose }) => {
  if (!imageUrl) return null;

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-[1000] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 transition-opacity animate-in fade-in duration-200"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative max-w-4xl max-h-[90vh] bg-neutral-900 rounded-3xl overflow-hidden shadow-2xl border border-white/10 flex flex-col"
      >
        {/* Top Control Bar */}
        <div className="flex items-center justify-between p-3.5 bg-neutral-900/90 border-b border-white/10 text-white">
          <span className="text-xs font-semibold text-neutral-300">Hazard Photo Inspection</span>
          <div className="flex items-center gap-2">
            {imageUrl.startsWith('http') && (
              <a
                href={imageUrl}
                target="_blank"
                rel="noreferrer"
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-neutral-300 transition-colors"
                title="Open in new tab"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-white/10 hover:bg-red-500 text-white transition-colors"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* High Resolution Image */}
        <div className="flex-1 overflow-auto p-2 flex items-center justify-center bg-black/50">
          <img
            src={imageUrl}
            alt="Hazard Evidence"
            className="max-w-full max-h-[80vh] object-contain rounded-2xl"
          />
        </div>
      </div>
    </div>
  );
};
