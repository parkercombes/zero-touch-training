"""
scenarios/hazmat.py — ChemCo Industrial DC: Hazmat Goods Receipt in SAP MIGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Handling profile: HAZMAT
  - UN number mandatory (identifies chemical substance)
  - Hazmat class assignment required (Flammable, Corrosive, etc.)
  - Storage location (hazmat bay) assignment required
  - Emergency contact verification required
  - SDS (Safety Data Sheet) verification required
  - DOT/OSHA compliance

To adapt for a different hazmat warehouse:
  1. Copy this file (e.g. pharma_hazmat.py, lithium_hazmat.py)
  2. Update SCENARIO metadata (id, title, site, role, handling_profile)
  3. Update tutorial steps (goals, instructions, hints, hotspots, feedback)
  4. Update generate_screens() to show your site's materials, UN numbers, storage bays
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
    "id":               "hazmat_gr",
    "title":            "Hazmat Goods Receipt in SAP MIGO",
    "site":             "ChemCo Industrial DC · Houston, TX",
    "role":             "Receiving Associate",
    "handling_profile": "hazmat",
    "tutorial": [
        {
            "screen":      "fiori_home.png",
            "goal":        "Open the MIGO transaction",
            "instruction": "Click the MIGO tile to open Goods Movement.",
            "hint":        "Look for the 'Goods Movement (MIGO)' tile — it has an amber highlight for hazmat.",
            "hotspot":     {"x": 473, "y": 162, "w": 200, "h": 130},
            "feedback":    "Nice! MIGO is open. Now let's configure your hazmat Goods Receipt.",
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
            "feedback":    "Good. Every hazmat GR at ChemCo must be tied to a PO.",
        },
        {
            "screen":      "migo_po.png",
            "goal":        "Enter the Purchase Order number",
            "instruction": "Type the PO number into the Purchase Order No. field and press Enter.",
            "hint":        "The PO number field is to the right of the Reference Document dropdown.",
            "hotspot":     {"x": 524, "y": 148, "w": 200, "h": 36},
            "feedback":    "PO 4500033900 loaded. SAP pulled in the chemical line items automatically.",
        },
        {
            "screen":      "migo_items.png",
            "goal":        "Verify line item quantities and check UN numbers",
            "instruction": "Check the Qty column and UN No. column. Confirm the chemicals match the packing list.",
            "hint":        "Compare each quantity and UN number against your delivery paperwork before proceeding.",
            "hotspot":     {"x": 450, "y": 272, "w": 100, "h": 34},
            "feedback":    "Quantities and UN numbers verified. Never post hazmat without confirming UN classification.",
        },
        {
            "screen":      "migo_un.png",
            "goal":        "Enter the UN number and hazmat class in item detail",
            "instruction": "Click the UN Number field and verify the hazmat class assignment.",
            "hint":        "UN Number field is mandatory for all hazmat. The hazmat class dropdown must match the SDS.",
            "hotspot":     {"x": 260, "y": 210, "w": 180, "h": 34},
            "feedback":    "UN number and hazmat class confirmed. SDS on file verified.",
        },
        {
            "screen":      "migo_storage_class.png",
            "goal":        "Assign to correct hazmat storage bay",
            "instruction": "Click the Storage Location dropdown and select the appropriate hazmat bay.",
            "hint":        "Flammable chemicals → HAZ-A · Corrosive chemicals → HAZ-B · Segregation rules apply.",
            "hotspot":     {"x": 260, "y": 210, "w": 220, "h": 34},
            "feedback":    "Storage location set to hazmat bay. Incompatible materials kept separate.",
        },
        {
            "screen":      "migo_post.png",
            "goal":        "Post the Goods Receipt",
            "instruction": "Review the summary. Confirm UN numbers and emergency contact. Click Post.",
            "hint":        "Emergency contact (1-800-DOT-HELP) must be on file before posting hazmat.",
            "hotspot":     {"x": 20, "y": 88, "w": 80, "h": 32},
            "feedback":    "Posted! Material document created. Hazmat inventory updated. Emergency contact confirmed.",
        },
    ],
    "mission": {
        "title":      "Your Mission",
        "briefing": (
            "Post a Goods Receipt for PO 4500033900.\n"
            "Acetone (CH-1101, 10 drums, UN1090, Class 3 Flammable) "
            "and Hydrochloric Acid 37% (CH-2205, 20 carboys, UN1789, Class 8 Corrosive) "
            "arriving at ChemCo Industrial DC, Houston TX.\n"
            "UN numbers and hazmat classes mandatory. Storage bay assignment required. "
            "Emergency contact 1-800-DOT-HELP on file."
        ),
        "par_clicks": 12,
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
    """Reusable MIGO hazmat line items table (y=210+) with UN numbers."""
    d.text((36, 216), "Line Items", font=fnt(14, bold=True), fill=SAP_TEXT)
    cols = [("Item", 60), ("Material", 120), ("Description", 180),
            ("Qty", 80), ("UoM", 60), ("UN No.", 100), ("Haz.Class", 100)]
    draw_table_header(d, 36, 240, cols)
    draw_table_row(d, 36, 272, cols,
                   ["0001", "CH-1101", "Acetone 55-gal drums", "10", "DR", "UN1090", "Class 3"],
                   highlight_col=highlight_col)
    draw_table_row(d, 36, 306, cols,
                   ["0002", "CH-2205", "HCl 37% 30L carboys", "20", "CB", "UN1789", "Class 8"],
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
    _header_row(d, po="4500033900", hl_po=True)
    placeholder_note(d)
    return img


def screen_migo_items():
    img, d = new_screen("Goods Movement (MIGO) — PO 4500033900")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500033900")
    _items_table(d, highlight_col=3)   # Qty column highlighted
    placeholder_note(d)
    return img


def screen_migo_un():
    img, d = new_screen("Goods Movement (MIGO) — Item Detail")
    draw_subheader(d, "Goods Movement > MIGO")
    draw_card(d, 20, 90, W - 20, 560,
              title="Item Detail — Line 0001: CH-1101 Acetone 55-gal drums")
    # Tabs
    tabs = ["Where", "Quantity", "Material", "Account Assignment", "Purchase Order"]
    tx = 36
    for i, tab in enumerate(tabs):
        active = (i == 2)
        bg = SAP_WHITE if active else SAP_GREY_BG
        d.rectangle([tx, 126, tx + len(tab) * 8 + 20, 150], fill=bg, outline=SAP_BORDER, width=1)
        if active:
            d.rectangle([tx, 148, tx + len(tab) * 8 + 20, 150], fill=SAP_BLUE)
        d.text((tx + 8, 132), tab,
               font=fnt(12, bold=active), fill=SAP_BLUE if active else SAP_LABEL)
        tx += len(tab) * 8 + 28
    d.line([(36, 150), (W - 36, 150)], fill=SAP_BORDER, width=1)
    d.text((36, 170), "Material Tab — Hazmat Classification",
           font=fnt(13, bold=True), fill=SAP_LABEL)
    draw_field(d, 36,  210, 200, 34, "Material Number",      "CH-1101")
    draw_field(d, 260, 210, 180, 34, "UN Number",            "UN1090", highlight=True)
    draw_dropdown(d, 460, 210, 180, 34, "Hazmat Class",      "Class 3 Flammable")
    draw_checkbox(d, 36, 278, "SDS Verified",                checked=True, highlight=False)
    draw_status_banner(d, "⚠ Hazmat item — UN number mandatory before posting", ok=False)
    placeholder_note(d)
    return img


def screen_migo_storage_class():
    img, d = new_screen("Goods Movement (MIGO) — Item Detail")
    draw_subheader(d, "Goods Movement > MIGO")
    draw_card(d, 20, 90, W - 20, 560,
              title="Item Detail — Line 0001: CH-1101 Acetone 55-gal drums")
    # Tabs
    tabs = ["Where", "Quantity", "Material", "Account Assignment", "Purchase Order"]
    tx = 36
    for i, tab in enumerate(tabs):
        active = (i == 0)
        bg = SAP_WHITE if active else SAP_GREY_BG
        d.rectangle([tx, 126, tx + len(tab) * 8 + 20, 150], fill=bg, outline=SAP_BORDER, width=1)
        if active:
            d.rectangle([tx, 148, tx + len(tab) * 8 + 20, 150], fill=SAP_BLUE)
        d.text((tx + 8, 132), tab,
               font=fnt(12, bold=active), fill=SAP_BLUE if active else SAP_LABEL)
        tx += len(tab) * 8 + 28
    d.line([(36, 150), (W - 36, 150)], fill=SAP_BORDER, width=1)
    d.text((36, 170), "Where Tab — Storage & Hazmat Assignment", font=fnt(13, bold=True), fill=SAP_LABEL)
    draw_field(   d, 36,  210, 200, 34, "Plant",            "HC01")
    draw_dropdown(d, 260, 210, 220, 34, "Storage Location", "HAZ-A (Flammable)", highlight=True)
    draw_field(   d, 504, 210, 200, 34, "Movement Type",    "101")
    draw_field(   d, 36,  278, 200, 34, "Vendor",           "NovoChem Supply")
    draw_field(   d, 260, 278, 220, 34, "Delivery Note",    "DN-20240215")
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
    draw_card(d, 20, 126, W - 20, 420, title="Ready to Post — Hazmat Summary")
    summary = [
        ("Action",             "Goods Receipt against Purchase Order"),
        ("Purchase Order",     "4500033900"),
        ("Line Items",         "2 hazmat items"),
        ("UN Numbers",         "UN1090 (Acetone), UN1789 (HCl 37%)"),
        ("Hazmat Classes",     "Class 3 (Flammable), Class 8 (Corrosive)"),
        ("Storage Locations",  "HAZ-A (Flammable), HAZ-B (Corrosive)"),
        ("Emergency Contact",  "✓ 1-800-DOT-HELP on file"),
    ]
    sy = 166
    for label, value in summary:
        d.text((36, sy),  label + ":",  font=fnt(12, bold=True), fill=SAP_LABEL)
        d.text((220, sy), value,        font=fnt(12),             fill=SAP_TEXT)
        sy += 24
    draw_status_banner(d, "✓ All hazmat validations passed. UN numbers, classes, and emergency contact confirmed.")
    placeholder_note(d)
    return img


# ── Screen registry ───────────────────────────────────────────────────────────
# Maps filename → generator function. ui_trainer.py calls generate_screens().

SCREEN_GENERATORS = {
    "fiori_home.png":            screen_fiori_home,
    "migo_action.png":           screen_migo_action,
    "migo_reference.png":        screen_migo_reference,
    "migo_po.png":               screen_migo_po,
    "migo_items.png":            screen_migo_items,
    "migo_un.png":               screen_migo_un,
    "migo_storage_class.png":    screen_migo_storage_class,
    "migo_post.png":             screen_migo_post,
}


def generate_screens(screens_dir: Path):
    """Generate all placeholder PNGs into screens_dir. Called by ui_trainer.py."""
    screens_dir.mkdir(parents=True, exist_ok=True)
    for fname, fn in SCREEN_GENERATORS.items():
        fn().save(str(screens_dir / fname), "PNG")
    return list(SCREEN_GENERATORS.keys())
