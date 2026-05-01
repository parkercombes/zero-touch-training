#!/usr/bin/env python3
"""
generate_index.py — Auto-generate the Scenario Selector (index.html)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scans every *.py file under scenarios/, imports the SCENARIO dict,
groups them by training_domain ("software" / "hardware"), and writes
a polished index.html into the output directory.

Usage:
    cd generators/
    python3 generate_index.py          # default output to ../output/ui_trainer/index.html
    python3 generate_index.py --out /path/to/index.html
"""

import argparse
import importlib
import sys
from pathlib import Path
from html import escape

# Ensure scenarios/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))


# ── Scenario discovery ───────────────────────────────────────────────────────

def discover_scenarios():
    """Import every scenario module and return list of metadata dicts."""
    scenario_dir = Path(__file__).resolve().parent / "scenarios"
    results = []

    for py_file in sorted(scenario_dir.glob("*.py")):
        name = py_file.stem
        if name.startswith("_") or name.startswith("base"):
            continue  # skip __init__, base.py, base_hardware.py

        mod_name = f"scenarios.{name}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"  ⚠ Skipping {mod_name}: {e}")
            continue

        S = getattr(mod, "SCENARIO", None)
        if not S:
            print(f"  ⚠ Skipping {mod_name}: no SCENARIO dict")
            continue

        mission = S.get("mission", {})
        branding = S.get("branding", {})

        results.append({
            "id":               S["id"],
            "title":            S["title"],
            "site":             S.get("site", ""),
            "role":             S.get("role", ""),
            "training_domain":  S.get("training_domain", "software"),
            "handling_profile": S.get("handling_profile") or S.get("training_domain", "software"),
            "steps":            len(S.get("tutorial", [])),
            "par_clicks":       mission.get("par_clicks", 0),
            "time_limit":       mission.get("time_limit", mission.get("time_limit_s", 0)),
            "difficulty":       _infer_difficulty(S),
            "tags":             _extract_tags(S),
            "accent_color":     branding.get("accent_color", "#E87600"),
            "shell_color":      branding.get("shell_color", "#033D80"),
            "level_names":      branding.get("level_names", []),
        })

    return results


def _infer_difficulty(S):
    """Rough difficulty label based on step count."""
    steps = len(S.get("tutorial", []))
    if steps <= 6:
        return "Beginner"
    elif steps <= 8:
        return "Intermediate"
    else:
        return "Advanced"


def _extract_tags(S):
    """Pull tags from the scenario or synthesise them from tutorial metadata."""
    if S.get("tags"):
        return S["tags"]

    hp = S.get("handling_profile", "")
    domain = S.get("training_domain", "software")

    if domain == "hardware":
        # Short keyword tags — NOT full step descriptions
        hw_tag_map = {
            "ar15_field_strip":    ["Safety check", "Takedown pins", "BCG removal", "Bolt disassembly"],
            "f150_trans_service":  ["Boot removal", "Eccentric stud", "Seal inspection", "Torque spec"],
        }
        sid = S.get("id", "")
        if sid in hw_tag_map:
            return hw_tag_map[sid]
        # Fallback: extract short keywords from step goals
        tags = []
        for step in S.get("tutorial", [])[:4]:
            goal = step.get("goal", "")
            # Take first 3 words as a keyword
            words = goal.split()[:3]
            if words:
                tags.append(" ".join(words))
        return tags[:4]

    # Software domain — profile-based tags
    tag_map = {
        "standard_dry":    ["Core workflow", "Standard receiving", "PO match", "Stock posting"],
        "perishable":      ["Batch / Lot", "Temp zone", "QI flag", "Cold chain"],
        "regulated_pharma":["Batch / Lot", "Expiry date", "Certificate of Analysis", "FDA audit trail"],
        "hazmat":          ["UN numbers", "Hazmat class", "Storage segregation", "SDS verification"],
        "serialized":      ["Serial capture", "Secure cage", "Manager approval", "Shrinkage prevention"],
    }
    return tag_map.get(hp, [])


# ── Color palette ────────────────────────────────────────────────────────────
# Stripe color encodes domain (SAP blue for software, safety orange for hardware).
# Badge colors are per-profile to identify the handling type.

DOMAIN_STRIPE = {
    "software": "#0070F2",   # SAP blue
    "hardware": "#FF8C00",   # safety orange
}

PROFILE_COLORS = {
    "standard_dry":    {"badge_bg": "#F3F4F6", "badge_fg": "#374151"},
    "perishable":      {"badge_bg": "#E0F0FF", "badge_fg": "#004A9E"},
    "regulated_pharma":{"badge_bg": "#E6F4EA", "badge_fg": "#0D652D"},
    "hazmat":          {"badge_bg": "#FDE8E8", "badge_fg": "#9B0000"},
    "serialized":      {"badge_bg": "#FFF4E5", "badge_fg": "#9A5700"},
    # Hardware
    "hardware":        {"badge_bg": "#FFF3E0", "badge_fg": "#BF6000"},
}

