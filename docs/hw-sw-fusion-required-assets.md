# Hardware/Software Fusion Scenarios — Required Assets

This document is the buyer-facing checklist for HW/SW fusion training. It answers one question: *what does an organization need to have so that the Zero-Touch Training pipeline can compile a fusion scenario for them?*

The PoC scenario in `poc/generators/scenarios/drone_preflight.py` demonstrates the engine handling a 6-step alternating procedure. The same engine renders any scenario whose assets fit the categories below.

---

## The Core Premise

Zero-Touch Training does not author training. It **compiles training** from assets the organization already maintains for other reasons — test automation, configuration management, technical documentation, regulatory compliance. If those assets exist and are accessible, the pipeline produces training that stays in sync with the underlying system.

For HW/SW fusion scenarios specifically, the principle is the same. The training compiles from the same assets that maintenance technicians, software engineers, and operators already use. When firmware updates, the software steps update. When the hardware revision changes, the hardware steps update. The training never falls out of date because it was never authored — it is regenerated.

What this document defines is the minimum asset set required for that compilation to work.

---

## Asset Categories

Seven categories, each with: where the asset lives in a typical organization, what it produces in the training, and what the PoC substitutes when the real asset is not yet available.

### 1. Hardware part identification photos

**Source:** OEM technical manual, parts catalog, IETM (Interactive Electronic Technical Manual), or in-house photography.

**What it produces:** Layer 1 (Navigation) hardware steps — annotated photographs with hotspot callouts identifying components the trainee must locate, inspect, or manipulate.

**Format:** Still images, ideally 1280×720 or higher, with components clearly visible at the angle a technician will see them in the field.

**PoC substitute:** Pillow-drawn schematic representations of drone components (top view of airframe with propellers, rear view of battery compartment, front view of gimbal). The placeholders deliberately look schematic rather than photographic so the gap between mockup and production is visible to the buyer.

**Production replacement effort:** Small. A drone OEM with a Mini 4 Pro asset library can drop in marketing photos, captioned with hotspot coordinates, in a few hours per scenario.

---

### 2. Software UI screenshots or capture session

**Source:** Live system access via Playwright (or equivalent browser automation), in-app screen recording, app store marketing screenshots, or vendor-provided UX assets.

**What it produces:** Layer 1 software steps — screen states with hotspot regions marked, used by the engine for click-target validation.

**Format:** Still images at app rendering resolution, with element bounding boxes captured as hotspot coordinates. The Zero-Touch Training Playwright capture pipeline (`poc/capture/`) already automates this for web-based UIs.

**PoC substitute:** Pillow-drawn mockups of a generic Drone Fly-style mobile app (aircraft connection screen, GPS lock screen, RTH altitude config screen). The mockups intentionally use the same visual language as the SAP Fiori scenarios in this PoC so the engine treats them identically.

**Production replacement effort:** Trivial for web UIs (Playwright capture is already built). For native mobile apps, requires manual screen capture or vendor cooperation. A modern OEM app captured via Android emulator and screencap is roughly 30 minutes per scenario.

---

### 3. Maintenance / operator procedure document

**Source:** Technical Manual (TM), IETM, operator manual, OEM pre-flight checklist, maintenance procedure SOP, or — most directly — the automated test scripts that already validate the procedure.

**What it produces:** Layer 3 (Execution) — the ordered step sequence with action verbs, inputs, and assertions. This is what the trainee actually does in the scenario.

**Format:** Structured procedure with explicit step ordering, action types (inspect, click, enter value, verify), and pass/fail criteria per step. Tosca XML, Selenium scripts, BPMN task sequences, or numbered TM procedures all qualify.

**PoC substitute:** Procedure inferred from public Part 107 guidance, manufacturer pre-flight checklists, and FAA general operating rules for sUAS. The 6-step PoC sequence is a deliberately simplified subset of what a full pre-flight covers.

