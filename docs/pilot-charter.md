# Zero-Touch Training Project — Proof of Concept Charter

**Document Version:** 1.0
**Date:** February 2026
**Status:** Draft for Review

---

## 1. Proof of Concept Purpose

The Zero-Touch Training PoC aims to validate that **AI-generated training can be produced from existing DevSecOps assets (automated test scripts, process models, and UI metadata) faster, cheaper, and more maintainably than traditional manual authoring.**

### What We're Proving

- **Feasibility:** AI can accurately translate Tosca test scripts and Signavio process models into multi-layer training content
- **Speed:** Training generation is 5–10x faster than manual course development
- **Quality:** Generated content achieves ≥95% accuracy against actual system behavior, as validated by subject matter experts
- **Maintainability:** Training updates can be automatically regenerated when underlying test scripts or process models change, enabling true "Training-as-Code" in the DevSecOps pipeline
- **Economics:** Production cost and effort are demonstrably lower than traditional training authoring

If successful, this PoC creates a scalable foundation for rapid, self-updating ERP training across multiple processes, roles, and sites.

---

## 2. Scope

The PoC is tightly scoped to ensure clear outcomes and controlled complexity.

### In Scope

| Dimension | Definition |
|-----------|-----------|
| **Site** | GlobalMart Southeast Distribution Center (Atlanta, GA) |
| **Process** | Purchase Requisition to Goods Receipt (MM-PUR end-to-end slice) |
| **Role** | Buyer / Requisitioner |
| **Training Layers** | Layer 1 (navigation walkthrough), Layer 2 (process explainer video), Layer 3 (role-specific job aids), Layer 4 (WalkMe draft—optional) |
| **System** | SAP S/4HANA 2023 (Fiori environment, production or sandbox) |
| **Duration** | 2 weeks |
| **Personnel** | 1 PoC lead, 1 SME, 1 sponsor |

### Out of Scope

- Training for other roles in the process (Approver, Goods Receiver, etc.)
- Other processes or sites
- Full instructor-led training or virtual classroom design
- Learning Management System (LMS) integration or deployment
- Ongoing production support (post-PoC)

### Process Selection Rationale

The Purchase Requisition to Goods Receipt process is a canonical ERP workflow that:
- Is well-documented in Tosca test scripts (high coverage expected)
- Has clear, sequential steps
- Involves one primary actor per stage (minimal branching complexity)
- Represents a high-frequency operational task (relevance to end users)

---

## 3. Success Criteria

All metrics are measured at the end of Week 2, before the go/no-go decision.

| Criterion | Target | Measurement Method |
|-----------|--------|-------------------|
| **Training Accuracy** | ≥95% step accuracy vs. actual system behavior | SME walkthrough validation of generated content against Fiori UI |
| **Generation Speed** | 5–10x faster than manual authoring baseline | Compare AI pipeline execution time vs. estimated manual course development (24–40 hrs) |
| **SME Approval Rating** | ≥4/5 on clarity, completeness, and usability | Structured review questionnaire (5-point Likert scale) |
| **Coverage Completeness** | 100% of process steps represented across layers | Traceability matrix: Tosca test steps → generated walkthroughs |
| **Automation Feasibility** | Documented, reproducible process for regeneration | One successful test: regenerate training after modifying a test script or process model; measure time and validation effort |

---

## 4. Prerequisites & Dependencies

The PoC cannot start until all prerequisites are confirmed.

### Required Inputs

| Item | Status | Owner | Due Date |
|------|--------|-------|----------|
| **Tosca Test Scripts** | Access to current, updated test scripts for Purchase Req→GR process | QA/Testing Team | Before Week 1 kickoff |
| **Signavio Process Model** | Current process model for SE-DC site configuration | Process Owner | Before Week 1 kickoff |
| **SAP/Fiori Access** | Read-only access to sandbox or production Fiori environment; OR high-quality screenshots/recording of the process flow | Basis/System Admin | Before Week 1 kickoff |
| **AI Tooling Stack** | Selection and provisioning of AI models/APIs (specify LLM, vision models, orchestration framework) | Technical Lead | During Week 1 setup |
| **SME Availability** | One process owner or power user, ~2–4 hours total (split across Week 2) | HR / Sponsor | Confirmed before kickoff |
| **PoC Lead** | 1 dedicated resource, ~30–40 hours over 2 weeks | Sponsor | Confirmed before kickoff |

### Infrastructure Assumptions

- Cloud or on-premise compute environment capable of running AI inference and generation pipelines
- Secure credential management for system access (Tosca, Signavio, SAP)
- Network connectivity to all required systems
- Version control (Git) for training artifacts and pipeline code

---

## 5. Timeline & Milestones

### Week 1: Asset Collection & Pipeline Setup

