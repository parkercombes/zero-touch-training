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
            "hotspot":     {"x": 540, "y": 100, "w": 200, "h": 130},
            "feedback":    "MIGO open. Now configure your high-value Goods Receipt.",
            "consequence": "Opening the wrong transaction means you're working in the wrong module. For high-value items, an incorrect transaction bypasses the serial capture workflow entirely — units enter inventory untracked.",
            "explore_info": [
                "Goods Movement (MIGO) — this is where you post receipts, issues, and transfers. Your main tool for receiving serialized assets. Look for the star icon.",
                "Purchase Requisition — request materials before a PO exists. Not used for receiving.",
                "Inventory Management — view stock levels. Read-only for receiving associates.",
                "Purchase Order — view PO details. You don't create POs, but you reference them in MIGO.",
                "Receiving Dock — TechVault custom tile showing today's expected deliveries.",
                "Vendor Invoice — finance uses this. Not part of the receiving workflow.",
            ],
        },
        {
            "screen":      "migo_action.png",
            "goal":        "Set the action to Goods Receipt",
            "instruction": "Confirm the Action dropdown is set to 'Goods Receipt'. Click it.",
            "hint":        "The Action dropdown is the first field in the transaction header.",
            "hotspot":     {"x": 36, "y": 148, "w": 220, "h": 36},
            "feedback":    "Correct. Action = Goods Receipt. Now set the reference type.",
            "consequence": "Selecting 'Goods Issue' instead of 'Goods Receipt' would remove electronics inventory. Those units vanish from the system — $15,000+ in laptops with no audit trail. Loss prevention flags it immediately.",
            "explore_info": [
                "Action — tells SAP what kind of goods movement you're doing. Options: Goods Receipt, Goods Issue, Transfer Posting, etc.",
                "Reference Document — what you're posting against. Usually a Purchase Order for receiving.",
                "Purchase Order No. — the PO number from your delivery paperwork.",
                "Execute button — loads the PO data into MIGO. Same as pressing Enter in the PO field.",
            ],
        },
        {
            "screen":      "migo_reference.png",
            "goal":        "Set the reference document to Purchase Order",
            "instruction": "Click the Reference Document dropdown and select 'Purchase Order'.",
            "hint":        "The Reference Document dropdown is next to the Action dropdown.",
            "hotspot":     {"x": 280, "y": 148, "w": 220, "h": 36},
            "feedback":    "Good. Every GR must be tied to a PO for audit trail.",
            "consequence": "Posting without a PO reference breaks the chain of custody from manufacturer to cage. If a unit goes missing, you can't prove it was ever received against a valid order.",
            "explore_info": [
                "Reference Document — links your receipt to an existing document. 'Purchase Order' is standard for receiving.",
                "Other reference types — 'Material Document' for reversals, 'Delivery' for inbound deliveries. You'll almost always use Purchase Order.",
            ],
        },
        {
            "screen":      "migo_po.png",
            "goal":        "Enter the Purchase Order number",
            "instruction": "Type the PO number into the Purchase Order No. field and press Enter.",
            "hint":        "The PO number field is to the right of the Reference Document dropdown.",
            "hotspot":     {"x": 524, "y": 148, "w": 200, "h": 36},
            "feedback":    "PO 4500077400 loaded. High-value items pulled in automatically.",
            "consequence": "Wrong PO number links this receipt to the wrong shipment. The serial numbers won't match the vendor's packing list, triggering a discrepancy investigation and delaying cage assignment.",
            "explore_info": [
                "PO Number — find this on the delivery note or bill of lading. SAP auto-populates the line items when you press Enter.",
                "Execute button — loads the PO data into MIGO. Same as pressing Enter in the PO field.",
                "Tip — always double-check the PO number against the paper BOL and verify vendor packing list before hitting Enter.",
            ],
        },
        {
            "screen":      "migo_items.png",
            "goal":        "Verify line item quantities and materials",
            "instruction": "Check the Qty column. Confirm it matches your delivery note.",
            "hint":        "10 ProBook 15 Laptops (EL-5501) and 25 RTX GPUs (EL-7720). Verify count.",
            "hotspot":     {"x": 450, "y": 272, "w": 100, "h": 34},
            "feedback":    "Quantities verified. Each unit requires individual serial capture.",
            "consequence": "Posting the wrong quantity for serialized items means the serial count won't match. If you receive 10 but post 8, two laptops exist physically but not in SAP — they're invisible to loss prevention.",
            "explore_info": [
                "Item — line number in the PO. Each material is a separate line.",
                "Material — SAP material number. Matches the product master.",
                "Description — human-readable product name.",
                "Qty — how many units you're receiving. Must match what's physically on the dock.",
                "UoM — Unit of Measure. CS = cases, EA = each, KG = kilograms.",
                "S.Loc — Storage Location. Determines which cage or zone the product goes to.",
                "Serial No. — individual unit identifier. Required for all serialized items.",
            ],
        },
        {
            "screen":      "migo_serial.png",
            "goal":        "Scan and enter serial numbers per unit",
            "instruction": "Enter the serial number for each unit. Serial capture is mandatory for chain of custody.",
            "hint":        "Type or scan each serial number. Laptops: SN-LT001 through SN-LT010. Do not skip any unit.",
            "hotspot":     {"x": 200, "y": 320, "w": 300, "h": 34},
            "feedback":    "Serials captured. Unit accountability complete. Now assign secure storage.",
            "consequence": "Skipping serial capture means units enter inventory without individual tracking. If a laptop is stolen or lost, you can't identify which specific unit is missing or trace it back to this shipment.",
            "explore_info": [
                "Serial number entry panel — capture one unit at a time. Scan or type the SN from the label.",
                "Unit accountability — each serial ties a physical laptop or GPU to an inventory record. No serial = no proof of possession.",
                "Chain of custody — SAP maintains a log linking every unit to this receipt and eventually to the employee who signed it out.",
                "Scan vs manual entry — scanning is faster and less error-prone. Manual entry requires extra care for accuracy.",
                "Why every unit matters — high-value items like these are theft targets. Every serial is how you prove shrinkage is not your fault.",
            ],
        },
        {
            "screen":      "migo_secure.png",
            "goal":        "Assign to secure storage (CAGE-01)",
            "instruction": "Click the Storage Location dropdown and select 'CAGE-01 (Secure)'.",
            "hint":        "High-value items do not go to the main floor. CAGE-01 is locked. Mandatory.",
            "hotspot":     {"x": 260, "y": 210, "w": 220, "h": 34},
            "feedback":    "CAGE-01 assigned. Secure cage lock mandatory. Ready for manager approval.",
            "consequence": "Assigning high-value electronics to the main warehouse floor instead of CAGE-01 means they're accessible to anyone. Laptops and GPUs are the #1 shrinkage target — unsecured storage is an open invitation.",
            "explore_info": [
                "Plant — the physical facility. TechVault-01 = TechVault DC Austin.",
                "Storage Location — where items are physically stored. CAGE-01 (Secure, locked), WH-01 (Main Floor, public), WH-02 (Staging).",
                "Movement Type — 101 = standard goods receipt against PO. Don't change this unless you know what you're doing.",
                "Vendor — the supplier. Auto-populated from the PO.",
                "Delivery Note — the DN number from the truck paperwork.",
            ],
        },
        {
            "screen":      "migo_post.png",
            "goal":        "Post the Goods Receipt",
            "instruction": "Click the Post button to submit for manager approval.",
            "hint":        "Review the summary. All serials captured and CAGE-01 confirmed. Then post.",
            "hotspot":     {"x": 20, "y": 88, "w": 80, "h": 32},
            "feedback":    "Posted! GR created. Manager approval pending. Shrinkage prevention: ON.",
            "consequence": "Clicking Check instead of Post runs validation but doesn't submit for manager approval. Clicking Cancel discards serial numbers — you'd need to re-scan every unit. The items sit unsecured until posted.",
            "explore_info": [
                "Post — creates the material document and updates inventory. Submits to manager for approval. This is the final step.",
                "Check — runs validation without posting. Use this if you're unsure and want SAP to flag errors first.",
                "Cancel — discards the entire goods receipt. You'll need to start over from the PO number.",
                "High-Value Summary panel — shows everything you've entered. Review it before clicking Post.",
            ],
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
        "time_limit": 180,
        "narratives": [
            "Loss prevention flagged yesterday's receipt — two GPUs were missing serial numbers. Your manager wants today's receipt done by the book. Every serial, every cage.",
            "The vendor's insurance requires a signed chain-of-custody receipt within 60 minutes of delivery. The clock started when the truck docked. Post the GR.",
            "Black Friday stock is arriving early. These laptops are pre-sold and customers are waiting. Get them into CAGE-01 so fulfillment can stage them.",
            "IT audit is next week. Every serialized asset in CAGE-01 must have a matching SAP record. Your receiving accuracy today determines whether that audit passes.",
        ],
    },
}


