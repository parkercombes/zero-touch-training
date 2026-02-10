# Zero-Touch Training — Tooling

## Full Solution

The production pipeline requires tooling across six functional areas.

### Source Ingestion

| Tool | Purpose | Notes |
|---|---|---|
| **Tosca API / XML Export** | Extract test scripts, screenshots, step-level execution data | Primary source of execution truth |
| **Signavio REST API** | Pull BPMN 2.0 process models, role definitions, org structures | Process and semantic truth |
| **SAP OData / RFC** | Read Fiori app catalog, transaction codes, config tables, PFCG roles | UI metadata + configuration |
| **Appian REST API** | Pull interface definitions, field metadata | Additional UI layer |

### AI Content Generation

| Tool | Purpose | Notes |
|---|---|---|
| **Claude API (Anthropic)** | Core LLM — transforms technical assets into training content | Script-to-job-aid, BPMN-to-video-script, step-to-walkthrough |
| **Prompt template library** | Structured prompts per content type | Version-controlled, iterable |
| **Embedding model** | Semantic search across source assets for context assembly | For linking related content across layers |

### Video Production

| Tool | Purpose | Notes |
|---|---|---|
| **Synthesia / HeyGen** | AI avatar narration of process explainer videos | Bigfoot-style: script in, video out |
| **ElevenLabs / Play.ht** | AI voiceover generation | Alternative to avatar — voiceover + screen recording |
| **FFmpeg** | Video assembly, editing, format conversion | Glue layer for automated video pipeline |

### Document & Asset Generation

| Tool | Purpose | Notes |
|---|---|---|
| **python-docx** | Generate formatted Word job aids | Templated output with screenshots |
| **ReportLab / WeasyPrint** | Generate PDF walkthroughs | For printable/distributable guides |
| **Pillow / OpenCV** | Screenshot annotation — arrows, highlights, callouts | Automated visual markup |
| **Mermaid / D3.js** | Generate process flow diagrams | Embedded in docs and videos |

### Pipeline Orchestration

| Tool | Purpose | Notes |
|---|---|---|
| **Apache Airflow / Prefect** | Workflow orchestration — ingest → generate → validate → publish | DAG-based, observable, retriggerable |
| **PostgreSQL** | Content registry — maps training to source assets, tracks staleness | Relational model for dependency tracking |
| **Git** | Version control for all text-based outputs | Training-as-Code |
| **S3 / Azure Blob** | Blob storage for video, screenshots, large assets | Versioned object storage |

### Change Detection & Delivery

| Tool | Purpose | Notes |
|---|---|---|
| **Tosca webhooks / polling** | Detect test script changes and regression failures | Primary change trigger |
| **SAP TMS monitor** | Detect configuration transports | Config change trigger |
| **Pixelmatch / ML-based diffing** | UI screenshot comparison across releases | Visual change detection |
| **WalkMe API** | Publish in-app guidance flows | Delivery surface for Layer 4 |
| **LMS API (SCORM)** | Publish courses and track completion | Delivery surface for Layers 1-3 |

### Infrastructure

| Tool | Purpose | Notes |
|---|---|---|
| **Docker / Kubernetes** | Containerized pipeline services | Portable, scalable |
| **Grafana / Prometheus** | Monitoring, alerting, staleness dashboards | Operational visibility |
| **HashiCorp Vault** | Secrets management for API keys, RFC credentials | Enterprise security |

---

## Proof of Concept (PoC)

The PoC strips the tooling down to the minimum needed to prove one thing: **AI can generate accurate, usable training from existing DevSecOps assets.**

No production infrastructure. No enterprise integrations. Just the core transformation.

### Scope

- One process: Purchase Requisition → Goods Receipt
- One role: Purchasing Officer
- One site: Anniston
- Inputs: Sample Tosca test script (XML) + sample BPMN process model
- Outputs: Navigation walkthrough, process explainer video script, role-specific job aids

### PoC Tool Stack

| Tool | Purpose | Why this, why now |
|---|---|---|
| **Python 3.11+** | Pipeline glue — parsing, orchestration, output generation | Universal, fast to build, no infrastructure needed |
| **Claude API (Anthropic)** | LLM for content generation | Best reasoning for technical-to-plain-English transformation |
| **python-docx** | Generate formatted job aids as Word docs | Professional output with minimal code |
| **Markdown** | Walkthrough and video script output | Lightweight, version-controllable, easy to review |
| **Pillow** | Basic screenshot annotation | Arrows, boxes, highlights on Tosca screenshots |
| **Git / GitHub** | Version control and collaboration | Already set up |

### What's Intentionally Left Out of PoC

| Full Solution Component | PoC Approach |
|---|---|
| Airflow orchestration | Single Python script runs the pipeline end-to-end |
| Real Tosca/Signavio API integration | Sample XML files that mirror real format |
| Video rendering (Synthesia/HeyGen) | AI-generated video script + storyboard (text output) |
| WalkMe integration | WalkMe flow definition as JSON (not deployed) |
| Change detection | Manual re-run; demonstrate that re-running with modified input produces updated output |
| Database / content registry | File-based — outputs stored in `output/` directory |
| Enterprise auth / secrets management | API key in `.env` file (gitignored) |
| Screenshot annotation pipeline | Manual screenshots or placeholders in PoC |

### PoC Directory Structure

```
zero-touch-training/
├── README.md
├── docs/                      # Project documentation
├── poc/
│   ├── README.md              # PoC setup and run instructions
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # API key template
│   ├── config.yaml            # PoC configuration (process, role, site)
│   ├── data/
│   │   ├── tosca/             # Sample Tosca test scripts (XML)
│   │   └── bpmn/              # Sample BPMN process models (XML)
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── tosca_parser.py    # Parse Tosca XML → structured steps
│   │   └── bpmn_parser.py     # Parse BPMN XML → process graph
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── walkthrough.py     # Generate Layer 1 navigation walkthroughs
│   │   ├── video_script.py    # Generate Layer 2 process explainer scripts
│   │   ├── job_aid.py         # Generate Layer 3 role-specific job aids
│   │   └── walkme_draft.py    # Generate Layer 4 WalkMe flow definitions
│   ├── prompts/
│   │   ├── walkthrough.txt    # Prompt template for walkthroughs
│   │   ├── video_script.txt   # Prompt template for video scripts
│   │   ├── job_aid.txt        # Prompt template for job aids
│   │   └── walkme.txt         # Prompt template for WalkMe flows
│   ├── assembler/
│   │   ├── __init__.py
│   │   └── overlay.py         # Apply Opal site overlay to generated content
│   ├── output/                # Generated training materials land here
│   │   └── .gitkeep
│   └── run.py                 # Main pipeline entry point
└── templates/
    └── job_aid_template.docx  # Word template for formatted job aids
```

### PoC Success Criteria

1. **Parsers work** — Tosca XML and BPMN XML are correctly parsed into structured data
2. **AI generates usable content** — Job aids, walkthroughs, and video scripts are coherent, accurate, and match the source data
3. **Overlay applies cleanly** — Anniston-specific variations appear correctly in output
4. **Re-run produces updated output** — Modify a test script input, re-run, and the output reflects the change
5. **An SME would approve it** — Generated content is close enough to "production ready" that a subject matter expert would sign off with minor edits
