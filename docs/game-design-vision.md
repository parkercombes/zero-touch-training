# Game Design Vision — Zero-Touch Training UI Trainer

This document captures the game mechanics framework, real-world benchmark examples, and planned enhancements for the UI trainer component of Zero-Touch Training.

---

## The Problem: Completion, Not Just Accuracy

Traditional ERP training has two problems. The first — accuracy and freshness — is solved by the Zero-Touch generation pipeline. The second — **completion** — is not. Most ERP training is completed out of compliance obligation, skimmed, and forgotten within days.

The question is: what makes someone actually want to finish a training module, and come back for the next one?

The answer is the same mechanics that make mobile games work. Not games for their own sake — game mechanics applied surgically to the moments where ERP training loses people: the first confusing screen, the long middle section with no feedback, the moment a wrong step happens with no explanation of why it mattered.

---

## The Four-Level Framework

The UI trainer is structured as four progressive levels for each process. A learner advances through levels on the same task — Goods Receipt, for example — getting less scaffolding and more pressure as they improve.

### Level 0 — UI Orientation
"Learn the controls."

The learner explores the SAP Fiori interface with no task pressure. Tooltips explain every field. The goal is just familiarity: where is the transaction code bar, what does a dropdown look like, what does "Post" do. No failure state.

### Level 1 — Guided Execution
"Follow the steps."

A specific task is presented. Each step is highlighted and prompted. Clicking the wrong field shows a gentle redirect. The learner succeeds as long as they follow. The emphasis is on building correct muscle memory — not testing it.

This is where most existing SAP training products stop.

### Level 2 — Semi-Guided
"You know this. Try it."

The same task, but prompts are removed. If the learner gets stuck, they can request a hint — but hints are delayed by 10 seconds and cost XP. The learner must think, not just follow. Errors trigger an explanation of the downstream consequence, not just a "wrong" indicator.

### Level 3 — Challenge Mode (Boss Fight)
"Real conditions, timer on."

A complete goods receipt scenario with a narrative premise: "The truck has been at the dock for 45 minutes. Dock fees start in 15 minutes. You need to post this receipt and flag the temperature discrepancy before your lead notices." No hints. Timer visible. Score recorded to the leaderboard.

The scenario rotates. One week it's a clean receipt. Next week there's a quantity discrepancy to catch. The week after that, the movement type is wrong in the pre-filled form.

---

## Key Mechanics

### XP and Achievement Badges
- XP is awarded for completing each level, with bonuses for speed and first-attempt success
- Achievement badges: "First Post," "Discrepancy Catcher," "Cold Chain Guardian," "Speed Receiver" (sub-3-minute goods receipt)
- Badges are visible on the team leaderboard

### Timer
- Only active in Level 3
- Visible countdown creates urgency without real-world consequences
- Score formula: `base_points × (time_bonus) × accuracy_multiplier`

### Leaderboard
- Site-level by default (who on this receiving dock is fastest)
- Weekly reset with trophy for top performer
- Optional cross-site league for larger organizations

### Narrative Framing
Every Level 3 scenario opens with a brief premise: a sentence or two that gives the task real stakes. Examples:
- "Vendor just called — they need confirmation of receipt before 3pm or the invoice auto-cancels."
- "Your lead is out sick. You're handling batch tracking solo today. The auditor is on-site."
- "New hire next to you just posted a 501 instead of 101. You need to correct and explain why before the shift ends."

The framing makes the simulation feel real without making failure feel punishing. Stakes are operational, not disciplinary.

### Feedback on Errors (Not "Wrong")
When a learner makes a mistake, the feedback explains the downstream consequence:
- "Movement type 501 creates a free-goods receipt with no PO reference. Finance sees an unplanned goods receipt and flags it for audit. The vendor invoice won't auto-match."
- "Temperature zone Zone-A doesn't match this product's cold chain requirement. It will fail QI inspection and need to be returned to the dock, adding 4–6 hours to the receipt cycle."

This is Layer 5 (Process Rationale) delivered in the moment — the learner sees *why* the rule exists while they're breaking it, not in a separate course.

### Confetti and Celebration
Clean level completion triggers a brief visual celebration. This sounds trivial but it isn't — positive reinforcement at the moment of success is a measurable driver of task repetition. The UKG Pro example below is partly attributable to this.

---

## Real-World Benchmarks

