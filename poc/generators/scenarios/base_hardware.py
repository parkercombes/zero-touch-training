"""
scenarios/base_hardware.py — Pillow drawing helpers for hardware training scenarios.

Hardware scenarios use photographs or diagrams as base images instead of
generated SAP Fiori screens.  This module provides:

  1. Image loading (real photo or dev placeholder)
  2. Annotation helpers (highlight regions, numbered badges, callout arrows)
  3. HARDWARE_BRANDING dict (safety-orange / steel-grey palette)

All coordinates use the same 1280×720 canvas as the software scenarios so
the React trainer engine (hotspot overlay, scoring, levels) works unchanged.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw

# Re-use the shared font helper from base.py
from scenarios.base import fnt, W, H


# ── Hardware colour palette ──────────────────────────────────────────────────
HW_STEEL    = (60,  60,  60)      # dark steel grey   — shell / chrome
HW_ORANGE   = (255, 140,  0)      # safety orange      — accent / hotspots
HW_GREEN    = (34,  177,  76)     # machine-ready      — Level 0 / success
HW_BLUE     = (33,  150, 243)     # informational      — Level 1 / guided
HW_RED      = (229,  57,  53)     # danger / error      — Level 3 / challenge
HW_WHITE    = (255, 255, 255)
HW_BG       = (235, 235, 235)     # light workshop grey — canvas background
HW_LABEL    = (80,  80,  80)      # dark label text
HW_BORDER   = (180, 180, 180)

# ── Branding dict (mirrors SAP_BRANDING keys) ───────────────────────────────
HARDWARE_BRANDING = {
    "shell_color":   "#3C3C3C",
    "accent_color":  "#FF8C00",
    "level_colors":  ["#22B14C", "#2196F3", "#FF8C00", "#E53935"],
    "level_names":   ["OBSERVE", "FOLLOW ALONG", "DO IT", "SPEED RUN"],
    "level_descriptions": [
        "Study the equipment. No time pressure. Click around to learn each part.",
        "Follow each step with visual guidance. Build proper technique.",
        "No highlights. Hints cost time. Wrong moves show real consequences.",
        "Timed scenario. No help. Prove you can do it under pressure.",
    ],
}


# ═════════════════════════════════════════════════════════════════════════════
# IMAGE LOADING
# ═════════════════════════════════════════════════════════════════════════════

def load_base_image(path=None):
    """Load a photograph/diagram and resize to canvas, or return a placeholder.

    Args:
        path: str or Path to an image file.  If None or missing, a grey
              placeholder is generated (useful during scenario authoring
              before real photos are available).

    Returns:
        PIL.Image.Image sized to (W, H) = (1280, 720).
    """
    if path and Path(path).exists():
        img = Image.open(path).convert("RGB")
        img = img.resize((W, H), Image.LANCZOS)
        return img

    # Placeholder
    img = Image.new("RGB", (W, H), HW_BG)
    d = ImageDraw.Draw(img)
    # Grid lines to suggest a workbench / layout
    for x in range(0, W, 80):
        d.line([(x, 0), (x, H)], fill=(220, 220, 220), width=1)
    for y in range(0, H, 80):
        d.line([(0, y), (W, y)], fill=(220, 220, 220), width=1)
    d.text((W // 2 - 180, H // 2 - 12),
           "[ Hardware image placeholder ]",
           font=fnt(18), fill=(140, 140, 140))
    return img


# ═════════════════════════════════════════════════════════════════════════════
# ANNOTATION HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def annotate_region(img, hotspot, label="", hl=True, decoy=False):
    """Draw a highlight or decoy annotation around a hotspot region.

    Args:
        img:     PIL Image to draw on (modified in-place and returned).
        hotspot: dict with x, y, w, h (pixel coordinates on the 1280×720 canvas).
        label:   Optional text label shown near the region.
        hl:      If True, draw a prominent highlight (used for L0/L1 screens).
                 If False, draw nothing or a subtle hint (used for L2/L3).
        decoy:   If True, draw a decoy annotation (blue, to distract on neutral).

    Returns:
        The annotated PIL Image.
    """
    d = ImageDraw.Draw(img)
    x, y, w, h = hotspot["x"], hotspot["y"], hotspot["w"], hotspot["h"]
    pad = 6

    if hl:
        # Prominent safety-orange rounded rect + label
        d.rounded_rectangle(
            [x - pad, y - pad, x + w + pad, y + h + pad],
            radius=8, outline=HW_ORANGE, width=3,
        )
        if label:
            _draw_badge(d, x + w + pad + 8, y - pad + 2, label, HW_ORANGE)
    elif decoy:
        # Subtle blue outline to draw the eye on neutral screens
        d.rounded_rectangle(
            [x - pad, y - pad, x + w + pad, y + h + pad],
            radius=6, outline=HW_BLUE, width=2,
        )
        if label:
            _draw_badge(d, x + w + pad + 8, y - pad + 2, label, HW_BLUE)
    # else: no annotation (fully neutral for L2/L3 highlighted screens)

    return img


def _draw_badge(draw, x, y, text, color):
    """Draw a numbered/labelled circle badge at (x, y)."""
    text = str(text)
    r = max(14, len(text) * 5 + 10)
    draw.ellipse([x, y, x + r * 2, y + r * 2], fill=color)
    # Centre text in badge
    tw = len(text) * 7  # rough text width
    draw.text((x + r - tw // 2, y + r - 7), text,
              font=fnt(12, bold=True), fill=HW_WHITE)


def draw_callout(img, x, y, text, anchor="right"):
    """Draw a callout arrow + label pointing at a component.

    Args:
        img:    PIL Image.
        x, y:   Tip of the arrow (the point on the component).
        text:   Label text.
        anchor: "right" = label to the right of the point,
                "left"  = label to the left.

    Returns:
        The annotated PIL Image.
    """
    d = ImageDraw.Draw(img)
    arrow_len = 40
    if anchor == "right":
        x2 = x + arrow_len
        tx = x2 + 8
    else:
        x2 = x - arrow_len
        tx = x2 - len(text) * 8 - 8

    # Arrow line
    d.line([(x, y), (x2, y)], fill=HW_ORANGE, width=2)
    # Arrowhead
    d.polygon([(x, y), (x + (8 if anchor == "right" else -8), y - 4),
               (x + (8 if anchor == "right" else -8), y + 4)],
              fill=HW_ORANGE)
    # Label background
    tw = len(text) * 8 + 12
    d.rounded_rectangle([tx - 4, y - 12, tx + tw, y + 12],
                        radius=4, fill=HW_STEEL)
    d.text((tx + 2, y - 7), text, font=fnt(12, bold=True), fill=HW_WHITE)

    return img


def draw_component_label(img, x, y, w, h, label, sublabel=""):
    """Draw a labelled rectangle representing a hardware component (for placeholders).

    Args:
        img:      PIL Image.
        x, y:     Top-left corner.
        w, h:     Width and height of the component region.
        label:    Main label (e.g., "Bolt Catch Release").
        sublabel: Optional smaller text below (e.g., "Left side of receiver").

    Returns:
        The annotated PIL Image.
    """
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], radius=6,
                        fill=(250, 250, 250), outline=HW_BORDER, width=1)
    d.text((x + 10, y + 10), label, font=fnt(13, bold=True), fill=HW_LABEL)
    if sublabel:
        d.text((x + 10, y + 28), sublabel, font=fnt(11), fill=(120, 120, 120))
    return img


# ═════════════════════════════════════════════════════════════════════════════
# HARDWARE SCREEN HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def new_hardware_screen(title="Equipment View"):
    """Create a blank hardware-themed screen with a simple top bar.

    Returns (img, draw) — same contract as base.new_screen().
    """
    img = Image.new("RGB", (W, H), HW_BG)
    d = ImageDraw.Draw(img)
    # Simple steel-grey top bar (no SAP shell, no avatar)
    d.rectangle([0, 0, W, 48], fill=HW_STEEL)
    d.text((20, 14), title, font=fnt(16, bold=True), fill=HW_WHITE)
    return img, d


def hardware_status_banner(draw, text, ok=True):
    """Draw a status banner at the bottom of a hardware screen."""
    col = (220, 245, 230) if ok else (255, 230, 230)
    border = HW_GREEN if ok else HW_RED
    icon = "✓" if ok else "✗"
    draw.rounded_rectangle([20, H - 100, W - 20, H - 50],
                           radius=4, fill=col, outline=border, width=1)
    draw.text((44, H - 84), f"{icon}  {text}",
              font=fnt(13, bold=True), fill=border)


def placeholder_note(draw):
    """Placeholder note for hardware screens (same pattern as base.py)."""
    draw.text((20, H - 28),
              "[ PLACEHOLDER — replace with real photograph ]",
              font=fnt(11), fill=(160, 160, 160))
