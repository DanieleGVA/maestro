# Handoff — Maestro Student App (v1 MVP)

Mobile-first student-facing app for the MAESTRO learning platform. Twelve hi-fi screens covering authentication, onboarding & profiling, daily navigation, knowledge map, gap-recovery missions, quizzes, personalised review documents, profile/preferences and the "Why this?" explainability sheet.

---

## About the design files

The files in this bundle are **design references created in HTML/JSX** — prototypes that demonstrate the intended look, layout and micro-interactions. They are **not** production code to copy verbatim.

The task is to **recreate these designs in the target codebase's environment**, using whatever stack and conventions are already in place (React Native, Flutter, SwiftUI, native Android, etc.). If no codebase exists yet, choose the framework that best fits the team and recreate the designs there. Match the visual system pixel-perfectly; do not lift the JSX as-is.

---

## Fidelity

**High-fidelity.** Final colours, typography, spacing, illustrations, copy and component composition are settled. Numbers (sizes, paddings, radii) in this README are authoritative — defer to them when the HTML/JSX disagrees.

Animations are not specified in the prototype (the HTML is static); they are documented below as design intent.

---

## Audience & tone

The app is used by **secondary-school teenagers (14–19)**. The aesthetic is intentionally bold and editorial — closer to a music magazine or a focused productivity tool than a "school portal".

Tone rules (non-negotiable, from the source spec):
- **Gaps ("lacuna") are reframed as missions** — "an open door, not a brand". Never punitive.
- **Never compare students.** No leaderboards, no peer rankings.
- **State indicators always use colour + icon + text** (accessibility / colour-blindness, per F9.3).
- **All copy in English** (this build); the production system is bilingual per F13.
- Headlines mix upright + italic display serifs to create rhythm — the italic word is the emphasis.

---

## Design tokens

### Colours

| Token | Hex | Use |
|---|---|---|
| `--ink` | `#14110D` | Primary background (dark surfaces) |
| `--ink-2` | `#1C1813` | Cards, raised surfaces |
| `--ink-3` | `#2A241C` | Tertiary fill, inactive |
| `--ink-line` | `#3A3327` | Borders on dark |
| `--bone` | `#F5EFE3` | Primary text on dark; light surface bg |
| `--bone-2` | `#ECE4D2` | Light alt |
| `--bone-3` | `#D9CFB8` | Light alt 2 |
| `--bone-line` | `#C8BDA1` | Borders on light |
| `--paper` | `#FBF7EE` | Document/reader background |
| `--char` | `#14110D` | Primary text on light |
| `--signal` | `#D4FF3D` | Brand pop, CTAs, active accents |
| `--signal-2` | `#E8FF7A` | Signal highlight |
| `--signal-ink` | `#0B1300` | Text on signal lime |

### Semaphore (state) colours — always pair with icon + text

| State | Hex | Icon glyph | Soft bg (on dark) |
|---|---|---|---|
| `red` — open gap | `#E74C3C` | `✕` | `#3A1F1A` |
| `orange` — in recovery | `#FF8A3D` | `↑` | `#3A2519` |
| `yellow` — to review | `#F5C53D` | `◷` | `#3A2F12` |
| `green` — consolidated | `#4ADE80` | `✓` | `#173220` |
| `white-st` — introduced | `#E7E0CE` | `○` | — |
| `gray` — not introduced | `#8A8275` | `·` | — |

### Typography

- **Display**: `Instrument Serif` (regular + italic). Used for headlines and the wordmark. Letter-spacing `-0.02em`, line-height `0.95`.
- **UI sans**: `Geist` (300/400/500/600/700). Body, controls, navigation. Letter-spacing `-0.01em`.
- **Mono**: `JetBrains Mono` (400/500). Eyebrows, tags, timestamps, technical labels. Letter-spacing `0.14em–0.18em`, often `text-transform: uppercase`.

Display sizes used across screens: `56 / 52 / 36 / 30 / 28 / 26 / 24 / 22 / 18`.
UI body: `13–16 px`. Mono "eyebrow": `9–11 px`.

### Radii

