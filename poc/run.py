#!/usr/bin/env python3
"""
Zero-Touch Training PoC — Pipeline Orchestrator

Runs the full training generation pipeline:
1. Load config
2. Parse source data (Tosca XML, BPMN XML)
3. Load and resolve Opal overlays
4. Run AI generators (walkthroughs, video scripts, job aids, WalkMe flows)
5. Write outputs

Usage:
    python run.py                    # Run full pipeline
    python run.py --dry-run          # Parse + overlay only, no AI calls
    python run.py --layer walkthrough  # Run a single layer
    python run.py --layer video_script
    python run.py --layer job_aid
    python run.py --layer walkme

Requires ANTHROPIC_API_KEY in environment or .env file.
"""

import argparse
import os
import sys
import time
from pathlib import Path

import yaml


def load_env():
    """Load .env file if present (simple key=value parsing)."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key_name = key.strip()
                    val = value.strip()
                    if val and not os.environ.get(key_name):
                        os.environ[key_name] = val


def load_config(config_path: str = None) -> dict:
    """Load the PoC config.yaml."""
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


def resolve_paths(config: dict) -> dict:
    """Resolve relative paths in config to absolute paths from poc/ root."""
    poc_root = Path(__file__).parent
    sources = config.get("sources", {})

    resolved = {}
    for source_type, paths in sources.items():
        resolved[source_type] = [str(poc_root / p) for p in paths]

    return resolved


def parse_sources(resolved_paths: dict) -> dict:
    """Parse all source files into structured data."""
    from parsers import ToscaParser, BpmnParser

    parsed = {
        "tosca_scripts": [],
        "bpmn_processes": [],
    }

    # Parse Tosca XML files
    tosca_parser = ToscaParser()
    for path in resolved_paths.get("tosca", []):
        if not Path(path).exists():
            print(f"  ⚠️  Tosca file not found: {path}")
            continue
        print(f"  Parsing Tosca: {Path(path).name}")
        script = tosca_parser.parse(path)
        parsed["tosca_scripts"].append(script)
        print(f"    → {script.name}: {len(script.steps)} steps, "
              f"{len(script.site_specific_steps)} site-specific")

    # Parse BPMN XML files
    bpmn_parser = BpmnParser()
    for path in resolved_paths.get("bpmn", []):
        if not Path(path).exists():
            print(f"  ⚠️  BPMN file not found: {path}")
            continue
        print(f"  Parsing BPMN: {Path(path).name}")
        process = bpmn_parser.parse(path)
        parsed["bpmn_processes"].append(process)
        print(f"    → {process.name}: {len(process.tasks)} tasks, "
              f"{len(process.roles)} roles, {len(process.decision_points)} decisions")

    return parsed


def load_overlays(resolved_paths: dict, role: str) -> dict:
    """Load and resolve Opal overlays."""
    from assembler import OpalOverlayAssembler

    overlay_paths = resolved_paths.get("overlay", [])
    if not overlay_paths:
        print("  ⚠️  No overlay files configured")
        return {"site": {}, "overlays": []}

    assembler = OpalOverlayAssembler(overlay_paths)
    assembler.load()

    print(f"\n  Overlay summary:")
    print(f"  {assembler.summary()}")

    return assembler.resolve(role=role)


def run_generators(
    config: dict,
    parsed_data: dict,
    overlay_data: dict,
    layers: list[str] = None,
    output_dir: str = None,
) -> dict:
    """
    Run AI generators for specified layers.

    Args:
        config: Parsed config.yaml
        parsed_data: Parsed Tosca/BPMN data
        overlay_data: Resolved overlay data
        layers: Which layers to run (None = all)
        output_dir: Output directory override

    Returns:
        Dict mapping layer name → list of output paths
    """
    from generators import (
        WalkthroughGenerator,
        VideoScriptGenerator,
        JobAidGenerator,
        WalkMeDraftGenerator,
    )

    if output_dir is None:
        poc_root = Path(__file__).parent
        output_dir = str(poc_root / config.get("output", {}).get("directory", "output"))

    # Map layer names to generator classes
    generator_map = {
        "walkthrough": WalkthroughGenerator,
        "video_script": VideoScriptGenerator,
        "job_aid": JobAidGenerator,
        "walkme": WalkMeDraftGenerator,
    }

    if layers is None:
        layers = list(generator_map.keys())

    results = {}
    for layer_name in layers:
        if layer_name not in generator_map:
            print(f"  ⚠️  Unknown layer: {layer_name}")
            continue

        GeneratorClass = generator_map[layer_name]
        print(f"\n{'='*60}")
        print(f"Layer: {layer_name.replace('_', ' ').title()}")
        print(f"{'='*60}")

        generator = GeneratorClass(config=config, output_dir=output_dir)
        try:
            output_paths = generator.generate(parsed_data, overlay_data)
            results[layer_name] = output_paths
            print(f"\n  Generated {len(output_paths)} file(s) for {layer_name}")
        except Exception as e:
            print(f"\n  ❌ Error in {layer_name}: {e}")
            results[layer_name] = []

    return results


def print_summary(results: dict) -> None:
    """Print a summary of all generated outputs."""
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print(f"{'='*60}")

    total = 0
    for layer, paths in results.items():
        count = len(paths)
        total += count
        status = "✅" if count > 0 else "⚠️ "
        print(f"  {status} {layer}: {count} file(s)")
        for p in paths:
            print(f"       → {p}")

    print(f"\n  Total outputs: {total}")


def main():
    parser = argparse.ArgumentParser(
        description="Zero-Touch Training PoC Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                       Full pipeline (all layers)
  python run.py --dry-run             Parse sources only, no AI
  python run.py --layer walkthrough   Generate walkthroughs only
  python run.py --layer video_script  Generate video scripts only
  python run.py --layer job_aid       Generate job aids only
  python run.py --layer walkme        Generate WalkMe flows only
  python run.py --config alt.yaml     Use alternate config
        """,
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to config.yaml (default: poc/config.yaml)",
    )
    parser.add_argument(
        "--layer", "-l",
        action="append",
        choices=["walkthrough", "video_script", "job_aid", "walkme"],
        help="Run specific layer(s) only. Can be repeated.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory override",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and overlay only — skip AI generation",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Banner
    print("""
╔══════════════════════════════════════════════════════════╗
║          Zero-Touch Training PoC Pipeline               ║
║          Training-as-Code → AI → Content                ║
╚══════════════════════════════════════════════════════════╝
    """)

    start_time = time.time()

    # Load environment
    print("📋 Loading environment...")
    load_env()

    # Load config
    print("📋 Loading config...")
    config = load_config(args.config)
    scope = config.get("scope", {})
    print(f"  Company: {scope.get('company')}")
    print(f"  Site: {scope.get('site')} ({scope.get('site_code')})")
    print(f"  Role: {scope.get('role')}")
    print(f"  Process: {scope.get('process')}")

    # Resolve paths
    resolved = resolve_paths(config)

    # Parse sources
    print("\n📂 Parsing source data...")
    parsed_data = parse_sources(resolved)

    tosca_count = len(parsed_data["tosca_scripts"])
    bpmn_count = len(parsed_data["bpmn_processes"])
    print(f"\n  Parsed: {tosca_count} Tosca script(s), {bpmn_count} BPMN process(es)")

    # Load overlays
    print("\n🔧 Loading Opal overlays...")
    overlay_data = load_overlays(resolved, role=scope.get("role", ""))

    if args.dry_run:
        print("\n🏁 Dry run complete — skipping AI generation")
        elapsed = time.time() - start_time
        print(f"   Elapsed: {elapsed:.1f}s")
        return

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n❌ ANTHROPIC_API_KEY not set.")
        print("   Copy .env.example to .env and add your API key.")
        print("   Or: export ANTHROPIC_API_KEY=your-key-here")
        sys.exit(1)

    # Run generators
    print("\n🤖 Running AI generators...")
    results = run_generators(
        config=config,
        parsed_data=parsed_data,
        overlay_data=overlay_data,
        layers=args.layer,
        output_dir=args.output,
    )

    # Summary
    print_summary(results)

    elapsed = time.time() - start_time
    print(f"\n  Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
