// ARIA — Realtime relay (WebSocket bridge to NVIDIA GPU backend).
//
// In production this function relays the browser's WebSocket to the GPU
// backend running NVIDIA Riva (ASR), NeMo (proactive dialog), Morpheus
// (PHI redaction), and Triton (vision). The protocol is defined in
// `src/lib/gpu-adapter.ts`.
//
// Until you set GPU_BACKEND_URL / GPU_BACKEND_TOKEN as project secrets, this
// function operates in "demo" mode and immediately tells the client to fall
// back to the scripted local playback.

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

function jsonRes(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

serve((req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  const url = new URL(req.url);
  const upgrade = req.headers.get("upgrade") ?? "";

  // Health check
  if (url.pathname.endsWith("/health") || (req.method === "GET" && upgrade.toLowerCase() !== "websocket")) {
    const host = Deno.env.get("GPU_BACKEND_HOST") ?? "demo";
    const hasUrl = !!Deno.env.get("GPU_BACKEND_URL");
    const hasToken = !!Deno.env.get("GPU_BACKEND_TOKEN");
    return jsonRes({
      ok: true,
      mode: hasUrl && hasToken ? "live" : "demo",
      host,
      hasUrl,
      hasToken,
      protocol: "v1",
      message: hasUrl && hasToken
        ? `Relay configured for ${host} backend.`
        : "GPU backend not configured. Set GPU_BACKEND_URL + GPU_BACKEND_TOKEN to go live.",
    });
  }

  // WebSocket upgrade
  if (upgrade.toLowerCase() !== "websocket") {
    return jsonRes({ error: "Expected WebSocket upgrade" }, 400);
  }

  const upstreamUrl = Deno.env.get("GPU_BACKEND_URL");
  const upstreamToken = Deno.env.get("GPU_BACKEND_TOKEN");

  const { socket: client, response } = Deno.upgradeWebSocket(req);

  if (!upstreamUrl || !upstreamToken) {
    // Demo mode — tell the client to use the scripted feed.
    client.onopen = () => {
      client.send(JSON.stringify({
        type: "error",
        code: "demo_mode",
        message: "GPU backend not configured. Falling back to scripted demo session.",
      }));
      try { client.close(1000, "demo_mode"); } catch { /* noop */ }
    };
    return response;
  }

  let upstream: WebSocket | null = null;
  let pingTimer: number | null = null;

  const connectUpstream = () => {
    try {
      upstream = new WebSocket(upstreamUrl, [`bearer.${upstreamToken}`]);
    } catch (e) {
      client.send(JSON.stringify({ type: "error", code: "upstream_init_failed", message: String(e) }));
      try { client.close(1011, "upstream_init_failed"); } catch { /* noop */ }
      return;
    }
    upstream.onopen = () => {
      // Forward auth handshake
      upstream?.send(JSON.stringify({ type: "auth", token: upstreamToken }));
      // Heartbeat
      pingTimer = setInterval(() => {
        try { upstream?.send(JSON.stringify({ type: "ping", ts: Date.now() })); } catch { /* noop */ }
      }, 15000) as unknown as number;
    };
    upstream.onmessage = (e) => {
      try { client.send(typeof e.data === "string" ? e.data : new Uint8Array(e.data as ArrayBuffer)); } catch { /* noop */ }
    };
    upstream.onerror = () => {
      try { client.send(JSON.stringify({ type: "error", code: "upstream_error", message: "GPU backend connection error" })); } catch { /* noop */ }
    };
    upstream.onclose = () => {
      if (pingTimer !== null) clearInterval(pingTimer);
      pingTimer = null;
      try { client.close(1000, "upstream_closed"); } catch { /* noop */ }
    };
  };

  client.onopen = () => connectUpstream();
  client.onmessage = (e) => {
    try { upstream?.send(typeof e.data === "string" ? e.data : new Uint8Array(e.data as ArrayBuffer)); } catch { /* noop */ }
  };
  client.onclose = () => {
    if (pingTimer !== null) clearInterval(pingTimer);
    try { upstream?.close(); } catch { /* noop */ }
  };

  return response;
});
