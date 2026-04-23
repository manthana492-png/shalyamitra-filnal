/**
 * NewSession — OR session configuration form.
 *
 * Reads ?domain=ayurveda|modern from the URL (set by DomainSelect).
 * Uses the ProcedurePicker for domain-aware, searchable procedure selection.
 */

import { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/integrations/supabase/client";
import { logAudit } from "@/lib/audit";
import { CDS_DISCLAIMER_FULL } from "@/lib/cds";
import { AppShell } from "@/components/AppShell";
import { CdsBanner } from "@/components/CdsBanner";
import { ProcedurePicker } from "@/components/ProcedurePicker";
import { getProceduresByDomain } from "@/lib/procedures";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "@/hooks/use-toast";
import { Loader2, ShieldCheck, Leaf, Dna, ArrowLeft } from "lucide-react";

const schema = z.object({
  procedure_name: z.string().min(2, "Required"),
  procedure_category: z.string().optional(),
  patient_code: z.string().min(1, "Required").max(40),
  surgeon_name: z.string().optional(),
  anaesthetist_name: z.string().optional(),
  theatre: z.string().optional(),
  notes: z.string().optional(),
  disclaimer_accepted: z.literal(true, {
    errorMap: () => ({ message: "Please accept the CDS disclaimer to continue." }),
  }),
});

type FormValues = z.infer<typeof schema>;

const DOMAIN_META = {
  ayurveda: {
    label: "Ayurveda Surgery",
    subtitle: "Shalya Tantra · MS Ayurved",
    icon: Leaf,
    color: "text-green-400",
    border: "border-green-500/30",
    bg: "bg-green-500/5",
  },
  modern: {
    label: "Modern Surgery",
    subtitle: "Allopathy · Evidence-Based",
    icon: Dna,
    color: "text-sky-400",
    border: "border-sky-500/30",
    bg: "bg-sky-500/5",
  },
} as const;

type Domain = "ayurveda" | "modern";

const NewSession = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, profile } = useAuth();
  const [submitting, setSubmitting] = useState(false);

  const rawDomain = searchParams.get("domain") ?? "modern";
  const domain: Domain = rawDomain === "ayurveda" ? "ayurveda" : "modern";
  const meta = DOMAIN_META[domain];
  const DomainIcon = meta.icon;
  const totalProcedures = getProceduresByDomain(domain).length;

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      procedure_name: "",
      procedure_category: domain === "ayurveda" ? "Shalya Tantra" : "General Surgery",
      patient_code: `PT-${Date.now().toString().slice(-6)}`,
      surgeon_name: profile?.full_name ?? "",
      anaesthetist_name: "",
      theatre: "OR-1",
      notes: "",
      disclaimer_accepted: false as unknown as true,
    },
  });

  const onSubmit = async (v: FormValues) => {
    if (!user) return;
    setSubmitting(true);
    const { data, error } = await supabase
      .from("sessions")
      .insert({
        created_by: user.id,
        procedure_name: v.procedure_name,
        procedure_category: v.procedure_category ?? null,
        patient_code: v.patient_code,
        surgeon_name: v.surgeon_name ?? null,
        anaesthetist_name: v.anaesthetist_name ?? null,
        theatre: v.theatre ?? null,
        notes: v.notes ?? null,
        status: "scheduled",
        current_mode: "reactive",
        disclaimer_accepted: true,
        disclaimer_accepted_at: new Date().toISOString(),
      })
      .select("id")
      .single();
    setSubmitting(false);
    if (error || !data) {
      toast({ title: "Could not create session", description: error?.message, variant: "destructive" });
      return;
    }
    await logAudit({
      action: "session.create",
      sessionId: data.id,
      details: { procedure: v.procedure_name, theatre: v.theatre, domain },
    });
    navigate(`/sessions/${data.id}/console`);
  };

  return (
    <AppShell>
      <CdsBanner />
      <div className="container py-8 max-w-3xl">

        {/* Back + domain badge */}
        <div className="flex items-center gap-3 mb-6">
          <Button asChild variant="ghost" size="sm" className="gap-1 text-muted-foreground hover:text-foreground">
            <Link to="/sessions/domain">
              <ArrowLeft className="h-4 w-4" /> Back
            </Link>
          </Button>
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${meta.border} ${meta.bg}`}>
            <DomainIcon className={`h-3.5 w-3.5 ${meta.color}`} />
            <span className={`text-mono text-[11px] uppercase tracking-[0.15em] ${meta.color}`}>
              {meta.label}
            </span>
          </div>
        </div>

        <h1 className="text-display text-3xl font-semibold tracking-tight">
          Configure OR Session
        </h1>
        <p className="mt-2 text-muted-foreground">
          Set up the case before stepping into theatre. Nael will start in{" "}
          <strong>Reactive</strong> mode — change at any time from the console.
        </p>

        <form onSubmit={form.handleSubmit(onSubmit)} className="mt-8 space-y-6">

          {/* Procedure section */}
          <div className="hud-frame hud-corners relative p-6 space-y-5">
            <span className="corner-tr" /><span className="corner-bl" />
            <h2 className="font-semibold flex items-center gap-2">
              <DomainIcon className={`h-4 w-4 ${meta.color}`} />
              Procedure
            </h2>

            {/* Smart picker */}
            <div>
              <Label className="mb-2 block">
                Procedure
                <span className="ml-2 text-mono text-[9px] text-primary/50 uppercase tracking-wider">
                  search or scroll · {totalProcedures} procedures
                </span>
              </Label>
              <ProcedurePicker
                domain={domain}
                value={form.watch("procedure_name")}
                onChange={(v) => form.setValue("procedure_name", v, { shouldValidate: true })}
              />
              {form.formState.errors.procedure_name && (
                <p className="mt-1 text-xs text-destructive">
                  {form.formState.errors.procedure_name.message}
                </p>
              )}
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="cat">Category</Label>
                <Input id="cat" {...form.register("procedure_category")} />
              </div>
              <div>
                <Label htmlFor="theatre">Theatre</Label>
                <Input id="theatre" {...form.register("theatre")} />
              </div>
            </div>
          </div>

          {/* Patient */}
          <div className="hud-frame hud-corners relative p-6 space-y-5">
            <span className="corner-tr" /><span className="corner-bl" />
            <div>
              <h2 className="font-semibold">Patient</h2>
              <p className="text-xs text-muted-foreground mt-1">
                Use a pseudonymous code only. Never enter real patient names or identifiers.
              </p>
            </div>
            <div>
              <Label htmlFor="pcode">Patient code</Label>
              <Input id="pcode" className="text-mono" {...form.register("patient_code")} />
              {form.formState.errors.patient_code && (
                <p className="mt-1 text-xs text-destructive">{form.formState.errors.patient_code.message}</p>
              )}
            </div>
          </div>

          {/* Team */}
          <div className="hud-frame hud-corners relative p-6 space-y-5">
            <span className="corner-tr" /><span className="corner-bl" />
            <h2 className="font-semibold">Team</h2>
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="surg">Surgeon</Label>
                <Input id="surg" {...form.register("surgeon_name")} />
              </div>
              <div>
                <Label htmlFor="anaes">Anaesthetist</Label>
                <Input id="anaes" {...form.register("anaesthetist_name")} />
              </div>
            </div>
            <div>
              <Label htmlFor="notes">Pre-op notes</Label>
              <Textarea id="notes" rows={3} {...form.register("notes")} />
            </div>
          </div>

          {/* CDS disclaimer */}
          <div className="hud-frame hud-corners relative p-6">
            <span className="corner-tr" /><span className="corner-bl" />
            <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-muted-foreground">
              <ShieldCheck className="h-4 w-4 text-primary" /> CDS Disclaimer
            </div>
            <p className="mt-3 text-sm text-muted-foreground">{CDS_DISCLAIMER_FULL}</p>
            <label className="mt-4 flex items-start gap-3 cursor-pointer">
              <Checkbox
                checked={form.watch("disclaimer_accepted") as unknown as boolean}
                onCheckedChange={(c) =>
                  form.setValue("disclaimer_accepted", (c === true) as unknown as true, { shouldValidate: true })
                }
              />
              <span className="text-sm">
                I understand Nael is a clinical decision support tool. Final clinical judgement rests with
                the operating team.
              </span>
            </label>
            {form.formState.errors.disclaimer_accepted && (
              <p className="mt-2 text-xs text-destructive">
                {form.formState.errors.disclaimer_accepted.message as string}
              </p>
            )}
          </div>

          <div className="flex justify-end gap-3">
            <Button type="button" variant="ghost" onClick={() => navigate(-1)}>Cancel</Button>
            <Button
              type="submit"
              disabled={submitting}
              className="bg-gradient-primary text-primary-foreground hover:opacity-90"
            >
              {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Enter OR Console
            </Button>
          </div>
        </form>
      </div>
    </AppShell>
  );
};

export default NewSession;
