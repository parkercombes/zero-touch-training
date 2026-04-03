#!/usr/bin/env python3
"""
capture_gr.py
Zero-Touch Training — ERPNext Goods Receipt Screen Capture Pipeline

Navigates ERPNext using Playwright, captures screenshots at each step
of the Purchase Receipt workflow, and writes them to:
  screens/         — clean screenshots (same as neutral for now)
  screens_neutral/ — clean screenshots (no overlays)

Usage (run from your Mac terminal, NOT the VM):
  pip install playwright
  playwright install chromium
  cd ~/Development/zero-touch-training/poc/capture
  python capture_gr.py --po PUR-ORD-2026-00011

Options:
  --po      Purchase Order number to use  (default: PUR-ORD-2026-00011)
  --config  Path to config YAML           (default: capture_config.yaml)
  --out     Override output directory
  --headed  Show browser window (useful for debugging)
  --slow    Slow down actions by N ms     (default: 0)
"""

import argparse
import os
import shutil
import sys
import time
from pathlib import Path

import yaml

# ── Playwright import with helpful error ──────────────────────────────────────
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("\n❌  Playwright not installed.")
    print("    Run:  pip install playwright && playwright install chromium\n")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def log(msg: str):
    print(f"  {msg}")


def dismiss_popups(page):
    """Close any 'Getting Started' or tour popups that block interaction."""
    selectors = [
        ".getting-started .close",
        ".widget-head .close",
        ".modal-dialog .close",
        "[data-dismiss='modal']",
        "button.close",
    ]
    for sel in selectors:
        try:
            els = page.query_selector_all(sel)
            for el in els:
                if el.is_visible():
                    el.click()
                    page.wait_for_timeout(300)
        except Exception:
            pass


def wait_for_page(page, settle_ms: int = 1200):
    """Wait for ERPNext's JS to settle after navigation."""
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except PWTimeout:
        pass  # networkidle can time out on slow machines — just continue
    page.wait_for_timeout(settle_ms)
    dismiss_popups(page)


def scroll_to(page, selector: str | None):
    if not selector:
        return
    try:
        el = page.query_selector(selector)
        if el:
            el.scroll_into_view_if_needed()
            page.wait_for_timeout(400)
    except Exception:
        pass


def apply_highlight(page, selector: str | None):
    """Inject a temporary amber outline onto a form element."""
    if not selector:
        return
    try:
        page.evaluate(f"""
            (() => {{
                const el = document.querySelector({repr(selector)});
                if (el) {{
                    el.style.outline = '3px solid #E8A000';
                    el.style.outlineOffset = '2px';
                    el.style.borderRadius = '3px';
                }}
            }})()
        """)
    except Exception:
        pass


def remove_highlights(page):
    """Strip any outlines added by apply_highlight."""
    try:
        page.evaluate("""
            document.querySelectorAll('*').forEach(el => {
                if (el.style.outline && el.style.outline.includes('E8A000')) {
                    el.style.outline = '';
                    el.style.outlineOffset = '';
                }
            });
        """)
    except Exception:
        pass


