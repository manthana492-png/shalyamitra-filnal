/**
 * WebRTC / Camera adapter.
 *
 * Three sources per camera, selectable at runtime via the per-tile toggle:
 *
 *   1. "placeholder" — animated holographic chrome (no MediaStream)
 *   2. "webcam"      — getUserMedia (laptop webcam / capture card)
 *   3. "webrtc"      — RTCPeerConnection negotiated via aria-realtime edge
 *                       function (relayed to the GPU backend / Triton overlays)
 *
 * The negotiation contract over the WebSocket is intentionally simple so any
 * GPU host (Lightning AI, RunPod, self-hosted) can implement it:
 *
 *   client → { type: "rtc.offer", camera, sdp }
 *   server → { type: "rtc.answer", camera, sdp }
 *   either → { type: "rtc.ice",   camera, candidate }
 *
 * In demo mode the relay closes with code "demo_mode" and we surface a clean
 * "offline" status so the UI never spins forever.
 */

import type { CameraId } from "@/lib/director";

export type CameraSource = "placeholder" | "webcam" | "webrtc";
export type CameraStatus = "idle" | "connecting" | "live" | "offline" | "error";

export type CameraStreamHandle = {
  id: CameraId;
  source: CameraSource;
  stream: MediaStream | null;
  status: CameraStatus;
  close: () => void;
};

const ANON_KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string;
const PROJECT_ID = import.meta.env.VITE_SUPABASE_PROJECT_ID as string;

function rtcSignalUrl() {
  return `wss://${PROJECT_ID}.functions.supabase.co/aria-realtime?apikey=${encodeURIComponent(ANON_KEY)}`;
}

async function connectWebcam(id: CameraId): Promise<CameraStreamHandle> {
  if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
    return { id, source: "webcam", stream: null, status: "error", close: () => {} };
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 } },
      audio: false,
    });
    return {
      id, source: "webcam", stream, status: "live",
      close: () => stream.getTracks().forEach((t) => t.stop()),
    };
  } catch {
    return { id, source: "webcam", stream: null, status: "error", close: () => {} };
  }
}

async function connectWebRtc(id: CameraId, sessionId: string | undefined): Promise<CameraStreamHandle> {
  let pc: RTCPeerConnection | null = null;
  let ws: WebSocket | null = null;
  let stream: MediaStream | null = null;

  const handle: CameraStreamHandle = {
    id, source: "webrtc", stream: null, status: "connecting",
    close: () => {
      try { pc?.close(); } catch { /* noop */ }
      try { ws?.close(); } catch { /* noop */ }
      stream?.getTracks().forEach((t) => t.stop());
    },
  };

  try {
    pc = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
    });
    pc.ontrack = (e) => {
      stream = e.streams[0];
      handle.stream = stream;
      handle.status = "live";
    };
    // We only want to *receive* video on this PC.
    pc.addTransceiver("video", { direction: "recvonly" });

    ws = new WebSocket(rtcSignalUrl());

    await new Promise<void>((resolve, reject) => {
      ws!.onopen = () => resolve();
      ws!.onerror = () => reject(new Error("ws_error"));
      setTimeout(() => reject(new Error("ws_timeout")), 4000);
    });

    ws.send(JSON.stringify({
      type: "auth", token: ANON_KEY, sessionId: sessionId ?? "demo",
    }));

    pc.onicecandidate = (e) => {
      if (e.candidate && ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "rtc.ice", camera: id, candidate: e.candidate }));
      }
    };

    ws.onmessage = async (e) => {
      try {
        const msg = JSON.parse(typeof e.data === "string" ? e.data : "");
        if (msg.type === "error" && msg.code === "demo_mode") {
          handle.status = "offline";
          try { ws?.close(); } catch { /* noop */ }
          return;
        }
        if (msg.type === "rtc.answer" && msg.camera === id) {
          await pc!.setRemoteDescription({ type: "answer", sdp: msg.sdp });
        } else if (msg.type === "rtc.ice" && msg.camera === id) {
          try { await pc!.addIceCandidate(msg.candidate); } catch { /* noop */ }
        }
      } catch { /* noop */ }
    };
    ws.onclose = () => {
      if (handle.status === "connecting") handle.status = "offline";
    };

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    ws.send(JSON.stringify({ type: "rtc.offer", camera: id, sdp: offer.sdp }));

    return handle;
  } catch {
    handle.status = "offline";
    handle.close();
    return handle;
  }
}

export async function connectCamera(
  id: CameraId,
  source: CameraSource,
  sessionId?: string,
): Promise<CameraStreamHandle> {
  if (source === "webcam") return connectWebcam(id);
  if (source === "webrtc") return connectWebRtc(id, sessionId);
  return { id, source: "placeholder", stream: null, status: "idle", close: () => {} };
}
