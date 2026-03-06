/**
 * DiseaseForecastPanel
 * Visualizes infection probability over time using a smooth line chart.
 * Expected env vars: None
 * Testing tips: Pass static forecast data and assert that the chart renders without crashing.
 */
import React from 'react';
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';

type Point = { day: number; infection_probability: number };

interface Props {
  forecast: { spread_forecast?: Point[] } | null;
}

export function DiseaseForecastPanel({ forecast }: Props) {
  const data = (forecast?.spread_forecast ?? []).map((p) => ({
    day: p.day,
    infection: Math.round(p.infection_probability * 100),
  }));

  if (!data.length) {
    return null;
  }

  return (
    <div className="glass-panel rounded-2xl p-4 text-neutral-dark pointer-events-auto">
      <h3 className="font-sora text-sm font-semibold mb-2">Disease progression forecast</h3>
      <div className="h-32">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
            <defs>
              <linearGradient id="infectionGradient" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#0B74FF" stopOpacity={0.9} />
                <stop offset="100%" stopColor="#4FD1FF" stopOpacity={0.9} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.25)" />
            <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fontSize: 10 }} />
            <YAxis
              domain={[0, 100]}
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 10 }}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              formatter={(value) => `${value as number}%`}
              labelFormatter={(label) => `Day ${label}`}
            />
            <Line
              type="monotone"
              dataKey="infection"
              stroke="url(#infectionGradient)"
              strokeWidth={2}
              dot={{ r: 3, stroke: '#0FAF68', strokeWidth: 1, fill: '#F6FBFF' }}
              activeDot={{ r: 5, fill: '#0FAF68' }}
              isAnimationActive
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

