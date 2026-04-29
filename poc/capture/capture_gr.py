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
    """Close any modal dialogs that block interaction.

    The 'Getting Started' / onboarding widget should be disabled in ERPNext
    admin settings rather than dismissed at capture time. This function only
    handles unexpected modals that might still appear.
    """
    selectors = [
        ".modal-dialog .close",
        "[data-dismiss='modal']",
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
    """Inject a temporary amber outline onto a form element.

    The selector string can be a CSS selector (comma-separated fallbacks work
    natively with querySelector).  If no match is found the function logs a
    warning so the capture log shows which selectors need adjusting.

    A short wait_for_selector is attempted first so that late-rendering
    elements (e.g. page-actions toolbar) have time to appear.
    """
    if not selector:
        return
    try:
        # Wait up to 3 s for at least one sub-selector to appear in the DOM.
        # Comma-separated selectors are valid in wait_for_selector.
        try:
            page.wait_for_selector(selector, state="attached", timeout=3000)
        except PWTimeout:
            pass  # fall through — the evaluate below will log the miss

        matched = page.evaluate(f"""
            (() => {{
                const el = document.querySelector({repr(selector)});
                if (el) {{
                    el.style.outline = '3px solid #E8A000';
                    el.style.outlineOffset = '2px';
                    el.style.borderRadius = '3px';
                    return el.tagName + '.' + (el.className || '').toString().slice(0, 60);
                }}
                return null;
            }})()
        """)
        if matched:
            log(f"  🎯  Highlight matched: {matched}")
        else:
            log(f"  ⚠️  No element matched highlight selector: {selector}")
    except Exception as e:
        log(f"  ⚠️  Highlight error: {e}")


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
# Disable onboarding (Getting Started popup)
# ─────────────────────────────────────────────────────────────────────────────

def disable_onboarding(page, base_url: str):
    """Kill the Getting Started / onboarding popup in ERPNext v16.

    ERPNext v16 has a known regression where the System Settings toggle
    alone doesn't prevent the popup from reappearing in fresh browser
    sessions (like Playwright contexts).  This function hits it from
    three angles:

      1. System Settings — set enable_onboarding = 0 via Frappe API
      2. Module onboarding — mark all Onboarding Step records as
         skipped/complete so the per-module widget has nothing to show
      3. CSS injection — register a page-level style that hides any
         onboarding widget that still leaks through (belt and suspenders)

    The CSS injection is added via page.add_init_script so it persists
    across navigations within this Playwright context.
    """
    log("Killing onboarding popup (3-layer approach)...")

    # ── Layer 1: System Settings toggle ──────────────────────────────────
    page.goto(f"{base_url}/desk/system-settings")
    wait_for_page(page, 1500)
    try:
        result = page.evaluate("""
            (async () => {
                await frappe.call({
                    method: 'frappe.client.set_value',
                    args: {
                        doctype: 'System Settings',
                        name: 'System Settings',
                        fieldname: 'enable_onboarding',
                        value: 0
                    }
                });
                return 'ok';
            })()
        """)
        log("  ✓ Layer 1: enable_onboarding set to 0")
    except Exception as e:
        log(f"  ⚠️  Layer 1 failed: {e}")

    # ── Layer 2: Bulk-skip all Onboarding Step records ───────────────────
    try:
        skipped = page.evaluate("""
            (async () => {
                const steps = await frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Onboarding Step',
                        filters: { is_skipped: 0, is_complete: 0 },
                        fields: ['name'],
                        limit_page_length: 0
                    }
                });
                const names = (steps.message || steps || []).map(s => s.name);
                for (const name of names) {
                    await frappe.call({
                        method: 'frappe.client.set_value',
                        args: {
                            doctype: 'Onboarding Step',
                            name: name,
                            fieldname: 'is_skipped',
                            value: 1
                        }
                    });
                }
                return names.length;
            })()
        """)
        log(f"  ✓ Layer 2: {skipped} onboarding step(s) marked skipped")
    except Exception as e:
        log(f"  ⚠️  Layer 2 failed: {e}")

    # ── Layer 3: CSS kill switch — persists across navigations ───────────
    page.add_init_script("""
        (() => {
            const style = document.createElement('style');
            style.textContent = `
                .onboarding-widget,
                .onboarding-widget-box,
                .getting-started,
                .widget.onboarding-widget-box,
                [data-widget-name*="onboarding" i],
                [data-widget-name*="getting-started" i],
                [data-widget-name*="setup" i] {
                    display: none !important;
                    visibility: hidden !important;
                    height: 0 !important;
                    overflow: hidden !important;
                }
            `;
            if (document.head) {
                document.head.appendChild(style);
            } else {
                document.addEventListener('DOMContentLoaded', () => {
                    document.head.appendChild(style);
                });
            }
        })();
    """)
    log("  ✓ Layer 3: CSS kill switch injected for all future navigations")

    page.wait_for_timeout(300)


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

        # ── Disable onboarding so the Getting Started popup never appears ──
        disable_onboarding(page, base_url)

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
