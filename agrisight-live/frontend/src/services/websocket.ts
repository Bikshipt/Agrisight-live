/**
 * WebSocket Service
 * Manages connection to the backend for real-time multimodal streaming.
 * Expected env vars: VITE_WS_URL (backend base WebSocket URL, e.g. ws://localhost:8000/api)
 * Testing tips: Mock WebSocket globally to test connection and message handling.
 */
import { useState, useCallback, useRef, useEffect } from 'react';

export type AnnotationMessage = {
  type: 'annotation';
  boxes: Array<{
    x: number;
    y: number;
    w: number;
    h: number;
    label: string;
    score: number;
  }>;
};

export type TranscriptMessage = {
  type: 'transcript';
  text: string;
};

export type DiagnosisMessage = {
  type: 'diagnosis';
  disease: string;
  confidence: number;
  recommended_actions: string[];
};

export type SessionLogUpdateMessage = {
  type: 'session_log_update';
  status: string;
};

type CombinedResultMessage = {
  type: 'combined_result';
  diagnosis: {
    disease: string;
    confidence: number;
  };
  spread_forecast: unknown;
  microclimate_risk: unknown;
  outbreak_alert: unknown;
  yield_impact: unknown;
  treatment_plan: unknown;
  farm_memory: unknown;
};

export type LiveServerMessage =
  | AnnotationMessage
  | TranscriptMessage
  | DiagnosisMessage
  | SessionLogUpdateMessage
  | CombinedResultMessage
  | { type: 'heartbeat_ack' };

export interface LiveState {
  boxes: AnnotationMessage['boxes'];
  transcript: string;
  disease: string | null;
  confidence: number;
  recommendedActions: string[];
  spreadForecast: unknown | null;
  microclimateRisk: unknown | null;
  outbreakAlert: unknown | null;
  yieldImpact: unknown | null;
  treatmentPlan: unknown | null;
  farmMemory: unknown | null;
}

const INITIAL_STATE: LiveState = {
  boxes: [],
  transcript: '',
  disease: null,
  confidence: 0,
  recommendedActions: [],
  spreadForecast: null,
  microclimateRisk: null,
  outbreakAlert: null,
  yieldImpact: null,
  treatmentPlan: null,
  farmMemory: null,
};

export function useLiveWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [liveState, setLiveState] = useState<LiveState>(INITIAL_STATE);
  const wsRef = useRef<WebSocket | null>(null);
  const retryCountRef = useRef(0);
  const heartbeatRef = useRef<number | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  const closeHeartbeat = () => {
    if (heartbeatRef.current !== null) {
      window.clearInterval(heartbeatRef.current);
      heartbeatRef.current = null;
    }
  };

  const scheduleHeartbeat = () => {
    closeHeartbeat();
    heartbeatRef.current = window.setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 15000);
  };

  const handleServerMessage = useCallback((raw: string) => {
    let msg: LiveServerMessage;
    try {
      msg = JSON.parse(raw) as LiveServerMessage;
    } catch {
      return;
    }

    if (msg.type === 'heartbeat_ack') {
      return;
    }

    setLiveState((prev) => {
      switch (msg.type) {
        case 'annotation':
          return { ...prev, boxes: msg.boxes };
        case 'transcript':
          return {
            ...prev,
            // Simple running transcript
            transcript: prev.transcript
              ? `${prev.transcript} ${msg.text}`
              : msg.text,
          };
        case 'diagnosis':
          return {
            ...prev,
            disease: msg.disease,
            confidence: msg.confidence,
            recommendedActions: msg.recommended_actions,
          };
        case 'session_log_update':
          if (msg.status === 'interrupted') {
            return { ...prev, boxes: [], confidence: 0 };
          }
          return prev;
        case 'combined_result':
          return {
            ...prev,
            disease: msg.diagnosis?.disease ?? prev.disease,
            confidence: msg.diagnosis?.confidence ?? prev.confidence,
            spreadForecast: msg.spread_forecast,
            microclimateRisk: msg.microclimate_risk,
            outbreakAlert: msg.outbreak_alert,
            yieldImpact: msg.yield_impact,
            treatmentPlan: msg.treatment_plan,
            farmMemory: msg.farm_memory,
          };
        default:
          return prev;
      }
    });
  }, []);

  const connectLiveSession = useCallback((sessionId: string) => {
    sessionIdRef.current = sessionId;
    const baseUrl =
      (import.meta.env.VITE_WS_URL as string | undefined) ??
      'ws://localhost:8000/api';
    const url = `${baseUrl}/ws/live/${sessionId}`;

    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      retryCountRef.current = 0;
      scheduleHeartbeat();
    };

    ws.onclose = () => {
      setIsConnected(false);
      closeHeartbeat();
      // Auto-reconnect with exponential backoff
      const attempt = retryCountRef.current + 1;
      retryCountRef.current = attempt;
      const delay = Math.min(30000, 1000 * 2 ** Math.min(attempt, 5));
      if (sessionIdRef.current) {
        window.setTimeout(
          () => connectLiveSession(sessionIdRef.current as string),
          delay,
        );
      }
    };

    ws.onerror = () => {
      // Error will ultimately trigger onclose; we rely on reconnection logic there.
    };

    ws.onmessage = (event: MessageEvent<string>) => {
      handleServerMessage(event.data);
    };
  }, [handleServerMessage]);

  const sendVideoFrame = useCallback((imageBase64: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'video_frame',
          timestamp: Date.now(),
          image_base64: imageBase64,
        }),
      );
    }
  }, []);

  const sendAudioChunk = useCallback((audioBase64: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'audio_chunk',
          timestamp: Date.now(),
          audio_base64: audioBase64,
        }),
      );
    }
  }, []);

  const interruptAgent = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'user_interrupt' }));
    }
  }, []);

  useEffect(() => {
    return () => {
      closeHeartbeat();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    isConnected,
    liveState,
    connectLiveSession,
    sendVideoFrame,
    sendAudioChunk,
    interruptAgent,
    handleServerMessage,
  };
}

