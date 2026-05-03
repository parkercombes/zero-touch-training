# Drone Anatomy Scenario — Build Report

**Date:** 2026-05-02
**Scenario:** `poc/generators/scenarios/drone_anatomy.py`
**Trainer output:** `poc/output/ui_trainer/drone_anatomy/index.html`

---

## What got built

A 5-step pure-hardware training scenario using real DJI photos. Each step has a hotspot on a real component, plus narrative consequence + explore_info + decoys for higher levels.

| # | Component | Source photo | Photo aspect | Hotspot status |
|---|---|---|---|---|
| 1 | Hasselblad wide-angle lens | `10:33:50 AM` (camera array) | 1.744 (near 16:9) | ✓ on lens |
| 2 | 3-axis gimbal mount | `10:40:46 AM` (front view) | 2.664 (wide, top/bottom letterboxed) | ✓ on gimbal |
| 3 | Front-left propeller | `10:40:38 AM` (top-down) | 1.173 (tall, side letterboxed) | ✓ on prop |
| 4 | Forward vision sensors | `10:41:09 AM` (front-low) | 1.463 (tall, side letterboxed) | ✓ on top body |
| 5 | Bottom vision sensors | `10:41:03 AM` (underbelly) | 1.140 (tall, side letterboxed) | ✓ on belly cluster |

All hotspots verified visually against grid overlays. Decoys (for L2/L3 neutral mode) placed on plausible wrong-answer regions.

---

## What I had to fix mid-build (trust calibration)

The first generation pass had **3 of 5 hotspots in the wrong place** plus **the wrong source photo for step 3**. Specifically:

- **Step 1 (Hasselblad lens):** my initial coordinate math put the hotspot ~150px to the right of the actual lens — empty space next to the camera housing.
- **Step 3 (propellers):** I used `10:40:14` based on my own inventory entry that called it "top-down with extended props." It is actually a side profile of a folded drone. The real top-down photo is `10:40:38`. The inventory I wrote earlier in this session mis-classified that file. **Inventory.md has been corrected separately if you want me to update it; right now it still has the wrong description for 10:40:14.**
- **Step 4 (top vision sensors):** hotspot was 80px too high — sat above the drone body in empty space.
- **Step 5 (bottom vision sensors):** hotspot was 80px too high AND ~80px too far left — landed on the left arm/strut, not on the belly recess.

**Why this matters:** I had two of the same Group D photos swapped in the inventory (10:41:03 vs 10:41:09 — caught and corrected on first verification) AND now a third (10:40:14 vs 10:40:38). That's a higher error rate than I should be carrying without flagging it. If you depend on the inventory.md classifications for anything else, double-check by opening the photos. I'd recommend I do a second pass through the inventory to fix any remaining misreads.

---

## Engine assumptions worth knowing

A few things about the existing engine I leaned on, and one workaround:

**Glob-tolerant filename lookup.** macOS Screenshot writes filenames with U+202F (narrow no-break space) before "AM"/"PM", not a regular space. Hard-coded filename strings in Python miss these files. The scenario's `_resolve_photo()` helper falls back to glob matching so the file resolves regardless of which space character is in the filename. If the user ever renames the screenshots, this still works.

**Letterbox instead of stretch.** The engine's `base_hardware.load_base_image()` does `.resize((W, H))` which stretches the source to 1280×720 — fine for square-ish hardware diagrams, distortive for wide marketing photos. The scenario uses its own `_load_letterboxed()` helper that fits within the canvas with HW_BG padding. Hotspot coordinates are in post-letterbox canvas space and depend on the source photo's aspect ratio.

**Hardware mode bakes the highlight into the PNG.** When `training_domain == "hardware"`, the React engine skips its overlay rendering (`trainer_app.jsx` line 488 and 525). The orange hotspot rectangle and the blue decoys are drawn in by `annotate_region()` at PNG generation time. So the same 1280×720 PNG must serve both Level 0 (no highlight) and Level 1 (highlight visible) — the engine handles that by generating two folders: `screens/` (with highlight) and `screens_neutral/` (with decoys instead).

---

## What this validates and what it doesn't

### Validates

1. The engine's hardware path works end-to-end with **real photographs** and not just PIL placeholders. Phase 2 of `PLAN_hardware_extension.md` is now exercised against real assets, not theoretical.
2. The `load_base_image` / `annotate_region` / `hardware_status_banner` contract is sufficient to author a hardware scenario as a single Python file.
3. Letterboxing wide marketing photos is a viable adaptation pattern for assets that don't match canvas aspect ratio.
4. Hotspot tuning needs visual verification against a coordinate-grid overlay — math from source-image-position is unreliable when the photo content isn't mathematically definable. Built `outputs/grid_debug/` images during this build; that loop should be standard practice for any hardware scenario using real photos.

### Does NOT validate

1. **Procedural training.** This scenario teaches *identification*, not *procedure*. The DJI source material doesn't include step-by-step procedural shots (battery insertion, prop orientation, gimbal cover removal, app activation, calibration). Those screens still need to be either shot live with a real Mavic 3 Pro or stubbed with PIL placeholders.
2. **The fusion (HW/SW) flow.** That's `drone_preflight.py`, which still uses PIL placeholders for everything. Real DJI Fly app screenshots would need to be captured from a phone running the actual app — none of the marketing screenshots show real app UI states.
3. **The scenario index.** I did not modify `generate_index.py`. The new scenario doesn't appear in any auto-generated launcher yet. Run it directly: `python3 ui_trainer.py scenarios/drone_anatomy`.
4. **Real-world pedagogical value.** I made up the consequence narratives and explore_info from general drone-operations knowledge plus the manual text — they're plausible but not authoritative. A real Part 107 instructor or a DJI service technician should review before any training use.

---

## Files changed/created

| Path | Status |
|---|---|
| `poc/generators/scenarios/drone_anatomy.py` | NEW — 5-step scenario module |
| `poc/output/ui_trainer/drone_anatomy/index.html` | NEW — generated trainer |
| `poc/output/ui_trainer/drone_anatomy/screens/*.png` | NEW — 5 highlighted PNGs |
| `poc/output/ui_trainer/drone_anatomy/screens_neutral/*.png` | NEW — 5 neutral+decoy PNGs |
| `docs/DJI_Mavic_3/inventory.md` | UNCHANGED — has known errors (see "trust calibration" above) |
| `docs/DJI_Mavic_3/build-report.md` | NEW — this file |

---

## Suggested next moves

In order of cost vs. payoff:

1. **Open the trainer and play through Levels 0-3 yourself.** See if the consequence narratives ring true to you, if any hotspots feel off in the actual click-through rather than the static screenshots, and if the decoy positions are convincingly tempting.
2. **If the scenario reads OK,** wire it into `generate_index.py` so it shows up in any scenario launcher you have. Quick change.
3. **If you want to push to real procedural training:** the next missing pieces are app screenshots and step-by-step photos. Cheapest path is shooting them on your phone with a Mavic 3 Pro on a table. Follow the `drone_preflight.py` PIL placeholder pattern as a structural template, then swap in real photos as they're shot.
4. **If you don't want to push further on drone:** the same `_load_letterboxed` pattern transfers to any future hardware scenario that uses real photography. Worth pulling up into `base_hardware.py` as a shared helper if you're going to keep using it.

I would NOT recommend marking the inventory work "done" until I do the second-pass verification I mentioned above. Two of my classifications turned out wrong; there may be more.
