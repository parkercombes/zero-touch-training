#!/usr/bin/env python3
"""
UI Trainer Scenario Validator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Validates all scenario folders for:
  1. Structural integrity (files exist, images loadable)
  2. Hotspot bounds (within image, reasonable size)
  3. Hotspot-to-screen alignment (renders overlay on actual screenshots)
  4. Explore panel overlap detection
  5. Data completeness (all required fields present)

Produces:
  - Console report with PASS/WARN/FAIL per check
  - Visual overlay PNGs in _validation/ folder for manual review

Usage:
  python3 validate_scenarios.py [scenario_folder ...]
  python3 validate_scenarios.py              # validates all
  python3 validate_scenarios.py hazmat_gr    # validates one
"""

import json, os, sys, re, glob
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ── Constants ─────────────────────────────────────────────────────────────────
EXPECTED_WIDTH = 1280
EXPECTED_HEIGHT = 720
MIN_HOTSPOT_DIM = 16      # minimum w or h in px
MAX_HOTSPOT_DIM = 600     # maximum w or h in px
TOLERANCE = 20            # click tolerance used by the React app
EXPLORE_PANEL_HEIGHT_PCT = 0.26  # ExplorePanel maxHeight is 26vh

# Colors for overlay rendering
COLOR_HOTSPOT = (232, 118, 0, 180)    # orange, semi-transparent
COLOR_HOTSPOT_BORDER = (232, 118, 0, 255)
COLOR_TOLERANCE = (107, 178, 255, 60)  # blue, very transparent
COLOR_EXPLORE_ZONE = (255, 50, 50, 80) # red overlay for explore panel area
COLOR_OK = "\033[92m"
COLOR_WARN = "\033[93m"
COLOR_FAIL = "\033[91m"
COLOR_RESET = "\033[0m"
COLOR_DIM = "\033[2m"
COLOR_BOLD = "\033[1m"


