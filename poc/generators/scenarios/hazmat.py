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
    "id":               "hazmat_gr",
    "title":            "Hazmat Goods Receipt — SAP MIGO",
    "site":             "ChemCo Industrial DC · Houston, TX",
    "role":             "Receiving Associate",
    "handling_profile": "hazmat",
    "training_domain":  "software",
    "branding":         SAP_BRANDING,
    "tutorial": [
        {
            "screen":      "fiori_home.png",
            "goal":        "Open the MIGO transaction",
            "instruction": "Click the MIGO tile to open Goods Movement.",
            "hint":        "Look for the 'Goods Movement (MIGO)' tile — it has an amber highlight for hazmat.",
            "hotspot":     {"x": 540, "y": 100, "w": 200, "h": 130},
            "feedback":    "Nice! MIGO is open. Now let's configure your hazmat Goods Receipt.",
            "consequence": "Opening the wrong transaction means you're working in the wrong module. For hazmat, posting in the wrong transaction could bypass DOT-mandated safety checks entirely.",
            "explore_info": [
                "Goods Movement (MIGO) — this is where you post receipts, issues, and transfers for hazmat. Your main tool for receiving chemicals. Look for the star icon.",
                "Safety Data Sheet (SDS) — critical for hazmat. All materials must have SDS verified before posting. Required by OSHA and DOT.",
                "Emergency Response Guide (ERG) — chemical emergency responders use this. Indexed by UN number. Correct UN classification is life-and-death critical.",
                "Purchase Order — references the PO for this chemical shipment. Matches vendor, UN numbers, and quantities.",
                "Hazmat Compliance Dashboard — ChemCo custom tile showing today's hazmat deliveries and Tier II reporting status.",
                "Receiving Dock — shows expected hazmat arrivals. Cross-check the truck against the PO before unloading.",
            ],
        },
        {
            "screen":      "migo_action.png",
            "goal":        "Set the action to Goods Receipt",
            "instruction": "Confirm the Action dropdown is set to 'Goods Receipt'. Click it.",
            "hint":        "The Action dropdown is the first field in the transaction header.",
            "hotspot":     {"x": 36, "y": 148, "w": 220, "h": 36},
            "feedback":    "Correct. Action = Goods Receipt. Now set the reference type.",
            "consequence": "Selecting 'Goods Issue' instead of 'Goods Receipt' would remove hazmat inventory. DOT/OSHA sees a phantom chemical on-site with no matching record — that's a compliance violation and potential fine.",
            "explore_info": [
                "Action — tells SAP what kind of goods movement you're doing. For hazmat receiving: 'Goods Receipt' only. Never 'Goods Issue' or 'Transfer'.",
                "Reference Document — what you're posting against. Always a Purchase Order for hazmat receiving.",
                "Purchase Order No. — the PO number from your hazmat delivery paperwork. Links to vendor SDS package.",
                "Execute button — loads the PO data including UN numbers and hazmat classes into MIGO.",
            ],
        },
        {
            "screen":      "migo_reference.png",
            "goal":        "Set the reference document to Purchase Order",
            "instruction": "Click the Reference Document dropdown and select 'Purchase Order'.",
            "hint":        "The Reference Document dropdown is next to the Action dropdown.",
            "hotspot":     {"x": 280, "y": 148, "w": 220, "h": 36},
            "feedback":    "Good. Every hazmat GR at ChemCo must be tied to a PO.",
            "consequence": "Posting without a PO reference means the shipment can't be traced to the vendor's SDS package. In a spill or exposure event, emergency responders need to know exactly what's on-site.",
            "explore_info": [
                "Reference Document — links your receipt to an existing document. 'Purchase Order' is standard for hazmat receiving.",
                "PO traceability — the PO number connects to the vendor's chemical specification sheet and SDS. Critical for emergency response.",
                "Other reference types — 'Material Document' for reversals, 'Delivery' for inbound hazmat deliveries. You'll almost always use Purchase Order for hazmat.",
            ],
        },
        {
            "screen":      "migo_po.png",
            "goal":        "Enter the Purchase Order number",
            "instruction": "Type the PO number into the Purchase Order No. field and press Enter.",
            "hint":        "The PO number field is to the right of the Reference Document dropdown.",
            "hotspot":     {"x": 524, "y": 148, "w": 200, "h": 36},
            "feedback":    "PO 4500033900 loaded. SAP pulled in the chemical line items automatically.",
            "consequence": "Wrong PO number links this receipt to the wrong chemical shipment. The UN numbers won't match, storage bay assignment is wrong, and in an emergency, responders get incorrect hazard information.",
            "explore_info": [
                "PO Number — find this on the hazmat delivery note or bill of lading. SAP auto-populates the UN numbers and classes when you press Enter.",
                "Execute button — loads the PO data into MIGO. Same as pressing Enter in the PO field.",
                "Tip — always double-check the PO number against the hazmat manifest before hitting Enter. Cross-reference with the truck placards.",
            ],
        },
        {
            "screen":      "migo_items.png",
            "goal":        "Verify line item quantities and UN numbers",
            "instruction": "Check the Qty and UN No. columns. Confirm the chemicals and quantities match the packing list.",
            "hint":        "Compare each quantity and UN number against your delivery paperwork before proceeding.",
            "hotspot":     {"x": 416, "y": 272, "w": 100, "h": 34},
            "feedback":    "Quantities and UN numbers verified. Never post hazmat without confirming UN classification.",
            "consequence": "Posting the wrong quantity for hazmat means your facility's Tier II report to the fire department is inaccurate. If acetone inventory exceeds threshold quantities without reporting, that's an OSHA/EPA violation.",
            "explore_info": [
                "Item — line number in the PO. Each chemical is a separate line.",
                "Material — SAP material number. Matches the hazmat product master.",
                "Description — human-readable chemical name and concentration.",
                "Qty — how many units (drums, carboys) you're receiving. Must match what's physically on the dock.",
                "UoM — Unit of Measure. DR = drums, CB = carboys, CS = cases.",
                "UN No. — UN classification number. Identifies the hazmat substance globally. Non-negotiable.",
                "Haz.Class — hazard classification. Class 3 = Flammable, Class 8 = Corrosive, etc. Must match the SDS.",
            ],
        },
        {
            "screen":      "migo_un.png",
            "goal":        "Verify UN number and hazmat class in item detail",
            "instruction": "Confirm the UN Number field and hazmat class dropdown. Check the SDS Verified checkbox.",
            "hint":        "UN Number field is mandatory for all hazmat. The hazmat class must match the Safety Data Sheet.",
            "hotspot":     {"x": 260, "y": 210, "w": 180, "h": 34},
            "feedback":    "UN number and hazmat class confirmed. SDS on file verified.",
            "consequence": "Wrong or missing UN number means the material is misclassified. In a spill, emergency responders consult the ERG by UN number. Wrong number = wrong response protocol = potential injuries or fatalities.",
            "explore_info": [
                "Material Number — the internal SAP material code. CH-1101 for Acetone, CH-2205 for HCl 37%.",
                "UN Number — the globally recognized hazmat identifier. UN1090 for Acetone, UN1789 for HCl 37%. MANDATORY.",
                "Hazmat Class — the classification. Class 3 = Flammable, Class 8 = Corrosive. Determines storage and response.",
                "SDS Verified — confirms the Safety Data Sheet is on file and current. Must be checked before posting hazmat.",
            ],
        },
        {
            "screen":      "migo_storage_class.png",
            "goal":        "Assign to correct hazmat storage bay",
            "instruction": "Click the Storage Location dropdown and select the appropriate hazmat bay.",
            "hint":        "Flammable chemicals → HAZ-A · Corrosive chemicals → HAZ-B · Segregation rules apply.",
            "hotspot":     {"x": 260, "y": 210, "w": 220, "h": 34},
            "feedback":    "Storage location set to hazmat bay. Incompatible materials kept separate.",
            "consequence": "Storing flammable and corrosive materials in the same bay violates NFPA and OSHA segregation rules. Acetone near hydrochloric acid can produce toxic fumes. This is a life-safety issue.",
            "explore_info": [
                "Plant — the physical facility. HC01 = ChemCo Houston.",
                "Storage Location — the hazmat bay. HAZ-A (Flammable, -20°C to +25°C), HAZ-B (Corrosive, ventilated), HAZ-C (Oxidizer, segregated).",
                "Movement Type — 101 = standard goods receipt against PO. Don't change this.",
                "Vendor — the chemical supplier. Auto-populated from the PO.",
                "Delivery Note — the DN number from the truck manifest.",
            ],
        },
        {
            "screen":      "migo_post.png",
            "goal":        "Post the Goods Receipt",
            "instruction": "Review the hazmat summary. Confirm UN numbers, classes, and emergency contact. Click Post.",
            "hint":        "Emergency contact (1-800-DOT-HELP) must be on file before posting hazmat.",
            "hotspot":     {"x": 20, "y": 88, "w": 80, "h": 32},
            "feedback":    "Posted! Material document created. Hazmat inventory updated. Emergency contact confirmed.",
            "consequence": "Clicking Check instead of Post runs validation but doesn't finalize the receipt. Clicking Cancel discards the hazmat data including UN classifications. The truck can't leave until the DOT manifest matches SAP.",
            "explore_info": [
                "Post — creates the material document and updates inventory. This is the final step. Generates compliance record for DOT/OSHA.",
                "Check — runs validation without posting. Use this if you're unsure and want SAP to flag errors first.",
                "Cancel — discards the entire hazmat goods receipt. You'll need to start over from the PO number.",
                "Hazmat Summary panel — shows everything you've entered: UN numbers, classes, storage locations, emergency contact. Review it before clicking Post.",
            ],
        },
    ],
    "mission": {
        "title":      "Your Mission",
        "briefing": (
            "Post a Goods Receipt for PO 4500033900.\n"
            "Acetone (CH-1101, 10 drums, UN1090, Class 3 Flammable) "
            "and Hydrochloric Acid 37% (CH-2205, 20 carboys, UN1789, Class 8 Corrosive) "
            "arriving at ChemCo Industrial DC, Houston TX.\n"
            "UN numbers and hazmat classes mandatory. Storage bay assignment required (HAZ-A for flammable, HAZ-B for corrosive). "
            "Emergency contact 1-800-DOT-HELP on file."
        ),
        "par_clicks": 12,
        "time_limit": 180,
        "narratives": [
            "The OSHA inspector just arrived for a surprise audit. She's reviewing your hazmat receiving procedures. Every UN number and storage assignment matters.",
            "The tanker truck driver needs the signed manifest before he can leave. DOT regulations — he's been here 40 minutes. Get the GR posted.",
            "A spill drill is scheduled for this afternoon. Your EHS manager wants all morning receipts posted and classified before the drill starts.",
            "New hire just completed HAZWOPER training. You're walking them through their first real hazmat receipt. Show them why segregation matters.",
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
    """Reusable MIGO hazmat line items table (y=210+) with UN numbers.
    blank_col: if set, blanks the values in that column (for L2/L3 challenge).
    decoy_cols: list of column indices to style as decoys (subtle blue tint).
    """
    d.text((36, 216), "Line Items", font=fnt(14, bold=True), fill=SAP_TEXT)
    cols = [("Item", 60), ("Material", 120), ("Description", 180),
            ("Qty", 80), ("UoM", 60), ("UN No.", 100), ("Haz.Class", 100)]
    row1 = ["0001", "CH-1101", "Acetone 55-gal drums", "10", "DR", "UN1090", "Class 3"]
    row2 = ["0002", "CH-2205", "HCl 37% 30L carboys", "20", "CB", "UN1789", "Class 8"]
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
    po_val = "4500033900" if hl else ""
    _header_row(d, po=po_val, hl_po=hl,
                decoy_ref=not hl, decoy_exec=not hl)
    placeholder_note(d)
    return img


def screen_migo_items(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — PO 4500033900")
    draw_subheader(d, "Goods Movement > MIGO")
    _header_row(d, po="4500033900")
    # Neutral: blank Qty (col 3) + decoy UN No. (5) and Haz.Class (6) columns
    _items_table(d, highlight_col=3 if hl else None,
                 blank_col=3 if not hl else None,
                 decoy_cols=[5, 6] if not hl else None)
    placeholder_note(d)
    return img


def screen_migo_un(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — Item Detail")
    draw_subheader(d, "Goods Movement > MIGO")
    draw_card(d, 20, 90, W - 20, 560,
              title="Item Detail — Line 0001: CH-1101 Acetone 55-gal drums")
    _draw_item_detail_tabs(d, active_idx=2)
    d.text((36, 170), "Material Tab — Hazmat Classification",
           font=fnt(13, bold=True), fill=SAP_LABEL)
    draw_field(d, 36,  210, 200, 34, "Material Number",      "CH-1101")
    # Neutral: blank UN number + decoy Hazmat Class dropdown and SDS checkbox
    un_val = "UN1090" if hl else ""
    draw_field(d, 260, 210, 180, 34, "UN Number", un_val, highlight=hl)
    draw_dropdown(d, 460, 210, 180, 34, "Hazmat Class", "Class 3 Flammable", decoy=not hl)
    draw_checkbox(d, 36, 278, "SDS Verified", checked=True, decoy=not hl)
    draw_status_banner(d, "⚠ Hazmat item — UN number mandatory before posting", ok=False)
    placeholder_note(d)
    return img


def screen_migo_storage_class(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — Item Detail")
    draw_subheader(d, "Goods Movement > MIGO")
    draw_card(d, 20, 90, W - 20, 560,
              title="Item Detail — Line 0001: CH-1101 Acetone 55-gal drums")
    _draw_item_detail_tabs(d, active_idx=0)
    d.text((36, 170), "Where Tab — Storage & Hazmat Assignment", font=fnt(13, bold=True), fill=SAP_LABEL)
    # Neutral: blank storage loc + decoy Plant and Movement Type
    draw_field(   d, 36,  210, 200, 34, "Plant",            "HC01",                         decoy=not hl)
    sloc_val = "HAZ-A (Flammable)" if hl else ""
    draw_dropdown(d, 260, 210, 220, 34, "Storage Location", sloc_val,                       highlight=hl)
    draw_field(   d, 504, 210, 200, 34, "Movement Type",    "101",                          decoy=not hl)
    draw_field(   d, 36,  278, 200, 34, "Vendor",           "NovoChem Supply")
    draw_field(   d, 260, 278, 220, 34, "Delivery Note",    "DN-20240215")
    placeholder_note(d)
    return img


def screen_migo_post(hl=True):
    img, d = new_screen("Goods Movement (MIGO) — Ready to Post")
    draw_subheader(d, "Goods Movement > MIGO")
    d.rectangle([0, 80, W, 116], fill=(248, 250, 252))
    d.line([(0, 116), (W, 116)], fill=SAP_BORDER, width=1)
    # Neutral: decoy Check and Cancel buttons
    draw_button(d, 20,  88, 80, 32, "Post",   primary=True,  highlight=hl)
    draw_button(d, 112, 88, 80, 32, "Check",  primary=False, decoy=not hl)
    draw_button(d, 204, 88, 80, 32, "Cancel", primary=False, decoy=not hl)
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
    """Generate highlighted + neutral PNGs. Called by ui_trainer.py.

    Output:
        screens/           ← highlighted variants (L0 Explore, L1 Guided)
        screens_neutral/   ← neutral variants   (L2 On Your Own, L3 Challenge)

    Returns highlighted_filenames.
    """
    screens_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = screens_dir.parent / "screens_neutral"
    neutral_dir.mkdir(parents=True, exist_ok=True)

    for fname, fn in SCREEN_GENERATORS.items():
        fn(hl=True).save(str(screens_dir / fname), "PNG")
        fn(hl=False).save(str(neutral_dir / fname), "PNG")

    names = list(SCREEN_GENERATORS.keys())
    return names
