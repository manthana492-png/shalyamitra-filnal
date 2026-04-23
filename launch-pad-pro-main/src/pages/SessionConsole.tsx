import { useEffect, useMemo, useState, useCallback, useRef } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { type StreamMode } from "@/lib/nael-stream";
import { useRealtimeStream, type RealtimeSource } from "@/lib/realtime-stream";
import { useVoiceControl } from "@/hooks/useVoiceControl";
import { useDirector } from "@/lib/director";
import { logAudit } from "@/lib/audit";
import { NaelLogo } from "@/components/NaelLogo";
import { NaelCore } from "@/components/console/NaelCore";
import { NaelHud } from "@/components/console/NaelHud";
import { ModeSwitcher } from "@/components/console/ModeSwitcher";
import { TranscriptStream, type TranscriptLine } from "@/components/console/TranscriptStream";
import { AlertsPanel } from "@/components/console/AlertsPanel";
import { VitalsBar, type Vitals } from "@/components/console/VitalsBar";
import { VitalAlertPanel } from "@/components/console/VitalAlertPanel";
import { CameraGrid } from "@/components/console/CameraGrid";
import { OverlayCanvas } from "@/components/console/OverlayCanvas";
import { KnowledgePanel } from "@/components/console/KnowledgePanel";
import { InstrumentCount } from "@/components/console/InstrumentCount";
import { RetractionTimer } from "@/components/console/RetractionTimer";
import { PKDashboard } from "@/components/console/PKDashboard";
import { DevilsAdvocate, type AdvocateEvent } from "@/components/console/DevilsAdvocate";
import { SurgeryTimeline } from "@/components/console/SurgeryTimeline";
import { VoiceCommandOverlay } from "@/components/console/VoiceCommandOverlay";
import { SessionSummary } from "@/components/console/SessionSummary";
import { OperatorOverride } from "@/components/console/OperatorOverride";
import { DEMO_TIMELINE_EVENTS, DEMO_DURATION } from "@/lib/demo-session";
import { type ShalyaAlert, ALERT_PRIORITY } from "@/lib/pillars";
import { playAlertTone } from "@/hooks/useAlertAudio";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Play, Pause, Square, LogOut, Volume2, VolumeX, Loader2, ShieldCheck, Circle } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { CDS_DISCLAIMER_SHORT } from "@/lib/cds";

type SessionRow = {
  id: string;
  procedure_name: string;
  patient_code: string;
  status: string;
  current_mode: string;
  started_at: string | null;
  ended_at: string | null;
  surgeon_name: string | null;
  theatre: string | null;
};

function fmt(t: number) {
  const h = Math.floor(t / 3600).toString().padStart(2, "0");
  const m = Math.floor((t % 3600) / 60).toString().padStart(2, "0");
  const s = Math.floor(t % 60).toString().padStart(2, "0");
  return `${h}:${m}:${s}`;
}

