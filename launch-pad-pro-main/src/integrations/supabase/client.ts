import { createClient } from "@supabase/supabase-js";
import type { Database } from "./types";
import { supabaseEnv } from "./env";

// Import the supabase client like this:
// import { supabase } from "@/integrations/supabase/client";

const FALLBACK_URL = "https://missing-supabase-env.invalid";
const FALLBACK_KEY = "missing-supabase-publishable-key";

if (supabaseEnv.issue && import.meta.env.DEV) {
  console.warn("[Supabase]", supabaseEnv.issue);
}

export const supabase = createClient<Database>(
  supabaseEnv.url || FALLBACK_URL,
  supabaseEnv.anonKey || FALLBACK_KEY,
  {
    auth: {
      storage: localStorage,
      persistSession: true,
      autoRefreshToken: true,
    },
  },
);