# ── Screen generators ─────────────────────────────────────────────────────────
# Each function returns a PIL Image for one step in the tutorial sequence.
# The highlighted element matches the hotspot in SCENARIO["tutorial"] above.

def _header_row(d, action="Goods Receipt", reference="Purchase Order",
                po="", hl_action=False, hl_ref=False, hl_po=False,
                decoy_action=False, decoy_ref=False, decoy_po=False, decoy_exec=False):
    """Reusable MIGO transaction header strip (y=90–200)."""
    draw_card(d, 20, 90, W - 20, 200, title="Transaction Header")
    draw_dropdown(d, 36,  148, 220, 36, "Action",             action,    highlight=hl_action, decoy=decoy_action)
    draw_dropdown(d, 280, 148, 220, 36, "Reference Document", reference, highlight=hl_ref,    decoy=decoy_ref)
    draw_field(   d, 524, 148, 200, 36, "Purchase Order No.", po,        highlight=hl_po,     decoy=decoy_po)
    draw_button(  d, 744, 148,  80, 36, "Execute",            decoy=decoy_exec)


def _items_table(d, highlight_col=None, blank_col=None, decoy_cols=None):
    """Reusable MIGO line items table for serialized high-value goods (y=210+).
    blank_col: if set, blanks the values in that column (for L2/L3 challenge).
    decoy_cols: list of column indices to style as decoys (subtle blue tint).
    """
    d.text((36, 216), "Line Items", font=fnt(14, bold=True), fill=SAP_TEXT)
    cols = [("Item", 60), ("Material", 120), ("Description", 200),
            ("Qty", 100), ("UoM", 70), ("S.Loc", 100), ("Serial No.", 120)]
    row1 = ["0001", "EL-5501", "ProBook 15 Laptop", "10", "EA", "CAGE-01", "SN-LT001..."]
    row2 = ["0002", "EL-7720", "RTX GPU Card", "25", "EA", "CAGE-01", "SN-GPU001..."]
    if blank_col is not None:
        row1[blank_col] = ""
        row2[blank_col] = ""
    draw_table_header(d, 36, 240, cols)
    draw_table_row(d, 36, 272, cols, row1, highlight_col=highlight_col, decoy_cols=decoy_cols)
    draw_table_row(d, 36, 306, cols, row2, highlight_col=None, decoy_cols=decoy_cols)


