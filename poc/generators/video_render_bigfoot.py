#!/usr/bin/env python3
"""
video_render_bigfoot.py — Bigfoot-quality social media training video
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uses:
  • OpenAI TTS (tts-1-hd, nova voice) — natural narration per slide
  • DALL-E 3 (1024x1792 portrait) — cinematic scene image per slide
  • NumPy — ambient background music (no external dependency)
  • Pillow — text/branding overlay composited on each image
  • ffmpeg — xfade transitions, audio mix, H.264 assembly

One-time Mac setup:
  brew install ffmpeg
  pip install openai pillow numpy

Usage:
  OPENAI_API_KEY="sk-..." python3 video_render_bigfoot.py
  # or place key in poc/.env as OPENAI_API_KEY=sk-...

Output: poc/output/training_video_bigfoot_se-dc.mp4
Estimated API cost: ~$0.90 per full run (TTS + 15 DALL-E images)
"""

import os, sys, json, time, math, wave, shutil, io, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import urllib.request, urllib.error

# ── Config ─────────────────────────────────────────────────────────────────
W, H      = 720, 1280
FPS       = 24
TRANS     = 0.5          # xfade crossfade duration (s)
PAD       = 0.4          # silence padding after each narration clip
TTS_MODEL = "tts-1-hd"   # or "tts-1" to reduce cost slightly
TTS_VOICE = "nova"       # alloy | echo | fable | onyx | nova | shimmer
IMG_SIZE  = "1024x1792"  # DALL-E 3 portrait — matches 9:16 aspect ratio
IMG_MODEL = "dall-e-3"

FONT_B = None   # resolved at runtime
FONT_R = None

