import { supabase } from "@/integrations/supabase/client";

/**
 * Append-only audit logger. Every meaningful action a clinician takes inside
 * ARIA should call this. Backed by the audit_log table with no UPDATE/DELETE
 * RLS policies — DPDP-style write-once.
 */
export async function logAudit(opts: {
  action: string;
  sessionId?: string | null;
  details?: Record<string, unknown>;
}) {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;
    await supabase.from("audit_log").insert({
      actor_id: user.id,
      actor_email: user.email ?? null,
      session_id: opts.sessionId ?? null,
      action: opts.action,
      details: (opts.details ?? {}) as never,
    });
  } catch (e) {
    // Never throw from audit — never block clinical flow.
    // eslint-disable-next-line no-console
    console.warn("audit log failed", e);
  }
}
