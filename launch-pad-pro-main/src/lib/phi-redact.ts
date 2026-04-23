/**
 * Morpheus-shape PHI redaction (client-side simulator).
 *
 * In production, the NVIDIA Morpheus PHI pipeline running on the GPU backend
 * tokenises each transcript line and returns `piiSpans: [start, end][]` so the
 * UI can render `[REDACTED]` chips without ever rendering the raw PHI.
 *
 * This module shapes the same contract for the demo:
 *   redactPhi("Patient John Smith, DOB 12/03/1971, MRN 4471293")
 *     → { text: "Patient [REDACTED], DOB [REDACTED], MRN [REDACTED]",
 *         spans: [[8,18],[24,34],[40,47]],
 *         categories: ["NAME","DOB","MRN"] }
 *
 * Patterns are conservative — designed to look right in a 5-minute clinical
 * demo, NOT to be the source of truth in production. Real Morpheus models on
 * the GPU backend handle name disambiguation, address recognition, multi-lang.
 */

export type PhiCategory = "NAME" | "DOB" | "MRN" | "PHONE" | "EMAIL" | "ADDRESS";

export type RedactionResult = {
  text: string;
  spans: Array<[number, number]>; // start/end offsets in the *redacted* text
  categories: PhiCategory[];
  redacted: boolean;
};

type Pattern = { re: RegExp; cat: PhiCategory };

const PATTERNS: Pattern[] = [
  // Honorific + capitalised name(s): "Mr. John Smith", "Dr Jane Doe-Smith"
  { re: /\b(?:Mr|Mrs|Ms|Dr|Prof|Sir|Dame)\.?\s+[A-Z][a-zA-Z'-]+(?:\s+[A-Z][a-zA-Z'-]+)?/g, cat: "NAME" },
  // Bare two-capitalised-word names following "patient", "name", etc.
  { re: /\b(?:patient|name(?:d)?|surgeon|anaesthetist)\s+(?:is\s+)?[A-Z][a-z]+\s+[A-Z][a-z]+\b/g, cat: "NAME" },
  // DOB / dates of birth
  { re: /\bDOB[:\s]+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b/g, cat: "DOB" },
  { re: /\b(?:born|d\.o\.b\.?|date of birth)[:\s]+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b/gi, cat: "DOB" },
  // MRN / patient ID
  { re: /\bMRN[:\s#]*\d{4,}\b/g, cat: "MRN" },
  { re: /\b(?:patient (?:id|number)|hospital number)[:\s#]*\d{4,}\b/gi, cat: "MRN" },
  // Email
  { re: /\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b/g, cat: "EMAIL" },
  // Phone (UK / IN / US-ish)
  { re: /\b(?:\+?\d{1,3}[\s-]?)?\(?\d{3,5}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}\b/g, cat: "PHONE" },
];

const MASK = "[REDACTED]";

export function redactPhi(input: string): RedactionResult {
  const matches: Array<{ start: number; end: number; cat: PhiCategory }> = [];

  for (const { re, cat } of PATTERNS) {
    re.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(input)) !== null) {
      matches.push({ start: m.index, end: m.index + m[0].length, cat });
    }
  }

  if (matches.length === 0) {
    return { text: input, spans: [], categories: [], redacted: false };
  }

  // Sort by start, drop overlaps (keep earliest)
  matches.sort((a, b) => a.start - b.start);
  const merged: typeof matches = [];
  for (const m of matches) {
    const last = merged[merged.length - 1];
    if (!last || m.start >= last.end) merged.push(m);
  }

  let out = "";
  let cursor = 0;
  const spans: Array<[number, number]> = [];
  const categories: PhiCategory[] = [];

  for (const m of merged) {
    out += input.slice(cursor, m.start);
    const start = out.length;
    out += MASK;
    spans.push([start, out.length]);
    categories.push(m.cat);
    cursor = m.end;
  }
  out += input.slice(cursor);

  return { text: out, spans, categories, redacted: true };
}

/** Used by the operator override drawer + scripted demo to seed PHI lines. */
export const DEMO_PHI_LINES = [
  "Confirming patient Mr. John Smith, DOB 12/03/1971, MRN 4471293, for laparoscopic cholecystectomy.",
  "Next of kin contact: Sarah Smith on +44 7700 900123.",
  "Anaesthetist Dr. Priya Patel signing in.",
];
