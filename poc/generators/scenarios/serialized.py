"""
scenarios/serialized.py — High-Value Serialized Electronics: Goods Receipt in SAP MIGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Handling profile: SERIALIZED / HIGH-VALUE
  - Individual serial number capture per unit (mandatory)
  - Chain of custody tracking
  - Secure cage (locked storage) assignment required
  - Manager approval required before posting
  - Asset tag and shrinkage prevention focus
  - Movement type: 101

To adapt for a different warehouse:
  1. Copy this file (e.g. pharma_serialized.py, hazmat_serialized.py)
  2. Update SCENARIO metadata (id, title, site, role, handling_profile)
  3. Update tutorial steps (goals, instructions, hints, hotspots, feedback)
  4. Update materials list and serial numbers in generate_screens()
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
    "id":               "serialized_gr",
    "title":            "Goods Receipt for High-Value Serialized Items (SAP MIGO)",
    "site":             "TechVault DC · Austin, TX",
    "role":             "Receiving Associate",
    "handling_profile": "serialized",
    "tutorial": [
        {
            "screen":      "fiori_home.png",
            "goal":        "Open the MIGO transaction",
            "instruction": "Click the MIGO tile to open Goods Movement.",
            "hint":        "Look for the 'Goods Movement (MIGO)' tile — it has a star icon.",
            "hotspot":     {"x": 473, "y": 162, "w": 200, "h": 130},
            "feedback":    "MIGO open. Now configure your high-value Goods Receipt.",
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
            "feedback":    "Good. Every GR must be tied to a PO for audit trail.",
        },
        {
            "screen":      "migo_po.png",
            "goal":        "Enter the Purchase Order number",
            "instruction": "Type the PO number into the Purchase Order No. field and press Enter.",
            "hint":        "The PO number field is to the right of the Reference Document dropdown.",
            "hotspot":     {"x": 524, "y": 148, "w": 200, "h": 36},
            "feedback":    "PO 4500077400 loaded. High-value items pulled in automatically.",
        },
        {
            "screen":      "migo_items.png",
            "goal":        "Verify line item quantities and materials",
            "instruction": "Check the Qty column. Confirm it matches your delivery note.",
            "hint":        "10 ProBook 15 Laptops (EL-5501) and 25 RTX GPUs (EL-7720). Verify count.",
            "hotspot":     {"x": 450, "y": 272, "w": 100, "h": 34},
            "feedback":    "Quantities verified. Each unit requires individual serial capture.",
        },
        {
            "screen":      "migo_serial.png",
            "goal":        "Scan and enter serial numbers per unit",
            "instruction": "Enter the serial number for each unit. Serial capture is mandatory for chain of custody.",
            "hint":        "Type or scan each serial number. Laptops: SN-LT001 through SN-LT010. Do not skip any unit.",
            "hotspot":     {"x": 200, "y": 320, "w": 300, "h": 34},
            "feedback":    "Serials captured. Unit accountability complete. Now assign secure storage.",
        },
        {
            "screen":      "migo_secure.png",
            "goal":        "Assign to secure storage (CAGE-01)",
            "instruction": "Click the Storage Location dropdown and select 'CAGE-01 (Secure)'.",
            "hint":        "High-value items do not go to the main floor. CAGE-01 is locked. Mandatory.",
            "hotspot":     {"x": 260, "y": 210, "w": 220, "h": 34},
            "feedback":    "CAGE-01 assigned. Secure cage lock mandatory. Ready for manager approval.",
        },
        {
            "screen":      "migo_post.png",
            "goal":        "Post the Goods Receipt",
            "instruction": "Click the Post button to submit for manager approval.",
            "hint":        "Review the summary. All serials captured and CAGE-01 confirmed. Then post.",
            "hotspot":     {"x": 20, "y": 88, "w": 80, "h": 32},
            "feedback":    "Posted! GR created. Manager approval pending. Shrinkage prevention: ON.",
        },
    ],
    "mission": {
        "title":      "Your Mission",
        "briefing": (
            "Post a Goods Receipt for PO 4500077400.\n"
            "10 ProBook 15 Laptops (EL-5501) + 25 RTX GPU Cards (EL-7720).\n"
            "Arriving at TechVault DC, Austin TX.\n"
            "Scan every serial number. Assign to CAGE-01 (locked). Manager approval required."
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
    """Reusable MIGO line items table for serialized high-value goods (y=210+)."""
    d.text((36, 216), "Line Items", font=fnt(14, bold=True), fill=SAP_TEXT)
    cols = [("Item", 60), ("Material", 120), ("Description", 200),
            ("Qty", 100), ("UoM", 70), ("S.Loc", 100), ("Serial No.", 120)]
    draw_table_header(d, 36, 240, cols)
    draw_table_row(d, 36, 272, cols,
                   ["0001", "EL-5501", "ProBook 15 Laptop", "10", "EA", "CAGE-01", "SN-LT001..."],
                   highlight_col=highlight_col)
    draw_table_row(d, 36, 306, cols,
                   ["0002", "EL-7720", "RTX GPU Card", "25", "EA", "CAGE-01", "SN-GPU001..."],
                   highlight_col=None)


def screen_fiori_home():
    """Fiori Launchpad with MIGO tile highlighted."""
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
    """MIGO with Action field highlighted."""
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, hl_action=True)
    placeholder_note(d)
    return img


def screen_migo_reference():
    """MIGO with Reference Document field highlighted."""
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, hl_ref=True)
    placeholder_note(d)
    return img


def screen_migo_po():
    """MIGO with PO number field highlighted."""
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500077400", hl_po=True)
    placeholder_note(d)
    return img


def screen_migo_items():
    """MIGO items table with Qty column highlighted."""
    img, d = new_screen("Goods Movement (MIGO) — PO 4500077400")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500077400")
    _items_table(d, highlight_col=3)   # Qty column highlighted
    placeholder_note(d)
    return img


def screen_migo_serial():
    """Serial number entry panel for high-value item (EL-5501 ProBook 15 Laptop)."""
    img, d = new_screen("Goods Movement (MIGO) — Serial Number Entry")
    draw_subheader(d, "Goods Movement > MIGO > Serial Capture")

    # Card header: "Serial Number Entry"
    draw_card(d, 20, 90, W - 20, 580,
              title="Serial Number Entry — EL-5501 ProBook 15 Laptop")

    # Instructions text
    d.text((36, 130), "Unit Accountability & Chain of Custody",
           font=fnt(12, bold=True), fill=SAP_LABEL)
    d.text((36, 154), "Scan or type each serial number. All 10 units require individual capture.",
           font=fnt(11), fill=SAP_TEXT)

    # Serial number entry fields
    serial_numbers = [
        ("SN-LT001", True),   # Already filled
        ("SN-LT002", True),   # Already filled
        ("SN-LT003", True),   # Already filled
        ("SN-LT004", True),   # Already filled
        ("SN-LT005", True),   # Already filled
        ("SN-LT006", False),  # Currently being entered (highlighted)
    ]

    sy = 190
    for idx, (sn, filled) in enumerate(serial_numbers, 1):
        label_text = f"Unit {idx}"
        if idx == 6:
            # Highlight this field as the active one
            draw_field(d, 36, sy, 300, 34, label_text, sn, highlight=True)
        else:
            # Show as filled but not highlighted
            draw_field(d, 36, sy, 300, 34, label_text, sn, highlight=False)
        sy += 50

    # Status banner
    draw_status_banner(d, "Serial capture active. Unit 6 of 10. Press Enter to advance.", ok=True)
    placeholder_note(d)
    return img


def screen_migo_secure():
    """Item Detail with Storage Location dropdown set to CAGE-01 and security banner."""
    img, d = new_screen("Goods Movement (MIGO) — Item Detail")
    draw_subheader(d, "Goods Movement > MIGO")
    draw_card(d, 20, 90, W - 20, 560,
              title="Item Detail — Line 0001: EL-5501 ProBook 15 Laptop")

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

    d.text((36, 170), "Where Tab — Secure Storage Assignment", font=fnt(13, bold=True), fill=SAP_LABEL)
    draw_field(   d, 36,  210, 200, 34, "Plant",            "TechVault-01")
    draw_dropdown(d, 260, 210, 220, 34, "Storage Location", "CAGE-01 (Secure)", highlight=True)
    draw_field(   d, 504, 210, 200, 34, "Movement Type",    "101")
    draw_field(   d, 36,  278, 200, 34, "Vendor",           "TechSupply Corp")
    draw_field(   d, 260, 278, 220, 34, "Delivery Note",    "DN-TechSupply-001")

    # Security status banner (red, for emphasis)
    d.rounded_rectangle([20, 380, W - 20, 430],
                        radius=4, fill=(255, 240, 240), outline=SAP_RED, width=2)
    d.text((44, 394), "⚠ High-value item — CAGE-01 assignment mandatory",
           font=fnt(12, bold=True), fill=SAP_RED)
    d.text((44, 414), "Secure cage lock required. No exceptions.",
           font=fnt(11), fill=SAP_RED)

    placeholder_note(d)
    return img


def screen_migo_post():
    """Post screen with serialized high-value GR summary."""
    img, d = new_screen("Goods Movement (MIGO) — Ready to Post")
    draw_subheader(d, "Goods Movement > MIGO")

    # Toolbar with Post highlighted
    d.rectangle([0, 80, W, 116], fill=(248, 250, 252))
    d.line([(0, 116), (W, 116)], fill=SAP_BORDER, width=1)
    draw_button(d, 20,  88, 80, 32, "Post",   primary=True,  highlight=True)
    draw_button(d, 112, 88, 80, 32, "Check",  primary=False)
    draw_button(d, 204, 88, 80, 32, "Cancel", primary=False)

    # Summary card
    draw_card(d, 20, 126, W - 20, 380, title="Ready to Post — High-Value Serialized GR Summary")
    summary = [
        ("Action",             "Goods Receipt against Purchase Order"),
        ("Purchase Order",     "4500077400"),
        ("Line Items",         "2 items (10 Laptops + 25 GPUs)"),
        ("Vendor",             "TechSupply Corp"),
        ("Serial Numbers",     "✓ All 35 units captured (chain of custody)"),
        ("Storage Location",   "CAGE-01 (Locked Secure Cage)"),
        ("Manager Approval",   "⧐ Pending approval before posting"),
    ]
    sy = 166
    for label, value in summary:
        d.text((36, sy),  label + ":", font=fnt(12, bold=True), fill=SAP_LABEL)
        d.text((220, sy), value,       font=fnt(12),             fill=SAP_TEXT)
        sy += 24

    draw_status_banner(d, "All validations passed. Serials captured. Secure storage confirmed. Ready for manager approval.")
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
    "migo_serial.png":    screen_migo_serial,
    "migo_secure.png":    screen_migo_secure,
    "migo_post.png":      screen_migo_post,
}


def generate_screens(screens_dir: Path):
    """Generate all placeholder PNGs into screens_dir. Called by ui_trainer.py."""
    screens_dir.mkdir(parents=True, exist_ok=True)
    for fname, fn in SCREEN_GENERATORS.items():
        fn().save(str(screens_dir / fname), "PNG")
    return list(SCREEN_GENERATORS.keys())