def extract_scenario_data(html_path):
    """Parse __SCENARIO__, __SCREENS__, __SCREENS_NEUTRAL__ from the HTML file."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    data = {}
    for var in ["__SCENARIO__", "__SCREENS__", "__SCREENS_NEUTRAL__"]:
        pattern = rf'window\.{re.escape(var)}\s*=\s*(\{{.*?\}});'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            try:
                data[var] = json.loads(match.group(1))
            except json.JSONDecodeError as e:
                data[var] = None
                print(f"  {COLOR_FAIL}FAIL{COLOR_RESET} Could not parse {var}: {e}")
        else:
            data[var] = None
            print(f"  {COLOR_FAIL}FAIL{COLOR_RESET} {var} not found in HTML")

    return data


def check_structural(scenario_dir, data):
    """Check that all referenced files exist and images are valid."""
    issues = []
    scenario = data.get("__SCENARIO__")
    screens = data.get("__SCREENS__")
    screens_neutral = data.get("__SCREENS_NEUTRAL__")

    if not scenario:
        issues.append(("FAIL", "No scenario data found"))
        return issues

    # Check tutorial steps exist
    tutorial = scenario.get("tutorial", [])
    if not tutorial:
        issues.append(("FAIL", "No tutorial steps defined"))
        return issues

    issues.append(("PASS", f"{len(tutorial)} tutorial steps found"))

    # Check screen image files
    for label, screen_map in [("highlighted", screens), ("neutral", screens_neutral)]:
        if not screen_map:
            issues.append(("FAIL", f"No {label} screen map"))
            continue
        for key, path in screen_map.items():
            full_path = os.path.join(scenario_dir, path)
            if not os.path.exists(full_path):
                issues.append(("FAIL", f"Missing {label} image: {path}"))
            elif HAS_PIL:
                try:
                    img = Image.open(full_path)
                    w, h = img.size
                    if w != EXPECTED_WIDTH or h != EXPECTED_HEIGHT:
                        issues.append(("WARN", f"{label}/{key}: {w}x{h} (expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT})"))
                    else:
                        issues.append(("PASS", f"{label}/{key}: {w}x{h} ✓"))
                except Exception as e:
                    issues.append(("FAIL", f"Cannot open {label}/{key}: {e}"))

    # Check required scenario fields
    for field in ["id", "title", "site", "role", "branding", "mission"]:
        if field not in scenario:
            issues.append(("WARN", f"Missing scenario field: {field}"))

    mission = scenario.get("mission", {})
    for field in ["title", "briefing", "par_clicks", "time_limit"]:
        if field not in mission:
            issues.append(("WARN", f"Missing mission field: {field}"))

    return issues


def check_hotspots(scenario_dir, data):
    """Validate hotspot coordinates against image dimensions."""
    issues = []
    scenario = data.get("__SCENARIO__")
    screens = data.get("__SCREENS__")
    if not scenario or not screens:
        return [("FAIL", "Cannot check hotspots — missing data")]

    tutorial = scenario.get("tutorial", [])

    for i, step in enumerate(tutorial):
        screen_name = step.get("screen", "?")
        hs = step.get("hotspot")
        if not hs:
            issues.append(("FAIL", f"Screen {i} ({screen_name}): No hotspot defined"))
            continue

        x, y, w, h = hs.get("x", 0), hs.get("y", 0), hs.get("w", 0), hs.get("h", 0)

        # Get actual image size
        img_path = os.path.join(scenario_dir, screens.get(screen_name, ""))
        img_w, img_h = EXPECTED_WIDTH, EXPECTED_HEIGHT
        if HAS_PIL and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img_w, img_h = img.size
            except:
                pass

        # Bounds check
        if x < 0 or y < 0:
            issues.append(("FAIL", f"Screen {i} ({screen_name}): Hotspot has negative coords ({x}, {y})"))
        if x + w > img_w:
            issues.append(("FAIL", f"Screen {i} ({screen_name}): Hotspot extends past right edge ({x}+{w}={x+w} > {img_w})"))
        if y + h > img_h:
            issues.append(("FAIL", f"Screen {i} ({screen_name}): Hotspot extends past bottom edge ({y}+{h}={y+h} > {img_h})"))

        # Size check
        if w < MIN_HOTSPOT_DIM or h < MIN_HOTSPOT_DIM:
            issues.append(("WARN", f"Screen {i} ({screen_name}): Hotspot very small ({w}x{h} px)"))
        if w > MAX_HOTSPOT_DIM or h > MAX_HOTSPOT_DIM:
            issues.append(("WARN", f"Screen {i} ({screen_name}): Hotspot very large ({w}x{h} px)"))

        # Tolerance zone check (expanded area)
        tol_left = x - TOLERANCE
        tol_top = y - TOLERANCE
        tol_right = x + w + TOLERANCE
        tol_bottom = y + h + TOLERANCE
        if tol_left < 0 or tol_top < 0:
            issues.append(("WARN", f"Screen {i} ({screen_name}): Tolerance zone clips top/left edge"))
        if tol_right > img_w or tol_bottom > img_h:
            issues.append(("WARN", f"Screen {i} ({screen_name}): Tolerance zone clips right/bottom edge"))

        # Reasonable position (not in extreme corners for small targets)
        center_x = x + w / 2
        center_y = y + h / 2

        # Check explore panel overlap (bottom 40% of screen)
        explore_top = img_h * (1 - EXPLORE_PANEL_HEIGHT_PCT)
        hotspot_bottom = y + h
        if hotspot_bottom > explore_top:
            overlap_px = hotspot_bottom - explore_top
            issues.append(("WARN", f"Screen {i} ({screen_name}): Hotspot overlaps Explore panel zone by {overlap_px:.0f}px "
                          f"(hotspot bottom={hotspot_bottom}, panel starts at y={explore_top:.0f})"))

        # Summary for passing
        if not any(screen_name in issue[1] and issue[0] in ("FAIL", "WARN") for issue in issues):
            issues.append(("PASS", f"Screen {i} ({screen_name}): hotspot ({x},{y}) {w}x{h} ✓"))

    return issues


def check_highlight_alignment(scenario_dir, data):
    """
    Compare highlighted vs neutral screenshots to detect where the visual
    highlight is, then verify the hotspot actually overlaps it.

    The screen generator bakes highlights (orange borders, tinted cells) into
    the 'screens/' images. The 'screens_neutral/' images are identical except
    without those highlights. Diffing the two reveals the highlighted region.
    If the hotspot doesn't overlap that region, the target is misaligned.
    """
    if not HAS_PIL:
        return [("WARN", "Pillow not installed — skipping highlight alignment check")]

    issues = []
    scenario = data.get("__SCENARIO__")
    screens = data.get("__SCREENS__")
    screens_neutral = data.get("__SCREENS_NEUTRAL__")
    if not scenario or not screens or not screens_neutral:
        return [("WARN", "Missing screen maps — skipping highlight alignment")]

    import numpy as np

    tutorial = scenario.get("tutorial", [])
    for i, step in enumerate(tutorial):
        screen_name = step.get("screen", "?")
        hs = step.get("hotspot", {})
        x, y, w, h = hs.get("x", 0), hs.get("y", 0), hs.get("w", 0), hs.get("h", 0)

        hi_path = os.path.join(scenario_dir, screens.get(screen_name, ""))
        lo_path = os.path.join(scenario_dir, screens_neutral.get(screen_name, ""))
        if not os.path.exists(hi_path) or not os.path.exists(lo_path):
            continue

        hi_img = np.array(Image.open(hi_path).convert("RGB"), dtype=np.int16)
        lo_img = np.array(Image.open(lo_path).convert("RGB"), dtype=np.int16)

        # Compute per-pixel colour difference
        diff = np.sqrt(np.sum((hi_img - lo_img).astype(np.float64) ** 2, axis=2))

        # Threshold: pixels with noticeable difference are "highlighted"
        highlight_mask = diff > 30  # ~30 units of RGB euclidean distance

        highlight_pixels = int(np.sum(highlight_mask))
        if highlight_pixels < 10:
            # No visible highlight difference — can't validate alignment
            issues.append(("PASS", f"Screen {i} ({screen_name}): no highlight diff detected (screens may be identical)"))
            continue

        # Check how many highlighted pixels fall inside the hotspot
        hs_mask = highlight_mask[max(0,y):y+h, max(0,x):x+w]
        inside = int(np.sum(hs_mask))

        # And how many highlighted pixels exist in total
        pct_inside = (inside / highlight_pixels * 100) if highlight_pixels > 0 else 0

        # Find the bounding box of the highlighted region
        rows = np.any(highlight_mask, axis=1)
        cols = np.any(highlight_mask, axis=0)
        if rows.any() and cols.any():
            hl_y0, hl_y1 = np.where(rows)[0][[0, -1]]
            hl_x0, hl_x1 = np.where(cols)[0][[0, -1]]

            # Check overlap between hotspot and highlight bounding box
            overlap_x = max(0, min(x + w, int(hl_x1)) - max(x, int(hl_x0)))
            overlap_y = max(0, min(y + h, int(hl_y1)) - max(y, int(hl_y0)))
            overlap_area = overlap_x * overlap_y
            hotspot_area = w * h

            if overlap_area == 0:
                issues.append(("FAIL", f"Screen {i} ({screen_name}): Hotspot ({x},{y}) {w}x{h} has ZERO overlap "
                              f"with highlight region ({hl_x0},{hl_y0})-({hl_x1},{hl_y1})"))
            elif pct_inside < 5:
                issues.append(("WARN", f"Screen {i} ({screen_name}): Only {pct_inside:.0f}% of highlight pixels "
                              f"inside hotspot — possible misalignment. "
                              f"Highlight bbox: ({hl_x0},{hl_y0})-({hl_x1},{hl_y1})"))
            else:
                issues.append(("PASS", f"Screen {i} ({screen_name}): {pct_inside:.0f}% highlight overlap ✓"))
        else:
            issues.append(("PASS", f"Screen {i} ({screen_name}): highlight check OK"))

    return issues


def check_explore_data(data):
    """Check explore_info completeness."""
    issues = []
    scenario = data.get("__SCENARIO__")
    if not scenario:
        return [("FAIL", "No scenario data")]

    tutorial = scenario.get("tutorial", [])
    for i, step in enumerate(tutorial):
        screen_name = step.get("screen", "?")
        explore_info = step.get("explore_info")
        if not explore_info:
            issues.append(("WARN", f"Screen {i} ({screen_name}): No explore_info — will fall back to instruction text"))
        elif len(explore_info) < 2:
            issues.append(("WARN", f"Screen {i} ({screen_name}): Only {len(explore_info)} explore_info item(s) — consider adding more"))
        else:
            issues.append(("PASS", f"Screen {i} ({screen_name}): {len(explore_info)} explore_info items ✓"))

        # Check required step fields
        for field in ["goal", "instruction", "hint", "feedback", "consequence"]:
            if field not in step or not step[field]:
                issues.append(("WARN", f"Screen {i} ({screen_name}): Missing step field '{field}'"))

    return issues


def check_back_links(scenario_dir):
    """Check that the scenario links back to the parent selector page."""
    issues = []
    html_path = os.path.join(scenario_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    selector_refs = content.count("selector.html")
    index_refs = len(re.findall(r'["\']\.\.\/index\.html["\']', content))
    total_back = selector_refs + index_refs

    if total_back >= 1:
        targets = []
        if selector_refs: targets.append(f"{selector_refs}x selector.html")
        if index_refs: targets.append(f"{index_refs}x ../index.html")
        issues.append(("PASS", f"Found back-link(s) to parent: {', '.join(targets)} ✓"))
    else:
        issues.append(("WARN", "No back-links to parent selector page found"))

    return issues


def _safe_text(text):
    """Strip non-ASCII characters for bitmap font compatibility."""
    return text.encode("ascii", "replace").decode("ascii")


def generate_visual_overlays(scenario_dir, data, output_dir):
    """Render hotspot overlays on actual screenshot images for manual review."""
    if not HAS_PIL:
        return [("WARN", "Pillow not installed — skipping visual overlays")]

    issues = []
    scenario = data.get("__SCENARIO__")
    screens = data.get("__SCREENS__")
    screens_neutral = data.get("__SCREENS_NEUTRAL__")
    if not scenario or not screens:
        return [("FAIL", "Cannot generate overlays — missing data")]

    os.makedirs(output_dir, exist_ok=True)
    tutorial = scenario.get("tutorial", [])

    for i, step in enumerate(tutorial):
        screen_name = step.get("screen", "?")
        hs = step.get("hotspot", {})
        x, y, w, h = hs.get("x", 0), hs.get("y", 0), hs.get("w", 0), hs.get("h", 0)

        # Use highlighted screen for Level 0/1 view
        img_path = os.path.join(scenario_dir, screens.get(screen_name, ""))
        if not os.path.exists(img_path):
            issues.append(("FAIL", f"Screen {i}: Cannot load {img_path}"))
            continue

        img = Image.open(img_path).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Draw tolerance zone
        draw.rectangle(
            [x - TOLERANCE, y - TOLERANCE, x + w + TOLERANCE, y + h + TOLERANCE],
            fill=COLOR_TOLERANCE,
            outline=(107, 178, 255, 120),
            width=1
        )

        # Draw hotspot
        draw.rectangle(
            [x, y, x + w, y + h],
            fill=COLOR_HOTSPOT,
            outline=COLOR_HOTSPOT_BORDER,
            width=2
        )

        # Draw explore panel zone
        explore_top = int(img.size[1] * (1 - EXPLORE_PANEL_HEIGHT_PCT))
        draw.rectangle(
            [0, explore_top, img.size[0], img.size[1]],
            fill=COLOR_EXPLORE_ZONE
        )

        # Draw crosshair at hotspot center
        cx, cy = x + w // 2, y + h // 2
        draw.line([(cx - 15, cy), (cx + 15, cy)], fill=(255, 255, 255, 200), width=1)
        draw.line([(cx, cy - 15), (cx, cy + 15)], fill=(255, 255, 255, 200), width=1)

        # Add labels
        font = None
        font_sm = None
        for font_path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSMono.ttf",
            "/Library/Fonts/Arial.ttf",
        ]:
            try:
                font = ImageFont.truetype(font_path, 14)
                font_sm = ImageFont.truetype(font_path, 11)
                break
            except (IOError, OSError):
                continue
        if font is None:
            font = ImageFont.load_default()
            font_sm = font

        # Hotspot label
        label = f"Screen {i}: {screen_name}"
        draw.text((x, y - 18), label, fill=(255, 255, 255, 240), font=font_sm)

        # Coords label
        coords = f"({x},{y}) {w}x{h}"
        draw.text((x, y + h + 4), coords, fill=(255, 200, 100, 240), font=font_sm)

        # Goal label at top
        draw.rectangle([0, 0, img.size[0], 28], fill=(0, 0, 0, 180))
        draw.text((8, 6), _safe_text(f"Step {i}: {step.get('goal', '?')}"), fill=(255, 255, 255, 240), font=font)

        # Explore zone label
        draw.text((10, explore_top + 4), "<-- Explore Panel Zone (26vh)", fill=(255, 100, 100, 200), font=font_sm)

        # Composite
        result = Image.alpha_composite(img, overlay)
        out_path = os.path.join(output_dir, f"step_{i:02d}_{screen_name}")
        result.save(out_path)
        issues.append(("PASS", f"Visual overlay: {out_path}"))

    # Generate summary sheet (all steps in a grid)
    if len(tutorial) > 0:
        thumb_w, thumb_h = 320, 180
        cols = min(4, len(tutorial))
        rows = (len(tutorial) + cols - 1) // cols
        sheet = Image.new("RGB", (thumb_w * cols + 10, thumb_h * rows + 30 * rows), (20, 20, 40))
        sheet_draw = ImageDraw.Draw(sheet)

        for i, step in enumerate(tutorial):
            screen_name = step.get("screen", "?")
            thumb_path = os.path.join(output_dir, f"step_{i:02d}_{screen_name}")
            if os.path.exists(thumb_path):
                thumb = Image.open(thumb_path).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
                col = i % cols
                row = i // cols
                px = col * thumb_w + 5
                py = row * (thumb_h + 30) + 25
                sheet.paste(thumb, (px, py))
                sheet_draw.text((px + 4, py - 16),
                    _safe_text(f"Step {i}: {step.get('goal', '?')[:40]}"),
                    fill=(200, 200, 200), font=font_sm)

        # Title
        scenario_id = scenario.get("id", "unknown")
        for tf_path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
        ]:
            try:
                title_font = ImageFont.truetype(tf_path, 16)
                break
            except (IOError, OSError):
                continue
        else:
            title_font = font
        sheet_draw.text((10, 4), _safe_text(f"Validation: {scenario_id}"), fill=(255, 255, 255), font=title_font)

        sheet_path = os.path.join(output_dir, f"_summary_sheet.png")
        sheet.save(sheet_path)
        issues.append(("PASS", f"Summary sheet: {sheet_path}"))

    return issues


def validate_scenario(scenario_dir):
    """Run all validation checks on a single scenario folder."""
    scenario_name = os.path.basename(scenario_dir)
    html_path = os.path.join(scenario_dir, "index.html")

    print(f"\n{'='*70}")
    print(f"{COLOR_BOLD}Validating: {scenario_name}{COLOR_RESET}")
    print(f"{'='*70}")

    if not os.path.exists(html_path):
        print(f"  {COLOR_FAIL}FAIL{COLOR_RESET} No index.html found in {scenario_dir}")
        return {"scenario": scenario_name, "pass": 0, "warn": 0, "fail": 1}

    # Extract data
    data = extract_scenario_data(html_path)
    counts = {"pass": 0, "warn": 0, "fail": 0}

    # Run checks
    checks = [
        ("Structure & Files", check_structural(scenario_dir, data)),
        ("Hotspot Bounds & Alignment", check_hotspots(scenario_dir, data)),
        ("Highlight Alignment", check_highlight_alignment(scenario_dir, data)),
        ("Explore Mode Data", check_explore_data(data)),
        ("Navigation Links", check_back_links(scenario_dir)),
    ]

    # Visual overlays
    output_dir = os.path.join(scenario_dir, "_validation")
    visual_issues = generate_visual_overlays(scenario_dir, data, output_dir)
    checks.append(("Visual Overlays", visual_issues))

    for section_name, issues in checks:
        print(f"\n  {COLOR_DIM}── {section_name} ──{COLOR_RESET}")
        for level, msg in issues:
            if level == "PASS":
                counts["pass"] += 1
                # Only print passes in verbose mode — keep output clean
            elif level == "WARN":
                counts["warn"] += 1
                print(f"  {COLOR_WARN}WARN{COLOR_RESET} {msg}")
            elif level == "FAIL":
                counts["fail"] += 1
                print(f"  {COLOR_FAIL}FAIL{COLOR_RESET} {msg}")

    print(f"\n  {COLOR_BOLD}Results:{COLOR_RESET} "
          f"{COLOR_OK}{counts['pass']} pass{COLOR_RESET}, "
          f"{COLOR_WARN}{counts['warn']} warn{COLOR_RESET}, "
          f"{COLOR_FAIL}{counts['fail']} fail{COLOR_RESET}")

    return {"scenario": scenario_name, **counts}


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Find scenarios to validate
    if len(sys.argv) > 1:
        scenario_dirs = [os.path.join(base_dir, s) for s in sys.argv[1:]]
    else:
        # Auto-detect: any subfolder with an index.html containing __SCENARIO__
        scenario_dirs = []
        for d in sorted(os.listdir(base_dir)):
            full = os.path.join(base_dir, d)
            idx = os.path.join(full, "index.html")
            if os.path.isdir(full) and os.path.exists(idx) and d != "_validation":
                with open(idx, "r") as f:
                    if "__SCENARIO__" in f.read(5000):
                        scenario_dirs.append(full)

    if not scenario_dirs:
        print("No scenario folders found. Run from ui_trainer_preview/ or pass folder names.")
        sys.exit(1)

    print(f"{COLOR_BOLD}UI Trainer Scenario Validator{COLOR_RESET}")
    print(f"Found {len(scenario_dirs)} scenario(s) to validate")
    if not HAS_PIL:
        print(f"{COLOR_WARN}Note: Install Pillow for visual overlay generation (pip install Pillow){COLOR_RESET}")

    results = []
    for sd in scenario_dirs:
        results.append(validate_scenario(sd))

    # Summary table
    print(f"\n{'='*70}")
    print(f"{COLOR_BOLD}Summary{COLOR_RESET}")
    print(f"{'='*70}")
    print(f"  {'Scenario':<25} {'Pass':>6} {'Warn':>6} {'Fail':>6}  Status")
    print(f"  {'─'*25} {'─'*6} {'─'*6} {'─'*6}  {'─'*8}")
    total_warn = 0
    total_fail = 0
    for r in results:
        total_warn += r["warn"]
        total_fail += r["fail"]
        status = (f"{COLOR_FAIL}FAIL{COLOR_RESET}" if r["fail"] > 0
                  else f"{COLOR_WARN}WARN{COLOR_RESET}" if r["warn"] > 0
                  else f"{COLOR_OK}PASS{COLOR_RESET}")
        print(f"  {r['scenario']:<25} {r['pass']:>6} {r['warn']:>6} {r['fail']:>6}  {status}")

    print()
    if total_fail > 0:
        print(f"  {COLOR_FAIL}✗ {total_fail} failure(s) need fixing{COLOR_RESET}")
    if total_warn > 0:
        print(f"  {COLOR_WARN}⚠ {total_warn} warning(s) to review{COLOR_RESET}")
    if total_fail == 0 and total_warn == 0:
        print(f"  {COLOR_OK}✓ All scenarios pass validation{COLOR_RESET}")

    print(f"\n  Visual overlays saved to each scenario's _validation/ folder.")
    print(f"  Review the _summary_sheet.png in each for a quick visual check.\n")


if __name__ == "__main__":
    main()
