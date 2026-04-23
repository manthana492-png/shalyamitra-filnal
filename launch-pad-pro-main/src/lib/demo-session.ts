/**
 * ShalyaMitra — Scripted Demo Session
 *
 * A simulated 6-minute laparoscopic cholecystectomy showcasing ALL eight
 * intelligence pillars:
 *  - Nael (conversational), Haemorrhage Sentinel, Monitor Sentinel,
 *    The Sentinel (instruments), The Pharmacist, The Scholar,
 *    The Oracle (Marma), Devil's Advocate, The Chronicler
 *
 * IMPORTANT: All clinical content is illustrative for demo purposes only.
 */

import type { PillarId, ShalyaAlert } from "./pillars";
import type { OverlayItem, InstrumentCountState, RetractionTimerState, KnowledgePillar } from "./director";
import type { OracleData } from "@/components/console/OracleContent";
import type { AdvocateEvent } from "@/components/console/DevilsAdvocate";
import type { TimelineEvent } from "@/components/console/SurgeryTimeline";

export type DemoSpeaker = "surgeon" | "anaesthetist" | "nurse" | "nael" | "system";
export type DemoAlertSeverity = "info" | "caution" | "warning" | "critical";

export type DemoTranscriptEvent = {
  kind: "transcript";
  at: number;
  speaker: DemoSpeaker;
  text: string;
};

export type DemoAlertEvent = {
  kind: "alert";
  at: number;
  severity: DemoAlertSeverity;
  pillar: PillarId;
  title: string;
  body: string;
  source: string;
  priority: number;
};

export type DemoVitalsEvent = {
  kind: "vitals";
  at: number;
  hr: number;
  spo2: number;
  map: number;
  etco2: number;
  temp: number;
  rr: number;
};

export type DemoPhaseEvent = {
  kind: "phase";
  at: number;
  phase: string;
};

export type DemoOverlayEvent = {
  kind: "overlays";
  at: number;
  items: OverlayItem[];
};

export type DemoKnowledgeEvent = {
  kind: "knowledge";
  at: number;
  pillar: KnowledgePillar;
  content: unknown;
};

export type DemoInstrumentEvent = {
  kind: "instrument_count";
  at: number;
  data: InstrumentCountState;
};

export type DemoRetractionEvent = {
  kind: "retraction";
  at: number;
  timer: RetractionTimerState;
};

export type DemoAdvocateEvent = {
  kind: "advocate";
  at: number;
  event: AdvocateEvent;
};

export type DemoNaelStateEvent = {
  kind: "nael_state";
  at: number;
  state: "idle" | "listening" | "thinking" | "speaking";
};

export type DemoEvent =
  | DemoTranscriptEvent
  | DemoAlertEvent
  | DemoVitalsEvent
  | DemoPhaseEvent
  | DemoOverlayEvent
  | DemoKnowledgeEvent
  | DemoInstrumentEvent
  | DemoRetractionEvent
  | DemoAdvocateEvent
  | DemoNaelStateEvent;

export const DEMO_PROCEDURE = "Laparoscopic Cholecystectomy";
export const DEMO_PATIENT_CODE = "PT-DEMO-001";

/** Baseline vitals with realistic drift. */
export function vitalsAt(t: number): {
  hr: number; spo2: number; map: number; etco2: number; temp: number; rr: number;
} {
  const hr = Math.round(72 + 6 * Math.sin(t / 12) + (t > 200 && t < 225 ? 22 : 0));
  const spo2 = Math.max(88, Math.round(98 - (t > 205 && t < 220 ? 6 : 0) + Math.sin(t / 9)));
  const map = Math.round(82 + 4 * Math.sin(t / 18) - (t > 200 && t < 225 ? 14 : 0));
  const etco2 = Math.round(35 + 2 * Math.sin(t / 7) + (t > 205 && t < 220 ? 4 : 0));
  const temp = parseFloat((36.4 + 0.1 * Math.sin(t / 60)).toFixed(1));
  const rr = Math.round(14 + 2 * Math.sin(t / 15));
  return { hr, spo2, map, etco2, temp, rr };
}

