import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { AppShell } from "@/components/AppShell";
import { CdsBanner } from "@/components/CdsBanner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Stethoscope, ArrowRight } from "lucide-react";

type Row = {
  id: string;
  procedure_name: string;
  patient_code: string;
  status: string;
  current_mode: string;
  created_at: string;
  surgeon_name: string | null;
  theatre: string | null;
};

const Sessions = () => {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      const { data } = await supabase
        .from("sessions")
        .select("id, procedure_name, patient_code, status, current_mode, created_at, surgeon_name, theatre")
        .order("created_at", { ascending: false });
      if (alive) {
        setRows((data ?? []) as Row[]);
        setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  return (
    <AppShell>
      <CdsBanner />
      <div className="container py-8 max-w-6xl">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-display text-3xl font-semibold tracking-tight">Sessions</h1>
            <p className="mt-2 text-sm text-muted-foreground">All operating-room sessions you have access to.</p>
          </div>
          <Button asChild className="bg-gradient-primary text-primary-foreground hover:opacity-90">
            <Link to="/sessions/new"><Stethoscope className="mr-2 h-4 w-4" /> New session</Link>
          </Button>
        </div>

        <div className="mt-8 panel overflow-hidden">
          <div className="hidden md:grid grid-cols-12 gap-4 border-b border-border px-5 py-3 text-xs uppercase tracking-[0.18em] text-muted-foreground">
            <div className="col-span-4">Procedure</div>
            <div className="col-span-2">Patient</div>
            <div className="col-span-2">Theatre</div>
            <div className="col-span-2">Mode</div>
            <div className="col-span-2 text-right">Status</div>
          </div>
          {loading ? (
            <div className="p-6 text-sm text-muted-foreground">Loading…</div>
          ) : rows.length === 0 ? (
            <div className="p-10 text-center">
              <p className="text-sm text-muted-foreground">No sessions yet.</p>
              <Button asChild className="mt-4 bg-gradient-primary text-primary-foreground hover:opacity-90">
                <Link to="/sessions/new">Start your first session</Link>
              </Button>
            </div>
          ) : (
            <ul className="divide-y divide-border">
              {rows.map((s) => (
                <li key={s.id}>
                  <Link
                    to={s.status === "completed" ? `/sessions/${s.id}/post-op` : `/sessions/${s.id}/console`}
                    className="grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 px-5 py-4 hover:bg-surface-2 transition-colors"
                  >
                    <div className="md:col-span-4">
                      <div className="font-medium">{s.procedure_name}</div>
                      <div className="text-xs text-muted-foreground mt-0.5">
                        {new Date(s.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className="md:col-span-2 text-mono text-sm text-muted-foreground self-center">{s.patient_code}</div>
                    <div className="md:col-span-2 text-sm text-muted-foreground self-center">{s.theatre ?? "—"}</div>
                    <div className="md:col-span-2 self-center">
                      <Badge variant="outline" className="text-[10px] uppercase tracking-wider">{s.current_mode}</Badge>
                    </div>
                    <div className="md:col-span-2 flex md:justify-end items-center gap-2 self-center">
                      <Badge className={
                        s.status === "in_progress" ? "bg-success/15 text-success border-success/30 border" :
                        s.status === "completed" ? "bg-info/15 text-info border-info/30 border" :
                        "bg-muted text-muted-foreground border-border border"
                      }>
                        {s.status.replace("_", " ")}
                      </Badge>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </AppShell>
  );
};

export default Sessions;
