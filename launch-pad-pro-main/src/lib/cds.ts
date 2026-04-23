/**
 * CDS (Clinical Decision Support) wrapper.
 *
 * Per ShalyaMitra Production Spec, every Nael-authored output must be wrapped
 * with a non-diagnostic, non-prescriptive disclaimer. This is what keeps the
 * system classified as a CDS tool (Class A/B SaMD) rather than a diagnostic
 * device (Class C) under CDSCO regulations.
 *
 * Use `wrapCds()` whenever displaying or speaking Nael output to the user.
 */

export const CDS_DISCLAIMER_SHORT =
  "Decision support — not a diagnosis. Final clinical judgement rests with the operating team.";

export const CDS_DISCLAIMER_FULL =
  "ShalyaMitra is a Clinical Decision Support tool. It does not provide diagnoses or treatment. All information is for the surgical team's reference only. Final clinical judgement rests with the operating team.";

export function wrapCds(text: string): { body: string; disclaimer: string } {
  return { body: text, disclaimer: CDS_DISCLAIMER_SHORT };
}

/** Strip identifiable patient names from a string (best-effort client-side hint).
 * Real PHI redaction happens server-side via Morpheus in production.
 */
export function lightRedact(text: string): string {
  // Replace anything that looks like "Mr./Mrs./Dr. <Capitalized Word>"
  return text.replace(/\b(Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+\b/g, "[REDACTED]");
}
