/**
 * RiskForecastPanel
 * Displays microclimate-based disease risk forecasts.
 * Expected env vars: None
 * Testing tips: Render with static microclimateRisk objects.
 */
import React from 'react';

interface Props {
  microclimateRisk: {
    risk_alert?: boolean;
    disease?: string | null;
    probability?: number;
    prediction_window_days?: number;
    recommended_prevention?: string | null;
  } | null;
}

export function RiskForecastPanel({ microclimateRisk }: Props) {
  if (!microclimateRisk) return null;

  const {
    risk_alert = false,
    disease,
    probability = 0,
    prediction_window_days = 0,
    recommended_prevention,
  } = microclimateRisk;

  return (
    <div className="glass-panel rounded-2xl p-4 text-xs md:text-sm text-neutral-dark pointer-events-auto">
      <div className="flex items-center justify-between mb-1">
        <h3 className="font-sora text-sm font-semibold">Microclimate risk</h3>
        <span
          className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${
            risk_alert ? 'bg-amber-500/20 text-amber-700' : 'bg-primary-green/10 text-primary-green'
          }`}
        >
          {risk_alert ? 'Elevated' : 'Low'}
        </span>
      </div>
      <p className="mb-1">
        {disease ? (
          <>
            Risk of <span className="font-semibold">{disease}</span> in the next{' '}
            {prediction_window_days} days.
          </>
        ) : (
          'No specific disease pattern dominating current microclimate.'
        )}
      </p>
      <p className="mb-1">
        <span className="font-semibold">Probability:</span>{' '}
        {(probability * 100).toFixed(0)}%
      </p>
      {recommended_prevention && (
        <p className="text-neutral-dark/80">
          <span className="font-semibold">Prevention:</span> {recommended_prevention}
        </p>
      )}
    </div>
  );
}