const SessionConsole = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<SessionRow | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [mode, setMode] = useState<StreamMode>("reactive");
  const [realtimeSource, setRealtimeSource] = useState<RealtimeSource>("live");
  const [lines, setLines] = useState<TranscriptLine[]>([]);
  const [vitals, setVitals] = useState<Vitals>({ hr: 72, spo2: 98, map: 82, etco2: 36, temp: 36.4, rr: 14 });
  const [hist, setHist] = useState<{ hr: number[]; spo2: number[]; map: number[]; etco2: number[]; temp: number[]; rr: number[] }>({
    hr: [], spo2: [], map: [], etco2: [], temp: [], rr: [],
  });
  const [advocateEvent, setAdvocateEvent] = useState<AdvocateEvent | null>(null);
  const [micActive, setMicActive] = useState(false);
  const [sessionEnded, setSessionEnded] = useState(false);
  const [haemorrhageBurst, setHaemorrhageBurst] = useState(false);
  const [oracleQueryCount, setOracleQueryCount] = useState(0);

  const director = useDirector();
  const endRef = useRef<() => void>(() => {});

  // Voice control
  const voiceCtl = useVoiceControl({
    onMute: () => setMicActive(false),
    onUnmute: () => setMicActive(true),
    onAckLatest: () => director.ackLatestAlert(),
    onEnd: () => endRef.current(),
    onModeChange: (m) => handleModeChange(m),
    onIntent: (i) => {
      if (i.kind !== "unknown") logAudit({ action: "voice.intent", sessionId: id, details: { intent: i } });
    },
  });

  // Load session
  useEffect(() => {
    if (!id) return;
    (async () => {
      const { data, error } = await supabase
        .from("sessions")
        .select("id, procedure_name, patient_code, status, current_mode, started_at, ended_at, surgeon_name, theatre")
        .eq("id", id).maybeSingle();
      if (error || !data) {
        toast({ title: "Session not found", variant: "destructive" });
        navigate("/sessions", { replace: true });
        return;
      }
      setSession(data as SessionRow);
      setMode((data.current_mode as StreamMode) ?? "reactive");
      setLoading(false);
    })();
  }, [id, navigate]);

  // Cleanup on unmount
  useEffect(() => () => { voiceCtl.stop(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Stream handlers — wire demo events to Director store
  const handlers = useMemo(() => ({
    onTranscript: (e: { speaker: TranscriptLine["speaker"]; text: string; at: number }) => {
      setLines((prev) => [...prev, { id: `${e.at}-${prev.length}`, ...e }]);
    },
    onAlert: (e: { severity: string; pillar: string; title: string; body: string; source: string; at: number; priority: number }) => {
      const alert: ShalyaAlert = {
        id: `${e.at}-${e.title}`,
        pillar: e.pillar as ShalyaAlert["pillar"],
        severity: e.severity as ShalyaAlert["severity"],
        title: e.title,
        body: e.body,
        source: e.source,
        at: e.at,
        acknowledged: false,
        priority: e.priority,
      };
      director.pushAlert(alert);
      // Audio alert (spec: every visual alert has audio)
      playAlertTone(e.severity as "critical" | "warning" | "caution" | "info");
      if (id) {
        supabase.from("alerts").insert({
          session_id: id, severity: e.severity, title: e.title, body: e.body, source: e.source,
        });
      }
      if (e.severity === "critical") {
        toast({ title: e.title, description: e.body, variant: "destructive" });
        // Haemorrhage burst: 3 rapid flashes then steady
        setHaemorrhageBurst(true);
        setTimeout(() => setHaemorrhageBurst(false), 1200);
      }
    },
    onVitals: (e: { hr: number; spo2: number; map: number; etco2: number; temp: number; rr: number }) => {
      setVitals({ hr: e.hr, spo2: e.spo2, map: e.map, etco2: e.etco2, temp: e.temp, rr: e.rr });
      setHist((p) => ({
        hr: [...p.hr, e.hr].slice(-60),
        spo2: [...p.spo2, e.spo2].slice(-60),
        map: [...p.map, e.map].slice(-60),
        etco2: [...p.etco2, e.etco2].slice(-60),
        temp: [...p.temp, e.temp].slice(-60),
        rr: [...p.rr, e.rr].slice(-60),
      }));
    },
    onPhase: (e: { phase: string }) => {
      director.setPhase(e.phase);
    },
    onOverlays: (e: { items: unknown[] }) => {
      director.setOverlayItems(e.items as any);
    },
    onKnowledge: (e: { pillar: string; content: unknown }) => {
      director.setKnowledgePanel(e.pillar as any, e.content);
      if (e.pillar === "oracle") setOracleQueryCount((c) => c + 1);
    },
    onInstrumentCount: (e: { data: { deployed: number; accounted: number; matched: boolean } }) => {
      director.setInstrumentCount(e.data);
    },
    onRetraction: (e: { timer: any }) => {
      director.addRetractionTimer(e.timer);
    },
    onAdvocate: (e: { event: AdvocateEvent }) => {
      setAdvocateEvent(e.event);
    },
    onNaelState: (e: { state: "idle" | "listening" | "thinking" | "speaking" }) => {
      director.setNaelState(e.state);
    },
    onTick: (t: number) => {
      director.setSurgeryTimer(Math.floor(t));
    },
    onComplete: () => {
      setRunning(false);
      toast({ title: "Demo session complete", description: "Move to post-op review when ready." });
    },
  }), [mode, id, director]);

  const { elapsed, total, status: streamStatus, resolvedSource } = useRealtimeStream({
    source: realtimeSource,
    running,
    mode,
    sessionId: id,
    handlers,
  });

  // Persist transcript lines
  const persistedCount = useMemo(() => ({ n: 0 }), []);
  useEffect(() => {
    if (!id) return;
    if (lines.length <= persistedCount.n) return;
    const newOnes = lines.slice(persistedCount.n);
    persistedCount.n = lines.length;
    supabase.from("transcripts").insert(
      newOnes.map((l) => ({ session_id: id, speaker: l.speaker, text: l.text }))
    ).then(() => {});
  }, [lines, id, persistedCount]);

  const handleStart = useCallback(async () => {
    if (!session) return;
    setRunning(true);
    if (!voiceCtl.active && voiceCtl.supported) voiceCtl.start();
    setMicActive(true);
    if (session.status === "scheduled") {
      await supabase.from("sessions").update({
        status: "in_progress",
        started_at: new Date().toISOString(),
      }).eq("id", session.id);
      setSession({ ...session, status: "in_progress", started_at: new Date().toISOString() });
      logAudit({ action: "session.start", sessionId: session.id });
    }
  }, [session, voiceCtl]);

  const handlePause = () => setRunning(false);

  const handleEnd = useCallback(async () => {
    if (!session) return;
    setRunning(false);
    voiceCtl.stop();
    await supabase.from("sessions").update({
      status: "completed",
      ended_at: new Date().toISOString(),
    }).eq("id", session.id);
    logAudit({ action: "session.end", sessionId: session.id, details: { lines: lines.length, alerts: director.alertQueue.length } });
    // Show session summary before navigating to PostOp
    setSessionEnded(true);
  }, [session, voiceCtl, lines.length, director.alertQueue.length]);

  const handleNavigatePostOp = useCallback(() => {
    if (!session) return;
    navigate(`/sessions/${session.id}/post-op`);
  }, [session, navigate]);
  endRef.current = handleEnd;

  const handleModeChange = async (m: StreamMode) => {
    setMode(m);
    if (session) {
      await supabase.from("sessions").update({ current_mode: m }).eq("id", session.id);
      logAudit({ action: "mode.change", sessionId: session.id, details: { to: m } });
    }
  };

  if (loading || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    );
  }

  // Show session summary screen after end
  if (sessionEnded && session) {
    return (
      <SessionSummary
        duration={elapsed}
        alertCount={director.alertQueue.length}
        oracleQueries={oracleQueryCount}
        procedureName={session.procedure_name}
        surgeonName={session.surgeon_name ?? undefined}
        onNavigatePostOp={handleNavigatePostOp}
        onKeepOpen={() => setSessionEnded(false)}
      />
    );
  }

  // Determine viewport alert class
  const viewportAlert = (() => {
    if (director.layoutState === "haemorrhage_alert") {
      return haemorrhageBurst ? "viewport-alert-red-burst" : "viewport-alert-red";
    }
    if (director.layoutState === "vital_alert") return "viewport-alert-amber";
    return "";
  })();

  const isKnowledgeOpen = director.layoutState === "knowledge_display";
  const isPK = director.layoutState === "pharmacokinetics";
  const isVitalAlert = director.layoutState === "vital_alert";

  return (
    <div className={`min-h-screen bg-background hud-scanline ${viewportAlert}`}>
      {/* Floating components */}
      <RetractionTimer />
      <DevilsAdvocate event={advocateEvent} onDismiss={() => setAdvocateEvent(null)} />
      <VoiceCommandOverlay />

      {/* ═══ HUD TOP BAR ═══ */}
      <header className="sticky top-0 relative border-b border-primary/20 bg-surface-1/50 backdrop-blur-md z-30">
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-primary/60 to-transparent" />
        <div className="flex items-center justify-between gap-4 px-4 md:px-6 py-2">
          <div className="flex items-center gap-4 min-w-0">
            {/* REC indicator — anti-burn-in to protect OLED */}
            {running && (
              <div className="flex items-center gap-1.5 anti-burn-in">
                <Circle className="h-2.5 w-2.5 fill-critical text-critical animate-hud-pulse" />
                <span className="text-[9px] font-mono text-critical/80 tracking-wider">REC</span>
              </div>
            )}
            <NaelLogo size="sm" showWordmark={false} />
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className={`pulse-dot ${running ? "live" : "nael"}`} />
                <h1 className="text-sm md:text-base font-semibold tracking-tight truncate text-glow">{session.procedure_name}</h1>
              </div>
              <div className="text-mono text-[10px] tracking-[0.2em] text-primary/70 mt-0.5 truncate uppercase anti-burn-in">
                {session.patient_code} · {session.theatre ?? "OR"} · T+{fmt(elapsed)} · PHASE {director.phase}
                {director.instrumentCount.deployed > 0 && (
                  <span className="ml-2">· <InstrumentCount /></span>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <NaelHud micActive={micActive} lastTranscript={voiceCtl.transcript} />
            <div className="hidden md:block w-64">
              <ModeSwitcher value={mode} onChange={handleModeChange} />
            </div>
            <Button
              size="sm" variant="ghost"
              onClick={() => setMicActive(!micActive)}
              title={micActive ? "Mute Nael" : "Unmute Nael"}
            >
              {micActive ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4 text-muted-foreground" />}
            </Button>
            {!running ? (
              <Button size="sm" onClick={handleStart}
                className="bg-gradient-primary text-primary-foreground hover:opacity-90 shadow-glow">
                <Play className="mr-1.5 h-4 w-4" /> {elapsed > 0 ? "Resume" : "Start"}
              </Button>
            ) : (
              <Button size="sm" variant="outline" onClick={handlePause} className="border-primary/40">
                <Pause className="mr-1.5 h-4 w-4" /> Pause
              </Button>
            )}
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button size="sm" variant="outline" className="border-critical/40 text-critical hover:bg-critical/10">
                  <Square className="mr-1.5 h-4 w-4" /> End
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>End this session?</AlertDialogTitle>
                  <AlertDialogDescription>
                    Session will be marked complete. You'll be taken to post-op review.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleEnd}>End session</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            <Button asChild size="sm" variant="ghost">
              <Link to="/dashboard"><LogOut className="h-4 w-4" /></Link>
            </Button>
          </div>
        </div>
        {/* CDS sub-strip */}
        <div className="px-4 md:px-6 py-1 text-mono text-[10px] tracking-[0.2em] text-muted-foreground uppercase border-t border-primary/10 flex items-center gap-3">
          <ShieldCheck className="h-3 w-3 text-primary/70" />
          <span className="truncate">{CDS_DISCLAIMER_SHORT}</span>
        </div>
      </header>

      {/* ═══ MAIN HUD AREA ═══ */}
      <div className="flex flex-col gap-3 p-3 md:p-4">
        {/* Instrument count closure banner */}
        {director.phase === "closure" && director.instrumentCount.deployed > 0 && (
          <InstrumentCount />
        )}

        {/* ── CAMERAS — Full Width ── */}
        {!isPK && (
          <section className="relative">
            <CameraGrid />
            <OverlayCanvas />
          </section>
        )}

        {/* PK Dashboard (replaces cameras in pharmacokinetics layout) */}
        {isPK && (
          <section className="hud-frame hud-corners relative overflow-hidden min-h-[400px]">
            <span className="corner-tr" />
            <span className="corner-bl" />
            <PKDashboard />
          </section>
        )}

        {/* Vital Alert Panel — expanded trend graph + prediction */}
        {isVitalAlert && (
          <VitalAlertPanel
            label="MAP"
            value={vitals.map}
            unit="mmHg"
            history={hist.map}
          />
        )}

        {/* ── TRANSCRIPT + NAEL CORE + ALERTS — Triple Column ── */}
        <div className={`grid gap-3 ${isKnowledgeOpen ? "grid-cols-1 lg:grid-cols-2" : "grid-cols-1 lg:grid-cols-3"}`}>
          {/* Transcript (left) */}
          <div className="hud-frame hud-corners relative min-h-[350px] flex flex-col">
            <span className="corner-tr" />
            <span className="corner-bl" />
            <div className="flex items-center justify-between border-b border-primary/20 px-4 py-2">
              <div className="text-hud-label">TRANSCRIPT</div>
              <Badge variant="outline" className="text-[9px] uppercase tracking-wider border-primary/30 text-primary/80">
                <span className={`pulse-dot ${running ? "live" : "nael"} mr-2`} />
                {running
                  ? resolvedSource === "live" || resolvedSource === "mock"
                    ? "LIVE NIM"
                    : "DEMO"
                  : "PAUSED"}
              </Badge>
            </div>
            <div className="flex-1 overflow-y-auto">
              <TranscriptStream lines={lines} />
            </div>
          </div>

          {/* Nael AI Core — Jarvis-style visualization (center) */}
          {!isKnowledgeOpen && (
            <NaelCore />
          )}

          {/* Knowledge Panel (replaces NaelCore when open) */}
          {isKnowledgeOpen && (
            <KnowledgePanel />
          )}

          {/* Alerts (right) */}
          <div className="hud-frame hud-corners relative flex flex-col min-h-[350px]">
            <span className="corner-tr" />
            <span className="corner-bl" />
            <div className="flex items-center justify-between border-b border-primary/20 px-3 py-2">
              <div className="text-hud-label">ALERTS</div>
              <Badge variant="outline" className="text-[9px] text-mono border-primary/30">
                {director.alertQueue.filter(a => !a.acknowledged).length} ACTIVE
              </Badge>
            </div>
            <div className="flex-1 overflow-y-auto">
              <AlertsPanel alerts={director.alertQueue} />
            </div>
          </div>
        </div>

        {/* ── VITALS BAR ── */}
        {!isVitalAlert && (
          <VitalsBar current={vitals} histories={hist} />
        )}

        {/* ── SURGERY TIMELINE ── */}
        <SurgeryTimeline events={DEMO_TIMELINE_EVENTS} duration={DEMO_DURATION} />
      </div>
    </div>
  );
};

export default SessionConsole;
