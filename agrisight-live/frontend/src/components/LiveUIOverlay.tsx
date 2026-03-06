/**
 * LiveUIOverlay Component
 * Renders the real-time annotations, transcript, and confidence meter over the video.
 * Expected env vars: None
 * Testing tips: Pass mock results to verify rendering of bounding boxes and text.
 */
import React from 'react';

interface Props {
  isConnected: boolean;
  boxes: Array<{
    x: number;
    y: number;
    w: number;
    h: number;
    label: string;
    score: number;
  }>;
  transcript: string;
  disease: string | null;
  confidence: number;
  recommendedActions: string[];
}

export default function LiveUIOverlay({
  isConnected,
  boxes,
  transcript,
  disease,
  confidence,
  recommendedActions,
}: Props) {
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const clampedConfidence = Math.max(0, Math.min(1, confidence));
  const offset = circumference * (1 - clampedConfidence);

  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Status Indicator */}
      <div className="absolute top-4 right-4 flex items-center gap-2 glass-panel px-3 py-1.5 rounded-full">
        <div className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-accent-green animate-pulse' : 'bg-red-500'}`} />
        <span className="text-xs font-semibold text-neutral-dark">
          {isConnected ? 'LIVE' : 'CONNECTING'}
        </span>
      </div>

      {/* Bounding Boxes */}
      {boxes.map((box, idx) => (
        <div
          key={idx}
          className="absolute border-2 border-primary-green rounded-lg transition-all duration-300 animate-[pulse_1.8s_ease-in-out_infinite]"
          style={{
            left: `${box.x}%`,
            top: `${box.y}%`,
            width: `${box.w}%`,
            height: `${box.h}%`,
          }}
        >
          <div className="absolute -top-7 left-0 bg-primary-green/90 text-white text-xs px-2 py-1 rounded-full shadow-lg whitespace-nowrap">
            {box.label} ({(box.score * 100).toFixed(0)}%)
          </div>
        </div>
      ))}

      {/* Bottom Info Panel */}
      <div className="absolute bottom-0 left-0 right-0 p-4">
        <div className="glass-panel rounded-2xl p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-4">
            {/* Circular confidence meter */}
            <div className="relative w-16 h-16">
              <svg className="w-16 h-16 -rotate-90" viewBox="0 0 80 80">
                <defs>
                  <linearGradient id="confidenceGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#0B74FF" />
                    <stop offset="100%" stopColor="#4FD1FF" />
                  </linearGradient>
                </defs>
                <circle
                  cx="40"
                  cy="40"
                  r={radius}
                  stroke="rgba(148, 163, 184, 0.3)"
                  strokeWidth="6"
                  fill="transparent"
                />
                <circle
                  cx="40"
                  cy="40"
                  r={radius}
                  stroke="url(#confidenceGradient)"
                  strokeWidth="6"
                  strokeLinecap="round"
                  fill="transparent"
                  strokeDasharray={circumference}
                  strokeDashoffset={offset}
                  className="transition-[stroke-dashoffset] duration-500 ease-out drop-shadow-[0_0_8px_rgba(79,209,255,0.6)]"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-semibold text-neutral-dark">
                  {(clampedConfidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <div>
              <h3 className="font-sora font-bold text-lg text-neutral-dark mb-1">
                {disease ?? 'Analyzing crop health...'}
              </h3>
              <p className="text-xs text-neutral-dark/70 line-clamp-2">
                {transcript || 'Point your camera at a leaf and hold steady to begin live analysis.'}
              </p>
            </div>
          </div>

          <ul className="text-xs md:text-sm text-neutral-dark/80 space-y-1 md:max-w-xs">
            {recommendedActions.slice(0, 3).map((action, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-primary-green mt-0.5">•</span>
                {action}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
