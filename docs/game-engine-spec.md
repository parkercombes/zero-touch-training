# Zero-Touch Training — Game Engine Specification

Technical and pedagogical reference for the domain-agnostic React SPA game engine.
This document contains detail that is intentionally summarised in the Executive Summary.

---

## Four-Level Progression

Every scenario runs through four levels regardless of domain. The scaffolding
decreases and the pressure increases at each level.

| Level | ERP Name        | Hardware Name    | What Changes                                                                 | Failure State                                      |
|-------|-----------------|------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| 0     | EXPLORE         | OBSERVE          | Full descriptions on every element. No task assigned. No failure.            | None — exploration only                            |
| 1     | GUIDED          | FOLLOW ALONG     | Target field highlighted. Wrong clicks redirected with gentle explanation.   | Soft correction, no score impact                   |
| 2     | ON YOUR OWN     | DO IT            | No highlights. Decoy fields active. Hints cost XP. Errors show consequence. | Consequence panel fires; XP deducted per hint used |
| 3     | CHALLENGE       | SPEED RUN        | Timer running. No hints. Rotating narrative premise card. Score recorded.    | Time-boxed; score saved to leaderboard             |

The level naming is controlled by a domain configuration object loaded at runtime.
ERP scenarios and hardware scenarios share identical engine code — only the config differs.

---

## Engagement Mechanics — Full Detail

### 1. Consequence-Based Error Feedback

**What it does:** When a learner clicks a wrong element in Level 2 or 3, a structured
panel appears instead of a generic "wrong" message. The panel names the exact downstream
consequence of that specific error in operational terms.

**Examples:**
- Posting the wrong quantity on a standard GR → "This creates a quantity discrepancy on
  the PO. The purchasing agent will see an under-delivery. The remaining quantity stays
  open, Accounts Payable cannot fully close the invoice, and the vendor may receive a
  short payment."
- Skipping the storage location on a hazmat receipt → "Without a storage location, SAP
  cannot generate the required hazardous material document. This GR will not post. The
  receiving dock lead will need to manually resolve the block with the compliance team."

**Rationale:** Research on error feedback in training consistently shows that learners
who understand the *why* of a mistake retain the correct behavior better than those
who simply receive a pass/fail signal. The consequence panel also models the systems
thinking a trained employee is expected to demonstrate.

**Implementation:** Each scenario definition file contains a `consequences` map:
`{ "wrongField": "consequence text", ... }`. The engine looks up the clicked element's
ID at the time of the wrong click and renders the matching consequence text.

---

### 2. Post-Level Debrief

**What it does:** After the learner completes any level (pass or fail), an expandable
debrief section appears before the next-level prompt. It contains 2–4 "why this step
matters" cards explaining the process rationale behind the steps just performed.

**Rationale:** Spaced explanation — rationale delivered after practice rather than
before — is more effective than pre-reading for procedural tasks. The debrief creates
a natural pause that separates the performance feedback from the next challenge.

**Implementation:** Debrief cards are defined in the scenario JSON under `debrief`.
Each card has a `title`, `body`, and optional `icon`. Cards are collapsed by default;
the learner expands them. The engine tracks whether debrief cards were opened (for
analytics) but does not gate progression on opening them.

---

### 3. Timer and Audio Cues

**What it does:** Level 3 activates a visible countdown timer. At T-10 seconds,
a tick sound begins at 1-second intervals. On success, a win fanfare plays. On
timeout, a distinct failure sound plays. Levels 0–2 are silent except for click
confirmation sounds.

**Rationale:** Audio urgency cues in Level 3 simulate the time pressure of the
real working environment (a receiving dock, a maintenance bay) without real-world
consequences. The contrast with the silent lower levels makes the Level 3 pressure
feel earned rather than arbitrary.

**Timer defaults:** 90 seconds (configurable per scenario in the definition file).
Challenge scenarios with fewer steps can be tuned lower; complex scenarios with
many required fields should stay at 90–120 seconds.

---

### 4. Confetti and Win Celebration

**What it does:** A full-screen confetti animation fires at the exact frame the
learner successfully completes a level. A win sound plays simultaneously. The
debrief and next-level prompt appear after the confetti settles (~1.5 seconds).

**Rationale:** Point-in-time positive reinforcement — reward delivered at the
moment of success rather than after a delay — is a well-documented driver of
behavior repetition. The confetti is not present in Level 0 (exploration should
feel low-stakes) but fires in Levels 1–3.

---

### 5. Rotating Narrative Premise Cards

**What it does:** Before Level 3 begins, a full-screen "situation card" sets an
operational scenario that the learner is about to perform within. The card rotates
through four options on repeat runs.

**Four ERP (Goods Receipt) premises:**
1. "The dock lead is out sick. You're covering solo today."
2. "This vendor has had two short-ship complaints this month. The purchasing team is watching."
3. "It's the last receiving window before the plant shuts down for the holiday. This shipment
   has to post today."
4. "Auditors are on-site this week. Every document must be traceable."

**Rationale:** Narrative context activates the learner's operational identity — "this
is something that could happen to me" — rather than the student identity of a training
module. It also prevents memorization gaming: a learner who has passed the scenario
once encounters a different framing on the second attempt.

---

### 6. Decoy Fields

**What it does:** In Levels 2 and 3, two to three non-target form fields are rendered
with subtle visual styling that makes them look like plausible click targets. They are
not highlighted (the target is not either), but they are present and clickable.

