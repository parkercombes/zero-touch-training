"""
scenarios/standard_dry.py — Standard Dry Goods: Goods Receipt in SAP MIGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Handling profile: STANDARD DRY (no batch, no temperature zone, no QI)
  - Batch/lot number NOT required
  - Temperature zone NOT required (single storage location WH-01)
  - Quality Inspection flag NOT required
  - Movement type: 101
  - Simplest GR workflow for non-hazardous, non-perishable goods

To adapt for a different warehouse:
  1. Copy this file (e.g. hazmat_gr.py, electronics_gr.py)
  2. Update SCENARIO metadata (id, title, site, role, handling_profile)
  3. Update tutorial steps (goals, instructions, hints, hotspots, feedback)
  4. Update generate_screens() to show your site's field values & highlights
  5. Run: python3 ui_trainer.py scenarios/your_scenario
"""

from pathlib import Path
from PIL import Image, ImageDraw

from scenarios.base import (
    W, H, fnt, new_screen, placeholder_note,
    draw_shell_bar, draw_subheader, draw_card, draw_field, draw_dropdown,
    draw_button, draw_table_header, draw_table_row, draw_checkbox,
    draw_status_banner,
    SAP_BLUE, SAP_SHELL, SAP_GREY_BG, SAP_WHITE, SAP_BORDER,
    SAP_TEXT, SAP_LABEL, SAP_AMBER, SAP_GREEN, SAP_RED,
)

# ── Scenario definition ───────────────────────────────────────────────────────
# handling_profile drives mission scoring weights and briefing emphasis.
# Valid values: "standard_dry" | "perishable" | "regulated_pharma" | "hazmat" | "serialized"

SCENARIO = {
    "id":               "standard_dry_gr",
    "title":            "Goods Receipt in SAP MIGO",
    "site":             "Apex Auto Parts DC · Memphis, TN",
    "role":             "Receiving Associate",
    "handling_profile": "standard_dry",
    "tutorial": [
        {
            "screen":      "fiori_home.png",
            "goal":        "Open the MIGO transaction",
            "instruction": "Click the MIGO tile to open Goods Movement.",
            "hint":        "Look for the 'Goods Movement (MIGO)' tile — it has a star icon.",
            "hotspot":     {"x": 473, "y": 162, "w": 200, "h": 130},
            "feedback":    "Nice! MIGO is open. Now let's configure your Goods Receipt.",
        },
        {
            "screen":      "migo_action.png",
            "goal":        "Set the action to Goods Receipt",
            "instruction": "Confirm the Action dropdown is set to 'Goods Receipt'. Click it.",
            "hint":        "The Action dropdown is the first field in the transaction header.",
            "hotspot":     {"x": 36, "y": 148, "w": 220, "h": 36},
            "feedback":    "Correct. Action = Goods Receipt. Now set the reference type.",
        },
        {
            "screen":      "migo_reference.png",
            "goal":        "Set the reference document to Purchase Order",
            "instruction": "Click the Reference Document dropdown and select 'Purchase Order'.",
            "hint":        "The Reference Document dropdown is next to the Action dropdown.",
            "hotspot":     {"x": 280, "y": 148, "w": 220, "h": 36},
            "feedback":    "Good. Every GR at Apex must be tied to a PO.",
        },
        {
            "screen":      "migo_po.png",
            "goal":        "Enter the Purchase Order number",
            "instruction": "Type the PO number into the Purchase Order No. field and press Enter.",
            "hint":        "The PO number field is to the right of the Reference Document dropdown.",
            "hotspot":     {"x": 524, "y": 148, "w": 200, "h": 36},
            "feedback":    "PO 4500098712 loaded. SAP pulled in the line items automatically.",
        },
        {
            "screen":      "migo_items.png",
            "goal":        "Verify line item quantities",
            "instruction": "Check the Qty column. Confirm it matches what's physically on your dock.",
            "hint":        "Compare each quantity against your delivery paperwork before proceeding.",
            "hotspot":     {"x": 450, "y": 272, "w": 100, "h": 34},
            "feedback":    "Quantities verified. If anything is short, update it now — not after posting.",
        },
        {
            "screen":      "migo_post.png",
            "goal":        "Post the Goods Receipt",
            "instruction": "Click the Post button to complete the Goods Receipt.",
            "hint":        "Review the summary first. Once you post, SAP generates the material document.",
            "hotspot":     {"x": 20, "y": 88, "w": 80, "h": 32},
            "feedback":    "Posted! Material document created. Inventory updated. Receiving complete.",
        },
    ],
    "mission": {
        "title":      "Your Mission",
        "briefing": (
            "Post a Goods Receipt for PO 4500098712.\n"
            "200 units of oil filter (AP-3310) and 150 sets of brake pads (AP-7721)\n"
            "arriving at Apex Auto Parts DC, Memphis TN. No special handling required."
        ),
        "par_clicks": 8,
    },
}


# ── Screen generators ─────────────────────────────────────────────────────────
# Each function returns a PIL Image for one step in the tutorial sequence.
# The highlighted element matches the hotspot in SCENARIO["tutorial"] above.

def _header_row(d, action="Goods Receipt", reference="Purchase Order",
                po="", hl_action=False, hl_ref=False, hl_po=False):
    """Reusable MIGO transaction header strip (y=90–200)."""
    draw_card(d, 20, 90, W - 20, 200, title="Transaction Header")
    draw_dropdown(d, 36,  148, 220, 36, "Action",                action,    highlight=hl_action)
    draw_dropdown(d, 280, 148, 220, 36, "Reference Document",    reference, highlight=hl_ref)
    draw_field(   d, 524, 148, 200, 36, "Purchase Order No.",    po,        highlight=hl_po)
    draw_button(  d, 744, 148,  80, 36, "Execute")


