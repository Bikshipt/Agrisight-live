/**
 * TreatmentPlanPanel
 * Communicates the recommended intervention plan to the user.
 * Expected env vars: None
 * Testing tips: Pass a static plan and confirm dosage math.
 */
import React from 'react';

interface Props {
  plan: {
    recommended_treatment?: string;
    dosage_ml_per_acre?: number;
    total_required_ml?: number;
    application_window_hours?: number;
  } | null;
}

export function TreatmentPlanPanel({ plan }: Props) {
  if (!plan) return null;

  const {
    recommended_treatment = '–',
    dosage_ml_per_acre = 0,
    total_required_ml = 0,
    application_window_hours = 0,
  } = plan;

  return (
    <div className="glass-panel rounded-2xl p-4 text-xs md:text-sm text-neutral-dark pointer-events-auto">
      <h3 className="font-sora text-sm font-semibold mb-2">Treatment plan</h3>
      <p className="mb-1">
        <span className="font-semibold">Product:</span> {recommended_treatment}
      </p>
      <p className="mb-1">
        <span className="font-semibold">Dosage:</span> {dosage_ml_per_acre} ml/acre
      </p>
      <p className="mb-1">
        <span className="font-semibold">Total required:</span> {total_required_ml} ml
      </p>
      <p className="mb-0">
        <span className="font-semibold">Apply within:</span> ~{application_window_hours} hours
      </p>
    </div>
  );
}

