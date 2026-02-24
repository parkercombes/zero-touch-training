# Layer 5 — Process Rationale & Consequence

## Learning Objective

> "I understand *why* we do it this way, what the alternatives are, when each applies, and what goes wrong if I choose incorrectly."

This layer addresses the most common source of costly ERP errors: people who know **how** to execute a process but not **why it's designed the way it is**. They substitute judgment for rules — and in an ERP environment, that judgment is often wrong and auditable.

---

## The Problem This Solves

Standard job aids (Layer 3) answer: *What do I click?*

Layer 5 answers:
- *Why this transaction and not that one?*
- *What is the system doing behind the scenes?*
- *What breaks downstream if I do it the wrong way?*
- *What does an auditor see when I make this choice?*

Without this layer, experienced users make confident mistakes. New users copy the wrong patterns from their peers. The consequences — financial misstatements, audit findings, supply chain disruption — take weeks or quarters to surface.

### Real Example: Found-on-Installation Goods Receipt

A material is found during an installation project that wasn't in the original goods receipt quantity. A trained user knows how to post a goods receipt in MIGO. But which transaction? Which movement type? Should it reference the PO or not?

| Choice | Looks the same to the user | Actual consequence |
|---|---|---|
| GR against PO (correct) | Posted successfully | 3-way match intact, AP can pay, audit clean |
| Free GR without PO | Posted successfully | GR/IR imbalance, AP payment blocked, SOX finding |
| GR to blocked stock (wrong movement type) | Posted successfully | Inventory unavailable, cold chain item may expire |

All three routes complete without an error message. The system won't stop you. Only the downstream consequence — sometimes weeks later — reveals the mistake.

---

## Content Structure

Each Process Rationale artifact covers one process or decision node and contains four sections.

### 1. Process Variant Decision Map

*When do you use this process versus the alternatives?*

- Lists two to four process variants that cover the same business scenario
- For each variant: triggering condition, correct usage context, who initiates it
- Decision tree or table format — scannable in the moment of decision
- Sourced from: BPMN gateway conditions, process variant documentation

**Example — Goods Receipt Options:**

| Scenario | Correct Process | Movement Type |
|---|---|---|
| Planned delivery against PO | GR against Purchase Order | 101 |
| Material found during installation, PO exists | GR against PO, reference existing PO line | 101 |
| Material found, no PO exists | Stop — raise emergency PO first | n/a |
| Return of vendor material | Return delivery against PO | 122 |

### 2. Anti-Pattern Gallery

*What does the wrong way look like, and why does it fail?*

For each anti-pattern:
- **Name** — what people call this approach colloquially
- **Why it feels right** — the intuitive logic that leads someone there
- **Why it's wrong** — the specific rule or control it violates
- **Immediate consequence** — what happens in the system right away
- **Downstream consequence** — what breaks later, and when it surfaces
- **Who notices** — auditor, AP team, warehouse manager, compliance officer

This section is written to be *empathetic* — it acknowledges why smart people make these mistakes, not to blame but to inoculate.

### 3. Consequence Matrix

*A structured mapping of deviation → impact.*

| Deviation | System Impact | Financial Impact | Compliance Impact | Who Is Affected |
|---|---|---|---|---|
| GR without PO reference | GR/IR account open item | AP accrual overstated | SOX 3-way match failure | External auditor, AP team |
| Wrong movement type | Inventory in blocked stock | Inventory write-down risk | Regulatory if perishable | Warehouse, production planning |

Sourced from: Opal overlay validation rules, SAP control documentation, audit finding history.

### 4. Compliance & Regulatory Context

*Why does the process exist the way it does?*

- The business control the process enforces (e.g., 3-way match, segregation of duties)
- The regulation or standard it satisfies (SOX, FDA cold chain, GAAP inventory valuation)
- What an auditor looks for in the system transaction log
- The specific audit question this process answers

This section transforms a procedural rule into a governance story. Users who understand the *why* make better decisions in edge cases that aren't covered by any job aid.

---

## Source Assets