`8 / 12 / 18 / 24 / 32` — used as `--r-xs / --r-sm / --r-md / --r-lg / --r-xl`. Buttons and pills use full `100px` (capsule).

### Spacing

Screen horizontal padding: `20–28 px` (`24` is the workhorse).
Vertical rhythm: `8 / 12 / 14 / 18 / 22 / 24 / 32 / 40`.

### Safe areas (mobile)

- Top safe area: `64 px` (status bar + dynamic island, iOS reference).
- Bottom safe area: `28–48 px` (home indicator + optional CTA breathing room).

### Wordmark

`Maestro` set in `Instrument Serif`, followed by a signal-lime `.` (period).

### Buttons

- **Primary**: signal-lime fill, ink text, capsule, `padding: 16px 22px`, `font-weight: 600`, `font-size: 15px`. Trailing arrow icon when it implies progress.
- **Ghost**: transparent, 1px `--ink-line` border, bone text (on dark) or ink (on light).
- **Solid dark**: ink-2 fill, ink-line border, bone text — used as alternate CTA.

### Pills (state badges)

`padding: 4px 9px`, `border-radius: 100px`, `font-size: 11px`, `font-weight: 500`, `1px` border in `currentColor @ 0.4`. Icon + text always.

---

## Screens

There are **12 hi-fi screens**, grouped in four sections.

### 01 · Sign in & set up

#### SCR-ST-01 — Login (`ScreenLogin`)
- **Background**: `--ink` with a radial signal-lime glow in the top-right corner.
- **Wordmark** top-left, mono version `v 1.0` top-right.
- **Hero**: display serif "Pick up *where* you left off." — three lines, 52 px. The word "where" is italic.
- **Fields**: two stacked field cards (`--ink-2` fill, `--ink-line` border, `r:18`). Each field shows a mono eyebrow label (USERNAME / PASSWORD) above the value. Password field has a trailing eye icon.
- **Primary CTA**: "Log in →" full-width.
- **Below CTA**: muted line "or _continue with school SSO_" (underline on the SSO portion).
- **Footer**: mono micro-text "forgot password? · ask your school IT".

#### SCR-ST-02a — Onboarding welcome (`ScreenOnbWelcome`) — light
- **Background**: full `--signal` (lime). Content uses `--signal-ink`.
- **Header**: small wordmark left, "Skip ›" text button right.
- **Progress bar**: 5 horizontal segments, first one filled (ink), rest at 18% opacity.
- **Eyebrow**: `step 1 of 5`.
- **Hero**: "Let's find *how you* learn best." (display, 56 px, "how you" italic).
- **Body**: "Not a graded test. Just a 5-minute vibe check so we can tune Maestro to *your* brain." (the word "your" is set in display serif italic inline).
- **Modality chips**: capsule chips for `Read · Listen · Watch · Try`. The fourth (`Try`) is filled ink, lime text — preview of what's next.
- **CTA**: "Let's go →", ink fill, lime text.

#### SCR-ST-02b — Modality quiz step (`ScreenOnbQuiz`)
- Same chrome as login but progress shows step 3/5.
- **Hero**: "What's a *variable*?" (28 px).
- **2×2 grid of modality cards** (Read / Listen / Watch / Try). Each card: `r:18`, 140 px min-height, top-left icon (24 px), bottom display title (22 px) + tiny blurb (11 px, 65% opacity).
  - `Read` is currently **active** — filled bone on ink; top-right mono badge `OPEN`.
  - `Try` is **done** — top-right green circle with checkmark (20 px).
  - Others are idle (`--ink-2` fill, `--ink-line` border).
- **Telemetry hint** row: `✦ You spent 42s reading. Maestro is paying attention.` (12 px, sparkle in signal).
- **CTA**: "Next concept →".

#### SCR-ST-02c — Result / radar (`ScreenOnbResult`)
- Hero: "You're a *visual,* hands-on type." (30 px).
- **Radar chart** (260×260 px SVG) — 5 axes: VISUAL · AUDITORY · HANDS-ON · REFLECTIVE · SOCIAL.
  - Grid: 4 concentric pentagons at 25/50/75/100%, stroke `bone @ 8%`.
  - Spokes: same opacity.
  - Fill polygon: `signal @ 18%`, stroke `signal` 2 px, with 3.5 px signal vertices.
  - Axis labels: mono 9 px, `bone @ 70%`.
