/**
 * useAlertAudio — Web Audio API alert tones for ShalyaMitra.
 *
 * Spec: "Every visual alert has an accompanying audio signal"
 *
 * Generates pure tones using Web Audio API (zero dependencies):
 * - CRITICAL: 3 short beeps at 800Hz (200ms each, 100ms gap)
 * - WARNING:  1 longer tone at 600Hz (400ms)
 * - INFO:     1 soft chime at 400Hz (200ms, low volume)
 *
 * Uses a singleton AudioContext to avoid browser limits.
 */

let ctx: AudioContext | null = null;

function getCtx(): AudioContext {
  if (!ctx) ctx = new AudioContext();
  return ctx;
}

function playTone(freq: number, durationMs: number, volume: number = 0.3) {
  try {
    const ac = getCtx();
    if (ac.state === "suspended") ac.resume();

    const osc = ac.createOscillator();
    const gain = ac.createGain();

    osc.type = "sine";
    osc.frequency.value = freq;

    gain.gain.setValueAtTime(0, ac.currentTime);
    // Smooth attack
    gain.gain.linearRampToValueAtTime(volume, ac.currentTime + 0.01);
    // Sustain
    gain.gain.setValueAtTime(volume, ac.currentTime + durationMs / 1000 - 0.02);
    // Smooth release
    gain.gain.linearRampToValueAtTime(0, ac.currentTime + durationMs / 1000);

    osc.connect(gain);
    gain.connect(ac.destination);

    osc.start(ac.currentTime);
    osc.stop(ac.currentTime + durationMs / 1000 + 0.05);
  } catch {
    // Silently fail — audio is supplementary, never block the UI
  }
}

export function playCriticalAlert() {
  // 3 rapid beeps: 200ms on, 100ms gap
  playTone(800, 200, 0.4);
  setTimeout(() => playTone(800, 200, 0.4), 300);
  setTimeout(() => playTone(800, 200, 0.4), 600);
}

export function playWarningAlert() {
  // Single longer tone
  playTone(600, 400, 0.25);
}

export function playInfoAlert() {
  // Soft short chime
  playTone(400, 200, 0.12);
}

/**
 * Play the appropriate alert tone for a severity level.
 */
export function playAlertTone(severity: "critical" | "warning" | "caution" | "info") {
  switch (severity) {
    case "critical":
      playCriticalAlert();
      break;
    case "warning":
    case "caution":
      playWarningAlert();
      break;
    case "info":
      playInfoAlert();
      break;
  }
}
