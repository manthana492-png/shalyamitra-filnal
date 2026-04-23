# ShalyaMitra — Theatre Display Frontend Design Specification

## Version 3.0 — Production-Ready UI/UX Architecture

> *The most advanced surgical intelligence interface ever designed. Not a dashboard. Not a monitor. A living, breathing visual consciousness that moves with the surgery.*

---

## 1. Design Philosophy — The JARVIS Principle

ShalyaMitra's Theatre Display is not a conventional medical UI. It is a **dynamic intelligence surface** — one that thinks, rearranges, anticipates, and responds in real time to the surgery happening in front of it.

### The Three Laws of the Theatre Display

**Law 1 — The surgeon never looks for information. Information finds the surgeon.**
Every element on screen appears because the AI determined it should be there at this moment. The surgeon glances. The answer is already waiting. If the surgeon must search, scan, or navigate — the UI has failed.

**Law 2 — The screen is a living organism, not a fixed layout.**
There are no static dashboards. No permanent panels. No fixed grids. The layout morphs continuously — expanding what matters, collapsing what doesn't, animating transitions so the surgeon's spatial memory is never violated. The screen breathes with the surgery.

**Law 3 — Darkness is the canvas. Light is the signal.**
The OR is a visually demanding environment. The display must never compete with the surgical field for the surgeon's attention. The background is absolute black. Every pixel of light on screen carries information. Nothing decorates. Nothing distracts. Nothing glows without purpose.

---

## 2. Design System — "Nael Dark"

### 2.1 Colour Palette

```
BACKGROUND & SURFACES
──────────────────────
Base Black:           #000000  (true black — OLED optimised)
Surface Level 1:      #0A0A0F  (card backgrounds)
Surface Level 2:      #12121A  (elevated panels)
Surface Level 3:      #1A1A25  (modal/overlay backgrounds)
Glass Surface:        rgba(15, 15, 25, 0.85) + backdrop-blur(20px)

PRIMARY ACCENT — "Nael Blue"
──────────────────────────────
Nael Blue 100:        #E0F0FF  (text on dark)
Nael Blue 300:        #7EB8FF  (secondary elements)
Nael Blue 500:        #3D8BFF  (primary interactive)
Nael Blue 700:        #1A5FCC  (borders, outlines)
Nael Blue Glow:       rgba(61, 139, 255, 0.15)  (ambient glow behind active elements)

INTELLIGENCE VOICE COLOURS — Each pillar has a unique accent
─────────────────────────────────────────────────────────────

[ignoring loop detection]

# ShalyaMitra — Theatre Display Frontend Design Specification
### Version 3.0 — Production-Ready UI/UX Architecture

> *Not a dashboard. Not a monitor. A living visual consciousness that moves with the surgery.*

---

## 1. Design Philosophy — The JARVIS Principle

ShalyaMitra's Theatre Display is a **dynamic intelligence surface** that thinks, rearranges, anticipates, and responds in real time. Three laws govern every pixel:

**Law 1 — Information finds the surgeon.** Every element appears because the AI determined it should be there NOW. If the surgeon must search or navigate, the UI has failed.

**Law 2 — The screen is a living organism.** No static dashboards. No permanent panels. The layout morphs continuously — expanding what matters, collapsing what doesn't, animating transitions so the surgeon's spatial memory is never broken.

**Law 3 — Darkness is canvas. Light is signal.** True black background (#000000). Every pixel of light carries meaning. Nothing decorates. Nothing glows without purpose. The OR is visually demanding — the display must never compete with the surgical field.

---

## 2. Design System — "Nael Dark"

### 2.1 Colour Architecture

**Surfaces:**
- Base Black: `#000000` (true black, OLED-optimised for Smart TV)
- Surface 1: `#0A0A0F` (card backgrounds)
- Surface 2: `#12121A` (elevated panels)
- Glass: `rgba(15, 15, 25, 0.85)` + `backdrop-blur(20px)` (glassmorphic overlays)