# Mac font candidates (fallback chain)
MAC_BOLD = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
MAC_REG = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def find_font(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def fnt(size, bold=False):
    global FONT_B, FONT_R
    path = (FONT_B if bold else FONT_R) or find_font(MAC_BOLD if bold else MAC_REG)
    if bold:
        FONT_B = path
    else:
        FONT_R = path
    try:
        return ImageFont.truetype(path, size) if path else ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

# ── Colours ─────────────────────────────────────────────────────────────────
C_WHITE  = (255, 255, 255)
C_BLUE   = (59,  130, 246)
C_AMBER  = (245, 158,  11)
C_GREEN  = (34,  197,  94)
C_BLACK  = (0,     0,   0)
C_DIM    = (180,  180, 180)

# ── Slide Definitions ────────────────────────────────────────────────────────
# Each slide has: type, narration, headline (optional), sub/bullets,
# and image_prompt for DALL-E 3.
SLIDES = [
    {
        "type": "title",
        "headline": "Zero-Touch\nTraining",
        "sub": "AI-Generated ERP Training\nGlobalMart SE-DC · Atlanta, GA",
        "narration": "Zero-Touch Training. AI-generated ERP training for GlobalMart Southeast Distribution Center in Atlanta.",
        "image_prompt": (
            "Aerial view of a modern large-scale distribution center at golden hour, "
            "forklifts and loading docks, clean organized warehouse interior visible through "
            "glass walls, cinematic drone photography, photorealistic, no text"
        ),
    },
    {
        "type": "problem",
        "headline": "The Problem",
        "bullets": [
            "ERP training is expensive to create",
            "Quickly becomes outdated",
            "Detached from how systems change",
        ],
        "narration": "ERP training today is expensive to create, slow to update, and quickly becomes detached from how the system actually changes.",
        "image_prompt": (
            "Warehouse worker looking frustrated at a thick binder of printed training manuals, "
            "outdated documents on a desk, ERP system visible on a computer screen in the background, "
            "cinematic lighting, photorealistic, no text overlays"
        ),
    },
    {
        "type": "idea",
        "headline": "The Core Idea",
        "body": "Compile training from the assets that already keep the system running.",
        "narration": "Our core idea: instead of manually authoring courses, we compile training directly from the same assets that already keep the system running.",
        "image_prompt": (
            "Abstract visualization of data flowing from code and process diagrams into clean "
            "training documents, glowing blue pipeline, dark background, futuristic enterprise "
            "technology concept art, photorealistic render, no text"
        ),
    },
    {
        "type": "section",
        "label": "LAYER 1",
        "headline": "Navigation &\nOrientation",
        "goal": "I'm not lost.",
        "narration": "Layer One: Navigation and Orientation. The goal — I am not lost.",
        "image_prompt": (
            "Close-up of hands navigating a modern ERP software interface on a large monitor, "
            "SAP Fiori tiles visible, clean office environment, professional corporate photography, "
            "shallow depth of field, no text overlays"
        ),
    },
    {
        "type": "layer",
        "label": "LAYER 1",
        "bullets": [
            "AI-generated navigation walkthroughs",
            "Site-specific menus and access paths",
            "Derived from UI metadata and test automation",
        ],
        "narration": "Layer One generates step-by-step navigation walkthroughs directly from UI metadata and automated test scripts.",
        "image_prompt": (
            "Split screen showing automated test scripts on the left and clean step-by-step "
            "documentation on the right, connected by glowing arrows, dark tech background, "
            "cinematic corporate technology photography, no text"
        ),
    },
    {
        "type": "section",
        "label": "LAYER 2",
        "headline": "End-to-End\nProcess",
        "goal": "I know where I fit.",
        "narration": "Layer Two: End-to-End Process Understanding. The goal — I know where I fit.",
        "image_prompt": (
            "Business process flowchart visualized as glowing nodes and connecting lines, "
            "multiple team members represented as icons in a collaborative workflow, "
            "modern supply chain process visualization, dark background, cinematic, no text"
        ),
    },
    {
        "type": "layer",
        "label": "LAYER 2",
        "bullets": [
            "AI-generated process explainer videos",
            "All roles, inputs, and outputs shown",
            "Minimal post-production required",
        ],
        "narration": "Layer Two produces process explainer videos showing every role, every input, and every output — with minimal post-production.",
        "image_prompt": (
            "Modern video production setup with a process diagram being recorded, cinematic "
            "lighting, supply chain workflow displayed on a large screen behind the camera, "
            "professional corporate videography atmosphere, no text"
        ),
    },
    {
        "type": "section",
        "label": "LAYER 3",
        "headline": "Role-Specific\nExecution",
        "goal": "I can do my job.",
        "narration": "Layer Three: Role-Specific Execution. The goal — I can do my job.",
        "image_prompt": (
            "Warehouse associate scanning inventory with a handheld device, tablet showing "
            "a step-by-step job aid app, organized warehouse shelving in background, "
            "professional corporate photography, good lighting, no text"
        ),
    },
    {
        "type": "layer",
        "label": "LAYER 3",
        "bullets": [
            "Short, task-focused job aids",
            "Generated from automated test scripts",
            "Site-specific Opal overlays included",
        ],
        "narration": "Layer Three generates short, task-focused job aids directly from automated test scripts, including site-specific overlays for each location.",
        "image_prompt": (
            "Tablet screen showing a clean, well-formatted digital job aid with numbered steps "
            "and checkboxes, warehouse environment visible in background, professional photo, "
            "crisp modern UI design visible on screen, no text"
        ),
    },
    {
        "type": "section",
        "label": "LAYER 4",
        "headline": "In-App\nAssistance",
        "goal": "Help me while I\u2019m doing it.",
        "narration": "Layer Four: In-App Assistance. The goal — help me while I am doing it.",
        "image_prompt": (
            "Computer screen showing software interface with a floating tooltip or guided overlay "
            "highlighting a key button, WalkMe-style UI guidance, clean modern enterprise software, "
            "office environment, professional photography, no text"
        ),
    },
    {
        "type": "layer",
        "label": "LAYER 4",
        "bullets": [
            "WalkMe point-of-need guidance",
            "AI drafts flows from test scripts",
            "Experts review and approve all outputs",
        ],
        "narration": "Layer Four drafts WalkMe guidance flows from test scripts. Subject matter experts review and approve every output before it goes live.",
        "image_prompt": (
            "Two professionals reviewing a digital workflow diagram on a large screen, "
            "one pointing at a step in the process, collaborative review meeting, modern office, "
            "enterprise software visible, professional corporate photography, no text"
        ),
    },
    {
        "type": "formula",
        "headline": "The Opal\nOverlay Pattern",
        "formula_parts": [
            ("Enterprise Process", C_BLUE),
            ("+  Site Overlay",    C_AMBER),
            ("+  Role Context",    C_GREEN),
            ("=  Delivered Training", C_WHITE),
        ],
        "narration": (
            "The Opal Overlay pattern combines the enterprise process baseline, "
            "a site-specific overlay, and the learner role context to produce delivered training."
        ),
        "image_prompt": (
            "Abstract layered architectural diagram showing three stacked translucent layers "
            "merging into one output, blue green amber color scheme, enterprise architecture "
            "visualization, dark background, cinematic tech art, photorealistic render, no text"
        ),
    },
    {
        "type": "poc",
        "headline": "Proof of Concept",
        "stats": [
            ("7",   "training artifacts generated"),
            ("4",   "content layers covered"),
            ("210s","total generation time"),
        ],
        "narration": (
            "Our proof of concept generated seven complete training artifacts "
            "across all four content layers in just two hundred and ten seconds — "
            "one role, one process, one site."
        ),
        "image_prompt": (
            "Clean analytics dashboard on a monitor showing successful metrics, green checkmarks, "
            "seven completed items, modern data visualization, professional office setting, "
            "celebratory atmosphere, cinematic corporate photography, no text"
        ),
    },
    {
        "type": "soundbite",
        "quote": "\u201cWe\u2019re not building training.\nWe\u2019re compiling it.\u201d",
        "narration": (
            "We are not building training. "
            "We are compiling it from the same assets that already keep the system running."
        ),
        "image_prompt": (
            "Dramatic close-up of code and process models on screen transforming into a polished "
            "training document, glowing transformation effect, dark moody background, "
            "cinematic tech photography, strong directional lighting, no text"
        ),
    },
    {
        "type": "end",
        "headline": "Zero-Touch\nTraining",
        "tags": ["Governed", "Accurate", "Always Current"],
        "sub": "Subject matter experts stay in the loop.\nThe pipeline does the heavy lifting.",
        "narration": (
            "Zero-Touch Training. Governed, accurate, and always current. "
            "Subject matter experts stay in the loop. The pipeline does the heavy lifting."
        ),
        "image_prompt": (
            "Modern distribution center at sunrise, warm golden light, organized and efficient "
            "operations visible, hopeful optimistic atmosphere, aerial cinematic photography, "
            "photorealistic, professional corporate imagery, no text"
        ),
    },
]

# ── OpenAI API helpers ───────────────────────────────────────────────────────
def oai_post(endpoint, payload, api_key, binary=False, retries=3):
    """POST to OpenAI API. Returns bytes if binary=True, else dict."""
    url = f"https://api.openai.com/v1/{endpoint}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read() if binary else json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:300]
            if e.code == 429 and attempt < retries - 1:
                wait = 20 * (attempt + 1)
                print(f"    rate-limited, waiting {wait}s …")
                time.sleep(wait)
                continue
            raise RuntimeError(f"OpenAI {e.code}: {body}")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5)
                continue
            raise
    raise RuntimeError("OpenAI request failed after retries")


