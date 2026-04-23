# ARIA — Frontend Build Specification (v1)

> **Scope of this document**: Pure **frontend** spec for the ARIA surgical AI copilot web app. This document is self-sufficient — handed to any AI agent, it should produce the exact same frontend (currently implemented features + the listed unimplemented specs at the end).
>
> **Backend integration is out of scope** here. The frontend is designed to talk to a Supabase-shaped backend (auth, RLS-protected tables: `sessions`, `transcripts`, `alerts`, `audit_log`, `profiles`, `user_roles`) and a GPU realtime relay edge function (`aria-realtime`) — but **the frontend works end-to-end against a local scripted demo session** with zero backend wiring.

---

## 1. Product Brief (frontend lens)

ARIA is a **Jarvis-class holographic OR HUD**: a futuristic, voice-controlled surgical copilot that displays live transcript, vitals, alerts, and 3 OR camera feeds during a surgery. The agent ("ARIA") can take **direct control of the UI** — rearranging layout, focusing cameras, surfacing checklists — driven by voice commands and procedure phase.

**Audience**: surgeons & anaesthetists in the OR. Operational, not marketing.
**Aesthetic**: deep space-black surfaces, electric cyan glows, animated HUD chrome, scanlines, mono data fonts. Think Iron Man HUD + clinical restraint.
**Critical constraint**: every clinical text output must wear a **CDS (Clinical Decision Support) disclaimer** — ARIA is a copilot, never a decision-maker.

---

## 2. Tech Stack (frozen)

| Layer | Tech |
|---|---|
| Framework | **React 18 + Vite 5 + TypeScript 5** |
| Styling | **Tailwind CSS v3** (semantic HSL tokens, no raw colors) |
| UI Primitives | **shadcn/ui** (Radix under the hood) |
| Routing | **react-router-dom v6** |
| State | **Zustand** (UI Director store) + React Context (Auth) |
| Forms | **react-hook-form + zod** |
| Data | **@tanstack/react-query** + Supabase JS client |
| Icons | **lucide-react** |
| PDF | **jspdf** + **jspdf-autotable** |
| Toasts | **sonner** + shadcn toast |
| Voice (in) | **Web Speech API** (`webkitSpeechRecognition`) |
| Voice (out) | Edge function `aria-tts` (Lovable AI Gateway TTS) → audio blob → `<audio>`, with **Web Speech Synthesis fallback** |

**Forbidden**: Next.js, Vue, Svelte, raw CSS color literals in components, `text-white`/`bg-black` Tailwind classes (always use semantic tokens).

---

## 3. Design System

### 3.1 Color tokens (`src/index.css`, all HSL)

```css
:root {
  /* Surfaces */
  --background: 220 40% 3%;          /* deep space black */
  --foreground: 180 35% 96%;
  --surface-1: 220 35% 5%;
  --surface-2: 220 32% 8%;
  --surface-3: 220 30% 11%;
  --card: 220 35% 5%;
  --popover: 220 38% 4%;

  /* Brand: electric cyan */
  --primary: 184 100% 54%;
  --primary-foreground: 220 60% 4%;
  --primary-glow: 184 100% 70%;

  /* Severity scale (clinical) */
  --info:     200 100% 62%;
  --caution:   42 100% 60%;
  --warning:   28 100% 56%;
  --critical: 358  90% 60%;
  --success:  152  80% 48%;

  /* HUD borders */
  --border:        188 60% 18%;
  --border-strong: 188 70% 30%;
  --ring:          184 100% 54%;

  --radius: 0.625rem;

  /* Gradients */
  --gradient-primary:  linear-gradient(135deg, hsl(184 100% 54%), hsl(195 100% 65%));
  --gradient-glow:     radial-gradient(ellipse 80% 60% at 50% 0%, hsl(184 100% 54% / 0.18), transparent 70%);
  --gradient-critical: linear-gradient(135deg, hsl(358 90% 60%), hsl(20 95% 55%));
  --gradient-hud:      linear-gradient(180deg, hsl(220 35% 6% / 0.8), hsl(220 40% 3% / 0.6));

  /* Shadows */
  --shadow-panel:        0 1px 0 hsl(184 100% 54% / 0.06) inset, 0 12px 32px -16px hsl(220 60% 0% / 0.7);
  --shadow-glow:         0 0 0 1px hsl(184 100% 54% / 0.4), 0 0 24px -2px hsl(184 100% 54% / 0.45);
  --shadow-glow-strong:  0 0 0 1px hsl(184 100% 54% / 0.6), 0 0 32px hsl(184 100% 54% / 0.55), 0 0 80px hsl(184 100% 54% / 0.25);
  --shadow-critical:     0 0 0 1px hsl(358 90% 60% / 0.5), 0 0 28px -2px hsl(358 90% 60% / 0.55);

  /* Motion */
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-hud:  350ms cubic-bezier(0.65, 0, 0.35, 1);
}
```

Body has a global radial cyan glow + secondary blue glow (`background-image` on `body`, `background-attachment: fixed`).

### 3.2 Typography

- `--font-sans`: **Inter**, with `font-feature-settings: 'cv02','cv03','cv04','cv11'`.
- `--font-mono`: **JetBrains Mono**, used for all data, timestamps, telemetry, IDs, intent labels.
- Display headings: `letter-spacing: -0.02em`.
- Mono labels (HUD chrome): uppercase, tracking `0.2em–0.3em`, size `10px`, color `text-primary/70`.

### 3.3 HUD primitive classes (`@layer components`)

