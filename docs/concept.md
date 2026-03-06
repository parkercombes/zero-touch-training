# Zero-Touch, AI-Generated Training

## The Problem We're Solving

Training today is expensive to create, slow to update, quickly outdated, and detached from how the underlying systems and procedures actually change.

In ERP environments this is amplified by site-specific processes, multiple UI layers (SAP Fiori, Appian Low Code, etc.), and high personnel turnover. In hardware and maintenance environments the problem is parallel: procedures are taught person-to-person, institutional knowledge walks out the door, and mistakes during maintenance have real safety consequences.

## The Core Idea

Training should be generated from the same assets that keep the system running — or from the same procedures that define correct maintenance technique.

Instead of manually authoring courses and job aids:

- Use automated test scripts, process models, and configuration data as the source of truth
- Apply AI to compile those assets into training materials
- Automatically update training whenever the system changes

This is **Training-as-Code**, embedded in the DevSecOps pipeline.

The platform now supports two training domains through a single domain-agnostic game engine:

- **Software training** — ERP workflows (SAP MIGO Goods Receipt across 5 handling profiles)
- **Hardware training** — Equipment maintenance and assembly (AR-15 field strip pilot, extensible to automotive, industrial equipment, etc.)

## How the Training Works (Layered Model)

### Layer 1 – ERP Orientation & Navigation

**Goal:** "I'm not lost."

- AI-generated navigation walkthroughs
- Site-specific menus and access paths
- Derived from UI metadata and test automation

### Layer 2 – End-to-End Process Understanding

**Goal:** "I know where I fit."

- AI-generated explainer videos showing all roles in a process, inputs/outputs between roles, and what happens before and after the learner's task
- Generated with minimal post-production (Bigfoot-style AI video approach)

### Layer 3 – Role-Specific Execution

**Goal:** "I can do my job."

- Short, task-focused job aids
- Step-by-step execution guidance
- Generated directly from automated test scripts
- Includes site-specific (Opal) overlays where processes differ

### Layer 4 – In-App Assistance

**Goal:** "Help me while I'm doing it."

- Intelligent in-app support provides point-of-need guidance
- AI generates draft in-app guidance flows from test scripts and UI metadata
- Humans review and approve (no manual authoring from scratch)

### Layer 5 – Process Rationale & Consequence

**Goal:** "I understand *why* we do it this way."

Training that addresses the institutional knowledge gap: people who know how to execute a process but not why it is designed that way, when to use it versus alternatives, and what breaks if they choose incorrectly.

- Decision maps: when to use this process vs. similar alternatives
- Anti-pattern gallery: common wrong approaches with empathetic explanation of why they feel right and what actually breaks downstream
- Consequence matrix: who notices, when, and what the audit or operational impact is
- Compliance context: the business control the process enforces and what an auditor looks for in the transaction record

Sourced from: BPMN decision gateways, Tosca negative test cases, Opal overlay validation rules, and a `consequences.yaml` data file maintained by the SME team. SME review and Finance/Compliance sign-off required before publication.

### Layer 6 – Continuous Update & Drift Control

**Goal:** "Training is never outdated."

Training updates are triggered automatically by:

- Configuration changes
- UI changes
- Regression test updates or failures
- Process model version changes

If a regression test changes, training is assumed stale until regenerated and SME-validated.

## Site-Specific Reality (Opal Overlay)

Enterprise processes remain the baseline. Site-specific differences are applied as overlays. AI assembles training as:

```
Enterprise Process + Site Overlay + Role Context = Delivered Training
```

This allows reuse without ignoring local reality.

## Role of Key Systems

| System | Role |
|---|---|
| **SAP / Signavio** | Source of process and semantic truth (not the UI truth) |
| **Robust Testing Scripts** | Primary execution truth — step-level fidelity, change detection via regression testing |
| **AI** | Translates technical assets into human-usable training — generates videos, job aids, and in-app guidance drafts |
| **Intelligent In-App Support** | Delivery surface, not the authoring engine |

