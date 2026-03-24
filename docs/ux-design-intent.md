# UX Design Intent — ERP Trainer Learner Experience

## Who We Are Designing For

The primary learner is someone on their first week in a warehouse — a new receiving clerk, a seasonal hire, or a transfer from another department. They may have never opened SAP before. They do not know what "MIGO" means, they do not know what "Goods Receipt" means as a transaction type, and they are not sitting at a desk in a classroom. They are on a warehouse floor, probably on a shared terminal or tablet, under time pressure, with a supervisor nearby who needs them to be productive.

This is the design target: not the trainer who built the course, not the IT team who deployed SAP, and not the experienced clerk who already knows the process. The system must serve someone who is encountering it for the first time, possibly mid-shift, possibly stressed.

---

## Five Core UX Design Principles

### 1. Task-First Language Throughout

The current ERP scenario names are organized by system name and transaction type — the vocabulary of the people who built the system, not the people who use it. A new clerk receiving their first hazmat shipment does not think "I need to do a Goods Receipt for Hazmat Materials in SAP MIGO." They think "a truck just showed up with drums marked with orange placards and I don't know what to do."

**All scenario labels visible to the learner must use plain task language:**

| Technical name (internal) | Learner-facing label |
|---|---|
| Goods Receipt — Standard Dry Goods | Receiving a Regular Shipment |
| Goods Receipt — Hazmat Materials | Receiving Hazmat / Dangerous Goods |
| Goods Receipt — Pharma / Cold Chain | Receiving Refrigerated or Cold Chain Items |
| Goods Receipt — Serialized Items | Receiving High-Value or Serialized Items |
| Goods Receipt — SEDC | Receiving Same-Day Distribution Items |

The SAP/MIGO technical label may appear as a subtitle for supervisors and trainers who need it, but it must never be the primary label the learner sees.

### 2. Two Clear Entry Modes

The current landing page offers only one path: the full four-level training experience. But a new worker in front of an unfamiliar screen during a live shift does not need a training game — they need a quick reference. These are two fundamentally different use cases and they should be separated at the top level.

**Mode A — "I need help right now"**
Gets the learner directly to the relevant scenario with a step-list view only — the sequence of actions required to complete the task, with no game mechanics, no scoring, and no level selection. This is the on-the-job reference mode. Speed and clarity are the only goals.

**Mode B — "I want to learn / practice"**
Leads to the full trainer experience with all four levels. This is the pre-shift, off-floor, or new-hire onboarding mode.

The entry-mode choice should be the first decision on the landing page, before scenario selection.

### 3. Situation-Based Navigation ("What Do You Have in Front of You?")

Scenario selection should not require the learner to recognize a category label — it should guide them through the situation they are actually in. A two-question flow covers the full scenario set:

**Step 1 — What arrived?**
- Regular boxes / pallets (→ Standard Dry)
- Drums or packages with hazard placards (→ Hazmat)
- Refrigerated / temperature-controlled items (→ Pharma / Cold Chain)
- Electronics or high-value serialized items (→ Serialized)
- Same-day distribution or local-source items (→ SEDC)

**Step 2 — Do you need help right now, or do you want to practice?**
(Routes to Mode A or Mode B from Principle 2.)

This replaces the current card-grid selection for new users. Experienced users who already know what scenario they want can still go directly to the card grid — the decision tree is an on-ramp, not a replacement.

### 4. Progress-Aware Level Selection

The four levels currently appear as equal options every time the learner lands on a scenario. This ignores where the learner is in their development and misses an opportunity to guide them forward naturally.

**Intended behavior:**
- A learner visiting a scenario for the first time lands on EXPLORE (Level 0) automatically, with a brief explanation of what that level is and what comes next.
- After completing EXPLORE, the system prompts them toward GUIDED rather than putting the full level menu back in front of them.
- Completed levels show a checkmark or similar indicator so the learner can see their own progress at a glance.
- Levels 2 and 3 are visually accessible but framed as "ready for more?" rather than presented as equal starting points.

The goal is a natural progression path — not a locked gating system — but with enough guidance that a new learner is never staring at four options with no idea which to pick.

### 5. Floor-Friendly Affordances

Warehouse conditions are different from office conditions. The UI must account for this:

- **Large tap targets** — minimum 48px hit areas. A learner using a touchscreen with gloves has less precision than a mouse user.
- **High contrast** — warehouse ambient lighting (fluorescent, mixed with dock daylight) reduces apparent contrast. Text and interactive elements must meet WCAG AA minimum contrast ratios, with preference for exceeding them.
- **Minimal scrolling to reach primary action** — the most important button on any screen (the next step, the scenario entry point) should be visible without scrolling on a standard tablet viewport.
- **Large, readable step text** — scenario steps should be readable at arm's length from a mounted tablet. Minimum 16px body text, step numbers and labels larger.
- **No hover-dependent interactions** — touchscreens have no hover state. Any information or action that depends on hover must have a tap-accessible equivalent.

---

## Navigation Structure (Intended)

```
Landing page
├── [I need help RIGHT NOW] ──────────────────────────────────────────┐
│   └── What do you have in front of you? (5 situation cards)         │
│       └── Step-list view (no game, no levels, just the steps)       │
│                                                                      │
└── [I want to LEARN / PRACTICE] ─────────────────────────────────────┘
    └── What do you have in front of you? (5 situation cards)
        └── Scenario landing (level selector, progress-aware)
            ├── EXPLORE (Level 0) — Start here
            ├── GUIDED (Level 1) — After EXPLORE
            ├── ON YOUR OWN (Level 2) — After GUIDED
            └── CHALLENGE (Level 3) — After ON YOUR OWN
```

---

## What This Is Not

This document describes the learner-facing UX intent for the ERP trainer. It does not cover:

- The generation pipeline (how scenarios are authored and built)
- The game mechanics within a scenario (four levels, XP, consequences, timer, confetti) — those are documented in `game-design-vision.md`
- The hardware training domain — that domain will have its own UX design document as it matures
- Leaderboard, badges, or XP persistence — those are engagement features documented separately

---

## Implementation Status

| Principle | Status |
|---|---|
| Task-first language on selector | Planned — landing page redesign |
| Two entry modes (help now / practice) | Planned — landing page redesign |
| Situation-based navigation decision tree | Planned — landing page redesign |
| Progress-aware level selection | Planned — scenario index.html updates |
| Floor-friendly affordances | Partially addressed (hotspot sizing, Explore panel) — full pass planned |