| Day | Activity | Deliverable | Owner |
|-----|----------|-------------|-------|
| **Monday–Tuesday** | Kick-off meeting; collect Tosca scripts, process model, and UI screenshots | Baseline assets in PoC repository | PoC Lead, SME |
| **Wednesday** | AI tooling selection and environment setup | Configured pipeline environment, documented tool stack | Technical Lead |
| **Thursday** | Run initial generation pipeline on collected assets | Draft Layer 1 (walkthrough) + Layer 2 (video script/storyboard) | PoC Lead |
| **Friday** | Validation check: do generated outputs match system? Iterate if needed | Refined Layer 1 & 2 outputs ready for SME review | PoC Lead, Technical Lead |

### Week 2: Refinement & Validation

| Day | Activity | Deliverable | Owner |
|-----|----------|-------------|-------|
| **Monday–Tuesday** | Generate Layer 3 (job aids); conduct initial accuracy audit | 3–5 role-specific job aids; accuracy assessment notes | PoC Lead |
| **Wednesday** | Optional: draft Layer 4 (WalkMe flow); collate all outputs | Complete training content package | PoC Lead |
| **Thursday** | SME review session: walkthrough, Q&A, feedback | SME sign-off form; change/refinement log | SME, PoC Lead |
| **Friday** | Incorporate SME feedback; document regeneration process; prepare final report | Final training artifacts; PoC results report; post-PoC recommendations | PoC Lead, Technical Lead |

### Go/No-Go Decision

- **Target Date:** End of Week 2 (Friday EOD)
- **Decision Forum:** Sponsor + PoC Lead + SME
- **Decision Criteria:** All success metrics reviewed; recommend Proceed, Iterate, or Pause

---

## 6. Deliverables

All deliverables are stored in `/zero-touch-training/poc-output/` and version-controlled in Git.

### Training Content

1. **Layer 1: Navigation Walkthrough** — Screenshot-annotated step-by-step guide; HTML or PDF
2. **Layer 2: Process Explainer** — Scripted video or animated storyboard (5–8 minutes); MP4 + script
3. **Layer 3: Job Aids** — 3–5 role-specific aids (e.g., "How to Create a Purchase Requisition," "Exception Handling: Missing Cost Center"); Markdown or PDF
4. **Layer 4: WalkMe Draft** — Interactive overlay specification (if tooling permits); JSON or PNG mockups

### Documentation & Reports

5. **PoC Results Report** — Executive summary, success metrics scorecard, lessons learned, recommendations for next phase
6. **Regeneration Process Guide** — Step-by-step instructions to regenerate training if test scripts/process model changes; includes pipeline code and maintenance runbook
7. **Technical Asset Inventory** — Catalog of Tosca test IDs, Signavio model elements, and Fiori UI identifiers used in generation

---

## 7. Roles & Responsibilities

### RACI Matrix

| Activity | PoC Lead | SME | Technical Support | Sponsor |
|----------|------------|-----|-------------------|---------|
| Asset collection & provisioning | C | R | R | I |
| Pipeline design & implementation | R | C | R | I |
| Generation execution | R | C | S | I |
| Accuracy validation | R | R | S | I |
| SME review & sign-off | S | R | — | I |
| Final report & go/no-go recommendation | R | C | R | A |

**Legend:** R = Responsible | A = Accountable | C = Consulted | S = Supported | I = Informed

### Detailed Responsibilities

**PoC Lead (1 FTE, 30–40 hours)**
- Coordinate all PoC activities and timeline
- Manage asset collection and environment setup
- Execute generation pipeline
- Conduct validation and quality assurance
- Facilitate SME review
- Document findings and regeneration process
- Present results to sponsor

**SME / Process Owner (~4–6 hours)**
- Confirm completeness of collected process documentation
- Review generated training content for accuracy and clarity
- Validate against actual system behavior
- Provide sign-off on Layer 3 job aids
- Answer clarifying questions during review

**Technical Support (as needed)**
- Provision access to Tosca, Signavio, and SAP systems
- Set up compute environment and AI tooling
- Assist with troubleshooting infrastructure issues
- Provide database/system information as needed

**Sponsor / Stakeholder (~2–3 hours)**
- Attend kick-off and go/no-go meeting
- Confirm resource availability and remove blockers
- Review final report and endorse next steps
- Communicate results to broader leadership

---

## 8. Risks & Mitigations

