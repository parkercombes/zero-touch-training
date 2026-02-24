#!/usr/bin/env python3
"""
Video Renderer — 60-second social media reel from training script.

Renders slide images with Pillow, assembles with ffmpeg concat demuxer.
Output: 720x1280 MP4 (9:16 vertical, ~60s)
"""

import os, re, shutil, subprocess
from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
BG = (15, 23, 42)
CARD = (30, 41, 59)
BLUE = (59, 130, 246)
WARN = (251, 191, 36)
GREEN = (34, 197, 94)
WHITE = (255, 255, 255)
GRAY = (148, 163, 184)

FDIR = "/usr/share/fonts/truetype/google-fonts"
def ft(name, sz):
    return ImageFont.truetype(os.path.join(FDIR, name), sz)

FB = lambda sz: ft("Poppins-Bold.ttf", sz)
FM = lambda sz: ft("Poppins-Medium.ttf", sz)
FL = lambda sz: ft("Poppins-Light.ttf", sz)


@dataclass
class Slide:
    stype: str
    head: str = ""
    body: str = ""
    dur: float = 3.5
    items: list = field(default_factory=list)


def wrap(text, f, mw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if f.getbbox(t)[2] <= mw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


def badge(d, txt, y, c=BLUE):
    f = FM(20)
    tw = f.getbbox(txt.upper())[2]
    x = (W - tw)//2 - 14
    d.rounded_rectangle([x, y, x+tw+28, y+34], radius=17, fill=c)
    d.text(((W-tw)//2, y+5), txt.upper(), font=f, fill=WHITE)


def pbar(d, pct):
    d.rectangle([0, H-4, W, H], fill=CARD)
    d.rectangle([0, H-4, int(W*pct), H], fill=BLUE)


# ─── Slides ───

def build_slides() -> list[Slide]:
    """Curated 60-second social reel — 17 slides."""
    return [
        Slide("title", "Purchase Requisition\nto Goods Receipt",
              "Buyer Training  •  GlobalMart SE-DC", 3.5),
        Slide("section", "THE PROCESS", dur=2.0),
        Slide("cap", "OVERVIEW",
              "Five roles work together: Requestor, Buyer, Category Manager, VP Supply Chain, and Receiving Clerk.", 4.0),
        Slide("cap", "OVERVIEW",
              "As a Buyer, you convert approved PRs into Purchase Orders and ensure cold chain compliance.", 4.0),
        Slide("section", "KEY STEPS", dur=2.0),
        Slide("cap", "PR CREATION",
              "Requestors create PRs in ME51N with material, quantity, and 7-day delivery window for perishables.", 4.0),
        Slide("callout", "SITE RULE",
              "At SE-DC, lot/batch tracking is mandatory for perishables and purchasing groups are restricted to R-SE or R-NAT only.", 5.0),
        Slide("decision", "APPROVAL",
              "Orders over $25K need 3-tier approval: Category Manager → Procurement Lead → VP Supply Chain.", 5.0),
        Slide("cap", "PO CREATION",
              "You convert the approved PR to a PO in ME21N — negotiate terms, verify suppliers, confirm delivery.", 4.0),
        Slide("callout", "TEMPERATURE",
              "Temperature zones must carry through: Zone-F (frozen), Zone-R (refrigerated), Zone-A (ambient).", 4.5),
        Slide("cap", "GOODS RECEIPT",
              "Receiving Clerks post in MIGO with cold chain verification — actual temperature recorded at the dock.", 4.0),
        Slide("callout", "QI REQUIRED",
              "Mandatory quality inspection for all perishable and private-label goods before stock integration.", 4.0),
        Slide("section", "REMEMBER", dur=2.0),
        Slide("takeaway", "Key Takeaways", items=[
            "R-SE / R-NAT groups only",
            "$25K threshold for perishables",
            "Mandatory lot/batch tracking",
            "Verify temperature zones",
            "Cold chain check at receiving",
        ], dur=5.5),
        Slide("end", "Training Complete",
              "GlobalMart SE-DC  •  Procurement Series", 3.0),
    ]


# ─── Renderers ───

def r_title(s):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 6], fill=BLUE)
    cx = W//2
    d.ellipse([cx-50, 340, cx+50, 440], fill=BLUE)
    d.text((cx-25, 362), "GM", font=FB(36), fill=WHITE)
    y = 490
    for ln in s.head.split("\n"):
        f = FB(42); tw = f.getbbox(ln)[2]
        d.text(((W-tw)//2, y), ln, font=f, fill=WHITE); y += 56
    y += 20
    for ln in s.body.split("\n"):
        f = FL(26); tw = f.getbbox(ln)[2]
        d.text(((W-tw)//2, y), ln, font=f, fill=GRAY); y += 36
    d.rectangle([0, H-6, W, H], fill=BLUE)
    return img

def r_section(s):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f = FB(44)
    lines = wrap(s.head, f, W-120)
    th = len(lines)*56
    y = (H-th)//2 - 16
    d.rectangle([(W//2-40), y-20, (W//2+40), y-14], fill=BLUE)
    for ln in lines:
        tw = f.getbbox(ln)[2]
        d.text(((W-tw)//2, y), ln, font=f, fill=WHITE); y += 56
    d.rectangle([(W//2-40), y+6, (W//2+40), y+12], fill=BLUE)
    return img

def r_cap(s, pct):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    badge(d, s.head, 80)
    f = FB(34); m = 56
    lines = wrap(s.body, f, W-m*2)
    lh = 48; th = len(lines)*lh
    sy = max(340, (H-th)//2)
    d.rounded_rectangle([m-28, sy-28, W-m+28, sy+th+28], radius=16, fill=CARD)
    for i, ln in enumerate(lines):
        d.text((m, sy+i*lh), ln, font=f, fill=WHITE)
    pbar(d, pct)
    return img

def r_callout(s, pct):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    badge(d, s.head, 80)
    d.rounded_rectangle([44, 180, W-44, 234], radius=10, fill=WARN)
    d.text((66, 192), "SE-DC SITE REQUIREMENT", font=FB(22), fill=BG)
    f = FB(32); m = 56
    lines = wrap(s.body, f, W-m*2)
    lh = 46; th = len(lines)*lh
    sy = 280
    d.rounded_rectangle([m-28, sy-28, W-m+28, sy+th+28], radius=16, fill=CARD)
    d.rectangle([m-28, sy-14, m-22, sy+th+14], fill=WARN)
    for i, ln in enumerate(lines):
        d.text((m, sy+i*lh), ln, font=f, fill=WHITE)
    pbar(d, pct)
    return img

def r_decision(s, pct):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    badge(d, "Decision Point", 80)
    cx, cy, sz = W//2, 250, 50
    d.polygon([(cx,cy-sz),(cx+sz,cy),(cx,cy+sz),(cx-sz,cy)], fill=BLUE)
    d.text((cx-8, cy-14), "?", font=FB(28), fill=WHITE)
    tw = FB(30).getbbox("$25,000")[2]
    d.text(((W-tw)//2, cy+sz+12), "$25,000", font=FB(30), fill=WARN)
    f = FB(32); m = 56
    lines = wrap(s.body, f, W-m*2)
    lh = 46; th = len(lines)*lh
    sy = 400
    d.rounded_rectangle([m-28, sy-28, W-m+28, sy+th+28], radius=16, fill=CARD)
    for i, ln in enumerate(lines):
        d.text((m, sy+i*lh), ln, font=f, fill=WHITE)
    pbar(d, pct)
    return img

def r_takeaway(s, pct):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f_h = FB(38); tw = f_h.getbbox(s.head)[2]
    d.text(((W-tw)//2, 160), s.head, font=f_h, fill=WHITE)
    d.rectangle([(W//2-40), 214, (W//2+40), 220], fill=BLUE)
    f = FM(28); y = 270
    for item in s.items:
        d.rounded_rectangle([72, y+2, 102, y+32], radius=6, outline=GREEN, width=2)
        d.text((78, y+2), "✓", font=FB(20), fill=GREEN)
        d.text((118, y+2), item, font=f, fill=WHITE)
        y += 56
    pbar(d, pct)
    return img

def r_end(s):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 6], fill=GREEN)
    cx = W//2
    d.ellipse([cx-50, 380, cx+50, 480], fill=GREEN)
    d.text((cx-12, 406), "✓", font=FB(42), fill=WHITE)
    f = FB(40); tw = f.getbbox(s.head)[2]
    d.text(((W-tw)//2, 520), s.head, font=f, fill=WHITE)
    y = 590
    for ln in s.body.split("\n"):
        f2 = FL(26); tw = f2.getbbox(ln)[2]
        d.text(((W-tw)//2, y), ln, font=f2, fill=GRAY); y += 36
    d.rectangle([0, H-6, W, H], fill=GREEN)
    return img


RENDERERS = {
    "title": lambda s, p: r_title(s),
    "section": lambda s, p: r_section(s),
    "cap": r_cap,
    "callout": r_callout,
    "decision": r_decision,
    "takeaway": r_takeaway,
    "end": lambda s, p: r_end(s),
}


def render(slides, out_path):
    tmp = Path("/tmp/zt_slides")
    if tmp.exists(): shutil.rmtree(tmp)
    tmp.mkdir(parents=True)

    total = sum(s.dur for s in slides)
    elapsed, concat = 0.0, []

    print(f"\n  Rendering {len(slides)} slides ({total:.0f}s)...")

    for i, s in enumerate(slides):
        pct = elapsed / total
        img = RENDERERS.get(s.stype, r_cap)(s, pct)
        p = tmp / f"s{i:03d}.png"
        img.save(p, "PNG")
        concat.append(f"file '{p}'")
        concat.append(f"duration {s.dur}")
        elapsed += s.dur
        print(f"    {i+1:2d}. [{s.stype:8s}] {s.dur:.1f}s")

    concat.append(f"file '{p}'")
    (tmp / "list.txt").write_text("\n".join(concat))

    print(f"  Encoding MP4...")
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(tmp / "list.txt"),
        "-vf", "fps=12",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "ultrafast", "-crf", "28",
        "-movflags", "+faststart", out_path,
    ], capture_output=True, text=True, timeout=60)

    if r.returncode != 0:
        print(f"  ❌ ffmpeg: {r.stderr[-300:]}")
        return None

    mb = os.path.getsize(out_path) / 1048576
    print(f"  ✅ {out_path} ({mb:.1f} MB, {total:.0f}s)")
    shutil.rmtree(tmp)
    return out_path


def main():
    slides = build_slides()
    total = sum(s.dur for s in slides)
    out = str(Path(__file__).parent.parent / "output" / "training_video_se-dc_buyer.mp4")
    print(f"📽️  Social Reel: {len(slides)} slides, {total:.0f}s, 720x1280")
    render(slides, out)

if __name__ == "__main__":
    main()