**Rationale:** The real SAP MIGO screen has many fields, most of which are not relevant
to any given step. A training screen with only one visible interactive element does not
simulate the actual cognitive load the learner will face on the job. Decoys restore that
load in a controlled way — the learner must discriminate, not just click the only thing.

**Implementation:** Decoy fields are declared in the scenario definition file under
`decoys` for each step. Each decoy has a `label`, `position`, and `wrongClickConsequence`.

---

### 7. Adaptive Hint System

**What it does:** In Level 2, hints are available at a cost (1 hint = N XP deducted).
After three consecutive wrong clicks on the same step, the next hint is provided free
of charge and the learner is not penalized for using it.

**Rationale:** The free-hint threshold prevents the learner from cycling endlessly
through wrong clicks in frustration. The cost mechanism before that threshold preserves
the "on your own" character of Level 2 — hints are available but have a consequence.

**Threshold:** 3 consecutive wrong clicks (configurable). Free hints do not compound:
if the learner gets a free hint and then clicks wrong again, the counter resets.

---

### 8. Review Mode

**What it does:** After completing any level, the win screen includes a "Review" button
that launches a separate quiz-like view. Five steps from the scenario are presented in
scrambled order. The learner must sequence them correctly. No score is recorded;
this is purely a spaced repetition tool.

**Rationale:** Spaced repetition is the most evidence-backed mechanism for moving
procedural knowledge from working memory into durable long-term retention. Review mode
makes it accessible in the same session immediately after the initial practice, or
later as a refresher.

---

## Scenario Definition File Format

Each scenario is defined in a JSON file that the engine loads at startup via
`window.__SCENARIO__`. The engine does not contain any scenario-specific logic.

```json
{
  "id": "goods-receipt-standard",
  "title": "Receiving a Regular Shipment",
  "subtitle": "MIGO Goods Receipt — Standard Dry Goods",
  "domain": "erp",
  "difficulty": "day1",
  "estimatedMinutes": 12,
  "clickPar": 5,

  "levels": [0, 1, 2, 3],
  "timerSeconds": 90,

  "steps": [
    {
      "id": "step-movement-type",
      "instruction": "Set Movement Type to 101",
      "targetElement": "movement-type-dropdown",
      "decoys": ["vendor-field", "reference-field"],
      "consequence": "Without movement type 101, SAP cannot identify this as a GR against a PO...",
      "hint": "Look for the Movement Type dropdown in the top-left of the header section."
    }
  ],

  "debrief": [
    {
      "title": "Why movement type matters",
      "body": "Movement type is the key that tells SAP what kind of goods movement this is..."
    }
  ],

  "premises": [
    "The dock lead is out sick. You're covering solo today.",
    "This vendor has had two short-ship complaints this month.",
    "Last receiving window before the holiday shutdown.",
    "Auditors on-site this week. Every document must be traceable."
  ]
}
```

---

## Domain Branding Configuration

The engine reads `window.__DOMAIN_CONFIG__` to apply domain-specific branding without
any code changes.

```json
{
  "domain": "erp",
  "levelNames": ["EXPLORE", "GUIDED", "ON YOUR OWN", "CHALLENGE"],
  "accentColor": "#0070f2",
  "shellColor": "#1d2d3e",
  "iconStyle": "corporate"
}
```

```json
{
  "domain": "hardware",
  "levelNames": ["OBSERVE", "FOLLOW ALONG", "DO IT", "SPEED RUN"],
  "accentColor": "#e87600",
  "shellColor": "#2d2d2d",
  "iconStyle": "industrial"
}
```

---

## Screen Assets

### Phase 1 (Current): Pillow-Drawn Screens

Screens are generated by `poc/generate_screens.py` using Python/Pillow. Fields,
labels, and interactive elements are drawn programmatically as SAP-approximate
representations. Fidelity is approximate but sufficient to prove the game engine,
pedagogy, and scenario structure.

### Phase 2 (Planned): Playwright-Captured Screens

A Playwright script replaces the drawing pipeline. The engine is completely
unchanged — it only needs the PNG screenshots and the hotspot coordinates.
Full capture pipeline architecture is in `docs/capture-pipeline.md`.

---

## Progress and State

The engine tracks the following state in `localStorage` (Level 1 deployment) or
via the progress API (Level 2+):

| Key                        | Type      | Description                                    |
|----------------------------|-----------|------------------------------------------------|
| `zt_progress`              | object    | `{ scenarioId: { levelReached, bestScore } }`  |
| `zt_persona`               | string    | Persona selected in Overview Video flow         |
| `zt_hints_used`            | object    | `{ scenarioId: { level: hintCount } }`          |
| `zt_review_completed`      | object    | `{ scenarioId: boolean }`                       |
| `zt_last_scenario`         | string    | Last scenario ID accessed (for resume)          |

---

## Related Documents

| Document                          | What it covers                                      |
|-----------------------------------|-----------------------------------------------------|
| `docs/capture-pipeline.md`        | Playwright capture architecture, Phase 1 vs Phase 2 |
| `docs/ux-design-intent.md`        | Five UX principles, Low Code surface considerations |
| `docs/design-decisions.md`        | Open design decisions: badge style, panel layout    |
| `docs/Zero-Touch-Training-Executive-Summary.docx` | Executive summary (condensed)      |