### Top 5 Risks

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|-----------|-------|
| **Insufficient Tosca test coverage** | Medium | High | Audit test scripts early (Week 1, Day 1); identify gaps; supplement with manual UI inspection if needed. Have backup process identified. | QA + PoC Lead |
| **System access delays** | Medium | High | Submit access requests 1 week before PoC start. Escalate blockers to Sponsor immediately. Have sandbox credentials pre-staged. | Technical Support |
| **AI accuracy below 95% threshold** | Medium | Medium | Run small validation sample by Day 4 (Week 1). If accuracy <90%, pivot to manual refinement or tooling adjustment in Week 2. | PoC Lead + Technical Lead |
| **SME unavailability** | Low | High | Confirm SME commitment and calendar blocks during kick-off. Identify backup SME if needed. Conduct review sessions async if required. | Sponsor |
| **Scope creep** | Medium | Medium | Document out-of-scope items explicitly in this charter. PoC Lead enforces change control. Any new requests are logged as "post-PoC considerations." | PoC Lead |

---

## 9. Decision Point: Go/No-Go Framework

### Exit Criteria & Decision Logic

At the end of Week 2, the Sponsor, PoC Lead, and SME will evaluate success criteria and decide:

#### **GO** — Expand to Production
- Conditions:
  - ≥95% training accuracy achieved
  - Generation speed ≥5x faster than baseline
  - SME approval ≥4/5 on usability
  - Regeneration process documented and tested
- Next Steps:
  - Select second process for production pipeline
  - Plan for 2–3 additional sites over Q2/Q3
  - Estimate ROI and resource model for ongoing operation

#### **ADJUST** — Refine & Retry
- Conditions:
  - Most success criteria met, but one or two require tooling/process improvements
  - Root causes identified and feasible to fix
- Next Steps:
  - Extend pilot by 1 week to implement fixes
  - Retake measurements
  - Plan for production with known mitigations

#### **PAUSE** — Reassess
- Conditions:
  - Multiple success criteria missed; root causes unclear
  - Dependencies (access, tooling) remain unresolved
  - SME or sponsor concerns about feasibility
- Next Steps:
  - Conduct post-mortem
  - Document lessons learned
  - Evaluate alternative approaches
  - Plan for restart in future phase (if applicable)

---

## 10. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| PoC Lead | [TBD] | | |
| SME / Process Owner | [TBD] | | |
| Technical Support Lead | [TBD] | | |
| Sponsor / Stakeholder | [TBD] | | |

---

## 11. Appendices

### A. Process Flow Overview

**Purchase Requisition to Goods Receipt (Simplified)**

1. Requisitioner creates PR in Fiori (MM-PUR-01)
2. Manager approves PR (MM-PUR-02)
3. Procurement creates PO from PR (MM-PUR-03)
4. Vendor ships goods
5. Goods Receipt clerk receives goods (MM-GR-01)
6. System matches GR to PO/PR
7. Invoice received and matched

*This flow is the candidate for Layer 1–4 training content.*

### B. Training Layer Definitions

- **Layer 1 (Navigation Walkthrough):** Annotated screenshots showing step-by-step system navigation (e.g., "Click MM-PUR-01 > Manage Purchase Requisition > Create New > Fill Required Fields > Save").
- **Layer 2 (Process Explainer Video):** 5–8 minute video or animated storyboard explaining the business purpose of each step, integration with other processes, and common exceptions.
- **Layer 3 (Job Aids):** 1-page (or short) reference guides for specific tasks (e.g., "Expediting a Purchase Requisition," "Handling Missing Cost Center Exceptions").
- **Layer 4 (WalkMe Draft):** Interactive overlay prototype showing guided UI highlighting, field-level tips, and context-sensitive help (optional; depends on tooling capability).

### C. Success Metrics — Detailed Definitions

**Training Accuracy (≥95%)**
- Measured by SME walkthrough: for each step in the generated walkthrough, SME confirms it matches actual system behavior (yes/no).
- Accuracy % = (Verified Steps / Total Steps) × 100.
- Target: ≥95% of steps verified correct.

**Generation Speed (5–10x Faster)**
- Baseline: estimated 24–40 hours to manually author equivalent training content (typical for a 1-role, 1-process course).
- Measured: end-to-end pipeline execution time (asset prep → final outputs).
- Target: completed in 4–8 hours of total automated execution (excluding SME review time).

**SME Approval Rating (≥4/5)**
- SME completes 10-question survey (5-point Likert scale) on:
  - Clarity of instructions
  - Completeness of coverage
  - Accuracy of process flow
  - Usefulness for training end users
  - Overall quality
- Target: average score ≥4.0/5.0.

**Regeneration Feasibility**
- Success = document step-by-step process for re-generating training if test scripts change.
- Test = execute regeneration process with a minor change to a test script; measure time to new output and validation effort.
- Target: regeneration time < 2 hours; validation effort < 1 hour.

### D. Contacts & Escalation

- **PoC Lead:** [Name, Email, Phone]
- **Sponsor / Stakeholder:** [Name, Email, Phone]
- **SME:** [Name, Email, Phone]
- **Technical Lead:** [Name, Email, Phone]

For blockers or critical issues, escalate to Sponsor immediately.

---

**END OF PROOF OF CONCEPT CHARTER**