// Mock Oracle data
const ORACLE_MARMA_DATA: OracleData = {
  marmaName: "Nābhi Marma",
  devanagari: "नाभि मर्म",
  classification: "Sadya Praṇahara",
  classificationSeverity: "sadya_pranahara",
  modernMapping: "Periumbilical region — abdominal aortic bifurcation, inferior mesenteric artery, autonomic nerve plexuses. Corresponds to the coeliac/mesenteric vascular territory.",
  consequences: "Injury causes immediate haemodynamic collapse. Classical texts describe 'sādyaḥ praṇahara' — death follows swiftly.",
  protectiveDoctrine: "Maintain absolute awareness of depth during umbilical port insertion. The posterior wall is thin; the great vessels lie mere centimetres behind the peritoneum.",
  shloka: "मर्माणि नाम ते विशेषायतनानि धातूनां, तेषु स्वभावत एव विशेषेण प्राणास्तिष्ठन्ति।",
  shlokaReference: "Suśruta Saṃhitā, Śārīrasthāna 6.16",
};

// Mock overlay items (anatomy near Calot's triangle)
const DISSECTION_OVERLAYS: OverlayItem[] = [
  { id: "ov1", type: "artery", bbox: [0.35, 0.3, 0.48, 0.55], label: "Cystic Artery", confidence: 0.89 },
  { id: "ov2", type: "duct", bbox: [0.42, 0.35, 0.58, 0.65], label: "Common Bile Duct", confidence: 0.92 },
  { id: "ov3", type: "vein", bbox: [0.55, 0.25, 0.72, 0.5], label: "Portal Vein", confidence: 0.85 },
  { id: "ov4", type: "duct", bbox: [0.3, 0.45, 0.45, 0.7], label: "Cystic Duct", confidence: 0.91 },
];

