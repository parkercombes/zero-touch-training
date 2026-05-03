# Zero-Touch Training — Developer Summary

**Repo:** [github.com/parkercombes/zero-touch-training](https://github.com/parkercombes/zero-touch-training)

## What This Is

An AI pipeline that **generates training materials from existing DevSecOps assets** — automated test scripts (Tosca), process models (Signavio/BPMN), and configuration data. No manual authoring. When the system changes, training updates automatically.

The platform supports two training domains: **software** (ERP workflows like SAP MIGO Goods Receipt) and **hardware** (equipment maintenance and assembly). Both share the same React game engine and four-level progression system — only the screen generation layer and visual branding differ.

The tagline: *"We're not building training. We're compiling it from the same assets that already keep the system running."*

## Who It's For

Commercial retail distribution center ERP users (starting at GlobalMart Southeast Distribution Center). The system sits on top of SAP S/4HANA 2023, Fiori, and Appian, with site-specific process overlays.

A near-term target use case is **Anniston Army Depot** — Army supply clerks working with Classes of Supply (I–IX) that map directly to the five handling profiles already built into the UI trainer.

Hardware training extends the platform to physical procedures (weapon maintenance, automotive service, industrial equipment) where the same four-level progression — explore, follow along, do it yourself, timed challenge — builds procedural muscle memory through repetition and consequence-based feedback.

## Six Training Layers

| Layer | Goal | Source | Output | Status |
|---|---|---|---|---|
| 1. Navigation | "I'm not lost" | UI metadata + test scripts | Step-by-step walkthroughs | ✅ Built |
| 2. Process | "I know where I fit" | BPMN process models | Explainer videos | ✅ Built |
| 3. Execution | "I can do my job" | Tosca test scripts | Role-specific job aids | ✅ Built |
| 4. In-App | "Help me while I'm doing it" | Test scripts + UI element IDs | WalkMe flow drafts | ✅ Built |
| 5. Rationale | "I understand *why* we do it this way" | BPMN gateways + consequences.yaml | Process decision guides | ✅ Built |
| 6. Updates | "Training is never outdated" | Change detection across all sources | Auto-regeneration triggers | 🔨 Phase 2 — in progress |

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
    │   ├── ui_trainer.py            # Interactive UI trainer (HTML + React, scenario-pack-driven)
    │   ├── generate_index.py        # Auto-generates scenario selector index.html from scenario metadata
    │   ├── trainer_app.jsx          # React game engine (~1,645 lines) — domain-agnostic, branding-injected
    │   └── scenarios/               # Scenario packs for the UI trainer
    │       ├── __init__.py
    │       ├── base.py              # Shared Pillow drawing helpers (SAP Fiori chrome) + SAP_BRANDING
    │       ├── base_hardware.py     # Hardware domain: photo annotation helpers + HARDWARE_BRANDING
    │       ├── sedc_goods_receipt.py  # SE-DC perishable goods receipt (original scenario)
    │       ├── standard_dry.py        # Apex Auto Parts DC — basic dry goods
    │       ├── regulated_pharma.py    # Cardinal Health DC — pharmaceutical/GxP
    │       ├── hazmat.py              # ChemCo Industrial DC — hazardous materials
    │       ├── serialized.py          # TechVault DC — serialized/high-value assets
    │       ├── ar15_field_strip.py    # AR-15 field strip (hardware domain pilot)
    │       └── f150_trans_service.py # F-150 shift lever & seal service (hardware domain)
    ├── capture/                  # ✅ BUILT — Playwright screen capture pipeline
    │   ├── capture_gr.py        # ERPNext Goods Receipt capture script (517 lines)
    │   └── capture_config.yaml  # Navigation path and screenshot config for ERPNext GR
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
| UI trainer — React game engine | ✅ Done | `trainer_app.jsx` — domain-agnostic React SPA with useReducer state machine, 4-level progression, branding injection, audio, confetti, debrief, review mode |
| UI trainer — branding abstraction | ✅ Done | SAP_BRANDING / HARDWARE_BRANDING dicts injected via SCENARIO.branding; hexToRgb() derives all rgba tints at runtime |
| UI trainer — SE-DC scenario | ✅ Done | `sedc_goods_receipt.py` — perishable goods receipt, 13 screens, cold chain, lot tracking |
| UI trainer — 4 additional SAP scenarios | ✅ Done | standard_dry, regulated_pharma, hazmat, serialized |
| UI trainer — hardware base module | ✅ Done | `base_hardware.py` — photo annotation helpers, placeholder generation, HARDWARE_BRANDING |
| UI trainer — AR-15 pilot scenario | ✅ Done | `ar15_field_strip.py` — 8-step field strip, placeholder diagrams, safety-first progression |
| UI trainer — F-150 scenario | ✅ Done | `f150_trans_service.py` — 7-step shift lever & seal service, real manual photos, automotive maintenance |
| UI trainer — drone pre-flight (HW/SW fusion) | ✅ Done | `drone_preflight.py` — 6-step alternating hardware-photo/software-app scenario; proves engine handles fusion with zero code changes (`training_domain: "fusion"`) |
| Scenario selector generator | ✅ Done | `generate_index.py` — auto-discovers scenarios, groups by domain (software/hardware), generates index.html |
| ERPNext capture pipeline | ✅ Done | `capture/capture_gr.py` — Playwright-based screen capture from live ERPNext, replaces drawn screens for standard_dry_gr |
| Drift detection (Layer 6) | ✅ Done | `detect_changes.py` — snapshot/check/status CLI; diffs parsed Tosca/BPMN/overlay against committed baselines, maps changes to affected scenarios via `scenario_deps.yaml`, emits JSON + Markdown reports with step-level before/after values, exits 1 for CI gating |
| CI integration reference | ✅ Done | `ci_examples/training-drift.yml` — sample GitHub Actions workflow showing PR commenting, scheduled scans, and optional auto-regenerate stub |
| Video character cast parameterization | ✅ Done | `video_casts.py` — Cast dataclass + CAST_BIGFOOT + CAST_HUMAN + shared 13-scene template; `video_render_veo3.py --cast {bigfoot,human}` and `video_render_veo3_poc.py --cast {bigfoot,human}`; both casts validated end-to-end on Veo 3 |

## The Character Casts

`video_render_veo3.py` supports two character casts of equivalent structure (Dave, Sandra, Marcus, Keisha — receiving lead, compliance, cold chain, QA), interchangeable via the `--cast` flag. Same scenes, same dialogue, same code path; different characters. The architecture is in `video_casts.py`: a shared 13-scene template with species-specific phrasing abstracted into per-cast tokens.

**Bigfoot Cast** (`--cast bigfoot`, default) — the memorable demo cast:

| Character | Fur | Vest | Domain |
|---|---|---|---|
| **Dave** | Dark reddish-brown | Orange (GLOBALMART SE-DC) | Intro, document entry, vendor data, line items, posting, follow-up, outro |
| **Sandra** | Silver-grey | Red (COMPLIANCE) | Delivery verification, movement type, discrepancy reporting |
| **Keisha** | Auburn reddish | White (QUALITY ASSURANCE) | QA inspection, batch tracking |
| **Marcus** | Jet-black | Yellow (RECEIVING) + blue hard hat | Temperature zone / cold chain |

**Human Cast** (`--cast human`) — the photorealistic warehouse worker cast for stakeholders who balk at the Bigfoot framing:

| Character | Description | Vest | Domain |
|---|---|---|---|
| **Dave** | 40-year-old man, short brown beard, broad-shouldered | Orange (GLOBALMART SE-DC) | Same as bigfoot Dave |
| **Sandra** | 45-year-old woman, grey-streaked hair, low ponytail | Red (COMPLIANCE) | Same as bigfoot Sandra |
| **Keisha** | Black woman, early 30s, locs pulled back | White (QUALITY ASSURANCE) | Same as bigfoot Keisha |
| **Marcus** | Black man, late 30s, close-cropped beard | Yellow (RECEIVING) + blue hard hat | Same as bigfoot Marcus |

Adding a third cast (e.g. military, healthcare, multilingual) is a single new `Cast(...)` block in `video_casts.py`. The scene template doesn't change.

The 3-scene POC features Dave (intro), Sandra (movement type 101), and Dave again (outro) — same structure across both casts.

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

## UI Trainer Architecture

### React Game Engine

The interactive trainer is a React single-page application (`trainer_app.jsx`, ~1,645 lines). A `useReducer` state machine drives all four progression levels plus review mode. The engine is completely domain-agnostic — it reads scenario metadata, screen images, and branding from JSON globals injected at build time.

### Multi-Domain Branding

Each scenario carries a `branding` dict that controls the visual identity:

| Property | SAP Software | Hardware |
|---|---|---|
| Shell color | `#033D80` (Fiori blue) | `#3C3C3C` (steel grey) |
| Accent color | `#E87600` (amber) | `#FF8C00` (safety orange) |
| Level names | Explore / Guided / On Your Own / Challenge | OBSERVE / FOLLOW ALONG / DO IT / SPEED RUN |

The JSX resolves branding at runtime via `SCENARIO.branding || {}` with SAP defaults as fallback. A `hexToRgb()` helper derives all rgba tints from the hex primaries, so the branding dict stays small (~6 keys) while covering 47+ color references throughout the UI.

### Scenario Pack Pattern

`ui_trainer.py` is the build script. It loads a scenario module dynamically, calls `generate_screens()` to render PNGs (highlighted for Levels 0–1, neutral with decoys for Levels 2–3), reads the JSX, injects three JSON blobs (scenario data, highlighted screen paths, neutral screen paths) plus the JSX source into a single HTML wrapper.

**Each scenario module exports:**
- `SCENARIO` dict — metadata (id, title, site, role, training_domain, branding, handling_profile, tutorial, mission)
- `SCREEN_GENERATORS` dict — maps screen names to generator functions
- `generate_screens(out_dir)` — calls all generators, writes PNGs (highlighted + neutral variants)

### Scenario Packs

**Software domain (SAP MIGO):**

| Profile | Scenario File | Site | Key Regulatory Layer |
|---|---|---|---|
| `perishable` | sedc_goods_receipt.py | GlobalMart SE-DC | Cold chain, lot/batch, QI |
| `standard_dry` | standard_dry.py | Apex Auto Parts DC | None |
| `regulated_pharma` | regulated_pharma.py | Cardinal Health DC | GxP, lot + expiry + CoA, QI |
| `hazmat` | hazmat.py | ChemCo Industrial DC | DOT/OSHA, UN number, hazmat class |
| `serialized` | serialized.py | TechVault DC | Serial scan, CAGE-01, manager approval |

**Hardware domain:**

| Scenario | Scenario File | Site | Key Focus |
|---|---|---|---|
| AR-15 Field Strip | ar15_field_strip.py | Range Safety Training Center | 8-step field strip, safety verification, component inspection |
| F-150 Shift Lever & Seal Service | f150_trans_service.py | Home Garage / Field Maintenance | 7-step transmission service, real manual photos, torque specs |

### Adding a New Scenario

**Software:** Copy any existing SAP scenario file, update the `SCENARIO` dict and screen generators, then run `python3 ui_trainer.py scenarios.your_new_scenario`.

**Hardware:** Copy `ar15_field_strip.py`, import from `base_hardware` instead of `base`, update steps/screens for the new equipment, run the same command. When real photographs are available, swap them in for the Pillow-drawn placeholders — hotspot coordinates just need to match.

### Scenario Selector

`generate_index.py` auto-discovers all scenario modules, reads their SCENARIO metadata, groups them by `training_domain`, and generates `output/ui_trainer/index.html` with domain sections (Software Training / Hardware Training), profile-colored cards, and inferred tags.

## Scenario Authoring Contract

Every scenario module is a contract with the React engine in `trainer_app.jsx`. There is no schema validator yet (Phase 2 work — see What's Next), so author scenarios by reading this section before copy-pasting from another module. The drone scenario's May 2026 black-screen incident was caused by a missing `mission` dict; that bug is preventable by understanding what the engine reads.

### Required SCENARIO fields (top level)

The engine reads these directly from `SCENARIO`:

| Field | Type | Used for |
|---|---|---|
| `id` | str | Output directory name, scenario ID throughout |
| `title` | str | Header banners, page title, win-screen messages |
| `site` | str | Header subtitle |
| `role` | str | Footer subtitle |
| `training_domain` | str | `"software"`, `"hardware"`, or `"fusion"`; gates `IS_HARDWARE` flag and index domain section |
| `branding` | dict | Color tokens, level names, level descriptions (see SAP_BRANDING / HARDWARE_BRANDING) |
| `tutorial` | list[dict] | Ordered step list (see step contract below) |
| `mission` | dict | Per-level briefings, time limit, narratives, learning objectives |
| `handling_profile` | str or None | Optional; profile-specific tags in the index |
| `exploded_view` | dict or None | Optional; Three.js exploded-view data for hardware scenarios |

### Required `mission` sub-fields

Engine reads these from `SCENARIO.mission`. Missing any of these breaks level entry.

| Field | Type | Used for |
|---|---|---|
| `title` | str | Mission card title |
| `briefing` | str | Pre-play briefing text |
| `time_limit` | int | Seconds, used as countdown for Level 3 |
| `narratives` | list[str] | Rotating premise cards shown before Level 3 (prevent memorization gaming) |
| `learning_objectives` | dict[int, list[str]] | Per-level objectives (keys 0/1/2/3); shown on briefing screen |
| `par_clicks` | int | Optional metadata, not currently rendered |

### Required per-step fields (each item in `tutorial`)

| Field | Type | Used for |
|---|---|---|
| `screen` | str | PNG filename in `screens/` and `screens_neutral/` |
| `goal` | str | Step title shown to learner |
| `instruction` | str | Detailed instruction at Level 1 |
| `hint` | str | Adaptive hint after 3 wrong clicks |
| `hotspot` | dict | `{x, y, w, h}` — correct click region |
| `feedback` | str | Success message on correct click |
| `consequence` | str | Layer 5 rationale shown on wrong click and in debrief |
| `explore_info` | list[str] | Bullet list shown at Level 0 EXPLORE |

### Required scenario-level functions

Each scenario module must expose:

```python
def generate_screens(screens_dir):
    """Generate annotated PNGs into screens_dir/ and screens_neutral/.
    Return list of filenames."""
```

The engine renders each step from two PNGs: one with the hotspot highlighted (for Level 1 GUIDED), one neutral (for Levels 0, 2, 3). The function writes both versions and returns the filename list.

### Common authoring mistakes (lessons from this codebase)

1. **Forgetting `mission`.** Engine reads `mission.time_limit` at level click; if `mission` is undefined, React tree dies → black screen. Drone scenario hit this in May 2026.
2. **Forgetting `screens_neutral` rendering.** If renderers don't accept an `hl=True/False` parameter, only the highlighted version exists; Level 0 falls back to highlighted screens, breaking the EXPLORE pedagogy.
3. **Inventing field names.** The engine reads what it reads. Adding an undocumented field (like the drone scenario's `premises`) is dead code; nothing renders it. If you need new metadata, add it to the engine first.
4. **Hardcoding scenario-specific text in renderers.** Renderers should produce images; scenario-specific dialogue belongs in `tutorial[].instruction`, not in the PNG.
5. **Confusing "build runs" with "trainer works."** The schema validator passing and `ui_trainer.py` exiting cleanly tells you the data is well-formed and the build didn't crash. It does not tell you the trainer is *usable* by a human. The system-wide GoalCard/ExplorePanel overlap bug (May 2026) shipped in every scenario for months because we only ever spot-checked the briefing screen, never sat down to play through a level on a real-sized viewport. The discipline: at minimum, manually click through Level 0 and Level 1 of any new scenario at a typical demo viewport (1440-1920px wide) before considering it done. Better long-term answer is visual regression testing in CI; that's queued in Phase 2 item 7 (Repeatable pipeline tooling).

### When to use Pillow vs. real assets

Pillow-drawn placeholders are appropriate for engine-and-pedagogy validation (Phase 1) but read as "early hack" in buy-in conversations. Real-asset migration is Phase 2 work; in the meantime, the index will display an `asset_source` indicator per scenario so demo audiences see fidelity tiers honestly. See `docs/asset-fidelity.md`.

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
python generators/video_render_veo3.py                  # bigfoot cast (default)
python generators/video_render_veo3.py --cast human     # warehouse worker cast

# Social video — 3-scene POC cut (~$3.60, daily-quota-safe)
python generators/video_render_veo3_poc.py              # bigfoot cast (default)
python generators/video_render_veo3_poc.py --cast human # warehouse worker cast

# Drift detection (Layer 6) — capture baselines and check for source drift
python detect_changes.py snapshot   # one-time: capture current state as baseline
python detect_changes.py check      # diff sources against baselines; exit 1 on drift
python detect_changes.py status     # show what's tracked

# Validate a single Veo clip (download raw, no audio stripping)
python generators/veo3_test_clip.py

# UI trainer — SE-DC perishable scenario (default)
python generators/ui_trainer.py

# UI trainer — software scenario packs
python generators/ui_trainer.py scenarios.standard_dry
python generators/ui_trainer.py scenarios.regulated_pharma
python generators/ui_trainer.py scenarios.hazmat
python generators/ui_trainer.py scenarios.serialized

# UI trainer — hardware scenario packs
python generators/ui_trainer.py scenarios.ar15_field_strip
python generators/ui_trainer.py scenarios.f150_trans_service

# UI trainer — HW/SW fusion scenario
python generators/ui_trainer.py scenarios.drone_preflight

# Regenerate the scenario selector (index.html) after adding/removing scenarios
python generators/generate_index.py

# Test parsers
python parsers/tosca_parser.py data/tosca/purchase_requisition.xml
python parsers/bpmn_parser.py data/bpmn/purchase_to_pay.xml
```

## What's Next (Phase 2 remaining)

Five of the eleven Phase 2 activities are complete (drift detection, character swap, HW/SW fusion scenario, refined demo materials, scenario schema validator). The Pillow phase-out is partially done (drone_anatomy, F-150, standard_dry_gr) and partially pending. Still ahead, in rough ROI order:

1. **Trainer UI Layout Refactor (Scope B — Responsive Grid)** — system-wide bug discovered May 2026: `GoalCard` and `ExplorePanel` are `position: fixed; bottom: 0/20` at z-index 200, sitting on top of the screen image. Visible across every scenario (software, hardware, fusion) at every viewport including 1920px+. Fix: responsive CSS Grid putting card to the right of the image at wide viewports, stacked below at narrow ones. Image `max-height` respects viewport so user never has to scroll to read instruction. Touches `ScreenView`, `GoalCard`, `ExplorePanel`, and parent layout in `App()`. Validation: manual check at 1280, 1440, 1920, 2560px.
2. **Continue Pillow phase-out** — drone_preflight (HW/SW fusion) needs real DJI Fly app screenshots from a phone running the actual app (not marketing captures). AR-15 needs publicly-available disassembly photos. 4 SAP scenarios (sedc, regulated_pharma, hazmat, serialized) need ERPNext Playwright capture (pipeline already exists for standard_dry_gr).
3. **Backfill mission.learning_objectives on the 5 SAP scenarios** — the validator surfaced this gap. Engine handles it gracefully but authors meant to fill in per-level objectives. Content task, not engineering.
4. **Refined process-agnostic prompt templates** — current prompts are tuned for SAP MIGO. Need parameterized templates that work for any transaction type without rewriting per-scenario.
5. **Opal overlay pattern** — formalize the configuration-driven overlay abstraction with real SE-DC site data; document the specification.
6. **WalkMe integration design** — beyond the JSON draft format the generator already produces. Design the actual integration points with a deployed WalkMe instance.
7. **Repeatable pipeline tooling** — versioning, rollback, automated asset validation, conflict detection. **Visual regression testing** (headless Chromium screenshot diffing) belongs here — would catch the layout-overlap class of bug we just discovered.
8. **3-5 additional process areas** — expand from PR/GR to 3-4 more processes (e.g. invoice receipt, returns, vendor master changes).

Phase 3 (multi-site rollout) and Phase 4 (operationalize / handoff) follow. See `docs/roadmap.md` for full detail.

## Key Docs to Read First

1. `docs/concept.md` — The "why", the layered model, and game-inspired training vision
2. `docs/game-design-vision.md` — Game mechanics framework, real-world examples, planned enhancements
3. `docs/architecture.md` — Full system design including video pipeline and UI trainer
4. `docs/tooling.md` — What we're using and why
5. `docs/drift-detection-demo.md` — Demo playbook for drift detection (Layer 6) and character swap, with pitch frame and objection handling