def gen_tts(text, out_mp3, api_key, voice=TTS_VOICE):
    """Generate narration via OpenAI TTS API. Saves to out_mp3."""
    audio_bytes = oai_post(
        "audio/speech",
        {"model": TTS_MODEL, "voice": voice, "input": text},
        api_key,
        binary=True,
    )
    with open(out_mp3, "wb") as f:
        f.write(audio_bytes)


def gen_dalle(prompt, out_png, api_key):
    """Generate scene image via DALL-E 3. Saves to out_png (720x1280 cropped)."""
    resp = oai_post(
        "images/generations",
        {
            "model": IMG_MODEL,
            "prompt": prompt,
            "size": IMG_SIZE,
            "quality": "standard",
            "n": 1,
        },
        api_key,
    )
    img_url = resp["data"][0]["url"]

    # Download image
    with urllib.request.urlopen(img_url, timeout=30) as r:
        raw = r.read()

    # Resize to exact 720x1280
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img = img.resize((W, H), Image.LANCZOS)
    img.save(out_png, "PNG")


# ── Slide overlay renderer ──────────────────────────────────────────────────
def gradient_overlay(draw, top_alpha=180, bottom_alpha=220):
    """Draw a vertical gradient overlay (dark at top and bottom, lighter in middle)."""
    # Top gradient (title area)
    for y in range(280):
        a = int(top_alpha * (1 - y / 280))
        if a > 0:
            draw.rectangle([0, y, W, y + 1], fill=(0, 0, 0, a))
    # Bottom gradient (caption area)
    for y in range(H - 420, H):
        a = int(bottom_alpha * ((y - (H - 420)) / 420))
        if a > 0:
            draw.rectangle([0, y, W, y + 1], fill=(0, 0, 0, a))