- Two chip rows below the chart:
  - **Tone**: Casual / Calm / Formal (Casual active).
  - **Length**: Short / Deep dive (Short active).
- CTA: "Looks like me →", secondary text-link "I want to tweak it manually".

---

### 02 · Daily nav

#### SCR-ST-03 — Home (`ScreenHome`)
- **Header row**: left = mono date (`WED · 18 MAY`) + display greeting (`Hey *Leo*.`, 26 px). Right = bell button (38×38, with signal-lime unread dot) + signal avatar (38×38 rounded square, letter `L`, 14 px bold).
- **Streak strip**: ink-2 card with flame icon (orange), "12-day streak" + mono `3 MISSIONS · 86 XP THIS WEEK`. Trailing weekly bars (7 thin bars, last one dim).
- **Section: your missions** — horizontal carousel, sliding cards (`flex: none`, gap 12). Three cards:
  1. **Open gap — SQL JOIN** — bone-filled card, red pill `✕ OPEN GAP`. Display title 30 px. Black "Start mission →" CTA. Width 260, height 200.
  2. **In recovery — PHP sessions** — ink-2 card, orange pill, signal CTA "Continue →". 200×180.
  3. **Review — Arrays** — ink-2 card, yellow pill, "Quiz me →" CTA. 200×180.
- **Mini-map** card: small node graph SVG (~80 px tall) showing the student's tree at a glance with colour-coded nodes. Below the graph: legend dots with counts (`● 12 ● 4 ● 1 ● 1`) and "See full map →" link.
- **Tabbar** (bottom, fixed): Home (active, lime) · Map · Profile. Mono labels in uppercase. Gradient fade behind the bar.

#### SCR-ST-04 — Knowledge map (`ScreenMap`)
- Back button (38 px circle) + meta breadcrumb `INFORMATICS · 3AI` + display title "Your map".
- Right: segmented control `Macro / Micro` (capsule, light pill active = Macro).
- **Canvas**: SVG graph 400×440 viewBox, 10 nodes laid out in a 3-column tree.
  - Background has a 24-px dot/grid pattern at 4% opacity and a faint lime radial bloom top-left.
  - Nodes: 22 px (44 px for the root), filled in semaphore colours with 3 px ink stroke. Internal glyph for state (✓ ◷ ↑ ✕). Label beneath in 11 px sans, 85% opacity.
  - "Current" nodes (SQL JOIN, PHP sessions) get an outer 6 px signal-lime ring at 60% opacity.
- **Zoom controls**: top-right stack of `+ / −` 36-px tiles.
- **Legend** (bottom drawer, glass): mono "legend" eyebrow + 3-column grid of state rows (coloured dot, glyph, label).

#### SCR-ST-05 — Node detail (`ScreenNodeDetail`)
- Back + breadcrumb `Map / Database / **SQL JOIN**`.
- **Red pill** `✕ OPEN GAP · 5 DAYS`.
- **Hero**: "SQL *JOIN*" 36 px display, + one-line definition body.
- **Status block**: ink-2 card with a big 64-px red disc (✕) with a 6 px soft red halo + heading "Gap detected" + reassuring sub-copy + mono timestamp.
- **History timeline** (vertical):
  - 1-px ink-line vertical rail; each entry has a 13 px coloured pill marker.
  - Per entry: title + mono date right-aligned + secondary line ("PHP test — 2/10", etc.) + optional `OVERRIDE` mono tag for teacher actions.
- **Primary CTA**: "Start mission · 4 steps →" + below it three muted markers ("· Review doc · Watch the clip (2m) · Quiz").

---

### 03 · Close the gap

