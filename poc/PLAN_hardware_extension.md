# Hardware Domain Extension — Implementation Plan

## Goal
Extend the trainer engine to support hardware training (gun maintenance, auto maintenance, etc.) alongside existing SAP software training — same repo, same 4-level progression engine.

## Why It Works Without a Fork
The React trainer engine (hotspot overlay, levels, scoring, timer, narratives, consequences, explore panels) is domain-agnostic. It just needs: an image + a hotspot rectangle + tutorial metadata. That contract is identical for "click the Storage Location dropdown" and "click the bolt catch release."

---

## Phase 1: Branding Abstraction
**What:** Extract hardcoded SAP colors/strings from `trainer_app.jsx` into a `branding` object injected from the scenario.

**Files changed:**
- `generators/scenarios/base.py` — Add `SAP_BRANDING` dict export (shell color, level names, level colors, level descriptions as hex strings)
- `generators/trainer_app.jsx` — Replace ~20 hardcoded color/string references with `SCENARIO.branding.*` lookups, with SAP defaults as fallback
- `generators/ui_trainer.py` — No change needed (already injects full SCENARIO JSON)
- All 5 existing scenario `.py` files — Add `"training_domain": "software"` and `"branding": SAP_BRANDING`

**Test:** All 5 existing trainers regenerate with identical appearance.

---

## Phase 2: Hardware Base Module
**What:** Create `base_hardware.py` — the hardware equivalent of `base.py`. Instead of SAP widget drawing (draw_field, draw_dropdown), it provides photo-annotation helpers.

**New file:** `generators/scenarios/base_hardware.py`

**Key functions:**
- `load_base_image(path)` — Load a photograph/diagram, or generate a grey placeholder for dev
- `annotate_region(img, hotspot, label, hl)` — Draw highlight box / numbered badge on a photo
- `draw_callout(img, x, y, text)` — Arrow + label pointing at a component
- `HARDWARE_BRANDING` dict — Safety-orange / steel-grey / green-red palette, hardware-appropriate level names ("OBSERVE", "FOLLOW ALONG", "DO IT", "SPEED RUN")

**Test:** Import module, generate a placeholder annotated image.

---

## Phase 3: Pilot Hardware Scenario
**What:** Build one real hardware scenario to prove the pipeline end-to-end.

**New file:** `generators/scenarios/ar15_field_strip.py` (or `oil_change.py` — your pick)

**Structure:** Same contract as SAP scenarios:
```python
SCENARIO = {
    "id": "ar15_field_strip",
    "title": "AR-15 Field Strip & Cleaning",
    "site": "Range Safety Training",
    "role": "Armorer Trainee",
    "training_domain": "hardware",
    "branding": HARDWARE_BRANDING,
    "tutorial": [ ... steps with hotspots on photo regions ... ],
    "mission": { ... }
}
SCREEN_GENERATORS = { ... }
def generate_screens(screens_dir): ...
```

**Screen generation:** Start with placeholder diagrams (labelled component rectangles drawn by PIL). Real photos can be swapped in later — the hotspot coordinates just need to match.

**Test:** `python3 ui_trainer.py scenarios/ar15_field_strip` → working trainer with 4 levels.

---

## Phase 4: Scenario Selector Update
**What:** Update `index.html` to group scenarios by domain (Software / Hardware) and auto-generate from scenario metadata.

**New file:** `generators/generate_index.py` — Scans scenario modules, builds index.html with domain sections.

**Test:** Run script, open index, see both SAP and hardware scenarios grouped.

---

## Order of Operations
```
Phase 1 (branding abstraction)  →  prerequisite for everything
Phase 2 (base_hardware.py)      →  can start in parallel with Phase 1
Phase 3 (pilot scenario)        →  needs Phase 1 + 2 complete
Phase 4 (index generator)       →  needs Phase 3 complete (need a hardware scenario to show)
```

## What Doesn't Change
- Game logic (state machine, hotspot detection, scoring, XP)
- 4-level progression (Explore → Guided → Solo → Challenge)
- Consequence / explore_info / narrative systems
- Screen dual-variant pattern (highlighted + neutral)
- The scenario pack contract (SCENARIO dict + generate_screens function)