## Game-Inspired Training (The Engagement Layer)

Generating accurate training quickly is necessary but not sufficient. If nobody completes the training, accuracy doesn't matter. The engagement problem is as important as the content problem.

The UI trainer is built as a game, not a tutorial. It is a React single-page application with a `useReducer` state machine driving all game logic entirely client-side. The design draws on the same mechanics that make mobile games addictive and applies them to task simulation — both software (SAP) and hardware (equipment maintenance):

**All of the following are fully built and working:**

- **Four-level progression:** Level 0 (explore/orientation) → Level 1 (guided steps with highlights) → Level 2 (no highlights, hints cost XP, wrong clicks show consequences) → Level 3 (timer, no help, score goes on the board)
- **Domain-specific branding:** Software scenarios use SAP Fiori blue shell and level names (Explore / Guided / On Your Own / Challenge). Hardware scenarios use steel-grey shell with safety-orange accent and level names (OBSERVE / FOLLOW ALONG / DO IT / SPEED RUN). Branding is injected at build time.
- **Consequence-based error feedback:** Structured "what would happen in production" panels on wrong clicks in Levels 2–3
- **Timer with audio cues:** Visible countdown in Level 3, tick sounds in the last 10 seconds, timeout alert
- **Confetti celebration:** Visual celebration on successful completion
- **Narrative premise cards:** 2–3 sentence scenario cards before each Level 3 challenge, rotating from a pool of 4 per scenario
- **Post-level debrief screens:** Expandable "why each step matters" cards shown after Levels 1–2
- **Decoy fields:** 2–3 non-target fields on neutral screens (Levels 2–3) styled with subtle blue borders to create multiple plausible click targets
- **Adaptive hint system:** After 3 consecutive wrong clicks in Level 2, the next hint becomes free
- **Review mode:** 5 randomly selected steps in scrambled order, accessible from the win screen
- **Audio cues via Web Audio API:** Correct/wrong tones, timer tick, win fanfare

Game-based training is not new — products like UKG Pro's learning platform have demonstrated that story mode, character missions, and challenge levels significantly outperform traditional eLearning on completion rates. Nobody has built this for SAP or equipment maintenance at an affordable price point. That's the gap.

The AI-generation capability means the game content (scenarios, screens, scripts) updates automatically when the system changes. A traditional gamified training platform would require manual rework of every level after each ERP upgrade. This one recompiles.

## Generation Architecture (UI Trainer)

The interactive UI trainer is fully generated from source — no AI is involved at build time or runtime. A single command (`python3 ui_trainer.py`) produces a self-contained HTML file and all screen images. There is no server, no API call, and no model inference in the pipeline.

### Source Files

The source is organized into a domain-agnostic game engine, domain-specific base modules, and per-scenario packs:

- **`trainer_app.jsx`** — The React game engine (~1260 lines). A `useReducer` state machine drives all four progression levels plus review mode. It reads scenario data and branding injected as JSON globals and renders the interactive experience entirely client-side. The JSX is completely domain-agnostic — it resolves colors and level names from `SCENARIO.branding` with SAP defaults as fallback.
- **`scenarios/base.py`** — Software domain: shared Pillow drawing primitives (SAP Fiori fields, dropdowns, buttons, tables, checkboxes, shell bar) plus `SAP_BRANDING` dict export.
- **`scenarios/base_hardware.py`** — Hardware domain: photo annotation helpers (highlight/decoy regions, callout arrows, component labels), placeholder diagram generation, plus `HARDWARE_BRANDING` dict export.
- **Scenario packs** (e.g. `sedc_goods_receipt.py`, `ar15_field_strip.py`) — Each contains the complete scenario definition (steps, goals, instructions, hints, hotspots, consequences, explore descriptions, branding, mission) plus screen generator functions. Each is self-contained and imports from the appropriate base module.

### Build Process

