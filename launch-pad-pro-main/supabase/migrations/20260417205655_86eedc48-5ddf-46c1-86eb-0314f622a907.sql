
-- ============================================================
-- ARIA — Surgical AI Copilot — Initial Schema
-- ============================================================

-- Roles enum
CREATE TYPE public.app_role AS ENUM ('admin', 'surgeon', 'anaesthetist');

-- Procedure / mode / severity / interaction-mode enums
CREATE TYPE public.aria_mode AS ENUM ('silent', 'reactive', 'proactive');
CREATE TYPE public.session_status AS ENUM ('scheduled', 'in_progress', 'completed', 'aborted');
CREATE TYPE public.alert_severity AS ENUM ('info', 'caution', 'warning', 'critical');
CREATE TYPE public.transcript_speaker AS ENUM ('surgeon', 'anaesthetist', 'nurse', 'aria', 'system');

-- ============================================================
-- profiles (display info, NOT roles)
-- ============================================================
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT,
  title TEXT,                  -- e.g. "Dr.", "Prof."
  hospital TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- user_roles (SEPARATE table — required for security)
-- ============================================================
CREATE TABLE public.user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role public.app_role NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, role)
);
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- has_role security definer (avoids RLS recursion)
-- ============================================================
CREATE OR REPLACE FUNCTION public.has_role(_user_id UUID, _role public.app_role)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles
    WHERE user_id = _user_id
      AND role = _role
  )
$$;

-- helper: is admin
CREATE OR REPLACE FUNCTION public.is_admin(_user_id UUID)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT public.has_role(_user_id, 'admin')
$$;

-- ============================================================
-- updated_at trigger fn
-- ============================================================
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_profiles_updated_at
BEFORE UPDATE ON public.profiles
FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================
-- handle_new_user trigger: create profile + default role
-- ============================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_role public.app_role;
  v_role_text TEXT;
BEGIN
  INSERT INTO public.profiles (user_id, full_name, title, hospital)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data ->> 'full_name', ''),
    COALESCE(NEW.raw_user_meta_data ->> 'title', ''),
    COALESCE(NEW.raw_user_meta_data ->> 'hospital', '')
  );

  v_role_text := COALESCE(NEW.raw_user_meta_data ->> 'role', 'surgeon');
  IF v_role_text NOT IN ('admin', 'surgeon', 'anaesthetist') THEN
    v_role_text := 'surgeon';
  END IF;
  v_role := v_role_text::public.app_role;

  INSERT INTO public.user_roles (user_id, role)
  VALUES (NEW.id, v_role);

  RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================
-- profiles RLS
-- ============================================================
CREATE POLICY "Profiles viewable by authenticated"
ON public.profiles FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Users update own profile"
ON public.profiles FOR UPDATE
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users insert own profile"
ON public.profiles FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- user_roles RLS
-- ============================================================
CREATE POLICY "Users view own roles"
ON public.user_roles FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Admins view all roles"
ON public.user_roles FOR SELECT
TO authenticated
USING (public.is_admin(auth.uid()));

CREATE POLICY "Admins manage roles"
ON public.user_roles FOR ALL
TO authenticated
USING (public.is_admin(auth.uid()))
WITH CHECK (public.is_admin(auth.uid()));

-- ============================================================
-- sessions (a surgical case)
-- ============================================================
CREATE TABLE public.sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  patient_code TEXT NOT NULL,                   -- pseudonymous, NEVER real PHI
  procedure_name TEXT NOT NULL,
  procedure_category TEXT,
  surgeon_name TEXT,
  anaesthetist_name TEXT,
  theatre TEXT,
  status public.session_status NOT NULL DEFAULT 'scheduled',
  current_mode public.aria_mode NOT NULL DEFAULT 'reactive',
  disclaimer_accepted BOOLEAN NOT NULL DEFAULT false,
  disclaimer_accepted_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;

CREATE TRIGGER trg_sessions_updated_at
BEFORE UPDATE ON public.sessions
FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE INDEX idx_sessions_created_by ON public.sessions(created_by);
CREATE INDEX idx_sessions_status ON public.sessions(status);

CREATE POLICY "Users view own sessions"
ON public.sessions FOR SELECT
TO authenticated
USING (auth.uid() = created_by OR public.is_admin(auth.uid()));

CREATE POLICY "Users insert own sessions"
ON public.sessions FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users update own sessions"
ON public.sessions FOR UPDATE
TO authenticated
USING (auth.uid() = created_by OR public.is_admin(auth.uid()));

CREATE POLICY "Admins delete sessions"
ON public.sessions FOR DELETE
TO authenticated
USING (public.is_admin(auth.uid()));

-- ============================================================
-- transcripts (live OR transcript lines)
-- ============================================================
CREATE TABLE public.transcripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES public.sessions(id) ON DELETE CASCADE,
  speaker public.transcript_speaker NOT NULL,
  text TEXT NOT NULL,
  spoken_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  redacted BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.transcripts ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_transcripts_session ON public.transcripts(session_id, spoken_at);

CREATE POLICY "View transcripts of accessible sessions"
ON public.transcripts FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = transcripts.session_id
      AND (s.created_by = auth.uid() OR public.is_admin(auth.uid()))
  )
);

CREATE POLICY "Insert transcripts to own sessions"
ON public.transcripts FOR INSERT
TO authenticated
WITH CHECK (
  EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = transcripts.session_id
      AND s.created_by = auth.uid()
  )
);

-- ============================================================
-- alerts (proactive ARIA alerts)
-- ============================================================
CREATE TABLE public.alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES public.sessions(id) ON DELETE CASCADE,
  severity public.alert_severity NOT NULL DEFAULT 'info',
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  source TEXT,                             -- e.g. 'vitals', 'protocol', 'vision'
  acknowledged BOOLEAN NOT NULL DEFAULT false,
  acknowledged_at TIMESTAMPTZ,
  acknowledged_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_alerts_session ON public.alerts(session_id, created_at DESC);

CREATE POLICY "View alerts of accessible sessions"
ON public.alerts FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = alerts.session_id
      AND (s.created_by = auth.uid() OR public.is_admin(auth.uid()))
  )
);

CREATE POLICY "Insert alerts to own sessions"
ON public.alerts FOR INSERT
TO authenticated
WITH CHECK (
  EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = alerts.session_id
      AND s.created_by = auth.uid()
  )
);

CREATE POLICY "Update alerts of accessible sessions"
ON public.alerts FOR UPDATE
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = alerts.session_id
      AND (s.created_by = auth.uid() OR public.is_admin(auth.uid()))
  )
);

-- ============================================================
-- audit_log (DPDP-compliant, append-only)
-- ============================================================
CREATE TABLE public.audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id UUID REFERENCES auth.users(id),
  actor_email TEXT,
  session_id UUID REFERENCES public.sessions(id) ON DELETE SET NULL,
  action TEXT NOT NULL,                    -- e.g. 'session.start', 'mode.change', 'alert.ack'
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.audit_log ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_audit_actor ON public.audit_log(actor_id, created_at DESC);
CREATE INDEX idx_audit_session ON public.audit_log(session_id, created_at DESC);

CREATE POLICY "Users view own audit entries"
ON public.audit_log FOR SELECT
TO authenticated
USING (auth.uid() = actor_id OR public.is_admin(auth.uid()));

CREATE POLICY "Authenticated insert audit entries"
ON public.audit_log FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = actor_id);

-- (No update / delete policies — audit log is append-only)
