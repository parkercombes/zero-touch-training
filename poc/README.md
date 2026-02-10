# Zero-Touch Training — Proof of Concept

## Overview

This PoC demonstrates that AI can generate accurate, usable ERP training materials from existing DevSecOps assets (test scripts, process models, configuration data).

## Scope

- **Process:** Purchase Requisition → Goods Receipt
- **Role:** Purchasing Officer
- **Site:** Anniston Army Depot
- **Layers:** Navigation walkthrough, process explainer video script, role-specific job aids, WalkMe flow draft

## Setup

```bash
cd poc/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your Anthropic API key
```

## Run

```bash
python run.py
```

Outputs are written to `output/`.

## Project Structure

```
poc/
├── config.yaml            # PoC configuration
├── data/
│   ├── tosca/             # Sample Tosca test scripts (XML)
│   ├── bpmn/              # Sample BPMN process model (XML)
│   └── opal_overlay.yaml  # Anniston site overlay
├── parsers/
│   ├── tosca_parser.py    # Parse Tosca XML → structured steps
│   └── bpmn_parser.py     # Parse BPMN XML → process graph
├── generators/
│   ├── walkthrough.py     # Layer 1: Navigation walkthroughs
│   ├── video_script.py    # Layer 2: Process explainer scripts
│   ├── job_aid.py         # Layer 3: Role-specific job aids
│   └── walkme_draft.py    # Layer 4: WalkMe flow definitions
├── prompts/               # LLM prompt templates
├── assembler/
│   └── overlay.py         # Apply Opal site overlay
├── output/                # Generated training materials
└── run.py                 # Pipeline entry point
```