#### SCR-ST-06 — Mission (`ScreenMission`)
- Back + mono `MISSION · STEP 2 / 4`.
- Hero: "Mission: *SQL JOIN*" (36 px), sub-copy.
- **Step progress**: 4 horizontal bars (filled with signal for done steps).
- **Step list** (vertical, gap 10):
  - Each step is a row card. The current step uses a **bone fill / ink text** (inversion) for emphasis.
  - Each row: 38 px square icon tile (12 r) + title + 11 px sub + 0X mono index on the right + a small play icon if it's the current step.
  - Done steps show a green checkmark tile, todo steps are at 0.55 opacity.
- CTA at bottom: "Continue · watch clip →".

#### SCR-ST-07a — Quiz question (`ScreenQuizQuestion`) — light theme
- **Background**: `--bone`. Used to give the quiz a different mental space ("focus mode").
- Top row: close (X) button + 5-segment progress (`03 / 05`).
- Mono eyebrow + question display "What does an *INNER JOIN* do?" (30 px).
- **Options** (A–D): card per option, `r:18`, 1 px ink @ 12% border. Each option has a circular 28-px letter tile (mono uppercase) and a body string at 14 px.
  - Selected state: card flips to **ink fill, bone text**, and the letter tile becomes a **lime** disc with ink letter.
- CTA: "Confirm →", ink fill, bone text, full-width.

#### SCR-ST-07b — Quiz result (`ScreenQuizResult`)
- Subtle green radial bloom from the top.
- Top-right close button only.
- **Centre**: sparkle icon, mono `nailed it` (green), big display `4/5` (the slash is signal italic).
- Sub-copy "that's 80% · keep this in your head".
- **State change pill**: yellow `◷ SQL JOIN moved to "TO REVIEW"`.
- **By-question list** (5 rows):
  - Per row: 24-px green or orange status disc (✓ or ✕), mono Q-index, question, "review" link on the right.
- CTAs: primary "Back to your map →" + ghost "Try a fresh angle".

#### SCR-ST-08 — Review document (`ScreenDocument`) — light/paper theme
- **Background**: `--paper` for a long-form reader feel.
- Header: back + breadcrumb + outline button `✦ Why this?` (links to SCR-ST-10).
- Mono eyebrow `REVIEW · MADE FOR YOU` + display "PHP *sessions*" (30 px) + meta "3 min read · with a basketball analogy, like you wanted".
- **4 stacked blocks** with a 4-px left stripe each — never colour alone:
  1. **WHERE YOU SLIPPED** — yellow tone, mono ERROR badge, mono code block, body explanation.
  2. **THE BASKETBALL VERSION** — white tone (ink stripe), analogy text.
  3. **HOW IT WORKS RIGHT** — green tone, CORRECT badge, mono code block.
  4. **REMEMBER THIS** — full signal-lime card, the rule highlighted with an inline display-italic phrase.
- Bottom action row: secondary "Listen" (speaker icon) + primary "Try it →".

---

### 04 · You, in control

#### SCR-ST-09 — Profile & preferences (`ScreenProfile`)
- Back + mono eyebrow `YOUR SETUP` + display "Profile".
- **Identity card**: 56-px signal-lime square avatar (initial `L`, display serif), name "Leo Romano", meta "3AI · Informatics · 17 nodes solid".
- **"How I learn" card**: mini radar SVG (72 px) on the left + sentence "You're a **visual + hands-on** type. We'll lean into diagrams and tiny experiments." ("visual + hands-on" in signal).
- **Tone & length**: two segmented controls (Casual/Calm/Formal · Short/Deep dive).
- **Accessibility** card (ink-2 panel) with rows:
  - Font (Geist) — current value in signal
  - Text size slider with `A` … `A` labels and `17 pt` value
  - Theme segmented (Light/Dark/Sepia)
  - High contrast toggle
- CTA: "Save changes ✓".

#### SCR-ST-10 — Why this? explainability sheet (`ScreenExplain`)
- **Bottom-sheet over the document**. The page behind is dimmed; sheet has a top drag handle.
- Sheet: ink-2 fill, `r:28`, large soft shadow above.
- Header: sparkle (signal) + mono `MAESTRO REASONING` + display "Why am I showing you *this*?" (28 px).
- Three sections, each with mono uppercase label:
  - **CONCEPTS IN PLAY** — coloured state pills (red PHP sessions / yellow Output buffering).
  - **YOUR PROFILE** — short sentence summarising profile + tone + analogy preference.
  - **WHAT JUST HAPPENED** — bulleted history (coloured dots + dates + events).
