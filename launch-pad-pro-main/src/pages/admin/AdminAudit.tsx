import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { AppShell } from "@/components/AppShell";
import { CdsBanner } from "@/components/CdsBanner";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

type AuditRow = {
  id: string; actor_email: string | null; action: string;
  details: Record<string, unknown>; created_at: string; session_id: string | null;
};

const AdminAudit = () => {
  const [rows, setRows] = useState<AuditRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const { data } = await supabase
        .from("audit_log")
        .select("id, actor_email, action, details, created_at, session_id")
        .order("created_at", { ascending: false })
        .limit(500);
      setRows((data ?? []) as AuditRow[]);
      setLoading(false);
    })();
  }, []);

  return (
    <AppShell>
      <CdsBanner />
      <div className="container py-8 max-w-5xl">
        <h1 className="text-display text-3xl font-semibold tracking-tight">Audit log</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Append-only record of every meaningful action taken across all ARIA sessions. DPDP-aligned.
        </p>

        <div className="mt-8 panel overflow-hidden">
          {loading ? (
            <div className="flex h-48 items-center justify-center"><Loader2 className="h-5 w-5 animate-spin text-primary" /></div>
          ) : rows.length === 0 ? (
            <div className="p-6 text-sm text-muted-foreground">No audit entries yet.</div>
          ) : (
            <ul className="divide-y divide-border">
              {rows.map((r) => (
                <li key={r.id} className="p-4">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <Badge variant="outline" className="text-mono text-[10px] uppercase tracking-wider">{r.action}</Badge>
                      <span className="text-sm truncate">{r.actor_email ?? "—"}</span>
                    </div>
                    <span className="text-mono text-[10px] text-muted-foreground shrink-0">
                      {new Date(r.created_at).toLocaleString()}
                    </span>
                  </div>
                  {r.details && Object.keys(r.details).length > 0 && (
                    <pre className="mt-2 overflow-x-auto rounded-md bg-surface-2 p-2 text-mono text-[11px] text-muted-foreground">
                      {JSON.stringify(r.details, null, 2)}
                    </pre>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </AppShell>
  );
};

export default AdminAudit;
