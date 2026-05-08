/**
 * useNaelVoice — speak as Nael.
 *
 * Tries the `nael-tts` edge function. If unavailable, falls back
 * transparently to the browser's built-in SpeechSynthesis API.
 * The caller just does `speak("…")` and Nael talks.
 */

import { useCallback, useEffect, useRef, useState } from "react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export function useNaelVoice() {
  const [speaking, setSpeaking] = useState(false);
  const [enabled, setEnabled] = useState(true);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    return () => {
      audioRef.current?.pause();
      if (typeof window !== "undefined") window.speechSynthesis?.cancel();
    };
  }, []);

  const browserSpeak = useCallback((text: string) => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 1.02;
    u.pitch = 1;
    u.volume = 0.95;
    const v = window.speechSynthesis.getVoices().find(
      (vv) => /en[-_](GB|US|IN)/i.test(vv.lang) && /female|samantha|google/i.test(vv.name),
    );
    if (v) u.voice = v;
    u.onend = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(u);
  }, []);

  const speak = useCallback(
    async (text: string) => {
      if (!enabled || !text) return;
      audioRef.current?.pause();
      if (typeof window !== "undefined") window.speechSynthesis?.cancel();
      try {
        const token = localStorage.getItem("sb-access-token") || "";
        const res = await fetch(`${BACKEND_URL.replace(/\/$/, "")}/api/voice/voices/test`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ text }),
        });
        if (!res.ok) {
          browserSpeak(text);
          return;
        }
        const data = await res.json() as {
          audio_b64?: string;
          mime_type?: string;
          engine_used?: string;
        };
        if (!data.audio_b64 || data.engine_used === "browser") {
          browserSpeak(text);
          return;
        }
        const url = `data:${data.mime_type || "audio/wav"};base64,${data.audio_b64}`;
        const audio = new Audio(url);
        audioRef.current = audio;
        audio.onplay = () => setSpeaking(true);
        audio.onended = () => setSpeaking(false);
        audio.onerror = () => { setSpeaking(false); browserSpeak(text); };
        await audio.play();
      } catch {
        browserSpeak(text);
      }
    },
    [enabled, browserSpeak],
  );

  const stop = useCallback(() => {
    audioRef.current?.pause();
    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
    setSpeaking(false);
  }, []);

  return { speak, stop, speaking, enabled, setEnabled };
}