| Class | Purpose |
|---|---|
| `.panel` | Standard rounded panel, `border-border`, `bg-card/70`, backdrop-blur, panel shadow |
| `.panel-strong` | Stronger border + opacity variant |
| `.hud-frame` | Sci-fi panel: cyan border, inset glow, **animated corner brackets via `::before` (TL) and `::after` (BR)** |
| `.hud-corners` + child `.corner-tr` + `.corner-bl` | Adds remaining 2 corner brackets (TR, BL) |
| `.hud-grid` | 40×40px cyan dotted grid background |
| `.hud-scanline` | Horizontal scanline overlay (3px repeat, very subtle cyan) |
| `.hud-sweep` | Vertical sweeping cyan beam (4s loop) — used inside camera tiles |
| `.text-mono`, `.text-display`, `.text-hud-label` | Typography utilities |
| `.text-glow`, `.text-glow-strong` | Cyan glow text-shadows |
| `.glow-ring`, `.glow-ring-strong` | Box-shadow glows |
| `.pulse-dot` (+ modifiers `.live`, `.cyan`) | Status dot with expanding-ring animation |

### 3.4 Animations (keyframes)

| Name | Duration | Use |
|---|---|---|
| `aria-pulse` | 1.4s loop | `.pulse-dot::after` expanding ring |
| `aria-listening` | 1s alt | Voice-bar scaleY |
| `aria-fade-in` | 280ms | Transcript line entrance |
| `aria-fade-up` | 350ms | Page enter |
| `hud-sweep` | 4s linear loop | Camera scan beam |
| `hud-pulse` | 2.4s loop | ARIA orb idle pulse |
| `hud-orbit` | 14s linear loop | Orb / camera placeholder ring |
| `hud-orbit-rev` | 22s | Counter-rotating ring |
| `hud-flicker` | 6s | Subtle CRT flicker |

Tailwind utilities exposed: `.animate-fade-in`, `.animate-fade-up`, `.animate-hud-pulse`, `.animate-hud-orbit`, `.animate-hud-orbit-rev`, `.animate-hud-flicker`, plus shadcn defaults (`.animate-listening`, accordion).

### 3.5 Tailwind config (`tailwind.config.ts`)

- `darkMode: ["class"]` (app is dark by default — `.dark` class on root).
- `container.padding: "1.5rem"`, `screens: { "2xl": "1440px" }`.
- `fontFamily: { sans: ["var(--font-sans)"], mono: ["var(--font-mono)"] }`.
- All semantic colors mapped to `hsl(var(--token))`.
- `colors.primary` includes `glow: "hsl(var(--primary-glow))"`.
- Severity colors: `info`, `caution`, `warning`, `critical`, `success` — each with `foreground`.
- `surface-1/2/3` colors mapped from CSS vars.

---

## 4. Routing & Page Map (`src/App.tsx`)

```
/                                  → Index (marketing landing)
/auth                              → Auth (sign in / sign up)
/dashboard                         → Dashboard (session list, role-gated admin links)   [protected]
/sessions                          → Sessions index                                      [protected]
/sessions/new                      → NewSession (create form)                            [protected]
/sessions/:id/console              → SessionConsole (the HUD)                            [protected]
/sessions/:id/post-op              → PostOp (summary + PDF export)                       [protected]
/admin/users                       → AdminUsers                                          [protected, admin]
/admin/audit                       → AdminAudit                                          [protected, admin]
/admin/gpu                         → AdminGpu (NVIDIA backend health)                    [protected, admin]
*                                  → NotFound
```

Wrapping providers (in order): `QueryClientProvider` → `TooltipProvider` → `Toaster` (shadcn) → `Sonner` → `BrowserRouter` → `AuthProvider` → `Routes`.

`ProtectedRoute` checks Supabase session; `requireRole` prop calls `has_role` to gate admin routes; redirects to `/auth` while preserving intended destination.

---

## 5. Global Components

### 5.1 `AppShell` (`src/components/AppShell.tsx`)
Top app chrome for non-console pages.

- Sticky header: ARIA logo (left), nav (Dashboard / Sessions / Admin if role), user menu (right) with profile + sign out.
- Optional CDS banner directly under the header (`<CdsBanner />`).
- `<main>` slot with `container mx-auto py-8`.
- Footer: tiny mono "ARIA · v1 · clinical decision support · not a medical device".

### 5.2 `AriaLogo`
Custom inline SVG: a stylized "A" inside a hex/diamond with a cyan glow. Two sizes via `size` prop (`sm`, `md`, `lg`). `text-glow` applied to the wordmark "ARIA".

### 5.3 `CdsBanner`
Slim cyan-bordered banner: `ShieldCheck` icon + the **CDS_DISCLAIMER_LONG** string from `src/lib/cds.ts`. Dismissable per-session via `localStorage`. Critical: it must NOT be dismissable on the SessionConsole — there it's permanently rendered above the HUD grid.

### 5.4 `NavLink`
React-router `NavLink` wrapper with HUD active state: `data-[active]:text-primary data-[active]:text-glow` + bottom border on active.

### 5.5 `ProtectedRoute`
- Subscribes to `useAuth()`.
- Loading → render full-screen "ARIA · standby" with `animate-hud-pulse` ring.
- No session → `<Navigate to="/auth" state={{ from: location }} />`.
- `requireRole` → checks role from `user_roles`; if missing, redirect to `/dashboard` with a toast.

---

## 6. Auth (`src/contexts/AuthContext.tsx` + `src/pages/Auth.tsx`)

- Single context exposing `{ user, session, role, loading, signIn, signUp, signOut }`.
- **Order rule (critical)**: in the `useEffect`, **call `onAuthStateChange` FIRST**, **then** `getSession()` — never the reverse — to avoid race conditions.
- Inside `onAuthStateChange`, if you need to read other Supabase tables (like `user_roles`), wrap in `setTimeout(() => …, 0)` to avoid deadlocks.
- Email + password auth. `emailRedirectTo: ${window.location.origin}/`.
- 3 roles: `surgeon` (default on signup) | `anaesthetist` | `admin`.
- Auto-confirm email is **enabled** in dev/demo so signups can immediately sign in.

`Auth.tsx` UI:
- Centered `hud-frame` panel, ARIA logo top, `Tabs` ("Sign In" / "Sign Up").
- Sign-up captures: full name, hospital, title, role select.
- Live form validation (zod). Loading spinners on submit.
- Toast feedback. Redirect to `location.state?.from || /dashboard` on success.