- Two buttons stacked: ghost "Explain it more simply" + primary "Got it ✓".

---

## Interactions & behaviour

These are not visible in the static HTML; document them so dev can wire them.

### Navigation
- The app is **mobile-native first** (React Native, Flutter, SwiftUI…). Treat each screen as a route.
- Tab bar (Home / Map / Profile) is persistent in **SCR-ST-03 only** in the prototype; the production tab bar should persist across Home/Map/Profile and slide away when a flow takes over (quiz, document, mission, why-this).
- Back affordance: 38-px circular button top-left in every secondary screen.

### Onboarding flow
1. Login (SCR-ST-01) → first-time activation gating (terms + consent recap; not designed in v1 — see source spec) → SCR-ST-02a.
2. SCR-ST-02a → 4× SCR-ST-02b (one per concept) → SCR-ST-02c → Home.
3. Tracking per concept card: open, time-on-card, completion. If consent (a) is denied, run the simplified flow that drops behavioural tracking and assigns a neutral profile.

### Modality cards (SCR-ST-02b)
- Tap = expand inline content (Read = expand text; Listen = play audio; Watch = open image; Try = mini exercise).
- "Next concept" disabled until at least one card has been interacted with.
- Audio card shows a "Not available" badge if the asset is missing.

### Mission carousel (Home)
- Horizontal scroll, snap to card.
- Tap = navigate to mission (recovery) or quiz (review).
- Empty state copy: "No open missions — you're all caught up!" with a celebratory accent.

### Map (SCR-ST-04)
- Pinch-to-zoom + drag-to-pan. `+/−` controls bound to the same zoom range.
- Tap node → SCR-ST-05.
- Macro/Micro toggle: triennio (Yr 11–13) only; biennio (Yr 9–10) hides the toggle.
- **Keyboard nav** (where applicable): Tab between nodes, Enter to open, arrows to traverse adjacent nodes. Each node `aria-label` = "concept name · state text".

### Mission (SCR-ST-06)
- Steps are linear but can be revisited. The "Continue" CTA always points at the current step.
- "I'm done, take me to the quiz" enabled only after ≥1 study step completed.
- If a mission is abandoned and re-entered, resume at last completed step.

### Quiz (SCR-ST-07a/b)
- One question at a time, no back-navigation between questions during the quiz.
- After confirm: brief check transition, then advance.
- Result thresholds:
  - **≥ 80%** — green vibe, "to consolidate" state on the node.
  - **50–79%** — yellow vibe, offer a different mission articulation.
  - **< 50%** — orange vibe (**never red**), reassuring copy "we'll talk to your prof".
- During the quiz the language is the course's official language only (per F13.19). Bilingual rendering applies only to study materials.

### Document (SCR-ST-08)
- Read-only; the "Listen" button toggles a TTS player (V1; can be hidden in MVP if not yet available).
- "Why this?" → opens SCR-ST-10 as a modal bottom-sheet from the same screen.

### Why this? sheet (SCR-ST-10)
- Modal: focus-trap, dismiss with Esc / drag-down / X / "Got it".
- Announce as `dialog` to screen readers.
- "Explain it more simply" → re-renders the same three sections with simpler copy.

### Profile (SCR-ST-09)
- All controls keyboard-reachable.
- Text-size slider step from keyboard arrows; preview text reflects the change live.
- "Save changes" disabled while no field has changed (track a dirty flag).

### Microinteractions (suggested)
- 150 ms ease-out on hover/tap state changes.
- Mission progress bar: animate fill on step completion (300 ms).
- Quiz-result: brief 600 ms scale-in on the score number, optional confetti **off by default** (gamification gating).
- Radar chart: animate fill polygon on first render (path morph from 0% values).

