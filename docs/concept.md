# Zero-Touch, AI-Generated ERP Training

## The Problem We're Solving

ERP training today is expensive to create, slow to update, quickly outdated, and detached from how the system actually changes.

At GlobalMart distribution centers (and other retail operations), this is amplified by:

- Site-specific processes (Opal overlays)
- Multiple UI layers (SAP, Fiori, Appian, etc.)
- High personnel turnover and mixed experience levels

## The Core Idea

Training should be generated from the same assets that keep the system running.

Instead of manually authoring courses and job aids:

- Use automated test scripts, process models, and configuration data as the source of truth
- Apply AI to compile those assets into training materials
- Automatically update training whenever the system changes

This is **Training-as-Code**, embedded in the DevSecOps pipeline.

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

- WalkMe (or similar) provides point-of-need guidance
- AI generates draft WalkMe flows from test scripts and UI metadata
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
| **Automated Testing (e.g., Tosca)** | Primary execution truth — step-level fidelity, change detection via regression testing |
| **AI** | Translates technical assets into human-usable training — generates videos, job aids, and in-app guidance drafts |
| **WalkMe** | Delivery surface, not the authoring engine |

## Why This Is Credible Now

The same AI techniques used to rapidly generate viral video content ("Bigfoot videos") are applied here in a governed, enterprise-safe way: script generation, video generation, workflow orchestration, and minimal human editing.

The difference is governance, security, and accuracy — not core capability.

## Pilot Approach

- One role
- One end-to-end process slice
- One site (GlobalMart SE-DC, Atlanta, GA)
- One person, ~1–2 weeks

**Outputs:**

- AI-generated process explainer video
- Several role-specific job aids
- Optional WalkMe draft

**Goal:** Prove speed, accuracy, and maintainability — not perfection.

## Executive Soundbite

> "We're not building training. We're compiling it from the same assets that already keep the system running."