DEFAULT_COLORS = {"badge_bg": "#F3F4F6", "badge_fg": "#374151"}


# ── HTML generation ──────────────────────────────────────────────────────────

_DIFFICULTY_ORDER = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}


def generate_html(scenarios):
    """Return the full HTML string for the scenario selector."""
    software = sorted(
        [s for s in scenarios if s["training_domain"] == "software"],
        key=lambda s: _DIFFICULTY_ORDER.get(s["difficulty"], 9),
    )
    hardware = [s for s in scenarios if s["training_domain"] == "hardware"]

    cards_sw = "\n".join(_card_html(s) for s in software)
    cards_hw = "\n".join(_card_html(s) for s in hardware)

    total = len(scenarios)
    sw_count = len(software)
    hw_count = len(hardware)

    # Domain section headers
    sw_section = ""
    hw_section = ""

    if software:
        sw_section = f"""
    <div class="domain-section">
      <div class="domain-header">
        <div class="domain-icon sw">⚙</div>
        <div>
          <h2 class="domain-title">Software Training</h2>
          <p class="domain-sub">SAP MIGO Goods Receipt — {sw_count} scenario{"s" if sw_count != 1 else ""}</p>
        </div>
      </div>
      <div class="grid">
{cards_sw}
      </div>
    </div>
"""

    if hardware:
        hw_section = f"""
    <div class="domain-section">
      <div class="domain-header">
        <div class="domain-icon hw">🔧</div>
        <div>
          <h2 class="domain-title">Hardware Training</h2>
          <p class="domain-sub">Equipment Maintenance & Assembly — {hw_count} scenario{"s" if hw_count != 1 else ""}</p>
        </div>
      </div>
      <div class="grid">
{cards_hw}
      </div>
    </div>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zero-Touch Training — Scenario Selector</title>
<style>
  :root {{
    --sap-blue: #0070F2;
    --sap-shell: #033D80;
    --sap-grey-bg: #F4F6F8;
    --sap-amber: #E87600;
    --sap-green: #107E3E;
    --sap-red: #BB000B;
    --sap-text: #333;
    --sap-label: #666;
    --sap-border: #CCC;
    --hw-steel: #3C3C3C;
    --hw-orange: #FF8C00;
    --radius: 12px;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--sap-grey-bg);
    color: var(--sap-text);
    min-height: 100vh;
  }}

  /* ── Shell bar ─────────────────────────────── */
  .shell-bar {{
    background: var(--sap-shell);
    color: #fff;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .shell-bar h1 {{ font-size: 18px; font-weight: 600; letter-spacing: -0.3px; }}
  .shell-bar .badge {{
    background: var(--sap-amber);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  /* ── Page layout ───────────────────────────── */
  .page {{ max-width: 1100px; margin: 0 auto; padding: 40px 24px 80px; }}
  .page-title {{ font-size: 28px; font-weight: 700; margin-bottom: 6px; color: var(--sap-shell); }}
  .page-sub {{ font-size: 15px; color: var(--sap-label); margin-bottom: 36px; line-height: 1.5; }}

  /* ── Domain sections ───────────────────────── */
  .domain-section {{ margin-bottom: 40px; }}
  .domain-header {{
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 20px; padding-bottom: 14px;
    border-bottom: 2px solid #e0e4e8;
  }}
  .domain-icon {{
    width: 42px; height: 42px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
  }}
  .domain-icon.sw {{ background: #E0F0FF; }}
  .domain-icon.hw {{ background: #FFF3E0; }}
  .domain-title {{ font-size: 20px; font-weight: 700; color: var(--sap-shell); }}
  .domain-sub {{ font-size: 13px; color: var(--sap-label); margin-top: 2px; }}

  /* ── Scenario cards grid ───────────────────── */
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }}

  .card {{
    background: #fff;
    border: 1px solid var(--sap-border);
    border-radius: var(--radius);
    overflow: hidden;
    transition: box-shadow 0.2s, transform 0.15s;
    cursor: pointer;
    text-decoration: none;
    color: inherit;
    display: flex;
    flex-direction: column;
  }}
  .card:hover {{
    box-shadow: 0 8px 28px rgba(0,0,0,0.10);
    transform: translateY(-3px);
    border-color: var(--sap-blue);
  }}
  .card.hw:hover {{ border-color: var(--hw-orange); }}

  .card .stripe {{ height: 6px; }}

  .card-body {{ padding: 24px 24px 20px; flex: 1; display: flex; flex-direction: column; }}

  .card .profile-badge {{
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    padding: 3px 10px;
    border-radius: 4px;
    margin-bottom: 12px;
    align-self: flex-start;
  }}

  .card h2 {{ font-size: 17px; font-weight: 600; margin-bottom: 6px; line-height: 1.3; }}
  .card .site {{ font-size: 13px; color: var(--sap-label); margin-bottom: 2px; }}
  .card .role {{ font-size: 12px; color: var(--sap-text); font-weight: 600; margin-bottom: 14px; }}

  .card .meta {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 16px;
    font-size: 12px;
    margin-bottom: 16px;
  }}
  .card .meta dt {{ color: var(--sap-label); }}
  .card .meta dd {{ font-weight: 600; }}

  .card .tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: auto; }}
  .card .tag {{
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 4px;
    background: var(--sap-grey-bg);
    color: var(--sap-label);
    border: 1px solid #e0e0e0;
  }}

  .card .launch {{
    display: block;
    text-align: center;
    padding: 12px;
    background: var(--sap-grey-bg);
    font-size: 13px;
    font-weight: 600;
    color: var(--sap-blue);
    border-top: 1px solid #eee;
    transition: background 0.15s;
  }}
  .card.hw .launch {{ color: var(--hw-orange); }}
  .card:hover .launch {{ background: #e8f0fe; }}
  .card.hw:hover .launch {{ background: #fff3e0; }}

  /* ── Footer ────────────────────────────────── */
  .footer {{
    text-align: center;
    padding: 24px;
    font-size: 12px;
    color: var(--sap-label);
  }}
</style>
</head>
<body>

<div class="shell-bar">
  <h1>Zero-Touch Training</h1>
  <span class="badge">POC</span>
</div>

<div class="page">
  <h1 class="page-title">Scenario Packs</h1>
  <p class="page-sub">
    Each scenario has four levels that progressively remove guidance and add pressure.
    Start with a beginner scenario to learn the flow, then move to specialized handling profiles.
  </p>
{sw_section}{hw_section}</div>

<div class="footer">
  Zero-Touch Training POC · {total} Scenario{"s" if total != 1 else ""} · 4 Difficulty Levels · Open in any browser
</div>

</body>
</html>
"""


