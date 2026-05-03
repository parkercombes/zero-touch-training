#!/usr/bin/env python3
"""
validate_scenario_schema.py — Schema validator for scenario source modules
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Validates each `scenarios/<name>.py` module against the React engine's required
SCENARIO contract — at *source-module* time, before the trainer is built. This
prevents bugs like the May 2026 drone black-screen incident, where a missing
`mission` dict caused the React tree to die silently on level click.

Distinct from `poc/output/ui_trainer/validate_scenarios.py`, which validates
the *built artifacts* (manifest JSON, hotspot bounds against rendered images).
This one validates *source modules* before they ever build.

Behavior
  - ERRORs cause exit code 1 (build should not proceed).
  - WARNs are surfaced but exit 0 (engine has fallbacks; build can proceed).
  - Each scenario gets a single grouped report so the developer can fix
    multiple issues in one editing pass.

Usage
  python3 validate_scenario_schema.py                # validate all scenarios
  python3 validate_scenario_schema.py drone_preflight   # one scenario
  python3 validate_scenario_schema.py --quiet        # only show failures

Designed to be invoked at the top of `generate_index.py` so the index can't be
regenerated against broken scenarios.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))


# ── Schema definition ────────────────────────────────────────────────────────
# Source of truth: what the React engine in trainer_app.jsx actually reads.
# Re-verify by grepping `SCENARIO\.` and `mission\.` and `step\.` in trainer_app.jsx.

REQUIRED_SCENARIO_FIELDS = {
    "id":              str,
    "title":           str,
    "site":            str,
    "role":            str,
    "training_domain": str,    # also constrained by VALID_DOMAINS below
    "tutorial":        list,
    "mission":         dict,
}

OPTIONAL_SCENARIO_FIELDS = {
    "branding":         dict,
    "handling_profile": (str, type(None)),
    "exploded_view":    (dict, type(None)),
    "asset_source":     str,    # constrained by VALID_ASSET_SOURCES
}

VALID_DOMAINS        = {"software", "hardware", "fusion"}
VALID_ASSET_SOURCES  = {"placeholder", "textbook", "oem_marketing", "captured", "photographed"}

# Mission sub-fields. `briefing` is hard-required (read unconditionally on
# trainer_app.jsx:1163). The rest have `|| fallback` guards, so we WARN
# but don't ERROR — the engine degrades gracefully but the author probably
# meant to set them.
MISSION_HARD_REQUIRED = {
    "briefing": str,
}

MISSION_SOFT_REQUIRED = {
    "time_limit":          int,
    "narratives":          list,
    "learning_objectives": dict,
}

# Per-step keys. Same hard/soft split.
STEP_HARD_REQUIRED = {
    "screen":      str,
    "goal":        str,
    "instruction": str,
    "hint":        str,
    "hotspot":     dict,
    "feedback":    str,
}

STEP_SOFT_REQUIRED = {
    "consequence":  str,
    "explore_info": list,
}

HOTSPOT_REQUIRED_KEYS = {"x", "y", "w", "h"}


# ── Result types ─────────────────────────────────────────────────────────────
class Issue:
    """An ERROR or WARN against a specific location in a scenario."""
    __slots__ = ("severity", "where", "message")

    def __init__(self, severity: str, where: str, message: str):
        self.severity = severity   # "ERROR" or "WARN"
        self.where = where         # human-readable path, e.g. "mission.briefing" or "tutorial[3].hotspot"
        self.message = message

    def __str__(self) -> str:
        sym = "✗" if self.severity == "ERROR" else "⚠"
        return f"  {sym} {self.severity}  {self.where}: {self.message}"


# ── Field-level checks ───────────────────────────────────────────────────────
def _check_field(obj: dict, key: str, expected: Any, where: str, severity: str) -> list[Issue]:
    """Check that obj[key] exists and matches expected type."""
    if key not in obj:
        return [Issue(severity, f"{where}.{key}", "field is missing")]
    value = obj[key]
    if isinstance(expected, tuple):
        if not isinstance(value, expected):
            type_names = "|".join(t.__name__ for t in expected)
            return [Issue(severity, f"{where}.{key}",
                          f"expected {type_names}, got {type(value).__name__}")]
    else:
        if not isinstance(value, expected):
            return [Issue(severity, f"{where}.{key}",
                          f"expected {expected.__name__}, got {type(value).__name__}")]
    if isinstance(value, str) and value.strip() == "":
        return [Issue("WARN", f"{where}.{key}", "value is empty string")]
    if isinstance(value, list) and len(value) == 0:
        return [Issue("WARN", f"{where}.{key}", "list is empty")]
    return []


def _check_hotspot(hs: Any, where: str) -> list[Issue]:
    """Hotspot must be a dict with numeric x, y, w, h."""
    issues: list[Issue] = []
    if not isinstance(hs, dict):
        return [Issue("ERROR", where, f"expected dict, got {type(hs).__name__}")]
    missing = HOTSPOT_REQUIRED_KEYS - set(hs.keys())
    if missing:
        issues.append(Issue("ERROR", where, f"hotspot missing keys: {sorted(missing)}"))
    for k in HOTSPOT_REQUIRED_KEYS & set(hs.keys()):
        if not isinstance(hs[k], (int, float)):
            issues.append(Issue("ERROR", f"{where}.{k}",
                                f"expected number, got {type(hs[k]).__name__}"))
        elif hs[k] < 0:
            issues.append(Issue("WARN", f"{where}.{k}", f"value is negative ({hs[k]})"))
    return issues


def _check_step(step: dict, idx: int) -> list[Issue]:
    """Validate a single tutorial step."""
    issues: list[Issue] = []
    where = f"tutorial[{idx}]"
    if not isinstance(step, dict):
        return [Issue("ERROR", where, f"expected dict, got {type(step).__name__}")]

    for key, expected in STEP_HARD_REQUIRED.items():
        issues.extend(_check_field(step, key, expected, where, severity="ERROR"))
    for key, expected in STEP_SOFT_REQUIRED.items():
        issues.extend(_check_field(step, key, expected, where, severity="WARN"))

    if "hotspot" in step:
        issues.extend(_check_hotspot(step["hotspot"], f"{where}.hotspot"))

    return issues


def _check_mission(mission: Any) -> list[Issue]:
    """Validate the mission dict."""
    issues: list[Issue] = []
    if not isinstance(mission, dict):
        return [Issue("ERROR", "mission", f"expected dict, got {type(mission).__name__}")]
    for key, expected in MISSION_HARD_REQUIRED.items():
        issues.extend(_check_field(mission, key, expected, "mission", severity="ERROR"))
    for key, expected in MISSION_SOFT_REQUIRED.items():
        issues.extend(_check_field(mission, key, expected, "mission", severity="WARN"))
    return issues


# ── Module-level checks ──────────────────────────────────────────────────────
def validate_scenario_module(module_name: str) -> tuple[str, list[Issue]]:
    """
    Import a scenario module and validate its SCENARIO dict + generate_screens().
    Returns (scenario_id_or_module_name, issues).
    """
    issues: list[Issue] = []

    try:
        mod = importlib.import_module(f"scenarios.{module_name}")
    except Exception as e:
        return module_name, [Issue("ERROR", "import", f"failed to import: {e}")]

    if not hasattr(mod, "SCENARIO"):
        issues.append(Issue("ERROR", "module", "no SCENARIO dict at module top level"))
        return module_name, issues

    scenario = mod.SCENARIO
    if not isinstance(scenario, dict):
        issues.append(Issue("ERROR", "SCENARIO", f"expected dict, got {type(scenario).__name__}"))
        return module_name, issues

    # Required top-level fields
    for key, expected in REQUIRED_SCENARIO_FIELDS.items():
        issues.extend(_check_field(scenario, key, expected, "SCENARIO", severity="ERROR"))

    # Optional top-level fields — only check type if present
    for key, expected in OPTIONAL_SCENARIO_FIELDS.items():
        if key in scenario:
            issues.extend(_check_field(scenario, key, expected, "SCENARIO", severity="WARN"))

    # Domain enum check
    domain = scenario.get("training_domain")
    if domain is not None and domain not in VALID_DOMAINS:
        issues.append(Issue("ERROR", "SCENARIO.training_domain",
                            f"invalid value '{domain}'; must be one of {sorted(VALID_DOMAINS)}"))

    # Asset source enum check (optional but tightly constrained when set)
    asset_src = scenario.get("asset_source")
    if asset_src is not None and asset_src not in VALID_ASSET_SOURCES:
        issues.append(Issue("ERROR", "SCENARIO.asset_source",
                            f"invalid value '{asset_src}'; must be one of {sorted(VALID_ASSET_SOURCES)}"))

    # Mission validation
    if "mission" in scenario:
        issues.extend(_check_mission(scenario["mission"]))

    # Tutorial validation
    tutorial = scenario.get("tutorial")
    if isinstance(tutorial, list):
        if len(tutorial) == 0:
            issues.append(Issue("ERROR", "SCENARIO.tutorial", "tutorial is empty"))
        for i, step in enumerate(tutorial):
            issues.extend(_check_step(step, i))

    # generate_screens() must exist and be callable
    if not hasattr(mod, "generate_screens"):
        issues.append(Issue("ERROR", "module",
                            "missing generate_screens(screens_dir) function — "
                            "ui_trainer.py invokes this to produce step PNGs"))
    elif not callable(getattr(mod, "generate_screens")):
        issues.append(Issue("ERROR", "module.generate_screens",
                            "exists but is not callable"))

    scenario_id = scenario.get("id", module_name) if isinstance(scenario, dict) else module_name
    return scenario_id, issues


# ── Discovery ────────────────────────────────────────────────────────────────
def discover_scenario_modules() -> list[str]:
    """Find all scenario modules in scenarios/ that look like real scenarios."""
    scen_dir = SCRIPT_DIR / "scenarios"
    modules = []
    for f in sorted(scen_dir.glob("*.py")):
        name = f.stem
        if name.startswith("_") or name.startswith("base"):
            continue
        modules.append(name)
    return modules


# ── Main ─────────────────────────────────────────────────────────────────────
def run(modules: list[str], quiet: bool = False) -> int:
    """Validate the given list of modules. Returns 0 on full success, 1 on any error."""
    total_errors = 0
    total_warns = 0

    for mod_name in modules:
        scenario_id, issues = validate_scenario_module(mod_name)
        errors = [i for i in issues if i.severity == "ERROR"]
        warns = [i for i in issues if i.severity == "WARN"]
        total_errors += len(errors)
        total_warns += len(warns)

        if not issues:
            if not quiet:
                print(f"✓ {scenario_id}")
            continue

        if errors:
            print(f"✗ {scenario_id}  ({len(errors)} error(s), {len(warns)} warning(s))")
        else:
            if quiet:
                continue
            print(f"⚠ {scenario_id}  ({len(warns)} warning(s))")

        for issue in issues:
            print(issue)

    print()
    if total_errors == 0 and total_warns == 0:
        print(f"✓ All {len(modules)} scenarios pass schema validation.")
    else:
        print(f"  Summary: {total_errors} error(s), {total_warns} warning(s) across {len(modules)} scenarios.")
        if total_errors == 0:
            print(f"  No build-blocking errors. The trainer build can proceed.")

    return 1 if total_errors > 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="validate_scenario_schema.py",
        description="Validate scenario source modules against the engine's SCENARIO contract.",
    )
    parser.add_argument("scenarios", nargs="*",
                        help="Specific scenario module names to validate. Default: all.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress success lines; only show failures.")
    args = parser.parse_args()

    modules = args.scenarios or discover_scenario_modules()
    if not modules:
        print("No scenario modules found.")
        return 1
    return run(modules, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