**Production replacement effort:** This is the highest-leverage asset category. If the buyer has Tosca tests for their procedure, the existing parser handles it directly. If they have a TM but no test automation, the procedure needs to be either parsed from structured text or transcribed once. After that, regeneration is automatic.

---

### 4. Decision and branching logic

**Source:** Procedure flowcharts, BPMN process models, decision matrices in TMs, conditional logic embedded in test scripts.

**What it produces:** Layer 2 (Process) — the swimlane explainer showing when the operator does hardware vs. software steps and why the alternation matters. Also feeds the rotating premise cards at Level 3 (CHALLENGE).

**Format:** BPMN 2.0 XML is the canonical input. Visio flowcharts, structured Markdown decision trees, or even prose describing branch conditions can be parsed as alternatives.

**PoC substitute:** Implicit branching only — the scenario is linear (six steps in order). The four rotating premise cards (first flight of the morning, new site, firmware updated last night, rental aircraft) are stand-ins for the kind of branch context a real BPMN model would encode.

**Production replacement effort:** Medium. Most organizations have *some* form of decision documentation but not in BPMN. A short engagement with a process owner produces a usable BPMN model in a day or two.

---

### 5. Failure modes and consequences

**Source:** Maintenance history records, FRACAS (Failure Reporting, Analysis, and Corrective Action System), FMEA documents, incident reports, post-mortem records, manufacturer technical bulletins, public crash databases (NTSB for aviation, NHTSA for ground vehicles).

**What it produces:** Layer 5 (Rationale) — the "why this matters" cards shown after each step in the post-level debrief. Converts mechanical instructions into reasoned understanding.

**Format:** Structured association of *step* → *what goes wrong if skipped or done incorrectly* → *downstream consequence*. The Zero-Touch Training pipeline uses a `consequences.yaml` file to encode this.

**PoC substitute:** Consequences inferred from public crash reports, drone forum incident discussions, OEM advisory bulletins, and manufacturer documentation about specific failure modes. Each step in the drone scenario has a `consequence` field that explains what happens when that check is skipped — propeller separation in flight, battery vibration loss, RTH-into-obstacle, and so on.

**Production replacement effort:** High initial, low ongoing. Building the first FMEA association takes effort because organizations rarely have it pre-structured. After it exists, it is reusable across all scenarios that touch the same components.

---

### 6. Software version and part number metadata

**Source:** Configuration management database (CMDB), parts management system, firmware versioning system, software bill of materials (SBOM), or OEM compatibility matrices.

**What it produces:** Layer 6 (Drift Detection) — the assets that change-detection compares against. When a firmware version increments or a part number is superseded, drift detection flags the affected scenarios for regeneration.

**Format:** Any structured representation that uniquely identifies the version of each component the training assumes. The PoC uses YAML for overlays; an enterprise customer would point at their existing CM system.

**PoC substitute:** Embedded version strings in the scenario module ("Firmware v01.04.0500", "App v1.13.4") and a placeholder note that production drift detection would query a real CMDB for these values.

**Production replacement effort:** Small if the customer has a CMDB or equivalent. Larger if they don't — but the absence of one is a maintenance problem the customer already has, not one this platform creates.

---

### 7. Safety and compliance constraints

**Source:** Regulatory references (FAA Part 107 for sUAS, OSHA for industrial, DOT for hazmat, AR 95-23 for Army aviation), MIL-STD requirements, organizational safety SOPs, manufacturer-specified operating limits.

**What it produces:** Embedded warnings, hold points, and compliance text that appears in the scenario at the appropriate steps. Also drives Layer 5 rationale text where regulatory consequence matters.

**Format:** Constraint statements with explicit step bindings — *before takeoff, verify NFZ status (Part 107 §107.41)*, *before powering, disconnect battery (manufacturer safety)*.

**PoC substitute:** Public Part 107 references, FAA NFZ guidance, and generic safety language for pre-flight inspection. The drone scenario references Part 107 §107.41 (operations in controlled airspace) and the 400 ft AGL altitude limit.

