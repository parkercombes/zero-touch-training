# Zero-Touch Training — Developer Summary

**Repo:** [github.com/parkercombes/zero-touch-training](https://github.com/parkercombes/zero-touch-training)

## What This Is

An AI pipeline that **generates ERP training materials from existing DevSecOps assets** — automated test scripts (Tosca), process models (Signavio/BPMN), and configuration data. No manual authoring. When the system changes, training updates automatically.

The tagline: *"We're not building training. We're compiling it from the same assets that already keep the system running."*

## Who It's For

Commercial retail distribution center ERP users (starting at GlobalMart Southeast Distribution Center). The system sits on top of SAP S/4HANA 2023, Fiori, and Appian, with site-specific process overlays.

## Six Training Layers

| Layer | Goal | Source | Output |
|---|---|---|---|
| 1. Navigation | "I'm not lost" | UI metadata + test scripts | Step-by-step walkthroughs |
| 2. Process | "I know where I fit" | BPMN process models | Explainer videos |
| 3. Execution | "I can do my job" | Tosca test scripts | Role-specific job aids |
| 4. In-App | "Help me while I'm doing it" | Test scripts + UI element IDs | WalkMe flow drafts |
| 5. Rationale | "I understand *why* we do it this way" | BPMN gateways + consequences.yaml | Process decision guides |
| 6. Updates | "Training is never outdated" | Change detection across all sources | Auto-regeneration triggers |

## Repo Structure

```
zero-touch-training/
├── README.md
├── DEVELOPER_SUMMARY.md         # This file
├── docs/
│   ├── concept.md               # Full project concept
│   ├── architecture.md          # System design, data flows, AI pipeline
│   ├── pilot-charter.md         # PoC charter (SE-DC, one process, two weeks)
│   ├── roadmap.md               # Four-phase plan: PoC → Expansion → Multi-site → Operationalize
│   ├── tooling.md               # Full solution vs PoC tool stacks
│   └── layers/                  # Detailed spec per training layer (6 docs)
└── poc/                         # Proof of Concept
    ├── config.yaml              # PoC scope config (company, site, role, sources)
    ├── requirements.txt         # Python deps: lxml, PyYAML, anthropic, python-docx, Pillow
    ├── run.py                   # Pipeline orchestrator — single entry point
    ├── .env.example             # API key template
    ├── data/
    │   ├── tosca/               # Sample Tosca test scripts (XML)
    │   │   ├── purchase_requisition.xml   (24 steps, ME51N)
    │   │   └── goods_receipt.xml          (28 steps, MIGO)
    │   ├── bpmn/
    │   │   └── purchase_to_pay.xml        (BPMN 2.0, 5 roles, 7 tasks)
    │   ├── opal_overlay.yaml              (SE-DC site-specific variations, 6 rules)
    │   └── consequences.yaml              (Layer 5: anti-patterns, consequences, compliance)
    ├── parsers/                  # ✅ BUILT & TESTED
    │   ├── tosca_parser.py      # Tosca XML → structured steps, assertions, annotations
    │   └── bpmn_parser.py       # BPMN 2.0 XML → process graph with execution order
    ├── generators/               # ✅ BUILT — AI content generation layer
    │   ├── base.py              # Shared: Claude API client, prompt rendering, output writing
    │   ├── walkthrough.py       # Layer 1: Tosca steps → navigation walkthroughs (Markdown)
    │   ├── video_script.py      # Layer 2: BPMN process → explainer video scripts (Markdown)
    │   ├── job_aid.py           # Layer 3: Tosca + BPMN → role-specific job aids (Markdown)
    │   ├── walkme_draft.py      # Layer 4: Tosca UI elements → WalkMe flow defs (JSON)
    │   ├── process_rationale.py # Layer 5: consequences.yaml + BPMN → decision guides (Markdown)
    │   ├── video_render_v2.py   # Social video: ffmpeg libflite TTS + xfade + numpy music
    │   └── video_render_bigfoot.py # Social video: DALL-E 3 + OpenAI TTS (run locally on Mac)
    ├── prompts/                  # ✅ BUILT — LLM prompt templates
    │   ├── walkthrough.txt      # Prompt: step-by-step navigation walkthrough
    │   ├── video_script.txt     # Prompt: process explainer video script
    │   ├── job_aid.txt          # Prompt: condensed desk-reference job aid
    │   ├── walkme.txt           # Prompt: WalkMe Smart Walk-Thru JSON definition
    │   └── process_rationale.txt # Prompt: process decision guide (Layer 5)
    ├── assembler/                # ✅ BUILT — Opal overlay assembly
    │   └── overlay.py           # Loads YAML overlays, resolves per-transaction constraints
    └── output/                   # Generated training materials land here
```

## What's Built

**Documentation (complete):**
- Full concept doc, system architecture, PoC charter, 4-phase roadmap, tooling analysis, and detailed specs for all 6 training layers.

**PoC — Full Pipeline:**

| Component | Status | Notes |
|---|---|---|
| Sample Tosca test scripts | ✅ Done | Realistic XML with SAP field refs, SE-DC constraints, assertions |
| Sample BPMN process model | ✅ Done | Valid BPMN 2.0 with swimlanes, gateways, message flows |
| Opal overlay config | ✅ Done | YAML with 6 site-specific variations (field constraints, approval rules, process gates, cold chain) |
| Consequences data | ✅ Done | `consequences.yaml` — anti-patterns, consequence mappings, compliance context for Layer 5 |
| Tosca parser | ✅ Done | Extracts steps, actions, UI elements, site-specific flags. Handles namespaced and plain XML |
| BPMN parser | ✅ Done | Extracts tasks, gateways, events, builds execution-order traversal via BFS |
| Prompt templates | ✅ Done | 5 structured prompt files (walkthroughs, video scripts, job aids, WalkMe flows, process rationale) |
| AI content generators | ✅ Done | 5 generator modules + base class with Claude API integration, retry logic, output writing |
| Overlay assembler | ✅ Done | Loads Opal YAML, resolves per-transaction constraints, provides to generators |
| Pipeline orchestrator | ✅ Done | `run.py` — single script: parse → overlay → generate → write. Supports `--dry-run`, `--layer` filtering |
| Social video (sandbox) | ✅ Done | `video_render_v2.py` — ffmpeg libflite TTS, xfade transitions, numpy music, 720×1280 |
| Social video (Bigfoot — Mark 1) | ✅ Done | `video_render_bigfoot.py` — Bigfoot vlog using DALL-E 3 still images + OpenAI TTS. 13 slides, ~$0.90/video. Tagged `cheapest-video-explainer-mark-1`. |
| Social video (Bigfoot — Veo 3)  | ✅ Done | `video_render_veo3.py` — Bigfoot vlog using Google Veo 3 real video clips + OpenAI TTS. 13 scenes, ~$41.60 (Standard) or ~$15.60 (Fast). Run locally on Mac. |

## Pipeline Architecture

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌───────────────┐
│  Source Data │ →  │   Parsers    │ →  │   Assembler   │ →  │  Generators   │
│             │    │              │    │               │    │               │
│ Tosca XML   │    │ tosca_parser │    │ overlay.py    │    │ walkthrough   │
│ BPMN XML    │    │ bpmn_parser  │    │ (Opal rules)  │    │ video_script  │
│ Opal YAML   │    │              │    │               │    │ job_aid       │
│             │    │              │    │               │    │ walkme_draft   │
└─────────────┘    └──────────────┘    └───────────────┘    └──────┬────────┘
                                                                    │
                                                          ┌─────────▼────────┐
                                                          │  Claude API      │
                                                          │  (content gen)   │
                                                          └─────────┬────────┘
                                                                    │
                                                          ┌─────────▼────────┐
                                                          │   output/        │
                                                          │  walkthroughs/   │
                                                          │  video_scripts/  │
                                                          │  job_aids/       │
                                                          │  walkme_flows/   │
                                                          └──────────────────┘
```

## How the Opal Overlay Pattern Works

Enterprise baseline + Site overlay + Role context = Delivered training

The overlay assembler loads `opal_overlay.yaml` which defines how SE-DC differs from GlobalMart enterprise standards. Generators inject these constraints into prompts so the AI produces site-accurate training — not generic docs.

Example: *Enterprise says "any purchasing group." SE-DC overlay says "R-SE or R-NAT only, because regional supplier programs." The walkthrough generator tells the user exactly which group to select and why.*

## PoC Scope

- **Process:** Purchase Requisition → Goods Receipt
- **Role:** Buyer
- **Site:** GlobalMart Southeast Distribution Center (Atlanta, GA)
- **Key SE-DC constraints baked into sample data:**
  - Lot/batch tracking mandatory for perishables (enterprise default: optional)
  - Purchasing group restricted to R-SE / R-NAT
  - 3-tier approval for amounts > $25K for perishable categories (enterprise: 2-tier > $50K)
  - Temperature zone must match product category (Zone-F/Zone-R/Zone-A)
  - Mandatory quality inspection for perishable and private-label goods
  - Cold chain verification with temperature recording at receiving dock

## Tech Stack (PoC)

- Python 3.10+
- `lxml` — XML parsing for Tosca and BPMN
- `PyYAML` — Opal overlay config
- `anthropic` — Claude API for content generation
- `python-docx` — Formatted Word doc job aids (future)
- `Pillow` — Image processing for screenshots (future)

## Getting Started

```bash
cd poc/

# Install dependencies
pip install -r requirements.txt

# Set up API key
cp .env.example .env
# Edit .env and add your Anthropic API key

# Dry run (parse + overlay, no AI calls)
python run.py --dry-run

# Full pipeline
python run.py

# Single layer only
python run.py --layer walkthrough
python run.py --layer video_script
python run.py --layer job_aid
python run.py --layer walkme
python run.py --layer process_rationale

# Social media video (sandbox — no external APIs)
python generators/video_render_v2.py

# Bigfoot vlog — Mark 1 (DALL-E 3 still images + TTS, ~$0.90, tagged cheapest-video-explainer-mark-1)
# Output: poc/output/bigfoot_goods_receipt_se-dc.mp4
OPENAI_API_KEY="sk-..." python generators/video_render_bigfoot.py

# Bigfoot vlog — Veo 3 (real video clips, ~$15.60 Fast / ~$41.60 Standard)
# Keys loaded automatically from poc/.env (GOOGLE_API_KEY + OPENAI_API_KEY)
# Output: poc/output/bigfoot_goods_receipt_veo3.mp4
# Install: pip install google-genai openai
python generators/video_render_veo3.py

# Test parsers directly
python parsers/tosca_parser.py data/tosca/purchase_requisition.xml
python parsers/bpmn_parser.py data/bpmn/purchase_to_pay.xml
```

## Key Docs to Read First

1. `docs/concept.md` — The "why" and the layered model
2. `docs/tooling.md` — What we're using and why
3. `poc/README.md` — How to run what's built so far