def _items_table(d, highlight_col=None):
    """Reusable MIGO line items table (y=210+) — no Batch column for standard_dry."""
    d.text((36, 216), "Line Items", font=fnt(14, bold=True), fill=SAP_TEXT)
    cols = [("Item", 60), ("Material", 120), ("Description", 200),
            ("Qty", 100), ("UoM", 70), ("S.Loc", 100)]
    draw_table_header(d, 36, 240, cols)
    draw_table_row(d, 36, 272, cols,
                   ["0001", "AP-3310", "Oil Filter 10W30 Case", "200", "UN", "WH-01"],
                   highlight_col=highlight_col)
    draw_table_row(d, 36, 306, cols,
                   ["0002", "AP-7721", "Brake Pads Organic Disc", "150", "SET", "WH-01"],
                   highlight_col=None)


def screen_fiori_home():
    img, d = new_screen("SAP Fiori Launchpad")
    tiles = [
        ("Purchase\nRequisition", False),  ("Goods\nMovement\n(MIGO)", True),
        ("Inventory\nManagement", False),  ("Vendor\nInvoice",          False),
        ("Purchase\nOrder",       False),  ("Receiving\nDock",          False),
    ]
    tw, th, gap = 200, 130, 24
    start_x = (W - (3 * tw + 2 * gap)) // 2
    start_y = 100
    for i, (label, highlight) in enumerate(tiles):
        col, row = i % 3, i // 3
        x = start_x + col * (tw + gap)
        y = start_y + row * (th + gap)
        border = SAP_AMBER if highlight else SAP_BORDER
        bg = (255, 248, 235) if highlight else SAP_WHITE
        d.rounded_rectangle([x, y, x + tw, y + th], radius=6,
                             fill=bg, outline=border, width=2 if highlight else 1)
        icon_col = SAP_AMBER if highlight else SAP_BLUE
        d.rounded_rectangle([x + tw // 2 - 20, y + 18, x + tw // 2 + 20, y + 58],
                             radius=4, fill=icon_col)
        for j, line in enumerate(label.split("\n")):
            d.text((x + tw // 2 - 40, y + 68 + j * 18), line,
                   font=fnt(13, bold=highlight), fill=SAP_TEXT)
        if highlight:
            d.text((x + 6, y + 6), "★", font=fnt(12), fill=SAP_AMBER)
    placeholder_note(d)
    return img


def screen_migo_action():
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, hl_action=True)
    placeholder_note(d)
    return img


def screen_migo_reference():
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, hl_ref=True)
    placeholder_note(d)
    return img


def screen_migo_po():
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500098712", hl_po=True)
    placeholder_note(d)
    return img


def screen_migo_items():
    img, d = new_screen("Goods Movement (MIGO) — PO 4500098712")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500098712")
    _items_table(d, highlight_col=3)   # Qty column highlighted
    placeholder_note(d)
    return img


def screen_migo_post():
    img, d = new_screen("Goods Movement (MIGO) — Ready to Post")
    draw_subheader(d, "Goods Movement > MIGO")
    # Toolbar with Post highlighted
    d.rectangle([0, 80, W, 116], fill=(248, 250, 252))
    d.line([(0, 116), (W, 116)], fill=SAP_BORDER, width=1)
    draw_button(d, 20,  88, 80, 32, "Post",   primary=True,  highlight=True)
    draw_button(d, 112, 88, 80, 32, "Check",  primary=False)
    draw_button(d, 204, 88, 80, 32, "Cancel", primary=False)
    # Summary card
    draw_card(d, 20, 126, W - 20, 340, title="Ready to Post — Summary")
    summary = [
        ("Action",             "Goods Receipt against Purchase Order"),
        ("Purchase Order",     "4500098712"),
        ("Vendor",             "Apex Supply Co"),
        ("Line Items",         "2 items"),
        ("Storage Location",   "WH-01 (Main Warehouse)"),
        ("Batch Tracking",     "Not required (standard dry goods)"),
    ]
    sy = 166
    for label, value in summary:
        d.text((36, sy),  label + ":", font=fnt(12, bold=True), fill=SAP_LABEL)
        d.text((220, sy), value,       font=fnt(12),             fill=SAP_TEXT)
        sy += 24
    draw_status_banner(d, "All validations passed. Click Post to complete the Goods Receipt.")
    placeholder_note(d)
    return img


# ── Screen registry ───────────────────────────────────────────────────────────
# Maps filename → generator function. ui_trainer.py calls generate_screens().

SCREEN_GENERATORS = {
    "fiori_home.png":     screen_fiori_home,
    "migo_action.png":    screen_migo_action,
    "migo_reference.png": screen_migo_reference,
    "migo_po.png":        screen_migo_po,
    "migo_items.png":     screen_migo_items,
    "migo_post.png":      screen_migo_post,
}


def generate_screens(screens_dir: Path):
    """Generate all placeholder PNGs into screens_dir. Called by ui_trainer.py."""
    screens_dir.mkdir(parents=True, exist_ok=True)
    for fname, fn in SCREEN_GENERATORS.items():
        fn().save(str(screens_dir / fname), "PNG")
    return list(SCREEN_GENERATORS.keys())