def screen_fiori_home(hl=True):
    """Fiori Launchpad with MIGO tile highlighted."""
    img, d = new_screen("SAP Fiori Launchpad")
    # Decoy tiles: Purchase Order (idx 4) and Receiving Dock (idx 5) when hl=False
    decoy_indices = set() if hl else {4, 5}
    tiles = [
        ("Purchase\nRequisition", False),  ("Goods\nMovement\n(MIGO)", hl),
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
        is_decoy = i in decoy_indices
        if highlight:
            border, bg, lw = SAP_AMBER, (255, 248, 235), 2
        elif is_decoy:
            border, bg, lw = SAP_BLUE, (240, 246, 255), 1
        else:
            border, bg, lw = SAP_BORDER, SAP_WHITE, 1
        d.rounded_rectangle([x, y, x + tw, y + th], radius=6,
                             fill=bg, outline=border, width=lw)
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


def screen_migo_action(hl=True):
    """MIGO with Action field highlighted."""
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    # Neutral: blank action + decoy ref and exec
    action_val = "Goods Receipt" if hl else ""
    _header_row(d, action=action_val, hl_action=hl,
                decoy_ref=not hl, decoy_exec=not hl)
    placeholder_note(d)
    return img


def screen_migo_reference(hl=True):
    """MIGO with Reference Document field highlighted."""
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    # Neutral: blank ref + decoy action and PO
    ref_val = "Purchase Order" if hl else ""
    _header_row(d, reference=ref_val, hl_ref=hl,
                decoy_action=not hl, decoy_po=not hl)
    placeholder_note(d)
    return img


def screen_migo_po(hl=True):
    """MIGO with PO number field highlighted."""
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    # Neutral: blank PO + decoy ref and exec
    po_val = "4500077400" if hl else ""
    _header_row(d, po=po_val, hl_po=hl,
                decoy_ref=not hl, decoy_exec=not hl)
    placeholder_note(d)
    return img


def screen_migo_items(hl=True):
    """MIGO items table with Qty column highlighted."""
    img, d = new_screen("Goods Movement (MIGO) — PO 4500077400")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500077400")
    # Neutral: blank Qty + decoy S.Loc (5) and Serial No. (6) columns
    _items_table(d, highlight_col=3 if hl else None,
                 blank_col=3 if not hl else None,
                 decoy_cols=[5, 6] if not hl else None)
    placeholder_note(d)
    return img


def screen_migo_serial(hl=True):
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
        ("SN-LT006", False),  # Currently being entered (highlighted when hl=True)
    ]

    sy = 190
    for idx, (sn, filled) in enumerate(serial_numbers, 1):
        label_text = f"Unit {idx}"
        if idx == 6:
            # Highlight this field when hl=True; blank it when hl=False
            draw_field(d, 36, sy, 300, 34, label_text, sn if hl else "", highlight=hl)
        elif idx in (2, 4):
            # Decoys: Unit 2 and 4 get decoy styling when hl=False
            draw_field(d, 36, sy, 300, 34, label_text, sn, decoy=not hl)
        else:
            # Normal display
            draw_field(d, 36, sy, 300, 34, label_text, sn)
        sy += 50

    # Status banner
    draw_status_banner(d, "Serial capture active. Unit 6 of 10. Press Enter to advance.", ok=True)
    placeholder_note(d)
    return img


