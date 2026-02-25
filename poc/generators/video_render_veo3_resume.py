#!/usr/bin/env python3
"""
video_render_veo3_resume.py — Resume a crashed Veo 3 video run
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scans an existing temp folder, skips scenes that already have a
composed scene_XX.mp4, generates the rest, then concatenates everything.

Usage:
  python3 generators/video_render_veo3_resume.py /path/to/ztt_veo3_XXXXX
"""

import os, sys, time, shutil, subprocess
from pathlib import Path
import urllib.request, urllib.error, json

# ── Import scene definitions and helpers from main script ─────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from video_render_veo3 import (
    SCENES, VEO_MODEL, VEO_SECS, ASPECT, TTS_MODEL, TTS_VOICE,
    POLL_SECS, MAX_POLLS, load_keys, gen_veo_clip, gen_tts,
    probe_duration, compose_scene, concat_scenes,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 video_render_veo3_resume.py /path/to/ztt_veo3_XXXXX")
        sys.exit(1)

    tmp = sys.argv[1]
    if not os.path.isdir(tmp):
        print(f"ERROR: temp folder not found: {tmp}")
        sys.exit(1)

    keys = load_keys()
    missing = [k for k, v in keys.items() if not v]
    if missing:
        for k in missing:
            print(f"ERROR: {k} not set in poc/.env")
        sys.exit(1)

    google_key = keys["GOOGLE_API_KEY"]
    openai_key = keys["OPENAI_API_KEY"]

    out_dir    = Path(__file__).parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_mp4 = str(out_dir / "bigfoot_goods_receipt_veo3.mp4")

    total = len(SCENES)
    print(f"Temp folder : {tmp}")
    print(f"Total scenes: {total}")
    print()

    # ── Scan what's already done ──────────────────────────────────────────────
    scene_mp4s = []
    for i in range(total):
        comp_mp4 = os.path.join(tmp, f"scene_{i:02d}.mp4")
        veo_mp4  = os.path.join(tmp, f"veo_{i:02d}.mp4")
        narr_mp3 = os.path.join(tmp, f"narr_{i:02d}.mp3")

        if os.path.exists(comp_mp4) and os.path.getsize(comp_mp4) > 10_000:
            dur = probe_duration(comp_mp4)
            print(f"[{i+1:02d}/{total}] {SCENES[i]['id']}  ✓ already done  ({dur:.1f}s)")
            scene_mp4s.append(comp_mp4)
            continue

        # Need to generate this scene
        print(f"[{i+1:02d}/{total}] {SCENES[i]['id']}")

        # Veo clip
        if not (os.path.exists(veo_mp4) and os.path.getsize(veo_mp4) > 10_000):
            print(f"       Veo 3 generating …", end="", flush=True)
            gen_veo_clip(SCENES[i]["video_prompt"], veo_mp4, google_key)
            print(f" ✓")
        else:
            print(f"       Veo clip already exists, skipping generation")

        # TTS narration
        if not (os.path.exists(narr_mp3) and os.path.getsize(narr_mp3) > 1_000):
            print(f"       TTS narration …", end="", flush=True)
            gen_tts(SCENES[i]["narration"], narr_mp3, openai_key)
            print(f" ✓  ({probe_duration(narr_mp3):.1f}s)")
        else:
            print(f"       TTS already exists ({probe_duration(narr_mp3):.1f}s)")

        # Compose
        compose_scene(veo_mp4, narr_mp3, comp_mp4)
        scene_mp4s.append(comp_mp4)

    # ── Final concat ──────────────────────────────────────────────────────────
    print(f"\nAll {total} scenes ready. Concatenating …")
    concat_scenes(scene_mp4s, output_mp4)

    size_mb   = os.path.getsize(output_mp4) / 1e6
    total_dur = sum(probe_duration(s) for s in scene_mp4s)
    print(f"\n✅  Done: {output_mp4}")
    print(f"   {size_mb:.1f} MB  |  ~{total_dur:.0f}s  |  720×1280  |  24fps")
    print(f"\n   Open with:  open \"{output_mp4}\"")


if __name__ == "__main__":
    main()