---

## 7. Marketing Landing (`src/pages/Index.tsx`)

Sections:
1. **Hero**: full-bleed `src/assets/hero-hud.jpg` (generated holographic OR HUD image) with cyan radial overlay, headline "ARIA · The OR Copilot", sub-headline, CTA buttons → `/auth`. Animated cyan particle/orbit ring behind the headline. `hud-grid` background.
2. **Three pillars**: cards (`hud-frame`) with icons — "Listens (Riva ASR)", "Sees (Triton Vision)", "Speaks (NeMo + Guardrails)".
3. **Live HUD preview** (animated mock screenshot of the SessionConsole, scaled 0.6).
4. **CDS strip** + footer.

All copy in clinical, calm tone — no marketing fluff in the HUD itself.

---

## 8. Dashboard (`src/pages/Dashboard.tsx`)

- Greeting card (top): "Good morning, Dr. {full_name}" + role badge + theatre + hospital. Keyed off time of day.
- **Big primary CTA**: "Start a new session" → `/sessions/new` (gradient-primary button with glow-ring).
- Stat cards (`StatCard`): Sessions today, In progress, Avg duration, Critical alerts (last 24h). Each is a `hud-frame` with icon + mono number + sub-line.
- **Recent sessions** table (latest 5): procedure_name, patient_code (last 4), `StatusBadge`, started_at, action → `/sessions/:id/console` or `/post-op`.
- Conditional **Admin panel** if `role === 'admin'`: 3 link cards → `/admin/users`, `/admin/audit`, `/admin/gpu`.

> **Unimplemented (target)**: refresh this page to match the HUD aesthetic — replace plain cards with `hud-frame` chrome, corner brackets, mono labels, animated stat counters, cyan accent gradients on the hero CTA, and a small "live theatre status" rail along the right edge showing each OR's current session/phase pulse-dot.

---

## 9. Sessions list & creation

### 9.1 `Sessions.tsx`
Filter chips (All / Scheduled / In Progress / Completed / Aborted). Search by patient_code or procedure. Same row layout as Dashboard's Recent table but paginated (20/page).

### 9.2 `NewSession.tsx`
`hud-frame` form, `react-hook-form + zod`:
- Procedure category (select: laparoscopic, open, robotic, endoscopic, other).
- Procedure name (text).
- Patient code (text; recommend hospital MRN suffix only).
- Theatre (select).
- Surgeon name, anaesthetist name.
- Initial mode (`silent` | `reactive` | `proactive`).
- Notes (textarea).
- **Mandatory CDS disclaimer checkbox** (red border until ticked) — disables Submit.

On submit: insert into `sessions`, audit-log the creation, navigate to `/sessions/:id/console`.

---

## 10. SessionConsole — the HUD (`src/pages/SessionConsole.tsx`)

This is the entire product, visually. **Single full-viewport route, no AppShell**.