def _card_html(s):
    """Generate HTML for a single scenario card."""
    profile = s["handling_profile"]
    domain = s["training_domain"]
    colors = PROFILE_COLORS.get(profile, PROFILE_COLORS.get(domain, DEFAULT_COLORS))
    stripe_color = DOMAIN_STRIPE.get(domain, "#0070F2")
    hw_class = " hw" if domain == "hardware" else ""

    # Build profile badge label — specific, not generic
    badge_labels = {
        "standard_dry":     "Standard Dry",
        "perishable":       "Perishable / Cold Chain",
        "regulated_pharma": "Regulated Pharma / GxP",
        "hazmat":           "Hazmat / DOT-OSHA",
        "serialized":       "Serialized / High-Value",
    }
    # Hardware: use specific type labels instead of generic "Hardware"
    if domain == "hardware":
        hw_badge_map = {
            "ar15_field_strip":    "Firearms Maintenance",
            "f150_trans_service":  "Automotive Service",
        }
        badge_text = hw_badge_map.get(s["id"], "Equipment")
    else:
        badge_text = badge_labels.get(profile, profile.replace("_", " ").title())

    # Tags HTML
    tags_html = ""
    if s["tags"]:
        tag_spans = "\n          ".join(
            f'<span class="tag">{escape(t)}</span>' for t in s["tags"]
        )
        tags_html = f"""
        <div class="tags">
          {tag_spans}
        </div>"""

    time_str = f'{s["time_limit"]} s' if s["time_limit"] else "—"

    return f"""    <a class="card{hw_class}" href="{escape(s['id'])}/index.html">
      <div class="stripe" style="background:{stripe_color}"></div>
      <div class="card-body">
        <span class="profile-badge" style="background:{colors['badge_bg']};color:{colors['badge_fg']}">{escape(badge_text)}</span>
        <h2>{escape(s['title'])}</h2>
        <div class="site">{escape(s['site'])}</div>
        <div class="role">{escape(s['role'])}</div>
        <dl class="meta">
          <dt>Steps</dt><dd>{s['steps']}</dd>
          <dt>Par</dt><dd>{s['par_clicks']} clicks</dd>
          <dt>Time Limit</dt><dd>{time_str}</dd>
          <dt>Difficulty</dt><dd>{escape(s['difficulty'])}</dd>
        </dl>{tags_html}
      </div>
      <div class="launch">Launch Trainer →</div>
    </a>"""


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate the scenario selector index.html")
    parser.add_argument("--out", default=None,
                        help="Output path (default: ../output/ui_trainer/index.html)")
    args = parser.parse_args()

    out_path = Path(args.out) if args.out else (
        Path(__file__).resolve().parent.parent / "output" / "ui_trainer" / "index.html"
    )

    print("Discovering scenarios...")
    scenarios = discover_scenarios()
    print(f"  Found {len(scenarios)} scenario(s)")

    for s in scenarios:
        domain_label = "🔧 HW" if s["training_domain"] == "hardware" else "⚙ SW"
        print(f"    {domain_label}  {s['id']:30s}  {s['title']}")

    html = generate_html(scenarios)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"\n✓ Wrote {out_path}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