**Primary Accent — "Nael Blue":**
- Primary: `#3D8BFF` (interactive elements, Nael's identity colour)
- Light: `#7EB8FF` (secondary text, borders)
- Glow: `rgba(61, 139, 255, 0.15)` (ambient halo behind active elements)

**Intelligence Pillar Colours** — Each intelligence has a signature colour so the surgeon INSTANTLY knows which AI is speaking/displaying, without reading a label:

| Intelligence | Colour | Hex | Rationale |
|---|---|---|---|
| Nael (The Voice) | Cool Blue | `#3D8BFF` | Calm, trustworthy, primary |
| Haemorrhage Sentinel | Arterial Red | `#FF3B4A` | Universally signals bleeding danger |
| Monitor Sentinel | Amber/Gold | `#FFB020` | Warning, physiological attention |
| The Sentinel (Overhead) | Teal | `#20D9B0` | Environmental, spatial awareness |
| The Pharmacist | Violet | `#A855F7` | Distinct from surgical colours, pharmaceutical |
| The Scholar | Warm White | `#F5E6D3` | Pre-operative knowledge, paper-like |
| The Oracle | Saffron/Gold | `#FF9F1C` | Classical Indian tradition, sacred |
| Devil's Advocate | Crimson-Orange | `#FF6B35` | Urgency with caution, not panic |
| The Chronicler | Silver | `#B0B8C8` | Documentation, neutral recording |

**Why this matters:** When a vital alert flashes with an amber border and amber glow, the surgeon doesn't read "Monitor Sentinel" — their peripheral vision registers AMBER and they know it's a physiological alert. When saffron text appears, it's the Oracle. This is **pre-attentive processing** — the UI communicates before conscious reading.

**Alert Severity Tiers:**
- Tier 1 CRITICAL: Full-screen pulse + colour flood + audio. Red/amber border animation.
- Tier 2 WARNING: Panel highlight + gentle pulse + audio tone. Coloured border only.
- Tier 3 INFO: Subtle corner indicator + optional audio chime. Dot indicator.

### 2.2 Typography

**Font Stack:** `Inter` (primary), `JetBrains Mono` (data/numbers), `Noto Sans Devanagari` (shlokas)

| Use Case | Font | Weight | Size | Tracking |
|---|---|---|---|---|
| Vital values (large) | JetBrains Mono | 700 | 72–96px | +2% |
| Alert messages | Inter | 600 | 28–36px | +1% |
| Panel headings | Inter | 500 | 20–24px | +3% |
| Body text / explanations | Inter | 400 | 16–18px | 0 |
| Data labels (small) | Inter | 500 | 12–14px | +5% (uppercase) |
| Shlokas (Devanagari) | Noto Sans Devanagari | 500 | 24–32px | 0 |
| Shloka transliteration | Inter | 400 italic | 18px | +1% |
| Timer / countdowns | JetBrains Mono | 700 | 48–64px | +3% |

**Readability rules:**
- Minimum font size anywhere on screen: 14px (visible from 3 metres at the operating table)
- Critical values (HR, BP, SpO₂): 72px minimum — readable from across the OR
- Maximum 60 characters per line for any running text
- Line height: 1.5 for body text, 1.2 for data/numbers

### 2.3 Spacing & Grid

The layout uses a **fluid 12-column grid** with 24px gutters on a 1920×1080 canvas (standard 55" Smart TV). All spacing follows an 8px base unit: 8, 16, 24, 32, 48, 64, 96.

**Safe zones:** 48px margin from all screen edges — content never touches the TV bezel.

### 2.4 Micro-Animations

Every transition in ShalyaMitra uses physics-based easing, never linear. The UI must feel alive and fluid, never jerky.

- **Panel expand/collapse:** 400ms, `cubic-bezier(0.16, 1, 0.3, 1)` — fast start, gentle land
- **Element fade in:** 250ms ease-out with 10px Y-translate (slides up into place)
- **Alert pulse:** Infinite `ease-in-out` glow animation, 1.5s period, on the pillar's accent colour
- **Camera transition (expand/collapse):** 500ms spring animation with slight overshoot
- **Data value change:** Number counter animation (old → new, 200ms) — values never jump, they transition
- **Vital trend arrows:** Smooth rotation transition when trend direction changes
- **Screen state transitions:** 600ms cross-fade between major layout states

**The Nael Listening Indicator:** When the surgeon says "Nael" and the system is listening, a subtle circular waveform animation appears — concentric rings pulsing outward from a small Nael icon in the corner. Cool blue. Gentle. Present but not demanding. Disappears when Nael finishes responding.

---

## 3. The Adaptive Layout Engine — How the Screen Thinks

This is what makes ShalyaMitra's display fundamentally different from every medical UI ever built. **The layout is not designed by a developer and rendered statically. The layout is computed by the AI in real time and rendered dynamically based on surgical context.**

### 3.1 Layout States

The display has **7 primary layout states**, and the AI switches between them automatically based on what's happening in the surgery. The surgeon can also command any state by voice.

---

#### STATE 1: "Theatre Overview" — Default Surveillance Mode

*When:* Surgery is stable, no active alerts, no active query. This is the resting state.

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │  SURGEON    │  │  OVERHEAD   │  │  MONITOR    │   ⏱ 01:23:45    │
│  │  CAMERA     │  │  CAMERA     │  │  CAMERA     │   Phase: Dissect │
│  │  (live)     │  │  (live)     │  │  (live)     │                  │
│  │             │  │             │  │             │   ● Nael Ready   │
│  │  480×270    │  │  480×270    │  │  480×270    │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
│                                                                      │
│  ┌──── VITALS (compact) ──────────────────────────────────────────┐  │
│  │  HR: 76 ↔   BP: 118/72 ↔   SpO₂: 99% ↔   EtCO₂: 35 ↔       │  │
│  │  Temp: 36.4°C   RR: 14   MAC: 1.1                             │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌── INSTRUMENTS ──┐  ┌── PHARMACIST ──┐  ┌── TIMELINE ──────────┐  │
│  │ 🔧 14/14 ✓     │  │ Propofol: ███  │  │ ──●──●──●──●──●──── │  │
│  │ 🧹 6/6  ✓      │  │ Remi: ████     │  │ Inc  Dissect  ...    │  │
│  └─────────────────┘  └────────────────┘  └──────────────────────┘  │
│                                                                      │
│  ░░░░░░░░░░░░░░░░░░░░░  Nael idle  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
└──────────────────────────────────────────────────────────────────────┘
```

**Details:**
- Three camera feeds side by side, equal size (16:9, ~480×270px each)
- Compact vitals bar below cameras — all values in one horizontal line with trend arrows (↑ ↗ → ↘ ↓)
- Bottom row: Instrument count (green checkmark = matched), Pharmacist mini-bar (propofol/remi plasma concentration as progress bars), and surgical timeline
- Top-right corner: Surgery timer, current surgical phase (auto-detected by the Eye), and Nael status indicator
- Everything in muted tones — nothing screams for attention

---

#### STATE 2: "Surgeon Focus" — Single Camera Expanded

*When:* Surgeon says "Nael, expand surgical camera" or "Nael, full screen surgeon view"

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │                                                            │ OVH  │
│  │                                                            │ ┌──┐ │
│  │              SURGEON CAMERA — FULL                         │ │  │ │
│  │              (1920×1080 or 1280×720)                       │ └──┘ │
│  │                                                            │ MON  │
│  │                                                            │ ┌──┐ │
│  │              [AI OVERLAYS ACTIVE ON THIS VIEW]              │ │  │ │
│  │                                                            │ └──┘ │
│  │                                                            │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  HR: 76   BP: 118/72   SpO₂: 99%   EtCO₂: 35    🔧14/14 ✓         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Details:**
- Surgeon camera expands to fill ~85% of screen with a smooth 500ms spring animation
- The other two cameras collapse into **small picture-in-picture thumbnails** (120×68px) stacked vertically on the right edge — still live, still visible, clickable/commandable to swap
- Vitals collapse to a single ultra-compact line at the bottom
- **This is where AI overlays live** — anatomy labels, Marma points, artery/vein/nerve markers are drawn directly on this expanded camera view

---

#### STATE 3: "Anatomy Overlay" — AI-Augmented Surgical View

*When:* Surgeon says "Nael, mark the arteries" / "show nerves" / "mark marma points" / "show anatomy"

This is the most visually advanced state. The surgeon camera is expanded (like State 2), and the AI draws **real-time overlays** on the live camera feed.

**Overlay Types:**

**A. Anatomical Structure Marking:**
```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│              LIVE SURGEON CAMERA                           │
│                                                            │
│         ╭─── Hepatic Artery ────╮                          │
│         │  (pulsing red outline) │                          │
│         ╰────────────────────────╯                          │
│                                                            │
│    ╭─── Common Bile Duct ────╮                              │
│    │  (green outline, label)  │                             │
│    ╰──────────────────────────╯                             │
│                                                            │
│              ╭─── Portal Vein ─╮                            │
│              │ (blue outline)   │                           │
│              ╰──────────────────╯                           │
│                                                            │
│  ┌─ LEGEND ──────────────────────────────┐                 │
│  │ ● Arteries (red)  ● Veins (blue)     │                 │
│  │ ● Nerves (yellow) ● Ducts (green)    │                 │
│  │ ● Marma Zone (saffron pulsing)        │                 │
│  └───────────────────────────────────────┘                 │
└────────────────────────────────────────────────────────────┘
```

- **Arteries:** Semi-transparent red outlines with subtle pulse animation synced to heart rate from Monitor Sentinel
- **Veins:** Semi-transparent blue outlines, steady glow
- **Nerves:** Yellow dashed outlines with gentle shimmer animation — nerves are danger zones
- **Ducts:** Green solid outlines
- **Marma zones:** Saffron/gold pulsing region with expanding concentric rings — the Oracle's domain made visual. When the surgeon approaches a Marma, the pulsing intensifies.

**Labels** float next to structures with a thin leader line connecting label to structure. Labels use glassmorphic background (frosted dark glass) so they're readable over any tissue colour. Labels auto-reposition to avoid overlapping each other.

**Surgeon controls via voice:**
- "Nael, mark arteries" → red overlays appear
- "Nael, mark nerves" → yellow overlays appear
- "Nael, mark marma points" → saffron overlays with Oracle data
- "Nael, mark everything" → all overlays simultaneously, colour-coded
- "Nael, remove overlays" → all overlays fade out (300ms)
- "Nael, remove nerve markers" → only nerve overlays fade
- "Nael, what's that structure?" (point-and-ask) → AI identifies and labels the pointed structure with a popup tooltip

**B. Marma Overlay (Oracle Integration):**

When Marma is detected or requested:

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│   LIVE CAMERA with saffron pulsing zone marking Marma region       │
│                                                                    │
│                  ╭────────────────╮                                 │
│                  │  ◉ MARMA ZONE  │                                 │
│                  │  (pulsing gold) │                                 │
│                  ╰────────────────╯                                 │
│                                                                    │
│  ┌── MARMA INTELLIGENCE PANEL ─────────────────────────────────┐   │
│  │                                                              │   │
│  │  मर्म: नाभि मर्म                                              │   │
│  │  Nābhi Marma                                                 │   │
│  │                                                              │   │
│  │  Classification: Sadya Pranahara (सद्य प्राणहर)                │   │
│  │  "Immediately fatal if injured"                              │   │
│  │                                                              │   │
│  │  Location: Umbilical region, 4 aṅgula extent                 │   │
│  │  Modern: Aortic bifurcation, IMA origin, coeliac axis       │   │
│  │                                                              │   │
│  │  ⚠ Consequences: Complete disruption of prāṇa vāyu          │   │
│  │  Modern: Catastrophic vascular injury                        │   │
│  │                                                              │   │
│  │  Protective Doctrine: "Distance, gentle dissection,          │   │
│  │  avoid cautery near the Marma boundary"                      │   │
│  │                                                              │   │
│  │  ────────────────────────────────────────────────────────    │   │
│  │  श्लोक: नाभिप्राणधरा मर्म...                                   │   │
│  │  — Sushruta Samhita, Sharira Sthana 6.28                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

The Marma panel slides in from the right edge (400ms, spring easing). Glassmorphic background. Saffron accent colour for all Oracle content. Devanagari text in Noto Sans Devanagari. Classification badge colour-coded by severity (red for Sadya Pranahara, orange for Kalantara, yellow for Vaikalyakara, etc.)

---

#### STATE 4: "Vital Emergency" — Monitor Sentinel Alert Mode

*When:* Monitor Sentinel detects adverse trajectory (predictive alert) or critical threshold breach

The **entire screen transforms** to communicate urgency:

```
┌──────────────────────────────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓ AMBER BORDER PULSE (Monitor Sentinel) ▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                                                                      │
│  ┌────────────────────────────────────────┐  ┌─────────────────────┐ │
│  │                                        │  │                     │ │
│  │         SURGEON CAMERA                 │  │  BLOOD PRESSURE     │ │
│  │         (still live, 60% width)        │  │                     │ │
│  │                                        │  │   118 → 104 → 96   │ │
│  │                                        │  │      ↓ DECLINING    │ │
│  └────────────────────────────────────────┘  │                     │ │
│                                              │  ┌─────────────┐   │ │
│  ┌── PREDICTIVE MODEL ─────────────────┐     │  │ TREND GRAPH │   │ │
│  │                                      │     │  │  ╲          │   │ │
│  │  "BP declining 2mmHg/min over 6min"  │     │  │   ╲         │   │ │
│  │  "Projected: 88 systolic in 10min"   │     │  │    ╲  ←88   │   │ │
│  │                                      │     │  │     ╲       │   │ │
│  │  ▶ Recommended: Note trajectory      │     │  └─────────────┘   │ │
│  │                                      │     │                     │ │
│  └──────────────────────────────────────┘     │  HR: 96 ↑  SpO₂:99│ │
│                                              └─────────────────────┘ │
│                                                                      │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
└──────────────────────────────────────────────────────────────────────┘
```

**Behaviours:**
- Screen border pulses with amber (Monitor Sentinel colour) — 1.5s ease-in-out infinite animation
- Vital panel expands to occupy 40% of screen — the declining value is displayed at 96px font with a downward arrow animation
- A **real-time trend graph** appears showing the last 10 minutes of the parameter with a **projected dashed line** showing where the AI predicts it will be
- Predictive text explanation appears in plain language
- Surgeon camera remains visible but reduced to 60% width — surgery doesn't stop for alerts
- After the team acknowledges or the trend reverses, the display smoothly transitions back to previous state (600ms)

**For CRITICAL threshold breach (not just trend):** The amber becomes red. The vital value pulses. An audio tone plays through theatre speakers. The value flashes 3 times before settling to steady display.

---

#### STATE 5: "Haemorrhage Alert" — Critical Alert Path Visual

*When:* Haemorrhage Sentinel fires (Critical Alert Path, <500ms)

This is the most aggressive visual state. It must be impossible to miss.

```
┌──────────────────────────────────────────────────────────────────────┐
│ ██ RED BORDER FLASH ██████████████████████████████████████████████ ██│
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                                                                │  │
│  │                SURGEON CAMERA (expanded)                       │  │
│  │                                                                │  │
│  │         ╔══════════════════════╗                                │  │
│  │         ║ ⚠ BLEED DETECTED   ║                                │  │
│  │         ║ Arterial, pulsatile ║                                │  │
│  │         ║ Lateral to dissect. ║                                │  │
│  │         ╚══════════════════════╝                                │  │
│  │              ↑                                                 │  │
│  │         (red pulsing circle marks the bleed region on camera)  │  │
│  │                                                                │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  HR: 76   BP: 118/72   SpO₂: 99%        🔧14/14 ✓                  │
│ ██████████████████████████████████████████████████████████████████████│
└──────────────────────────────────────────────────────────────────────┘
```

**Behaviours:**
- Screen border flashes arterial red (`#FF3B4A`) — 3 rapid pulses (200ms on/200ms off), then settles to steady red border
- Surgeon camera auto-expands to full screen if not already
- A **pulsing red circle/region overlay** appears on the camera feed at the detected bleed location — the AI marks WHERE the bleeding is on the actual live video
- A concise alert box appears with glassmorphic red background: type of bleeding, location relative to dissection
- Everything else is suppressed — this is the highest priority state
- Fades back to previous state after 8 seconds or on surgeon voice command "Nael, acknowledged"

---

#### STATE 6: "Knowledge Display" — Scholar/Oracle/Consultant Content

*When:* Surgeon asks for references, explanations, shlokas, risk flags, pre-op data

This is a **split-screen** state — camera on one side, knowledge on the other:

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐  │
│  │                          │  │  THE ORACLE                      │  │
│  │    SURGEON CAMERA        │  │  ══════════                      │  │
│  │    (60% width)           │  │                                  │  │
│  │                          │  │  Query: "Marma near hepato-      │  │
│  │                          │  │  duodenal ligament"               │  │
│  │                          │  │                                  │  │
│  │   [AI overlays if        │  │  नाभिप्राणधरा मर्म                │  │
│  │    relevant]             │  │  Nābhi Marma                     │  │
│  │                          │  │                                  │  │
│  │                          │  │  Classification: Sadya Pranahara │  │
│  │                          │  │                                  │  │
│  │                          │  │  Modern Mapping:                 │  │
│  │                          │  │  Coeliac trunk, SMA origin...    │  │
│  │                          │  │                                  │  │
│  │                          │  │  ─── Shloka ────                 │  │
│  │                          │  │  Sanskrit text in Devanagari     │  │
│  │                          │  │  — Sushruta, Sharira 6.28        │  │
│  └──────────────────────────┘  │                                  │  │
│                                │  [scrollable if long]            │  │
│  HR: 76  BP: 118/72  SpO₂:99  └──────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

**Content variations:**
- **Oracle query:** Saffron accent, Devanagari text, shloka with verse reference, bidirectional mapping
- **Scholar risk flags:** Warm white accent, pre-op flags displayed as priority-ordered cards with colour-coded severity badges
- **Consultant answer:** Blue accent, structured clinical response in clear sections (immediate action, considerations, technique)
- **Pre-op imaging:** CT/MRI/X-ray viewer with Clara-generated anatomy segmentation overlays. Surgeon can say "Nael, show the CT" and the DICOM viewer appears with AI-highlighted anomalies
- **Drug reference:** Violet accent (Pharmacist colour), dose calculations, interaction warnings

**Dismiss:** "Nael, clear" or "Nael, back to cameras" — knowledge panel slides out to the right (400ms)

---

#### STATE 7: "Pharmacokinetics Dashboard" — Anaesthesia Intelligence View

*When:* "Nael, show pharmacokinetics" or Pharmacist proactively triggers during TIVA

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  ┌── PROPOFOL ─────────────────────┐  ┌── REMIFENTANIL ───────────┐ │
│  │  Model: Schnider                │  │  Model: Minto              │ │
│  │                                 │  │                            │ │
│  │  Plasma: 3.2 µg/mL             │  │  Plasma: 4.1 ng/mL        │ │
│  │  Effect-site: 2.8 µg/mL        │  │  Effect-site: 3.8 ng/mL   │ │
│  │  Rate: 180 mL/hr               │  │  Rate: 0.15 µg/kg/min     │ │
│  │                                 │  │                            │ │
│  │  ┌─────────────────────────┐    │  │  ┌────────────────────┐   │ │
│  │  │  ╱╲                     │    │  │  │   ╱──────          │   │ │
│  │  │ ╱  ╲___________         │    │  │  │  ╱                 │   │ │
│  │  │╱               ╲        │    │  │  │ ╱                  │   │ │
│  │  │                 ╲╌╌╌╌╌  │    │  │  │╱                   │   │ │
│  │  │ plasma ── effect ╌╌╌   │    │  │  │ plasma ── effect   │   │ │
│  │  └─────────────────────────┘    │  │  └────────────────────┘   │ │
│  │  Emergence prediction: 12 min   │  │  Context-sensitive t½:   │ │
│  │  after stopping infusion        │  │  3.5 min                  │ │
│  └─────────────────────────────────┘  └────────────────────────────┘ │
│                                                                      │
│  ┌── DRUG LOG ─────────────────────────────────────────────────────┐ │
│  │  14:23  Propofol 130mg IV (induction)                           │ │
│  │  14:24  Fentanyl 100µg IV                                       │ │
│  │  14:25  Atracurium 35mg IV                                      │ │
│  │  14:26  Propofol infusion started @ 10mg/kg/hr                  │ │
│  │  14:30  Remifentanil infusion started @ 0.15µg/kg/min           │ │
│  │  ...                                                             │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  HR: 72   BP: 108/68   SpO₂: 100%   EtCO₂: 34   Temp: 36.3°C     │
└──────────────────────────────────────────────────────────────────────┘
```

**Details:**
- Dual concentration-time curves (plasma = solid line, effect-site = dashed line) rendered as smooth SVG paths with real-time data point appending
- Predicted emergence time displayed prominently
- All content framed in Pharmacist violet (`#A855F7`) accent
- Complete drug log scrollable in bottom panel with timestamps
- Vitals always visible at bottom
- This view is primarily for the anaesthesiologist — it can be routed to a second display near the anaesthesia workstation if available

---

### 3.2 AI-Driven Layout Transitions

The AI doesn't just display states — it **transitions between them intelligently based on surgical context.

[ignoring loop detection]

# ShalyaMitra — Theatre Display Frontend Design Specification
### Version 3.0 — Production-Ready UI/UX Architecture

> *Not a dashboard. Not a monitor. A living visual consciousness that moves with the surgery.*

---

## 1. Design Philosophy — The JARVIS Principle

**Law 1 — Information finds the surgeon.** Every element appears because the AI determined it should be there NOW. If the surgeon must search, the UI has failed.

**Law 2 — The screen is a living organism.** No static dashboards. The layout morphs continuously — expanding what matters, collapsing what doesn't, animating transitions so spatial memory is never broken.

**Law 3 — Darkness is canvas. Light is signal.** True black background. Every pixel of light carries meaning. The OR is visually demanding — the display must never compete with the surgical field.

---

## 2. Design System — "Nael Dark"

### 2.1 Colour Architecture

**Surfaces:**
- Base Black: `#000000` (true black, OLED-optimised for Smart TV)
- Surface 1: `#0A0A0F` (card backgrounds)
- Surface 2: `#12121A` (elevated panels)
- Glass: `rgba(15, 15, 25, 0.85)` + `backdrop-blur(20px)` (glassmorphic overlays)

**Primary Accent — "Nael Blue":** `#3D8BFF` (interactive elements, Nael's identity)

**Intelligence Pillar Colours** — Each intelligence has a signature colour so the surgeon INSTANTLY knows which AI is speaking without reading a label:

| Intelligence | Colour | Hex | Rationale |
|---|---|---|---|
| Nael (The Voice) | Cool Blue | `#3D8BFF` | Calm, trustworthy, primary |
| Haemorrhage Sentinel | Arterial Red | `#FF3B4A` | Universal bleeding danger |
| Monitor Sentinel | Amber/Gold | `#FFB020` | Warning, physiological |
| The Sentinel (Overhead) | Teal | `#20D9B0` | Environmental, spatial |
| The Pharmacist | Violet | `#A855F7` | Pharmaceutical, distinct |
| The Scholar | Warm White | `#F5E6D3` | Knowledge, paper-like |
| The Oracle | Saffron/Gold | `#FF9F1C` | Classical tradition, sacred |
| Devil's Advocate | Crimson-Orange | `#FF6B35` | Caution without panic |
| The Chronicler | Silver | `#B0B8C8` | Neutral recording |

**Why this matters:** When an amber-bordered alert appears, the surgeon's peripheral vision registers AMBER = physiological alert, before conscious reading. Saffron = Oracle. Red = bleeding. This is **pre-attentive processing** — the UI communicates before the brain reads.

**Alert Severity Tiers:**
- **CRITICAL:** Full-screen border pulse + colour flood + audio tone
- **WARNING:** Panel highlight + gentle pulse + audio chime
- **INFO:** Subtle corner dot indicator, no audio

### 2.2 Typography

| Use Case | Font | Size |
|---|---|---|
| Vital values (large) | JetBrains Mono 700 | 72–96px |
| Alert messages | Inter 600 | 28–36px |
| Panel headings | Inter 500 | 20–24px |
| Body text | Inter 400 | 16–18px |
| Data labels | Inter 500 UPPERCASE | 12–14px |
| Shlokas (Devanagari) | Noto Sans Devanagari 500 | 24–32px |
| Shloka transliteration | Inter 400 italic | 18px |
| Timers | JetBrains Mono 700 | 48–64px |

**Readability rules:** Minimum 14px anywhere on screen (visible from 3 metres). Critical values 72px+ (readable from across OR). Max 60 chars per line.

### 2.3 Micro-Animations

Every transition uses physics-based easing, never linear:

- **Panel expand/collapse:** 400ms, `cubic-bezier(0.16, 1, 0.3, 1)`
- **Element fade in:** 250ms ease-out with 10px Y-translate
- **Alert pulse:** 1.5s ease-in-out infinite glow in pillar accent colour
- **Camera transitions:** 500ms spring animation with slight overshoot
- **Data value change:** 200ms counter animation (values transition, never jump)
- **Screen state changes:** 600ms cross-fade

**The Nael Listening Indicator:** When the surgeon says "Nael" — concentric blue rings pulse outward from a small icon in the corner. Present but gentle. Disappears when Nael finishes responding.

---

## 3. The Adaptive Layout Engine — 7 Dynamic States

The layout is **computed by the AI in real time** based on surgical context. The surgeon can also command any state by voice.

---

### STATE 1: "Theatre Overview" — Default Surveillance

*When: Surgery stable, no alerts, no active query.*

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐    ⏱ 01:23:45     │
│  │ SURGEON   │  │ OVERHEAD  │  │ MONITOR   │    Phase: Dissect  │
│  │ CAMERA    │  │ CAMERA    │  │ CAMERA    │    ● Nael Ready    │
│  │ (live)    │  │ (live)    │  │ (live)    │                    │
│  └───────────┘  └───────────┘  └───────────┘                    │
│                                                                  │
│  ┌─ VITALS (compact bar) ─────────────────────────────────────┐  │
│  │ HR:76 ↔  BP:118/72 ↔  SpO₂:99% ↔  EtCO₂:35  Temp:36.4°C │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ INSTRUMENTS ─┐  ┌─ PHARMACIST ─┐  ┌─ TIMELINE ──────────┐  │
│  │ 🔧 14/14 ✓    │  │ Propofol ███ │  │ ──●──●──●──●──●──── │  │
│  │ 🧹 6/6  ✓     │  │ Remi ████    │  │ Inc  Dissect  ...   │  │
│  └────────────────┘  └──────────────┘  └─────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

- Three equal cameras side by side (16:9, ~480×270px each)
- Compact vitals bar with trend arrows (↑ ↗ → ↘ ↓)
- Bottom row: instrument count (green ✓ = matched), PK mini-bars, surgical timeline
- Top-right: surgery timer, auto-detected phase, Nael status
- Everything muted — nothing screams for attention

---

### STATE 2: "Surgeon Focus" — Single Camera Expanded

*Voice: "Nael, expand surgical camera" / "full screen surgeon view"*

```
┌──────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────┐            │
│  │                                                  │  ┌──┐ OVH │
│  │           SURGEON CAMERA — FULL                  │  │  │     │
│  │           (fills ~85% of screen)                 │  └──┘     │
│  │                                                  │  ┌──┐ MON │
│  │           [AI OVERLAYS ACTIVE HERE]               │  │  │     │
│  │                                                  │  └──┘     │
│  └──────────────────────────────────────────────────┘            │
│  HR:76  BP:118/72  SpO₂:99%  EtCO₂:35   🔧14/14 ✓              │
└──────────────────────────────────────────────────────────────────┘
```

- 500ms spring animation expansion
- Other cameras collapse to PiP thumbnails (120×68px) stacked on right edge — still live
- Vitals compress to single line at bottom
- **This is where AI overlays live** — anatomy, Marma, structure markers

---

### STATE 3: "Anatomy Overlay" — AI-Augmented Surgical View

*Voice: "Nael, mark the arteries" / "show nerves" / "mark marma points"*

Surgeon camera expanded with **real-time AI overlays drawn on the live feed:**

**Overlay colour coding:**
- **Arteries:** Semi-transparent red outlines with subtle pulse synced to heart rate
- **Veins:** Semi-transparent blue outlines, steady glow
- **Nerves:** Yellow dashed outlines with gentle shimmer — danger zones
- **Ducts:** Green solid outlines
- **Marma zones:** Saffron pulsing region with expanding concentric rings — intensifies on approach

**Labels** float next to structures with thin leader lines. Glassmorphic background (frosted dark glass) for readability over any tissue colour. Auto-reposition to prevent overlap.

A **legend panel** (bottom-left corner) shows active overlay types.

**Voice controls:**
- "Nael, mark arteries" → red overlays appear
- "Nael, mark everything" → all overlays, colour-coded
- "Nael, remove overlays" → all fade out (300ms)
- "Nael, remove nerve markers" → selective removal
- "Nael, what's that structure?" → AI identifies + labels the pointed structure

**Marma Overlay (Oracle Integration):**

When Marma is detected, a **Marma Intelligence Panel** slides in from the right (400ms spring, saffron accent):

- Marma name in Devanagari + transliteration
- Classification badge (colour-coded by severity — red for Sadya Pranahara, orange for Kalantara, yellow for Vaikalyakara)
- Modern anatomical mapping
- Consequences of injury (classical + modern)
- Protective doctrine
- Sanskrit shloka with chapter/verse reference
- Dismiss: "Nael, clear" — slides out

---

### STATE 4: "Vital Alert" — Monitor Sentinel Predictive Warning

*When: Monitor Sentinel detects adverse trajectory*

```
┌──────────────────────────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓ AMBER BORDER PULSE (1.5s ease-in-out) ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                                                                  │
│  ┌────────────────────────────┐  ┌─────────────────────────────┐ │
│  │                            │  │   BLOOD PRESSURE            │ │
│  │   SURGEON CAMERA (60%)     │  │   118 → 104 → 96  ↓        │ │
│  │   (still live)             │  │   (96px, declining arrow)   │ │
│  │                            │  │                             │ │
│  └────────────────────────────┘  │   ┌── TREND GRAPH ───────┐ │ │
│                                  │   │  ╲                    │ │ │
│  ┌── PREDICTION ──────────────┐  │   │   ╲                   │ │ │
│  │ "BP declining 2mmHg/min    │  │   │    ╲╌╌╌ ← 88 proj    │ │ │
│  │  over 6 min. Projected:   │  │   └───────────────────────┘ │ │
│  │  88 systolic in 10 min."  │  │                             │ │
│  └────────────────────────────┘  │   HR:96↑  SpO₂:99  EtCO₂:35│ │
│                                  └─────────────────────────────┘ │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
└──────────────────────────────────────────────────────────────────┘
```

- Amber border pulses infinitely until acknowledged or trend reverses
- Declining value displayed at 96px with animated downward arrow
- Real-time **trend graph** (SVG) with **projected dashed line** showing AI prediction
- Plain language prediction text
- Camera stays visible at 60% — surgery doesn't stop
- Auto-dismisses when trend reverses, or on "Nael, acknowledged"
- **CRITICAL breach** (not just trend): Amber → Red. Value flashes 3×. Audio tone through speakers.

---

### STATE 5: "Haemorrhage Alert" — Critical Alert Path Visual

*When: Haemorrhage Sentinel fires (<500ms path)*

**The most aggressive visual state — impossible to miss:**

- Screen border **flashes arterial red** — 3 rapid pulses (200ms on/off), then steady red
- Surgeon camera **auto-expands** to full screen
- A **pulsing red circle overlay** appears on the live camera at the detected bleed location — AI marks WHERE
- Concise alert box: bleeding type, location relative to dissection
- Everything else suppressed
- Auto-fades after 8 seconds or on "Nael, acknowledged"

---

### STATE 6: "Knowledge Display" — Split Screen for Scholar/Oracle/Consultant

*Voice: "Nael, show the risk flags" / "read the shloka" / any knowledge query*

```
┌──────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────┐  ┌────────────────────────────────────┐ │
│  │                     │  │  THE ORACLE            [saffron]   │ │
│  │  SURGEON CAMERA     │  │                                    │ │
│  │  (60% width)        │  │  Query: "Marma near hepato-       │ │
│  │                     │  │  duodenal ligament"                │ │
│  │  [overlays if       │  │                                    │ │
│  │   relevant]         │  │  नाभिप्राणधरा मर्म                  │ │
│  │                     │  │  Nābhi Marma                       │ │
│  │                     │  │                                    │ │
│  │                     │  │  Classification: Sadya Pranahara   │ │
│  │                     │  │  Modern: Coeliac trunk, SMA...     │ │
│  │                     │  │                                    │ │
│  │                     │  │  ─── Shloka ────                   │ │
│  │                     │  │  Sanskrit in Devanagari            │ │
│  └─────────────────────┘  │  — Sushruta, Sharira 6.28          │ │
│                           └────────────────────────────────────┘ │
│  HR:76  BP:118/72  SpO₂:99%                                     │
└──────────────────────────────────────────────────────────────────┘
```

**Content variations by pillar:**
- **Oracle:** Saffron accent, Devanagari text, shloka citations, bidirectional mapping
- **Scholar:** Warm white accent, pre-op flags as priority-ordered cards with severity badges
- **Consultant:** Blue accent, structured clinical response (action → considerations → technique)
- **Pre-op Imaging:** CT/MRI DICOM viewer with Clara/MONAI segmentation overlays, AI-highlighted anomalies
- **Drug Reference:** Violet accent, dose calculations, interaction warnings

Knowledge panel slides in from right (400ms spring). Dismiss: "Nael, clear"

---

### STATE 7: "Pharmacokinetics Dashboard" — TIVA Intelligence

*Voice: "Nael, show pharmacokinetics"*

- Dual concentration-time curve graphs (plasma = solid line, effect-site = dashed)
- Real-time data point appending as smooth SVG paths
- Emergence time prediction prominently displayed
- Complete drug log with timestamps (scrollable)
- Violet (`#A855F7`) accent throughout
- Can be routed to a second display near anaesthesia workstation

---

## 4. Priority Interrupt System — How Alerts Override Everything

**Priority Hierarchy (highest first):**

1. **Haemorrhage Sentinel** — RED — Overrides everything. Full screen takeover.
2. **Instrument Count Discrepancy** — RED — At closure, blocks all other content.
3. **Monitor Sentinel Critical** — RED — Threshold breach, vital emergency.
4. **Monitor Sentinel Warning** — AMBER — Predictive trend alert.
5. **Tissue Stress Alert** — AMBER — Retraction time threshold.
6. **Devil's Advocate** — CRIMSON-ORANGE — Cross-intelligence conflict query.
7. **Active conversation with Nael** — BLUE — Current query response.
8. **Background surveillance** — No accent — Default theatre overview.

**The critical rule:** A Priority 1 alert fires INSTANTLY regardless of what's on screen. If the surgeon is reviewing a shloka and the Haemorrhage Sentinel fires — the shloka is immediately pushed to a small saved panel, the haemorrhage alert takes full screen. After acknowledgment, the shloka returns. No context is lost.

**Alert Queue:** If multiple alerts fire within 2 seconds, they stack by priority. The highest shows first. Lower-priority alerts appear as compact notification badges in the top-right corner, awaiting their turn.

---

## 5. The Nael Interaction Layer — Voice-Driven UI Patterns

### 5.1 The Listening State

When "Nael" is detected:

1. **Nael icon** (bottom-right corner, 48px circle with waveform inside) transitions from idle (dim blue dot) to **active** (pulsing blue rings expanding outward, 1.5s period)
2. A subtle **"LISTENING..."** label appears next to the icon with a live audio waveform visualisation showing the surgeon's voice amplitude
3. The current screen state is preserved — nothing changes until Nael has a response

### 5.2 The Thinking State

After Nael has the query and is reasoning (~1–1.5s):

1. The waveform changes to a **rotating dot cluster** animation (three dots orbiting, like a thinking indicator)
2. Label changes to **"THINKING..."**
3. If the response requires a layout change (e.g., expanding a knowledge panel), the transition **begins during thinking** — so by the time Nael speaks, the visual answer is already appearing

### 5.3 The Response State

When Nael responds:

1. Icon shows a **speaking waveform** animation (amplitude bars matching Nael's audio output)
2. If the response includes visual content → layout transitions to appropriate state (Knowledge, Overlay, etc.)
3. If the response is audio-only (no visual needed) → screen stays in current state, only the Nael icon animates
4. A **subtle transcript line** appears at the bottom edge (optional, togglable): a single line of the current Nael response, useful for the anaesthesiologist who may not have heard through their own neckband

### 5.4 Voice Command Reference on Screen

On "Nael, help" or "Nael, what can I ask?" — a semi-transparent overlay appears with categorised commands:

```
┌── NAEL COMMANDS ─────────────────────────────────────────┐
│                                                          │
│  📷 CAMERAS                    🔬 ANATOMY                │
│  "Expand surgical camera"      "Mark arteries"           │
│  "Show overhead"               "Mark nerves"             │
│  "Show monitor camera"         "Mark marma points"       │
│  "Show all cameras"            "Mark everything"         │
│  "Full screen [camera]"        "Remove overlays"         │
│                                "What's that structure?"   │
│  📊 VITALS                                               │
│  "Show the monitor"            📜 KNOWLEDGE              │
│  "Show vital trends"           "Show risk flags"         │
│  "Show pharmacokinetics"       "Read the shloka"         │
│                                "Show the MRI/CT"         │
│  🔧 STATUS                     "Show drug doses"         │
│  "Instrument count"            "Show explanation"        │
│  "Retraction timer"                                      │
│  "Timeline"                    🔇 CONTROL                │
│  "Show drug log"               "Acknowledged"            │
│                                "Clear" / "Back"          │
└──────────────────────────────────────────────────────────┘
```

Fades out after 10 seconds or on "Nael, clear."

---

## 6. Pre-Operative Screen — Scholar Intelligence View

Before the surgery begins, the Theatre Display serves as the **pre-operative briefing surface.** This is a completely different UI mode.

### 6.1 Pre-Op Dashboard

```
┌──────────────────────────────────────────────────────────────────┐
│  SHALYAMITRA PRE-OPERATIVE INTELLIGENCE                         │
│  Patient: [Name]    Procedure: [Type]    Surgeon: Dr. [Name]    │
│                                                                  │
│  ┌── RISK SCORE ──┐  ┌── CRITICAL FLAGS ──────────────────────┐ │
│  │                 │  │                                        │ │
│  │   ASA III       │  │  ⚠ Borderline eGFR: 52               │ │
│  │                 │  │  ⚠ ACE inhibitor — stop 24hr pre-op? │ │
│  │  RCRI: 2/6      │  │  ⚠ Allergy: Penicillin (anaphylaxis)│ │
│  │                 │  │  ⚠ Previous difficult airway          │ │
│  │  Renal Risk:    │  │                                        │ │
│  │  MODERATE       │  └────────────────────────────────────────┘ │
│  └─────────────────┘                                             │
│                                                                  │
│  ┌── TABS ──────────────────────────────────────────────────┐    │
│  │ [Clinical Synthesis] [Imaging] [Drug Map] [Ayurvedic]    │    │
│  │                                                          │    │
│  │  Full clinical narrative generated by the Scholar...     │    │
│  │  Scrollable, with sections expandable on tap/voice.      │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌── IMAGING VIEWER ────────────────────────────────────────┐    │
│  │  CT/MRI with MONAI segmentation overlays                  │    │
│  │  AI-highlighted anatomical deviations in yellow           │    │
│  │  "Anomalous hepatic artery — replaced right hepatic       │    │
│  │   artery arising from SMA" — auto-flagged                 │    │
│  └───────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

**Tab structure:**
- **Clinical Synthesis:** Full narrative from Scholar. Expandable sections.
- **Imaging:** DICOM viewer with MONAI/Clara segmentation. Pinch-zoom equivalent via voice ("Nael, zoom in on the portal vein").
- **Drug Interaction Map:** Visual network diagram — current medications as nodes, potential intraoperative agents as nodes, red lines connecting dangerous interactions, green for safe.
- **Ayurvedic Assessment:** Prakriti analysis, Dosha status, classical contraindication flags. Saffron accent.

**Transition to surgery:** When the surgeon says "Nael, let's begin" or the first camera connects — the pre-op view smoothly transitions (800ms) to Theatre Overview (State 1). The Scholar's data doesn't disappear — it moves into the background, queryable at any time.

---

## 7. Closure Sequence — End-of-Surgery UI

When the AI detects closure phase beginning:

### 7.1 Instrument Count Confirmation

The Sentinel's count status auto-appears as a full-width banner:

```
┌──────────────────────────────────────────────────────────────────┐
│  ┌── SENTINEL — INSTRUMENT & SWAB COUNT ───────────────────────┐│
│  │                                                              ││
│  │  🔧 Instruments: 14 deployed │ 14 accounted │ ✓ COMPLETE    ││
│  │  🧹 Swabs:       18 deployed │ 18 accounted │ ✓ COMPLETE    ││
│  │                                                              ││
│  │  ✅ FIELD IS CLEAR — Safe to close                           ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [Surgeon camera still live below]                               │
└──────────────────────────────────────────────────────────────────┘
```

If discrepancy: Banner turns RED, "✓ COMPLETE" becomes "⚠ DISCREPANCY — VERIFY BEFORE CLOSURE." Audio alert fires. Banner does NOT auto-dismiss — it stays until count is resolved.

### 7.2 Post-Surgery Session Summary

After surgeon confirms closure:

```
┌──────────────────────────────────────────────────────────────────┐
│  SHALYAMITRA SESSION COMPLETE                                    │
│                                                                  │
│  Duration: 2h 34m    AI Alerts: 3    Oracle Queries: 2           │
│  GPU Cost: ₹740                                                  │
│                                                                  │
│  ┌── CHRONICLER — HANDOVER BRIEF ──────────────────────────────┐│
│  │                                                              ││
│  │  Procedure: Laparoscopic Cholecystectomy                     ││
│  │  Key Findings: Replaced right hepatic artery (managed)       ││
│  │  Anaesthetic: TIVA (Propofol/Remi), uneventful              ││
│  │  Blood Loss: ~150mL (est.)                                   ││
│  │  Alerts: 1× Haemorrhage (arterial perforator, controlled)   ││
│  │          1× BP trend (corrected by anaesthesia)              ││
│  │          1× Retraction timer (20min, released)               ││
│  │                                                              ││
│  │  Post-Op Watch: MAP >65, monitor eGFR (pre-existing)        ││
│  │  Classical: Ropana protocol recommended per Oracle           ││
│  │                                                              ││
│  │  [Full report exported to Chronicler archive]                ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [Shutdown in 60s... or "Nael, keep session open"]               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 8. Technology Stack for Frontend

| Layer | Technology | Why |
|---|---|---|
| Framework | **Next.js 15** (React 19) | Server components for pre-op, client for real-time theatre |
| Rendering | **React + Canvas/WebGL** for overlays | Camera overlays need pixel-level control |
| Video | **LiveKit React SDK** (`@livekit/components-react`) | Native WebRTC video rendering, room state management |
| Real-time data | **WebSocket** (via LiveKit data channels) | Vitals, alerts, AI responses stream through LiveKit data |
| Charts | **D3.js** (vital trends, PK curves) | Custom SVG paths for medical-grade precision |
| Animations | **Framer Motion** | Physics-based layout animations, spring transitions |
| Styling | **CSS Modules + CSS Custom Properties** | Design tokens as CSS variables for the entire colour system |
| Typography | **Google Fonts** (Inter, JetBrains Mono, Noto Sans Devanagari) | All three loaded for the typography stack |
| DICOM Viewer | **Cornerstone.js** (`cornerstonejs/cornerstone3D`) | Medical imaging standard, MONAI overlay compatible |
| State Management | **Zustand** | Lightweight, perfect for layout state machine |
| Deployment | **Chromium kiosk mode** on Smart TV / laptop | Full-screen, no browser chrome, auto-start |

### 8.1 Architecture

```
┌─────────────────── THEATRE DISPLAY (Chromium Kiosk) ──────────────┐
│                                                                    │
│  Next.js App (Client-Side Rendering for real-time)                 │
│    │                                                               │
│    ├── LiveKit Room Connection                                     │
│    │     ├── Video Tracks (3 cameras) → <VideoTrack> components    │
│    │     ├── Audio Tracks (Nael responses) → <AudioTrack>          │
│    │     └── Data Channel → JSON messages from AI backend          │
│    │           ├── vitals updates (every 1s)                       │
│    │           ├── alert events (instant)                          │
│    │           ├── layout commands (AI-driven state changes)       │
│    │           ├── overlay data (bounding boxes, labels, coords)   │
│    │           └── knowledge content (Oracle, Scholar, etc.)       │
│    │                                                               │
│    ├── Layout State Machine (Zustand)                              │
│    │     ├── currentState: 'theatre_overview' | 'surgeon_focus'... │
│    │     ├── activeAlerts: Alert[]                                  │
│    │     ├── overlays: OverlayData[]                               │
│    │     ├── knowledgePanel: KnowledgeContent | null               │
│    │     └── naelState: 'idle' | 'listening' | 'thinking' | ...   │
│    │                                                               │
│    ├── Overlay Renderer (Canvas/WebGL)                             │
│    │     ├── Draws anatomy labels on surgeon camera                │
│    │     ├── Draws bleed detection circles                         │
│    │     ├── Draws Marma zone pulsing regions                      │
│    │     └── Coordinates from AI backend (normalised 0-1 → px)    │
│    │                                                               │
│    └── Components                                                  │
│          ├── CameraGrid (adaptive 1/2/3 camera layout)             │
│          ├── VitalsBar (compact/expanded)                          │
│          ├── AlertOverlay (priority interrupt rendering)            │
│          ├── KnowledgePanel (Oracle/Scholar/Consultant

[ignoring loop detection]

# ShalyaMitra — Theatre Display Frontend Design Specification
### Version 3.0 — Production-Ready UI/UX Architecture

> *Not a dashboard. A living visual consciousness that moves with the surgery.*

---

## 1. Design Philosophy

**Law 1 — Information finds the surgeon.** Every element appears because the AI determined it should be there NOW.

**Law 2 — The screen is a living organism.** No static dashboards. Layout morphs continuously — expanding what matters, collapsing what doesn't.

**Law 3 — Darkness is canvas. Light is signal.** True black. Every pixel carries meaning. Nothing decorates.

---

## 2. Design System — "Nael Dark"

### 2.1 Colours

**Surfaces:** Base Black `#000000` | Surface 1 `#0A0A0F` | Surface 2 `#12121A` | Glass `rgba(15,15,25,0.85)` + `backdrop-blur(20px)`

**Primary Accent — Nael Blue:** `#3D8BFF`

**Intelligence Pillar Colours** — each intelligence has a unique accent so the surgeon knows which AI is active without reading:

| Intelligence | Hex | Rationale |
|---|---|---|
| Nael (Voice) | `#3D8BFF` | Calm, primary |
| Haemorrhage Sentinel | `#FF3B4A` | Arterial red = bleeding |
| Monitor Sentinel | `#FFB020` | Amber = physiological warning |
| Sentinel (Overhead) | `#20D9B0` | Teal = environmental |
| Pharmacist | `#A855F7` | Violet = pharmaceutical |
| Scholar | `#F5E6D3` | Warm white = knowledge |
| Oracle | `#FF9F1C` | Saffron = classical tradition |
| Devil's Advocate | `#FF6B35` | Crimson-orange = caution |
| Chronicler | `#B0B8C8` | Silver = recording |

**Pre-attentive processing:** Surgeon's peripheral vision registers AMBER = physiology alert, RED = bleeding, SAFFRON = Oracle — before conscious reading.

**Alert Tiers:** CRITICAL = full border pulse + audio | WARNING = panel highlight + chime | INFO = corner dot only

### 2.2 Typography

`Inter` (primary) | `JetBrains Mono` (data/numbers) | `Noto Sans Devanagari` (shlokas)

- Vital values: JetBrains Mono 700, 72–96px (readable from across OR)
- Alerts: Inter 600, 28–36px
- Body: Inter 400, 16–18px
- Shlokas: Noto Sans Devanagari 500, 24–32px
- Minimum anywhere: 14px (visible from 3m)

### 2.3 Animations

All transitions use physics-based easing. The UI must feel alive:
- Panel expand/collapse: 400ms spring
- Camera transitions: 500ms with slight overshoot
- Value changes: 200ms counter (values transition, never jump)
- Alert pulse: 1.5s infinite ease-in-out glow
- State transitions: 600ms cross-fade

**Nael Listening Indicator:** When "Nael" detected → concentric blue rings pulse outward from corner icon. Disappears when response complete.

---

## 3. The 7 Dynamic Layout States

The AI switches between states automatically based on surgical context. Surgeon can also command any state by voice.

---

### STATE 1: "Theatre Overview" — Default

*When: Stable, no alerts, no query*

- Three camera feeds side by side (equal, ~480×270px each on 1920×1080)
- Compact vitals bar below: `HR:76↔ BP:118/72↔ SpO₂:99%↔ EtCO₂:35 Temp:36.4°C` with trend arrows
- Bottom row: Instrument count (`🔧14/14 ✓`), Pharmacist PK mini-bars, surgical timeline
- Top-right: surgery timer, auto-detected phase, Nael status dot
- Everything muted — nothing demands attention

### STATE 2: "Surgeon Focus" — Single Camera Expanded

*Voice: "Nael, expand surgical camera"*

- Selected camera expands to ~85% of screen (500ms spring animation)
- Other two cameras collapse to PiP thumbnails (120×68px) stacked on right edge — still live, swappable by voice
- Vitals compress to single bottom line
- **AI overlays render on this expanded view**

### STATE 3: "Anatomy Overlay" — AI-Augmented View

*Voice: "Nael, mark arteries" / "show nerves" / "mark marma points"*

Camera expanded with real-time overlays drawn on live feed:

**Overlay types:**
- **Arteries:** Red semi-transparent outlines, subtle pulse synced to heart rate
- **Veins:** Blue outlines, steady glow
- **Nerves:** Yellow dashed outlines with shimmer — danger zones
- **Ducts:** Green solid outlines
- **Marma zones:** Saffron pulsing region with expanding concentric rings, intensifies on approach

Labels float next to structures with thin leader lines. Glassmorphic background for readability over any tissue. Auto-reposition to prevent overlap. Bottom-left legend shows active overlay types.

**Voice commands:** "mark arteries" / "mark everything" / "remove overlays" / "remove nerve markers" / "what's that structure?" (point-and-ask → AI identifies + labels)

**Marma Overlay:** Saffron panel slides in from right — Marma name in Devanagari, classification badge (colour-coded by severity), modern mapping, protective doctrine, shloka with verse reference.

### STATE 4: "Vital Alert" — Monitor Sentinel Warning

*When: Adverse trajectory detected*

- Amber border pulses infinitely
- Vital panel expands to 40% screen — declining value at 96px with animated arrow
- Real-time **trend graph** (SVG) with **projected dashed line** showing AI prediction
- Plain language prediction: "BP declining 2mmHg/min. Projected: 88 systolic in 10 min"
- Camera stays at 60% — surgery doesn't stop
- Auto-dismiss on trend reversal or "Nael, acknowledged"
- **Critical breach:** Amber→Red, value flashes 3×, audio tone

### STATE 5: "Haemorrhage Alert" — Critical Alert Path

*When: Haemorrhage Sentinel fires (<500ms)*

- Border flashes RED — 3 rapid pulses, then steady
- Surgeon camera auto-expands full screen
- **Pulsing red circle overlay** on camera at detected bleed location
- Alert box: bleeding type + location
- Everything else suppressed — highest priority
- Auto-fades 8s or "Nael, acknowledged"

### STATE 6: "Knowledge Display" — Split Screen

*Voice: "show risk flags" / "read the shloka" / any knowledge query*

- Camera 60% left, knowledge panel 40% right (slides in, 400ms spring)
- **Oracle content:** Saffron accent, Devanagari text, shloka citations
- **Scholar content:** Warm white, pre-op flags as priority cards
- **Consultant content:** Blue, structured clinical response
- **Pre-op imaging:** DICOM viewer with MONAI/Clara segmentation overlays
- **Drug reference:** Violet, dose calculations
- Dismiss: "Nael, clear"

### STATE 7: "Pharmacokinetics" — TIVA Dashboard

*Voice: "show pharmacokinetics"*

- Dual concentration-time curves (plasma solid, effect-site dashed) as live SVG paths
- Emergence time prediction prominently displayed
- Complete drug log with timestamps
- Violet accent throughout
- Can route to secondary display at anaesthesia workstation

---

## 4. Priority Interrupt System

**Hierarchy (highest first):**
1. Haemorrhage Sentinel → RED → Full takeover
2. Instrument Count Discrepancy → RED → Blocks closure
3. Monitor Sentinel Critical → RED → Threshold breach
4. Monitor Sentinel Warning → AMBER → Predictive trend
5. Tissue Stress Alert → AMBER → Retraction threshold
6. Devil's Advocate → CRIMSON-ORANGE → Conflict query
7. Active Nael conversation → BLUE → Current response
8. Background surveillance → No accent → Default overview

**Critical rule:** Priority 1 fires INSTANTLY regardless of current screen. If surgeon is reading a shloka and haemorrhage fires → shloka pushes to saved panel, alert takes screen. After acknowledgment, shloka returns. No context lost.

**Alert queue:** Multiple alerts within 2s stack by priority. Highest shows first. Lower appear as notification badges in top-right.

---

## 5. Nael Interaction Layer

### Visual States of Nael Icon (bottom-right, 48px circle)

| State | Visual | Label |
|---|---|---|
| Idle | Dim blue dot | None |
| Listening | Pulsing blue concentric rings + live audio waveform | "LISTENING..." |
| Thinking | Three dots orbiting | "THINKING..." |
| Speaking | Amplitude bars matching Nael's voice output | None |

**During "thinking":** If response needs a layout change, the transition **begins during thinking** — visual answer appears as Nael starts speaking.

**Subtle transcript line** (optional, togglable): Single line at bottom edge showing Nael's current response text — useful for anaesthesiologist who may not hear through their neckband.

### Voice Command Overlay

On "Nael, help" — semi-transparent overlay with categorised commands (cameras, anatomy, vitals, knowledge, control). Auto-fades after 10s.

---

## 6. Pre-Operative Screen — Scholar View

Before surgery, the display serves as a **pre-op briefing surface:**

- **Risk Score Panel:** ASA class, RCRI, renal/pulmonary risk with colour-coded severity
- **Critical Flags:** Priority-ordered list with ⚠ icons — anticoagulants, allergies, difficult airway, organ compromise
- **Tabbed Content:**
  - *Clinical Synthesis:* Full Scholar narrative, expandable sections
  - *Imaging:* DICOM viewer (Cornerstone.js) with MONAI segmentation overlays. AI-highlighted anomalies in yellow. Voice-controlled zoom.
  - *Drug Interaction Map:* Visual network — current meds as nodes, planned agents as nodes, red lines = dangerous interactions, green = safe
  - *Ayurvedic Assessment:* Prakriti, Dosha, classical contraindications. Saffron accent.

**Transition to surgery:** "Nael, let's begin" or first camera connects → 800ms morph to Theatre Overview. Scholar data doesn't disappear — moves to background, queryable anytime.

---

## 7. Closure Sequence

### Instrument Count Confirmation

Auto-appears as full-width banner when closure detected:

- `🔧 Instruments: 14/14 ✓ COMPLETE` | `🧹 Swabs: 18/18 ✓ COMPLETE`
- `✅ FIELD IS CLEAR — Safe to close`
- **If discrepancy:** Banner turns RED. `⚠ DISCREPANCY — VERIFY BEFORE CLOSURE.` Audio alert. Banner does NOT auto-dismiss.

### Session Summary

After closure confirmed:
- Duration, alert count, Oracle queries, GPU cost (₹740)
- Chronicler's Handover Brief: procedure, findings, anaesthetic summary, blood loss, alerts fired, post-op watch parameters, classical recommendations
- "Full report exported to Chronicler archive"
- Auto-shutdown timer (60s) or "Nael, keep session open"

---

## 8. Technology Stack

| Layer | Technology | Why |
|---|---|---|
| Framework | **Next.js 15** (React 19) | SSR for pre-op, CSR for real-time theatre |
| Video | **LiveKit React SDK** | Native WebRTC rendering, room management |
| Real-time | **LiveKit Data Channels** | Vitals, alerts, overlays, AI responses as JSON |
| Overlays | **HTML5 Canvas / WebGL** | Pixel-level overlay rendering on camera feeds |
| Charts | **D3.js** | Custom SVG for vital trends + PK curves |
| Animations | **Framer Motion** | Physics-based spring layout transitions |
| Styling | **CSS Modules + Custom Properties** | Design tokens as CSS variables |
| DICOM | **Cornerstone.js** | Medical imaging viewer, MONAI compatible |
| State | **Zustand** | Lightweight state machine for layout states |
| Fonts | **Google Fonts** | Inter, JetBrains Mono, Noto Sans Devanagari |
| Deploy | **Chromium Kiosk Mode** | Full-screen on Smart TV, no browser chrome |

### Architecture Flow

```
LiveKit Room (GPU Server)
    │
    ├── Video Tracks (3 cameras) ──► <VideoTrack> React components
    ├── Audio Tracks (Nael voice) ──► <AudioTrack> components
    └── Data Channel (JSON) ──► Zustand State Machine
            │
            ├── vitals_update → VitalsBar component re-render
            ├── alert_event → Priority Interrupt → Layout State change
            ├── layout_command → AI-driven state transition
            ├── overlay_data → Canvas renderer (bounding boxes, labels)
            ├── knowledge_content → KnowledgePanel component
            └── nael_state → NaelIndicator component
```

### Key Components

```
src/
├── app/
│   ├── theatre/          # Intraoperative display (primary)
│   └── preop/            # Pre-operative Scholar view
├── components/
│   ├── cameras/
│   │   ├── CameraGrid.tsx        # Adaptive 1/2/3 camera layout
│   │   ├── CameraFeed.tsx        # Single LiveKit video track
│   │   └── OverlayCanvas.tsx     # Canvas layer for AI overlays
│   ├── vitals/
│   │   ├── VitalsBar.tsx         # Compact/expanded vitals display
│   │   ├── VitalValue.tsx        # Animated number with trend arrow
│   │   └── TrendGraph.tsx        # D3 SVG trend line + prediction
│   ├── alerts/
│   │   ├── AlertOverlay.tsx      # Priority interrupt renderer
│   │   ├── HaemorrhageAlert.tsx  # Full-screen red flash state
│   │   ├── VitalAlert.tsx        # Amber predictive warning
│   │   └── CountAlert.tsx        # Instrument count at closure
│   ├── knowledge/
│   │   ├── KnowledgePanel.tsx    # Slide-in panel (right side)
│   │   ├── OracleContent.tsx     # Saffron, Devanagari, shlokas
│   │   ├── ScholarFlags.tsx      # Pre-op risk flags cards
│   │   ├── ConsultantAnswer.tsx  # Structured clinical response
│   │   └── ImagingViewer.tsx     # Cornerstone.js DICOM wrapper
│   ├── pharmacist/
│   │   ├── PKDashboard.tsx       # TIVA concentration curves
│   │   ├── DrugLog.tsx           # Timestamped drug list
│   │   └── PKCurve.tsx           # D3 dual plasma/effect-site graph
│   ├── nael/
│   │   ├── NaelIndicator.tsx     # Idle/listening/thinking/speaking
│   │   ├── ListeningWaveform.tsx # Audio amplitude visualisation
│   │   └── TranscriptLine.tsx    # Optional bottom transcript
│   ├── sentinel/
│   │   ├── InstrumentCount.tsx   # Count status badge + closure banner
│   │   └── RetractionTimer.tsx   # Active retractor timers
│   ├── timeline/
│   │   └── SurgeryTimeline.tsx   # Horizontal event timeline
│   └── shared/
│       ├── GlassPanel.tsx        # Glassmorphic container
│       ├── PillarBadge.tsx       # Coloured intelligence identifier
│       └── AnimatedNumber.tsx    # Counter transition component
├── stores/
│   ├── layoutStore.ts            # Zustand: current state, transitions
│   ├── vitalsStore.ts            # Zustand: real-time vital values
│   ├── alertStore.ts             # Zustand: alert queue + priority
│   └── sessionStore.ts           # Zustand: surgery metadata
├── hooks/
│   ├── useLiveKitData.ts         # Parse LiveKit data channel messages
│   ├── useLayoutTransition.ts    # Animated state machine transitions
│   └── useOverlayRenderer.ts    # Canvas drawing for camera overlays
├── lib/
│   ├── colours.ts                # Pillar colour constants
│   ├── priorities.ts             # Alert priority hierarchy
│   └── overlayEngine.ts          # Normalised coords → pixel mapping
└── styles/
    ├── globals.css               # CSS custom properties (design tokens)
    ├── animations.css            # Keyframe definitions
    └── typography.css            # Font face + type scale
```

### Data Channel Message Protocol

All AI→Frontend communication flows through LiveKit data channels as JSON:

```typescript
// Vital update (every ~1s)
{ type: "vitals", data: { hr: 76, bp_sys: 118, bp_dia: 72, spo2: 99, etco2: 35, temp: 36.4, trend: { hr: "stable", bp: "declining" } }}

// Alert event (instant)
{ type: "alert", priority: 1, pillar: "haemorrhage_sentinel", data: { message: "Arterial bleed detected", location: { x: 0.45, y: 0.62, radius: 0.08 }, severity: "critical" }}

// Layout command (AI-driven)
{ type: "layout", target_state: "surgeon_focus", camera: "surgeon_eye", reason: "haemorrhage_alert" }

// Overlay data (per frame or on change)
{ type: "overlay", camera: "surgeon_eye", structures: [
  { id: "hepatic_artery", type: "artery", bbox: [0.3, 0.4, 0.5, 0.6], label: "Hepatic Artery", confidence: 0.94 },
  { id: "cbd", type: "duct", bbox: [0.35, 0.45, 0.48, 0.58], label: "Common Bile Duct", confidence: 0.91 }
]}

// Knowledge content
{ type: "knowledge", pillar: "oracle", content: { marma_name: "Nābhi Marma", devanagari: "नाभि मर्म", classification: "Sadya Pranahara", shloka: "...", reference: "Sharira 6.28", modern_mapping: "..." }}

// Nael state
{ type: "nael_state", state: "listening" | "thinking" | "speaking" | "idle" }
```

---

## 9. Responsive Behaviour

### Primary: 55" Smart TV (1920×1080)
Standard layout as described above. Chromium kiosk mode. Full HD.

### Secondary: Laptop/Tablet (fallback)
- Same layout engine, scaled proportionally
- Camera feeds reduce to 720p rendering
- Touch interaction available as backup to voice
- Can run as supplementary display for anaesthesiologist (showing PK dashboard permanently)

### Dual Display Setup (advanced)
- **Display 1 (main, surgeon-facing):** Full theatre display as described
- **Display 2 (anaesthesia station):** Permanent PK dashboard + drug log + vitals + Pharmacist channel. Connected to same LiveKit room, different layout state.

---

## 10. Performance Requirements

| Metric | Target |
|---|---|
| Camera feed rendering | 30fps, <100ms delay from LiveKit |
| Overlay rendering | 60fps canvas redraw |
| Alert display latency | <50ms from data channel receipt to screen |
| Layout state transition | <600ms animation complete |
| Vital value update | <100ms from receipt to display |
| Initial page load | <3s to first camera frame |
| Memory usage | <512MB (3 video streams + canvas + D3) |

### Optimisation Strategies
- Video tracks: Hardware-decoded via `<video>` element (browser handles WebRTC decoding)
- Canvas overlays: Only redraw on new overlay data, not every frame
- D3 charts: Update only changed data points, not full re-render
- Framer Motion: `layout` prop for automatic layout animations without manual calculation
- React: Aggressive `memo()` on camera and vital components to prevent unnecessary re-renders

---

## 11. Accessibility & Safety Considerations

- **Colour-blind safe:** All alerts use both colour AND shape/pattern (red + flashing border, amber + pulse, etc.) — never colour alone
- **Audio redundancy:** Every visual alert has an accompanying audio signal — the surgeon may not be looking at the display
- **Fail-safe default:** If the display crashes or disconnects, all AI intelligence continues operating via audio through neckbands — the display is supplementary to voice, never the sole channel
- **Anti-burn-in:** For OLED TVs, subtle pixel shifting on static elements (timers, labels) — 1px movement every 60 seconds
- **Night/Day modes:** Both are dark, but "Day" mode has slightly elevated surface brightness for brightly-lit ORs

---

## 12. The Devil's Advocate Visual Pattern

When the Devil's Advocate fires, it has a unique visual treatment — distinct from all other alerts because it's not an emergency, it's a *question*:

- A **crimson-orange glass panel** slides down from the top centre (300ms)
- Contains one sentence — the conflict question
- Below the question: the **evidence** — a mini-card showing the data point from Scholar/Pharmacist/Monitor that triggered the conflict
- Two implicit options: surgeon verbally confirms → panel fades (400ms) | surgeon asks for more detail → panel expands to Knowledge Display
- The panel has a subtle **thinking pulse** animation — slower than alerts, more contemplative
- It never blocks the camera feeds — it overlays transparently

---

## 13. Retraction Timer Widget

A persistent but non-intrusive floating widget when any retractor is tracked:

```
┌─ RETRACTION ──────────────────┐
│  Lateral femoral cutaneous    │
│  ██████████████░░░  18:42     │
│  Threshold: 20:00   ⚠ CLOSE  │
└───────────────────────────────┘
```

- Progress bar fills with time, colour transitions: green → yellow (75%) → amber (90%) → red (100%)
- At threshold: bar pulses, audio alert fires via Critical Alert Path
- Multiple retractors tracked simultaneously as stacked widgets
- Position: bottom-left corner, out of the way but visible

---

## 14. The Instrument Tracking Live View

When surgeon says "Nael, show instrument count" — a dedicated panel showing:

- Visual grid of all instruments (icon-based)
- Each instrument: ✅ (in tray) or 🔴 (in field) or ⚠ (missing)
- Swab counter: deployed vs recovered with mini swab icons
- Real-time — updates as Sentinel tracks items entering/leaving field
- Visual confidence indicator per item (high/medium/low recognition confidence)

---

## 15. Session Recording Indicator

A subtle red dot (●) with "REC" label in the top-left corner — always visible, always honest. The surgeon must always know the system is observing. This aligns with the Foundational Protection philosophy — transparency, not surveillance.

---

This covers the complete frontend design specification. The document describes every visual state, every interaction pattern, the component architecture, the data flow, the animation system, the colour language, the priority hierarchy, and the technology stack needed to build ShalyaMitra's Theatre Display.

**What's NOT in this document** (belongs in separate specs):
- Android Companion App UI (camera streaming app)
- Surgeon Profile settings/preferences screen
- Admin/hospital configuration panel
- Post-surgery review/teaching mode replay interface

[ignoring loop detection]

# ShalyaMitra — Extended Frontend Specifications (Part 2)

---

## 16. Android Companion App UI

> *The bridge between the operating theatre and the cloud brain.*

### 16.1 App Identity

**Name:** ShalyaMitra Companion
**Platform:** Android 10+ (API 29+)
**Language:** Kotlin
**Core SDK:** LiveKit Android SDK + CameraX

The Companion App serves two roles: **camera streaming device** (for all 3 phones) and **surgeon's personal neckband audio bridge** (for the surgeon's phone specifically).

### 16.2 Design System — "Nael Dark Mobile"

Same colour foundation as Theatre Display but adapted for small screen:

- Background: `#000000`
- Surface: `#0A0A0F`
- Accent: Nael Blue `#3D8BFF`
- Status colours: Green `#22C55E` (connected), Red `#FF3B4A` (error), Amber `#FFB020` (warning)
- Font: Inter (UI), JetBrains Mono (data)
- All text minimum 16sp for gloved-hand readability
- Buttons minimum 56dp touch targets — surgical gloves reduce touch precision

### 16.3 App Flow

```
LAUNCH
  │
  ├── First time → Hospital WiFi Setup + Server Configuration
  │
  └── Returning → Auto-connect attempt
          │
          ├── Success → Role Selection Screen
          │
          └── Failure → Connection Troubleshoot Screen
```

### 16.4 Screen 1: Role Selection

After connecting to the ShalyaMitra server, the user selects what this phone will do:

```
┌─────────────────────────────────┐
│                                 │
│   SHALYAMITRA COMPANION         │
│   ● Connected to GPU Session    │
│   Surgery: Dr. Shivalumar       │
│   Session: #2026-04-20-001      │
│                                 │
│   Select Role for This Device:  │
│                                 │
│  ┌─────────────────────────┐    │
│  │  📷 SURGEON CAMERA      │    │
│  │  Head-mounted, Eye One  │    │
│  │  Rear camera, 1080p     │    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │  📺 MONITOR CAMERA      │    │
│  │  Fixed on patient monitor│    │
│  │  Rear camera, 1080p     │    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │  🔭 OVERHEAD CAMERA     │    │
│  │  Boom/ceiling mount     │    │
│  │  Rear camera, wide-angle│    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │  🎧 AUDIO BRIDGE ONLY   │    │
│  │  Neckband audio relay   │    │
│  │  No camera streaming    │    │
│  └─────────────────────────┘    │
│                                 │
└─────────────────────────────────┘
```

- Large cards, easy to tap with gloved hands
- Each card shows which camera/CameraX config it will use
- "Audio Bridge Only" option for the anaesthesiologist's phone (connects neckband audio but no camera needed if a dedicated overhead camera is used)

### 16.5 Screen 2: Active Streaming — The "Set and Forget" Screen

Once role is selected, the phone becomes a dedicated streaming device. The screen must be **minimal** — this phone is mounted on a tripod/headband and won't be interacted with during surgery.

```
┌─────────────────────────────────┐
│                                 │
│  ┌─────────────────────────┐    │
│  │                         │    │
│  │   LIVE CAMERA PREVIEW   │    │
│  │   (small viewfinder)    │    │
│  │                         │    │
│  │   [what the camera sees]│    │
│  │                         │    │
│  └─────────────────────────┘    │
│                                 │
│  ● STREAMING — MONITOR CAMERA  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                 │
│  Resolution: 1080p @ 30fps      │
│  Bitrate: 2.8 Mbps             │
│  Latency: 87ms                  │
│  WiFi Signal: ████░ Strong      │
│                                 │
│  🔋 Battery: 78%  (~3h 12m)    │
│  🌡️ Temp: 38°C (Normal)       │
│                                 │
│  ┌──────────┐  ┌──────────┐    │
│  │ 🔦 LIGHT │  │ ⚙️ FOCUS │    │
│  └──────────┘  └──────────┘    │
│                                 │
│  Session: 01:23:45 elapsed      │
│                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  [        STOP STREAMING       ]│
│  (requires confirmation)        │
│                                 │
└─────────────────────────────────┘
```

**Key features:**

- **Live preview** (small, 40% of screen) — so the person mounting the phone can verify angle and framing
- **Connection status** with green pulsing dot — confidence that streaming is active
- **Technical metrics** — resolution, bitrate, latency, WiFi signal. Visible but not prominent.
- **Battery prediction** — estimated remaining stream time at current consumption. Critical for 3+ hour surgeries.
- **Temperature monitoring** — phones running continuous camera + WebRTC get hot. Amber warning at 42°C, red at 45°C with suggestions (reduce resolution, remove case).
- **Quick controls** — flashlight toggle (useful for monitor camera in dim ORs), focus lock/unlock
- **Screen stays on** — wake lock active, screen dims to lowest brightness after 30s of no touch to save battery, but never sleeps
- **Stop button** requires confirmation dialog ("Are you sure? Surgery may still be active.") — prevent accidental disconnection

### 16.6 Screen 3: Audio Bridge Mode (Surgeon's Phone)

When the surgeon's phone is also serving as the audio bridge for the BT neckband:

```
┌─────────────────────────────────┐
│                                 │
│  ┌─────────────────────────┐    │
│  │   CAMERA PREVIEW        │    │
│  │   (streaming active)    │    │
│  └─────────────────────────┘    │
│                                 │
│  ● STREAMING — SURGEON CAMERA  │
│                                 │
│  ┌── AUDIO STATUS ───────────┐  │
│  │                           │  │
│  │  🎧 Neckband: Connected   │  │
│  │  Jabra Evolve2 65         │  │
│  │  BT Codec: aptX LL       │  │
│  │                           │  │
│  │  🎤 Mic: Active           │  │
│  │  ░░░░░███░░░ (voice level)│  │
│  │                           │  │
│  │  🔊 Nael Audio: Ready     │  │
│  │  Volume: ████████░░ 80%   │  │
│  │                           │  │
│  │  Last Nael response: 2m ago│  │
│  └───────────────────────────┘  │
│                                 │
│  🔋 82%  WiFi:Strong  38°C     │
│                                 │
└─────────────────────────────────┘
```

- Shows BT neckband connection status, codec, and battery (if available from BT metadata)
- Live microphone level visualisation — surgeon can verify their voice is being captured
- Nael audio output status — confirms that AI responses will play through the neckband
- Volume slider for Nael's voice in the earpiece

### 16.7 Screen 4: Connection Troubleshoot

If connection fails:

```
┌─────────────────────────────────┐
│                                 │
│  ⚠ CONNECTION ISSUE             │
│                                 │
│  Cannot reach ShalyaMitra       │
│  GPU Session                    │
│                                 │
│  Checklist:                     │
│  ✅ WiFi connected (OR-WiFi-6)  │
│  ❌ GPU Server not responding   │
│  ── LiveKit Server: timeout     │
│                                 │
│  Possible causes:               │
│  • GPU session not started yet  │
│  • Wrong WiFi network           │
│  • Server IP changed            │
│                                 │
│  ┌─────────────────────────┐    │
│  │    RETRY CONNECTION     │    │
│  └─────────────────────────┘    │
│  ┌─────────────────────────┐    │
│  │    CONFIGURE SERVER     │    │
│  └─────────────────────────┘    │
│  ┌─────────────────────────┐    │
│  │    CONTACT SUPPORT      │    │
│  └─────────────────────────┘    │
│                                 │
└─────────────────────────────────┘
```

Automated checklist that tests WiFi → DNS → Server ping → LiveKit handshake, showing ✅/❌ for each step.

### 16.8 App Behaviour — Critical Details

- **Auto-reconnect:** If WiFi drops momentarily (common in hospitals), the app reconnects automatically within 5 seconds. During disconnection, the status dot turns amber and shows "Reconnecting..."
- **Background streaming:** If the phone screen is accidentally locked or another app opens, camera streaming continues via a foreground service with persistent notification
- **Battery optimisation bypass:** App requests exemption from Android battery optimisation on first launch — critical for 3+ hour streaming
- **Rotation lock:** Locked to portrait for monitor/overhead cameras, locked to landscape for surgeon camera — based on selected role
- **No sensitive data stored:** The app streams only. No patient data, no recordings, no transcriptions are stored on the phone. Pure relay device.

---

## 17. Surgeon Profile Settings & Preferences

> *Where Nael becomes YOUR Nael.*

This is a **web-based settings panel** (part of the main Next.js app) accessed on a laptop/tablet OUTSIDE the operating theatre — never during surgery.

### 17.1 Access

URL: `shalyamitra.local/profile` or cloud: `app.shalyamitra.com/profile`
Auth: Surgeon login (email + password or hospital SSO)

### 17.2 Design

Same "Nael Dark" design system but with more interactive depth — this is a settings environment, not a glanceable surgical display:

- Background: `#0A0A0F`
- Cards: `#12121A` with subtle 1px `#1A1A25` borders
- Accent: Nael Blue throughout
- Comfortable spacing — this isn't a "3 metres away" UI
- Standard web font sizes (14–16px body)

### 17.3 Navigation

Left sidebar navigation:

```
┌── SURGEON PROFILE ─────────────────────────────────────────────┐
│                                                                │
│  ┌──────────┐                                                  │
│  │ SIDEBAR  │  CONTENT AREA                                    │
│  │          │                                                  │
│  │ 👤 Profile│                                                 │
│  │ 🎤 Voice │                                                  │
│  │ 🔔 Alerts │                                                 │
│  │ 📺 Display│                                                 │
│  │ 📊 History│                                                 │
│  │ 🔒 Privacy│                                                 │
│  │ ⚙️ System │                                                 │
│  │          │                                                  │
│  └──────────┘                                                  │
└────────────────────────────────────────────────────────────────┘
```

### 17.4 Settings Sections

**A. Profile — Personal & Clinical**

| Setting | Type | Description |
|---|---|---|
| Name, Title, Speciality | Text fields | Dr. Shivalumar, MS General Surgery |
| Hospital(s) | Multi-select | Linked hospitals where surgeon operates |
| Preferred language | Dropdown | English / Hindi / English-Hindi mix / Kannada / Tamil / etc. |
| Preferred terminology | Toggle | Eponyms vs Descriptive ("Calot's triangle" vs "hepatocystic triangle") |
| Classical training | Toggle | Show Ayurvedic/Shalyatantra content (Oracle active) or modern-only mode |
| Speciality modules | Checklist | General, Ortho, Neuro, Cardiac, Ophthalmic, Ayurvedic Shalya |

**B. Voice Preferences — How Nael Speaks to You**

| Setting | Type | Description |
|---|---|---|
| Response verbosity | Slider (1–5) | 1 = single sentence answers. 5 = detailed explanations with context |
| Proactive alerts | Toggle per alert type | Which unsolicited alerts the surgeon wants (can suppress retraction timer, for example) |
| Nael voice profile | Audio preview selector | Choose Nael's voice character — calm male, calm female, neutral, etc. |
| Response speed | Slider | Speaking rate of Nael's TTS output |
| Wake word sensitivity | Slider | How sensitive "Nael" detection is — higher = fewer misses but more false triggers |
| Alert volume | Separate sliders | Critical alerts vs conversational responses — many surgeons want alerts louder than conversation |
| Pharmacist channel | Toggle | Whether the surgeon also hears Pharmacist alerts or only the anaesthesiologist does |

**C. Alert Preferences — What Deserves Your Attention**

A matrix of all alert types with per-alert configuration:

| Alert | Audio | Display | Threshold |
|---|---|---|---|
| Haemorrhage detection | 🔊 Always (locked) | 📺 Always (locked) | Cannot disable — safety-critical |
| Instrument count discrepancy | 🔊 Always (locked) | 📺 Always (locked) | Cannot disable — safety-critical |
| BP predictive trend | 🔊 On/Off | 📺 On/Off | Configure: alert at projected decline of ___ mmHg |
| HR trend | 🔊 On/Off | 📺 On/Off | Configure threshold |
| SpO₂ trend | 🔊 On/Off | 📺 On/Off | Configure threshold |
| Retraction timer | 🔊 On/Off | 📺 On/Off | Configure: alert at ___ minutes (default 20) |
| Sterile field breach | 🔊 On/Off | 📺 On/Off | Sensitivity slider |
| Team endurance | 🔊 On/Off | 📺 On/Off | Configure: suggest break after ___ hours |
| Devil's Advocate | 🔊 Always (locked) | 📺 Always (locked) | Cannot disable — safety-critical |

**Locked alerts (🔒):** Haemorrhage, Count, and Devil's Advocate CANNOT be disabled. These are safety-critical and non-negotiable. The UI shows a lock icon with tooltip: "This alert is locked for patient safety and cannot be disabled."

**D. Display Preferences**

| Setting | Type | Description |
|---|---|---|
| Default layout | Dropdown | Theatre Overview / Surgeon Focus / Custom |
| Default expanded camera | Dropdown | Which camera is expanded in Surgeon Focus mode |
| Overlay opacity | Slider (30–100%) | How opaque the anatomy/marma overlays are on camera |
| Marma auto-display | Toggle | Show Marma indicators automatically or only on request |
| PK dashboard visibility | Toggle | Always visible in corner or only on request |
| Shloka display | Toggle | Show Devanagari, transliteration, or both |
| Colour-blind mode | Dropdown | Normal / Deuteranopia / Protanopia / Tritanopia (shifts alert colours to safe alternatives) |
| Display brightness | Slider | Adapt to OR lighting conditions |

**E. Surgery History — The Surgeon's Mirror**

A chronological list of all surgeries with ShalyaMitra:

```
┌── SURGERY HISTORY ──────────────────────────────────────────────┐
│                                                                  │
│  ┌── 20 Apr 2026 ──────────────────────────────────────────────┐│
│  │  Laparoscopic Cholecystectomy                                ││
│  │  Duration: 2h 34m  |  Alerts: 3  |  Oracle: 2 queries       ││
│  │  Patient: [anonymised ID]                                    ││
│  │  [View Report]  [View Timeline]  [View AI Log]               ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌── 18 Apr 2026 ──────────────────────────────────────────────┐│
│  │  Open Appendicectomy                                         ││
│  │  Duration: 1h 12m  |  Alerts: 1  |  Oracle: 0 queries       ││
│  │  [View Report]  [View Timeline]  [View AI Log]               ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ── STATISTICS ──                                                │
│  Total surgeries: 23                                             │
│  Avg duration: 1h 48m                                            │
│  Most common alert: Retraction timer (14 occurrences)            │
│  Oracle usage: 34% of surgeries                                  │
│  Profile maturity: ████████░░ 80% (2 more surgeries to full)    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Profile maturity bar:** Shows progress toward full Surgeon Profile calibration (target: 10 surgeries). After 10: badge changes to "✓ Profile Complete — Nael is calibrated to your style."

**F. Privacy & Data Control**

| Setting | Description |
|---|---|
| Session data retention | How long raw session data is kept (30/60/90/180 days / indefinite) |
| Research consent | Granular: allow anonymised data for research? Per-surgery or blanket |
| Export my data | Download all personal data (GDPR/DPDP compliance) |
| Delete session | Delete any specific surgery session permanently |
| Delete all data | Nuclear option — removes all data from ShalyaMitra (requires 2FA confirmation) |
| AI training consent | Explicit toggle: "Allow my anonymised data to improve ShalyaMitra's models" — OFF by default |
| Access log | View every access to your data — who, when, what, from where |

---

## 18. Admin & Hospital Configuration Panel

> *The control centre for the IT team and chief surgeon.*

### 18.1 Access & Auth

URL: `shalyamitra.local/admin` or cloud: `app.shalyamitra.com/admin`
Auth: Hospital admin credentials (role-based: System Admin, Chief Surgeon, IT Admin)
All admin actions are logged with full audit trail.

### 18.2 Dashboard — System Health

```
┌── SHALYAMITRA ADMIN — [Hospital Name] ──────────────────────────┐
│                                                                  │
│  ┌── ACTIVE SESSIONS ─────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  OT-3: Dr. Shivalumar — Lap Chole — 01:23 elapsed         │  │
│  │  GPU: H100 (Nebius) — VRAM 42/80GB — Health: ✅            │  │
│  │  Cameras: 3/3 ✅  Audio: 2/2 ✅  Display: ✅              │  │
│  │  [Monitor Session]                                         │  │
│  │                                                            │  │
│  │  OT-1: Dr. Priya — Thyroidectomy — 00:45 elapsed          │  │
│  │  GPU: H100 (Lightning) — VRAM 38/80GB — Health: ✅        │  │
│  │  Cameras: 3/3 ✅  Audio: 1/2 ⚠ (anaesth neckband offline)│  │
│  │  [Monitor Session]                                         │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌── TODAY'S STATS ────┐  ┌── INFRASTRUCTURE ─────────────────┐  │
│  │ Surgeries: 4/6      │  │ WiFi AP: ✅ Strong (all OTs)     │  │
│  │ GPU hours used: 7.2h│  │ Cloud API: ✅ 34ms latency       │  │
│  │ Cost today: ₹5,920  │  │ Riva: ✅ Running                 │  │
│  │ Alerts fired: 12    │  │ Holoscan: ✅ 3 graphs active     │  │
│  │ Oracle queries: 8   │  │ LLM (NIM): ✅ Nemotron loaded    │  │
│  └─────────────────────┘  │ Storage: 234GB / 1TB             │  │
│                           └───────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 18.3 Admin Sections

**A. Surgeon Management**

| Feature | Description |
|---|---|
| Add/remove surgeons | Create accounts, assign to OTs |
| View surgeon profiles | Read-only view of profile settings (admin cannot modify surgeon preferences) |
| Surgery schedule | Calendar integration — pre-schedule GPU sessions |
| Usage analytics | Per-surgeon: surgery count, avg duration, alert patterns, Oracle usage |

**B. Theatre Configuration**

Per-OT setup:

| Setting | Description |
|---|---|
| Theatre name/number | OT-1, OT-2, etc. |
| Display device | IP/hostname of the Smart TV/Chromium device |
| WiFi network | SSID and credentials for OR WiFi |
| Camera positions | Default roles for phones in this OT |
| Secondary display | Optional — anaesthesia station display config |
| GPU provider preference | Nebius / Lightning AI / DGX Cloud — priority order |
| Pre-warm schedule | Auto-start GPU session N minutes before scheduled surgery |

**C. GPU & Cost Management**

```
┌── GPU COST DASHBOARD ───────────────────────────────────────────┐
│                                                                  │
│  This Month: ₹47,320 (62 surgeries, 186 GPU hours)              │
│                                                                  │
│  ┌── DAILY COST GRAPH ─────────────────────────────────────┐    │
│  │  Bar chart: cost per day over last 30 days               │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Average cost/surgery: ₹763                                      │
│  Avg GPU session: 3.0 hours                                      │
│  Provider breakdown: Nebius 78% | Lightning 22%                  │
│                                                                  │
│  Budget alert: Set monthly budget → alert at 80% ── [₹60,000]  │
│                                                                  │
│  DGX Cloud credits remaining: ₹1,24,000 (Inception programme)  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**D. AI Model Management**

| Setting | Description |
|---|---|
| ASR model | Select Riva model variant (Parakeet TDT 0.6B default) |
| Custom vocabulary | Upload/edit surgical vocabulary list for ASR fine-tuning |
| TTS voice profiles | Manage voice profiles for each intelligence pillar |
| Vision models | YOLOv11 weights version, MONAI bundles installed |
| LLM model | Nemotron version, quantisation level (INT4/FP8) |
| Wake word sensitivity | Global default (surgeons can override individually) |
| Alert pre-recorded audio | Upload/regenerate alert audio library |

**E. Data & Compliance**

| Setting | Description |
|---|---|
| Data retention policy | Hospital-wide default retention period |
| Encryption status | Verify AES-256 at rest, TLS 1.3 in transit |
| Audit log viewer | Every system access, every data export, every deletion — filterable |
| DPDP compliance report | Auto-generated compliance report for regulatory submission |
| CDSCO documentation | Export AI decision logs in CDSCO-required format |
| Research data export | Batch export anonymised data for approved research projects |
| Consent management | Track patient consent status per surgery session |

**F. System Diagnostics**

- **Health check dashboard:** Real-time status of every component (LiveKit, Riva, Holoscan, NIM, Qdrant, Redis, PostgreSQL)
- **Latency monitor:** End-to-end latency measurements for both audio paths
- **GPU session logs:** Start/stop times, VRAM usage curves, error logs
- **Alert replay:** Replay any alert event to verify correct behaviour
- **Network analyser:** WiFi throughput test per OT, bandwidth allocation

---

## 19. Post-Surgery Review & Teaching Mode Interface

> *Every surgery becomes a classroom.*

### 19.1 Access

URL: `app.shalyamitra.com/review` or `shalyamitra.local/review`
Auth: Surgeon (own surgeries), Resident (assigned cases), Faculty (all cases in department)

### 19.2 Design

Shifts from "Nael Dark" to **"Scholar Warm"** design:
- Background: `#0F0F14` (slightly warmer black)
- Surface: `#161620`
- Accent: Scholar Warm White `#F5E6D3`
- Secondary: Nael Blue `#3D8BFF`
- This is a learning environment, not a live surgical cockpit — slightly warmer, more contemplative

### 19.3 Surgery Library — Case Browser

```
┌── SURGICAL LIBRARY ─────────────────────────────────────────────┐
│                                                                  │
│  ┌── FILTERS ────────────────────────────────────────────────┐  │
│  │ Surgeon: [All ▼]  Procedure: [All ▼]  Date: [Range ▼]    │  │
│  │ Tags: [Complication ▼]  Oracle Used: [Yes/No ▼]           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌── CASE CARD ──────────────────────────────────────────────┐  │
│  │  📋 Laparoscopic Cholecystectomy                          │  │
│  │  Dr. Shivalumar  |  20 Apr 2026  |  2h 34m                │  │
│  │                                                            │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐                               │  │
│  │  │thumb1│ │thumb2│ │thumb3│  ← camera thumbnails (key      │  │
│  │  │      │ │      │ │      │    frames auto-selected by AI) │  │
│  │  └──────┘ └──────┘ └──────┘                               │  │
│  │                                                            │  │
│  │  Tags: Haemorrhage Event | Marma Consultation | TIVA       │  │
│  │  Alerts: 3  |  Oracle: 2 queries  |  DA: 1 intervention   │  │
│  │                                                            │  │
│  │  [OPEN REVIEW]  [VIEW REPORT]  [TEACHING ANNOTATE]        │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [More cases below...]                                           │
└──────────────────────────────────────────────────────────────────┘
```

- AI auto-generates thumbnail keyframes from the 3 cameras at significant moments
- Tag system: auto-tagged by AI (complication types, Oracle usage, alert types) + manual tags by surgeon
- Search by procedure type, date range, specific events, or specific structures encountered

### 19.4 Surgery Replay — The Core Teaching Interface

This is the most complex screen. It's a **multi-track surgical video player** with synchronised AI annotation, timeline, and knowledge layers.

```
┌── SURGERY REPLAY ───────────────────────────────────────────────┐
│                                                                  │
│  ┌─────────────────────────────────┐  ┌───────────────────────┐ │
│  │                                 │  │                       │ │
│  │     PRIMARY VIDEO VIEW          │  │  AI ANNOTATION PANEL  │ │
│  │     (selected camera)           │  │                       │ │
│  │                                 │  │  At this moment:      │ │
│  │     [AI overlays rendered       │  │                       │ │
│  │      on the video frame]        │  │  🔬 Eye: "Approaching │ │
│  │                                 │  │  hepatoduodenal       │ │
│  │                                 │  │  ligament"            │ │
│  │                                 │  │                       │ │
│  │                                 │  │  📊 Vitals: HR 76,   │ │
│  │                                 │  │  BP 118/72, stable    │ │
│  │                                 │  │                       │ │
│  │                                 │  │  🔧 Instruments: 8/14│ │
│  │                                 │  │  in field             │ │
│  └─────────────────────────────────┘  │                       │ │
│                                       │  💬 Nael: (transcript │ │
│  ┌──────┐ ┌──────┐ ┌──────┐          │  of conversation at   │ │
│  │ CAM1 │ │ CAM2 │ │ CAM3 │          │  this timestamp)      │ │
│  │(mini)│ │(mini)│ │(mini)│          │                       │ │
│  └──────┘ └──────┘ └──────┘          └───────────────────────┘ │
│                                                                  │
│  ┌── TIMELINE ──────────────────────────────────────────────┐   │
│  │  ▶ ──●────●───●──────●──────●────●──────●───────●── ■    │   │

[ignoring loop detection]

# ShalyaMitra — Extended Frontend Specs (Part 2)

---

## 16. Android Companion App UI

### Design System
Same "Nael Dark" adapted for mobile. Background `#000000`, accent `#3D8BFF`. Minimum text 16sp, buttons 56dp (gloved hands). Font: Inter + JetBrains Mono.

### App Flow
Launch → Auto-connect → Role Selection → Active Streaming

### Screen 1: Role Selection
After connecting to GPU session, select this phone's role via large tap-friendly cards:
- **📷 Surgeon Camera** — Head-mounted, rear camera, 1080p
- **📺 Monitor Camera** — Fixed on patient monitor, rear camera
- **🔭 Overhead Camera** — Boom/ceiling mount, wide-angle
- **🎧 Audio Bridge Only** — Neckband relay, no camera (for anaesthesiologist's phone)

Each card shows which CameraX config activates. Single tap, no menus.

### Screen 2: Active Streaming ("Set and Forget")
Once role selected, the phone becomes a dedicated streaming device:

- **Live camera preview** (40% of screen) — verify angle during mounting
- **Green pulsing dot** — "STREAMING — MONITOR CAMERA"
- **Metrics:** Resolution (1080p@30fps), bitrate, latency (ms), WiFi signal strength
- **Battery prediction:** "🔋 78% (~3h 12m remaining)" — critical for long surgeries
- **Temperature monitor:** Amber at 42°C, red at 45°C (phones get hot during continuous WebRTC)
- **Quick controls:** Flashlight toggle, focus lock/unlock
- **Screen behaviour:** Wake lock active. Dims to minimum brightness after 30s no-touch. Never sleeps.
- **Stop button:** Requires confirmation dialog — prevent accidental disconnection mid-surgery

### Screen 3: Audio Bridge (Surgeon's Phone)
When also serving as neckband audio bridge, shows additional panel:
- BT neckband connection status + codec (aptX LL / LC3)
- Live mic level visualisation (surgeon can verify voice capture)
- Nael audio output status + volume slider
- "Last Nael response: 2m ago"

### Screen 4: Connection Troubleshoot
If connection fails — automated checklist testing WiFi → DNS → Server ping → LiveKit handshake, showing ✅/❌ per step. Retry + Configure + Support buttons.

### Critical App Behaviours
- **Auto-reconnect** on WiFi drop (within 5s, amber "Reconnecting..." status)
- **Background streaming** via foreground service if screen locked
- **Battery optimisation bypass** requested on first launch
- **Rotation lock** per role (portrait for monitor/overhead, landscape for surgeon)
- **No sensitive data stored** on phone — pure relay device

### Tech Stack
Kotlin, CameraX (Jetpack), LiveKit Android SDK, Gradle, target Android 10+ (API 29+)

---

## 17. Surgeon Profile & Preferences

### Access
Web-based: `app.shalyamitra.com/profile` — accessed on laptop/tablet outside OR, never during surgery.

### Design
"Nael Dark" with interactive depth. Left sidebar navigation: Profile | Voice | Alerts | Display | History | Privacy | System

### Settings Sections

**A. Profile — Personal & Clinical**

| Setting | Type |
|---|---|
| Name, title, speciality | Text |
| Hospital(s) | Multi-select |
| Preferred language | Dropdown (English / Hindi / mix / regional) |
| Terminology style | Toggle: Eponyms vs Descriptive |
| Classical training | Toggle: Oracle active or modern-only |
| Speciality modules | Checklist: General, Ortho, Neuro, Cardiac, Ayurvedic Shalya |

**B. Voice — How Nael Speaks to You**

| Setting | Type |
|---|---|
| Response verbosity | Slider 1–5 (terse ↔ detailed) |
| Nael voice profile | Audio preview: calm male / calm female / neutral |
| Response speaking rate | Slider |
| Wake word sensitivity | Slider (fewer misses ↔ fewer false triggers) |
| Alert volume vs conversation volume | Separate sliders |
| Hear Pharmacist alerts? | Toggle (surgeon may want anaesth-only) |

**C. Alert Preferences — What Deserves Attention**

Matrix of all alert types with per-alert Audio ON/OFF, Display ON/OFF, threshold config.

**🔒 Locked alerts (cannot disable):** Haemorrhage, Instrument Count, Devil's Advocate. Lock icon with tooltip: "Locked for patient safety." These are non-negotiable.

Configurable thresholds: BP decline trigger (mmHg), retraction timer (default 20min), SpO₂ trend sensitivity, team endurance break suggestion (hours).

**D. Display Preferences**

| Setting | Description |
|---|---|
| Default layout state | Theatre Overview / Surgeon Focus / Custom |
| Default expanded camera | Which camera is primary |
| Overlay opacity | Slider 30–100% |
| Marma auto-display | Auto vs on-request only |
| Shloka display format | Devanagari / transliteration / both |
| Colour-blind mode | Normal / Deuteranopia / Protanopia / Tritanopia |

**E. Surgery History — The Surgeon's Mirror**

Chronological list of all surgeries:
- Per surgery: procedure, duration, alert count, Oracle queries
- Links: View Report | View Timeline | View AI Log
- **Aggregate stats:** Total surgeries, avg duration, most common alert type, Oracle usage %, profile maturity bar

**Profile maturity bar:** Progress toward full calibration (10 surgeries). After 10: "✓ Nael is calibrated to your style."

**F. Privacy & Data Control**

| Setting | Description |
|---|---|
| Data retention period | 30 / 60 / 90 / 180 days / indefinite |
| Research consent | Per-surgery or blanket toggle |
| Export my data | Full personal data download (DPDP compliance) |
| Delete session | Delete any specific surgery permanently |
| Delete all data | Nuclear option, requires 2FA |
| AI training consent | OFF by default. Explicit toggle. |
| Access log | Every access to your data — who, when, what |

---

## 18. Admin & Hospital Configuration Panel

### Access
`app.shalyamitra.com/admin` — Role-based: System Admin, Chief Surgeon, IT Admin. All actions audit-logged.

### Dashboard — System Health

Shows at a glance:
- **Active sessions:** Per-OT card showing surgeon, procedure, elapsed time, GPU health (VRAM usage), camera/audio/display status with ✅/⚠/❌
- **Today's stats:** Surgery count, GPU hours, total cost, alerts fired
- **Infrastructure status:** WiFi AP, Cloud API latency, Riva, Holoscan, NIM, storage usage

### Admin Sections

**A. Surgeon Management**
- Add/remove surgeon accounts, assign to OTs
- View profiles (read-only — admin cannot modify surgeon preferences)
- Surgery schedule with calendar integration for GPU pre-warming
- Usage analytics per surgeon

**B. Theatre Configuration (per OT)**

| Setting | Description |
|---|---|
| Theatre name/number | OT-1, OT-2, etc. |
| Display device | IP/hostname of Smart TV |
| WiFi network | SSID + credentials for OR WiFi |
| Default camera roles | Per-phone defaults for this OT |
| Secondary display | Anaesthesia station config |
| GPU provider priority | Nebius → Lightning AI → DGX Cloud |
| Pre-warm schedule | Auto-start GPU N minutes before scheduled surgery |

**C. GPU & Cost Management**

- Monthly cost dashboard with daily bar chart
- Average cost/surgery, provider breakdown
- Budget alert threshold (alert at 80% of monthly budget)
- DGX Cloud credit tracking (Inception programme remaining balance)
- Cost export for hospital finance

**D. AI Model Management**

| Setting | Description |
|---|---|
| ASR model variant | Riva Parakeet TDT version selection |
| Custom vocabulary | Upload surgical/Ayurvedic term list for ASR |
| TTS voice profiles | Manage per-pillar voice profiles |
| Vision model weights | YOLOv11 version, MONAI bundles |
| LLM model + quantisation | Nemotron version, INT4/FP8 |
| Alert audio library | Upload/regenerate pre-recorded alerts |

**E. Data & Compliance**

| Feature | Description |
|---|---|
| Hospital-wide retention policy | Default retention period |
| Encryption verification | AES-256 at rest, TLS 1.3 in transit status |
| Audit log viewer | Filterable log of every access/export/deletion |
| DPDP compliance report | Auto-generated for regulatory submission |
| CDSCO documentation export | AI decision logs in required format |
| Consent management | Track patient consent per session |

**F. System Diagnostics**
- Component health dashboard (LiveKit, Riva, Holoscan, NIM, Qdrant, Redis, PostgreSQL)
- End-to-end latency measurements for both audio paths
- GPU session logs with VRAM usage curves
- Network throughput test per OT
- Alert replay (verify any past alert fired correctly)

---

## 19. Post-Surgery Review & Teaching Mode

### Design Shift
Background warms slightly to `#0F0F14`. Accent shifts to Scholar Warm White `#F5E6D3`. This is a learning environment, not a cockpit.

### Access
`app.shalyamitra.com/review` — Auth levels: Surgeon (own), Resident (assigned), Faculty (department-wide)

### Surgery Library — Case Browser

Filterable grid of case cards:
- **Filters:** Surgeon, procedure type, date range, tags (complication type, Oracle used, alert types)
- **Case card:** Procedure name, surgeon, date, duration, 3 AI-selected keyframe thumbnails from cameras, auto-generated tags, alert/Oracle/DA count
- **Actions:** Open Review | View Report | Teaching Annotate

### Surgery Replay — Multi-Track Player

The core teaching interface. A video player unlike any medical review tool:

**Layout:**
- **Primary video** (65% width): Selected camera feed with AI overlays rendered on the frame
- **Camera switcher:** Three mini-thumbnails below — click to swap primary view. All three recorded and synchronised.
- **AI Annotation Panel** (35% right): Shows what the AI knew/did at the current timestamp:
  - Eye's anatomical recognition state
  - Vitals at this moment (from Monitor Sentinel)
  - Instrument count at this moment
  - Nael conversation transcript at this point
  - Oracle citations if active
  - Devil's Advocate interventions if any
- **Timeline scrubber** (bottom): Full surgery timeline with event markers

### Timeline — The Intelligent Scrubber

```
▶ ──●────●───●──────●──────●────●──────●───────●── ■
   Inc  Drug  Nael   Alert  Marma  DA   Alert  Close
```

- Horizontal timeline spanning full surgery duration
- **Event markers** as coloured dots using pillar colours:
  - Red dot = Haemorrhage alert
  - Amber dot = Monitor Sentinel alert
  - Blue dot = Nael conversation
  - Saffron dot = Oracle query
  - Orange dot = Devil's Advocate
  - Teal dot = Sentinel event (count, sterile field)
  - Violet dot = Drug administration
- Click any dot → video jumps to that moment, annotation panel updates
- **Hover** on dot → tooltip preview: "01:23:45 — Haemorrhage Sentinel: Arterial bleed detected"
- Standard playback controls: Play/Pause, 0.5×/1×/1.5×/2× speed, skip to next event, skip to previous event

### Overlay Replay

During replay, the AI overlays that were active during surgery can be toggled:
- **"Show AI overlays"** toggle — renders the anatomy/marma/bleed detection overlays exactly as they appeared during live surgery
- **"Show retrospective overlays"** toggle — renders overlays generated POST-surgery with better models (if available), showing what the AI would identify now
- This comparison is invaluable for teaching: "Here's what the AI saw in real-time vs what we know now"

### Teaching Annotations

Faculty can add **teaching annotations** to any moment in the replay:

- Click timeline → add text annotation at that timestamp
- Annotation types: "Teaching Point", "Common Mistake", "Alternative Approach", "Exam Relevant"
- Annotations appear as markers on the timeline (distinct colour — professor green `#4ADE80`)
- When a resident watches, annotations popup as cards alongside the AI annotation panel
- Faculty can record voice annotations (60s clips) attached to specific moments
- Annotations are per-case, shareable across the department

### Structured Review Reports

The Chronicler's outputs are viewable as formatted documents:

**Intraoperative Chronicle:**
- Complete timestamped event log
- Anaesthetic record with TIVA curves (interactive D3 charts)
- AI intervention log: every alert, every DA question, every Oracle consultation — with timestamp and reasoning context
- Downloadable as PDF for departmental records

**Handover Brief:**
- Formatted for print/share with receiving team
- Includes post-op watch parameters, suggested orders

**AI Decision Audit:**
- Every AI decision traceable: what was the input → what did the model output → what was displayed/spoken
- This is the CDSCO audit trail — viewable by admin and regulatory bodies
- Exportable as structured JSON for regulatory submission

### Research Mode View

For approved research:
- Batch selection of anonymised cases matching criteria
- Aggregate statistics dashboard: vital trends across N surgeries, alert frequency distributions, complication correlation analysis
- Export as CSV / Parquet for statistical analysis
- Oracle usage patterns: which shlokas are most consulted, in which surgical contexts
- All data is fully anonymised — no patient identifiers, no surgeon identifiers unless specifically consented

### Comparison View

Side-by-side comparison of two surgeries:
- Same procedure type, different outcomes — what differed?
- Synchronised playback at same surgical phase (AI aligns phases, not timestamps)
- Vitals overlay comparison: patient A trajectory vs patient B
- Invaluable for M&M (Morbidity & Mortality) conferences

---

## 20. Cross-Platform Consistency Summary

| Interface | Platform | Primary User | Design Theme |
|---|---|---|---|
| Theatre Display | Chromium kiosk on Smart TV | Surgeon (glance) | Nael Dark — pure black, maximum contrast |
| Android Companion | Kotlin native app | OR technician (setup) | Nael Dark Mobile — minimal, set-and-forget |
| Surgeon Profile | Next.js web app | Surgeon (outside OR) | Nael Dark — interactive settings |
| Admin Panel | Next.js web app | IT/Chief Surgeon | Nael Dark — data-dense dashboard |
| Teaching Review | Next.js web app | Faculty/Residents | Scholar Warm — contemplative, learning |

**Shared across all:** Pillar colour system, Inter/JetBrains Mono/Noto Sans Devanagari fonts, 8px spacing grid, glassmorphic panels, physics-based animations, accessibility compliance.

---

## 21. Implementation Priority

| Phase | Build | Why First |
|---|---|---|
| **Phase 1** | Theatre Display (States 1–5) + Android App (streaming only) | Core surgical experience — this IS the product |
| **Phase 2** | Theatre Display (States 6–7, overlays, PK) + Surgeon Profile | Full intelligence display + personalisation |
| **Phase 3** | Post-Surgery Review + Teaching Mode | Value multiplier — every surgery becomes education |
| **Phase 4** | Admin Panel + Research Mode + Comparison View | Scale infrastructure — multi-OT, multi-hospital |

---

This completes the full frontend specification for ShalyaMitra — covering all 5 interfaces (Theatre Display, Android App, Surgeon Profile, Admin Panel, Teaching/Review Mode), the design system, every layout state, the data protocol, component architecture, and implementation priority.