### 10.1 Layout (CSS grid)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HEADER BAR (sticky)                                                       │
│  ARIA logo · session.procedure_name · pulse-dot live · phase · timer · mode│
│  [mute] [start/pause] [end (dialog)] [logout]                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  CdsBanner (always rendered, non-dismissable here)                         │
├──────────────────┬───────────────────────────────────┬──────────────────────┤
│                  │                                   │                      │
│  LEFT COL        │  CENTER COL (cameras + transcript) │  RIGHT COL           │
│  (panels.aria)   │  (panels.cameras + panels.transcript) │  (panels.vitals + alerts) │
│  ┌────────────┐  │  ┌─────────────────────────────┐   │  ┌────────────────┐  │
│  │  AriaOrb    │  │  │  CameraGrid (3 tiles)        │   │  │  VitalsBar     │  │
│  │  + VoiceHud │  │  │  (layout: grid|focus|cinema) │   │  │  HR SpO2 MAP   │  │
│  └────────────┘  │  └─────────────────────────────┘   │  │  ETCO2 + sparks│  │
│  ModeSwitcher   │  ┌─────────────────────────────┐   │  └────────────────┘  │
│  Director ctrls │  │  TranscriptStream            │   │  ┌────────────────┐  │
│  Phase chip     │  │  (autoscroll, mono labels)    │   │  │  AlertsPanel   │  │
│                  │  └─────────────────────────────┘   │  └────────────────┘  │
└──────────────────┴───────────────────────────────────┴──────────────────────┘
```

Grid: `grid-cols-[260px_1fr_340px] gap-3 p-3 h-[calc(100vh-headerH)]`.
Each cell wraps content in `.hud-frame.hud-corners` with `<span class="corner-tr"/><span class="corner-bl"/>`.

### 10.2 Layout presets (driven by `useDirector`)

| Preset | Behaviour |
|---|---|
| `grid` | Equal 3-camera grid (default) |
| `focus` | 1 large camera + 2 small stacked on right (2/3 + 1/3) |
| `cinema` | 1 hero camera fullscreen above center, 2 thumbs + a "LOCKED/AUX" placeholder below (3-up) |
| `vitals` | Hide cameras + transcript, vitals & alerts span full width |
| `transcript` | Hide cameras, transcript spans full width |

Layout transitions use `transition-all duration-350 ease-[cubic-bezier(0.65,0,0.35,1)]`.

### 10.3 Header HUD details

- Live timer: `T+MM:SS` mono, updates every 1s while `running`.
- Phase chip: `phaseAt(elapsed, alerts)` — preparation → access → dissection → resection → closure (overrides to `CRITICAL` while any unack critical alert exists). Color shifts the chip background.
- Pulse dot: `live` (success) when session running, `cyan` when paused, `critical` when there's an unack critical alert.

### 10.4 End-session dialog (shadcn `AlertDialog`)

Title "End session?" + body "All data will be persisted and the post-op summary will be generated." + secondary input for surgeon's free-text closure note → on confirm: update `sessions.status='completed'`, `ended_at=now()`, audit-log, route to `/sessions/:id/post-op`.

---

## 11. Console subcomponents

### 11.1 `AriaOrb` (`src/components/console/AriaOrb.tsx`)
- 160×160 cyan orb composed of:
  - Outer ring (border `primary/30`, `animate-hud-orbit`).
  - Mid ring (`primary/20`, `animate-hud-orbit-rev`).
  - Inner core: cyan radial gradient with `text-glow-strong`.
- 4 visual states (prop `state: "idle"|"listening"|"thinking"|"speaking"`):
  - `idle` → slow `animate-hud-pulse`.
  - `listening` → 5 vertical bars below orb animating with `animate-listening` staggered delays.
  - `thinking` → orbit speeds up 2×; small dot orbits the rim.
  - `speaking` → bigger glow-strong shadow + opacity flicker tied to TTS playback (driven by audio element `timeupdate`).

### 11.2 `VoiceHud` (`src/components/console/VoiceHud.tsx`)
- Compact strip under the orb showing:
  - `MIC ●` (success when active, muted when off, error if Web Speech unsupported).
  - Last interim transcript (mono, muted).
  - Last parsed intent chip (e.g. `intent: focus cam2`).
  - Wake-word hint: "Say *ARIA, focus laparoscope*".
- Toggles voice listening (`useVoiceControl().start/stop`).

### 11.3 `ModeSwitcher` (`src/components/console/ModeSwitcher.tsx`)
- Segmented control with 3 pills: **Silent** (mic-off icon), **Reactive** (radio icon), **Proactive** (radar icon).
- Active pill: cyan gradient + `text-glow`. Inactive: `border-border` muted.
- Tooltips explain behaviour. Calls `onModeChange(mode)` (which updates `sessions.current_mode` + audit logs + emits `control` message to relay).

### 11.4 `CameraGrid` (`src/components/console/CameraGrid.tsx`)
3 fixed cameras: `cam1=LAPAROSCOPE`, `cam2=OVERHEAD`, `cam3=PATIENT (anaesthesia monitor)`.

Each `CameraTile`:
- `aspect-video` `hud-frame.hud-corners` with `<span class="corner-tr"/><span class="corner-bl"/>`.
- Background: `bg-black hud-grid`.
- If `handle.stream` (MediaStream) present: `<video autoPlay muted playsInline className="opacity-90 object-cover"/>`.
- Else: animated holographic placeholder — two counter-rotating concentric rings + central `Camera` icon.
- `.hud-sweep` overlay (the cyan beam).
- Vignette: `bg-gradient-to-t from-black/70 via-transparent to-black/30`.
- Top-left HUD label: `pulse-dot` (live when streaming) + `cam1 · LAPAROSCOPE` mono.
- Top-right status: `syncing… | ● live | offline | standby`.
- Bottom bar: detail string (`Surgical view · 1080p`) + `FOCUS / TAP` indicator with Maximize/Minimize icon.
- Click → `setFocus(camera)` and (in `dynamic`/`agentic` mode) bumps layout to `focus` if currently `grid`.

`connectCamera(id)` (from `src/lib/webrtc.ts`) returns `{ id, stream | null, close() }`. Default v1 returns `{stream:null}` (placeholder); a `SOURCE_OVERRIDES` map allows per-camera `webcam` (uses `getUserMedia`) or `webrtc` (TODO — negotiated through `aria-realtime`).

Renders by layout preset:
- `grid` → 3-up.
- `focus` → 2/3 hero + 1/3 stacked thumbs.
- `cinema` → big hero on top + 3 small slots (2 cams + 1 "LOCKED/AUX" placeholder showing a `Lock` icon when `layoutLocked`).

Also exports `CameraGridStatus` — a tiny mono caption "VISION · GRID · FOCUS CAM1" used in headers.

### 11.5 `TranscriptStream` (`src/components/console/TranscriptStream.tsx`)
- Auto-scrolls to bottom on new lines.
- Each line: speaker label (uppercase mono, color-coded: surgeon=foreground, anaesthetist=info, nurse=success, ARIA=primary, system=muted) + `T+MM:SS` timestamp + body text.
- ARIA lines append a tiny `ShieldCheck` + `CDS_DISCLAIMER_SHORT` line under the body.
- Empty state: centered "Waiting for the first utterance…".
- Animation: `.animate-fade-in` per line.

> **Unimplemented (target)**: PHI redaction visual — wrap detected PHI spans in `<mark class="bg-warning/20 text-warning-foreground rounded px-1">[REDACTED]</mark>`. Frontend reads `redacted: true` and `piiSpans: number[][]` from the transcript event (Morpheus shape) and renders the masked spans. If `redacted=true` and no spans provided, replace whole body with `▌ [PHI redacted by Morpheus] ▌`.

### 11.6 `VitalsBar` (`src/components/console/VitalsBar.tsx`)
4 stat cards in a row: HR, SpO2, MAP, ETCO2.
- Big mono number with unit subscript.
- 60-sample sparkline (inline SVG polyline, cyan stroke, glow).
- Color shifts to `caution`/`warning`/`critical` when crossing clinical thresholds:
  - HR: <50 caution / <40 warning; >120 caution / >140 warning.
  - SpO2: <94 caution / <90 warning / <85 critical.
  - MAP: <65 caution / <55 warning.
  - ETCO2: <30 or >50 caution.
- Underneath: thin progress bars showing each value vs its safe band.

### 11.7 `AlertsPanel` (`src/components/console/AlertsPanel.tsx`)
- Vertical scroll list of cards. Each card:
  - Severity icon + ring color (`info=Info`, `caution=Bell`, `warning=AlertTriangle`, `critical=AlertOctagon`).
  - Title (semibold) + body (1–2 lines) + source chip (`vitals|vision|protocol|audio`) + `T+MM:SS`.
  - "Acknowledge" button (only when `!acknowledged`).
- Empty state "No active alerts." (calm, not muted).
- Critical alerts get `shadow-critical` and a slow pulsing border.

---

## 12. The UI Director (Zustand) — `src/lib/director.ts`

The agent's "hands on the UI". A single Zustand store everything subscribes to.

```ts
type ControlMode = "conservative" | "dynamic" | "agentic";
type LayoutPreset = "grid" | "focus" | "cinema" | "vitals" | "transcript";
type CameraId = "cam1" | "cam2" | "cam3";

