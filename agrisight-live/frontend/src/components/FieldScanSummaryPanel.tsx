/**
 * FieldScanSummaryPanel
 * Visualizes plant health statistics and a simple infection heat representation.
 * Expected env vars: None
 * Testing tips: Render with mock summary data from video scan engine.
 */
import React from 'react';

interface Hotspot {
  x: number;
  y: number;
  severity: 'low' | 'medium' | 'high' | string;
}

interface Props {
  summary: {
    plants_analyzed?: number;
    healthy_percent?: number;
    mild_infection_percent?: number;
    severe_infection_percent?: number;
    hotspot_regions?: Hotspot[];
  } | null;
}

export function FieldScanSummaryPanel({ summary }: Props) {
  if (!summary) return null;

  const {
    plants_analyzed = 0,
    healthy_percent = 0,
    mild_infection_percent = 0,
    severe_infection_percent = 0,
    hotspot_regions = [],
  } = summary;

  const total = healthy_percent + mild_infection_percent + severe_infection_percent || 1;

  return (
    <div className="glass-panel rounded-2xl p-4 text-xs md:text-sm text-neutral-dark pointer-events-auto">
      <h3 className="font-sora text-sm font-semibold mb-2">Field walkthrough snapshot</h3>
      <p className="mb-1">Plants analyzed: {plants_analyzed}</p>
      <div className="flex gap-2 mb-2">
        <div className="flex-1">
          <div className="h-1.5 rounded-full overflow-hidden bg-neutral-200/70">
            <div
              className="h-full bg-emerald-500"
              style={{ width: `${(healthy_percent / total) * 100}%` }}
            />
          </div>
          <p className="text-[11px] mt-1">Healthy: {healthy_percent}%</p>
        </div>
        <div className="flex-1">
          <div className="h-1.5 rounded-full overflow-hidden bg-neutral-200/70">
            <div
              className="h-full bg-amber-400"
              style={{ width: `${(mild_infection_percent / total) * 100}%` }}
            />
          </div>
          <p className="text-[11px] mt-1">Mild: {mild_infection_percent}%</p>
        </div>
        <div className="flex-1">
          <div className="h-1.5 rounded-full overflow-hidden bg-neutral-200/70">
            <div
              className="h-full bg-red-500"
              style={{ width: `${(severe_infection_percent / total) * 100}%` }}
            />
          </div>
          <p className="text-[11px] mt-1">Severe: {severe_infection_percent}%</p>
        </div>
      </div>

      {/* Simplified heatmap chips */}
      {hotspot_regions.length > 0 && (
        <div className="mt-1">
          <p className="text-[11px] mb-1">Hotspot regions:</p>
          <div className="flex flex-wrap gap-1">
            {hotspot_regions.map((h, idx) => {
              const color =
                h.severity === 'high'
                  ? 'bg-red-500/80'
                  : h.severity === 'medium'
                  ? 'bg-amber-400/80'
                  : 'bg-emerald-500/80';
              return (
                <span
                  key={idx}
                  className={`${color} text-white text-[10px] px-2 py-0.5 rounded-full shadow`}
                >
                  ({h.x},{h.y}) {h.severity}
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

