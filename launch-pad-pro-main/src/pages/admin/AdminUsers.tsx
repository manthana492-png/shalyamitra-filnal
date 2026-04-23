import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { AppShell } from "@/components/AppShell";
import { CdsBanner } from "@/components/CdsBanner";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

type ProfileRow = {
  user_id: string; full_name: string | null; title: string | null; hospital: string | null;
};
type RoleRow = { user_id: string; role: string };

const AdminUsers = () => {
  const [profiles, setProfiles] = useState<ProfileRow[]>([]);
  const [rolesByUser, setRolesByUser] = useState<Record<string, string[]>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const [{ data: p }, { data: r }] = await Promise.all([
        supabase.from("profiles").select("user_id, full_name, title, hospital"),
        supabase.from("user_roles").select("user_id, role"),
      ]);
      setProfiles((p ?? []) as ProfileRow[]);
      const map: Record<string, string[]> = {};
      ((r ?? []) as RoleRow[]).forEach((row) => {
        map[row.user_id] = [...(map[row.user_id] ?? []), row.role];
      });
      setRolesByUser(map);
      setLoading(false);
    })();
  }, []);

  return (
    <AppShell>
      <CdsBanner />
      <div className="container py-8 max-w-5xl">
        <h1 className="text-display text-3xl font-semibold tracking-tight">Users</h1>
        <p className="mt-2 text-sm text-muted-foreground">All accounts with access to this ARIA project.</p>

        <div className="mt-8 panel overflow-hidden">
          {loading ? (
            <div className="flex h-48 items-center justify-center"><Loader2 className="h-5 w-5 animate-spin text-primary" /></div>
          ) : (
            <ul className="divide-y divide-border">
              {profiles.map((p) => (
                <li key={p.user_id} className="p-4 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="font-medium truncate">
                      {p.title ? `${p.title} ` : ""}{p.full_name ?? "(no name)"}
                    </div>
                    {p.hospital && <div className="text-xs text-muted-foreground truncate">{p.hospital}</div>}
                  </div>
                  <div className="flex gap-1.5 shrink-0">
                    {(rolesByUser[p.user_id] ?? ["surgeon"]).map((role) => (
                      <Badge key={role} variant="outline" className="text-[10px] uppercase tracking-wider">{role}</Badge>
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </AppShell>
  );
};

export default AdminUsers;