state: {
  layout: LayoutPreset;            // default "grid"
  focusedCamera: CameraId;         // default "cam1"
  panels: { transcript, vitals, alerts, cameras, aria: boolean };  // all true
  controlMode: ControlMode;        // default "dynamic"
  voiceListening: boolean;
  lastIntent: string | null;
  layoutLocked: boolean;           // surgeon override — freezes ARIA's hands
  phase: string;                   // e.g. "preparation"
}

actions: setLayout, setFocus, togglePanel, setPanel, setControlMode,
         setVoiceListening, setLastIntent, setLayoutLocked, setPhase,
         applyDirective(d), reset()

type Directive =
  | { kind: "layout"; layout }
  | { kind: "focus";  camera }
  | { kind: "panel";  panel; show }
  | { kind: "phase";  phase };
```

**`applyDirective` policy** (the safety gate):
1. If `controlMode === "conservative"` and directive is `layout|focus|panel` → **reject** (return false).
2. If `layoutLocked` and directive ≠ `phase` → **reject**.
3. Otherwise apply and return true.

The 3 modes mean:
- **conservative** — voice can only switch mode, mute/unmute, ack alerts, end session.
- **dynamic** — voice can additionally rearrange layout, focus cameras, hide chrome.
- **agentic** — ARIA additionally pushes layout decisions on its own based on procedure phase + alert severity.

**Agentic phase→layout rules** (called from the alert/phase handlers):
- New `critical` alert → `applyDirective({kind:"layout", layout:"cinema"})` + `focus` to the camera tied to the alert source (or `cam1`).
- Phase = `closure` → switch to `transcript` layout to show the post-op handoff.
- All criticals acked → revert to `grid`.

---

## 13. Voice Control — `src/hooks/useVoiceControl.ts`

Wraps `webkitSpeechRecognition` (Chrome/Edge). Continuous, interim results enabled, `lang: "en-US"`.

**Wake-word required**: only commands containing `aria` (regex `/\b(hey )?aria\b/i`) are dispatched. Strip the wake word, then `parseIntent(rest)`.

**Intent grammar** (regex per intent):
| Phrase | Intent |
|---|---|
| `silent`, `silence`, `mute mode` | `mode = silent` |
| `reactive`, `standby` | `mode = reactive` |
| `proactive`, `alert mode`, `active` | `mode = proactive` |
| `focus camera 1`, `focus laparoscope`, `focus laparo` | `focus cam1` |
| `focus camera 2`, `focus overhead` | `focus cam2` |
| `focus camera 3`, `focus patient`, `focus monitor` | `focus cam3` |
| `zoom`, `fullscreen`, `cinema` | `layout cinema` |
| `grid`, `all cameras`, `tile` | `layout grid` |
| `focus mode`, `main view` | `layout focus` |
| `vitals only` | `layout vitals` |
| `transcript only` | `layout transcript` |
| `show/hide vitals|transcript|alerts|cameras` | `panel <p> <show>` |
| `mute` / `unmute` | `mute` / `unmute` |
| `ack`, `acknowledge` | `ack` (acks latest unack alert) |
| `end session`, `stop session`, `end procedure` | `end` |
| `lock layout` / `unlock layout` | `lock` / `unlock` |

Auto-restart on `onend` + `onerror` if still active. Cleans up on unmount via `useEffect` return.

API: `{ supported, active, transcript, start, stop }`. The hook also takes `handlers: { onMute, onUnmute, onAckLatest, onEnd, onModeChange, onIntent }` — non-Director intents are routed back to the page.

---

## 14. Voice Output — `src/hooks/useAriaVoice.ts`

Plays ARIA's spoken responses. Strategy:
1. Try edge function `aria-tts` (POST `{ text, voice: "alloy" }`) → returns `{ audioBase64, mimeType }`.
2. Decode → blob → `<audio>` element → `play()`. Sets orb state `speaking` while playing.
3. **Fallback**: `window.speechSynthesis` (`SpeechSynthesisUtterance`) with voice "Google US English" or first available `en-` voice, rate 1.0, pitch 1.0.
4. `mute()` immediately stops audio + cancels synthesis.
5. Queue: incoming `say(text)` while another is playing is queued; `flush()` clears.

Hook returns `{ say, flush, mute, isSpeaking, isMuted, setMuted }`.

---

## 15. The Demo Stream — `src/lib/demo-session.ts` + `src/lib/aria-stream.ts`

The frontend ships with a fully-scripted **5-minute laparoscopic cholecystectomy** so the entire HUD works without a backend.

**Event types** (mirrored to the GPU `ServerEvent` shape):
- `transcript` — speaker, text, at (seconds), `redacted?`, `piiSpans?`.
- `alert` — severity, title, body, source, at.
- `vitals` — hr, spo2, map, etco2, at.
- `phase` — phase, confidence, at.
- `vision` — camera, detections (label, score, bbox), at.

`vitalsAt(t)` is a deterministic sine-based generator (HR baseline 78 ± 6, SpO2 99 ± 1, MAP 82 ± 5, ETCO2 36 ± 3) — guarantees natural drift even between scripted events.

`useScriptedSession({ running, mode, handlers })`:
- 1-second `setInterval` while `running`.
- Each tick: `elapsed++`, fire `onTick(elapsed)`, fire `onVitals(vitalsAt(elapsed))`, then drain any DEMO_EVENTS whose `at <= elapsed`.
- Mode filter: in `silent` only `transcript` of speaker `aria` is suppressed; in `reactive`, alerts only fire if user-triggered; in `proactive`, all alerts fire.
- At `DEMO_DURATION (360)` calls `onComplete()` and stops.

The hook is the single source of truth — swapping it for a real WebSocket source (`aria-realtime`) is a one-line change in `SessionConsole`.

---

## 16. Realtime / GPU adapter (frontend side) — `src/lib/gpu-adapter.ts` + `src/lib/webrtc.ts`

The frontend codes against **typed contracts**, no live network until creds are added.

### 16.1 Wire protocol

```ts
ClientMessage =
  | { type: "auth"; token; sessionId }
  | { type: "audio"; codec: "opus"|"pcm16"; data: base64; ts }
  | { type: "video_frame"; camera: cam1|cam2|cam3; data: base64; ts }
  | { type: "control"; mode: silent|reactive|proactive }
  | { type: "ping"; ts };

