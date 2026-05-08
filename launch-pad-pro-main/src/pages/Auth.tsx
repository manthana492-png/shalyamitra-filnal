import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { supabase } from "@/integrations/supabase/client";
import { friendlySupabaseAuthMessage, isSupabaseReachabilityError, supabaseEnv } from "@/integrations/supabase/env";
import { useAuth } from "@/contexts/AuthContext";
import { NaelLogo } from "@/components/NaelLogo";
import { CdsBanner } from "@/components/CdsBanner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { toast } from "@/hooks/use-toast";
import { Loader2 } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const OWNER_TEST_EMAIL = "shivakumarcjh@gmail.com";
const OWNER_TEST_PIN = "707";
const OWNER_SUPABASE_PASSWORD = "707707";

const normalizeOwnerPassword = (email: string, password: string) => {
  const e = email.trim().toLowerCase();
  if (e === OWNER_TEST_EMAIL && password === OWNER_TEST_PIN) {
    return OWNER_SUPABASE_PASSWORD;
  }
  return password;
};

const signInSchema = z.object({
  email: z.string().email(),
  // Allow 3-char owner test pin ("707") while keeping regular password checks server-side.
  password: z.string().min(3, "At least 3 characters"),
});

const signUpSchema = z.object({
  email: z.string().email(),
  password: z.string().min(3, "At least 3 characters"),
  full_name: z.string().min(2, "Required"),
  title: z.string().optional(),
  hospital: z.string().optional(),
  role: z.enum(["surgeon", "anaesthetist", "admin"]),
});

type SignInValues = z.infer<typeof signInSchema>;
type SignUpValues = z.infer<typeof signUpSchema>;

