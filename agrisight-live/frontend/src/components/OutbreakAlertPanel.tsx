/**
 * OutbreakAlertPanel
 * Displays an emerging regional outbreak warning with basic geo context.
 * Expected env vars: None
 * Testing tips: Render with and without an active alert to verify states.
 */
import React from 'react';

interface Props {
  outbreak: {
    outbreak_alert?: boolean;
    disease?: string | null;
    cluster_center?: [number, number] | null;
    radius_km?: number;
    spread_probability?: number;
  } | null;
}

export function OutbreakAlertPanel({ outbreak }: Props) {
  if (!outbreak) return null;

  const isActive = Boolean(outbreak.outbreak_alert);
  const probability = outbreak.spread_probability ?? 0;
  const center = outbreak.cluster_center;

  return (
    <div
      className={`rounded-2xl p-4 text-xs md:text-sm pointer-events-auto ${
        isActive
          ? 'bg-red-500/10 border border-red-500/40 shadow-[0_0_24px_rgba(248,113,113,0.4)]'
          : 'bg-primary-green/5 border border-primary-green/30'
      }`}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="font-sora text-sm font-semibold">
          {isActive ? 'Regional outbreak risk' : 'No active outbreak cluster'}
        </span>
        {isActive && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-500/20 text-red-700 font-semibold uppercase">
            Alert
          </span>
        )}
      </div>
      {isActive && (
        <>
          <p className="text-neutral-dark/80 mb-1">
            {outbreak.disease} cluster detected within approximately {outbreak.radius_km} km.
          </p>
          {center && (
            <p className="text-neutral-dark/70">
              Centered near{' '}
              <span className="font-mono">
                {center[0].toFixed(3)}, {center[1].toFixed(3)}
              </span>
              . Spread probability ~{Math.round((probability ?? 0) * 100)}%.
            </p>
          )}
        </>
      )}
      {!isActive && (
        <p className="text-neutral-dark/70">
          We continuously monitor recent crop scans to raise early warnings if clusters emerge.
        </p>
      )}
    </div>
  );
}

