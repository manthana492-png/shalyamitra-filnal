import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { supabase } from "@/integrations/supabase/client";
import type { Session, User } from "@supabase/supabase-js";

export type AppRole = "admin" | "surgeon" | "anaesthetist";
const DEV_AUTH_BYPASS = String(import.meta.env.VITE_DEV_AUTH_BYPASS || "false").toLowerCase() === "true";
const DEV_OWNER_EMAIL = String(import.meta.env.VITE_DEV_OWNER_EMAIL || "owner@localhost");
const DEV_OWNER_ID = String(import.meta.env.VITE_DEV_OWNER_ID || "00000000-0000-0000-0000-000000000001");

export type Profile = {
  id: string;
  user_id: string;
  full_name: string | null;
  title: string | null;
  hospital: string | null;
  avatar_url: string | null;
};

type AuthContextValue = {
  user: User | null;
  session: Session | null;
  profile: Profile | null;
  roles: AppRole[];
  loading: boolean;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [roles, setRoles] = useState<AppRole[]>([]);
  const [loading, setLoading] = useState(true);

  const loadProfileAndRoles = async (uid: string) => {
    const [{ data: prof }, { data: r }] = await Promise.all([
      supabase.from("profiles").select("*").eq("user_id", uid).maybeSingle(),
      supabase.from("user_roles").select("role").eq("user_id", uid),
    ]);
    setProfile((prof as Profile) ?? null);
    setRoles(((r ?? []) as { role: AppRole }[]).map((x) => x.role));
  };

  useEffect(() => {
    if (DEV_AUTH_BYPASS) {
      const devUser = {
        id: DEV_OWNER_ID,
        email: DEV_OWNER_EMAIL,
        aud: "authenticated",
        role: "authenticated",
        app_metadata: { provider: "email", providers: ["email"] },
        user_metadata: { full_name: "Owner Dev", role: "admin" },
        created_at: new Date().toISOString(),
      } as User;
      setSession(null);
      setUser(devUser);
      setProfile({
        id: DEV_OWNER_ID,
        user_id: DEV_OWNER_ID,
        full_name: "Owner Dev",
        title: "Dr.",
        hospital: "Local Dev",
        avatar_url: null,
      });
      setRoles(["admin"]);
      setLoading(false);
      return;
    }

    // Set listener FIRST
    const { data: sub } = supabase.auth.onAuthStateChange((_event, sess) => {
      setSession(sess);
      setUser(sess?.user ?? null);
      if (sess?.user) {
        // Defer profile fetch (avoid deadlock)
        setTimeout(() => loadProfileAndRoles(sess.user.id), 0);
      } else {
        setProfile(null);
        setRoles([]);
      }
    });

    // THEN check existing session
    supabase.auth.getSession().then(({ data: { session: sess } }) => {
      setSession(sess);
      setUser(sess?.user ?? null);
      if (sess?.user) {
        loadProfileAndRoles(sess.user.id).finally(() => setLoading(false));
      } else {
        setLoading(false);
      }
    });

    return () => sub.subscription.unsubscribe();
  }, []);

  const refresh = async () => {
    if (DEV_AUTH_BYPASS) return;
    if (user) await loadProfileAndRoles(user.id);
  };

  const signOut = async () => {
    if (DEV_AUTH_BYPASS) return;
    await supabase.auth.signOut();
  };

  return (
    <AuthContext.Provider value={{ user, session, profile, roles, loading, signOut, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function useHasRole(role: AppRole) {
  const { roles } = useAuth();
  return roles.includes(role);
}
