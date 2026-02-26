# Zero-Touch Training — Developer Summary

**Repo:** [github.com/parkercombes/zero-touch-training](https://github.com/parkercombes/zero-touch-training)

## What This Is

An AI pipeline that **generates ERP training materials from existing DevSecOps assets** — automated test scripts (Tosca), process models (Signavio/BPMN), and configuration data. No manual authoring. When the system changes, training updates automatically.

The tagline: *"We're not building training. We're compiling it from the same assets that already keep the system running."*

## Who It's For

Commercial retail distribution center ERP users (starting at GlobalMart Southeast Distribution Center). The system sits on top of SAP S/4HANA 2023, Fiori, and Appian, with site-specific process overlays.

A near-term target use case is **Anniston Army Depot** — Army supply clerks working with Classes of Supply (I–IX) that map directly to the five handling profiles already built into the UI trainer.

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
│   ├── concept.md               # Full project concept + game-inspired training vision
│   ├── architecture.md          # System design, data flows, AI pipeline, video + UI trainer
│   ├── game-design-vision.md    # Game mechanics framework, real-world examples, Anniston use case
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
    │   ├── video_render_bigfoot.py  # Social video Mark 1: DALL-E 3 stills + OpenAI TTS
    │   ├── video_render_veo3.py     # Social video Mark 2: Veo 3 real video + native audio
    │   ├── video_render_veo3_poc.py # 3-scene POC cut (intro + 101 lesson + outro)
    │   ├── veo3_test_clip.py        # Single-clip validator — downloads raw Veo output
    │   ├── ui_trainer.py            # Interactive SAP UI trainer (HTML, scenario-pack-driven)
    │   └── scenarios/               # Scenario packs for the UI trainer
    │       ├── __init__.py
    │       ├── base.py              # Shared Pillow drawing helpers (SAP Fiori chrome)
    │       ├── sedc_goods_receipt.py  # SE-DC perishable goods receipt (original scenario)
    │       ├── standard_dry.py        # Apex Auto Parts DC — basic dry goods
    │       ├── regulated_pharma.py    # Cardinal Health DC — pharmaceutical/GxP
    │       ├── hazmat.py              # ChemCo Industrial DC — hazardous materials
    │       └── serialized.py          # TechVault DC — serialized/high-value assets
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
- Full concept doc, system architecture, PoC charter, 4-phase roadmap, tooling analysis, detailed specs for all 6 training layers, and game design vision.

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
| Social video (Bigfoot — Mark 1) | ✅ Done | `video_render_bigfoot.py` — DALL-E 3 stills + OpenAI TTS. 13 slides, ~$0.90/video. Tagged `cheapest-video-explainer-mark-1`. |
| Social video (Bigfoot — Veo 3)  | ✅ Done | `video_render_veo3.py` — Veo 3 real video + **native lip-synced audio**. 4-character cast. ~$15.60 Fast / ~$41.60 Standard. |
| Bigfoot POC cut | ✅ Done | `video_render_veo3_poc.py` — 3 scenes (intro/101/outro), ~$3.60, daily-quota-safe |
| UI trainer — generic engine | ✅ Done | `ui_trainer.py` — scenario-pack-driven SAP Fiori simulation. Loads any scenario module. |
| UI trainer — SE-DC scenario | ✅ Done | `sedc_goods_receipt.py` — perishable goods receipt, 13 screens, cold chain, lot tracking |
| UI trainer — 4 additional scenarios | ✅ Done | standard_dry, regulated_pharma, hazmat, serialized |

## The Bigfoot Character Cast

`video_render_veo3.py` uses a cast of four named Bigfoot employees to make different domain areas visually distinct. Each character is embedded in every relevant video prompt to guide Veo toward visual consistency.

| Character | Fur | Vest | Domain |
|---|---|---|---|
| **Dave** | Dark reddish-brown | Orange (GLOBALMART SE-DC) | Intro, document entry, vendor data, line items, posting, follow-up, outro |
| **Sandra** | Silver-grey | Red (COMPLIANCE) | Delivery verification, movement type, discrepancy reporting |
| **Keisha** | Auburn reddish | White (QUALITY ASSURANCE) | QA inspection, batch tracking |
| **Marcus** | Jet-black | Yellow (RECEIVING) + blue hard hat | Temperature zone / cold chain |

The 3-scene POC features Dave (intro), Sandra (movement type 101), and Marcus (outro).

## Video Pipeline: Native Audio Architecture

**Mark 1** (video_render_bigfoot.py): DALL-E 3 generates still images → OpenAI TTS generates voiceover → ffmpeg combines them. No lip sync possible.

**Mark 2** (video_render_veo3.py): Google Veo 3 generates video **and** audio together from a single prompt. Dialogue embedded in the video prompt produces natural lip movement and voice in sync. No separate TTS step.

Key implementation detail in `compose_scene()`:
```python
"-map", "0:v",
"-map", "0:a?",   # preserve Veo's native lip-synced audio
                   # (? = skip gracefully if clip has no audio track)
```

The earlier (broken) version used `-map 1:a` to overlay OpenAI TTS, discarding Veo's generated audio entirely. The `veo3_test_clip.py` validator never applied this transform, which is why the test clip sounded correct while the full pipeline didn't.

## UI Trainer Scenario Pack Architecture

`ui_trainer.py` is a generic HTML simulation engine. All warehouse-specific content lives in a separate scenario module.

**Each scenario module exports:**
- `SCENARIO` dict — metadata (id, title, site, process, handling_profile, num_screens)
- `SCREEN_GENERATORS` dict — maps screen names to generator functions
- `generate_screens(out_dir)` — calls all generators, writes PNGs to output dir

**Handling profiles built:**

| Profile | Example Site | Key Regulatory Layer |
|---|---|---|
| `perishable` | GlobalMart SE-DC | Cold chain, lot/batch, QI |
| `standard_dry` | Apex Auto Parts DC | None |
| `regulated_pharma` | Cardinal Health DC | GxP, lot + expiry + CoA, QI |
| `hazmat` | ChemCo Industrial DC | DOT/OSHA, UN number, hazmat class |
| `serialized` | TechVault DC | Serial scan, CAGE-01, manager approval |

Adding a new scenario: copy any existing scenario file, update the `SCENARIO` dict and screen generator functions, then run `python3 ui_trainer.py scenarios.your_new_scenario`.

## Getting Started

```bash
cd poc/

# Install dependencies
pip install -r requirements.txt
pip install google-genai openai pillow  # for video + UI trainer

# Set up API keys
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY

# Dry run (parse + overlay, no AI calls)
python run.py --dry-run

# Full training pipeline
python run.py

# Social video — sandbox (no external APIs)
python generators/video_render_v2.py

# Social video — Mark 1 (DALL-E 3 stills + TTS, ~$0.90)
python generators/video_render_bigfoot.py

# Social video — Mark 2, full 13-scene (Veo 3 native audio, ~$15.60)
# Requires Tier 2 Google AI Studio API or own GCP billing
python generators/video_render_veo3.py

# Social video — 3-scene POC cut (~$3.60, daily-quota-safe)
python generators/video_render_veo3_poc.py

# Validate a single Veo clip (download raw, no audio stripping)
python generators/veo3_test_clip.py

# UI trainer — SE-DC perishable scenario (default)
python generators/ui_trainer.py

# UI trainer — alternate scenario packs
python generators/ui_trainer.py scenarios.standard_dry
python generators/ui_trainer.py scenarios.regulated_pharma
python generators/ui_trainer.py scenarios.hazmat
python generators/ui_trainer.py scenarios.serialized

# Test parsers
python parsers/tosca_parser.py data/tosca/purchase_requisition.xml
python parsers/bpmn_parser.py data/bpmn/purchase_to_pay.xml
```

## Key Docs to Read First

1. `docs/concept.md` — The "why", the layered model, and game-inspired training vision
2. `docs/game-design-vision.md` — Game mechanics framework, real-world examples, planned enhancements
3. `docs/architecture.md` — Full system design including video pipeline and UI trainer
4. `docs/tooling.md` — What we're using and why
