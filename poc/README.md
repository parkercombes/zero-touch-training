# Zero-Touch Training — Proof of Concept

## Overview

This PoC demonstrates that AI can generate accurate, usable training materials from existing DevSecOps assets (test scripts, process models, configuration data) — and that a game-inspired interactive trainer can be built on top of the same source.

The PoC now covers two training domains: **software** (SAP MIGO Goods Receipt across 5 handling profiles) and **hardware** (AR-15 field strip pilot), both driven by the same React game engine.

## Scope

**AI content pipeline:**
- **Process:** Purchase Requisition → Goods Receipt
- **Role:** Buyer
- **Site:** GlobalMart Southeast Distribution Center (Atlanta, GA)
- **Layers:** Navigation walkthrough, process explainer video script, role-specific job aids, WalkMe flow draft, process rationale

**Interactive UI trainer:**
- 5 SAP software scenarios (standard dry, perishable, pharma, hazmat, serialized)
- 2 hardware scenarios (AR-15 field strip, F-150 shift lever & seal service)
- React game engine with 4-level progression, consequence feedback, timer, confetti, narrative premises, decoy fields, debrief, review mode
- Auto-generated scenario selector with domain grouping

**Social media videos:**
- Sandbox renderer (ffmpeg + libflite, free)
- Mark 1 (DALL-E 3 + OpenAI TTS, ~$0.90)
- Mark 2 (Google Veo 3 native lip-synced audio, ~$3.60–$15.60)

## Setup

```bash
cd poc/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pillow                    # for UI trainer screen generation
pip install google-genai openai       # for video pipeline (optional)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY (and optionally GOOGLE_API_KEY, OPENAI_API_KEY)
```

## Run

```bash
# Full AI content pipeline (Layers 1–5)
python run.py

# Dry run (parse + overlay, no AI calls)
python run.py --dry-run

# UI trainer — generate a scenario
python generators/ui_trainer.py                              # SE-DC perishable (default)
python generators/ui_trainer.py scenarios.standard_dry       # software
python generators/ui_trainer.py scenarios.regulated_pharma   # software
python generators/ui_trainer.py scenarios.hazmat             # software
python generators/ui_trainer.py scenarios.serialized         # software
python generators/ui_trainer.py scenarios.ar15_field_strip   # hardware

# Regenerate scenario selector after adding/removing scenarios
python generators/generate_index.py

# Social video — sandbox (no external APIs)
python generators/video_render_v2.py

# Social video — Mark 1 (DALL-E 3 + TTS, ~$0.90)
python generators/video_render_bigfoot.py

# Social video — Mark 2 (Veo 3, ~$3.60 POC / ~$15.60 full)
python generators/video_render_veo3_poc.py
python generators/video_render_veo3.py
```

Outputs are written to `output/`. Open `output/ui_trainer/index.html` in any browser to access the scenario selector.

## Project Structure

```
poc/
├── config.yaml              # PoC configuration
├── requirements.txt         # Python deps
├── run.py                   # AI content pipeline entry point
├── data/
│   ├── tosca/               # Sample Tosca test scripts (XML)
│   ├── bpmn/                # Sample BPMN process model (XML)
│   ├── opal_overlay.yaml    # SE-DC site overlay
│   └── consequences.yaml    # Layer 5: anti-patterns + consequences
├── parsers/
│   ├── tosca_parser.py      # Parse Tosca XML → structured steps
│   └── bpmn_parser.py       # Parse BPMN XML → process graph
├── generators/
│   ├── base.py              # Claude API client, prompt rendering
│   ├── walkthrough.py       # Layer 1: Navigation walkthroughs
│   ├── video_script.py      # Layer 2: Process explainer scripts
│   ├── job_aid.py           # Layer 3: Role-specific job aids
│   ├── walkme_draft.py      # Layer 4: WalkMe flow definitions
│   ├── process_rationale.py # Layer 5: Decision guides
│   ├── video_render_v2.py       # Social video: sandbox
│   ├── video_render_bigfoot.py  # Social video: DALL-E 3 + TTS
│   ├── video_render_veo3.py     # Social video: Veo 3 full
│   ├── video_render_veo3_poc.py # Social video: Veo 3 POC cut
│   ├── veo3_test_clip.py        # Single-clip validator
│   ├── ui_trainer.py            # Interactive trainer build script
│   ├── trainer_app.jsx          # React game engine (~1630 lines)
│   ├── generate_index.py        # Auto-generates scenario selector
│   └── scenarios/
│       ├── base.py              # Software: SAP Fiori drawing + SAP_BRANDING
│       ├── base_hardware.py     # Hardware: photo annotation + HARDWARE_BRANDING
│       ├── sedc_goods_receipt.py # Perishable / cold chain
│       ├── standard_dry.py      # Basic dry goods
│       ├── regulated_pharma.py  # Pharmaceutical / GxP
│       ├── hazmat.py            # Hazardous materials
│       ├── serialized.py        # High-value serialized assets
│       ├── ar15_field_strip.py  # AR-15 field strip (hardware)
│       └── f150_trans_service.py # F-150 shift lever & seal (hardware)
├── prompts/                 # LLM prompt templates (5 files)
├── assembler/
│   └── overlay.py           # Apply Opal site overlay
└── output/                  # Generated training materials
    ├── walkthroughs/        # Layer 1 output
    ├── video_scripts/       # Layer 2 output
    ├── job_aids/            # Layer 3 output
    ├── walkme_flows/        # Layer 4 output
    └── ui_trainer/          # Interactive trainers
        ├── index.html       # Auto-generated scenario selector
        ├── standard_dry_gr/ # Software trainer
        ├── sedc_goods_receipt/ # Software trainer
        ├── pharma_gr/       # Software trainer
        ├── hazmat_gr/       # Software trainer
        ├── serialized_gr/   # Software trainer
        └── ar15_field_strip/ # Hardware trainer
```
