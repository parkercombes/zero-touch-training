#!/usr/bin/env python3
"""
ui_trainer.py — Game-style interactive UI trainer for SAP MIGO Goods Receipt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generates a self-contained interactive HTML training experience:
  • TUTORIAL MODE — pulsing spotlight guides the user through each UI element
  • MISSION MODE   — no hints; user completes a full GR transaction unassisted

Output: poc/output/ui_trainer/
  ├── index.html        ← open this in any browser, no server needed
  └── screens/          ← placeholder PNGs (swap with real SAP screenshots)
      ├── fiori_home.png
      ├── migo_action.png
      └── ...

To use real screenshots:
  1. Capture SAP Fiori screens at 1280×720 (or any consistent resolution)
  2. Name them to match the filenames in screens/
  3. Replace the placeholder PNGs — index.html updates automatically
  4. Adjust hotspot coordinates in SCENARIO below if element positions differ

Usage:
  pip install pillow
  python3 generators/ui_trainer.py
"""

import os, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1280, 720

# ── SAP Fiori colour palette ──────────────────────────────────────────────────
SAP_BLUE       = (0,   112, 242)   # #0070F2  primary brand blue
SAP_SHELL      = (3,   61,  128)   # #033D80  shell bar
SAP_GREY_BG    = (244, 246, 248)   # #F4F6F8  page background
SAP_WHITE      = (255, 255, 255)
SAP_BORDER     = (204, 204, 204)   # #CCCCCC
SAP_TEXT       = (50,  50,  50)    # dark text
SAP_LABEL      = (107, 107, 107)   # field labels
SAP_AMBER      = (232, 118,   0)   # #E87600  SE-DC accent / hotspot colour
SAP_GREEN      = (16,  126,  62)   # #107E3E
SAP_RED        = (187,   0,  11)   # #BB000B

