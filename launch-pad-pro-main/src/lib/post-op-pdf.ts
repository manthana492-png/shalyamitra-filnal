/**
 * Post-op PDF export — generates a clinical session summary PDF.
 *
 * Includes: session metadata, vitals snapshot summary, alerts, full transcript,
 * and the mandatory CDS disclaimer footer on every page.
 */

import { jsPDF } from "jspdf";
import { CDS_DISCLAIMER_FULL } from "@/lib/cds";

export type PostOpInput = {
  procedure: string;
  patientCode: string;
  theatre: string | null;
  surgeon: string | null;
  anaesthetist: string | null;
  startedAt: string | null;
  endedAt: string | null;
  notes: string | null;
  transcripts: { speaker: string; text: string; spoken_at: string }[];
  alerts: { severity: string; title: string; body: string; source: string | null; created_at: string; acknowledged: boolean }[];
};

const MARGIN = 48;
const LINE = 14;

export function generatePostOpPdf(input: PostOpInput): Blob {
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();

  let y = MARGIN;
  let pageNo = 1;

  const dur = input.startedAt && input.endedAt
    ? Math.round((new Date(input.endedAt).getTime() - new Date(input.startedAt).getTime()) / 1000)
    : null;

  const ensureSpace = (need: number) => {
    if (y + need > pageH - MARGIN - 40) {
      drawFooter();
      doc.addPage();
      pageNo += 1;
      y = MARGIN;
      drawHeader();
    }
  };

  const drawHeader = () => {
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.setTextColor(20, 130, 160);
    doc.text("ARIA · Surgical Copilot", MARGIN, MARGIN - 18);
    doc.setTextColor(120);
    doc.setFont("helvetica", "normal");
    doc.text("Post-operative session report", pageW - MARGIN, MARGIN - 18, { align: "right" });
    doc.setDrawColor(20, 130, 160);
    doc.setLineWidth(0.5);
    doc.line(MARGIN, MARGIN - 12, pageW - MARGIN, MARGIN - 12);
    y = MARGIN;
  };

  const drawFooter = () => {
    const fy = pageH - MARGIN + 10;
    doc.setDrawColor(220);
    doc.line(MARGIN, fy - 26, pageW - MARGIN, fy - 26);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(7.5);
    doc.setTextColor(110);
    const wrap = doc.splitTextToSize(CDS_DISCLAIMER_FULL, pageW - MARGIN * 2);
    doc.text(wrap, MARGIN, fy - 18);
    doc.setFontSize(8);
    doc.setTextColor(140);
    doc.text(`Page ${pageNo}`, pageW - MARGIN, fy + 4, { align: "right" });
    doc.text(`Generated ${new Date().toLocaleString()}`, MARGIN, fy + 4);
  };

  drawHeader();

  // Title
  doc.setFont("helvetica", "bold");
  doc.setFontSize(20);
  doc.setTextColor(15);
  doc.text(input.procedure, MARGIN, y + 6);
  y += 26;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(80);
  doc.text(`Patient code: ${input.patientCode}`, MARGIN, y); y += LINE;
  doc.text(`Theatre: ${input.theatre ?? "—"}`, MARGIN, y); y += LINE;
  doc.text(`Surgeon: ${input.surgeon ?? "—"}    ·    Anaesthetist: ${input.anaesthetist ?? "—"}`, MARGIN, y); y += LINE;
  doc.text(`Started: ${input.startedAt ? new Date(input.startedAt).toLocaleString() : "—"}`, MARGIN, y); y += LINE;
  doc.text(`Ended:   ${input.endedAt ? new Date(input.endedAt).toLocaleString() : "—"}`, MARGIN, y); y += LINE;
  if (dur !== null) {
    doc.text(`Duration: ${Math.floor(dur / 60)}m ${dur % 60}s`, MARGIN, y); y += LINE;
  }
  y += 8;

  // Summary box
  ensureSpace(48);
  doc.setDrawColor(20, 130, 160);
  doc.setFillColor(240, 250, 252);
  doc.roundedRect(MARGIN, y, pageW - MARGIN * 2, 40, 4, 4, "FD");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(20, 90, 110);
  doc.text("SUMMARY", MARGIN + 10, y + 14);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(40);
  doc.text(`${input.transcripts.length} transcript lines · ${input.alerts.length} alerts surfaced`, MARGIN + 10, y + 30);
  y += 56;

  // Alerts
  if (input.alerts.length > 0) {
    ensureSpace(LINE * 2);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.setTextColor(15);
    doc.text("Alerts", MARGIN, y); y += LINE + 4;

    for (const a of input.alerts) {
      ensureSpace(LINE * 4);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(10);
      doc.setTextColor(15);
      doc.text(a.title, MARGIN, y);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(8.5);
      doc.setTextColor(120);
      doc.text(`${a.severity.toUpperCase()} · ${a.source ?? "—"} · ${new Date(a.created_at).toLocaleTimeString()} · ${a.acknowledged ? "ack" : "not ack"}`, pageW - MARGIN, y, { align: "right" });
      y += LINE;
      const wrap = doc.splitTextToSize(a.body, pageW - MARGIN * 2);
      doc.setTextColor(60);
      doc.setFontSize(9.5);
      doc.text(wrap, MARGIN, y);
      y += LINE * wrap.length + 6;
    }
    y += 6;
  }

  // Transcript
  if (input.transcripts.length > 0) {
    ensureSpace(LINE * 2);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.setTextColor(15);
    doc.text("Transcript", MARGIN, y); y += LINE + 4;

    for (const t of input.transcripts) {
      ensureSpace(LINE * 2);
      const time = new Date(t.spoken_at).toLocaleTimeString();
      doc.setFont("helvetica", "bold");
      doc.setFontSize(8.5);
      doc.setTextColor(20, 130, 160);
      doc.text(`${t.speaker.toUpperCase().padEnd(12, " ")}`, MARGIN, y);
      doc.setTextColor(140);
      doc.setFont("helvetica", "normal");
      doc.text(time, MARGIN + 90, y);
      y += LINE - 2;
      doc.setTextColor(40);
      doc.setFontSize(10);
      const wrap = doc.splitTextToSize(t.text, pageW - MARGIN * 2);
      doc.text(wrap, MARGIN, y);
      y += LINE * wrap.length + 4;
    }
  }

  // Notes
  if (input.notes) {
    y += 10;
    ensureSpace(LINE * 4);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.setTextColor(15);
    doc.text("Notes", MARGIN, y); y += LINE + 4;
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(40);
    const wrap = doc.splitTextToSize(input.notes, pageW - MARGIN * 2);
    doc.text(wrap, MARGIN, y);
    y += LINE * wrap.length;
  }

  drawFooter();

  return doc.output("blob");
}
