import { CDS_DISCLAIMER_SHORT } from "@/lib/cds";
import { ShieldCheck } from "lucide-react";

export function CdsBanner({ inline = false }: { inline?: boolean }) {
  if (inline) {
    return (
      <div className="flex items-start gap-2 rounded-md border border-border bg-surface-2 px-3 py-2 text-xs text-muted-foreground">
        <ShieldCheck className="h-3.5 w-3.5 mt-0.5 shrink-0 text-primary" />
        <span>{CDS_DISCLAIMER_SHORT}</span>
      </div>
    );
  }
  return (
    <div className="border-b border-border bg-surface-1">
      <div className="container flex items-center gap-2 py-2 text-xs text-muted-foreground">
        <ShieldCheck className="h-3.5 w-3.5 text-primary" />
        <span>
          <span className="font-medium text-foreground">Clinical Decision Support</span> ·{" "}
          {CDS_DISCLAIMER_SHORT}
        </span>
      </div>
    </div>
  );
}
