"""
scenarios/base.py — Shared Pillow drawing helpers for UI trainer scenario packs.

All scenario packs import from here so the SAP Fiori chrome stays consistent
while the content (fields, values, highlights) varies per scenario.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1280, 720

# ── SAP Fiori colour palette ──────────────────────────────────────────────────
SAP_BLUE    = (0,   112, 242)   # #0070F2  primary brand blue
SAP_SHELL   = (3,   61,  128)   # #033D80  shell bar
SAP_GREY_BG = (244, 246, 248)   # #F4F6F8  page background
SAP_WHITE   = (255, 255, 255)
SAP_BORDER  = (204, 204, 204)   # #CCCCCC
SAP_TEXT    = (50,  50,  50)    # dark text
SAP_LABEL   = (107, 107, 107)   # field labels
SAP_AMBER   = (232, 118,   0)   # #E87600  hotspot / accent
SAP_GREEN   = (16,  126,  62)   # #107E3E
SAP_RED     = (187,   0,  11)   # #BB000B


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


def new_screen(title="SAP Fiori Launchpad"):
    """Create a blank screen with shell bar. Returns (img, draw)."""
    img = Image.new("RGB", (W, H), SAP_GREY_BG)
    d = ImageDraw.Draw(img)
    draw_shell_bar(d, title)
    return img, d


def placeholder_note(draw):
    draw.text((20, H - 28),
              "[ PLACEHOLDER — replace with real screenshot ]",
              font=fnt(11), fill=(160, 160, 160))


def draw_shell_bar(draw, title="SAP Fiori Launchpad", initials="USR"):
    draw.rectangle([0, 0, W, 48], fill=SAP_SHELL)
    draw.text((20, 14), "≡", font=fnt(20, bold=True), fill=SAP_WHITE)
    draw.text((56, 14), title, font=fnt(16, bold=True), fill=SAP_WHITE)
    draw.ellipse([W - 50, 10, W - 10, 38], fill=SAP_BLUE)
    draw.text((W - 44, 16), initials[:3], font=fnt(11, bold=True), fill=SAP_WHITE)


def draw_field(draw, x, y, w, h, label, value="", highlight=False):
    draw.text((x, y - 18), label, font=fnt(11), fill=SAP_LABEL)
    border_col = SAP_AMBER if highlight else SAP_BORDER
    lw = 2 if highlight else 1
    draw.rectangle([x, y, x + w, y + h], fill=SAP_WHITE, outline=border_col, width=lw)
    if value:
        draw.text((x + 8, y + 8), value, font=fnt(13), fill=SAP_TEXT)
    if highlight:
        draw.rectangle([x, y + h - 2, x + w, y + h], fill=SAP_AMBER)


def draw_dropdown(draw, x, y, w, h, label, value, highlight=False):
    draw_field(draw, x, y, w, h, label, value, highlight)
    arr_x = x + w - 24
    draw.polygon([(arr_x, y + 12), (arr_x + 12, y + 12), (arr_x + 6, y + 22)],
                 fill=SAP_BLUE if not highlight else SAP_AMBER)


def draw_button(draw, x, y, w, h, label, primary=True, highlight=False):
    col = SAP_AMBER if highlight else (SAP_BLUE if primary else SAP_GREY_BG)
    border = SAP_AMBER if highlight else (SAP_BLUE if primary else SAP_BORDER)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=4,
                            fill=col, outline=border, width=1)
    txt_col = SAP_WHITE if (primary or highlight) else SAP_TEXT
    draw.text((x + w // 2 - 20, y + h // 2 - 8), label,
              font=fnt(13, bold=True), fill=txt_col)


def draw_table_header(draw, x, y, columns):
    draw.rectangle([x, y, W - 40, y + 32], fill=(230, 235, 240))
    cx = x
    for col_label, col_w in columns:
        draw.text((cx + 6, y + 8), col_label, font=fnt(11, bold=True), fill=SAP_TEXT)
        draw.line([(cx + col_w, y), (cx + col_w, y + 32)], fill=SAP_BORDER, width=1)
        cx += col_w
    draw.line([(x, y + 32), (W - 40, y + 32)], fill=SAP_BORDER, width=1)


def draw_table_row(draw, x, y, columns, values, highlight_col=None):
    cx = x
    draw.rectangle([x, y, W - 40, y + 34], fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    for i, ((col_label, col_w), val) in enumerate(zip(columns, values)):
        bg = (255, 248, 235) if i == highlight_col else SAP_WHITE
        draw.rectangle([cx, y, cx + col_w, y + 34], fill=bg)
        draw.line([(cx + col_w, y), (cx + col_w, y + 34)], fill=SAP_BORDER, width=1)
        draw.text((cx + 6, y + 10), str(val), font=fnt(12), fill=SAP_TEXT)
        if i == highlight_col:
            draw.rectangle([cx, y + 32, cx + col_w, y + 34], fill=SAP_AMBER)
        cx += col_w


def draw_checkbox(draw, x, y, label, checked=False, highlight=False):
    border = SAP_AMBER if highlight else SAP_BORDER
    lw = 2 if highlight else 1
    draw.rectangle([x, y, x + 18, y + 18], fill=SAP_WHITE, outline=border, width=lw)
    if checked:
        draw.line([(x + 3, y + 9), (x + 7, y + 14), (x + 15, y + 4)],
                  fill=SAP_GREEN, width=2)
    draw.text((x + 26, y + 1), label, font=fnt(13), fill=SAP_TEXT)
    if highlight:
        draw.rectangle([x - 4, y - 4, x + 22, y + 22],
                       outline=SAP_AMBER, width=2)


def draw_subheader(draw, text):
    draw.rectangle([0, 48, W, 80], fill=SAP_WHITE)
    draw.text((20, 58), text, font=fnt(12), fill=SAP_LABEL)


def draw_card(draw, x, y, x2, y2, title=None):
    draw.rounded_rectangle([x, y, x2, y2], radius=4,
                            fill=SAP_WHITE, outline=SAP_BORDER, width=1)
    if title:
        draw.text((x + 16, y + 10), title, font=fnt(14, bold=True), fill=SAP_TEXT)
        draw.line([(x + 16, y + 30), (x2 - 16, y + 30)], fill=SAP_BORDER, width=1)


def draw_status_banner(draw, text, ok=True):
    col = (235, 250, 240) if ok else (255, 240, 240)
    border = SAP_GREEN if ok else SAP_RED
    icon = "✓" if ok else "✗"
    draw.rounded_rectangle([20, H - 100, W - 20, H - 50],
                            radius=4, fill=col, outline=border, width=1)
    draw.text((44, H - 84), f"{icon}  {text}",
              font=fnt(13, bold=True), fill=border)
