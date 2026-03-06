# Game Design Vision — Zero-Touch Training UI Trainer

This document captures the game mechanics framework, real-world benchmark examples, and planned enhancements for the UI trainer component of Zero-Touch Training.

---

## The Problem: Completion, Not Just Accuracy

Traditional ERP training has two problems. The first — accuracy and freshness — is solved by the Zero-Touch generation pipeline. The second — **completion** — is not. Most ERP training is completed out of compliance obligation, skimmed, and forgotten within days.

The question is: what makes someone actually want to finish a training module, and come back for the next one?

The answer is the same mechanics that make mobile games work. Not games for their own sake — game mechanics applied surgically to the moments where ERP training loses people: the first confusing screen, the long middle section with no feedback, the moment a wrong step happens with no explanation of why it mattered.

---

## The Four-Level Framework (Fully Built)

The UI trainer is a React single-page application structured as four progressive levels for each process. A learner advances through levels on the same task — getting less scaffolding and more pressure as they improve.

The level names and descriptions are domain-specific, injected via the branding system:

| Level | Software (SAP) | Hardware |
|---|---|---|
| 0 | **EXPLORE** — "Learn the screen" | **OBSERVE** — "Study the equipment" |
| 1 | **GUIDED** — "Follow the prompts" | **FOLLOW ALONG** — "Follow the prompts" |
| 2 | **ON YOUR OWN** — "No highlights, hints cost XP" | **DO IT** — "No highlights, hints cost XP" |
| 3 | **CHALLENGE** — "Timer on, no help" | **SPEED RUN** — "Timer on, no help" |

### Level 0 — Explore / Observe
"Learn the controls."

The learner explores the interface with no task pressure. Clickable explore zones explain every element. The goal is just familiarity. No failure state.

### Level 1 — Guided / Follow Along
"Follow the steps."

A specific task is presented. Each step is highlighted. Clicking the wrong field shows a gentle redirect. The emphasis is on building correct muscle memory — not testing it.

This is where most existing training products stop.

### Level 2 — Semi-Guided / Do It
"You know this. Try it."

The same task, but highlights are removed. Neutral screens include 2–3 decoy fields styled with subtle blue borders to create multiple plausible click targets. Hints are available but cost XP. After 3 consecutive wrong clicks, the next hint becomes free (adaptive hint system). Errors trigger a structured consequence explanation panel — not just a "wrong" indicator.

### Level 3 — Challenge / Speed Run
"Real conditions, timer on."

A narrative premise card sets the scene before the scenario begins. No hints. Visible countdown timer with audio ticks in the last 10 seconds. Score recorded. The narrative rotates from a pool of 4 per scenario.

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

## UI Trainer Enhancement Status

### Built and Working

| Feature | Status | Notes |
|---|---|---|
| Challenge Mode with Timer | ✅ Built | Visible countdown, audio tick in last 10s, timeout alert |
| Confetti Animation | ✅ Built | Canvas-based confetti burst on successful completion |
| Narrative Premise Cards | ✅ Built | 4 rotating narratives per scenario, shown before Level 3 |
| Error Consequence Explanations | ✅ Built | Structured panels on wrong clicks in Levels 2–3 |
| Post-Level Debrief | ✅ Built | Expandable "why each step matters" cards after Levels 1–2 |
| Decoy Fields | ✅ Built | 2–3 non-target fields on neutral screens (Levels 2–3) |
| Adaptive Hints | ✅ Built | After 3 consecutive wrong clicks, next hint is free |
| Review Mode | ✅ Built | 5 scrambled steps accessible from win screen |
| Audio Cues | ✅ Built | Web Audio API: correct/wrong tones, timer tick, fanfare |
| Multi-Domain Branding | ✅ Built | SAP blue vs. steel grey, domain-specific level names |

### Remaining Enhancements

**1. Achievement Badges**
Define 8–10 badges with clear unlock conditions. Store in JSON alongside the learner session. Display on the HUD. Zero new scenario content required.

**2. XP Persistence**
Currently XP resets per session. Requires localStorage or a lightweight backend to persist across sessions.

**3. Leaderboard (Site-Level)**
Requires a minimal backend — a JSON file or lightweight API that stores scores per user per scenario. Can be file-based for the PoC. Weekly reset. Display on the HUD.

---

## Hardware Training Domain

The game engine now supports hardware training scenarios alongside software. The same four-level progression applies — the difference is in the branding (steel grey shell, safety orange accent) and the level nomenclature (OBSERVE / FOLLOW ALONG / DO IT / SPEED RUN).

The first hardware scenario is an AR-15 field strip: 8 steps from verification clear through disassembly, inspection, cleaning, lubrication, reassembly, and function check. The consequence model maps directly: skipping clearance verification → negligent discharge risk; forcing takedown pins with a steel tool → deformed pin holes and receiver wobble.

Hardware scenarios currently use Pillow-drawn placeholder diagrams (rifle silhouettes, BCG exploded views). These can be swapped for real photographs — hotspot coordinates just need to match the photo layout. The `base_hardware.py` module provides annotation helpers that work on any base image (photo or placeholder).

Future hardware scenarios could include: Glock field strip, M4 armorer-level maintenance, oil change procedure, brake pad replacement, industrial equipment lockout/tagout. Each would follow the same scenario pack contract: SCENARIO dict + SCREEN_GENERATORS dict + `generate_screens()` function.

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
