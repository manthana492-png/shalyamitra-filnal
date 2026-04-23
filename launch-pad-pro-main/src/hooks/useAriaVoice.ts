/**
 * useAriaVoice — speak as ARIA.
 *
 * Tries the `aria-tts` edge function (Lovable AI Gateway). If unavailable
 * (status quota, no audio endpoint, network error), falls back transparently
 * to the browser's built-in SpeechSynthesis API. Either way, the caller just
 * does `speak("...")` and ARIA talks.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

export function useAriaVoice() {
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
    // Prefer a calm English voice if available.
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
      // Stop anything currently playing.
      audioRef.current?.pause();
      if (typeof window !== "undefined") window.speechSynthesis?.cancel();

      try {
        const { data, error } = await supabase.functions.invoke("aria-tts", {
          body: { text },
        });
        if (error || !data || data.fallback === "browser_tts" || !data.audioBase64) {
          browserSpeak(text);
          return;
        }
        const url = `data:${data.mimeType};base64,${data.audioBase64}`;
        const audio = new Audio(url);
        audioRef.current = audio;
        audio.onplay = () => setSpeaking(true);
        audio.onended = () => setSpeaking(false);
        audio.onerror = () => {
          setSpeaking(false);
          browserSpeak(text);
        };
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