ServerEvent =
  | { type: "transcript"; speaker; text; at; redacted?; piiSpans? }
  | { type: "alert"; severity; title; body; source; at; cite? }
  | { type: "vitals"; hr; spo2; map; etco2; at }
  | { type: "phase"; phase; confidence; at }
  | { type: "vision"; camera; detections[]; at }
  | { type: "tts"; audioBase64; mimeType; at }
  | { type: "pong"; ts }
  | { type: "error"; code; message };
```

### 16.2 Hosting presets shown in `/admin/gpu`

Lightning AI · RunPod · Self-hosted (NIM) · Demo. Each has env-var hint, recommended GPU SKU, console URL, expected endpoint shape, and `healthCheckPath`.

### 16.3 `webrtc.ts`

`connectCamera(id): Promise<{id, stream|null, close()}>`:
1. Default `placeholder` source → `{stream:null}`.
2. `webcam` source → `getUserMedia({video:{1280x720}, audio:false})`.
3. `webrtc` source → **TODO** (negotiates via `aria-realtime`).

> **Unimplemented (target)**: per-tile source toggle UI in `CameraGrid` — small dropdown in each tile's bottom-bar to pick `placeholder | webcam | demo loop | webrtc`. Persist in `localStorage` per-camera. For "demo loop", use `<video src="/demo-cam{1|2|3}.mp4" loop muted autoPlay>` — three placeholder MP4s in `public/`.

> **Unimplemented (target)**: actual WebRTC negotiation — `RTCPeerConnection` with STUN, signal SDP through the `aria-realtime` WebSocket using `{type:"webrtc_offer", camera, sdp}` / `{type:"webrtc_answer", sdp}`, attach `pc.ontrack` to the tile's video element.

---

## 17. Admin pages

### 17.1 `/admin/users` (`AdminUsers.tsx`)
Table of users (joined from `profiles` + `user_roles`):
- Columns: avatar, full_name, email, hospital, title, role, signed-up.
- Role select per row → updates `user_roles` (admin-only RLS).
- Invite form (email + role) — calls a future edge function (frontend wires the form, button shows toast "Invitation sent").

### 17.2 `/admin/audit` (`AdminAudit.tsx`)
Append-only log table (`audit_log`):
- Columns: time, actor email, action, session, details (truncated JSON, expandable).
- Filters: action type, date range, actor.
- Export CSV button.

### 17.3 `/admin/gpu` (`AdminGpu.tsx`)
Live backend health & configuration:
- Card row showing `mode` (`live` | `demo`), `host`, `hasUrl`, `hasToken` — pulled from `aria-realtime/health` GET.
- Big preset selector (Lightning / RunPod / Self-hosted / Demo) — each card shows recommended GPU, env vars to set, endpoint shape.
- "Test connection" button → opens a WS to `aria-realtime`, waits for `error code:demo_mode` or successful `auth_ok`, displays `success | demo | error`.
- Module legend: Riva / NeMo / Morpheus / Triton / Guardrails — each with status dot.

---

## 18. Post-Op (`src/pages/PostOp.tsx`) + PDF export (`src/lib/post-op-pdf.ts`)

After a session ends:
- Header: procedure, patient code, surgeon, anaesthetist, theatre, started/ended timestamps, total duration.
- Summary cards: alerts by severity (counts), CDS interactions, mode distribution timeline.
- Full transcript (collapsible).
- Alerts list (chronological).
- Surgeon's free-text closure note (editable until "Sign-off").
- Big buttons: **Download PDF**, **Sign off**, **Email to me**.

`postOpPdf(session, transcript, alerts)`:
- jsPDF A4, 2 pages min.
- Header with ARIA logo (vector), procedure + patient.
- Footer on every page: `CDS_DISCLAIMER_LONG` (8pt) + page no.
- Section 1: meta table (autoTable).
- Section 2: alerts (autoTable, severity-colored badge cell).
- Section 3: transcript (autoTable with wrap, `at` left col).
- Final page: signature line + "Generated by ARIA · timestamp".

---

## 19. CDS — `src/lib/cds.ts`

Two strings + one helper:

```ts
export const CDS_DISCLAIMER_SHORT =
  "Decision support only. Not a substitute for clinical judgement.";

export const CDS_DISCLAIMER_LONG =
  "ARIA is a clinical decision-support tool. All outputs are advisory and " +
  "must be independently verified by the responsible clinician. ARIA is " +
  "not a medical device under MDR/FDA. Do not rely on ARIA as the sole " +
  "basis for any clinical decision.";

