/**
 * CameraStream Component
 * Handles WebRTC getUserMedia for video/audio, renders preview, and samples frames.
 * Implements adjustable frame sampling and microphone capture for streaming
 * to the backend WebSocket.
 *
 * Expected env vars: VITE_WS_URL (used by websocket service)
 * Testing tips: Mock navigator.mediaDevices.getUserMedia and MediaRecorder in tests.
 */
import React, { useEffect, useRef, useState } from 'react';
import { useLiveWebSocket } from '../services/websocket';
import LiveUIOverlay from './LiveUIOverlay';
import { DiseaseForecastPanel } from './DiseaseForecastPanel';
import { OutbreakAlertPanel } from './OutbreakAlertPanel';
import { EconomicImpactPanel } from './EconomicImpactPanel';
import { TreatmentPlanPanel } from './TreatmentPlanPanel';
import { RiskForecastPanel } from './RiskForecastPanel';
import { FieldScanSummaryPanel } from './FieldScanSummaryPanel';
import { FarmHistoryPanel } from './FarmHistoryPanel';

const DEFAULT_FPS = 1;

export default function CameraStream() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const videoRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<BlobPart[]>([]);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string>('');
  const [sessionId] = useState<string>(() => crypto.randomUUID());
  const [fps, setFps] = useState<number>(DEFAULT_FPS);
  const [isRecordingField, setIsRecordingField] = useState(false);
  const [fieldScanSummary, setFieldScanSummary] = useState<any | null>(null);

  const { isConnected, liveState, connectLiveSession, sendVideoFrame, sendAudioChunk, interruptAgent } =
    useLiveWebSocket();

  useEffect(() => {
    async function setupMedia() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' },
          audio: true,
        });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }

        connectLiveSession(sessionId);

        // Microphone capture via MediaRecorder (Opus / webm in most browsers).
        const audioTrack = mediaStream.getAudioTracks()[0];
        if (audioTrack) {
          const audioStream = new MediaStream([audioTrack]);
          const recorder = new MediaRecorder(audioStream, {
            mimeType: 'audio/webm;codecs=opus',
          });
          mediaRecorderRef.current = recorder;
          recorder.ondataavailable = async (event) => {
            if (event.data && event.data.size > 0) {
              const arrayBuffer = await event.data.arrayBuffer();
              const bytes = new Uint8Array(arrayBuffer);
              const base64 = btoa(String.fromCharCode(...bytes));
              sendAudioChunk(base64);
            }
          };
          recorder.start(500); // 500ms chunks
        }
      } catch (err) {
        setError('Failed to access camera/microphone.');
        // eslint-disable-next-line no-console
        console.error(err);
      }
    }
    setupMedia();

    return () => {
      stream?.getTracks().forEach((track) => track.stop());
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      if (videoRecorderRef.current && videoRecorderRef.current.state !== 'inactive') {
        videoRecorderRef.current.stop();
      }
      interruptAgent();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!isConnected || !videoRef.current || !canvasRef.current) return;

    const intervalMs = Math.max(250, 1000 / fps);

    const interval = window.setInterval(() => {
      const video = videoRef.current;
      const canvasEl = canvasRef.current;
      if (!video || !canvasEl || video.readyState !== 4) return;

      const width = video.videoWidth;
      const height = video.videoHeight;
      if (!width || !height) return;

      canvasEl.width = width;
      canvasEl.height = height;
      const ctx = canvasEl.getContext('2d');
      if (!ctx) return;

      ctx.drawImage(video, 0, 0, width, height);

      // Basic compression: JPEG at 0.6 quality.
      const base64Frame = canvasEl.toDataURL('image/jpeg', 0.6);
      sendVideoFrame(base64Frame);
    }, intervalMs);

    return () => window.clearInterval(interval);
  }, [isConnected, fps, sendVideoFrame]);

  const startFieldRecording = () => {
    if (!stream || isRecordingField) return;
    recordedChunksRef.current = [];
    try {
      const recorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp8,opus',
      });
      videoRecorderRef.current = recorder;
      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };
      recorder.onstop = async () => {
        const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        const formData = new FormData();
        formData.append('file', blob, 'field-walkthrough.webm');
        try {
          const baseUrl =
            (import.meta.env.VITE_API_URL as string | undefined) ??
            'http://localhost:8000';
          const res = await fetch(`${baseUrl}/api/field-scan`, {
            method: 'POST',
            body: formData,
          });
          if (res.ok) {
            const json = await res.json();
            setFieldScanSummary(json);
          }
        } catch (e) {
          // eslint-disable-next-line no-console
          console.error('Field scan upload failed', e);
        } finally {
          setIsRecordingField(false);
        }
      };
      recorder.start();
      setIsRecordingField(true);
      // Auto-stop after 20 seconds
      window.setTimeout(() => {
        if (videoRecorderRef.current && videoRecorderRef.current.state === 'recording') {
          videoRecorderRef.current.stop();
        }
      }, 20000);
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('Unable to start field recording', e);
    }
  };

  const stopFieldRecording = () => {
    if (videoRecorderRef.current && videoRecorderRef.current.state === 'recording') {
      videoRecorderRef.current.stop();
    }
  };

  return (
    <div className="relative w-full h-full bg-black aspect-[9/16] md:aspect-auto md:h-[600px]">
      {error ? (
        <div className="absolute inset-0 flex items-center justify-center text-white p-4 text-center">
          {error}
        </div>
      ) : (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
          <canvas ref={canvasRef} className="hidden" />

          {/* Accessibility / control strip */}
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 pointer-events-auto">
            <div className="glass-panel rounded-full px-4 py-2 flex items-center gap-3 shadow-lg">
              <label className="text-xs text-neutral-dark/80 font-medium flex items-center gap-2">
                FPS
                <input
                  type="range"
                  min={1}
                  max={5}
                  value={fps}
                  onChange={(e) => setFps(Number(e.target.value))}
                  className="w-24 accent-primary-blue"
                />
              </label>
              <button
                type="button"
                onClick={interruptAgent}
                className="text-xs font-semibold text-surface-white bg-neutral-dark/80 hover:bg-neutral-dark px-3 py-1.5 rounded-full transition-colors"
              >
                Interrupt
              </button>
              <button
                type="button"
                onClick={isRecordingField ? stopFieldRecording : startFieldRecording}
                className={`text-xs font-semibold px-3 py-1.5 rounded-full transition-colors ${
                  isRecordingField
                    ? 'bg-red-500 text-white hover:bg-red-600'
                    : 'bg-primary-blue text-white hover:bg-accent-blue'
                }`}
              >
                {isRecordingField ? 'Stop field scan' : 'Record field walkthrough'}
              </button>
            </div>
          </div>

          <LiveUIOverlay
            isConnected={isConnected}
            boxes={liveState.boxes}
            transcript={liveState.transcript}
            disease={liveState.disease}
            confidence={liveState.confidence}
            recommendedActions={liveState.recommendedActions}
          />

          {/* Right-side stacked intelligence panels */}
          <div className="absolute top-4 left-4 right-4 md:left-auto md:right-4 md:w-80 flex flex-col gap-2">
            <DiseaseForecastPanel forecast={liveState.spreadForecast as any} />
            <RiskForecastPanel microclimateRisk={liveState.microclimateRisk as any} />
            <OutbreakAlertPanel outbreak={liveState.outbreakAlert as any} />
            <EconomicImpactPanel yieldImpact={liveState.yieldImpact as any} />
            <TreatmentPlanPanel plan={liveState.treatmentPlan as any} />
            <FieldScanSummaryPanel summary={fieldScanSummary} />
            <FarmHistoryPanel farmMemory={liveState.farmMemory as any} />
          </div>
        </>
      )}
    </div>
  );
}