def _draw_item_detail_tabs(d, active_idx):
    """Shared tab bar for item detail screens."""
    tabs = ["Where", "Quantity", "Material", "Account Assignment", "Purchase Order"]
    tx = 36
    for i, tab in enumerate(tabs):
        active = (i == active_idx)
        bg = SAP_WHITE if active else SAP_GREY_BG
        d.rectangle([tx, 126, tx + len(tab) * 8 + 20, 150], fill=bg, outline=SAP_BORDER, width=1)
        if active:
            d.rectangle([tx, 148, tx + len(tab) * 8 + 20, 150], fill=SAP_BLUE)
        d.text((tx + 8, 132), tab,
               font=fnt(12, bold=active), fill=SAP_BLUE if active else SAP_LABEL)
        tx += len(tab) * 8 + 28
    d.line([(36, 150), (W - 36, 150)], fill=SAP_BORDER, width=1)


def screen_migo_secure(hl=True):
    """Item Detail with Storage Location dropdown set to CAGE-01 and security banner."""
    img, d = new_screen("Goods Movement (MIGO) — Item Detail")
    draw_subheader(d, "Goods Movement > MIGO")
    draw_card(d, 20, 90, W - 20, 560,
              title="Item Detail — Line 0001: EL-5501 ProBook 15 Laptop")

    # Use shared tab drawing function
    _draw_item_detail_tabs(d, active_idx=0)

    d.text((36, 170), "Where Tab — Secure Storage Assignment", font=fnt(13, bold=True), fill=SAP_LABEL)
    # Neutral: blank storage loc + decoy Plant and Movement Type
    sloc_val = "CAGE-01 (Secure)" if hl else ""
    draw_field(   d, 36,  210, 200, 34, "Plant",            "TechVault-01", decoy=not hl)
    draw_dropdown(d, 260, 210, 220, 34, "Storage Location", sloc_val, highlight=hl)
    draw_field(   d, 504, 210, 200, 34, "Movement Type",    "101", decoy=not hl)
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


def screen_migo_post(hl=True):
    """Post screen with serialized high-value GR summary."""
    img, d = new_screen("Goods Movement (MIGO) — Ready to Post")
    draw_subheader(d, "Goods Movement > MIGO")

    # Toolbar with Post highlighted or not
    d.rectangle([0, 80, W, 116], fill=(248, 250, 252))
    d.line([(0, 116), (W, 116)], fill=SAP_BORDER, width=1)
    # Neutral: decoy Check and Cancel buttons
    draw_button(d, 20,  88, 80, 32, "Post",   primary=True,  highlight=hl)
    draw_button(d, 112, 88, 80, 32, "Check",  primary=False, decoy=not hl)
    draw_button(d, 204, 88, 80, 32, "Cancel", primary=False, decoy=not hl)

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
    """Generate highlighted + neutral PNGs. Called by ui_trainer.py.

    Output:
        screens/           ← highlighted variants (L0 Explore, L1 Guided)
        screens_neutral/   ← neutral variants   (L2 On Your Own, L3 Challenge)

    Returns filenames list.
    """
    screens_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = screens_dir.parent / "screens_neutral"
    neutral_dir.mkdir(parents=True, exist_ok=True)

    for fname, fn in SCREEN_GENERATORS.items():
        fn(hl=True).save(str(screens_dir / fname), "PNG")
        fn(hl=False).save(str(neutral_dir / fname), "PNG")

    names = list(SCREEN_GENERATORS.keys())
    return names
