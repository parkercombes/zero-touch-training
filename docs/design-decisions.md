# Zero-Touch Training — Open Design Decisions

Running log of decisions that need a call before finalizing mocks or building
production UI. Add a decision with `## DDR-NNN` and mark it `RESOLVED` once called.

---

## DDR-001 — Badge style: solid number vs. progress ring

**Status:** OPEN
**Surface:** Fiori launchpad tile badge (top-right corner of each tile)
**Reference:** `fiori-launchpad-mock.html`

### Options

| Style | Description | Pro | Con |
|---|---|---|---|
| **A — Solid fill + level number** | Amber circle, white number (0–3) showing current level | Tells the user *which level* they're on; familiar notification dot pattern | Doesn't show % completion across all 4 levels at a glance |
| **B — SVG arc ring** | Amber arc segments on a light ring showing how many of 4 levels are done | Percentage progress immediately visible; no number to decode | Can't tell *which* level without opening popover; more complex to render |

### Decision needed
Pick one style to standardize across all badge states and surfaces (launchpad tile
+ in-app floating button + manager dashboard). The arc ring only works at ≥24px;
below that the number is safer.

**Recommendation:** Style A (solid + number) for V1. It's smaller, works at all
sizes, and the level number maps directly to the 4-level language already used in
scenario cards. Revisit to ring style if user testing shows confusion about progress.

---

## DDR-002 — Badge tap target size for gloved/warehouse use

**Status:** OPEN
**Surface:** Fiori launchpad tile badge, in-app floating button
**Reference:** `fiori-launchpad-mock.html` design notes

### Context
Current badge visual is 26 px. Effective tap area with negative margin ≈ 46 px.
SAP Fiori accessibility guideline and our own floor-friendly target is 52 px minimum.

### Options

| Option | Visual badge | Effective tap area | Notes |
|---|---|---|---|
| **A — Enlarge badge to 32 px** | Badge visually larger, more prominent on tile | ~52 px with margin | Simple; badge starts to dominate tile corner |
| **B — Invisible ::after hit area** | Badge stays 26 px visually | 52 px via CSS pseudo-element | Clean visual, no layout impact, standard mobile pattern |
| **C — Tap entire tile for popover, swipe/hold for badge** | No change | Full tile area | Conflicts with normal tile tap-to-open behavior |

**Recommendation:** Option B — invisible enlarged hit area on the badge. No visual
change, full accessibility compliance. Implement with `padding` or `::after`.

---

## DDR-003 — Panel entry point: floating button vs. in-app header icon

**Status:** OPEN
**Surface:** Fiori app shell (inside a transaction like MIGO, ME21N)
**Reference:** `fiori-in-app-panel-mock.html` (in development)

### Context
Once a user has clicked a launchpad tile and is inside the Fiori app, they need a
way to open the training panel without leaving the transaction.

### Options

| Option | Placement | Behavior | Risk |
|---|---|---|---|
| **A — Floating action button (FAB)** | Fixed bottom-right, always visible | Tapping opens slide-in panel | Overlaps page content; SAP Fiori doesn't natively use FABs |
| **B — App header icon** | Right side of the Fiori app sub-header bar | Tapping opens slide-in panel | Requires SAP UI5 extension/injection; harder to deploy without system access |
| **C — Persistent bottom bar (mobile)** | Docked below page content, above OS navigation | Tap "Training" tab to open panel drawer from bottom | Changes app chrome; needs shell customization |
| **D — Browser extension / overlay** | Injected by a Chrome/Edge extension | Works with any app, no SAP customization needed | Requires IT deployment of extension; not viable for all environments |

**Recommendation:** Option A (FAB) for the initial PoC and HTML mock — easiest to
prototype and visually unambiguous. Revisit Option B for production if SAP UI5
extensibility is available (BTP side panel API exists for Fiori Elements apps).

---

## DDR-004 — Panel layout: side panel vs. bottom drawer

**Status:** OPEN
**Surface:** Training panel opened from inside a Fiori transaction
**Reference:** `fiori-in-app-panel-mock.html` (in development)

### Context
The panel needs to show training content alongside the live SAP form. Two primary
layout patterns on different device types.

### Options

| Layout | Best for | App content behavior | Notes |
|---|---|---|---|
| **A — Right slide-in panel (~360 px)** | Desktop / large tablet (landscape) | App content compresses or overlaps | Standard for most enterprise help panels (e.g., SAP CoPilot) |
| **B — Bottom drawer (40–60% of screen height)** | Tablet portrait / warehouse terminal | App content remains visible above drawer | Better on smaller screens; harder to show step-by-step content |
| **C — Full-screen overlay with back button** | Mobile / phone | App hidden while training | Breaks the "train alongside the real thing" experience |
| **D — Responsive: side panel on wide, drawer on narrow** | All | Adapts to viewport | Best UX; more implementation complexity |

**Recommendation:** Option A for V1 mock (desktop focus). Flag Option D as the
target for production — the breakpoint is ≈ 768 px viewport width.

---

## DDR-005 — Training content in panel: iframe vs. embedded component

**Status:** OPEN
**Surface:** Training panel content area
**Reference:** Architecture decision; no mock yet

### Context
The training scenario (the React SPA game engine) currently runs as a full-page
HTML file. In the in-app panel it needs to run in a constrained ≈360×(full height)
column.

### Options

| Option | Implementation | Isolation | Notes |
|---|---|---|---|
| **A — Sandboxed `<iframe>`** | Point iframe src at existing trainer URL | Full CSS/JS isolation | Simplest; trainer needs responsive layout at 360 px wide |
| **B — Embedded React component (same page)** | Import trainer as a component into the panel shell | Shared context; can share user state | Requires trainer to be refactored as a component, not a standalone page |
| **C — Separate browser tab / window** | Open trainer in new tab from panel button | No overlap concerns | Breaks "train alongside" workflow; acceptable fallback |

**Recommendation:** Option A (iframe) for PoC. The trainer SPA already runs
standalone. The panel just needs `width: 360px; height: 100%` and `overflow: auto`
in the iframe. Production can revisit Option B for deeper state sharing.

---

## DDR-006 — "Help now" default vs. user-last-state default in panel

**Status:** OPEN
**Surface:** Panel mode on open (Help Now vs. Practice toggle)
**Reference:** `index.html` two-mode design; `fiori-in-app-panel-mock.html`

### Context
The training panel has two modes (per the landing page redesign):
- **Help Now** — reactive; shows current step in the scenario the user is on
- **Practice** — proactive; shows all levels and lets the user choose

When opened from inside a running SAP transaction, which mode should be default?

### Options

| Default | Rationale | Risk |
|---|---|---|
| **Help Now** | User is mid-task — they probably want immediate guidance | If they opened the panel to practice, extra tap to switch |
| **Practice** | Consistent with landing page default | Wrong for someone who is stuck and needs immediate help |
| **Last used mode** | Personalized; remembers per-user preference | Requires session/localStorage state |
| **Context-driven** | If opened from launchpad badge = Practice; if opened from in-app FAB = Help Now | Smart; maps to intent | More complex logic |

**Recommendation:** Context-driven (Option 4) — badge tap from launchpad defaults
to Practice; FAB tap from inside an app defaults to Help Now. Implement as a URL
param (`?mode=help` or `?mode=practice`) passed to the trainer iframe src.

---

## Resolved decisions

*(None yet — move entries here once a call is made)*
