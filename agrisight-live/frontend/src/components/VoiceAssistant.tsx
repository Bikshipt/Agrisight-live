/**
 * VoiceAssistant
 * Provides a simple conversational interface using Web Speech API and backend voice-query.
 * Expected env vars: VITE_API_URL
 * Testing tips: Mock window.SpeechRecognition and fetch.
 */
import React, { useEffect, useRef, useState } from 'react';

type RecognitionType = SpeechRecognition | webkitSpeechRecognition;

declare global {
  interface Window {
    webkitSpeechRecognition?: {
      new (): webkitSpeechRecognition;
    };
  }
}

export function VoiceAssistant() {
  const [listening, setListening] = useState(false);
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const recognitionRef = useRef<RecognitionType | null>(null);

  useEffect(() => {
    const SpeechRec =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRec) return;
    const rec: RecognitionType = new SpeechRec();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = language === 'hi' ? 'hi-IN' : 'en-US';
    rec.onresult = (event: SpeechRecognitionEvent) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
      void sendToBackend(text);
    };
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
  }, [language]);

  const baseUrl =
    (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000';

  async function sendToBackend(text: string) {
    try {
      const res = await fetch(`${baseUrl}/api/voice-query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language }),
      });
      if (res.ok) {
        const json = await res.json();
        setResponse(json.answer);
        speak(json.answer);
      }
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('Voice query failed', e);
    }
  }

  function speak(text: string) {
    const synth = window.speechSynthesis;
    if (!synth) return;
    synth.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = language === 'hi' ? 'hi-IN' : 'en-US';
    synth.speak(utter);
  }

  function toggleListening() {
    const rec = recognitionRef.current;
    if (!rec) return;
    if (listening) {
      rec.stop();
      setListening(false);
    } else {
      setTranscript('');
      setResponse('');
      rec.lang = language === 'hi' ? 'hi-IN' : 'en-US';
      rec.start();
      setListening(true);
    }
  }

  return (
    <div className="glass-panel rounded-2xl p-4 text-xs md:text-sm text-neutral-dark">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-sora text-sm font-semibold">AI Voice Assistant</h3>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value as 'en' | 'hi')}
          className="text-xs bg-transparent border border-neutral-dark/10 rounded-full px-2 py-0.5 focus:outline-none"
        >
          <option value="en">English</option>
          <option value="hi">हिन्दी</option>
        </select>
      </div>
      <button
        type="button"
        onClick={toggleListening}
        className={`text-xs font-semibold px-3 py-1.5 rounded-full transition-colors ${
          listening ? 'bg-red-500 text-white' : 'bg-primary-blue text-white'
        }`}
      >
        {listening ? 'Stop listening' : 'Ask a question'}
      </button>
      {transcript && (
        <p className="mt-2 text-neutral-dark/80">
          <span className="font-semibold">You:</span> {transcript}
        </p>
      )}
      {response && (
        <p className="mt-1 text-neutral-dark/80">
          <span className="font-semibold">AI:</span> {response}
        </p>
      )}
    </div>
  );
}

