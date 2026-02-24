#!/usr/bin/env python3
"""
video_render_v2.py — Enhanced social media training video
Features: flite narration, xfade transitions, ambient music, improved slide design
Output:  720x1280 vertical reel, ~60-70s, H.264
"""

import os, sys, subprocess, tempfile, wave, struct, math, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── Constants ─────────────────────────────────────────────────────────────────
W, H     = 720, 1280
FPS      = 12
TRANS    = 0.5          # xfade/acrossfade duration (seconds)
PAD      = 0.6          # silence padding after narration

# Fonts
FONT_B = "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Colours
C_BG      = (15,  23,  42)   # slate-900
C_CARD    = (30,  41,  59)   # slate-800
C_BLUE    = (59, 130, 246)   # blue-500
C_BLUE_D  = (37,  99, 235)   # blue-600
C_AMBER   = (245,158, 11)    # amber-500
C_GREEN   = (34, 197, 94)    # green-500
C_WHITE   = (255,255,255)
C_LIGHT   = (226,232,240)    # slate-200
C_MID     = (148,163,184)    # slate-400
C_DIM     = (71,  85,105)    # slate-600

# ── Slide Definitions ─────────────────────────────────────────────────────────
SLIDES = [
    {
        "type": "title",
        "headline": "Zero-Touch\nTraining",
        "sub": "AI-Generated ERP Training\nGlobalMart SE-DC · Atlanta, GA",
        "narration": "Zero-Touch Training. AI-generated ERP training for GlobalMart Southeast Distribution Center in Atlanta.",
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
    },
    {
        "type": "idea",
        "headline": "The Core Idea",
        "body": "Training compiled from the same assets that keep the system running.",
        "narration": "Our core idea: instead of manually authoring courses, we compile training from the same assets that already keep the system running.",
    },
    {
        "type": "section",
        "label": "LAYER 1",
        "headline": "Navigation &\nOrientation",
        "goal": "I'm not lost.",
        "narration": "Layer One: Navigation and Orientation. The goal is simple — I am not lost.",
    },
    {
        "type": "layer",
        "label": "LAYER 1",
        "bullets": [
            "AI-generated navigation walkthroughs",
            "Site-specific menus and access paths",
            "Derived from UI metadata and test automation",
        ],
        "narration": "Layer One generates step-by-step navigation walkthroughs derived directly from UI metadata and automated test scripts.",
    },
    {
        "type": "section",
        "label": "LAYER 2",
        "headline": "End-to-End\nProcess",
        "goal": "I know where I fit.",
        "narration": "Layer Two: End-to-End Process Understanding. The goal is I know where I fit.",
    },
    {
        "type": "layer",
        "label": "LAYER 2",
        "bullets": [
            "AI-generated process explainer videos",
            "All roles, inputs, and outputs shown",
            "Minimal post-production required",
        ],
        "narration": "Layer Two produces process explainer videos showing every role, input, and output in a workflow — with minimal post-production.",
    },
    {
        "type": "section",
        "label": "LAYER 3",
        "headline": "Role-Specific\nExecution",
        "goal": "I can do my job.",
        "narration": "Layer Three: Role-Specific Execution. The goal is I can do my job.",
    },
    {
        "type": "layer",
        "label": "LAYER 3",
        "bullets": [
            "Short, task-focused job aids",
            "Generated from automated test scripts",
            "Includes site-specific Opal overlays",
        ],
        "narration": "Layer Three generates short job aids directly from automated test scripts, including site-specific overlays for each location.",
    },
    {
        "type": "section",
        "label": "LAYER 4",
        "headline": "In-App\nAssistance",
        "goal": "Help me while I\u2019m doing it.",
        "narration": "Layer Four: In-App Assistance. The goal is help me while I am doing it.",
    },
    {
        "type": "layer",
        "label": "LAYER 4",
        "bullets": [
            "WalkMe point-of-need guidance",
            "AI drafts flows from test scripts",
            "Experts review and approve all outputs",
        ],
        "narration": "Layer Four drafts WalkMe flows from test scripts. Subject matter experts review and approve every output before it goes live.",
    },
    {
        "type": "formula",
        "narration": "The Opal Overlay pattern assembles training by combining the enterprise process baseline, a site-specific overlay, and the learner role context.",
    },
    {
        "type": "poc",
        "narration": "The proof of concept generated seven complete training artifacts across all four content layers in a single two hundred ten second run.",
    },
    {
        "type": "soundbite",
        "narration": "We are not building training. We are compiling it from the same assets that already keep the system running.",
    },
    {
        "type": "end",
        "narration": "Zero-Touch Training. Governed, accurate, and always current. Subject matter experts stay in the loop — the pipeline does the heavy lifting.",
    },
]

