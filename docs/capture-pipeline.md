# Capture Pipeline — System-Agnostic Screen Generation

This document describes the architecture for generating training content from real systems,
replacing the fabricated Pillow-drawn screens used in the initial PoC.

---

## The Problem with Drawn Screens

The PoC generates training screenshots using a Python/Pillow script that draws
SAP-like fields, tables, and buttons programmatically. This approach proved the
game engine concept but has two significant limitations:

1. **Fidelity gap** — Drawn screens look like approximations. Real system fidelity
   builds learner confidence and transfers directly to on-the-job performance.
2. **Single-system lock-in** — The drawing code is SAP-specific. Every new system
   (Appian, ServiceNow, a custom portal) requires a new drawing library.

Both problems are solved by replacing the drawing pipeline with a capture pipeline.

---

## The Core Insight: The Trainer Is Already System-Agnostic

The game engine (`trainer_app.jsx`) does not know what system it is simulating.
It only needs three inputs:

1. A folder of screenshots showing the workflow at each step (highlighted and neutral)
2. A scenario definition file (steps, hotspot coordinates, consequence text, branding)
3. A branding configuration object (colors, level names, shell title)

In the PoC, a Python script generates those screenshots by drawing. In production,
a Playwright script generates those screenshots by capturing. The game engine is
unchanged either way.

---

## The Capture Pipeline

```
Real System (any web-based UI)
       ↓
Playwright Scenario Recorder
  — developer walks through the workflow once in record mode
  — script captures a screenshot at each significant step
  — inspects DOM to find the target element for each step
  — records element bounding box → hotspot x, y, width, height
  — captures both "before click" (neutral) and "after highlight" states
       ↓
Auto-generated scenario pack
  ├── screens_highlighted/   (with visual cues baked in)
  ├── screens_neutral/       (for Levels 2-3 with decoy overlays)
  └── scenario_data.json     (steps, hotspots, branding, consequences)
       ↓
Existing trainer_app.jsx game engine (no changes required)
       ↓
Fully interactive trainer for that system
```

### What the Recorder Does

The Playwright recorder is a developer-facing tool, not a learner-facing one.
A developer (or a process SME working with a developer) runs through the workflow
once in a real or sandbox environment:

1. Launches the recorder script targeting the system URL
2. Navigates the workflow as normal
3. At each step, marks the target action (field click, button press, dropdown select)
4. The recorder captures the screen, records the element position, logs the step

Output: a complete scenario pack ready for the trainer, generated in a single session.

### Highlighted vs. Neutral Screens

The current Pillow approach bakes visual highlights (blue borders, spotlight overlays)
directly into the screenshot pixels. The capture pipeline produces this in two ways:

- **Highlight overlay**: Playwright injects a temporary CSS class on the target element
  before capturing, then removes it. The screenshot shows the real UI with a visual cue.
- **Neutral screen**: Captured with no overlay — the real UI as the learner would see it
  on the floor.

This produces the same two-image-per-step structure the trainer already expects.

---

## System Compatibility

The capture pipeline works with any system that renders in a web browser.
The trainer does not require modification between systems — only the scenario pack changes.

| System | Notes |
|---|---|
| **SAP Fiori** | Capture from SAP training client or IDES system |
| **Appian** | Capture from Appian dev or staging environment |
| **ServiceNow** | Capture from ServiceNow developer instance (free) |
| **OutSystems / Mendix** | Capture from any deployed environment |
| **ERPNext** | Capture from self-hosted Docker instance — zero license cost |
| **Salesforce** | Capture from Salesforce sandbox |
| **Custom web portals** | Capture from any authenticated URL |

### Low-Code Front-Ends for ERP

Many SAP deployments do not expose SAP Fiori directly to warehouse clerks.
A Low Code platform (Appian, ServiceNow, OutSystems) sits in front of the SAP
transaction, presenting a simplified form that submits via API to the underlying ERP.

The learner never sees SAP — they see the Low Code screen.

With the capture pipeline:
- Point the recorder at the Appian form (not the SAP screen behind it)
- Capture the actual interface the learner uses on the floor
- The trainer presents exactly what the learner will encounter in production

This is the only training approach that naturally handles the Low Code layer
without additional authoring effort.

---

## ERPNext as a Zero-Cost Capture Target

For PoC extension and demonstration purposes without access to a SAP training client
or Appian environment, ERPNext provides a functionally equivalent substitute:

- **Purchase Receipt** in ERPNext maps directly to SAP MIGO Goods Receipt
- Same field types: vendor, PO reference, material, quantity, batch, serial, storage location
- Same logic: batch tracking, serial number capture, quality inspection flag, temperature zone
- Deployable in Docker in under 5 minutes
- Community edition: completely free, no license

Screenshots captured from a live ERPNext Purchase Receipt are indistinguishable in
training fidelity from SAP Fiori screenshots. The workflow logic is identical.
The UI is a real web application, not a drawing.

### Docker Sandbox Approach

For a multi-user training environment:

```
Training server (single modest VM, ~$40-80/mo)
    ↓
Docker containers — one per active session
    ├── ERPNext instance with pre-seeded scenario data
    ├── Spun up on demand (~30 seconds)
    ├── User interacts with real running system
    └── Destroyed and reset after session ends
```

Each user gets a fully isolated environment. No shared state, no data bleeding,
no interference between concurrent users. The "safe sandbox" problem is solved
at the infrastructure level — not by simulating safety, but by making each
session a fresh, disposable system.

---

## Comparison: Drawn vs. Captured

| Dimension | PoC (Pillow/Drawn) | Production (Playwright/Captured) |
|---|---|---|
| Fidelity | Approximate — drawn approximation | Exact — real system screenshots |
| Build time per scenario | 2-4 hours coding | 1-2 hours capture session |
| New system support | Requires new drawing code | No code change — just point at new URL |
| Low Code front-end support | Not supported | Natively supported |
| Auto-update when UI changes | Manual redraw | Re-run capture session |
| Cost | Free (Pillow is open source) | Free (Playwright is open source) |
| Infrastructure required | None | Access to system sandbox or ERPNext |

---

## Development Roadmap

### Phase 1 (Current PoC)
Pillow-drawn SAP approximations. Proves game engine, pedagogical mechanics,
and scenario structure. Five SAP MIGO scenarios + one hardware scenario.

### Phase 2 (Next)
Playwright capture script targeting ERPNext. Replaces drawn screens with real
system screenshots. Proves the capture pipeline with a free, accessible system.
Game engine unchanged. Scenario count unchanged.

### Phase 3
Capture script extended to support SAP Fiori, Appian, and one Low Code front-end.
Multi-system scenario packs demonstrated side by side.

### Phase 4
Containerized Docker sandbox for multi-user live training.
Progress tracking backend (lightweight API + database).
SCORM wrapper for LMS deployment.

---

## Relationship to Other Documents

- `concept.md` — Overall system architecture and layered training model
- `ux-design-intent.md` — Learner-facing UX principles including system-agnostic design
- `game-design-vision.md` — Game mechanics, levels, engagement model
- `docs/layers/` — Individual layer design specs