### UKG Pro Training Game (Gold Standard)
UKG (formerly Kronos) rebuilt their HR software training as a game — story mode, named characters, missions, and challenge levels. Results: **67% higher completion rate** vs. their previous eLearning format. The key design choices were narrative framing (not just "complete module 4"), character continuity, and immediate in-game feedback rather than end-of-module assessment.

UKG Pro is the closest existing product to what Zero-Touch Training's UI trainer is building. The difference: UKG built it manually for one product. Zero-Touch generates it automatically for any ERP process, and updates it when the process changes.

### WalkMe and Whatfix (In-App Overlay Approach)
These tools provide real-time step-by-step guidance inside the live application. They're not games — they're training wheels that never come off. Effective for day-one onboarding, but they don't build durable competency. A WalkMe flow that disappears (because the UI changed or the license lapsed) leaves users with nothing.

Zero-Touch Training generates WalkMe drafts (Layer 4) but also builds the simulation-based UI trainer as a standalone competency development tool. The goal is users who can work without the overlay, not users who are dependent on it.

### SAP Enable Now (Official SAP Training Tool)
SAP's own tool for generating documentation and guided tours from recorded UI sessions. Accurate, well-integrated, and completely dry. No game mechanics. No narrative. No leaderboard. Completion rates reflect this. It's the standard and it sets a low bar.

### Observation: The Gap
No vendor currently offers AI-generated, game-based SAP training at an accessible price point. The enterprise tools (SAP Enable Now, Cornerstone) are expensive and manual. The game-based tools (UKG-style) exist for individual SaaS products but nobody has applied the approach to SAP/ERP simulation at scale. This is the market gap.

---

## Planned UI Trainer Enhancements

These are the four highest-impact additions, ordered by implementation priority:

**1. Challenge Mode with Timer (Level 3)**
Add a visible countdown timer to existing Level 3 scenarios. Score based on time and accuracy. This is mechanical — no new content required, just a timer component and score formula.

**2. Achievement Badges**
Define 8–10 badges with clear unlock conditions. Store in JSON alongside the learner session. Display on the HUD. Zero new scenario content required.

**3. Confetti Animation on Successful Post**
CSS animation triggered on the "Goods Receipt Posted" screen. Two-second visual celebration. One-day implementation.

**4. Narrative Premise Cards**
Prepend a 2–3 sentence scenario card before each Level 3 challenge. Rotates weekly. Written once per scenario, stored in the scenario pack config. No code changes to the engine required — just data.

**5. Error Consequence Explanations (Deeper Layer 5 Integration)**
Expand the error feedback in the UI trainer to include the downstream consequence, not just "incorrect." Each wrong step in each scenario needs a one-paragraph consequence explanation. This is the most content-intensive enhancement but also the highest educational value.

**6. Leaderboard (Site-Level)**
Requires a minimal backend — a JSON file or lightweight API that stores scores per user per scenario. Can be file-based for the PoC. Weekly reset. Display on the HUD.

---

## Anniston Army Depot — Target Use Case

Anniston Army Depot (Anniston, AL) operates a major maintenance and supply operation under Army Materiel Command. Supply clerks manage all nine Army Classes of Supply using SAP-based systems (GCSS-Army or equivalent).

The Classes of Supply map directly to the five handling profiles already built:

| Army Class of Supply | Handling Profile | Example Items |
|---|---|---|
| Class I (Subsistence) | perishable | Rations, food service supplies |
| Class II/III/IV (General supplies) | standard_dry | Clothing, tools, construction material |
| Class VI (Personal demand items) | serialized | Controlled items requiring accountability |
| Class VIII (Medical material) | regulated_pharma | Pharmaceuticals, medical devices, GxP |
| Class III/IX (POL, repair parts w/ hazmat) | hazmat | Fuels, solvents, hazardous repair parts |

Why Anniston is an ideal early adopter:

- High clerk turnover, consistent training need
- Regulatory pressure (Army audit standards, OSHA, DOT) makes accurate training not optional
- Existing SAP infrastructure — no integration work required
- Government procurement vehicles exist that can fund training tools without a traditional sales cycle
- The game mechanics angle resonates with the demographic: Army clerks are typically 18–25, mobile-first, and are not well served by the CBT-style courses DoD typically provides

The training content Zero-Touch generates — accurate, process-specific, with narrative stakes that mirror real dock and supply room conditions — is a much better fit for this audience than anything currently available in the government training market.
