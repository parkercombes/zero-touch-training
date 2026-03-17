#!/usr/bin/env python3
"""
ui_trainer.py — Generic game-style interactive UI trainer engine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loads a scenario pack and generates a self-contained interactive HTML trainer.

FOUR-LEVEL PROGRESSION:
  Level 0 — EXPLORE       Free roam, tooltips, no task pressure
  Level 1 — GUIDED        Spotlight + step-by-step + hints
  Level 2 — ON YOUR OWN   No spotlight, hints cost XP (10s delay)
  Level 3 — CHALLENGE     Timer, narrative premise, no hints, leaderboard

Usage:
  python3 generators/ui_trainer.py                         # default SE-DC GR
  python3 generators/ui_trainer.py scenarios/pharma_gr     # pharma scenario
  python3 generators/ui_trainer.py scenarios/hazmat_gr     # hazmat scenario

Output:  poc/output/ui_trainer/{scenario_id}/
  ├── index.html   ← open in any browser, no server needed
  └── screens/     ← placeholder PNGs (swap with real screenshots)

Scenario pack contract
──────────────────────
Each scenario is a Python module (in generators/scenarios/) that exports:

  SCENARIO : dict
    id               str    — kebab-case identifier (used in output path)
    title            str    — displayed in browser tab + HUD
    site             str    — displayed in HUD subtitle
    role             str    — learner's job role
    handling_profile str    — "standard_dry" | "perishable" | "regulated_pharma"
                              | "hazmat" | "serialized"
    tutorial         list   — steps; each step:
        screen       str    — filename in screens/
        goal         str    — shown as the step objective
        instruction  str    — shown as the action instruction
        hint         str    — revealed on demand (Level 1 free, Level 2 costs XP)
        hotspot      dict   — {x, y, w, h} pixel rect of the clickable target
        feedback     str    — shown after a correct click
        consequence  str    — (optional) shown on wrong click in Level 2+
        explore_info list   — (optional) [str] element descriptions shown in Level 0
    mission          dict
        title        str
        briefing     str    — shown before mission starts
        par_clicks   int    — target click count for scoring
        narratives   list   — (optional) rotating narrative premise strings
        time_limit   int    — (optional) seconds for Level 3 timer (default 180)

  generate_screens(screens_dir: Path) -> list[str]
    Generates placeholder PNGs into screens_dir.
    Returns list of filenames generated.

To create a new scenario, copy scenarios/sedc_goods_receipt.py and edit it.
"""

import sys, os, json, importlib
from pathlib import Path


# ── Resolve scenario module ───────────────────────────────────────────────────
def load_scenario(module_path: str):
    """
    Import scenario module from a dotted name or file path.
    Default: scenarios.sedc_goods_receipt
    """
    # Normalise: convert path separators + strip .py suffix
    module_path = module_path.replace("/", ".").replace("\\", ".").rstrip(".")
    if module_path.endswith(".py"):
        module_path = module_path[:-3]

    # Add generators/ to sys.path so relative imports work
    generators_dir = str(Path(__file__).parent)
    if generators_dir not in sys.path:
        sys.path.insert(0, generators_dir)

    return importlib.import_module(module_path)


# ── React HTML wrapper ────────────────────────────────────────────────────────
# Loads React 18 + Babel standalone from CDN.
# Injects scenario data as window globals, then includes the JSX inline.

REACT_WRAPPER = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Interactive UI Trainer</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.9/babel.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0a0a1a; margin: 0; }
  #root { height: 100vh; overflow: hidden; }

</style>
</head>
<body>
<div id="root"></div>

<script>
// ── Scenario data (injected by ui_trainer.py) ──
window.__SCENARIO__        = __SCENARIO_JSON__;
window.__SCREENS__         = __SCREENS_JSON__;
window.__SCREENS_NEUTRAL__ = __SCREENS_NEUTRAL_JSON__;
</script>

<script type="text/babel">
__JSX_CODE__
// ── Mount ──
ReactDOM.createRoot(document.getElementById("root")).render(<App />);
</script>
</body>
</html>
"""


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Resolve scenario
    scenario_arg = sys.argv[1] if len(sys.argv) > 1 else "scenarios.sedc_goods_receipt"
    print(f"Loading scenario: {scenario_arg}")
    mod = load_scenario(scenario_arg)

    scenario = mod.SCENARIO
    sid = scenario["id"]
    print(f"  Title   : {scenario['title']}")
    print(f"  Site    : {scenario['site']}")
    print(f"  Profile : {scenario['handling_profile']}")
    print(f"  Steps   : {len(scenario['tutorial'])}")

    # Output paths
    base_out    = Path(__file__).parent.parent / "output" / "ui_trainer" / sid
    screens_dir = base_out / "screens"
    base_out.mkdir(parents=True, exist_ok=True)

    # Generate placeholder screens
    print("\nGenerating placeholder screens …")
    generated = mod.generate_screens(screens_dir)
    for fname in generated:
        print(f"  ✓  {fname}")

    # Build both screen maps (relative paths for HTML)
    screens_hl      = {fname: f"screens/{fname}" for fname in generated}
    screens_neutral = {fname: f"screens_neutral/{fname}" for fname in generated}

    # Read the React JSX component source
    jsx_path = Path(__file__).parent / "trainer_app.jsx"
    jsx_code = jsx_path.read_text(encoding="utf-8")
    print(f"\n  JSX source: {jsx_path}  ({len(jsx_code)} chars)")

    # Build the HTML wrapper with injected data + JSX
    html = REACT_WRAPPER.replace(
        "__SCENARIO_JSON__", json.dumps(scenario, indent=2)
    ).replace(
        "__SCREENS_JSON__", json.dumps(screens_hl, indent=2)
    ).replace(
        "__SCREENS_NEUTRAL_JSON__", json.dumps(screens_neutral, indent=2)
    ).replace(
        "__JSX_CODE__", jsx_code
    )

    index_path = base_out / "index.html"
    index_path.write_text(html, encoding="utf-8")

    print(f"\n✅  Done!  (React version)")
    print(f"   Trainer : {index_path}")
    print(f"   Screens : {screens_dir}/")
    print(f"\n   Open with:  open \"{index_path}\"")
    print(f"\n   4 levels: Explore → Guided → On Your Own → Challenge")
    print(f"   Each level adds pressure and removes scaffolding.\n")


if __name__ == "__main__":
    main()