The generator script (`ui_trainer.py`) reads the scenario module, calls its `generate_screens()` function (which renders highlighted PNGs for Levels 0–1 and neutral PNGs with decoy fields for Levels 2–3), reads the JSX file, and injects three JSON blobs (scenario data including branding, highlighted screen paths, neutral screen paths) plus the JSX source into a single HTML wrapper. The output is a standalone directory: `index.html` plus two screen folders.

A separate script (`generate_index.py`) auto-discovers all scenario modules, groups them by `training_domain` (software/hardware), and generates the scenario selector `index.html` with domain sections and profile-colored cards.

### Where AI Contributed Content

AI (Claude) authored the following content during the development process, not at runtime: all consequence descriptions (what happens in production if a step is done wrong), all explore-mode element descriptions, the narrative premises for Level 3, and the hint text for each step. These are plausible SAP MIGO descriptions based on general warehouse receiving knowledge but are not sourced from an actual SE-DC standard operating procedure or SAP configuration. For a real deployment, these strings would require SME review to ensure accuracy against the site's specific process.

Pixel coordinates for hotspots and field positions are calculated deterministically from the Pillow drawing code, not estimated or AI-generated.

### Pedagogical Features

The current build includes six pedagogical mechanics beyond the base four-level progression: consequence-based elaborated error feedback (structured "what would happen in production" panels on wrong clicks in Levels 2–3), post-level debrief screens (expandable "why each step matters" cards shown after Levels 1–2), audio cues via Web Audio API (correct/wrong tones, timer tick in the last 10 seconds, win fanfare, timeout alert), a Review mode (5 randomly selected steps in scrambled order, accessible from the win screen), an adaptive hint system (after 3 consecutive wrong clicks in Level 2, the next hint becomes free), and decoy fields on neutral screens (2–3 non-target fields styled with subtle blue borders and tints to create multiple plausible click targets).

## Why This Is Credible Now

The same AI techniques used to rapidly generate viral video content ("Bigfoot videos") are applied here in a governed, enterprise-safe way: script generation, video generation, workflow orchestration, and minimal human editing.

The difference is governance, security, and accuracy — not core capability.

The game mechanics gap is a distribution and incentive problem, not a technical one. The hard part — generating accurate, up-to-date simulation content at near-zero marginal cost — is what this system solves.

## Pilot Approach (all fabricated data)

This PoC uses a fictional company — "GlobalMart Southeast Distribution Center" — with entirely fabricated process data, test scripts, and site configurations. No real enterprise data is used.

- One role (Buyer)
- One end-to-end process slice (Purchase Requisition → Goods Receipt)
- One fictional site (GlobalMart SE-DC, Atlanta, GA)
- One person, off-hours development

**Outputs:**

- AI-generated process explainer video
- Several role-specific job aids
- Interactive UI trainer with game mechanics
- Optional in-app guidance drafts

**Goal:** Prove speed, accuracy, and maintainability — not perfection.

## Current Status

The PoC to date covers Layers 1 through 5 with working code: navigation walkthroughs, AI-generated explainer videos (including a lip-synced Bigfoot character vlog built on Google Veo 3), role-specific job aids, in-app guidance drafts, and process rationale content. Layer 6 (continuous update triggers) is designed but not yet automated.

The interactive UI trainer is a React single-page application with a fully built game engine. It supports two training domains through a branding abstraction layer: software (5 SAP MIGO handling profiles — standard dry, perishable, pharma, hazmat, serialized) and hardware (AR-15 field strip pilot). All game mechanics — four-level progression, consequence feedback, timer with audio cues, confetti, narrative premises, decoy fields, debrief screens, adaptive hints, and review mode — are fully implemented and working.

An auto-generated scenario selector groups all scenarios by domain and provides a landing page with profile-colored cards.

Total development time: 18 days of off-hours work. Total external API spend: less than $200.

## Executive Soundbite

> "We're not building training. We're compiling it from the same assets that already keep the system running."