### Empty / loading / error states
- **Loading** a document: skeleton blocks matching the 4-block layout, paper background.
- **Empty** map: "Your teacher is still preparing the course."
- **Login error**: top banner "Invalid credentials" — generic, no detail.
- **Too many attempts**: "Try again in 15 minutes."
- **Consent missing**: "Your family hasn't registered consent yet."

---

## State / data model (minimal)

Per the source spec, the production app needs at least:

- **User profile**: learning preferences (radar values across 5 axes), tone, length, font/theme/contrast accessibility settings, bilingual flag + native language, consent flags (a–e).
- **Knowledge graph**: nodes (id, name, level, prerequisites), per-student state (one of `not_introduced / introduced / lacuna / in_recupero / da_consolidare / consolidato`) + transition history.
- **Missions**: per (student, node), ordered list of steps, completion state, attempt #.
- **Quizzes**: per node, set of questions + per-attempt answers, score, resulting transition.
- **Documents**: per (student, node), 4-block content + analogy seed + status (active/archived).
- **Audit log**: every transition (auto or teacher override), timestamp, author, evidence.

---

## Assets

- **Fonts**: Google Fonts — `Instrument Serif`, `Geist`, `JetBrains Mono`. License: Open Font License. The handoff codebase should self-host these in production.
- **Icons**: all icons are inline SVG, drawn by stroke (1.8–2.2 px) or filled. No external icon library is used. The codebase may swap them for its standard library (Phosphor, Lucide, SF Symbols, Material Symbols, etc.) — keep the visual weight comparable (line ~1.8 px, rounded joins).
- **Imagery**: none. All illustration is type + colour + SVG node graphs.

---

## Files in this bundle

```
design_handoff_maestro_student/
├── README.md                       ← this file
├── Maestro Student App.html        ← canvas host: lays all 12 screens out side-by-side
├── maestro-tokens.css              ← design tokens (CSS custom properties) + utility classes
├── screens-1.jsx                   ← Login + Onboarding (welcome / quiz / result)
├── screens-2.jsx                   ← Home + Map + Node detail + Mission
├── screens-3.jsx                   ← Quiz question + Quiz result + Document + Profile + Why-this
├── screens-tablet.jsx              ← Tablet-breakpoint layouts of the same 12 screens
├── screens-desktop.jsx             ← Desktop-breakpoint layouts of the same 12 screens
├── ios-frame.jsx                   ← iOS device chrome used only for preview framing — NOT to be reproduced in the app
└── design-canvas.jsx               ← pan/zoom presentation canvas — NOT to be reproduced in the app
```

To preview the designs locally, open `Maestro Student App.html` in a modern browser. The canvas is pan/zoom (drag, scroll wheel, pinch) and any artboard can be opened fullscreen by clicking its label.

`ios-frame.jsx` and `design-canvas.jsx` are **scaffolding only** — they exist to display the screens; they are not part of the app to be built.

---

## Accessibility (F9) — must-haves

- Font choice: provide `Geist` (default), `OpenDyslexic`, `Atkinson Hyperlegible` in the profile.
- Text size: user adjustable from 12 pt to 24 pt.
- Themes: light / dark / sepia.
- High-contrast mode toggle.
- All state colours **paired with icon + text label**.
- Full keyboard navigation (Tab, Enter, arrows for grids/maps).
- ARIA labels on every interactive element; `aria-live="polite"` for dynamic state changes (quiz result, map updates).
- Audio assets need text transcripts.

---

## Open items for the dev team

1. **Gamification (V1)** — XP, streak, badges are visible on Home but the rules engine isn't designed yet. Gate behind the user's `gamification` toggle.
2. **Bilingual rendering** — when consent (b) is granted, documents render in a two-column layout (official language | native language). Not yet drawn — adapt SCR-ST-08.
3. **Podcast player (SCR-ST-11)** and **Quests (SCR-ST-12)** — V1 priority, not in this handoff.
4. **First-activation flow** — terms acceptance + consent recap card (post-login) is described in the source spec but not yet drawn.
5. **Notifications panel** — the bell icon on Home shows an unread dot; the panel itself isn't drawn.