**Production replacement effort:** Small. Regulatory text rarely changes; once embedded, it propagates across all scenarios in that domain.

---

## Asset-to-Layer Mapping

For quick reference, here is which asset category feeds which training layer:

| Asset Category | Layer 1 Navigation | Layer 2 Process | Layer 3 Execution | Layer 5 Rationale | Layer 6 Drift |
|---|:-:|:-:|:-:|:-:|:-:|
| Hardware photos | ● | | | | ● |
| Software UI captures | ● | | | | ● |
| Procedure document | | | ● | | ● |
| Branching logic | | ● | | | ● |
| Failure modes | | | | ● | |
| Version metadata | | | | | ● |
| Safety constraints | | ● | | ● | |

Layer 4 (In-App) is generated as a derivative of Layer 1 + Layer 3 and does not require its own asset category.

---

## Pre-Engagement Asset Audit

Before a real customer engagement begins, a 60-minute audit answers four questions for the candidate scenario:

**1. Do hardware photos exist?**
   - If yes: are they at sufficient resolution, and do they show the right angles for an operator's perspective?
   - If no: who has access to the hardware and a camera? (Bias toward in-house photography over OEM marketing assets — operator-perspective angles matter more than studio polish.)

**2. Are software screenshots accessible?**
   - If the software is web-based: Playwright capture against a dev/training environment, no manual work needed.
   - If the software is mobile native: who has device access and screen-capture capability?

**3. Where does the procedure live?**
   - Existing test automation (Tosca, Selenium, Playwright): plug directly into existing parsers.
   - TM or operator manual only: one-time transcription; subsequent updates flow through revision control.
   - Tribal knowledge only: requires SME engagement before scenario generation can begin.

**4. Is there configuration management for the relevant components?**
   - Firmware versions, part numbers, software versions tracked somewhere?
   - If yes: drift detection wires into that source.
   - If no: drift detection still works against snapshotted source files, but the customer is missing a CM capability that bites them outside training too.

Outcomes of the audit: green-light scenario, partial green-light with substitutions, or red-light pending asset development. The PoC drone scenario was built green-light against entirely public assets, which proves the audit can be executed end-to-end against an organization that does not yet have a formal asset library.

---

## What the PoC Drone Scenario Specifically Proves

The drone pre-flight scenario in this repository validates four claims that matter for HW/SW fusion deployment:

**1. The engine handles alternating step types without modification.**
   The React trainer engine renders both hardware (photo annotation) and software (app screen) step types from a single ordered sequence. No engine code branched on step type; the abstraction was already adequate.

**2. The visual language can stay consistent across step types.**
   Hardware steps use the safety-orange/steel palette; software steps use the same palette inside a generic app shell. The trainee experiences one trainer, not two stitched together.

**3. The asset categories above are sufficient.**
   Every element of the drone scenario maps to one of the seven categories. Nothing is missing, and nothing is required that does not appear on the list.

**4. Substitutability is real.**
   The drone scenario was built against entirely public, commercial assets with no vendor relationships, no IP licensing, and no classified materials. The same engine and the same scenario structure would render identically against a customer's proprietary assets — only the contents of the seven categories change.

---

## Out of Scope for This Document

What this document deliberately does not address:

- **Specific scenario authoring** — choosing which procedure to build a scenario for is a content-strategy decision, not an asset question.
- **SME validation methodology** — once a scenario is generated, a subject matter expert reviews it for accuracy. That process is described separately in the pilot charter.
- **Procurement and contracting paths** — SBIR, OTA, CSO, DFARS pathways for funding a deployment are tracked in separate program documentation.
- **Multi-language deployment** — the asset categories above produce English content. Multilingual rendering is a separate pipeline concern (TTS overlay, translation memory, etc.).

---

## Document Change Log

| Date | Change |
|---|---|
| 2026-05-02 | Initial version written alongside the drone pre-flight PoC scenario. |
