#!/usr/bin/env python3
"""
Drift Detection (Layer 6) — Zero-Touch Training PoC

When a source asset changes (Tosca test script, BPMN process model, Opal overlay),
the training materials generated from it become stale. This CLI detects that drift.

Subcommands
-----------
  snapshot  Capture the current parsed state of all source files as the new baseline.
  check     Re-parse current sources, diff against the baseline, emit a drift report.
            Exit code 0 = no drift, 1 = drift detected (suitable for CI gates).
  status    Show the current snapshot date and a summary of what's tracked.

Design
------
Each source file is parsed into its dataclass representation (ToscaTestScript,
BpmnProcess, or raw YAML for overlays), then reduced to a "training-relevant
fingerprint" — a normalized dict capturing only the fields that, if changed,
would invalidate generated training. Cosmetic changes (descriptions, comments,
formatting) are intentionally excluded so we don't trigger spurious regenerations.

The fingerprint is stored in poc/snapshots/<file>.snapshot.json. On `check`,
we recompute and diff. Each diff is mapped through scenario_deps.yaml to the
list of scenarios and generated artifacts that need regeneration.

Output: poc/output/drift_report.json (machine-readable) and
        poc/output/drift_report.md (human-readable).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# Make sibling parser modules importable when invoked from poc/
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from parsers.tosca_parser import ToscaParser, ToscaTestScript  # noqa: E402
from parsers.bpmn_parser import BpmnParser, BpmnProcess  # noqa: E402


SNAPSHOT_DIR = SCRIPT_DIR / "snapshots"
OUTPUT_DIR = SCRIPT_DIR / "output"
CONFIG_PATH = SCRIPT_DIR / "config.yaml"
DEPS_PATH = SCRIPT_DIR / "data" / "scenario_deps.yaml"


# ---------------------------------------------------------------------------
# Fingerprinting
# ---------------------------------------------------------------------------

def _hash_dict(d: dict) -> str:
    """Stable hash of a dict for change detection."""
    canonical = json.dumps(d, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def fingerprint_tosca(script: ToscaTestScript) -> dict[str, Any]:
    """
    Reduce a Tosca script to a training-relevant fingerprint.

    Included (changes invalidate training):
      - script_id, version, process, transaction, site_code
      - per-step: step_id, step_number, action_type, element identifier, value
      - per-step: assertion type + field reference + expected value
      - annotation count + types

    Excluded (cosmetic, doesn't affect training):
      - description text
      - execution_status, execution_count, last_executed
      - screenshot paths
    """
    steps = []
    for step in script.steps:
        step_fp = {
            "step_id": step.step_id,
            "step_number": step.step_number,
            "action_type": step.action_type,
            "element_id": step.element.identifier if step.element else "",
            "value": step.value,
            "target_url": step.target_url,
            "assertions": [
                {
                    "type": a.type,
                    "field_reference": a.field_reference,
                    "expected_value": a.expected_value,
                    "allowed_values": a.allowed_values,
                    "validation_type": a.validation_type,
                }
                for a in step.assertions
            ],
        }
        step_fp["hash"] = _hash_dict(step_fp)
        steps.append(step_fp)

    return {
        "kind": "tosca",
        "script_id": script.script_id,
        "version": script.version,
        "process": script.process,
        "transaction": script.transaction,
        "site_code": script.site_code,
        "step_count": len(script.steps),
        "steps": steps,
        "annotation_types": sorted({a.type for a in script.annotations}),
        "annotation_count": len(script.annotations),
    }


def fingerprint_bpmn(process: BpmnProcess) -> dict[str, Any]:
    """
    Reduce a BPMN process to a training-relevant fingerprint.

    Included:
      - process id + name
      - tasks (id, name, transaction_code)
      - gateways (id, name, type)
      - events (id, type)
      - roles (participant names)
      - sequence flow topology (source -> target pairs)

    Excluded:
      - documentation text
      - layout/diagram coordinates
    """
    return {
        "kind": "bpmn",
        "process_id": process.id,
        "process_name": process.name,
        "tasks": sorted(
            [{"id": t.id, "name": t.name, "transaction_code": t.transaction_code} for t in process.tasks],
            key=lambda x: x["id"],
        ),
        "gateways": sorted(
            [{"id": g.id, "name": g.name, "type": g.gateway_type} for g in process.gateways],
            key=lambda x: x["id"],
        ),
        "events": sorted(
            [{"id": e.id, "type": e.event_type} for e in process.events],
            key=lambda x: x["id"],
        ),
        "roles": sorted(process.roles),
        "flows": sorted(
            [{"source": f.source_ref, "target": f.target_ref} for f in process.sequence_flows],
            key=lambda x: (x["source"], x["target"]),
        ),
    }


def fingerprint_overlay(yaml_path: Path) -> dict[str, Any]:
    """Treat overlay YAML as a structural dict — full content matters."""
    with yaml_path.open() as f:
        data = yaml.safe_load(f) or {}
    return {"kind": "overlay", "content": data, "content_hash": _hash_dict(data)}


# ---------------------------------------------------------------------------
# Snapshot I/O
# ---------------------------------------------------------------------------

def _snapshot_path(source_path: Path) -> Path:
    """Map a source file to its snapshot file in poc/snapshots/."""
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    safe_name = str(source_path.relative_to(SCRIPT_DIR)).replace("/", "__").replace("\\", "__")
    return SNAPSHOT_DIR / f"{safe_name}.snapshot.json"


def load_config() -> dict:
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


def load_deps() -> dict:
    if not DEPS_PATH.exists():
        return {"scenarios": {}}
    with DEPS_PATH.open() as f:
        return yaml.safe_load(f)


def parse_source(source_path: Path) -> dict[str, Any]:
    """Dispatch to the right parser based on file location/extension."""
    rel = str(source_path.relative_to(SCRIPT_DIR))
    if "tosca" in rel and rel.endswith(".xml"):
        script = ToscaParser().parse(str(source_path))
        return fingerprint_tosca(script)
    elif "bpmn" in rel and rel.endswith(".xml"):
        process = BpmnParser().parse(str(source_path))
        return fingerprint_bpmn(process)
    elif rel.endswith(".yaml") or rel.endswith(".yml"):
        return fingerprint_overlay(source_path)
    else:
        raise ValueError(f"Unknown source type: {rel}")


def collect_sources(config: dict) -> list[Path]:
    """All source paths declared in config.yaml under sources.*"""
    paths = []
    for kind in ("tosca", "bpmn", "overlay"):
        for rel in config.get("sources", {}).get(kind, []) or []:
            paths.append(SCRIPT_DIR / rel)
    return paths


# ---------------------------------------------------------------------------
# Diffing
# ---------------------------------------------------------------------------

def _diff_tosca(old: dict, new: dict) -> list[dict]:
    """Compare two Tosca fingerprints, return list of change records."""
    changes = []

    # Top-level fields
    for key in ("script_id", "version", "process", "transaction", "site_code"):
        if old.get(key) != new.get(key):
            changes.append({"type": "metadata", "field": key, "old": old.get(key), "new": new.get(key)})

    # Step-by-step diff using step_id as the join key
    old_steps = {s["step_id"]: s for s in old.get("steps", [])}
    new_steps = {s["step_id"]: s for s in new.get("steps", [])}

    for step_id in old_steps.keys() - new_steps.keys():
        changes.append({"type": "step_removed", "step_id": step_id})
    for step_id in new_steps.keys() - old_steps.keys():
        changes.append({"type": "step_added", "step_id": step_id, "action_type": new_steps[step_id]["action_type"]})
    for step_id in old_steps.keys() & new_steps.keys():
        if old_steps[step_id]["hash"] != new_steps[step_id]["hash"]:
            modified_fields = [
                k for k in ("action_type", "element_id", "value", "target_url")
                if old_steps[step_id].get(k) != new_steps[step_id].get(k)
            ]
            assertion_changed = old_steps[step_id].get("assertions") != new_steps[step_id].get("assertions")
            changes.append({
                "type": "step_modified",
                "step_id": step_id,
                "fields_changed": modified_fields,
                "assertions_changed": assertion_changed,
            })

    if old.get("annotation_types") != new.get("annotation_types"):
        changes.append({
            "type": "annotations_changed",
            "old": old.get("annotation_types"),
            "new": new.get("annotation_types"),
        })

    return changes


def _diff_bpmn(old: dict, new: dict) -> list[dict]:
    changes = []

    old_task_ids = {t["id"]: t for t in old.get("tasks", [])}
    new_task_ids = {t["id"]: t for t in new.get("tasks", [])}
    for tid in old_task_ids.keys() - new_task_ids.keys():
        changes.append({"type": "task_removed", "task_id": tid, "name": old_task_ids[tid]["name"]})
    for tid in new_task_ids.keys() - old_task_ids.keys():
        changes.append({"type": "task_added", "task_id": tid, "name": new_task_ids[tid]["name"]})
    for tid in old_task_ids.keys() & new_task_ids.keys():
        if old_task_ids[tid] != new_task_ids[tid]:
            changes.append({"type": "task_modified", "task_id": tid, "old": old_task_ids[tid], "new": new_task_ids[tid]})

    old_gw = {g["id"]: g for g in old.get("gateways", [])}
    new_gw = {g["id"]: g for g in new.get("gateways", [])}
    for gid in old_gw.keys() - new_gw.keys():
        changes.append({"type": "gateway_removed", "gateway_id": gid})
    for gid in new_gw.keys() - old_gw.keys():
        changes.append({"type": "gateway_added", "gateway_id": gid, "gateway_type": new_gw[gid]["type"]})
    for gid in old_gw.keys() & new_gw.keys():
        if old_gw[gid] != new_gw[gid]:
            changes.append({"type": "gateway_modified", "gateway_id": gid})

    if set(old.get("roles", [])) != set(new.get("roles", [])):
        changes.append({
            "type": "roles_changed",
            "added": sorted(set(new.get("roles", [])) - set(old.get("roles", []))),
            "removed": sorted(set(old.get("roles", [])) - set(new.get("roles", []))),
        })

    if old.get("flows") != new.get("flows"):
        changes.append({"type": "flows_changed", "old_count": len(old.get("flows", [])), "new_count": len(new.get("flows", []))})

    return changes


def _diff_overlay(old: dict, new: dict) -> list[dict]:
    if old.get("content_hash") != new.get("content_hash"):
        return [{"type": "overlay_modified"}]
    return []


def diff_fingerprints(old: dict, new: dict) -> list[dict]:
    if old.get("kind") != new.get("kind"):
        return [{"type": "kind_changed", "old": old.get("kind"), "new": new.get("kind")}]
    if old["kind"] == "tosca":
        return _diff_tosca(old, new)
    if old["kind"] == "bpmn":
        return _diff_bpmn(old, new)
    if old["kind"] == "overlay":
        return _diff_overlay(old, new)
    return []


# ---------------------------------------------------------------------------
# Mapping changes to affected scenarios
# ---------------------------------------------------------------------------

def affected_scenarios(changed_source_rel: str, deps: dict) -> dict[str, list[str]]:
    """
    Given a source file (relative path under poc/), return:
      {
        "scenarios": [scenario_id, ...],
        "artifacts": [artifact_key, ...],
      }
    """
    affected = {"scenarios": [], "artifacts": []}
    scenarios_block = deps.get("scenarios", {}) or {}

    for scenario_id, dep_spec in scenarios_block.items():
        if scenario_id == "generated_artifacts":
            continue
        all_deps = []
        for kind in ("tosca", "bpmn", "overlay"):
            all_deps.extend(dep_spec.get(kind, []) or [])
        if changed_source_rel in all_deps:
            affected["scenarios"].append(scenario_id)

    artifacts_block = scenarios_block.get("generated_artifacts", {}) or {}
    for artifact_key, dep_spec in artifacts_block.items():
        all_deps = []
        for kind in ("tosca", "bpmn", "overlay"):
            all_deps.extend(dep_spec.get(kind, []) or [])
        if changed_source_rel in all_deps:
            affected["artifacts"].append(artifact_key)

    return affected


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_snapshot(args) -> int:
    config = load_config()
    sources = collect_sources(config)
    SNAPSHOT_DIR.mkdir(exist_ok=True)

    print(f"Capturing baseline snapshot of {len(sources)} source files...")
    for src in sources:
        if not src.exists():
            print(f"  ✗ {src.relative_to(SCRIPT_DIR)} — file not found, skipping")
            continue
        fp = parse_source(src)
        snap_path = _snapshot_path(src)
        with snap_path.open("w") as f:
            json.dump(
                {
                    "source": str(src.relative_to(SCRIPT_DIR)),
                    "captured_at": datetime.now(timezone.utc).isoformat(),
                    "fingerprint": fp,
                },
                f,
                indent=2,
                sort_keys=True,
            )
        print(f"  ✓ {src.relative_to(SCRIPT_DIR)} → {snap_path.relative_to(SCRIPT_DIR)}")

    print(f"\nBaseline captured. Run `python detect_changes.py check` after source changes.")
    return 0


def cmd_check(args) -> int:
    config = load_config()
    deps = load_deps()
    sources = collect_sources(config)

    OUTPUT_DIR.mkdir(exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources_checked": len(sources),
        "sources_with_changes": 0,
        "missing_baselines": [],
        "changes": [],
        "stale_scenarios": set(),
        "stale_artifacts": set(),
    }

    for src in sources:
        rel = str(src.relative_to(SCRIPT_DIR))
        snap_path = _snapshot_path(src)

        if not src.exists():
            report["changes"].append({"source": rel, "diff": [{"type": "source_missing"}]})
            continue

        if not snap_path.exists():
            report["missing_baselines"].append(rel)
            continue

        with snap_path.open() as f:
            old = json.load(f)["fingerprint"]
        new = parse_source(src)

        diffs = diff_fingerprints(old, new)
        if diffs:
            report["sources_with_changes"] += 1
            affected = affected_scenarios(rel, deps)
            report["changes"].append({
                "source": rel,
                "diff": diffs,
                "affected_scenarios": affected["scenarios"],
                "affected_artifacts": affected["artifacts"],
            })
            report["stale_scenarios"].update(affected["scenarios"])
            report["stale_artifacts"].update(affected["artifacts"])

    report["stale_scenarios"] = sorted(report["stale_scenarios"])
    report["stale_artifacts"] = sorted(report["stale_artifacts"])

    json_path = OUTPUT_DIR / "drift_report.json"
    md_path = OUTPUT_DIR / "drift_report.md"
    with json_path.open("w") as f:
        json.dump(report, f, indent=2)
    with md_path.open("w") as f:
        f.write(_render_markdown(report))

    drift_found = report["sources_with_changes"] > 0
    print(f"\nDrift report written to {json_path.relative_to(SCRIPT_DIR)} and {md_path.relative_to(SCRIPT_DIR)}")
    if report["missing_baselines"]:
        print(f"  ⚠  No baseline for: {', '.join(report['missing_baselines'])} — run `snapshot` first")
    if drift_found:
        print(f"  ⚠  Drift detected in {report['sources_with_changes']} source(s).")
        print(f"     Stale scenarios: {', '.join(report['stale_scenarios']) or '(none)'}")
        print(f"     Stale artifacts: {', '.join(report['stale_artifacts']) or '(none)'}")
        return 1
    print("  ✓ No drift detected. All training assets in sync with sources.")
    return 0


def cmd_status(args) -> int:
    config = load_config()
    sources = collect_sources(config)

    print("Drift detection — current baseline status")
    print("-" * 60)
    for src in sources:
        rel = str(src.relative_to(SCRIPT_DIR))
        snap_path = _snapshot_path(src)
        if not snap_path.exists():
            print(f"  ✗ {rel:50s}  no baseline")
            continue
        with snap_path.open() as f:
            data = json.load(f)
        captured = data.get("captured_at", "?")
        kind = data.get("fingerprint", {}).get("kind", "?")
        print(f"  ✓ {rel:50s}  {kind:8s}  {captured}")
    return 0


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------

def _render_markdown(report: dict) -> str:
    lines = []
    lines.append("# Training Drift Report")
    lines.append("")
    lines.append(f"**Generated:** {report['generated_at']}")
    lines.append(f"**Sources checked:** {report['sources_checked']}")
    lines.append(f"**Sources with changes:** {report['sources_with_changes']}")
    lines.append("")

    if report["missing_baselines"]:
        lines.append("## Missing Baselines")
        lines.append("")
        for src in report["missing_baselines"]:
            lines.append(f"- `{src}` — no baseline snapshot. Run `python detect_changes.py snapshot` to create one.")
        lines.append("")

    if not report["changes"]:
        lines.append("## ✓ No drift detected")
        lines.append("")
        lines.append("All training assets are in sync with their source files.")
        return "\n".join(lines)

    lines.append("## Stale Training Assets")
    lines.append("")
    if report["stale_scenarios"]:
        lines.append("**Scenarios needing regeneration:**")
        for s in report["stale_scenarios"]:
            lines.append(f"- `{s}`")
        lines.append("")
    if report["stale_artifacts"]:
        lines.append("**Generated artifacts needing regeneration:**")
        for a in report["stale_artifacts"]:
            lines.append(f"- `{a}` (walkthrough, video script, job aid, walkme draft, process rationale)")
        lines.append("")

    lines.append("## Changes by Source")
    lines.append("")
    for change in report["changes"]:
        lines.append(f"### `{change['source']}`")
        lines.append("")
        if change.get("affected_scenarios"):
            lines.append(f"**Affected scenarios:** {', '.join('`' + s + '`' for s in change['affected_scenarios'])}")
        if change.get("affected_artifacts"):
            lines.append(f"**Affected artifacts:** {', '.join('`' + a + '`' for a in change['affected_artifacts'])}")
        lines.append("")
        lines.append("**Detected changes:**")
        for d in change["diff"]:
            lines.append(f"- {_format_diff_entry(d)}")
        lines.append("")

    return "\n".join(lines)


def _format_diff_entry(d: dict) -> str:
    t = d.get("type", "unknown")
    if t == "metadata":
        return f"Metadata `{d['field']}` changed: `{d['old']}` → `{d['new']}`"
    if t == "step_added":
        return f"Step **added**: `{d['step_id']}` ({d.get('action_type', '?')})"
    if t == "step_removed":
        return f"Step **removed**: `{d['step_id']}`"
    if t == "step_modified":
        fields = ", ".join(d.get("fields_changed", [])) or "—"
        assertion_note = " · assertions changed" if d.get("assertions_changed") else ""
        return f"Step **modified**: `{d['step_id']}` (fields: {fields}{assertion_note})"
    if t == "annotations_changed":
        return f"Annotations changed"
    if t == "task_added":
        return f"BPMN task **added**: `{d['task_id']}` — {d['name']}"
    if t == "task_removed":
        return f"BPMN task **removed**: `{d['task_id']}` — {d.get('name', '?')}"
    if t == "task_modified":
        return f"BPMN task **modified**: `{d['task_id']}`"
    if t == "gateway_added":
        return f"BPMN gateway **added**: `{d['gateway_id']}` ({d.get('gateway_type', '?')})"
    if t == "gateway_removed":
        return f"BPMN gateway **removed**: `{d['gateway_id']}`"
    if t == "gateway_modified":
        return f"BPMN gateway **modified**: `{d['gateway_id']}`"
    if t == "roles_changed":
        added = ", ".join(d.get("added", []))
        removed = ", ".join(d.get("removed", []))
        return f"Roles changed (added: {added or '—'}; removed: {removed or '—'})"
    if t == "flows_changed":
        return f"Sequence flow topology changed ({d['old_count']} → {d['new_count']} flows)"
    if t == "overlay_modified":
        return f"Overlay content modified"
    if t == "source_missing":
        return f"Source file missing"
    if t == "kind_changed":
        return f"Source type changed: {d['old']} → {d['new']}"
    return f"{t}: {d}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="detect_changes.py",
        description="Drift detection for Zero-Touch Training (Layer 6).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("snapshot", help="Capture current source state as baseline.")
    sub.add_parser("check", help="Diff current sources against baseline; emit drift report. Exit 1 on drift.")
    sub.add_parser("status", help="Show current baseline status per source.")

    args = parser.parse_args()
    if args.command == "snapshot":
        return cmd_snapshot(args)
    if args.command == "check":
        return cmd_check(args)
    if args.command == "status":
        return cmd_status(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
