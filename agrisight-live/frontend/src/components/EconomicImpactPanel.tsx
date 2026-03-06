/**
 * EconomicImpactPanel
 * Summarizes yield loss and financial impact from the current diagnosis.
 * Expected env vars: None
 * Testing tips: Pass a static yield impact object and assert that values render correctly.
 */
import React from 'react';

interface Props {
  yieldImpact: {
    yield_loss_percent?: number;
    expected_loss_rupees?: number;
    treatment_cost?: number;
    net_savings_if_treated?: number;
  } | null;
}

export function EconomicImpactPanel({ yieldImpact }: Props) {
  if (!yieldImpact) return null;

  const {
    yield_loss_percent = 0,
    expected_loss_rupees = 0,
    treatment_cost = 0,
    net_savings_if_treated = 0,
  } = yieldImpact;

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(v);

  return (
    <div className="glass-panel rounded-2xl p-4 text-xs md:text-sm text-neutral-dark pointer-events-auto">
      <h3 className="font-sora text-sm font-semibold mb-2">Economic impact</h3>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-wide text-neutral-dark/60 mb-0.5">
            Estimated yield loss
          </p>
          <p className="text-lg font-semibold text-primary-green">
            {(yield_loss_percent * 100).toFixed(1)}%
          </p>
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-wide text-neutral-dark/60 mb-0.5">
            Expected loss
          </p>
          <p className="text-lg font-semibold">
            ₹{formatCurrency(expected_loss_rupees)}
          </p>
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-wide text-neutral-dark/60 mb-0.5">
            Treatment cost
          </p>
          <p className="text-sm font-semibold">
            ₹{formatCurrency(treatment_cost)}
          </p>
        </div>
        <div>
          <p className="text-[11px] uppercase tracking-wide text-neutral-dark/60 mb-0.5">
            Net savings if treated
          </p>
          <p className="text-sm font-semibold text-primary-blue">
            ₹{formatCurrency(net_savings_if_treated)}
          </p>
        </div>
      </div>
    </div>
  );
}

