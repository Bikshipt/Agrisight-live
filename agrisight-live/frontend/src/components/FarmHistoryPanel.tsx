/**
 * FarmHistoryPanel
 * Shows recurring disease patterns and farm-level recommendations.
 * Expected env vars: None
 * Testing tips: Render with mocked farm memory profile.
 */
import React from 'react';

interface Props {
  farmMemory: {
    pattern_detected?: boolean;
    pattern?: string | null;
    recommendation?: string | null;
    profile?: {
      crop_types?: string[];
      recurring_diseases?: string[];
    };
  } | null;
}

export function FarmHistoryPanel({ farmMemory }: Props) {
  if (!farmMemory) return null;

  const { pattern_detected, pattern, recommendation, profile } = farmMemory;

  return (
    <div className="glass-panel rounded-2xl p-4 text-xs md:text-sm text-neutral-dark pointer-events-auto">
      <h3 className="font-sora text-sm font-semibold mb-2">Farm memory</h3>
      {pattern_detected && pattern ? (
        <>
          <p className="mb-1">
            <span className="font-semibold">Pattern:</span> {pattern}
          </p>
          {recommendation && (
            <p className="mb-1 text-neutral-dark/80">
              <span className="font-semibold">Next-season recommendation:</span> {recommendation}
            </p>
          )}
        </>
      ) : (
        <p className="mb-1 text-neutral-dark/80">
          No strong recurring patterns detected yet for this farm.
        </p>
      )}

      {profile && (
        <div className="mt-1">
          {profile.crop_types && profile.crop_types.length > 0 && (
            <p className="mb-0.5">
              <span className="font-semibold">Crop types:</span>{' '}
              {profile.crop_types.join(', ')}
            </p>
          )}
          {profile.recurring_diseases && profile.recurring_diseases.length > 0 && (
            <p className="mb-0.5">
              <span className="font-semibold">Recurring diseases:</span>{' '}
              {profile.recurring_diseases.join(', ')}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