export function withCdsFooter(text: string): string;  // appends short variant to TTS strings
```

Rules (enforced in code):
- Every ARIA transcript line in `TranscriptStream` must render the short disclaimer.
- Every TTS string sent to `useAriaVoice.say()` must pass through `withCdsFooter()` for the first utterance per session, then again every 60s.
- Every PDF must include the long disclaimer in its footer.
- The CdsBanner must be permanently rendered on `SessionConsole`.

---

## 20. Audit logging — `src/lib/audit.ts`

`logAudit({ action, sessionId?, details? })` — inserts into `audit_log`. Called for:
- session.created / started / paused / resumed / ended / aborted
- session.mode_changed (with from/to)
- alert.acknowledged
- transcript.exported
- pdf.generated
- voice.intent (only when `controlMode === "agentic"`)
- admin.role_changed

All inserts include `actor_id`, `actor_email`, `created_at` (server default).

---

## 21. State, errors, accessibility

- All async fetches use `useQuery`; show `Skeleton` shimmer (not spinners) while loading.
- Realtime subscriptions: Supabase `channel().on('postgres_changes', ...)` for `alerts` and `transcripts` filtered by `session_id`. Unsubscribe on unmount.
- Errors → `toast` (sonner) with severity color; never block the HUD with a modal during an active session.
- Keyboard: `Cmd/Ctrl+M` toggles mute, `Cmd/Ctrl+L` toggles `layoutLocked`, `Cmd/Ctrl+1/2/3` focuses cameras, `Esc` closes any drawer/dialog.
- Focus rings honor `--ring`. Tab order through HUD cells: header → orb → mode → camera grid → transcript → vitals → alerts.
- Screen-reader: every `pulse-dot` has `<span class="sr-only">{status}</span>`; transcript region is `aria-live="polite"`; alerts region is `aria-live="assertive"`.
- Reduced-motion: respect `prefers-reduced-motion`; replace `hud-sweep`, `hud-orbit`, `aria-pulse` with static states.
- All toasts auto-dismiss in 4s except critical alerts (sticky until acked).

---

## 22. File tree (frontend only)

```
src/
├── App.tsx                          # routes + providers
├── main.tsx
├── index.css                        # design system (HSL tokens, HUD primitives, keyframes)
├── App.css
├── assets/
│   └── hero-hud.jpg                 # generated holographic OR HUD hero
├── components/
│   ├── AppShell.tsx
│   ├── AriaLogo.tsx
│   ├── CdsBanner.tsx
│   ├── NavLink.tsx
│   ├── ProtectedRoute.tsx
│   ├── console/
│   │   ├── AlertsPanel.tsx
│   │   ├── AriaOrb.tsx
│   │   ├── CameraGrid.tsx
│   │   ├── ModeSwitcher.tsx
│   │   ├── TranscriptStream.tsx
│   │   ├── VitalsBar.tsx
│   │   ├── VoiceHud.tsx
│   │   └── OperatorOverrideDrawer.tsx        # ← unimplemented (see §23)
│   └── ui/                          # shadcn primitives (full set)
├── contexts/
│   └── AuthContext.tsx
├── hooks/
│   ├── useAriaVoice.ts
│   ├── useVoiceControl.ts
│   ├── use-mobile.tsx
│   └── use-toast.ts
├── lib/
│   ├── aria-stream.ts               # useScriptedSession()
│   ├── audit.ts
│   ├── cds.ts
│   ├── demo-session.ts              # DEMO_EVENTS, DEMO_DURATION, vitalsAt()
│   ├── director.ts                  # Zustand UI Director
│   ├── gpu-adapter.ts               # GPU contracts + presets
│   ├── post-op-pdf.ts               # jsPDF generator
│   ├── webrtc.ts                    # connectCamera()
│   └── utils.ts                     # cn()
├── pages/
│   ├── Auth.tsx
│   ├── Dashboard.tsx
│   ├── Index.tsx
│   ├── NewSession.tsx
│   ├── NotFound.tsx
│   ├── PostOp.tsx
│   ├── SessionConsole.tsx
│   ├── Sessions.tsx
│   └── admin/
│       ├── AdminAudit.tsx
│       ├── AdminGpu.tsx
│       └── AdminUsers.tsx
├── integrations/supabase/
│   ├── client.ts                    # auto-generated; do NOT edit
│   └── types.ts                     # auto-generated; do NOT edit
└── test/
    ├── example.test.ts
    └── setup.ts
public/
  ├── favicon.svg
  ├── robots.txt
  ├── demo-cam1.mp4                  # ← unimplemented placeholders
  ├── demo-cam2.mp4
  └── demo-cam3.mp4
