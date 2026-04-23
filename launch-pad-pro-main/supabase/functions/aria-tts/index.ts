// ARIA — Text-to-Speech edge function
// Streams ARIA's voice via Lovable AI Gateway (Gemini 2.5 Flash Image/Audio).
// Returns base64-encoded MP3 audio in JSON for easy client playback.
//
// NOTE: Lovable AI Gateway currently exposes text models. For TTS we use
// Gemini's audio-capable model. If unavailable, we degrade gracefully and
// the client will fall back to the browser's SpeechSynthesis API.

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { text } = await req.json();
    if (!text || typeof text !== "string" || text.length > 1000) {
      return new Response(
        JSON.stringify({ error: "text required (string, ≤1000 chars)" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) {
      return new Response(
        JSON.stringify({ error: "LOVABLE_API_KEY not configured", fallback: "browser_tts" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    // Use Lovable AI Gateway. We try to coerce structured TTS via tool calling.
    // If the gateway's TTS support is unavailable, we return a clean fallback
    // signal so the client uses the browser's SpeechSynthesis API.
    const upstream = await fetch("https://ai.gateway.lovable.dev/v1/audio/speech", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash",
        input: text,
        voice: "alloy",
        format: "mp3",
      }),
    });

    if (upstream.status === 429) {
      return new Response(
        JSON.stringify({ error: "rate_limited", fallback: "browser_tts" }),
        { status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }
    if (upstream.status === 402) {
      return new Response(
        JSON.stringify({ error: "payment_required", fallback: "browser_tts" }),
        { status: 402, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }
    if (!upstream.ok) {
      // Most likely the audio endpoint isn't exposed by the gateway yet —
      // tell the client to fall back to browser TTS.
      return new Response(
        JSON.stringify({ error: "tts_unavailable", fallback: "browser_tts" }),
        { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } },
      );
    }

    const buf = await upstream.arrayBuffer();
    // Encode to base64 for JSON transport.
    const bytes = new Uint8Array(buf);
    let binary = "";
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    const audioBase64 = btoa(binary);

    return new Response(
      JSON.stringify({ audioBase64, mimeType: "audio/mpeg" }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  } catch (e) {
    console.error("aria-tts error:", e);
    return new Response(
      JSON.stringify({
        error: e instanceof Error ? e.message : "unknown_error",
        fallback: "browser_tts",
      }),
      { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } },
    );
  }
});
