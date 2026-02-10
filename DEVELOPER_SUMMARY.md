# Zero-Touch Training — Developer Summary

**Repo:** [github.com/parkercombes/zero-touch-training](https://github.com/parkercombes/zero-touch-training)

## What This Is

An AI pipeline that **generates ERP training materials from existing DevSecOps assets** — automated test scripts (Tosca), process models (Signavio/BPMN), and configuration data. No manual authoring. When the system changes, training updates automatically.

The tagline: *"We're not building training. We're compiling it from the same assets that already keep the system running."*

## Who It's For

Army depot ERP users (starting at Anniston Army Depot). The system sits on top of SAP, Fiori, and Appian, with site-specific process overlays.

## Five Training Layers

| Layer | Goal | Source | Output |
|---|---|---|---|
| 1. Navigation | "I'm not lost" | UI metadata + test scripts | Step-by-step walkthroughs |
| 2. Process | "I know where I fit" | BPMN process models | Explainer videos |
| 3. Execution | "I can do my job" | Tosca test scripts | Role-specific job aids |
| 4. In-App | "Help me while I'm doing it" | Test scripts + UI element IDs | WalkMe flow drafts |
| 5. Updates | "Training is never outdated" | Change detection across all sources | Auto-regeneration triggers |

## Repo Structure

```
zero-touch-training/
├── README.md
├── docs/
│   ├── concept.md              # Full project concept
│   ├── architecture.md         # System design, data flows, AI pipeline
│   ├── pilot-charter.md        # PoC charter (Anniston, one process, two weeks)
│   ├── roadmap.md              # Four-phase plan: PoC → Expansion → Multi-site → Operationalize
│   ├── tooling.md              # Full solution vs PoC tool stacks
│   └── layers/                 # Detailed spec per training layer (5 docs)
└── poc/                        # Proof of Concept (in progress)
    ├── config.yaml             # PoC scope config
    ├── requirements.txt        # Python deps: lxml, PyYAML, anthropic, python-docx, Pillow
    ├── data/
    │   ├── tosca/              # Sample Tosca test scripts (XML)
    │   │   ├── purchase_requisition.xml   (22 steps, ME51N)
    │   │   └── goods_receipt.xml          (25 steps, MIGO)
    │   ├── bpmn/
    │   │   └── purchase_to_pay.xml        (BPMN 2.0, 5 roles, 7 tasks)
    │   └── opal_overlay.yaml              (Anniston site-specific variations)
    ├── parsers/                 # ✅ BUILT & TESTED
    │   ├── tosca_parser.py     # Tosca XML → structured steps, assertions, annotations
    │   └── bpmn_parser.py      # BPMN 2.0 XML → process graph with execution order
    ├── generators/             # 🔜 NEXT: AI content generation
    ├── prompts/                # 🔜 NEXT: LLM prompt templates
    ├── assembler/              # 🔜 NEXT: Opal overlay assembly
    └── output/                 # Generated training materials land here
```

## What's Built

**Documentation (complete):**
- Full concept doc, system architecture, PoC charter, 4-phase roadmap, tooling analysis, and detailed specs for all 5 training layers.

**PoC — Phase 1 (in progress):**

| Component | Status | Notes |
|---|---|---|
| Sample Tosca test scripts | ✅ Done | Realistic XML with SAP field refs, Anniston constraints, assertions |
| Sample BPMN process model | ✅ Done | Valid BPMN 2.0 with swimlanes, gateways, message flows |
| Opal overlay config | ✅ Done | YAML with 5 site-specific variations (field requirements, approval rules, process gates) |
| Tosca parser | ✅ Done | Extracts steps, actions, UI elements, site-specific flags. Handles namespaced and plain XML |
| BPMN parser | ✅ Done | Extracts tasks, gateways, events, builds execution-order traversal via BFS |
| AI content generators | 🔜 Next | Will use Claude API to transform parsed data into training content |
| Prompt templates | 🔜 Next | Structured prompts for walkthroughs, video scripts, job aids, WalkMe flows |
| Overlay assembler | 🔜 Next | Applies Anniston-specific variations to generated content |
| Pipeline orchestrator | 🔜 Next | `run.py` — single script that runs the full pipeline end-to-end |

## PoC Scope

- **Process:** Purchase Requisition → Goods Receipt
- **Role:** Purchasing Officer
- **Site:** Anniston Army Depot
- **Key Anniston constraints baked into sample data:**
  - Equipment code mandatory (enterprise default: optional)
  - Purchasing group restricted to 010/020
  - 3-tier approval for amounts > $50K (enterprise: 2-tier > $100K)
  - Storage location must match equipment assignment
  - Mandatory quality inspection for Class IX materials

## Tech Stack (PoC)

- Python 3.10+
- `lxml` — XML parsing for Tosca and BPMN
- `PyYAML` — Opal overlay config
- `anthropic` — Claude API for content generation (next step)
- `python-docx` — Formatted Word doc job aids (next step)

## Getting Started

```bash
cd poc/
pip install -r requirements.txt

# Test parsers
python parsers/tosca_parser.py data/tosca/purchase_requisition.xml
python parsers/bpmn_parser.py data/bpmn/purchase_to_pay.xml
```

## Key Docs to Read First

1. `docs/concept.md` — The "why" and the layered model
2. `docs/tooling.md` — What we're using and why
3. `poc/README.md` — How to run what's built so far