def tbbox(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_wrapped_centered(draw, text, font, cx, y, max_w, fill, line_gap=8):
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        tw, _ = tbbox(draw, test, font)
        if tw > max_w and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    for line in lines:
        tw, th = tbbox(draw, line, font)
        draw.text((cx - tw // 2, y), line, font=font, fill=fill)
        y += th + line_gap
    return y


def render_overlay(slide, bg_path, out_png, idx, total):
    """Composite text + branding over the DALL-E background image."""
    base = Image.open(bg_path).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    gradient_overlay(draw)

    stype = slide["type"]

    # ── Progress dots (top) ──────────────────────────────────────────────────
    dot_r, spacing = 5, 18
    total_w = total * (dot_r * 2) + (total - 1) * (spacing - dot_r * 2)
    sx = (W - total_w) // 2
    for i in range(total):
        x = sx + i * spacing
        col = (*C_BLUE, 255) if i == idx else (255, 255, 255, 80)
        draw.ellipse([x, 22, x + dot_r * 2, 22 + dot_r * 2], fill=col)

    # ── Top accent bar ───────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 5], fill=(*C_BLUE, 230))

    # ── Slide-type specific content ──────────────────────────────────────────
    if stype == "title":
        y = 340
        for line in slide["headline"].split("\n"):
            f = fnt(86, bold=True)
            # Shadow
            draw.text((W // 2 - tbbox(draw, line, f)[0] // 2 + 2, y + 2), line, font=f, fill=(0, 0, 0, 160))
            draw.text((W // 2 - tbbox(draw, line, f)[0] // 2, y), line, font=f, fill=(*C_WHITE, 255))
            y += tbbox(draw, line, f)[1] + 8
        draw.rectangle([W // 2 - 50, y + 18, W // 2 + 50, y + 22], fill=(*C_BLUE, 220))
        y += 42
        for line in slide["sub"].split("\n"):
            f = fnt(30)
            draw.text((W // 2 - tbbox(draw, line, f)[0] // 2, y), line, font=f, fill=(220, 230, 255, 220))
            y += tbbox(draw, line, f)[1] + 8

    elif stype == "problem":
        f_h = fnt(60, bold=True)
        hw, hh = tbbox(draw, slide["headline"], f_h)
        draw.text((W // 2 - hw // 2, 120), slide["headline"], font=f_h, fill=(*C_WHITE, 255))
        draw.rectangle([W // 2 - 50, 192, W // 2 + 50, 196], fill=(*C_AMBER, 220))

        y = H - 400
        for b in slide["bullets"]:
            draw.ellipse([54, y + 6, 74, y + 26], fill=(*C_AMBER, 230))
            f_b = fnt(30)
            draw_wrapped_centered(draw, b, f_b, W // 2 + 20, y, W - 140, (240, 240, 240, 240))
            y += 56

    elif stype == "idea":
        f_h = fnt(56, bold=True)
        draw_wrapped_centered(draw, slide["headline"], f_h, W // 2, 110, W - 80, (*C_WHITE, 255), line_gap=6)
        draw.rectangle([W // 2 - 40, 196, W // 2 + 40, 200], fill=(*C_BLUE, 200))
        f_b = fnt(34)
        draw_wrapped_centered(draw, slide["body"], f_b, W // 2, H - 320, W - 100, (220, 230, 255, 230), line_gap=10)

    elif stype == "section":
        # Big centered label + goal at bottom
        f_lbl = fnt(30, bold=True)
        lw, lh = tbbox(draw, slide["label"], f_lbl)
        lx = W // 2 - lw // 2 - 16
        draw.rounded_rectangle([lx, 200, lx + lw + 32, 200 + lh + 14], radius=14, fill=(*C_BLUE, 200))
        draw.text((lx + 16, 207), slide["label"], font=f_lbl, fill=(*C_WHITE, 255))
        y = 280
        for line in slide["headline"].split("\n"):
            f = fnt(74, bold=True)
            fw, fh = tbbox(draw, line, f)
            draw.text((W // 2 - fw // 2 + 2, y + 2), line, font=f, fill=(0, 0, 0, 140))
            draw.text((W // 2 - fw // 2, y), line, font=f, fill=(*C_WHITE, 255))
            y += fh + 6
        # Goal pill at bottom
        goal = f'\u201c{slide["goal"]}\u201d'
        f_g = fnt(34)
        gw, gh = tbbox(draw, goal, f_g)
        gx = W // 2 - gw // 2 - 20
        draw.rounded_rectangle([gx, H - 200, gx + gw + 40, H - 200 + gh + 20], radius=16, fill=(0, 0, 0, 160))
        draw.text((gx + 20, H - 190), goal, font=f_g, fill=(200, 220, 255, 240))

    elif stype == "layer":
        f_lbl = fnt(26, bold=True)
        lw, lh = tbbox(draw, slide["label"], f_lbl)
        draw.rounded_rectangle([50, 80, 50 + lw + 28, 80 + lh + 12], radius=10, fill=(*C_BLUE, 200))
        draw.text((64, 86), slide["label"], font=f_lbl, fill=(*C_WHITE, 255))
        y = H - 380
        for i, b in enumerate(slide["bullets"]):
            draw.ellipse([54, y + 6, 74, y + 26], fill=(*C_GREEN, 220))
            f_b = fnt(30, bold=True)
            f_n = fnt(18, bold=True)
            draw.text((59, y + 7), str(i + 1), font=f_n, fill=(*C_WHITE, 255))
            draw_wrapped_centered(draw, b, fnt(30), W // 2 + 20, y + 2, W - 140, (240, 240, 240, 240))
            y += 56

    elif stype == "formula":
        f_h = fnt(50, bold=True)
        y = 100
        for line in slide["headline"].split("\n"):
            fw, fh = tbbox(draw, line, f_h)
            draw.text((W // 2 - fw // 2, y), line, font=f_h, fill=(*C_WHITE, 255))
            y += fh + 6
        draw.rectangle([W // 2 - 40, y + 14, W // 2 + 40, y + 18], fill=(*C_GREEN, 200))
        y = H - 460
        for text, color in slide["formula_parts"]:
            f = fnt(36, bold=True)
            fw, fh = tbbox(draw, text, f)
            draw.text((W // 2 - fw // 2, y), text, font=f, fill=(*color, 240))
            y += fh + 18

    elif stype == "poc":
        f_h = fnt(52, bold=True)
        hw, hh = tbbox(draw, slide["headline"], f_h)
        draw.text((W // 2 - hw // 2, 100), slide["headline"], font=f_h, fill=(*C_WHITE, 255))
        draw.rectangle([W // 2 - 40, 162, W // 2 + 40, 166], fill=(*C_BLUE, 200))
        y = H - 400
        for num, label in slide["stats"]:
            f_num = fnt(58, bold=True)
            f_lbl = fnt(28)
            nw, nh = tbbox(draw, num, f_num)
            lw, lh = tbbox(draw, label, f_lbl)
            draw.text((80, y), num, font=f_num, fill=(*C_BLUE, 255))
            draw.text((80 + nw + 16, y + 14), label, font=f_lbl, fill=(220, 230, 240, 220))
            y += nh + 20

    elif stype == "soundbite":
        y = 280
        for line in slide["quote"].split("\n"):
            f = fnt(54, bold=True)
            fw, fh = tbbox(draw, line, f)
            draw.text((W // 2 - fw // 2 + 2, y + 2), line, font=f, fill=(0, 0, 0, 150))
            draw.text((W // 2 - fw // 2, y), line, font=f, fill=(*C_WHITE, 255))
            y += fh + 10
        # Attribution line
        attr = "— Zero-Touch Training"
        f_a = fnt(28)
        aw, ah = tbbox(draw, attr, f_a)
        draw.text((W // 2 - aw // 2, y + 24), attr, font=f_a, fill=(180, 200, 240, 200))

    elif stype == "end":
        y = 280
        for line in slide["headline"].split("\n"):
            f = fnt(78, bold=True)
            fw, fh = tbbox(draw, line, f)
            draw.text((W // 2 - fw // 2 + 2, y + 2), line, font=f, fill=(0, 0, 0, 150))
            draw.text((W // 2 - fw // 2, y), line, font=f, fill=(*C_WHITE, 255))
            y += fh + 8
        draw.rectangle([W // 2 - 50, y + 16, W // 2 + 50, y + 20], fill=(*C_BLUE, 200))
        y = H - 360
        for tag in slide["tags"]:
            f_t = fnt(32)
            tw, th = tbbox(draw, tag, f_t)
            draw.text((W // 2 - tw // 2, y), tag, font=f_t, fill=(200, 220, 255, 200))
            y += th + 12
        y += 16
        for line in slide["sub"].split("\n"):
            f_s = fnt(26)
            sw, sh = tbbox(draw, line, f_s)
            draw.text((W // 2 - sw // 2, y), line, font=f_s, fill=(160, 180, 200, 180))
            y += sh + 8

    # ── ZTT brand watermark (bottom right) ──────────────────────────────────
    f_wm = fnt(20)
    draw.text((W - 100, H - 44), "ZTT · SE-DC", font=f_wm, fill=(255, 255, 255, 80))

    # Composite
    result = Image.alpha_composite(base, overlay).convert("RGB")
    result.save(out_png, "PNG")


# ── Audio helpers ────────────────────────────────────────────────────────────
def probe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", path],
        capture_output=True, text=True,
    )
    for line in r.stdout.splitlines():
        if line.startswith("duration="):
            return float(line.split("=")[1])
    return 4.0


def gen_music(duration_s, out_wav):
    """Ambient chord loop — Am F C G, synthesized with numpy."""
    sr = 44100
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
    chords = [
        [110.0, 130.8, 164.8],
        [87.3,  110.0, 130.8],
        [130.8, 164.8, 196.0],
        [98.0,  123.5, 146.8],
    ]
    cd = duration_s / len(chords)
    audio = np.zeros(len(t))
    for i, freqs in enumerate(chords):
        s, e = int(i * cd * sr), int((i + 1) * cd * sr)
        st = t[s:e]
        for f in freqs:
            audio[s:e] += np.sin(2 * math.pi * f * st) * 0.055
            audio[s:e] += np.sin(2 * math.pi * f * 2 * st) * 0.018
    fade = int(3 * sr)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)
    audio = audio / (np.max(np.abs(audio)) + 1e-9) * 0.15
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(out_wav, "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2)
        wf.setframerate(sr); wf.writeframes(pcm.tobytes())


# ── Video assembly ───────────────────────────────────────────────────────────
def build_video(slide_pngs, narr_mp3s, durations, music_wav, output_mp4):
    n = len(slide_pngs)
    inputs = []
    for png, mp3, dur in zip(slide_pngs, narr_mp3s, durations):
        inputs += ["-loop", "1", "-t", str(dur), "-i", png]
        inputs += ["-i", mp3]

    music_idx = n * 2
    vid_idx = [i * 2 for i in range(n)]
    aud_idx = [i * 2 + 1 for i in range(n)]

    fc = []
    for i in range(n):
        fc.append(f"[{vid_idx[i]}:v]scale={W}:{H}:force_original_aspect_ratio=disable,setsar=1[v{i}]")

    # xfade video chain
    cum = 0.0
    prev = "v0"
    for i in range(n - 1):
        cum += durations[i] - TRANS
        out = f"xf{i}"
        fc.append(f"[{prev}][v{i+1}]xfade=transition=fade:duration={TRANS}:offset={cum:.3f}[{out}]")
        prev = out

    # acrossfade audio chain
    aprev = f"{aud_idx[0]}:a"
    for i in range(1, n):
        aout = f"af{i-1}"
        fc.append(f"[{aprev}][{aud_idx[i]}:a]acrossfade=d={TRANS}:c1=tri:c2=tri[{aout}]")
        aprev = aout

    total_dur = sum(durations) - (n - 1) * TRANS
    fc.append(f"[{music_idx}:a]volume=0.12,atrim=duration={total_dur:.3f}[music]")
    fc.append(f"[{aprev}][music]amix=inputs=2:duration=first[aout]")

    cmd = (
        ["ffmpeg", "-y"]
        + inputs + ["-i", music_wav]
        + [
            "-filter_complex", "; ".join(fc),
            "-map", f"[{prev}]",
            "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-r", str(FPS),
            output_mp4,
        ]
    )
    print("  Assembling with ffmpeg …")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-2000:])
        raise RuntimeError("ffmpeg assembly failed")


# ── Main ─────────────────────────────────────────────────────────────────────
def load_api_key():
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        return key
    # Try poc/.env
    env_paths = [
        Path(__file__).parent.parent / ".env",
        Path(".env"),
    ]
    for ep in env_paths:
        if ep.exists():
            for line in ep.read_text().splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    if val:
                        return val
    return None


def main():
    api_key = load_api_key()
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set.")
        print("  Set it with:  export OPENAI_API_KEY='sk-...'")
        print("  Or add it to poc/.env as OPENAI_API_KEY=sk-...")
        sys.exit(1)

    out_dir = Path(__file__).parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_mp4 = str(out_dir / "training_video_bigfoot_se-dc.mp4")

    tmp = tempfile.mkdtemp(prefix="ztt_bigfoot_")
    print(f"Workspace: {tmp}")
    print(f"Slides: {len(SLIDES)}  |  TTS: {TTS_MODEL}/{TTS_VOICE}  |  Images: {IMG_MODEL}\n")

    total = len(SLIDES)
    slide_pngs, narr_mp3s, durations = [], [], []

    for i, slide in enumerate(SLIDES):
        print(f"[{i+1:02d}/{total}] {slide['type']}")

        # 1 — Generate DALL-E scene image
        raw_png = os.path.join(tmp, f"raw_{i:02d}.png")
        comp_png = os.path.join(tmp, f"slide_{i:02d}.png")
        print(f"       DALL-E 3 …", end="", flush=True)
        gen_dalle(slide["image_prompt"], raw_png, api_key)
        print(" ✓")

        # 2 — Generate TTS narration
        mp3_path = os.path.join(tmp, f"narr_{i:02d}.mp3")
        print(f"       TTS …", end="", flush=True)
        gen_tts(slide["narration"], mp3_path, api_key)
        dur = probe_duration(mp3_path) + PAD
        dur = max(dur, 3.5)
        durations.append(dur)
        print(f" ✓  ({dur:.1f}s)")

        # 3 — Render text overlay on image
        render_overlay(slide, raw_png, comp_png, i, total)
        slide_pngs.append(comp_png)
        narr_mp3s.append(mp3_path)

    total_dur = sum(durations) - (len(durations) - 1) * TRANS
    print(f"\nTotal duration: {total_dur:.1f}s")

    print("Generating background music …")
    music_wav = os.path.join(tmp, "music.wav")
    gen_music(total_dur + 4, music_wav)

    print("Assembling video …")
    build_video(slide_pngs, narr_mp3s, durations, music_wav, output_mp4)

    size_mb = os.path.getsize(output_mp4) / 1e6
    print(f"\n✅  Done: {output_mp4}")
    print(f"   {size_mb:.1f} MB  |  {total_dur:.1f}s  |  {W}x{H}  |  {FPS}fps")
    print(f"\nEstimated API cost: TTS ~${total * 0.02:.2f}  +  Images ~${total * 0.04:.2f}  =  ~${total * 0.06:.2f}")

    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
