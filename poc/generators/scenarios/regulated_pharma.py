"""
scenarios/regulated_pharma.py — Regulated Pharma: Goods Receipt in SAP MIGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Handling profile: REGULATED_PHARMA / GXP
  - Batch/lot number mandatory
  - Shelf Life / Expiry Date mandatory per item
  - Certificate of Analysis required — checked before post
  - Chain of custody audit trail enabled
  - Movement type: 101

Cardinal Health DC, Cincinnati OH — Pharmaceutical Distribution Center
Receiving RX drugs for retail pharmacy network. Every step audited and GxP traceable.

To adapt for a different warehouse:
  1. Copy this file (e.g. hazmat_gr.py, drygoods_gr.py)
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
    "id":               "pharma_gr",
    "title":            "Pharma GxP Goods Receipt — SAP MIGO",
    "site":             "Cardinal Health DC · Cincinnati, OH",
    "role":             "Receiving Associate (GxP Qualified)",
    "handling_profile": "regulated_pharma",
    "training_domain":  "software",
    "asset_source":     "placeholder",
    "branding":         SAP_BRANDING,
    "tutorial": [
        {
            "screen":      "fiori_home.png",
            "goal":        "Open the MIGO transaction",
            "instruction": "Click the MIGO tile to open Goods Movement.",
            "hint":        "Look for the 'Goods Movement (MIGO)' tile — it has a star icon.",
            "hotspot":     {"x": 540, "y": 100, "w": 200, "h": 130},
            "feedback":    "MIGO opened. GxP audit trail is active. Now configure your Goods Receipt.",
            "consequence": "Opening the wrong transaction means you're working in the wrong module. In a GxP environment, every incorrect action is logged in the audit trail and requires a deviation report.",
            "explore_info": [
                "Goods Movement (MIGO) — post receipts, issues, and transfers for Cardinal Health network. Your main tool for receiving RX drugs. Look for the star icon.",
                "Purchase Requisition — request RX materials before a PO exists. Not used for direct receiving.",
                "Inventory Management — view stock levels and pharma holding areas. Read-only for receiving associates.",
                "Purchase Order — view PO details. You don't create POs, but you reference them against delivery.",
                "Receiving Dock — Cardinal Health custom tile showing today's expected pharmaceutical deliveries.",
                "Vendor Invoice — finance uses this. Not part of the receiving workflow, GxP-wise.",
            ],
        },
        {
            "screen":      "migo_action.png",
            "goal":        "Set the action to Goods Receipt",
            "instruction": "Confirm the Action dropdown is set to 'Goods Receipt'. Click it.",
            "hint":        "The Action dropdown is the first field in the transaction header.",
            "hotspot":     {"x": 36, "y": 148, "w": 220, "h": 36},
            "feedback":    "Correct. Action = Goods Receipt. Now set the reference type.",
            "consequence": "Selecting the wrong action (e.g. 'Goods Issue' instead of 'Goods Receipt') would remove pharmaceutical inventory instead of adding it. This triggers an FDA-reportable discrepancy and halts distribution.",
            "explore_info": [
                "Action — tells SAP what kind of goods movement you're doing. Options: Goods Receipt, Goods Issue, Transfer Posting, etc.",
                "Reference Document — what you're posting against. Usually a Purchase Order for receiving pharmaceuticals.",
                "PO No — the PO number from your delivery paperwork.",
                "Execute — loads the PO data into MIGO. Same as pressing Enter in the PO field.",
            ],
        },
        {
            "screen":      "migo_reference.png",
            "goal":        "Set the reference document to Purchase Order",
            "instruction": "Click the Reference Document dropdown and select 'Purchase Order'.",
            "hint":        "The Reference Document dropdown is next to the Action dropdown.",
            "hotspot":     {"x": 280, "y": 148, "w": 220, "h": 36},
            "feedback":    "Good. Every GR at Cardinal Health must be tied to a PO — chain of custody begins here.",
            "consequence": "Posting without a PO reference breaks the chain of custody. GxP requires full traceability from manufacturer to patient. An unlinked receipt triggers an audit finding.",
            "explore_info": [
                "Reference Document — links your receipt to an existing document. 'Purchase Order' is standard for RX receiving.",
                "Other reference types — 'Material Document' for reversals, 'Delivery' for inbound logistics. Always use Purchase Order for Cardinal Health.",
            ],
        },
        {
            "screen":      "migo_po.png",
            "goal":        "Enter the Purchase Order number",
            "instruction": "Type the PO number into the Purchase Order No. field and press Enter.",
            "hint":        "The PO number field is to the right of the Reference Document dropdown.",
            "hotspot":     {"x": 524, "y": 148, "w": 200, "h": 36},
            "feedback":    "PO 4500055001 loaded. SAP pulled in the line items automatically.",
            "consequence": "Entering the wrong PO number links this receipt to the wrong shipment. The lot numbers won't match the manufacturer's Certificate of Analysis, triggering a GxP non-conformance.",
            "explore_info": [
                "PO Number — find this on the delivery note or bill of lading. SAP auto-populates the line items when you press Enter.",
                "Execute button — loads the PO data into MIGO. Same as pressing Enter in the PO field.",
                "Tip — always double-check the PO number against the pharmaceutical shipment packing list and CoA.",
            ],
        },
        {
            "screen":      "migo_items.png",
            "goal":        "Verify line item quantities against packing slip",
            "instruction": "Check the Qty column. Confirm it matches your packing slip exactly.",
            "hint":        "Compare each quantity against your delivery paperwork before proceeding. This is mandatory.",
            "hotspot":     {"x": 416, "y": 272, "w": 100, "h": 34},
            "feedback":    "Quantities verified. If anything is short, update it now — GxP requires accuracy at receipt.",
            "consequence": "Posting the wrong quantity for pharmaceutical products means inventory records don't match physical stock. This is a GxP critical finding — the FDA requires exact counts for controlled substances.",
            "explore_info": [
                "Item — line number in the PO. Each material is a separate line.",
                "Material — SAP material number. Matches the product master data.",
                "Description — human-readable RX product name (e.g., Metformin 500mg tablets).",
                "Qty — how many units you're receiving. Must match what's physically on the dock.",
                "UoM — Unit of Measure. EA = each, CS = cases, KG = kilograms.",
                "S.Loc — Storage Location. PHARM-1 is climate-controlled for RX products.",
                "Batch — lot/batch code from manufacturer. Required for all pharmaceuticals.",
            ],
        },
        {
            "screen":      "migo_lot.png",
            "goal":        "Enter the batch / lot number",
            "instruction": "Click the Batch field and enter the lot code from the pharmaceutical label.",
            "hint":        "Batch entry is mandatory for all RX drugs at Cardinal Health — this is GxP requirement, not optional.",
            "hotspot":     {"x": 686, "y": 272, "w": 120, "h": 34},
            "feedback":    "Lot number recorded. This establishes the chain of custody. Lot is traceable in audit trail.",
            "consequence": "Skipping the lot number breaks the chain of custody. If there's a product recall, you can't trace which patients received this batch. FDA 21 CFR Part 211 requires lot-level traceability.",
            "explore_info": [
                "Batch / Lot — traceability code from the manufacturer. Required for all RX drugs at Cardinal Health.",
                "Why it matters — in a recall, this is how you identify which batches to pull. No batch = no traceability = patient safety issue.",
                "Where to find it — printed on the pharmaceutical label, shipping case, and Certificate of Analysis.",
            ],
        },
        {
            "screen":      "migo_expiry.png",
            "goal":        "Enter the expiry date in item detail",
            "instruction": "Click the Shelf Life / Expiry Date field and enter the expiration date from the pharmaceutical label.",
            "hint":        "Shelf Life and Expiry Date are separate GxP requirements. This ensures no expired drugs enter stock.",
            "hotspot":     {"x": 260, "y": 278, "w": 220, "h": 34},
            "feedback":    "Expiry date recorded. SAP validates against today's date. Cold chain audit trail locked in.",
            "consequence": "Missing or incorrect expiry date means expired drugs could enter sellable stock. Dispensing expired medication is a patient safety issue and a GxP critical deviation.",
            "explore_info": [
                "Plant — the physical facility. CH01 = Cardinal Health Cincinnati.",
                "Storage Location — PHARM-1 (Climate Controlled for RX products).",
                "Movement Type — 101 = standard goods receipt against PO. Don't change this.",
                "Vendor — the supplier. Auto-populated from the PO.",
                "Shelf Life / Expiry Date — the expiration date from the pharmaceutical label. SAP validates it's future-dated.",
            ],
        },
        {
            "screen":      "migo_coa.png",
            "goal":        "Confirm Certificate of Analysis checkbox",
            "instruction": "Check the 'Certificate of Analysis Received' checkbox. CoA must be on file before posting.",
            "hint":        "This is a GxP gate. If CoA is missing, the receiving process cannot complete. Verify with vendor.",
            "hotspot":     {"x": 36, "y": 350, "w": 300, "h": 26},
            "feedback":    "Certificate of Analysis confirmed. Quality gate passed. All mandatory GxP fields complete.",
            "consequence": "Posting without a Certificate of Analysis means the drug hasn't been verified against manufacturer specs. If potency, purity, or sterility is off, compromised product reaches pharmacies.",
            "explore_info": [
                "Certificate of Analysis Received — GxP gate. Must be checked before post. Verifies manufacturer testing.",
                "Batch Tracking Enabled — automatically set for all RX products. Shows lot-level tracking is active.",
                "Lot Number Verification — confirms lot matches CoA. Automatic quality check.",
            ],
        },
        {
            "screen":      "migo_post.png",
            "goal":        "Post the Goods Receipt",
            "instruction": "Click the Post button to complete the Goods Receipt.",
            "hint":        "Review the GxP summary. Once you post, SAP generates the material document with full audit trail.",
            "hotspot":     {"x": 20, "y": 88, "w": 80, "h": 32},
            "feedback":    "Posted! Material document created. Inventory updated. Full GxP audit trail recorded. Chain of custody complete.",
            "consequence": "Clicking Check instead of Post runs validation but doesn't create the document. Clicking Cancel discards everything — you'd need to re-enter all GxP data. The audit trail records the cancellation.",
            "explore_info": [
                "Post — creates the material document and updates inventory. Final step. Can be reversed, but clean execution is better.",
                "Check — runs validation without posting. Use this if you're unsure and want SAP to flag errors first.",
                "Cancel — discards the entire goods receipt. You'll need to start over from the PO number.",
                "GxP Summary panel — shows everything you've entered. Review lot, expiry, CoA status before clicking Post.",
            ],
        },
    ],
    "mission": {
        "title":      "Your Mission",
        "briefing": (
            "Post a Goods Receipt for PO 4500055001.\n"
            "RX-4401 Metformin 500mg tablets (500 units, Lot LOT-RX2402) from PharmaCo Inc.\n"
            "RX-8812 Lisinopril 10mg (200 units, Lot LOT-RX2403) from PharmaCo Inc.\n"
            "Storage: PHARM-1 (Climate Controlled). Lot numbers & expiry dates mandatory.\n"
            "Certificate of Analysis required. GxP audit trail enabled."
        ),
        "par_clicks": 12,
        "time_limit": 180,
        "narratives": [
            "The FDA inspector is on-site for a routine audit. She's reviewing receiving procedures right now. Every field matters.",
            "PharmaCo's cold-chain truck has been at the dock for 30 minutes. Temperature excursion risk rises every minute. Post the GR and get product into climate control.",
            "A hospital in the network is running low on Metformin. They've escalated to your DC manager. Get this receipt posted so the order can ship today.",
            "Your GxP trainer is evaluating your solo receiving competency. This is your qualification run — zero errors expected.",
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


def _items_table(d, highlight_col=None, batch_val="", blank_col=None, decoy_cols=None):
    """Reusable MIGO line items table (y=210+) for pharmaceutical materials.
    blank_col: if set, blanks the values in that column (for L2/L3 challenge).
    decoy_cols: list of column indices to style as decoys (subtle blue tint).
    """
    d.text((36, 216), "Line Items", font=fnt(14, bold=True), fill=SAP_TEXT)
    cols = [("Item", 60), ("Material", 120), ("Description", 200),
            ("Qty", 100), ("UoM", 70), ("S.Loc", 100), ("Batch", 120)]
    row1 = ["0001", "RX-4401", "Metformin 500mg tablets", "500", "EA", "PHARM-1", batch_val]
    row2 = ["0002", "RX-8812", "Lisinopril 10mg tablets", "200", "EA", "PHARM-1", ""]
    if blank_col is not None:
        row1[blank_col] = ""
        row2[blank_col] = ""
    draw_table_header(d, 36, 240, cols)
    draw_table_row(d, 36, 272, cols, row1, highlight_col=highlight_col, decoy_cols=decoy_cols)
    draw_table_row(d, 36, 306, cols, row2, highlight_col=None, decoy_cols=decoy_cols)


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
    po_val = "4500055001" if hl else ""
    _header_row(d, po=po_val, hl_po=hl,
                decoy_ref=not hl, decoy_exec=not hl)
    placeholder_note(d)
    return img


def screen_migo_items(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — PO 4500055001")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500055001")
    # Neutral: blank Qty + decoy S.Loc (5) and Batch (6) columns
    _items_table(d, highlight_col=3 if hl else None,
                 blank_col=3 if not hl else None,
                 decoy_cols=[5, 6] if not hl else None)
    placeholder_note(d)
    return img


def screen_migo_lot(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — PO 4500055001")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500055001")
    # Neutral: blank Batch + decoy Qty (3) and S.Loc (5) columns
    batch = "LOT-RX2402" if hl else ""
    _items_table(d, highlight_col=6 if hl else None, batch_val=batch,
                 decoy_cols=[3, 5] if not hl else None)
    placeholder_note(d)
    return img


def screen_migo_expiry(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — Item Detail")
    draw_subheader(d, "Goods Movement > MIGO")
    draw_card(d, 20, 90, W - 20, 560,
              title="Item Detail — Line 0001: RX-4401 Metformin 500mg tablets")
    _draw_item_detail_tabs(d, active_idx=0)
    d.text((36, 170), "Where Tab — Storage & Shelf Life (GxP Required)",
           font=fnt(13, bold=True), fill=SAP_LABEL)
    # Neutral: blank expiry value + decoy Plant and Movement Type fields
    expiry_val = "2026-12-31" if hl else ""
    draw_field(   d, 36,  210, 200, 34, "Plant",                    "CH01",       decoy=not hl)
    draw_field(   d, 260, 210, 220, 34, "Storage Location",         "PHARM-1")
    draw_field(   d, 504, 210, 200, 34, "Movement Type",            "101",        decoy=not hl)
    draw_field(   d, 36,  278, 200, 34, "Vendor",                   "V-PHARMACO")
    draw_field(   d, 260, 278, 220, 34, "Shelf Life / Expiry Date", expiry_val,   highlight=hl)
    placeholder_note(d)
    return img


def screen_migo_coa(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — Item Detail")
    draw_subheader(d, "Goods Movement > MIGO")
    draw_card(d, 20, 90, W - 20, 560,
              title="Item Detail — Line 0001: RX-4401 Metformin 500mg tablets")
    _draw_item_detail_tabs(d, active_idx=2)
    d.text((36, 170), "Material Tab — Quality & GxP Compliance",
           font=fnt(13, bold=True), fill=SAP_LABEL)
    draw_field(d, 36,  210, 200, 34, "Material Number",      "RX-4401")
    draw_field(d, 260, 210, 220, 34, "Material Description", "Metformin 500mg tablets")
    draw_field(d, 36,  278, 200, 34, "Purchasing Group",     "PHARMA-001")
    # Neutral: decoy Batch Tracking and Lot Verification checkboxes
    draw_checkbox(d, 36, 350, "Certificate of Analysis Received", checked=False, highlight=hl)
    draw_checkbox(d, 36, 390, "Batch Tracking Enabled",          checked=True,  decoy=not hl)
    draw_checkbox(d, 36, 430, "Lot Number Verification",         checked=True,  decoy=not hl)
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
    draw_card(d, 20, 126, W - 20, 340, title="Ready to Post — GxP Summary")
    summary = [
        ("Action",             "Goods Receipt against Purchase Order"),
        ("Purchase Order",     "4500055001"),
        ("Line Items",         "2 RX items"),
        ("Storage Location",   "PHARM-1 (Climate Controlled)"),
        ("Lot Numbers",        "✓ LOT-RX2402, LOT-RX2403 entered"),
        ("Expiry Dates",       "✓ All items shelf-life verified"),
        ("Certificate of Analysis", "✓ Received & on file"),
        ("GxP Audit Trail",    "✓ Full traceability enabled"),
    ]
    sy = 166
    for label, value in summary:
        d.text((36, sy),  label + ":", font=fnt(12, bold=True), fill=SAP_LABEL)
        d.text((220, sy), value,       font=fnt(12),             fill=SAP_TEXT)
        sy += 24
    draw_status_banner(d, "All GxP validations passed. Chain of custody complete. Click Post to finalize.")
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
    "migo_lot.png":       screen_migo_lot,
    "migo_expiry.png":    screen_migo_expiry,
    "migo_coa.png":       screen_migo_coa,
    "migo_post.png":      screen_migo_post,
}


def generate_screens(screens_dir: Path):
    """Generate highlighted + neutral PNGs. Called by ui_trainer.py.

    Output:
        screens/           ← highlighted variants (L0 Explore, L1 Guided)
        screens_neutral/   ← neutral variants   (L2 On Your Own, L3 Challenge)

    Returns (highlighted_filenames).
    """
    screens_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = screens_dir.parent / "screens_neutral"
    neutral_dir.mkdir(parents=True, exist_ok=True)

    for fname, fn in SCREEN_GENERATORS.items():
        fn(hl=True).save(str(screens_dir / fname), "PNG")
        fn(hl=False).save(str(neutral_dir / fname), "PNG")

    names = list(SCREEN_GENERATORS.keys())
    return names
