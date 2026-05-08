import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useScriptedSession, type StreamMode } from "@/lib/nael-stream";
import { DEMO_DURATION, type DemoAlertEvent, type DemoTranscriptEvent } from "@/lib/demo-session";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Pause, Play } from "lucide-react";

function fmt(t: number) {
  const m = Math.floor(t / 60).toString().padStart(2, "0");
  const s = Math.floor(t % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

const DemoConsole = () => {
  const [running, setRunning] = useState(false);
  const [mode, setMode] = useState<StreamMode>("reactive");
  const [transcripts, setTranscripts] = useState<DemoTranscriptEvent[]>([]);
  const [alerts, setAlerts] = useState<DemoAlertEvent[]>([]);
  const [vitals, setVitals] = useState({ hr: 72, spo2: 98, map: 82, etco2: 36, temp: 36.4, rr: 14 });

  const stream = useScriptedSession({
    running,
    mode,
    handlers: {
      onTranscript: (evt) => setTranscripts((prev) => [...prev, evt]),
      onAlert: (evt) => setAlerts((prev) => [...prev, evt]),
      onVitals: (evt) =>
        setVitals({
          hr: evt.hr,
          spo2: evt.spo2,
          map: evt.map,
          etco2: evt.etco2,
          temp: evt.temp,
          rr: evt.rr,
        }),
      onComplete: () => setRunning(false),
    },
  });

  const lastLines = useMemo(() => transcripts.slice(-12), [transcripts]);
  const lastAlerts = useMemo(() => alerts.slice(-8).reverse(), [alerts]);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="mx-auto max-w-6xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <Badge variant="outline">Demo Mode Only</Badge>
            <h1 className="text-2xl font-semibold">ShalyaMitra Demo Console</h1>
            <p className="text-sm text-muted-foreground">
              Scripted demo feed isolated from production runtime paths.
            </p>
          </div>
          <Button asChild variant="outline">
            <Link to="/">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Link>
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-md border p-4">
            <div className="text-xs uppercase text-muted-foreground">Timer</div>
            <div className="mt-1 font-mono text-2xl">{fmt(stream.elapsed)} / {fmt(DEMO_DURATION)}</div>
            <div className="mt-3 flex gap-2">
              {!running ? (
                <Button onClick={() => setRunning(true)}>
                  <Play className="mr-2 h-4 w-4" />
                  Start
                </Button>
              ) : (
                <Button variant="outline" onClick={() => setRunning(false)}>
                  <Pause className="mr-2 h-4 w-4" />
                  Pause
                </Button>
              )}
              <Button
                variant="ghost"
                onClick={() => {
                  setRunning(false);
                  setTranscripts([]);
                  setAlerts([]);
                  stream.reset();
                }}
              >
                Reset
              </Button>
            </div>
          </div>

          <div className="rounded-md border p-4">
            <div className="text-xs uppercase text-muted-foreground">Mode</div>
            <div className="mt-2 flex gap-2">
              {(["silent", "reactive", "proactive"] as const).map((m) => (
                <Button
                  key={m}
                  variant={mode === m ? "default" : "outline"}
                  size="sm"
                  onClick={() => setMode(m)}
                >
                  {m}
                </Button>
              ))}
            </div>
          </div>

          <div className="rounded-md border p-4">
            <div className="text-xs uppercase text-muted-foreground">Vitals</div>
            <div className="mt-2 grid grid-cols-3 gap-2 text-sm">
              <div>HR {vitals.hr}</div>
              <div>SpO2 {vitals.spo2}</div>
              <div>MAP {vitals.map}</div>
              <div>EtCO2 {vitals.etco2}</div>
              <div>Temp {vitals.temp}</div>
              <div>RR {vitals.rr}</div>
            </div>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <section className="rounded-md border p-4">
            <h2 className="text-sm font-semibold">Transcripts</h2>
            <div className="mt-3 space-y-2 text-sm">
              {lastLines.map((line, idx) => (
                <div key={`${line.at}-${idx}`} className="rounded bg-muted/40 p-2">
                  <span className="font-mono text-xs text-muted-foreground">T+{fmt(line.at)} </span>
                  <span className="font-semibold">{line.speaker}: </span>
                  <span>{line.text}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-md border p-4">
            <h2 className="text-sm font-semibold">Alerts</h2>
            <div className="mt-3 space-y-2 text-sm">
              {lastAlerts.map((alert, idx) => (
                <div key={`${alert.at}-${idx}`} className="rounded bg-muted/40 p-2">
                  <span className="font-mono text-xs text-muted-foreground">T+{fmt(alert.at)} </span>
                  <span className="font-semibold uppercase">{alert.severity}</span>
                  <span className="mx-1">·</span>
                  <span>{alert.title}</span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default DemoConsole;
