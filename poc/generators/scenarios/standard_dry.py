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
    SAP_BRANDING,
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
    "title":            "Standard Goods Receipt — SAP MIGO",
    "site":             "Apex Auto Parts DC · Memphis, TN",
    "role":             "Receiving Associate",
    "handling_profile": "standard_dry",
    "training_domain":  "software",
    "asset_source":     "captured",
    "branding":         SAP_BRANDING,
    "tutorial": [
        {
            "screen":      "fiori_home.png",
            "goal":        "Open the MIGO transaction",
            "instruction": "Click the MIGO tile to open Goods Movement.",
            "hint":        "Look for the 'Goods Movement (MIGO)' tile — it has a star icon.",
            "hotspot":     {"x": 540, "y": 100, "w": 200, "h": 130},
            "feedback":    "Nice! MIGO is open. Now let's configure your Goods Receipt.",
            "consequence": "Opening the wrong transaction means you're working in the wrong module. If you open Inventory Management instead of MIGO, you can't post a goods receipt against a PO.",
            "explore_info": [
                "Goods Movement (MIGO) — this is where you post receipts, issues, and transfers. Your main tool for receiving. Look for the star icon.",
                "Purchase Requisition — request materials before a PO exists. Not used for receiving.",
                "Inventory Management — view stock levels. Read-only for receiving associates.",
                "Purchase Order — view PO details. You don't create POs, but you reference them in MIGO.",
                "Receiving Dock — Apex tile showing today's expected deliveries.",
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
            "consequence": "Selecting the wrong action (e.g. 'Goods Issue' instead of 'Goods Receipt') would remove inventory instead of adding it. Finance sees a negative stock movement and the PO won't match.",
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
            "feedback":    "Good. Every GR at Apex must be tied to a PO.",
            "consequence": "Posting without a PO reference creates a free-goods receipt. Finance can't match it to an invoice, the vendor doesn't get paid on time, and an auditor flags the discrepancy.",
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
            "feedback":    "PO 4500098712 loaded. SAP pulled in the line items automatically.",
            "consequence": "Entering the wrong PO number means you're receiving against someone else's order. The quantities won't match, the vendor invoice won't clear, and both POs get stuck in error.",
            "explore_info": [
                "PO Number — find this on the delivery note or bill of lading. SAP auto-populates the line items when you press Enter.",
                "Execute button — loads the PO data into MIGO. Same as pressing Enter in the PO field.",
                "Tip — always double-check the PO number against the paper BOL before hitting Enter.",
            ],
        },
        {
            "screen":      "migo_items.png",
            "goal":        "Verify line item quantities",
            "instruction": "Check the Qty column. Confirm it matches what's physically on your dock.",
            "hint":        "Compare each quantity against your delivery paperwork before proceeding.",
            "hotspot":     {"x": 450, "y": 272, "w": 100, "h": 34},
            "feedback":    "Quantities verified. If anything is short, update it now — not after posting.",
            "consequence": "Posting the wrong quantity means inventory records don't match physical stock. Short receipt: vendor doesn't get paid for what they shipped. Over receipt: you're paying for product you didn't get.",
            "explore_info": [
                "Item — line number in the PO. Each material is a separate line.",
                "Material — SAP material number. Matches the product master.",
                "Description — human-readable product name.",
                "Qty — how many units you're receiving. Must match what's physically on the dock.",
                "UoM — Unit of Measure. UN = units, SET = sets, CS = cases.",
                "S.Loc — Storage Location. All dry goods at Apex go to WH-01 (Main Warehouse).",
            ],
        },
        {
            "screen":      "migo_post.png",
            "goal":        "Post the Goods Receipt",
            "instruction": "Click the Post button to complete the Goods Receipt.",
            "hint":        "Review the summary first. Once you post, SAP generates the material document.",
            "hotspot":     {"x": 20, "y": 88, "w": 80, "h": 32},
            "feedback":    "Posted! Material document created. Inventory updated. Receiving complete.",
            "consequence": "Clicking Check instead of Post runs validation but doesn't create the document. Clicking Cancel discards everything — you'd need to start over. Neither is harmful, but the dock is clear and trucks are waiting.",
            "explore_info": [
                "Post — creates the material document and updates inventory. This is the final step. Can be reversed, but it's easier to get it right the first time.",
                "Check — runs validation without posting. Use this if you're unsure and want SAP to flag errors first.",
                "Cancel — discards the entire goods receipt. You'll need to start over from the PO number.",
                "Summary panel — shows everything you've entered. Review it before clicking Post.",
            ],
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
        "time_limit": 120,
        "narratives": [
            "It's peak season and the dock is stacked three-deep. Get this PO posted so the forklift team can start putaway.",
            "Your supervisor is running the morning standup in 10 minutes. She wants this receipt confirmed before the meeting.",
            "The vendor's driver needs a signed BOL before he can leave. Post the GR so the system generates the confirmation.",
            "New hire is watching you work through a standard receipt. Show them the basics — clean and quick.",
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
    """Reusable MIGO line items table (y=210+) — no Batch column for standard_dry."""
    d.text((36, 216), "Line Items", font=fnt(14, bold=True), fill=SAP_TEXT)
    cols = [("Item", 60), ("Material", 120), ("Description", 200),
            ("Qty", 100), ("UoM", 70), ("S.Loc", 100)]
    row1 = ["0001", "AP-3310", "Oil Filter 10W30 Case", "200", "UN", "WH-01"]
    row2 = ["0002", "AP-7721", "Brake Pads Organic Disc", "150", "SET", "WH-01"]
    if blank_col is not None:
        row1[blank_col] = ""
        row2[blank_col] = ""
    draw_table_header(d, 36, 240, cols)
    draw_table_row(d, 36, 272, cols, row1, highlight_col=highlight_col, decoy_cols=decoy_cols)
    draw_table_row(d, 36, 306, cols, row2, highlight_col=None, decoy_cols=decoy_cols)


def screen_fiori_home(hl=True):
    img, d = new_screen("SAP Fiori Launchpad")
    # Decoy tiles: Purchase Order (idx 4) and Receiving Dock (idx 5) look active on neutral
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
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    # Neutral: blank target + decoy the Reference Doc dropdown and Execute button
    action_val = "Goods Receipt" if hl else ""
    _header_row(d, action=action_val, hl_action=hl,
                decoy_ref=not hl, decoy_exec=not hl)
    placeholder_note(d)
    return img


def screen_migo_reference(hl=True):
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    # Neutral: blank target + decoy the Action dropdown and PO field
    ref_val = "Purchase Order" if hl else ""
    _header_row(d, reference=ref_val, hl_ref=hl,
                decoy_action=not hl, decoy_po=not hl)
    placeholder_note(d)
    return img


def screen_migo_po(hl=True):
    img, d = new_screen("Goods Movement (MIGO)")
    draw_subheader(d, "Goods Movement > MIGO")
    # Neutral: blank target + decoy the Reference Doc dropdown and Execute button
    po_val = "4500098712" if hl else ""
    _header_row(d, po=po_val, hl_po=hl,
                decoy_ref=not hl, decoy_exec=not hl)
    placeholder_note(d)
    return img


def screen_migo_items(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — PO 4500098712")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500098712")
    # Neutral: blank Qty + decoy S.Loc (col 5)
    _items_table(d, highlight_col=3 if hl else None,
                 blank_col=3 if not hl else None,
                 decoy_cols=[5] if not hl else None)
    placeholder_note(d)
    return img


def screen_migo_post(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — Ready to Post")
    draw_subheader(d, "Goods Movement > MIGO")
    # Toolbar with Post highlighted
    d.rectangle([0, 80, W, 116], fill=(248, 250, 252))
    d.line([(0, 116), (W, 116)], fill=SAP_BORDER, width=1)
    # Neutral: decoy Check and Cancel buttons
    draw_button(d, 20,  88, 80, 32, "Post",   primary=True,  highlight=hl)
    draw_button(d, 112, 88, 80, 32, "Check",  primary=False, decoy=not hl)
    draw_button(d, 204, 88, 80, 32, "Cancel", primary=False, decoy=not hl)
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
    """Generate highlighted + neutral PNGs. Called by ui_trainer.py.

    Output:
        screens/           ← highlighted variants (L0 Explore, L1 Guided)
        screens_neutral/   ← neutral variants   (L2 On Your Own, L3 Challenge)

    Returns (highlighted_filenames, neutral_filenames).
    """
    screens_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = screens_dir.parent / "screens_neutral"
    neutral_dir.mkdir(parents=True, exist_ok=True)

    for fname, fn in SCREEN_GENERATORS.items():
        fn(hl=True).save(str(screens_dir / fname), "PNG")
        fn(hl=False).save(str(neutral_dir / fname), "PNG")

    names = list(SCREEN_GENERATORS.keys())
    return names
