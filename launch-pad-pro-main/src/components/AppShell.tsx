import { ReactNode } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { NaelLogo } from "@/components/NaelLogo";
import { Button } from "@/components/ui/button";
import { LayoutGrid, Activity, ShieldCheck, Users, LogOut, Stethoscope, Cpu, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const NAV_ITEMS = [
  { to: "/dashboard", icon: LayoutGrid, label: "Dashboard" },
  { to: "/sessions/domain", icon: Stethoscope, label: "New Session" },
  { to: "/sessions", icon: Activity, label: "Sessions" },
  { to: "/settings/profile", icon: User, label: "Profile" },
];

const ADMIN_ITEMS = [
  { to: "/admin/audit", icon: ShieldCheck, label: "Audit Log" },
  { to: "/admin/users", icon: Users, label: "Users" },
  { to: "/admin/gpu",   icon: Cpu,    label: "GPU Backend" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { profile, roles, signOut, user } = useAuth();
  const navigate = useNavigate();
  const isAdmin = roles.includes("admin");
  const primaryRole = roles[0] ?? "surgeon";

  const handleSignOut = async () => {
    await signOut();
    navigate("/", { replace: true });
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="hidden lg:flex w-60 shrink-0 flex-col border-r border-border bg-surface-1">
        <div className="px-5 pt-5 pb-4">
          <NaelLogo />
        </div>
        <nav className="flex-1 px-3 space-y-1">
          {NAV_ITEMS.map((it) => (
            <NavLink
              key={it.to}
              to={it.to}
              end={it.to === "/sessions"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                  isActive
                    ? "bg-surface-3 text-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-surface-2",
                )
              }
            >
              <it.icon className="h-4 w-4" />
              {it.label}
            </NavLink>
          ))}

          {isAdmin && (
            <>
              <div className="px-3 pt-5 pb-2 text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                Compliance
              </div>
              {ADMIN_ITEMS.map((it) => (
                <NavLink
                  key={it.to}
                  to={it.to}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                      isActive
                        ? "bg-surface-3 text-foreground"
                        : "text-muted-foreground hover:text-foreground hover:bg-surface-2",
                    )
                  }
                >
                  <it.icon className="h-4 w-4" />
                  {it.label}
                </NavLink>
              ))}
            </>
          )}
        </nav>

        <div className="border-t border-border p-3">
          <div className="rounded-md bg-surface-2 px-3 py-2.5">
            <div className="text-sm font-medium truncate">
              {profile?.title ? `${profile.title} ` : ""}
              {profile?.full_name || user?.email}
            </div>
            <div className="mt-1 flex items-center gap-2">
              <Badge variant="outline" className="text-[10px] uppercase tracking-wider">
                {primaryRole}
              </Badge>
              {profile?.hospital && (
                <span className="text-xs text-muted-foreground truncate">{profile.hospital}</span>
              )}
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="mt-2 w-full justify-start text-muted-foreground hover:text-foreground"
            onClick={handleSignOut}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Sign out
          </Button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 min-w-0">
        {/* Mobile top bar */}
        <header className="lg:hidden sticky top-0 z-20 flex items-center justify-between border-b border-border bg-surface-1/80 backdrop-blur px-4 py-3">
          <NaelLogo size="sm" />
          <Button variant="ghost" size="sm" onClick={handleSignOut}>
            <LogOut className="h-4 w-4" />
          </Button>
        </header>
        {children}
      </main>
    </div>
  );
}
