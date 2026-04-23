/**
 * OperatorOverride — hidden Cmd/Ctrl+K drawer for live demo control.
 *
 * Lets the operator (presenter) inject scripted utterances and alerts on top
 * of the running session, force layout/focus directives, and switch the GPU
 * source preset — without touching the keyboard mouse during a stage demo.
 *
 * NOT visible by default. Surfaces only when the user presses ⌘K / Ctrl+K.
 * Audited: every override is logged to the audit_log table.
 */

import { useEffect, useState } from "react";
import {
  Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle,
} from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useDirector, type LayoutPreset, type CameraId } from "@/lib/director";
import { logAudit } from "@/lib/audit";
import {
  Keyboard, MessageSquare, AlertTriangle, Layout as LayoutIcon, Cpu, Eye,
} from "lucide-react";
import type { TranscriptLine } from "@/components/console/TranscriptStream";
import type { AlertItem } from "@/components/console/AlertsPanel";
import type { RealtimeSource } from "@/lib/realtime-stream";
import { DEMO_PHI_LINES } from "@/lib/phi-redact";

type Speaker = TranscriptLine["speaker"];
type Severity = AlertItem["severity"];

export type OperatorOverrideProps = {
  sessionId?: string;
  elapsed: number;
  source: RealtimeSource;
  onSourceChange: (s: RealtimeSource) => void;
  onInjectTranscript: (line: { speaker: Speaker; text: string; at: number }) => void;
  onInjectAlert: (alert: { severity: Severity; title: string; body: string; source: string; at: number }) => void;
};

export function OperatorOverride(props: OperatorOverrideProps) {
  const [open, setOpen] = useState(false);
  const director = useDirector();

  // Cmd/Ctrl + K → toggle
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetContent side="right" className="w-full sm:max-w-lg overflow-y-auto bg-surface-1/95 backdrop-blur-md border-l border-primary/30">
        <SheetHeader>
          <div className="flex items-center gap-2">
            <Keyboard className="h-4 w-4 text-primary" />
            <SheetTitle className="text-glow">Operator Override</SheetTitle>
            <Badge variant="outline" className="ml-auto text-[9px] uppercase tracking-wider border-primary/40 text-primary/80">
              ⌘K
            </Badge>
          </div>
          <SheetDescription>
            Inject scripted events into the live session. Every override is audit-logged.
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          <SourceBlock source={props.source} onChange={props.onSourceChange} sessionId={props.sessionId} />
          <LayoutBlock />
          <TranscriptInjector
            elapsed={props.elapsed}
            sessionId={props.sessionId}
            onInject={props.onInjectTranscript}
          />
          <AlertInjector
            elapsed={props.elapsed}
            sessionId={props.sessionId}
            onInject={props.onInjectAlert}
          />
        </div>
      </SheetContent>
    </Sheet>
  );
}

function Section({ icon: Icon, title, children }: { icon: typeof Eye; title: string; children: React.ReactNode }) {
  return (
    <div className="hud-frame hud-corners relative p-4 space-y-3">
      <span className="corner-tr" /><span className="corner-bl" />
      <div className="text-hud-label flex items-center gap-2"><Icon className="h-3 w-3" /> {title}</div>
      {children}
    </div>
  );
}

function SourceBlock({ source, onChange, sessionId }: { source: RealtimeSource; onChange: (s: RealtimeSource) => void; sessionId?: string }) {
  return (
    <Section icon={Cpu} title="REALTIME SOURCE">
      <Select value={source} onValueChange={(v) => {
        onChange(v as RealtimeSource);
        logAudit({ action: "operator.source_change", sessionId, details: { to: v } });
      }}>
        <SelectTrigger><SelectValue /></SelectTrigger>
        <SelectContent>
          <SelectItem value="scripted">Scripted (local playback)</SelectItem>
          <SelectItem value="mock">Mock GPU (edge function, no GPU needed)</SelectItem>
          <SelectItem value="live">Live (aria-realtime → GPU backend)</SelectItem>
        </SelectContent>
      </Select>
      <p className="text-[11px] text-muted-foreground">
        Live falls back to scripted automatically if GPU_BACKEND_URL is not configured.
      </p>
    </Section>
  );
}

function LayoutBlock() {
  const director = useDirector();
  const layouts: LayoutPreset[] = ["grid", "focus", "cinema"];
  const cams: CameraId[] = ["cam1", "cam2", "cam3"];

  return (
    <Section icon={LayoutIcon} title="LAYOUT DIRECTIVES">
      <div className="space-y-2">
        <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">Layout</Label>
        <div className="flex gap-2">
          {layouts.map((l) => (
            <Button
              key={l}
              variant={director.layout === l ? "default" : "outline"}
              size="sm"
              onClick={() => director.setLayout(l)}
              className="flex-1 capitalize text-xs"
            >
              {l}
            </Button>
          ))}
        </div>
      </div>
      <div className="space-y-2">
        <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">Focus camera</Label>
        <div className="flex gap-2">
          {cams.map((c) => (
            <Button
              key={c}
              variant={director.focusedCamera === c ? "default" : "outline"}
              size="sm"
              onClick={() => director.setFocus(c)}
              className="flex-1 uppercase text-xs"
            >
              {c}
            </Button>
          ))}
        </div>
      </div>
      <Button
        variant={director.layoutLocked ? "default" : "outline"}
        size="sm"
        className="w-full"
        onClick={() => director.setLayoutLocked(!director.layoutLocked)}
      >
        {director.layoutLocked ? "Layout LOCKED" : "Lock layout"}
      </Button>
    </Section>
  );
}

