/**
 * Main App component for AgriSight Live.
 * Renders a multi-panel dashboard with live scan, forecasts, economics,
 * regional map, satellite health, and farm history.
 */
import React, { useEffect } from 'react';
import CameraStream from './components/CameraStream';
import DeviceMockHero from './components/DeviceMockHero';
import { OutbreakMap } from './components/OutbreakMap';
import { VoiceAssistant } from './components/VoiceAssistant';
import { startSyncEngine } from './services/sync_engine';

export default function App() {
  useEffect(() => {
    startSyncEngine();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-surface-white via-primary-green/5 to-primary-blue/10 text-neutral-dark font-manrope">
      <div className="max-w-6xl mx-auto px-4 py-6 md:py-10 space-y-6">
        {/* Hero and Live Scan */}
        <div className="grid grid-cols-1 md:grid-cols-[1.2fr_1.1fr] gap-6 items-stretch">
          <div className="bg-primary-green/10 rounded-3xl md:rounded-[2.5rem] p-6 md:p-10 shadow-lg relative overflow-hidden">
            <div className="absolute -left-24 -top-24 w-64 h-64 bg-primary-blue/10 rounded-full blur-3xl" />
            <h1 className="font-sora text-3xl md:text-5xl font-bold mb-4 text-primary-green relative">
              AgriSight Live
            </h1>
            <p className="text-sm md:text-base mb-6 max-w-md relative">
              Live crop intelligence for every field – from leaf-level diagnosis to
              farm-level forecasting, even in offline rural conditions.
            </p>
            <div className="hidden md:block relative">
              <DeviceMockHero />
            </div>
          </div>

          <div className="bg-surface-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/60 p-3 md:p-4">
            <h2 className="font-sora text-sm font-semibold mb-2">Live Scan</h2>
            <div className="rounded-3xl overflow-hidden border border-neutral-dark/10">
              <CameraStream />
            </div>
          </div>
        </div>

        {/* Regional Map & Satellite Health & Voice Assistant */}
        <div className="grid grid-cols-1 md:grid-cols-[1.4fr_0.9fr] gap-6">
          <div className="bg-surface-white/80 backdrop-blur-xl rounded-3xl shadow-lg border border-white/60 p-4 md:p-5">
            <h2 className="font-sora text-sm font-semibold mb-3">Regional Outbreak Map</h2>
            <OutbreakMap />
          </div>
          <div className="flex flex-col gap-4">
            <VoiceAssistant />
          </div>
        </div>
      </div>
    </div>
  );
}
