// mock-gpu — server-side scripted ARIA event stream.
//
// Emits the same `ServerEvent` shape as the real GPU backend (see
// src/lib/gpu-adapter.ts) so the realtime pipeline can be exercised
// end-to-end without any NVIDIA hardware. Swapping to the real backend is a
// single env-var change (GPU_BACKEND_URL) — clients keep the same protocol.

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

type Speaker = "surgeon" | "anaesthetist" | "nurse" | "aria" | "system";
type Severity = "info" | "caution" | "warning" | "critical";

type Evt =
  | { kind: "t"; at: number; speaker: Speaker; text: string; piiSpans?: number[][] }
  | { kind: "a"; at: number; severity: Severity; title: string; body: string; source: string };

const SCRIPT: Evt[] = [
  { kind: "t", at: 1, speaker: "system", text: "Mock GPU stream connected — emitting scripted ServerEvents." },
  { kind: "t", at: 3, speaker: "anaesthetist", text: "Patient asleep, paralysed, ready for prep." },
  { kind: "t", at: 7, speaker: "surgeon", text: "Confirming [REDACTED], DOB [REDACTED], for laparoscopic cholecystectomy.", piiSpans: [[12, 22], [29, 39]] },
  { kind: "t", at: 12, speaker: "nurse", text: "Time-out complete. Antibiotic given at induction." },
  { kind: "t", at: 16, speaker: "aria", text: "Time-out logged. Antibiotic prophylaxis recorded within window." },
  { kind: "t", at: 26, speaker: "surgeon", text: "Veress needle in. Starting insufflation to 12 mmHg." },
  { kind: "a", at: 40, severity: "info", source: "protocol",
    title: "Insufflation phase",
    body: "Pneumoperitoneum confirmed. Keep intra-abdominal pressure ≤ 15 mmHg unless clinically required." },
  { kind: "t", at: 55, speaker: "surgeon", text: "Three working ports in. Camera in." },
  { kind: "t", at: 70, speaker: "surgeon", text: "Retracting fundus cephalad. Exposing Calot's triangle." },
  { kind: "a", at: 80, severity: "caution", source: "vision",
    title: "Critical View of Safety — not yet achieved",
    body: "Vision module has not yet detected a clear CVS. Consider continuing dissection before clipping." },
  { kind: "t", at: 95, speaker: "surgeon", text: "I have what looks like the cystic duct and artery clearly." },
  { kind: "t", at: 100, speaker: "aria", text: "Two tubular structures isolated. Critical View of Safety appears achieved." },
  { kind: "a", at: 110, severity: "warning", source: "vitals",
    title: "MAP trending down — 68 mmHg",
    body: "Mean arterial pressure has dropped 14 points over 90 seconds. Consider reviewing depth of anaesthesia." },
  { kind: "t", at: 118, speaker: "anaesthetist", text: "I see it — bolus 250ml crystalloid." },
  { kind: "t", at: 130, speaker: "surgeon", text: "Clipping the cystic artery. Three clips proximal." },
  { kind: "t", at: 145, speaker: "aria", text: "Both structures clipped and divided. No bleeding visible." },
  { kind: "t", at: 165, speaker: "surgeon", text: "Gallbladder fully detached. Placing in retrieval bag." },
  { kind: "t", at: 180, speaker: "aria", text: "Procedure summary ready for sign-out." },
];

function vitalsAt(t: number) {
  const hr = Math.round(72 + 6 * Math.sin(t / 12) + (t > 100 && t < 120 ? 18 : 0));
  const spo2 = Math.max(88, Math.round(98 - (t > 110 && t < 118 ? 6 : 0) + Math.sin(t / 9)));
  const map = Math.round(82 + 4 * Math.sin(t / 18) - (t > 100 && t < 120 ? 12 : 0));
  const etco2 = Math.round(35 + 2 * Math.sin(t / 7) + (t > 110 && t < 118 ? 4 : 0));
  return { hr, spo2, map, etco2 };
}

serve((req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  const url = new URL(req.url);
  const upgrade = req.headers.get("upgrade") ?? "";

  if (url.pathname.endsWith("/health") || (req.method === "GET" && upgrade.toLowerCase() !== "websocket")) {
    return new Response(JSON.stringify({
      ok: true, mode: "mock", protocol: "v1",
      message: "mock-gpu emits scripted ServerEvents over WebSocket.",
    }), { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  }

  if (upgrade.toLowerCase() !== "websocket") {
    return new Response(JSON.stringify({ error: "Expected WebSocket upgrade" }),
      { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  }

  const { socket, response } = Deno.upgradeWebSocket(req);
  let started = 0;
  let cursor = 0;
  let timer: number | null = null;
  let mode: "silent" | "reactive" | "proactive" = "reactive";

  const tick = () => {
    const t = (Date.now() - started) / 1000;
    // vitals every second
    if (Math.floor(t) !== Math.floor(t - 1)) {
      const v = vitalsAt(Math.floor(t));
      try { socket.send(JSON.stringify({ type: "vitals", at: Math.floor(t), ...v })); } catch { /* noop */ }
    }
    while (cursor < SCRIPT.length && SCRIPT[cursor].at <= t) {
      const e = SCRIPT[cursor++];
      if (e.kind === "t") {
        try {
          socket.send(JSON.stringify({
            type: "transcript", at: e.at, speaker: e.speaker, text: e.text,
            redacted: !!e.piiSpans, piiSpans: e.piiSpans ?? [],
          }));
        } catch { /* noop */ }
      } else {
        const sev = e.severity;
        if (mode === "silent" && sev !== "critical") continue;
        if (mode === "reactive" && (sev === "info" || sev === "caution")) continue;
        try {
          socket.send(JSON.stringify({
            type: "alert", at: e.at, severity: sev,
            title: e.title, body: e.body, source: e.source,
          }));
        } catch { /* noop */ }
      }
    }
    if (cursor >= SCRIPT.length && t > SCRIPT[SCRIPT.length - 1].at + 5) {
      try { socket.close(1000, "complete"); } catch { /* noop */ }
    }
  };

  socket.onopen = () => {
    started = Date.now();
    timer = setInterval(tick, 1000) as unknown as number;
  };
  socket.onmessage = (e) => {
    try {
      const msg = JSON.parse(typeof e.data === "string" ? e.data : "");
      if (msg.type === "control" && msg.mode) mode = msg.mode;
      if (msg.type === "ping") socket.send(JSON.stringify({ type: "pong", ts: msg.ts }));
    } catch { /* noop */ }
  };
  socket.onclose = () => { if (timer !== null) clearInterval(timer); };
  socket.onerror = () => { if (timer !== null) clearInterval(timer); };

  return response;
});