const AuthPage = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [params] = useSearchParams();
  const initialMode = params.get("mode") === "signup" ? "signup" : "signin";
  const [tab, setTab] = useState<"signin" | "signup">(initialMode);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && user) navigate("/dashboard", { replace: true });
  }, [user, loading, navigate]);

  const signInForm = useForm<SignInValues>({
    resolver: zodResolver(signInSchema),
    defaultValues: { email: "", password: "" },
  });
  const signUpForm = useForm<SignUpValues>({
    resolver: zodResolver(signUpSchema),
    defaultValues: { email: "", password: "", full_name: "", title: "Dr.", hospital: "", role: "surgeon" },
  });

  const onSignIn = async (v: SignInValues) => {
    setSubmitting(true);
    const normalizedPassword = normalizeOwnerPassword(v.email, v.password);
    const { error } = await supabase.auth.signInWithPassword({
      email: v.email.trim(), password: normalizedPassword,
    });
    setSubmitting(false);
    if (error) {
      toast({
        title: "Sign-in failed",
        description: friendlySupabaseAuthMessage(error.message),
        variant: "destructive",
      });
      return;
    }
    navigate("/dashboard", { replace: true });
  };

  const onSignUp = async (v: SignUpValues) => {
    setSubmitting(true);
    const email = v.email.trim();
    const normalizedPassword = normalizeOwnerPassword(email, v.password);
    const isOwner = email.toLowerCase() === OWNER_TEST_EMAIL;
    const { error } = await supabase.auth.signUp({
      email,
      password: normalizedPassword,
      options: {
        emailRedirectTo: `${window.location.origin}/dashboard`,
        data: {
          full_name: isOwner ? "Shiva Kumar" : v.full_name,
          title: v.title ?? "",
          hospital: v.hospital ?? "",
          role: isOwner ? "admin" : v.role,
        },
      },
    });
    setSubmitting(false);
    if (error) {
      toast({
        title: "Sign-up failed",
        description: friendlySupabaseAuthMessage(error.message),
        variant: "destructive",
      });
      return;
    }
    toast({ title: "Welcome to ShalyaMitra", description: "Account created. Signing you in…" });
    navigate("/dashboard", { replace: true });
  };

  const ownerQuickAccess = async () => {
    setSubmitting(true);
    const email = OWNER_TEST_EMAIL;
    const password = OWNER_SUPABASE_PASSWORD;
    const signIn = await supabase.auth.signInWithPassword({ email, password });
    if (!signIn.error) {
      setSubmitting(false);
      navigate("/dashboard", { replace: true });
      return;
    }

    if (isSupabaseReachabilityError(signIn.error.message)) {
      setSubmitting(false);
      toast({
        title: "Owner quick access failed",
        description: friendlySupabaseAuthMessage(signIn.error.message),
        variant: "destructive",
      });
      return;
    }

    // If owner user doesn't exist yet, create once and continue.
    const signUp = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/dashboard`,
        data: {
          full_name: "Shiva Kumar",
          title: "Dr.",
          hospital: "ShalyaMitra Test",
          role: "admin",
        },
      },
    });
    setSubmitting(false);
    if (signUp.error) {
      toast({
        title: "Owner quick access failed",
        description: friendlySupabaseAuthMessage(signUp.error.message),
        variant: "destructive",
      });
      return;
    }
    toast({
      title: "Owner test account ready",
      description: "Use shivakumarcjh@gmail.com and PIN 707 to sign in.",
    });
    navigate("/dashboard", { replace: true });
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="border-b border-border">
        <div className="container flex h-14 items-center justify-between">
          <NaelLogo />
          <Button asChild variant="ghost" size="sm"><Link to="/">Back</Link></Button>
        </div>
      </header>
      <CdsBanner />

      {supabaseEnv.issue && (
        <div className="border-b border-border bg-muted/40 px-4 py-3">
          <Alert variant="destructive">
            <AlertTitle>Supabase configuration</AlertTitle>
            <AlertDescription>{supabaseEnv.issue}</AlertDescription>
          </Alert>
        </div>
      )}

      <div className="flex-1 grid lg:grid-cols-2">
        <div className="hidden lg:flex flex-col justify-center px-14 bg-surface-1 border-r border-border">
          <h1 className="text-display text-4xl font-semibold tracking-tight max-w-md">
            Sign in to your <span className="bg-gradient-primary bg-clip-text text-transparent">surgical intelligence</span>.
          </h1>
          <p className="mt-4 text-muted-foreground max-w-md">
            ShalyaMitra is a clinical decision support tool. Access is role-based and every action is recorded
            in an append-only audit log.
          </p>
          <ul className="mt-8 space-y-2 text-sm text-muted-foreground max-w-md">
            <li>• Surgeons run intra-operative sessions and review post-op summaries.</li>
            <li>• Anaesthetists co-attend sessions and monitor vitals-driven alerts.</li>
            <li>• Admins manage users, roles, and review the compliance audit log.</li>
          </ul>
        </div>

        <div className="flex items-center justify-center p-6 sm:p-12">
          <div className="w-full max-w-md">
            <Tabs value={tab} onValueChange={(v) => setTab(v as "signin" | "signup")}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="signin">Sign in</TabsTrigger>
                <TabsTrigger value="signup">Create account</TabsTrigger>
              </TabsList>

              <TabsContent value="signin" className="mt-6">
                <form onSubmit={signInForm.handleSubmit(onSignIn)} className="space-y-4">
                  <div className="rounded-md border border-primary/30 bg-surface-2 px-3 py-2 text-xs text-muted-foreground">
                    Owner quick test: <span className="font-mono">{OWNER_TEST_EMAIL}</span> /
                    <span className="font-mono"> {OWNER_TEST_PIN}</span>
                  </div>
                  <div>
                    <Label htmlFor="si-email">Email</Label>
                    <Input id="si-email" type="email" autoComplete="email"
                      {...signInForm.register("email")} />
                    {signInForm.formState.errors.email && (
                      <p className="mt-1 text-xs text-destructive">{signInForm.formState.errors.email.message}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="si-password">Password</Label>
                    <Input id="si-password" type="password" autoComplete="current-password"
                      {...signInForm.register("password")} />
                    {signInForm.formState.errors.password && (
                      <p className="mt-1 text-xs text-destructive">{signInForm.formState.errors.password.message}</p>
                    )}
                  </div>
                  <Button type="submit" disabled={submitting}
                    className="w-full bg-gradient-primary text-primary-foreground hover:opacity-90">
                    {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Sign in
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    disabled={submitting}
                    onClick={ownerQuickAccess}
                    className="w-full"
                  >
                    Owner quick access
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="signup" className="mt-6">
                <form onSubmit={signUpForm.handleSubmit(onSignUp)} className="space-y-4">
                  <div className="grid grid-cols-3 gap-3">
                    <div className="col-span-1">
                      <Label htmlFor="su-title">Title</Label>
                      <Input id="su-title" placeholder="Dr." {...signUpForm.register("title")} />
                    </div>
                    <div className="col-span-2">
                      <Label htmlFor="su-name">Full name</Label>
                      <Input id="su-name" placeholder="Jane Smith" {...signUpForm.register("full_name")} />
                      {signUpForm.formState.errors.full_name && (
                        <p className="mt-1 text-xs text-destructive">{signUpForm.formState.errors.full_name.message}</p>
                      )}
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="su-hospital">Hospital / Institution</Label>
                    <Input id="su-hospital" placeholder="Apollo Hospital, Bengaluru" {...signUpForm.register("hospital")} />
                  </div>
                  <div>
                    <Label htmlFor="su-role">Role</Label>
                    <Select
                      defaultValue="surgeon"
                      onValueChange={(v) => signUpForm.setValue("role", v as SignUpValues["role"])}
                    >
                      <SelectTrigger id="su-role"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="surgeon">Surgeon</SelectItem>
                        <SelectItem value="anaesthetist">Anaesthetist</SelectItem>
                        <SelectItem value="admin">Admin / Compliance</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="su-email">Email</Label>
                    <Input id="su-email" type="email" autoComplete="email"
                      {...signUpForm.register("email")} />
                    {signUpForm.formState.errors.email && (
                      <p className="mt-1 text-xs text-destructive">{signUpForm.formState.errors.email.message}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="su-password">Password</Label>
                    <Input id="su-password" type="password" autoComplete="new-password"
                      {...signUpForm.register("password")} />
                    {signUpForm.formState.errors.password && (
                      <p className="mt-1 text-xs text-destructive">{signUpForm.formState.errors.password.message}</p>
                    )}
                  </div>
                  <Button type="submit" disabled={submitting}
                    className="w-full bg-gradient-primary text-primary-foreground hover:opacity-90">
                    {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Create account
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