# ── Font helpers ──────────────────────────────────────────────────────────────
def fnt(size, bold=False):
    path = FONT_B if bold else FONT_R
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def text_bbox(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]

def wrap_text(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        tw, _ = text_bbox(draw, test, font)
        if tw > max_w and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines

def draw_wrapped(draw, text, font, cx, y, max_w, fill, align="center", line_gap=8):
    lines = wrap_text(text, font, max_w, draw)
    for line in lines:
        tw, th = text_bbox(draw, line, font)
        if align == "center":
            x = cx - tw // 2
        elif align == "left":
            x = cx
        else:
            x = cx - tw
        draw.text((x, y), line, font=font, fill=fill)
        y += th + line_gap
    return y

def progress_bar(draw, idx, total):
    """Dots at top showing slide progress."""
    dot_r = 5
    spacing = 18
    total_w = total * (dot_r * 2) + (total - 1) * (spacing - dot_r * 2)
    start_x = (W - total_w) // 2
    y = 28
    for i in range(total):
        x = start_x + i * spacing
        col = C_BLUE if i == idx else C_DIM
        draw.ellipse([x, y, x + dot_r * 2, y + dot_r * 2], fill=col)

# ── Slide Renderers ───────────────────────────────────────────────────────────
def render_title(slide, idx, total):
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)

    # Top accent stripe
    draw.rectangle([0, 0, W, 6], fill=C_BLUE)
    progress_bar(draw, idx, total)

    # Big headline
    cy = 380
    for line in slide["headline"].split("\n"):
        f = fnt(88, bold=True)
        tw, th = text_bbox(draw, line, f)
        draw.text((W // 2 - tw // 2, cy), line, font=f, fill=C_WHITE)
        cy += th + 10

    # Accent divider
    draw.rectangle([W // 2 - 60, cy + 24, W // 2 + 60, cy + 28], fill=C_BLUE)

    # Sub
    cy += 52
    for line in slide["sub"].split("\n"):
        f = fnt(30)
        tw, th = text_bbox(draw, line, f)
        draw.text((W // 2 - tw // 2, cy), line, font=f, fill=C_MID)
        cy += th + 10

    # Bottom tag
    f = fnt(22)
    tag = "Training-as-Code  ·  DevSecOps Pipeline"
    tw, th = text_bbox(draw, tag, f)
    draw.text((W // 2 - tw // 2, H - 80), tag, font=f, fill=C_DIM)
    draw.rectangle([0, H - 6, W, H], fill=C_BLUE_D)
    return img

def render_problem(slide, idx, total):
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 6], fill=C_AMBER)
    progress_bar(draw, idx, total)

    # Headline
    f = fnt(60, bold=True)
    tw, th = text_bbox(draw, slide["headline"], f)
    draw.text((W // 2 - tw // 2, 140), slide["headline"], font=f, fill=C_WHITE)

    # Amber bar
    draw.rectangle([60, 220, W - 60, 224], fill=C_AMBER)

    # Bullets
    y = 290
    for b in slide["bullets"]:
        # Circle marker
        draw.ellipse([60, y + 8, 82, y + 30], fill=C_AMBER)
        f_b = fnt(34)
        cy = draw_wrapped(draw, b, f_b, 100, y, W - 130, C_LIGHT, align="left", line_gap=6)
        y = cy + 28

    draw.rectangle([0, H - 6, W, H], fill=C_AMBER)
    return img

def render_idea(slide, idx, total):
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 6], fill=C_BLUE)
    progress_bar(draw, idx, total)

    f_h = fnt(60, bold=True)
    tw, th = text_bbox(draw, slide["headline"], f_h)
    draw.text((W // 2 - tw // 2, 160), slide["headline"], font=f_h, fill=C_WHITE)

    # Card background for body
    draw.rounded_rectangle([50, 320, W - 50, 620], radius=20, fill=C_CARD)
    # Blue left border
    draw.rectangle([50, 320, 58, 620], fill=C_BLUE)

    f_b = fnt(36)
    draw_wrapped(draw, slide["body"], f_b, 90, 370, W - 150, C_LIGHT, align="left", line_gap=12)

    # Training-as-Code badge
    badge = "Training-as-Code"
    f_badge = fnt(26, bold=True)
    bw, bh = text_bbox(draw, badge, f_badge)
    bx = W // 2 - (bw + 40) // 2
    by = 680
    draw.rounded_rectangle([bx - 4, by - 4, bx + bw + 44, by + bh + 12], radius=12, fill=C_BLUE_D)
    draw.text((bx + 16, by), badge, font=f_badge, fill=C_WHITE)

    draw.rectangle([0, H - 6, W, H], fill=C_BLUE_D)
    return img

def render_section(slide, idx, total):
    img = Image.new("RGB", (W, H), C_BLUE_D)
    draw = ImageDraw.Draw(img)
    progress_bar(draw, idx, total)

    # Layer label
    f_label = fnt(32, bold=True)
    tw, th = text_bbox(draw, slide["label"], f_label)
    # Pill background
    px, py = W // 2 - tw // 2 - 20, 240
    draw.rounded_rectangle([px, py - 6, px + tw + 40, py + th + 10], radius=20, fill=(255, 255, 255, 60))
    draw.text((px + 20, py), slide["label"], font=f_label, fill=C_WHITE)

    # Headline
    cy = 360
    for line in slide["headline"].split("\n"):
        f = fnt(76, bold=True)
        tw, th = text_bbox(draw, line, f)
        draw.text((W // 2 - tw // 2, cy), line, font=f, fill=C_WHITE)
        cy += th + 8

    # Divider
    draw.rectangle([W // 2 - 50, cy + 24, W // 2 + 50, cy + 28], fill=C_WHITE)

    # Goal
    cy += 52
    goal = f'Goal: "{slide["goal"]}"'
    f_g = fnt(34)
    draw_wrapped(draw, goal, f_g, W // 2, cy, W - 100, (220, 230, 255), align="center", line_gap=8)
    return img

def render_layer(slide, idx, total):
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 6], fill=C_BLUE)
    progress_bar(draw, idx, total)

    # Layer badge
    f_label = fnt(26, bold=True)
    tw, th = text_bbox(draw, slide["label"], f_label)
    draw.rounded_rectangle([60 - 4, 70 - 4, 60 + tw + 24, 70 + th + 8], radius=10, fill=C_BLUE_D)
    draw.text((60 + 12, 70), slide["label"], font=f_label, fill=C_WHITE)

    # Bullets with card backgrounds
    y = 180
    for i, b in enumerate(slide["bullets"]):
        card_h = 110
        draw.rounded_rectangle([50, y, W - 50, y + card_h], radius=14, fill=C_CARD)
        # Number circle
        draw.ellipse([70, y + 28, 106, y + 64], fill=C_BLUE)
        f_n = fnt(24, bold=True)
        num = str(i + 1)
        nw, nh = text_bbox(draw, num, f_n)
        draw.text((88 - nw // 2, y + 46 - nh // 2), num, font=f_n, fill=C_WHITE)
        # Text
        f_b = fnt(30)
        draw_wrapped(draw, b, f_b, 122, y + 32, W - 180, C_LIGHT, align="left", line_gap=5)
        y += card_h + 16

    draw.rectangle([0, H - 6, W, H], fill=C_BLUE_D)
    return img

def render_formula(slide, idx, total):
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 6], fill=C_GREEN)
    progress_bar(draw, idx, total)

    f_h = fnt(48, bold=True)
    title = "The Opal Overlay Pattern"
    tw, th = text_bbox(draw, title, f_h)
    draw.text((W // 2 - tw // 2, 140), title, font=f_h, fill=C_WHITE)

    draw.rectangle([60, 224, W - 60, 228], fill=C_GREEN)

    # Formula parts
    parts = [
        ("Enterprise Process", C_BLUE,  340),
        ("+",                  C_WHITE, 470),
        ("Site Overlay",       C_AMBER, 530),
        ("+",                  C_WHITE, 660),
        ("Role Context",       C_GREEN, 720),
        ("=",                  C_WHITE, 860),
        ("Delivered Training", C_WHITE, 930),
    ]
    for text, color, y in parts:
        f = fnt(42, bold=(text not in ("+", "=")))
        tw, th = text_bbox(draw, text, f)
        draw.text((W // 2 - tw // 2, y), text, font=f, fill=color)

    draw.rectangle([0, H - 6, W, H], fill=C_GREEN)
    return img

def render_poc(slide, idx, total):
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 6], fill=C_BLUE)
    progress_bar(draw, idx, total)

    f_h = fnt(50, bold=True)
    tw, th = text_bbox(draw, "Proof of Concept", f_h)
    draw.text((W // 2 - tw // 2, 120), "Proof of Concept", font=f_h, fill=C_WHITE)
    draw.rectangle([60, 192, W - 60, 196], fill=C_BLUE)

    stats = [
        ("7",   "training artifacts generated"),
        ("4",   "content layers covered"),
        ("210", "seconds to generate everything"),
        ("1",   "role · 1 process · 1 site"),
    ]

    y = 240
    for num, label in stats:
        draw.rounded_rectangle([50, y, W - 50, y + 120], radius=14, fill=C_CARD)
        f_num = fnt(64, bold=True)
        nw, nh = text_bbox(draw, num, f_num)
        draw.text((100, y + 26), num, font=f_num, fill=C_BLUE)
        f_lbl = fnt(28)
        draw_wrapped(draw, label, f_lbl, 100 + nw + 20, y + 42, W - 220, C_LIGHT, align="left", line_gap=5)
        y += 136

    draw.rectangle([0, H - 6, W, H], fill=C_BLUE_D)
    return img

def render_soundbite(slide, idx, total):
    img = Image.new("RGB", (W, H), C_BLUE_D)
    draw = ImageDraw.Draw(img)
    progress_bar(draw, idx, total)

    # Big quotation mark
    f_q = fnt(200, bold=True)
    draw.text((50, 80), "\u201C", font=f_q, fill=(255, 255, 255, 40))

    quote = "We\u2019re not building training.\n\nWe\u2019re compiling it from the same assets that already keep the system running."
    y = 300
    for line in quote.split("\n"):
        if not line:
            y += 20
            continue
        f = fnt(38, bold=True)
        y = draw_wrapped(draw, line, f, W // 2, y, W - 100, C_WHITE, align="center", line_gap=8)
        y += 10

    draw.rectangle([0, H - 6, W, H], fill=C_WHITE)
    return img

def render_end(slide, idx, total):
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 6], fill=C_BLUE)
    progress_bar(draw, idx, total)

    f_h = fnt(70, bold=True)
    line1 = "Zero-Touch"
    line2 = "Training"
    for i, line in enumerate([line1, line2]):
        tw, th = text_bbox(draw, line, f_h)
        draw.text((W // 2 - tw // 2, 280 + i * 90), line, font=f_h, fill=C_WHITE)

    draw.rectangle([W // 2 - 60, 490, W // 2 + 60, 496], fill=C_BLUE)

    tags = ["Governed", "Accurate", "Always Current"]
    y = 530
    for tag in tags:
        f_t = fnt(32)
        tw, th = text_bbox(draw, tag, f_t)
        draw.text((W // 2 - tw // 2, y), tag, font=f_t, fill=C_MID)
        y += th + 14

    # SME badge
    sme = "Subject Matter Experts stay in the loop"
    f_s = fnt(26)
    draw.rounded_rectangle([50, 740, W - 50, 820], radius=14, fill=C_CARD)
    draw.rectangle([50, 740, 58, 820], fill=C_GREEN)
    tw, th = text_bbox(draw, sme, f_s)
    draw_wrapped(draw, sme, f_s, 80, 766, W - 130, C_LIGHT, align="left", line_gap=5)

    draw.rectangle([0, H - 6, W, H], fill=C_BLUE_D)
    return img

RENDERERS = {
    "title":     render_title,
    "problem":   render_problem,
    "idea":      render_idea,
    "section":   render_section,
    "layer":     render_layer,
    "formula":   render_formula,
    "poc":       render_poc,
    "soundbite": render_soundbite,
    "end":       render_end,
}

# ── Narration helpers ─────────────────────────────────────────────────────────
def gen_narration(text, out_wav, voice="slt"):
    """Generate narration using ffmpeg's libflite TTS. Returns duration in seconds.
    Uses textfile= to avoid filter-string parsing issues with colons and special chars."""
    # Write text to a temp file — avoids ALL ffmpeg filter escaping issues
    txt_path = out_wav + ".txt"
    clean = text.replace("\n", " ").replace("'", " ").replace('"', " ")
    with open(txt_path, "w") as f:
        f.write(clean)
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"flite=textfile='{txt_path}':voice={voice}",
        out_wav
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"flite failed: {r.stderr.decode()[:400]}")
    return probe_duration(out_wav)

def probe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", path],
        capture_output=True, text=True
    )
    for line in r.stdout.splitlines():
        if line.startswith("duration="):
            return float(line.split("=")[1])
    return 4.0

# ── Background music ──────────────────────────────────────────────────────────
def gen_music(duration_s, out_wav):
    sr = 44100
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)

    # Am  F  C  G chord loop
    chords = [
        [110.0, 130.8, 164.8],   # Am (lower octave — warmer)
        [87.3,  110.0, 130.8],   # F
        [130.8, 164.8, 196.0],   # C
        [98.0,  123.5, 146.8],   # G
    ]
    cd = duration_s / len(chords)
    audio = np.zeros(len(t))
    for i, freqs in enumerate(chords):
        s, e = int(i * cd * sr), int((i + 1) * cd * sr)
        st = t[s:e]
        for f in freqs:
            sig = np.sin(2 * math.pi * f * st) * 0.06
            sig += np.sin(2 * math.pi * f * 2 * st) * 0.02
            audio[s:e] += sig

    # Slow attack / fade-out
    fade = int(3 * sr)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)

    # Normalise to 20% of full scale (background feel)
    peak = np.max(np.abs(audio)) + 1e-9
    audio = audio / peak * 0.18
    pcm = (audio * 32767).astype(np.int16)

    with wave.open(out_wav, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

# ── Video builder ─────────────────────────────────────────────────────────────
def build_video(slide_pngs, narr_wavs, durations, music_wav, output_mp4):
    n = len(slide_pngs)
    assert n == len(narr_wavs) == len(durations)

    # Build inputs
    inputs = []
    for png, wav in zip(slide_pngs, narr_wavs):
        inputs += ["-loop", "1", "-t", str(durations[0]), "-i", png]  # placeholder dur
    # Fix: use actual durations per input
    inputs = []
    for i, (png, wav, dur) in enumerate(zip(slide_pngs, narr_wavs, durations)):
        inputs += ["-loop", "1", "-t", str(dur), "-i", png]
        inputs += ["-i", wav]

    # Build filter_complex
    # Video inputs are at indices 0, 2, 4, ...  (even)
    # Audio inputs are at indices 1, 3, 5, ...  (odd)
    vid_idx = [i * 2     for i in range(n)]
    aud_idx = [i * 2 + 1 for i in range(n)]
    music_idx = n * 2   # last input

    # Scale each video to exact size
    fc = []
    for i in range(n):
        fc.append(f"[{vid_idx[i]}:v]scale={W}:{H}:force_original_aspect_ratio=disable,setsar=1[v{i}]")

    # xfade video chain
    offsets, cum = [], 0.0
    for i in range(n - 1):
        cum += durations[i] - TRANS
        offsets.append(cum)

    prev = "v0"
    for i in range(n - 1):
        nxt = f"v{i+1}"
        out = f"xf{i}"
        fc.append(f"[{prev}][{nxt}]xfade=transition=fade:duration={TRANS}:offset={offsets[i]:.3f}[{out}]")
        prev = out
    video_out = prev  # final video label

    # acrossfade audio chain
    aprev = f"{aud_idx[0]}:a"
    for i in range(1, n):
        anxt = f"{aud_idx[i]}:a"
        aout = f"af{i-1}"
        fc.append(f"[{aprev}][{anxt}]acrossfade=d={TRANS}:c1=tri:c2=tri[{aout}]")
        aprev = aout
    audio_narr_out = aprev  # final narration audio label

    # Mix narration + background music
    total_dur = sum(durations) - (n - 1) * TRANS
    fc.append(f"[{music_idx}:a]volume=0.15,atrim=duration={total_dur:.3f}[music_trim]")
    fc.append(f"[{audio_narr_out}][music_trim]amix=inputs=2:duration=first[aout]")

    fc_str = "; ".join(fc)

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + ["-i", music_wav]
        + [
            "-filter_complex", fc_str,
            "-map", f"[{video_out}]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-r", str(FPS),
            output_mp4,
        ]
    )
    print("Running ffmpeg …")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("STDERR:", r.stderr[-1500:])
        raise RuntimeError("ffmpeg failed")
    print("ffmpeg done.")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    out_dir = Path("/sessions/adoring-clever-sagan/mnt/Development/zero-touch-training/poc/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    output_mp4 = str(out_dir / "training_video_v2_se-dc.mp4")

    tmp = tempfile.mkdtemp(prefix="ztt_v2_")
    print(f"Working in {tmp}")

    total = len(SLIDES)
    slide_pngs, narr_wavs, durations = [], [], []

    print("Generating narration + slides …")
    for i, slide in enumerate(SLIDES):
        print(f"  [{i+1}/{total}] {slide['type']} …", end="", flush=True)

        # Narration
        wav_path = os.path.join(tmp, f"narr_{i:02d}.wav")
        dur = gen_narration(slide["narration"], wav_path) + PAD
        dur = max(dur, 3.0)  # minimum 3 seconds per slide
        durations.append(dur)

        # Slide PNG
        png_path = os.path.join(tmp, f"slide_{i:02d}.png")
        renderer = RENDERERS.get(slide["type"], render_title)
        img = renderer(slide, i, total)
        img.save(png_path, "PNG")

        slide_pngs.append(png_path)
        narr_wavs.append(wav_path)
        print(f" {dur:.1f}s")

    total_dur = sum(durations) - (len(durations) - 1) * TRANS
    print(f"\nTotal video duration: {total_dur:.1f}s")

    # Background music
    print("Generating background music …")
    music_wav = os.path.join(tmp, "music.wav")
    gen_music(total_dur + 4, music_wav)

    # Assemble
    print("Assembling video …")
    build_video(slide_pngs, narr_wavs, durations, music_wav, output_mp4)

    # Stats
    size_mb = os.path.getsize(output_mp4) / 1e6
    print(f"\n✅  Output: {output_mp4}")
    print(f"   Size:   {size_mb:.1f} MB")
    print(f"   Duration: {total_dur:.1f}s  |  {total} slides  |  {FPS}fps  |  {W}x{H}")

    shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