index.html                           # title, meta, viewport, theme-color #03060a
```

---

## 23. Unimplemented specs (build these)

These are explicitly part of the v1 frontend target. Implement them to complete the spec.

### 23.1 Operator Override Drawer (`OperatorOverrideDrawer.tsx`)
A hidden, demo/pitch-time tool inside `SessionConsole`.

- Open/close: **`Cmd/Ctrl+K`** (also a tiny ghost button in the header revealed by `Alt`).
- shadcn `Drawer` from the right, 420px wide, `hud-frame` styling, semi-transparent backdrop.
- Tabs: **Inject Transcript** | **Inject Alert** | **Set Phase** | **Force Layout** | **Replay Event**.
- **Inject Transcript**: speaker select (surgeon/anaesthetist/nurse/aria/system) + textarea + "Inject" → calls `handlers.onTranscript({...synthetic, at: currentElapsed})`. Optional `redacted` checkbox to test PHI rendering.
- **Inject Alert**: severity, title, body, source, optional `cite` → `handlers.onAlert(...)`. Optional "Trigger agentic camera focus" toggles `applyDirective` to `cinema`.
- **Set Phase**: free text or preset chips → `director.setPhase` + `applyDirective({kind:"phase", phase})`.
- **Force Layout**: 5 layout buttons → `director.applyDirective({kind:"layout",...})`. Also exposes `Lock layout` toggle.
- **Replay Event**: lists `DEMO_EVENTS`, click any to re-fire it now.
- Audit-logs every action with `details: { source: "operator_override" }` so the demo history is honest.
- **Hide entirely** in production builds — gate on `import.meta.env.MODE !== "production"` OR feature flag in `localStorage["aria.operatorOverride"] === "1"`.

### 23.2 Per-camera webcam toggle (in `CameraGrid`)
Already detailed in §16.3. Spec recap:
- Each tile's bottom-bar gets a small `DropdownMenu` (gear icon).
- Options: `Placeholder` · `Device webcam` · `Demo loop` · `WebRTC remote`.
- Persist per-cam in `localStorage["aria.cam.<id>.source"]`.
- For `Device webcam`, list available `enumerateDevices()` and let user pick.
- For `Demo loop`, render `<video src="/demo-cam{n}.mp4" loop muted autoPlay playsInline>` instead of MediaStream.
- Show a tiny "PERMISSION REQUIRED" CTA if webcam is denied.

### 23.3 Actual WebRTC negotiation
- New helper `negotiateWebRTC(cameraId, ws)`:
  - `pc = new RTCPeerConnection({ iceServers: [{ urls: "stun:stun.l.google.com:19302" }] })`
  - `pc.addTransceiver("video", { direction: "recvonly" })`
  - Send `{ type:"webrtc_offer", camera, sdp: offer }` over the existing `aria-realtime` WS.
  - On `{ type:"webrtc_answer", sdp }` → `pc.setRemoteDescription`.
  - Trickle ICE: `pc.onicecandidate` → send `{ type:"webrtc_ice", camera, candidate }`.
  - `pc.ontrack` → set `tile.video.srcObject = event.streams[0]`.
- Reconnect strategy: if `iceConnectionState === "failed"`, exponential backoff (1s, 2s, 4s, max 10s).

### 23.4 Mock GPU edge function for end-to-end demo
Frontend side: a `useRealtimeStream({ url, token, sessionId })` hook that mirrors `useScriptedSession`'s callbacks (`onTranscript`, `onAlert`, `onVitals`, `onPhase`, `onVision`, `onComplete`).

- On mount: open WS to `aria-realtime`.
- Emit `{type:"auth", token, sessionId}` then `{type:"control", mode}`.
- On `error code:demo_mode` → fall back to `useScriptedSession` (no UI change).
- On any `ServerEvent` → fan out to handlers.
- 15s heartbeat ping.
- Auto-reconnect with backoff; toast "ARIA backend reconnecting…" only after 2 failures.
- The backend mock function returns the SAME `DEMO_EVENTS` shape as `aria-stream.ts` so the frontend cannot tell whether it's local or remote — that's the point.

### 23.5 Morpheus-shape PHI redaction in the demo transcript
- Extend `DemoTranscriptEvent` with optional `redacted: boolean`, `piiSpans: number[][]`.
- Add 2–3 events in `DEMO_EVENTS` where the surgeon/anaesthetist mentions a name or DOB and the event is pre-flagged `redacted:true` with `piiSpans:[[start,end]]`.
- `TranscriptStream` renders these spans as `<mark>` blocks (cyan-warning, mono "[REDACTED]") OR if no spans, full-line replacement `▌ [PHI redacted by Morpheus] ▌`.
- Add a tiny legend chip above the transcript: `🛡 PHI auto-redacted` (cyan) explaining the masking.
- Audit-log every redaction event with `action:"phi.redacted"`.

### 23.6 Dashboard refresh to match HUD
- Replace plain cards with `hud-frame.hud-corners` panels.
- Greeting card: cyan radial glow background, large `text-display` name, mono role+hospital strip.
- Stat cards: animate the number on mount (count-up), mono labels, sparkline mini-chart in each.
- "Recent sessions" → mono table with status pulse-dot, hover row reveals a thin glow ring + chevron.
- Right rail (240px on `lg+`): "Live theatres" — one row per theatre with pulse-dot + procedure + elapsed timer (subscribed to `sessions` realtime).
- Admin panel cards become `hud-frame` tiles with corner brackets.
- Hero CTA "Start a new session" gets `bg-gradient-primary shadow-glow-strong text-glow` and a cyan sweep on hover.

---

## 24. Acceptance criteria

A reviewer can sign off this frontend when, **with no backend wiring beyond the demo stream**:

1. `/` renders the holographic landing with hero image and CDS strip.
2. `/auth` lets you sign up & sign in (email/password); 3 roles selectable.
3. `/dashboard` shows the greeting, CTA, stats, recent sessions, and admin panel for admins.
4. `/sessions/new` validates and creates a session, audit-logs it, navigates to console.
5. `/sessions/:id/console` renders the full HUD with header, ARIA orb, mode switcher, 3-camera grid (holographic placeholders), transcript, vitals, alerts.
6. Pressing **Start** runs the 5-min scripted session: transcript scrolls, vitals drift, alerts fire, ARIA TTS speaks (with CDS suffix), orb animates state changes.
7. Saying **"ARIA, focus laparoscope"** focuses cam1; **"ARIA, cinema"** switches layout; **"ARIA, mute"** mutes; **"ARIA, acknowledge"** acks the latest alert.
8. **Lock layout** freezes ARIA's hands; flipping to **conservative** mode also blocks layout/focus voice intents.
9. Critical alerts get the critical shadow + override the phase chip; in `agentic` mode they auto-switch layout to `cinema`.
10. **End session** dialog persists, navigates to `/sessions/:id/post-op`, generates downloadable PDF with CDS footer.
11. `/admin/gpu` reports `mode: demo` until env vars are set, then `mode: live`.
12. Operator override drawer (Cmd+K) injects synthetic events.
13. Per-camera source toggle works (placeholder / webcam / demo loop / webrtc-stub).
14. PHI-flagged transcript lines render with `[REDACTED]` masks.
15. Dashboard wears full HUD chrome.

---

## 25. Build & run

```bash
bun install          # or npm install
bun run dev          # vite dev server
bun run build        # production build
bun run preview      # preview built bundle
```

Env vars (frontend reads only `VITE_*`; everything else is backend-side):
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY`
- `VITE_SUPABASE_PROJECT_ID`

`index.html`: set `<title>ARIA · Surgical Copilot</title>`, meta description, `<meta name="theme-color" content="#03060a">`, `<link rel="icon" href="/favicon.svg">`. Single `<h1>` per route.

---

*End of frontend spec.*