| Asset | What It Provides |
|---|---|
| BPMN process models (Signavio/XML) | Decision gateways — the formal points where process variants diverge |
| Tosca test scripts | Negative test cases — what the system validates as incorrect |
| Opal overlay (`consequences` section) | Site-specific deviations, audit rules, downstream impact mapping |
| SAP configuration (field rules, movement types) | Why certain fields are mandatory, what posting rules enforce |

### New Data Requirement: `consequences.yaml`

The existing `opal_overlay.yaml` stores site-specific process variations. Layer 5 requires a new data file — `consequences.yaml` — that stores per-process consequence mappings:

```yaml
processes:
  - id: goods_receipt_po
    name: "Goods Receipt against Purchase Order"
    transaction: MIGO
    anti_patterns:
      - id: free_gr_no_po
        name: "Posting GR without PO reference"
        why_feels_right: "Faster — no need to locate the PO number"
        why_wrong: "Breaks 3-way match. AP cannot match invoice to GR."
        consequences:
          - { category: financial, description: "GR/IR open item, AP accrual overstated" }
          - { category: audit, severity: critical, description: "SOX 3-way match control failure" }
          - { category: operational, description: "Vendor payment blocked until corrected" }
        recovery: "Reverse the GR (movement type 102), re-post with PO reference"
    compliance:
      regulation: "SOX Section 404"
      control: "Purchase-to-Pay 3-way match (PO / GR / Invoice)"
      audit_question: "Does every goods receipt trace to an approved purchase order?"
```

---

## Generation Approach

The AI is given:
1. The process name and transaction code
2. The BPMN gateway conditions for that process (when does the flow diverge?)
3. Relevant Tosca test steps (including negative/validation test cases)
4. The `consequences.yaml` entry for that process
5. The Opal overlay rules for the site

The AI generates a structured Markdown document in the four-section format above.

**Key instruction to the AI:** Generate the anti-patterns with empathy. The goal is not to warn users away from mistakes through fear, but to give them a mental model so they make the right call instinctively in edge cases.

---

## Human-in-the-Loop Requirements

This layer carries higher review requirements than Layers 1–4 because:

- Consequence descriptions must be factually accurate — an incorrect consequence mapping is worse than no mapping
- Compliance context must be reviewed by someone with audit/controls knowledge
- Anti-pattern names must match the colloquial language the site actually uses (not formal SAP terminology)

**Recommended review:** SME sign-off **plus** a reviewer from Finance/Compliance before publication.

---

## Delivery Format

| Format | Use case |
|---|---|
| Markdown (rendered) | Intranet / LMS page — searchable, linkable |
| PDF card (2-page) | Printable laminated quick reference |
| WalkMe smart tip | In-app popup at the decision gateway field |
| Layer 2 video segment | 60–90 second "why this way" insert in the process explainer video |

The WalkMe integration is particularly valuable: at the exact moment a user reaches a process decision point, a smart tip surfaces the consequence context without requiring them to leave the screen.

---

## Relationship to Other Layers

```
Layer 3 (Execution) ──► "Here are the steps"
Layer 5 (Rationale) ──► "Here is why, and what breaks if you deviate"
Layer 4 (WalkMe)    ──► "Reminder at the exact moment of the decision"
Layer 6 (Drift)     ──► "When the process changes, the rationale updates too"
```

Layer 5 content is version-controlled alongside the process it describes. When a BPMN model changes, the rationale artifact is flagged as stale and regenerated for SME review — same drift pipeline as Layers 1–4.

---

## Note on Layer Numbering

This layer is inserted between the former Layer 4 (In-App Assistance) and the former Layer 5 (Continuous Update & Drift Control). With the addition of this layer, the numbering becomes:

- Layer 1 — Navigation & Orientation
- Layer 2 — End-to-End Process Understanding
- Layer 3 — Role-Specific Execution
- Layer 4 — In-App Assistance (WalkMe)
- **Layer 5 — Process Rationale & Consequence** *(new)*
- Layer 6 — Continuous Update & Drift Control