export const DEMO_EVENTS: DemoEvent[] = [
  // ═══════════════════════════════════════════════════════════════════
  // T+0: Session start
  // ═══════════════════════════════════════════════════════════════════
  { kind: "phase", at: 0, phase: "preparation" },
  { kind: "transcript", at: 2, speaker: "system", text: "All systems connected. Nael is listening." },
  { kind: "nael_state", at: 2, state: "speaking" },
  { kind: "transcript", at: 6, speaker: "nael", text: "Good morning, Dr. Shivalumar. Pre-operative analysis loaded for laparoscopic cholecystectomy. Two risk flags identified. I'm here when you need me." },
  { kind: "nael_state", at: 10, state: "idle" },

  { kind: "transcript", at: 14, speaker: "anaesthetist", text: "Patient asleep, paralysed, ready for prep." },
  { kind: "transcript", at: 18, speaker: "surgeon", text: "Confirming patient identity and procedure. Time-out please." },
  { kind: "transcript", at: 24, speaker: "nurse", text: "Time-out complete. Antibiotic given at induction." },
  { kind: "nael_state", at: 25, state: "speaking" },
  { kind: "transcript", at: 26, speaker: "nael", text: "Time-out logged. Antibiotic prophylaxis recorded within window." },
  { kind: "nael_state", at: 29, state: "idle" },

  // ═══════════════════════════════════════════════════════════════════
  // T+30: Access phase — instrument count begins
  // ═══════════════════════════════════════════════════════════════════
  { kind: "phase", at: 30, phase: "access" },
  { kind: "transcript", at: 32, speaker: "surgeon", text: "Veress needle in. Starting insufflation to 12 mmHg." },
  { kind: "instrument_count", at: 35, data: { deployed: 14, accounted: 14, matched: true } },

  { kind: "alert", at: 45, severity: "info", pillar: "sentinel", priority: 8,
    title: "Instrument Count Started",
    body: "14 instruments, 6 swabs deployed. Sentinel tracking active.",
    source: "sentinel" },

  { kind: "transcript", at: 48, speaker: "anaesthetist", text: "Pressures normal. EtCO₂ steady." },

  { kind: "alert", at: 55, severity: "info", pillar: "nael", priority: 8,
    title: "Insufflation phase",
    body: "Pneumoperitoneum confirmed. Reminder: keep intra-abdominal pressure ≤ 15 mmHg unless clinically required.",
    source: "protocol" },

  // ═══════════════════════════════════════════════════════════════════
  // T+60: Dissection — anatomy overlays fire
  // ═══════════════════════════════════════════════════════════════════
  { kind: "phase", at: 60, phase: "dissection" },
  { kind: "transcript", at: 62, speaker: "surgeon", text: "Three working ports in. Camera in. Retracting fundus cephalad." },
  { kind: "overlays", at: 65, items: DISSECTION_OVERLAYS },
  { kind: "nael_state", at: 66, state: "speaking" },
  { kind: "transcript", at: 67, speaker: "nael", text: "Dissection phase identified. Anatomy overlays available — cystic artery, CBD, portal vein visible in current view." },
  { kind: "nael_state", at: 72, state: "idle" },

  { kind: "transcript", at: 78, speaker: "surgeon", text: "Beginning dissection of the cystic pedicle." },

  { kind: "alert", at: 85, severity: "caution", pillar: "nael", priority: 7,
    title: "Critical View of Safety — not yet achieved",
    body: "Vision module has not yet detected a clear Critical View of Safety. Consider continuing dissection until both cystic structures are clearly isolated before clipping.",
    source: "vision" },

  // ═══════════════════════════════════════════════════════════════════
  // T+90: Monitor Sentinel — vital trend
  // ═══════════════════════════════════════════════════════════════════
  { kind: "alert", at: 92, severity: "info", pillar: "monitor", priority: 7,
    title: "Heart rate climbing",
    body: "HR trending up: 78 → 96 over 3 minutes. Consistent with surgical stress response. No intervention required at this time.",
    source: "monitor-sentinel" },

  // ═══════════════════════════════════════════════════════════════════
  // T+120: Oracle — Marma proximity event
  // ═══════════════════════════════════════════════════════════════════
  { kind: "knowledge", at: 120, pillar: "oracle", content: ORACLE_MARMA_DATA },
  { kind: "nael_state", at: 121, state: "speaking" },
  { kind: "transcript", at: 122, speaker: "nael", text: "Oracle advisory: Nābhi Marma proximity detected. Periumbilical critical zone — Sadya Praṇahara classification. Protective doctrine loaded." },
  { kind: "nael_state", at: 128, state: "idle" },

  // ═══════════════════════════════════════════════════════════════════
  // T+150: Pharmacist — drug log
  // ═══════════════════════════════════════════════════════════════════
  { kind: "alert", at: 150, severity: "info", pillar: "pharmacist", priority: 8,
    title: "Fentanyl 100μg IV logged",
    body: "Total opioid load: 100μg fentanyl. Remifentanil infusion at 0.15μg/kg/min. No interaction flags.",
    source: "pharmacist" },
  { kind: "transcript", at: 152, speaker: "nael", text: "Pharmacist: Fentanyl 100 microgram IV logged. No interaction alerts." },

  { kind: "transcript", at: 160, speaker: "surgeon", text: "Continuing dissection. Hartmann's pouch now mobile." },

  { kind: "transcript", at: 172, speaker: "surgeon", text: "I have what looks like the cystic duct and artery clearly." },
  { kind: "nael_state", at: 173, state: "speaking" },
  { kind: "transcript", at: 175, speaker: "nael", text: "Two tubular structures isolated. Critical View of Safety appears achieved on current view." },
  { kind: "nael_state", at: 179, state: "idle" },

  // ═══════════════════════════════════════════════════════════════════
  // T+180: Retraction timer starts
  // ═══════════════════════════════════════════════════════════════════
  { kind: "retraction", at: 180, timer: {
    id: "ret-1",
    structure: "Lateral hepatic retractor",
    startedAt: 180,
    thresholdMinutes: 20,
  }},
  { kind: "transcript", at: 182, speaker: "nael", text: "Retraction timer started: lateral hepatic retractor. 20-minute threshold." },

  // ═══════════════════════════════════════════════════════════════════
  // T+210: HAEMORRHAGE ALERT — Critical Alert Path
  // ═══════════════════════════════════════════════════════════════════
  { kind: "alert", at: 210, severity: "critical", pillar: "haemorrhage", priority: 1,
    title: "⚠ POSSIBLE ARTERIAL BLEED",
    body: "Pulsatile pattern detected lateral to dissection field. Haemorrhage Sentinel confidence: 94%. Automatic camera focus activated.",
    source: "haemorrhage-sentinel" },
  { kind: "nael_state", at: 210, state: "speaking" },
  { kind: "transcript", at: 211, speaker: "nael", text: "ALERT — Possible arterial bleed. Pulsatile pattern lateral to dissection. I've expanded the surgical camera." },

  // T+220: Resolved
  { kind: "nael_state", at: 220, state: "idle" },
  { kind: "transcript", at: 222, speaker: "surgeon", text: "That's controlled. Small cystic artery branch — cauterised." },
  { kind: "transcript", at: 226, speaker: "nael", text: "Haemorrhage resolved. Returning to overview." },

  // Clipping
  { kind: "transcript", at: 232, speaker: "surgeon", text: "Clipping the cystic artery. Three clips proximal." },
  { kind: "transcript", at: 240, speaker: "surgeon", text: "Now the cystic duct. Three clips, dividing." },
  { kind: "transcript", at: 245, speaker: "nael", text: "Both structures clipped and divided. No bleeding visible." },

  // ═══════════════════════════════════════════════════════════════════
  // T+240: Devil's Advocate
  // ═══════════════════════════════════════════════════════════════════
  { kind: "advocate", at: 248, event: {
    question: "The Scholar identified borderline platelet function pre-operatively. Are you satisfied the haemostasis is adequate before proceeding with liver bed dissection?",
    evidence: "Pre-op platelet count: 142,000/μL (borderline). INR 1.1. Intraoperative bleeding episode at T+3:30.",
    pillarSource: "Scholar + Haemorrhage Sentinel",
  }},

  // ═══════════════════════════════════════════════════════════════════
  // T+270: Oracle — Shloka display
  // ═══════════════════════════════════════════════════════════════════
  { kind: "transcript", at: 270, speaker: "surgeon", text: "Beginning dissection of gallbladder from liver bed using hook diathermy." },
  { kind: "nael_state", at: 275, state: "speaking" },
  { kind: "transcript", at: 276, speaker: "nael", text: "Oracle reference available: Suśruta Saṃhitā on hepatic dissection technique. Say 'Nael, show shloka' to view." },
  { kind: "nael_state", at: 280, state: "idle" },

  // ═══════════════════════════════════════════════════════════════════
  // T+300: Closure — instrument count confirmation
  // ═══════════════════════════════════════════════════════════════════
  { kind: "phase", at: 300, phase: "closure" },
  { kind: "transcript", at: 302, speaker: "surgeon", text: "Gallbladder fully detached. Placing in retrieval bag. Specimen out." },
  { kind: "transcript", at: 310, speaker: "surgeon", text: "Inspecting operative field. Haemostasis good. Releasing pneumoperitoneum." },

  { kind: "instrument_count", at: 315, data: { deployed: 14, accounted: 14, matched: true } },
  { kind: "nael_state", at: 316, state: "speaking" },
  { kind: "transcript", at: 317, speaker: "nael", text: "Instrument count: 14 of 14 instruments, 6 of 6 swabs accounted. Field is clear. Safe to close." },
  { kind: "nael_state", at: 322, state: "idle" },

  { kind: "transcript", at: 325, speaker: "surgeon", text: "Closing fascia at 10mm port. Skin closure with subcuticular." },

  // ═══════════════════════════════════════════════════════════════════
  // T+340: Chronicler — session summary
  // ═══════════════════════════════════════════════════════════════════
  { kind: "nael_state", at: 340, state: "speaking" },
  { kind: "transcript", at: 342, speaker: "nael", text: "Chronicler: Session summary generating. Total operative time 5 minutes 40 seconds. One haemorrhage alert — resolved. Oracle consulted once. AI compute cost: ₹740." },
  { kind: "nael_state", at: 350, state: "idle" },

  { kind: "transcript", at: 355, speaker: "system", text: "Session complete. Post-operative review available." },
];

/** Total scripted duration (seconds). */
export const DEMO_DURATION = 360;

/** Timeline events for the SurgeryTimeline component. */
export const DEMO_TIMELINE_EVENTS: TimelineEvent[] = [
  { at: 2, pillar: "nael", label: "Session start" },
  { at: 35, pillar: "sentinel", label: "Instrument count" },
  { at: 65, pillar: "nael", label: "Overlays available" },
  { at: 85, pillar: "nael", label: "CVS check" },
  { at: 92, pillar: "monitor", label: "HR trending up" },
  { at: 120, pillar: "oracle", label: "Marma proximity" },
  { at: 150, pillar: "pharmacist", label: "Fentanyl logged" },
  { at: 180, pillar: "sentinel", label: "Retraction timer" },
  { at: 210, pillar: "haemorrhage", label: "HAEMORRHAGE ALERT" },
  { at: 248, pillar: "advocate", label: "Devil's Advocate" },
  { at: 315, pillar: "sentinel", label: "Count confirmed" },
  { at: 342, pillar: "chronicler", label: "Summary" },
];