function TranscriptInjector({ elapsed, sessionId, onInject }: {
  elapsed: number; sessionId?: string;
  onInject: (l: { speaker: Speaker; text: string; at: number }) => void;
}) {
  const [speaker, setSpeaker] = useState<Speaker>("surgeon");
  const [text, setText] = useState("");

  const submit = (overrideText?: string) => {
    const t = (overrideText ?? text).trim();
    if (!t) return;
    onInject({ speaker, text: t, at: Math.floor(elapsed) });
    logAudit({ action: "operator.transcript_inject", sessionId, details: { speaker, text: t, at: elapsed } });
    setText("");
  };

  return (
    <Section icon={MessageSquare} title="INJECT TRANSCRIPT">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">Speaker</Label>
          <Select value={speaker} onValueChange={(v) => setSpeaker(v as Speaker)}>
            <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="surgeon">Surgeon</SelectItem>
              <SelectItem value="anaesthetist">Anaesthetist</SelectItem>
              <SelectItem value="nurse">Nurse</SelectItem>
              <SelectItem value="aria">ARIA</SelectItem>
              <SelectItem value="system">System</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">At T+</Label>
          <Input className="mt-1 text-mono" value={`${Math.floor(elapsed)}s`} disabled />
        </div>
      </div>
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type an utterance to inject…"
        rows={3}
      />
      <Button size="sm" className="w-full" onClick={() => submit()} disabled={!text.trim()}>
        Inject line
      </Button>
      <div className="space-y-1.5">
        <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">PHI test lines (Morpheus demo)</Label>
        {DEMO_PHI_LINES.map((line, i) => (
          <Button
            key={i}
            variant="outline"
            size="sm"
            className="w-full justify-start text-left text-[11px] h-auto py-1.5 whitespace-normal"
            onClick={() => submit(line)}
          >
            {line.length > 80 ? line.slice(0, 80) + "…" : line}
          </Button>
        ))}
      </div>
    </Section>
  );
}

function AlertInjector({ elapsed, sessionId, onInject }: {
  elapsed: number; sessionId?: string;
  onInject: (a: { severity: Severity; title: string; body: string; source: string; at: number }) => void;
}) {
  const [severity, setSeverity] = useState<Severity>("warning");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [src, setSrc] = useState("operator");

  const submit = () => {
    if (!title.trim() || !body.trim()) return;
    onInject({ severity, title, body, source: src, at: Math.floor(elapsed) });
    logAudit({ action: "operator.alert_inject", sessionId, details: { severity, title, source: src } });
    setTitle(""); setBody("");
  };

  const presets = [
    { sev: "critical" as Severity, t: "Suspected major bleed", b: "Vision module detected sustained haemorrhage. Recommend immediate haemostasis." },
    { sev: "warning"  as Severity, t: "SpO₂ dropping — 91%", b: "SpO₂ has fallen 6 points in 60s. Review ventilation and circuit." },
    { sev: "caution"  as Severity, t: "Diathermy near vital structure", b: "Active electrode close to common bile duct on cam-1." },
  ];

  return (
    <Section icon={AlertTriangle} title="INJECT ALERT">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">Severity</Label>
          <Select value={severity} onValueChange={(v) => setSeverity(v as Severity)}>
            <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="info">Info</SelectItem>
              <SelectItem value="caution">Caution</SelectItem>
              <SelectItem value="warning">Warning</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">Source</Label>
          <Input className="mt-1" value={src} onChange={(e) => setSrc(e.target.value)} />
        </div>
      </div>
      <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Alert title…" />
      <Textarea value={body} onChange={(e) => setBody(e.target.value)} placeholder="Body / rationale…" rows={2} />
      <Button size="sm" className="w-full" onClick={submit} disabled={!title.trim() || !body.trim()}>
        Inject alert
      </Button>
      <div className="space-y-1.5">
        <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">Quick presets</Label>
        {presets.map((p, i) => (
          <Button
            key={i}
            variant="outline"
            size="sm"
            className="w-full justify-start text-left text-[11px] h-auto py-1.5"
            onClick={() => {
              onInject({ severity: p.sev, title: p.t, body: p.b, source: "operator", at: Math.floor(elapsed) });
              logAudit({ action: "operator.alert_inject", sessionId, details: { preset: p.t, severity: p.sev } });
            }}
          >
            <span className="text-mono uppercase mr-2 text-[9px] text-primary">{p.sev}</span>
            {p.t}
          </Button>
        ))}
      </div>
    </Section>
  );
}