def fnt(size=14, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_shell_bar(draw, title="SAP Fiori Launchpad"):
    """Draw SAP Fiori shell bar at top."""
    draw.rectangle([0, 0, W, 48], fill=SAP_SHELL)
    draw.text((20, 14), "≡", font=fnt(20, bold=True), fill=SAP_WHITE)
    draw.text((56, 14), title, font=fnt(16, bold=True), fill=SAP_WHITE)
    # User avatar placeholder
    draw.ellipse([W-50, 10, W-10, 38], fill=SAP_BLUE)
    draw.text((W-38, 16), "BPC", font=fnt(11, bold=True), fill=SAP_WHITE)

def draw_field(draw, x, y, w, h, label, value="", highlight=False):
    """Draw a labelled input field."""
    draw.text((x, y - 18), label, font=fnt(11), fill=SAP_LABEL)
    border_col = SAP_AMBER if highlight else SAP_BORDER
    lw = 2 if highlight else 1
    draw.rectangle([x, y, x+w, y+h], fill=SAP_WHITE, outline=border_col, width=lw)
    if value:
        draw.text((x+8, y+8), value, font=fnt(13), fill=SAP_TEXT)
    if highlight:
        draw.rectangle([x, y+h-2, x+w, y+h], fill=SAP_AMBER)

def draw_dropdown(draw, x, y, w, h, label, value, highlight=False):
    """Draw a labelled dropdown."""
    draw_field(draw, x, y, w, h, label, value, highlight)
    arr_x = x + w - 24
    draw.polygon([(arr_x, y+12), (arr_x+12, y+12), (arr_x+6, y+22)],
                 fill=SAP_BLUE if not highlight else SAP_AMBER)

def draw_button(draw, x, y, w, h, label, primary=True, highlight=False):
    """Draw a button."""
    col = SAP_AMBER if highlight else (SAP_BLUE if primary else SAP_GREY_BG)
    border = SAP_AMBER if highlight else (SAP_BLUE if primary else SAP_BORDER)
    draw.rounded_rectangle([x, y, x+w, y+h], radius=4,
                            fill=col, outline=border, width=1)
    txt_col = SAP_WHITE if (primary or highlight) else SAP_TEXT
    draw.text((x + w//2 - 20, y + h//2 - 8), label,
              font=fnt(13, bold=True), fill=txt_col)

def draw_table_header(draw, x, y, columns):
    """Draw table header row."""
    draw.rectangle([x, y, W-40, y+32], fill=(230, 235, 240))
    cx = x
    for col_label, col_w in columns:
        draw.text((cx+6, y+8), col_label, font=fnt(11, bold=True), fill=SAP_TEXT)
        draw.line([(cx+col_w, y), (cx+col_w, y+32)], fill=SAP_BORDER, width=1)
        cx += col_w
    draw.line([(x, y+32), (W-40, y+32)], fill=SAP_BORDER, width=1)

def draw_table_row(draw, x, y, columns, values, highlight_col=None):
    """Draw a table data row with optional highlighted cell."""
    cx = x
    draw.rectangle([x, y, W-40, y+34], fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    for i, ((col_label, col_w), val) in enumerate(zip(columns, values)):
        bg = (255, 248, 235) if i == highlight_col else SAP_WHITE
        draw.rectangle([cx, y, cx+col_w, y+34], fill=bg)
        draw.line([(cx+col_w, y), (cx+col_w, y+34)], fill=SAP_BORDER, width=1)
        draw.text((cx+6, y+10), str(val), font=fnt(12), fill=SAP_TEXT)
        if i == highlight_col:
            draw.rectangle([cx, y+32, cx+col_w, y+34], fill=SAP_AMBER)
        cx += col_w

def draw_checkbox(draw, x, y, label, checked=False, highlight=False):
    """Draw a checkbox with label."""
    border = SAP_AMBER if highlight else SAP_BORDER
    lw = 2 if highlight else 1
    draw.rectangle([x, y, x+18, y+18], fill=SAP_WHITE, outline=border, width=lw)
    if checked:
        draw.line([(x+3, y+9), (x+7, y+14), (x+15, y+4)],
                  fill=SAP_GREEN, width=2)
    draw.text((x+26, y+1), label, font=fnt(13), fill=SAP_TEXT)
    if highlight:
        draw.rectangle([x-4, y-4, x+22, y+22],
                       outline=SAP_AMBER, width=2)

# ── Screen generators ─────────────────────────────────────────────────────────

def screen_fiori_home():
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, "SAP Fiori Launchpad")
    # Tile grid
    tiles = [
        ("Purchase\nRequisition", False),  ("Goods\nMovement\n(MIGO)", True),
        ("Inventory\nManagement",  False), ("Vendor\nInvoice",          False),
        ("Purchase\nOrder",        False), ("Receiving\nDock",          False),
    ]
    cols, rows = 3, 2
    tw, th = 200, 130
    gap = 24
    start_x = (W - (cols * tw + (cols-1) * gap)) // 2
    start_y = 100
    for i, (label, highlight) in enumerate(tiles):
        col, row = i % cols, i // cols
        x = start_x + col * (tw + gap)
        y = start_y + row * (th + gap)
        border = SAP_AMBER if highlight else SAP_BORDER
        bg = (255, 248, 235) if highlight else SAP_WHITE
        lw = 2 if highlight else 1
        d.rounded_rectangle([x, y, x+tw, y+th], radius=6,
                             fill=bg, outline=border, width=lw)
        # Icon area
        icon_col = SAP_AMBER if highlight else SAP_BLUE
        d.rounded_rectangle([x+tw//2-20, y+18, x+tw//2+20, y+58],
                             radius=4, fill=icon_col)
        for j, line in enumerate(label.split("\n")):
            d.text((x + tw//2 - 40, y+68 + j*18), line,
                   font=fnt(13, bold=highlight), fill=SAP_TEXT)
        if highlight:
            d.text((x+6, y+6), "★", font=fnt(12), fill=SAP_AMBER)
    # Placeholder note
    d.text((20, H-28), "[ PLACEHOLDER — replace with real SAP Fiori screenshot ]",
           font=fnt(11), fill=(160, 160, 160))
    return img

def screen_migo_action():
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, "Goods Movement (MIGO)")
    # Sub-header
    d.rectangle([0, 48, W, 80], fill=SAP_WHITE)
    d.text((20, 58), "Goods Movement > MIGO", font=fnt(12), fill=SAP_LABEL)
    # Transaction header card
    d.rounded_rectangle([20, 90, W-20, 200], radius=4,
                        fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    d.text((36, 100), "Transaction Header", font=fnt(14, bold=True), fill=SAP_TEXT)
    d.line([(36, 120), (W-36, 120)], fill=SAP_BORDER, width=1)
    # Action dropdown — HIGHLIGHTED
    draw_dropdown(d, 36, 148, 220, 36, "Action", "Goods Receipt", highlight=True)
    # Reference dropdown
    draw_dropdown(d, 280, 148, 220, 36, "Reference Document", "Purchase Order")
    # PO number
    draw_field(d, 524, 148, 200, 36, "Purchase Order No.", "")
    draw_button(d, 744, 148, 80, 36, "Execute")
    d.text((20, H-28), "[ PLACEHOLDER — replace with real SAP Fiori screenshot ]",
           font=fnt(11), fill=(160, 160, 160))
    return img

def screen_migo_reference():
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, "Goods Movement (MIGO)")
    d.rectangle([0, 48, W, 80], fill=SAP_WHITE)
    d.text((20, 58), "Goods Movement > MIGO", font=fnt(12), fill=SAP_LABEL)
    d.rounded_rectangle([20, 90, W-20, 200], radius=4,
                        fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    d.text((36, 100), "Transaction Header", font=fnt(14, bold=True), fill=SAP_TEXT)
    d.line([(36, 120), (W-36, 120)], fill=SAP_BORDER, width=1)
    draw_dropdown(d, 36, 148, 220, 36, "Action", "Goods Receipt")
    # Reference dropdown — HIGHLIGHTED
    draw_dropdown(d, 280, 148, 220, 36, "Reference Document", "Purchase Order", highlight=True)
    draw_field(d, 524, 148, 200, 36, "Purchase Order No.", "")
    draw_button(d, 744, 148, 80, 36, "Execute")
    d.text((20, H-28), "[ PLACEHOLDER — replace with real SAP Fiori screenshot ]",
           font=fnt(11), fill=(160, 160, 160))
    return img

def screen_migo_po():
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, "Goods Movement (MIGO)")
    d.rectangle([0, 48, W, 80], fill=SAP_WHITE)
    d.text((20, 58), "Goods Movement > MIGO", font=fnt(12), fill=SAP_LABEL)
    d.rounded_rectangle([20, 90, W-20, 200], radius=4,
                        fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    d.text((36, 100), "Transaction Header", font=fnt(14, bold=True), fill=SAP_TEXT)
    d.line([(36, 120), (W-36, 120)], fill=SAP_BORDER, width=1)
    draw_dropdown(d, 36, 148, 220, 36, "Action", "Goods Receipt")
    draw_dropdown(d, 280, 148, 220, 36, "Reference Document", "Purchase Order")
    # PO field — HIGHLIGHTED
    draw_field(d, 524, 148, 200, 36, "Purchase Order No.", "4500012345", highlight=True)
    draw_button(d, 744, 148, 80, 36, "Execute")
    d.text((20, H-28), "[ PLACEHOLDER — replace with real SAP Fiori screenshot ]",
           font=fnt(11), fill=(160, 160, 160))
    return img

def screen_migo_items():
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, "Goods Movement (MIGO) — PO 4500012345")
    d.rectangle([0, 48, W, 80], fill=SAP_WHITE)
    # Toolbar
    d.rounded_rectangle([20, 90, W-20, 200], radius=4,
                        fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    d.text((36, 100), "Transaction Header", font=fnt(14, bold=True), fill=SAP_TEXT)
    d.line([(36, 120), (W-36, 120)], fill=SAP_BORDER, width=1)
    draw_dropdown(d, 36, 148, 180, 30, "Action", "Goods Receipt")
    draw_dropdown(d, 236, 148, 180, 30, "Reference", "Purchase Order")
    draw_field(d, 436, 148, 150, 30, "PO Number", "4500012345")
    draw_button(d, 604, 148, 70, 30, "Execute")
    # Line items table
    d.text((36, 216), "Line Items", font=fnt(14, bold=True), fill=SAP_TEXT)
    cols = [("Item", 60), ("Material", 120), ("Description", 200),
            ("Qty", 100), ("UoM", 70), ("S.Loc", 100), ("Batch", 120)]
    draw_table_header(d, 36, 240, cols)
    # Row with Quantity highlighted
    draw_table_row(d, 36, 272, cols,
                   ["0001", "FZ-9921", "Frozen Burrito 12pk", "50", "CS", "ZONE-F", ""],
                   highlight_col=3)
    draw_table_row(d, 36, 306, cols,
                   ["0002", "RF-4410", "Chilled Salsa 6pk",  "24", "CS", "ZONE-R", ""],
                   highlight_col=None)
    d.text((20, H-28), "[ PLACEHOLDER — replace with real SAP Fiori screenshot ]",
           font=fnt(11), fill=(160, 160, 160))
    return img

def screen_migo_batch():
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, "Goods Movement (MIGO) — PO 4500012345")
    d.rectangle([0, 48, W, 80], fill=SAP_WHITE)
    d.rounded_rectangle([20, 90, W-20, 200], radius=4,
                        fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    d.text((36, 100), "Transaction Header", font=fnt(14, bold=True), fill=SAP_TEXT)
    d.line([(36, 120), (W-36, 120)], fill=SAP_BORDER, width=1)
    draw_dropdown(d, 36, 148, 180, 30, "Action", "Goods Receipt")
    draw_dropdown(d, 236, 148, 180, 30, "Reference", "Purchase Order")
    draw_field(d, 436, 148, 150, 30, "PO Number", "4500012345")
    draw_button(d, 604, 148, 70, 30, "Execute")
    d.text((36, 216), "Line Items", font=fnt(14, bold=True), fill=SAP_TEXT)
    cols = [("Item", 60), ("Material", 120), ("Description", 200),
            ("Qty", 100), ("UoM", 70), ("S.Loc", 100), ("Batch", 120)]
    draw_table_header(d, 36, 240, cols)
    # Batch column highlighted
    draw_table_row(d, 36, 272, cols,
                   ["0001", "FZ-9921", "Frozen Burrito 12pk", "50", "CS", "ZONE-F", "LOT-240201"],
                   highlight_col=6)
    draw_table_row(d, 36, 306, cols,
                   ["0002", "RF-4410", "Chilled Salsa 6pk",  "24", "CS", "ZONE-R", ""],
                   highlight_col=None)
    d.text((20, H-28), "[ PLACEHOLDER — replace with real SAP Fiori screenshot ]",
           font=fnt(11), fill=(160, 160, 160))
    return img

def screen_migo_storage():
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, "Goods Movement (MIGO) — Item Detail")
    d.rectangle([0, 48, W, 80], fill=SAP_WHITE)
    d.rounded_rectangle([20, 90, W-20, 560], radius=4,
                        fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    d.text((36, 100), "Item Detail — Line 0001: FZ-9921 Frozen Burrito 12pk",
           font=fnt(14, bold=True), fill=SAP_TEXT)
    # Tabs
    tabs = ["Where", "Quantity", "Material", "Account Assignment", "Purchase Order"]
    tx = 36
    for i, tab in enumerate(tabs):
        active = i == 0
        bg = SAP_WHITE if active else SAP_GREY_BG
        border_b = SAP_BLUE if active else SAP_BORDER
        d.rectangle([tx, 126, tx+len(tab)*8+20, 150], fill=bg, outline=SAP_BORDER, width=1)
        if active:
            d.rectangle([tx, 148, tx+len(tab)*8+20, 150], fill=SAP_BLUE)
        d.text((tx+8, 132), tab, font=fnt(12, bold=active), fill=SAP_BLUE if active else SAP_LABEL)
        tx += len(tab)*8 + 28
    d.line([(36, 150), (W-36, 150)], fill=SAP_BORDER, width=1)
    # Fields
    d.text((36, 170), "Where Tab — Storage Information", font=fnt(13, bold=True), fill=SAP_LABEL)
    draw_field(d, 36, 210, 200, 34, "Plant", "SE01")
    # Storage Location — HIGHLIGHTED
    draw_dropdown(d, 260, 210, 220, 34, "Storage Location", "ZONE-F (Frozen)", highlight=True)
    draw_field(d, 504, 210, 200, 34, "Movement Type", "101")
    draw_field(d, 36, 278, 200, 34, "Vendor", "V-00042")
    draw_field(d, 260, 278, 220, 34, "Delivery Note", "DN-20240201")
    d.text((20, H-28), "[ PLACEHOLDER — replace with real SAP Fiori screenshot ]",
           font=fnt(11), fill=(160, 160, 160))
    return img

def screen_migo_qi():
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, "Goods Movement (MIGO) — Item Detail")
    d.rectangle([0, 48, W, 80], fill=SAP_WHITE)
    d.rounded_rectangle([20, 90, W-20, 560], radius=4,
                        fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    d.text((36, 100), "Item Detail — Line 0001: FZ-9921 Frozen Burrito 12pk",
           font=fnt(14, bold=True), fill=SAP_TEXT)
    tabs = ["Where", "Quantity", "Material", "Account Assignment", "Purchase Order"]
    tx = 36
    for i, tab in enumerate(tabs):
        active = i == 2
        bg = SAP_WHITE if active else SAP_GREY_BG
        d.rectangle([tx, 126, tx+len(tab)*8+20, 150], fill=bg, outline=SAP_BORDER, width=1)
        if active:
            d.rectangle([tx, 148, tx+len(tab)*8+20, 150], fill=SAP_BLUE)
        d.text((tx+8, 132), tab, font=fnt(12, bold=active), fill=SAP_BLUE if active else SAP_LABEL)
        tx += len(tab)*8 + 28
    d.line([(36, 150), (W-36, 150)], fill=SAP_BORDER, width=1)
    d.text((36, 170), "Material Tab — Quality & Classification", font=fnt(13, bold=True), fill=SAP_LABEL)
    draw_field(d, 36, 210, 200, 34, "Material Number", "FZ-9921")
    draw_field(d, 260, 210, 220, 34, "Material Description", "Frozen Burrito 12pk")
    draw_field(d, 36, 278, 200, 34, "Purchasing Group", "R-SE")
    # QI Checkbox — HIGHLIGHTED
    draw_checkbox(d, 36, 350, "Quality Inspection Required", checked=False, highlight=True)
    draw_checkbox(d, 36, 390, "Cold Chain Verification", checked=True)
    draw_checkbox(d, 36, 430, "Private Label Item", checked=True)
    d.text((20, H-28), "[ PLACEHOLDER — replace with real SAP Fiori screenshot ]",
           font=fnt(11), fill=(160, 160, 160))
    return img

def screen_migo_post():
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, "Goods Movement (MIGO) — Ready to Post")
    d.rectangle([0, 48, W, 80], fill=SAP_WHITE)
    # Toolbar with Post button highlighted
    d.rectangle([0, 80, W, 116], fill=(248, 250, 252))
    d.line([(0, 116), (W, 116)], fill=SAP_BORDER, width=1)
    draw_button(d, 20, 88, 80, 32, "Post", primary=True, highlight=True)
    draw_button(d, 112, 88, 80, 32, "Check", primary=False)
    draw_button(d, 204, 88, 80, 32, "Cancel", primary=False)
    # Summary card
    d.rounded_rectangle([20, 126, W-20, 320], radius=4,
                        fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    d.text((36, 136), "Ready to Post — Summary", font=fnt(14, bold=True), fill=SAP_TEXT)
    d.line([(36, 156), (W-36, 156)], fill=SAP_BORDER, width=1)
    summary = [
        ("Action",             "Goods Receipt against Purchase Order"),
        ("Purchase Order",     "4500012345"),
        ("Line Items",         "2 items"),
        ("Storage Locations",  "ZONE-F (Frozen), ZONE-R (Refrigerated)"),
        ("Batch Tracking",     "✓ Lot numbers entered"),
        ("Quality Inspection", "✓ Flagged for QA review"),
    ]
    sy = 166
    for label, value in summary:
        d.text((36, sy), label + ":", font=fnt(12, bold=True), fill=SAP_LABEL)
        d.text((220, sy), value, font=fnt(12), fill=SAP_TEXT)
        sy += 24
    # Green checkmark status
    d.rounded_rectangle([20, 330, W-20, 390], radius=4,
                        fill=(235, 250, 240), outline=SAP_GREEN, width=1)
    d.text((44, 352), "✓  All validations passed. Click Post to complete the Goods Receipt.",
           font=fnt(13, bold=True), fill=SAP_GREEN)
    d.text((20, H-28), "[ PLACEHOLDER — replace with real SAP Fiori screenshot ]",
           font=fnt(11), fill=(160, 160, 160))
    return img


# ── Scenario definition ───────────────────────────────────────────────────────
# hotspot: {x, y, w, h} — pixel rectangle of the clickable target on the screen
# tolerance: extra px around hotspot that still counts as a correct click

SCENARIO = {
    "title": "Goods Receipt in SAP MIGO",
    "site": "GlobalMart SE-DC · Atlanta, GA",
    "role": "Buyer",
    "tutorial": [
        {
            "screen": "fiori_home.png",
            "goal": "Open the MIGO transaction",
            "instruction": "Click the MIGO tile to open Goods Movement.",
            "hint": "Look for the 'Goods Movement (MIGO)' tile — it has a star icon.",
            "hotspot": {"x": 473, "y": 162, "w": 200, "h": 130},
            "feedback": "Nice! MIGO is open. Now let's configure your Goods Receipt.",
        },
        {
            "screen": "migo_action.png",
            "goal": "Set the action to Goods Receipt",
            "instruction": "Confirm the Action dropdown is set to 'Goods Receipt'. Click it.",
            "hint": "The Action dropdown is the first field in the transaction header.",
            "hotspot": {"x": 36, "y": 148, "w": 220, "h": 36},
            "feedback": "Correct. Action = Goods Receipt. Now set the reference type.",
        },
        {
            "screen": "migo_reference.png",
            "goal": "Set the reference document to Purchase Order",
            "instruction": "Click the Reference Document dropdown and select 'Purchase Order'.",
            "hint": "The Reference Document dropdown is next to the Action dropdown.",
            "hotspot": {"x": 280, "y": 148, "w": 220, "h": 36},
            "feedback": "Good. Every GR at SE-DC must be tied to a PO.",
        },
        {
            "screen": "migo_po.png",
            "goal": "Enter the Purchase Order number",
            "instruction": "Type the PO number into the Purchase Order No. field and press Enter.",
            "hint": "The PO number field is to the right of the Reference Document dropdown.",
            "hotspot": {"x": 524, "y": 148, "w": 200, "h": 36},
            "feedback": "PO 4500012345 loaded. SAP pulled in the line items automatically.",
        },
        {
            "screen": "migo_items.png",
            "goal": "Verify line item quantities",
            "instruction": "Check the Qty column. Confirm it matches what's physically on your dock.",
            "hint": "Compare each line's quantity against your delivery paperwork before proceeding.",
            "hotspot": {"x": 450, "y": 272, "w": 100, "h": 34},
            "feedback": "Quantities verified. If anything is short, update it now — not after posting.",
        },
        {
            "screen": "migo_batch.png",
            "goal": "Enter the batch / lot number",
            "instruction": "Click the Batch field and enter the lot code from the pallet label.",
            "hint": "Batch entry is mandatory for all perishable items at SE-DC — enterprise says optional, we say required.",
            "hotspot": {"x": 650, "y": 272, "w": 120, "h": 34},
            "feedback": "Batch recorded. This is how we trace product in a recall.",
        },
        {
            "screen": "migo_storage.png",
            "goal": "Set the storage location (temperature zone)",
            "instruction": "Click the Storage Location dropdown and select the correct temperature zone.",
            "hint": "Zone-F = Frozen · Zone-R = Refrigerated · Zone-A = Ambient. Match the product.",
            "hotspot": {"x": 260, "y": 210, "w": 220, "h": 34},
            "feedback": "ZONE-F confirmed. Frozen product to the freezer. Cold chain maintained.",
        },
        {
            "screen": "migo_qi.png",
            "goal": "Check the Quality Inspection flag",
            "instruction": "Click the Quality Inspection Required checkbox.",
            "hint": "This is mandatory for perishable and private-label goods. QA will sign off before the stock ships.",
            "hotspot": {"x": 32, "y": 346, "w": 300, "h": 26},
            "feedback": "QI flagged. The QA team will receive a task automatically.",
        },
        {
            "screen": "migo_post.png",
            "goal": "Post the Goods Receipt",
            "instruction": "Click the Post button to complete the Goods Receipt.",
            "hint": "Review the summary first. Once you post, SAP generates the material document and updates inventory.",
            "hotspot": {"x": 20, "y": 88, "w": 80, "h": 32},
            "feedback": "Posted! Material document created. Inventory updated. Three-way match triggered. That product is officially in the building.",
        },
    ],
    "mission": {
        "title": "Your Mission",
        "briefing": (
            "Post a Goods Receipt for PO 4500012345.\n"
            "50 cases of Frozen Burrito (FZ-9921) arriving at the SE-DC receiving dock.\n"
            "Lot number: LOT-240201 · Temperature zone: ZONE-F · QI required."
        ),
        "par_clicks": 12,
    },
}


# ── HTML player (self-contained) ──────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GR in MIGO — Interactive UI Trainer · GlobalMart SE-DC</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0a0a1a;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    color: #fff;
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  /* ── Top HUD ── */
  #hud {
    position: fixed; top: 0; left: 0; right: 0;
    height: 52px;
    background: rgba(3, 61, 128, 0.95);
    backdrop-filter: blur(8px);
    display: flex; align-items: center; gap: 16px;
    padding: 0 20px;
    z-index: 100;
    border-bottom: 2px solid rgba(0,112,242,0.6);
  }
  #hud-title { font-size: 14px; font-weight: 700; color: #fff; flex: 1; }
  #hud-mode  { font-size: 11px; font-weight: 700; letter-spacing: 1px;
               background: #E87600; color: #fff; padding: 3px 10px;
               border-radius: 12px; text-transform: uppercase; }
  #hud-step  { font-size: 13px; color: #a0c4ff; }
  #progress-bar-wrap { width: 200px; height: 6px; background: rgba(255,255,255,0.15);
                       border-radius: 3px; overflow: hidden; }
  #progress-bar { height: 100%; background: #E87600; border-radius: 3px;
                  transition: width 0.4s ease; }
  #score-badge { font-size: 12px; background: rgba(255,255,255,0.1);
                 padding: 4px 12px; border-radius: 12px; color: #e0e0e0; }

  /* ── Screen container ── */
  #screen-wrap {
    position: relative;
    margin-top: 52px;
    width: 100%;
    max-width: 1280px;
    cursor: crosshair;
  }
  #screen-img {
    display: block;
    width: 100%;
    height: auto;
    user-select: none;
    -webkit-user-drag: none;
  }

  /* ── Dark overlay with spotlight ── */
  #overlay {
    position: absolute; inset: 0;
    pointer-events: none;
    transition: opacity 0.3s;
  }
  #overlay canvas { display: block; width: 100%; height: 100%; }

  /* ── Click catcher ── */
  #click-layer {
    position: absolute; inset: 0;
    cursor: crosshair;
  }

  /* ── Goal card ── */
  #goal-card {
    position: fixed;
    bottom: 20px; left: 50%; transform: translateX(-50%);
    width: min(680px, 90vw);
    background: rgba(3, 20, 50, 0.92);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0,112,242,0.5);
    border-radius: 12px;
    padding: 18px 22px;
    z-index: 200;
    transition: opacity 0.3s, transform 0.3s;
  }
  #goal-label {
    font-size: 10px; font-weight: 700; letter-spacing: 2px;
    color: #E87600; text-transform: uppercase; margin-bottom: 6px;
  }
  #goal-text { font-size: 17px; font-weight: 600; color: #fff; margin-bottom: 10px; line-height: 1.4; }
  #instruction-text { font-size: 13px; color: #a0c4ff; margin-bottom: 12px; line-height: 1.5; }
  #card-footer { display: flex; align-items: center; gap: 12px; }
  #hint-btn {
    font-size: 12px; padding: 6px 14px; border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.2); background: transparent;
    color: #a0c4ff; cursor: pointer; transition: background 0.2s;
  }
  #hint-btn:hover { background: rgba(255,255,255,0.1); }
  #hint-text { font-size: 12px; color: #ffd080; display: none; flex: 1; }
  #skip-btn { margin-left: auto; font-size: 12px; padding: 6px 14px;
              border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);
              background: transparent; color: #666; cursor: pointer; }
  #skip-btn:hover { color: #999; background: rgba(255,255,255,0.05); }

  /* ── Feedback flash ── */
  #feedback-flash {
    position: fixed; inset: 0; pointer-events: none; z-index: 300;
    display: flex; align-items: center; justify-content: center;
    opacity: 0; transition: opacity 0.15s;
  }
  #feedback-flash.show { opacity: 1; }
  #feedback-flash.correct { background: rgba(16, 126, 62, 0.25); }
  #feedback-flash.wrong   { background: rgba(187, 0, 11, 0.25); }
  #feedback-msg {
    background: rgba(0,0,0,0.85); padding: 20px 32px; border-radius: 12px;
    font-size: 16px; font-weight: 600; max-width: 500px; text-align: center;
    line-height: 1.5; border: 2px solid transparent;
  }
  .correct #feedback-msg { border-color: #107E3E; color: #6ee7a8; }
  .wrong   #feedback-msg { border-color: #BB000B; color: #ff8080; }

  /* ── Mission briefing overlay ── */
  #mission-screen {
    position: fixed; inset: 0; background: rgba(5, 10, 30, 0.97);
    display: flex; align-items: center; justify-content: center;
    z-index: 500; flex-direction: column; gap: 24px;
    display: none;
  }
  #mission-screen h2 { font-size: 32px; color: #E87600; letter-spacing: 2px; }
  #mission-briefing {
    font-size: 16px; line-height: 1.8; color: #c0d4ff; text-align: center;
    max-width: 600px; background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1); border-radius: 12px;
    padding: 24px 32px;
  }
  .btn-primary {
    font-size: 16px; font-weight: 700; padding: 14px 40px;
    border-radius: 8px; border: none; background: #0070F2; color: #fff;
    cursor: pointer; transition: background 0.2s, transform 0.1s;
  }
  .btn-primary:hover { background: #0060d0; }
  .btn-primary:active { transform: scale(0.97); }

  /* ── Win screen ── */
  #win-screen {
    position: fixed; inset: 0; background: rgba(5, 20, 10, 0.97);
    display: none; align-items: center; justify-content: center;
    z-index: 600; flex-direction: column; gap: 20px;
  }
  #win-screen h1 { font-size: 48px; color: #6ee7a8; }
  #win-screen p  { font-size: 18px; color: #a0c4ff; text-align: center; max-width: 480px; }
  #win-stats { font-size: 15px; color: #e0e0e0; text-align: center; }

  /* ── Mode switcher ── */
  #mode-select {
    position: fixed; top: 52px; right: 0;
    display: flex; gap: 0; z-index: 100;
  }
  .mode-btn {
    font-size: 11px; font-weight: 700; padding: 6px 16px;
    border: 1px solid rgba(255,255,255,0.15); cursor: pointer;
    letter-spacing: 0.5px; transition: background 0.2s;
  }
  .mode-btn.active { background: #E87600; border-color: #E87600; color: #fff; }
  .mode-btn:not(.active) { background: rgba(0,0,0,0.6); color: #a0c4ff; }

  @keyframes pulse-ring {
    0%   { transform: scale(1);    opacity: 0.9; }
    50%  { transform: scale(1.12); opacity: 0.4; }
    100% { transform: scale(1),    opacity: 0.9; }
  }
  @keyframes confetti { 0% { opacity:1; top:0; } 100% { opacity:0; top:100%; } }
</style>
</head>
<body>

<!-- HUD -->
<div id="hud">
  <div id="hud-title">SAP MIGO — Goods Receipt · GlobalMart SE-DC</div>
  <div id="hud-mode">Tutorial</div>
  <div id="hud-step">Step 1 of 9</div>
  <div id="progress-bar-wrap"><div id="progress-bar" style="width:11%"></div></div>
  <div id="score-badge">Score: 0</div>
</div>

<!-- Mode selector -->
<div id="mode-select">
  <button class="mode-btn active" onclick="setMode('tutorial')">Tutorial</button>
  <button class="mode-btn" onclick="setMode('mission')">Mission</button>
</div>

<!-- Screen -->
<div id="screen-wrap">
  <img id="screen-img" src="" alt="SAP screen" draggable="false">
  <div id="overlay"><canvas id="overlay-canvas"></canvas></div>
  <div id="click-layer" onclick="handleClick(event)"></div>
</div>

<!-- Goal card -->
<div id="goal-card">
  <div id="goal-label">Objective</div>
  <div id="goal-text"></div>
  <div id="instruction-text"></div>
  <div id="card-footer">
    <button id="hint-btn" onclick="showHint()">💡 Hint</button>
    <div id="hint-text"></div>
    <button id="skip-btn" onclick="nextStep(true)">Skip →</button>
  </div>
</div>

<!-- Feedback flash -->
<div id="feedback-flash">
  <div id="feedback-msg"></div>
</div>

<!-- Mission briefing -->
<div id="mission-screen">
  <h2>⚡ MISSION BRIEFING</h2>
  <div id="mission-briefing"></div>
  <button class="btn-primary" onclick="startMissionSteps()">Start Mission</button>
</div>

<!-- Win screen -->
<div id="win-screen">
  <h1>✅ GR Posted!</h1>
  <p id="win-msg"></p>
  <div id="win-stats"></div>
  <button class="btn-primary" onclick="restartMode()">Play Again</button>
</div>

<script>
// ── Scenario data (injected by generator) ────────────────────────────────────
const SCENARIO = __SCENARIO_JSON__;
const SCREENS  = __SCREENS_JSON__;  // { filename: "screens/foo.png" }

// ── State ─────────────────────────────────────────────────────────────────────
let mode      = 'tutorial';   // 'tutorial' | 'mission'
let stepIdx   = 0;
let score     = 0;
let wrongClicks = 0;
let totalClicks = 0;

const steps   = SCENARIO.tutorial;
const mission = SCENARIO.mission;

// ── DOM refs ──────────────────────────────────────────────────────────────────
const screenImg    = document.getElementById('screen-img');
const overlayCanvas= document.getElementById('overlay-canvas');
const hudMode      = document.getElementById('hud-mode');
const hudStep      = document.getElementById('hud-step');
const progressBar  = document.getElementById('progress-bar');
const scoreBadge   = document.getElementById('score-badge');
const goalText     = document.getElementById('goal-text');
const instrText    = document.getElementById('instruction-text');
const hintText     = document.getElementById('hint-text');
const feedbackEl   = document.getElementById('feedback-flash');
const feedbackMsg  = document.getElementById('feedback-msg');
const missionScreen= document.getElementById('mission-screen');
const winScreen    = document.getElementById('win-screen');
const modeButtons  = document.querySelectorAll('.mode-btn');

// ── Scale factor (screen rendered smaller than 1280px) ────────────────────────
function getScale() {
  return screenImg.getBoundingClientRect().width / 1280;
}

// ── Draw overlay ──────────────────────────────────────────────────────────────
function drawOverlay(step) {
  const rect = screenImg.getBoundingClientRect();
  const canvas = overlayCanvas;
  canvas.width  = rect.width;
  canvas.height = rect.height;
  const ctx   = canvas.getContext('2d');
  const scale = getScale();

  if (mode === 'mission') {
    // Mission: no spotlight, no ring — just subtle vignette
    ctx.fillStyle = 'rgba(0,0,0,0.06)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    return;
  }

  // Tutorial: dark overlay with spotlight cutout
  const hs = step.hotspot;
  const hx = hs.x * scale, hy = hs.y * scale;
  const hw = hs.w * scale, hh = hs.h * scale;
  const pad = 12 * scale;

  ctx.fillStyle = 'rgba(0,0,0,0.62)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Cut out spotlight
  ctx.clearRect(hx - pad, hy - pad, hw + pad*2, hh + pad*2);

  // Soft glow border
  ctx.strokeStyle = '#E87600';
  ctx.lineWidth = 3;
  ctx.shadowColor = '#E87600';
  ctx.shadowBlur = 18;
  ctx.beginPath();
  ctx.roundRect(hx - pad, hy - pad, hw + pad*2, hh + pad*2, 6);
  ctx.stroke();
  ctx.shadowBlur = 0;
}

// Animated pulse ring (CSS canvas animation)
let pulseAnim = null;
let pulsePhase = 0;
function startPulse(step) {
  stopPulse();
  const rect = screenImg.getBoundingClientRect();
  const scale = getScale();
  const hs = step.hotspot;
  const cx = (hs.x + hs.w/2) * scale;
  const cy = (hs.y + hs.h/2) * scale;
  const rx = (hs.w/2 + 16) * scale;
  const ry = (hs.h/2 + 16) * scale;

  function frame() {
    pulsePhase = (pulsePhase + 0.04) % (Math.PI * 2);
    const s = 1 + Math.sin(pulsePhase) * 0.08;
    const alpha = 0.5 + Math.sin(pulsePhase) * 0.3;
    drawOverlay(step);
    const ctx = overlayCanvas.getContext('2d');
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(s, s);
    ctx.strokeStyle = `rgba(232, 118, 0, ${alpha})`;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.ellipse(0, 0, rx/s, ry/s, 0, 0, Math.PI*2);
    ctx.stroke();
    ctx.restore();
    pulseAnim = requestAnimationFrame(frame);
  }
  pulseAnim = requestAnimationFrame(frame);
}
function stopPulse() {
  if (pulseAnim) { cancelAnimationFrame(pulseAnim); pulseAnim = null; }
}

// ── Load a step ───────────────────────────────────────────────────────────────
function loadStep(idx) {
  stepIdx = idx;
  hintText.style.display = 'none';
  const step = steps[idx];

  // Update screen image
  screenImg.src = SCREENS[step.screen];
  screenImg.onload = () => {
    overlayCanvas.width  = screenImg.getBoundingClientRect().width;
    overlayCanvas.height = screenImg.getBoundingClientRect().height;
    if (mode === 'tutorial') startPulse(step); else drawOverlay(step);
  };

  // Update HUD
  const total = steps.length;
  hudStep.textContent = `Step ${idx+1} of ${total}`;
  progressBar.style.width = `${((idx+1)/total)*100}%`;
  scoreBadge.textContent = `Score: ${score}`;

  // Update goal card
  goalText.textContent    = step.goal;
  instrText.textContent   = step.instruction;
  hintText.textContent    = step.hint;

  document.getElementById('hint-btn').style.display = mode === 'tutorial' ? '' : 'none';
  document.getElementById('skip-btn').style.display = mode === 'tutorial' ? '' : 'none';
}

// ── Click handler ─────────────────────────────────────────────────────────────
function handleClick(e) {
  const rect = screenImg.getBoundingClientRect();
  const scale = getScale();
  const mx = (e.clientX - rect.left) / scale;
  const my = (e.clientY - rect.top)  / scale;

  const step = steps[stepIdx];
  const hs   = step.hotspot;
  const tol  = 20; // tolerance pixels

  totalClicks++;
  const hit = mx >= hs.x - tol && mx <= hs.x + hs.w + tol &&
              my >= hs.y - tol && my <= hs.y + hs.h + tol;

  if (hit) {
    score += (mode === 'mission' ? 200 : 100) - (wrongClicks * 25);
    score = Math.max(score, 0);
    wrongClicks = 0;
    showFeedback('correct', mode === 'mission' ? '✓ Correct!' : step.feedback);
    setTimeout(() => nextStep(false), mode === 'mission' ? 800 : 2200);
  } else {
    wrongClicks++;
    showFeedback('wrong', mode === 'tutorial'
      ? 'Not quite — look for the highlighted area.'
      : 'Wrong element. Try again.');
    if (mode === 'tutorial') {
      setTimeout(() => { hintText.style.display = 'block'; }, 400);
    }
  }
}

function showFeedback(type, msg) {
  feedbackEl.className = `show ${type}`;
  feedbackMsg.textContent = msg;
  setTimeout(() => { feedbackEl.className = ''; }, type === 'correct' ? 2000 : 1200);
}

function showHint() {
  hintText.style.display = hintText.style.display === 'block' ? 'none' : 'block';
}

function nextStep(skip) {
  stopPulse();
  if (!skip) score += 50;
  if (stepIdx + 1 >= steps.length) {
    showWin();
  } else {
    loadStep(stepIdx + 1);
  }
}

// ── Win ───────────────────────────────────────────────────────────────────────
function showWin() {
  stopPulse();
  winScreen.style.display = 'flex';
  const acc = totalClicks > 0 ? Math.round((totalClicks - wrongClicks*2) / totalClicks * 100) : 100;
  document.getElementById('win-msg').textContent =
    mode === 'tutorial'
      ? 'You completed the Goods Receipt tutorial! Ready for the Mission?'
      : 'Goods Receipt posted successfully. Material document created. Three-way match triggered.';
  document.getElementById('win-stats').innerHTML =
    `Final Score: <strong>${score}</strong> &nbsp;|&nbsp; ` +
    `Accuracy: <strong>${Math.max(0,acc)}%</strong> &nbsp;|&nbsp; ` +
    `Mode: <strong>${mode === 'tutorial' ? 'Tutorial' : 'Mission'}</strong>`;
  scoreBadge.textContent = `Score: ${score}`;
}

function restartMode() {
  winScreen.style.display = 'none';
  score = 0; wrongClicks = 0; totalClicks = 0;
  loadStep(0);
}

// ── Mode switching ────────────────────────────────────────────────────────────
function setMode(m) {
  mode = m;
  winScreen.style.display = 'none';
  modeButtons.forEach(b => b.classList.toggle('active', b.textContent.toLowerCase() === m));
  hudMode.textContent = m === 'tutorial' ? 'Tutorial' : 'Mission';
  score = 0; wrongClicks = 0; totalClicks = 0;
  scoreBadge.textContent = 'Score: 0';

  if (m === 'mission') {
    missionScreen.style.display = 'flex';
    document.getElementById('mission-briefing').textContent = mission.briefing;
    document.getElementById('hint-btn').style.display = 'none';
  } else {
    missionScreen.style.display = 'none';
    loadStep(0);
  }
}

function startMissionSteps() {
  missionScreen.style.display = 'none';
  loadStep(0);
}

// ── Init ─────────────────────────────────────────────────────────────────────
window.addEventListener('resize', () => { if (steps[stepIdx]) loadStep(stepIdx); });
loadStep(0);
</script>
</body>
</html>
"""


# ── Build everything ──────────────────────────────────────────────────────────
def main():
    out_dir     = Path(__file__).parent.parent / "output" / "ui_trainer"
    screens_dir = out_dir / "screens"
    out_dir.mkdir(parents=True, exist_ok=True)
    screens_dir.mkdir(exist_ok=True)

    # Generate placeholder screens
    screen_fns = {
        "fiori_home.png":   screen_fiori_home,
        "migo_action.png":  screen_migo_action,
        "migo_reference.png": screen_migo_reference,
        "migo_po.png":      screen_migo_po,
        "migo_items.png":   screen_migo_items,
        "migo_batch.png":   screen_migo_batch,
        "migo_storage.png": screen_migo_storage,
        "migo_qi.png":      screen_migo_qi,
        "migo_post.png":    screen_migo_post,
    }
    print("Generating placeholder screens …")
    for fname, fn in screen_fns.items():
        path = screens_dir / fname
        fn().save(str(path), "PNG")
        print(f"  ✓  {fname}")

    # Build screens map for HTML (relative paths)
    screens_map = {fname: f"screens/{fname}" for fname in screen_fns}

    # Inject scenario + screens into HTML template
    html = HTML_TEMPLATE.replace(
        "__SCENARIO_JSON__", json.dumps(SCENARIO, indent=2)
    ).replace(
        "__SCREENS_JSON__", json.dumps(screens_map, indent=2)
    )

    index_path = out_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    print(f"\n✅  Done!")
    print(f"   Trainer : {index_path}")
    print(f"   Screens : {screens_dir}  ({len(screen_fns)} placeholder PNGs)")
    print(f"\n   Open with:  open \"{index_path}\"")
    print(f"\nTo use real screenshots:")
    print(f"   Capture SAP Fiori at 1280×720, name to match screens/*.png")
    print(f"   Drop into {screens_dir} — no other changes needed.")


if __name__ == "__main__":
    main()
