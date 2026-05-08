export type SupabaseEnvStatus = {
  url: string;
  anonKey: string;
  /** Present when URL parses; useful for support messages */
  displayHost: string | null;
  /** Misconfiguration only (missing vars / bad URL shape). DNS failures are detected at request time. */
  issue: string | null;
};

export function readSupabaseEnv(): SupabaseEnvStatus {
  const rawUrl = (import.meta.env.VITE_SUPABASE_URL as string | undefined)?.trim() ?? "";
  const anonKey =
    (import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string | undefined)?.trim() ?? "";

  if (!rawUrl || !anonKey) {
    return {
      url: rawUrl,
      anonKey,
      displayHost: null,
      issue:
        "Supabase is not configured: set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY (copy from .env.example into .env.local).",
    };
  }

  let displayHost: string | null = null;
  try {
    const u = new URL(rawUrl);
    displayHost = u.hostname;
    if (!u.hostname.endsWith(".supabase.co")) {
      return {
        url: rawUrl,
        anonKey,
        displayHost,
        issue: `Supabase URL host "${u.hostname}" should be *.supabase.co (Dashboard → Settings → API → Project URL).`,
      };
    }
  } catch {
    return {
      url: rawUrl,
      anonKey,
      displayHost: null,
      issue: "VITE_SUPABASE_URL is not a valid URL.",
    };
  }

  return { url: rawUrl, anonKey, displayHost, issue: null };
}

/** Loaded once at startup — matches values passed into createClient */
export const supabaseEnv = readSupabaseEnv();

export function friendlySupabaseAuthMessage(raw: string | undefined): string {
  const message = (raw ?? "").trim();
  if (isSupabaseReachabilityError(message)) {
    return (
      "Cannot reach Supabase (network/DNS). Open Dashboard → Settings → API and set VITE_SUPABASE_URL to your active " +
      "Project URL. If the browser shows ERR_NAME_NOT_RESOLVED for *.supabase.co, the project ref is wrong or the project was deleted."
    );
  }
  return message || "Sign-in request failed.";
}

export function isSupabaseReachabilityError(message: string | undefined): boolean {
  const m = (message ?? "").trim();
  return (
    /failed to fetch|networkerror|network request failed|load failed|fetch/i.test(m) ||
    /name not resolved|could not resolve/i.test(m)
  );
}
