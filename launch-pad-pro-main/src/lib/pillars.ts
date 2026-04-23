/**
 * ShalyaMitra Intelligence Pillars
 *
 * Each of the eight intelligences (plus Nael, the orchestrator) has a unique
 * colour, icon, and identity. This module centralises pillar metadata so
 * every component renders consistent visual identity.
 *
 * The pillar colour is the single most important pre-attentive cue:
 * the surgeon's peripheral vision registers AMBER = physiological alert,
 * RED = bleeding, SAFFRON = Oracle, before conscious reading.
 */

import {
  Brain,
  Droplets,
  MonitorCheck,
  Eye,
  Pill,
  BookOpen,
  ScrollText,
  Scale,
  FileText,
  type LucideIcon,
} from "lucide-react";

export type PillarId =
  | "nael"
  | "haemorrhage"
  | "monitor"
  | "sentinel"
  | "pharmacist"
  | "scholar"
  | "oracle"
  | "advocate"
  | "chronicler";

export type PillarInfo = {
  id: PillarId;
  name: string;
  shortName: string;
  cssVar: string;          // e.g. "--pillar-nael"
  shadowVar: string;       // e.g. "--shadow-glow" (or pillar-specific)
  icon: LucideIcon;
  description: string;
};

export const PILLARS: Record<PillarId, PillarInfo> = {
  nael: {
    id: "nael",
    name: "Nael — The Voice",
    shortName: "Nael",
    cssVar: "--pillar-nael",
    shadowVar: "--shadow-glow",
    icon: Brain,
    description: "Conversational surgical companion",
  },
  haemorrhage: {
    id: "haemorrhage",
    name: "Haemorrhage Sentinel",
    shortName: "Haemorrhage",
    cssVar: "--pillar-haemorrhage",
    shadowVar: "--shadow-haemorrhage",
    icon: Droplets,
    description: "Real-time bleed detection (<500ms)",
  },
  monitor: {
    id: "monitor",
    name: "Monitor Sentinel",
    shortName: "Monitor",
    cssVar: "--pillar-monitor",
    shadowVar: "--shadow-monitor",
    icon: MonitorCheck,
    description: "Predictive vital sign analysis",
  },
  sentinel: {
    id: "sentinel",
    name: "The Sentinel",
    shortName: "Sentinel",
    cssVar: "--pillar-sentinel",
    shadowVar: "--shadow-glow",
    icon: Eye,
    description: "Overhead instrument & swab tracking",
  },
  pharmacist: {
    id: "pharmacist",
    name: "The Pharmacist",
    shortName: "Pharmacist",
    cssVar: "--pillar-pharmacist",
    shadowVar: "--shadow-pharmacist",
    icon: Pill,
    description: "Pharmacokinetic modelling & drug interactions",
  },
  scholar: {
    id: "scholar",
    name: "The Scholar",
    shortName: "Scholar",
    cssVar: "--pillar-scholar",
    shadowVar: "--shadow-glow",
    icon: BookOpen,
    description: "Pre-operative intelligence & risk synthesis",
  },
  oracle: {
    id: "oracle",
    name: "The Oracle",
    shortName: "Oracle",
    cssVar: "--pillar-oracle",
    shadowVar: "--shadow-oracle",
    icon: ScrollText,
    description: "Marma mapping & Sushruta Samhita wisdom",
  },
  advocate: {
    id: "advocate",
    name: "Devil's Advocate",
    shortName: "Advocate",
    cssVar: "--pillar-advocate",
    shadowVar: "--shadow-advocate",
    icon: Scale,
    description: "Cross-intelligence conflict detection",
  },
  chronicler: {
    id: "chronicler",
    name: "The Chronicler",
    shortName: "Chronicler",
    cssVar: "--pillar-chronicler",
    shadowVar: "--shadow-glow",
    icon: FileText,
    description: "Intraoperative documentation & handover",
  },
};

/** Get the CSS custom property value string for a pillar's colour. */
export function getPillarColor(pillar: PillarId): string {
  return `hsl(var(${PILLARS[pillar].cssVar}))`;
}

/** Get Tailwind class for pillar text colour. */
export function getPillarTextClass(pillar: PillarId): string {
  return `text-pillar-${pillar}`;
}

/** Get Tailwind class for pillar border colour. */
export function getPillarBorderClass(pillar: PillarId): string {
  return `border-pillar-${pillar}`;
}

/**
 * Alert priority — lower number = higher priority.
 * Priority 1 alerts interrupt everything immediately.
 */
export const ALERT_PRIORITY: Record<string, number> = {
  haemorrhage: 1,
  instrument_discrepancy: 2,
  monitor_critical: 3,
  monitor_warning: 4,
  retraction: 5,
  advocate: 6,
  conversation: 7,
  background: 8,
};

/** ShalyaMitra alert type with pillar attribution. */
export type ShalyaAlert = {
  id: string;
  pillar: PillarId;
  severity: "info" | "caution" | "warning" | "critical";
  title: string;
  body: string;
  source: string;
  at: number;            // seconds from session start
  acknowledged: boolean;
  priority: number;
};