def screenshot(page, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(path), full_page=False)
    log(f"  📸  {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────────────────────

def login(page, base_url: str, username: str, password: str):
    log("Logging in to ERPNext...")
    page.goto(f"{base_url}/login")
    wait_for_page(page, 800)

    # Fill credentials
    page.fill("#login_email", username)
    page.fill("#login_password", password)
    page.click(".btn-login, [data-label='Login'], button[type='submit']")
    wait_for_page(page, 2000)

    # Handle first-login password change prompt if present
    if "update-password" in page.url or page.query_selector("#new_password"):
        log("  First-login password prompt detected — skipping (use --headed to handle manually)")

    log("  ✓ Logged in")


# ─────────────────────────────────────────────────────────────────────────────
# Navigate to Purchase Receipt via PO → Create
# ─────────────────────────────────────────────────────────────────────────────

def open_purchase_receipt_from_po(page, base_url: str, po_number: str, settle_ms: int):
    """
    Open a PO, click Create → Purchase Receipt, and return.
    Returns the URL of the new Purchase Receipt draft.
    """
    log(f"Opening Purchase Order {po_number}...")
    page.goto(f"{base_url}/desk/purchase-order/{po_number}")
    wait_for_page(page, settle_ms)
    dismiss_popups(page)

    # Click the Create split-button (dropdown toggle arrow, not the label)
    log("  Clicking Create button...")
    try:
        page.click(".page-actions .btn-group.dropdown .dropdown-toggle", timeout=5000)
    except PWTimeout:
        try:
            # ERPNext sometimes renders it differently — try the caret icon
            page.click(".page-actions .btn-split-open", timeout=3000)
        except PWTimeout:
            # Last resort: use JS to find and click the dropdown toggle
            page.evaluate("""
                const btns = [...document.querySelectorAll('.page-actions button')];
                const create = btns.find(b => b.textContent.trim().startsWith('Create'));
                const toggle = create && create.closest('.btn-group') &&
                               create.closest('.btn-group').querySelector('.dropdown-toggle');
                if (toggle) toggle.click();
                else if (create) create.click();
            """)

    page.wait_for_timeout(600)

    # Click "Purchase Receipt" — scoped to the open dropdown menu only
    log("  Selecting Purchase Receipt...")
    try:
        # ERPNext dropdown items live in .dropdown-menu li a
        page.click(".dropdown-menu li a:has-text('Purchase Receipt')", timeout=5000)
    except PWTimeout:
        try:
            # Alternative: data-label attribute
            page.click(".dropdown-menu [data-label='Purchase Receipt']", timeout=3000)
        except PWTimeout:
            # JS fallback: find the anchor by exact text inside the open dropdown
            page.evaluate("""
                const links = [...document.querySelectorAll('.dropdown-menu a')];
                const pr = links.find(a => a.textContent.trim() === 'Purchase Receipt');
                if (pr) pr.click();
            """)
            page.wait_for_timeout(500)

    wait_for_page(page, settle_ms)
    dismiss_popups(page)

    pr_url = page.url
    log(f"  ✓ Purchase Receipt draft opened: {pr_url}")
    return pr_url


# ─────────────────────────────────────────────────────────────────────────────
# Main capture loop
# ─────────────────────────────────────────────────────────────────────────────

def run_capture(config: dict, po_number: str, out_dir: Path, headed: bool, slow_mo: int):

    erpnext_cfg = config["erpnext"]
    cap_cfg     = config["capture"]
    base_url    = erpnext_cfg["base_url"].rstrip("/")
    settle_ms   = cap_cfg.get("settle_ms", 1200)
    vp          = cap_cfg.get("viewport", {"width": 1440, "height": 900})

    screens_dir         = out_dir / "screens"
    screens_neutral_dir = out_dir / "screens_neutral"
    screens_dir.mkdir(parents=True, exist_ok=True)
    screens_neutral_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headed, slow_mo=slow_mo)
        ctx     = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
        page    = ctx.new_page()

        # ── Login ────────────────────────────────────────────────────────────
        login(page, base_url, erpnext_cfg["username"], erpnext_cfg["password"])

        # ── Screen loop ──────────────────────────────────────────────────────
        # The PR draft is created inline when the screen loop hits the
        # "create_pr" action (after capturing the PO detail screen).
        captured_count = 0

        for screen in config["screens"]:
            name      = screen["name"]
            title     = screen.get("title", name)
            action    = screen.get("action", "wait")
            highlight = screen.get("highlight")

            print(f"\n▶  {name}  —  {title}")

            try:
                # ── create_pr: transition step (no screenshot) ───────────────
                if action == "create_pr":
                    log("  Creating Purchase Receipt from current PO...")
                    pr_url = open_purchase_receipt_from_po(
                        page, base_url, po_number, settle_ms
                    )
                    log(f"  ✓ Now on Purchase Receipt: {pr_url}")
                    continue   # no screenshot for transition steps

                # ── navigate: go to a URL ────────────────────────────────────
                elif action == "navigate":
                    url = screen["url"].format(
                        base_url=base_url,
                        po_number=po_number,
                    )
                    page.goto(url)
                    wait_for_page(page, settle_ms)
                    dismiss_popups(page)

                # ── wait: stay on current page ───────────────────────────────
                elif action == "wait":
                    wait_for_page(page, settle_ms)
                    dismiss_popups(page)

                # ── click: click a selector ──────────────────────────────────
                elif action == "click":
                    sel = screen.get("selector", "")
                    try:
                        page.click(sel, timeout=4000)
                        wait_for_page(page, settle_ms)
                        dismiss_popups(page)
                    except PWTimeout:
                        log(f"  ⚠️  Selector not found: {sel} — taking screenshot anyway")

                # ── fill: type into a field ──────────────────────────────────
                elif action == "fill":
                    sel = screen.get("selector", "")
                    val = screen.get("value", "")
                    try:
                        page.fill(sel, val)
                        page.keyboard.press("Enter")
                        wait_for_page(page, settle_ms)
                        dismiss_popups(page)
                    except PWTimeout:
                        log(f"  ⚠️  Fill target not found: {sel}")

                # Scroll into view if requested
                scroll_to(page, screen.get("scroll_to"))

                # ── Neutral screenshot (no highlight) ─────────────────────────
                neutral_path = screens_neutral_dir / f"{name}.png"
                screenshot(page, neutral_path)

                # ── Highlighted screenshot ────────────────────────────────────
                if highlight:
                    apply_highlight(page, highlight)
                    page.wait_for_timeout(150)

                screens_path = screens_dir / f"{name}.png"
                screenshot(page, screens_path)

                if highlight:
                    remove_highlights(page)

                captured_count += 1

            except Exception as e:
                log(f"  ❌  Error on screen '{name}': {e}")
                # Still try to save whatever's on screen for debugging
                try:
                    err_path = out_dir / f"_error_{name}.png"
                    page.screenshot(path=str(err_path))
                    log(f"     Error screenshot saved: {err_path.name}")
                except Exception:
                    pass

        browser.close()

    print(f"\n✅  Capture complete.")
    print(f"    screens/         → {screens_dir}")
    print(f"    screens_neutral/ → {screens_neutral_dir}")
    print(f"    {captured_count} screens captured.\n")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ERPNext Goods Receipt screen capture")
    parser.add_argument("--po",     default="PUR-ORD-2026-00011",
                        help="Purchase Order number (default: PUR-ORD-2026-00011)")
    parser.add_argument("--config", default="capture_config.yaml",
                        help="Path to YAML config file")
    parser.add_argument("--out",    default=None,
                        help="Override output directory")
    parser.add_argument("--headed", action="store_true",
                        help="Show browser window (useful for debugging)")
    parser.add_argument("--slow",   type=int, default=0,
                        help="Slow down actions by N ms (default: 0)")
    args = parser.parse_args()

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌  Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Resolve output directory
    if args.out:
        out_dir = Path(args.out)
    else:
        raw_out = config["capture"].get("output_dir", "../output/ui_trainer/standard_dry_gr")
        out_dir = (config_path.parent / raw_out).resolve()

    print(f"\n🎬  Zero-Touch Training — ERPNext Capture")
    print(f"    PO:     {args.po}")
    print(f"    Output: {out_dir}")
    print(f"    Headed: {args.headed}\n")

    run_capture(config, args.po, out_dir, args.headed, args.slow)


if __name__ == "__main__":
    main()
