#!/usr/bin/env python3
"""
video_render_veo3.py — Bigfoot's Goods Receipt Vlog, powered by Google Veo 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Each scene is a REAL Veo 3 video clip — Bigfoot physically moving, gesturing,
and walking through the Goods Receipt process at GlobalMart SE-DC.

Architecture:
  • Google Veo 3  → one 8s cinematic video clip per scene
  • OpenAI TTS    → narration audio per scene
  • ffmpeg        → loop clip to match narration length, mix audio, concat all scenes

One-time Mac setup:
  brew install ffmpeg
  pip install google-genai openai

Usage:
  python3 video_render_veo3.py
  # Keys auto-loaded from poc/.env: GOOGLE_API_KEY + OPENAI_API_KEY

Output:    poc/output/bigfoot_goods_receipt_veo3.mp4
Cost est:  13 clips × 8s × $0.40/s = ~$41.60  (Veo 3 Standard)
           13 clips × 8s × $0.15/s = ~$15.60  (Veo 3 Fast — change VEO_MODEL)
"""

import os, sys, time, wave, math, shutil, subprocess, tempfile
from pathlib import Path
import urllib.request, urllib.error, json

# ── Config ───────────────────────────────────────────────────────────────────
VEO_MODEL  = "veo-3.0-fast-generate-001"   # Fast tier: ~60% cheaper ($0.15/s vs $0.40/s)
VEO_SECS   = 8                             # 4, 6, or 8
ASPECT     = "9:16"                        # portrait (matches our 720x1280 target)
TTS_MODEL  = "tts-1-hd"
TTS_VOICE  = "nova"
POLL_SECS  = 20                            # how often to check Veo generation status
MAX_POLLS  = 60                            # 60 × 20s = 20 min max wait per clip

# ── Character cast & scenes ──────────────────────────────────────────────────
# Casts and scene template are defined in video_casts.py. The cast selection
# happens in main() via --cast, defaulting to "bigfoot" for backward compatibility.
# DAVE/SANDRA/MARCUS/KEISHA/SCENES below are the BIGFOOT cast bindings, kept at
# module level so video_render_veo3_poc.py and video_render_veo3_resume.py keep
# importing them by name without changes.
from video_casts import (
    CAST_BIGFOOT, CAST_HUMAN, CASTS,
    get_cast, build_scenes, build_poc_scenes,
    POC_SCENE_IDS,
)

DAVE   = CAST_BIGFOOT.dave
SANDRA = CAST_BIGFOOT.sandra
MARCUS = CAST_BIGFOOT.marcus
KEISHA = CAST_BIGFOOT.keisha
SCENES = build_scenes(CAST_BIGFOOT)



# ── API key loader ────────────────────────────────────────────────────────────
def load_keys():
    keys = {"GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY", ""),
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "")}
    env_paths = [Path(__file__).parent.parent / ".env", Path(".env")]
    for ep in env_paths:
        if ep.exists():
            for line in ep.read_text().splitlines():
                for k in keys:
                    if line.startswith(f"{k}=") and not keys[k]:
                        keys[k] = line.split("=", 1)[1].strip()
    return keys


# ── Veo 3 generation ──────────────────────────────────────────────────────────
def gen_veo_clip(prompt, out_mp4, google_api_key, retries=4):
    """Generate a Veo 3 video clip. Polls until done, downloads to out_mp4.
    Automatically retries on 429 rate-limit with exponential back-off."""
    try:
        from google import genai
        from google.genai import types
        from google.genai import errors as genai_errors
    except ImportError:
        print("\n  ERROR: google-genai not installed. Run: pip install google-genai")
        sys.exit(1)

    client = genai.Client(api_key=google_api_key)

    for attempt in range(retries):
        try:
            # Start generation
            operation = client.models.generate_videos(
                model=VEO_MODEL,
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio=ASPECT,
                    duration_seconds=VEO_SECS,
                ),
            )

            # Poll until complete
            for poll in range(MAX_POLLS):
                if operation.done:
                    break
                time.sleep(POLL_SECS)
                operation = client.operations.get(operation)
                elapsed = (poll + 1) * POLL_SECS
                print(f"    [{elapsed}s] waiting for Veo …", end="\r", flush=True)

            print()  # newline after polling dots

            if not operation.done:
                raise RuntimeError("Veo generation timed out after 20 minutes")

            if operation.error:
                raise RuntimeError(f"Veo generation failed: {operation.error.message}")

            # Check for silent empty-result failure (fast model occasionally returns no video)
            videos = operation.result.generated_videos if operation.result else []
            if not videos:
                if attempt < retries - 1:
                    print(f"\n  Veo returned empty result (silent failure). Retrying "
                          f"({attempt+1}/{retries-1}) in 30s …")
                    time.sleep(30)
                    continue
                raise RuntimeError("Veo returned no video output after all retries")

            break  # success — exit retry loop

        except Exception as e:
            # ClientError attribute name varies by library version — check string
            is_429 = "429" in str(e)
            if is_429 and attempt < retries - 1:
                wait = 300 * (2 ** attempt)  # 5min, 10min, 20min, 40min
                mins = wait // 60
                print(f"\n  Quota exhausted (429). Waiting {mins} min before retry "
                      f"({attempt+1}/{retries-1}) …")
                # Countdown so it's clear the script is still alive
                for remaining in range(wait, 0, -30):
                    print(f"    {remaining}s remaining …", end="\r", flush=True)
                    time.sleep(min(30, remaining))
                print()
                continue
            raise  # re-raise if not 429 or out of retries

    # Download video to file  (videos already validated inside retry loop)
    video_file = videos[0].video
    video_bytes = client.files.download(file=video_file)
    with open(out_mp4, "wb") as f:
        f.write(bytes(video_bytes))


# ── OpenAI TTS ────────────────────────────────────────────────────────────────
def gen_tts(text, out_mp3, openai_api_key):
    """Generate narration via OpenAI TTS API."""
    url = "https://api.openai.com/v1/audio/speech"
    payload = json.dumps({"model": TTS_MODEL, "voice": TTS_VOICE, "input": text}).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Authorization": f"Bearer {openai_api_key}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(out_mp3, "wb") as f:
                    f.write(resp.read())
            return
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:200]
            if e.code == 429 and attempt < 2:
                time.sleep(20 * (attempt + 1))
                continue
            raise RuntimeError(f"TTS {e.code}: {body}")
        except Exception:
            if attempt < 2:
                time.sleep(5)
                continue
            raise
    raise RuntimeError("TTS failed after retries")


# ── Audio/video helpers ───────────────────────────────────────────────────────
def probe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", path],
        capture_output=True, text=True,
    )
    for line in r.stdout.splitlines():
        if line.startswith("duration="):
            return float(line.split("=")[1])
    return float(VEO_SECS)


def compose_scene(veo_mp4, out_mp4):
    """
    Transcode Veo clip preserving its native audio (lip-synced to video).
    Veo 3 generates speech + ambient audio together with the video — keep it.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", veo_mp4,
        "-map", "0:v",    # video stream
        "-map", "0:a?",   # native Veo audio (? = skip gracefully if absent)
        "-vf", "scale=720:1280:force_original_aspect_ratio=disable,setsar=1",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-r", "24",
        out_mp4,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ffmpeg STDERR:", r.stderr[-1000:])
        raise RuntimeError(f"compose_scene failed for {out_mp4}")


def concat_scenes(scene_mp4s, output_mp4):
    """Concatenate all composed scene files into the final video."""
    n = len(scene_mp4s)
    inputs = []
    for s in scene_mp4s:
        inputs += ["-i", s]

    fc_in = "".join(f"[{i}:v][{i}:a]" for i in range(n))
    fc = f"{fc_in}concat=n={n}:v=1:a=1[v][a]"

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + [
            "-filter_complex", fc,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            output_mp4,
        ]
    )
    print("  Concatenating scenes …")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ffmpeg STDERR:", r.stderr[-2000:])
        raise RuntimeError("concat_scenes failed")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    import argparse
    ap = argparse.ArgumentParser(
        description="Veo 3 Goods Receipt video. Default cast: bigfoot."
    )
    ap.add_argument(
        "--cast",
        default="bigfoot",
        choices=sorted(CASTS.keys()),
        help="Character cast to render with (default: bigfoot)",
    )
    args = ap.parse_args()

    cast = get_cast(args.cast)
    scenes = build_scenes(cast)

    keys = load_keys()
    missing = [k for k, v in keys.items() if not v]
    if missing:
        for k in missing:
            print(f"ERROR: {k} not set.")
            print(f"  Add it to poc/.env as {k}=...")
        sys.exit(1)

    google_key  = keys["GOOGLE_API_KEY"]
    openai_key  = keys["OPENAI_API_KEY"]

    out_dir = Path(__file__).parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_mp4 = str(out_dir / f"goods_receipt_veo3_{cast.name}.mp4")

    tmp = tempfile.mkdtemp(prefix=f"ztt_veo3_{cast.name}_")
    print(f"Cast      : {cast.label}")
    print(f"Workspace : {tmp}")
    print(f"Scenes    : {len(scenes)}")
    print(f"Veo model : {VEO_MODEL}  ({VEO_SECS}s clips, {ASPECT})")
    print(f"Audio     : Veo 3 native (lip-synced, no TTS)")
    veo_cost = len(scenes) * VEO_SECS * (0.15 if "fast" in VEO_MODEL else 0.40)
    print(f"Est. cost : ~${veo_cost:.2f}\n")

    total      = len(scenes)
    scene_mp4s = []

    for i, scene in enumerate(scenes):
        print(f"[{i+1:02d}/{total}] {scene['id']}")

        veo_mp4  = os.path.join(tmp, f"veo_{i:02d}.mp4")
        comp_mp4 = os.path.join(tmp, f"scene_{i:02d}.mp4")

        # 1 — Generate Veo clip
        print(f"       Veo 3 generating (video + audio) …", end="", flush=True)
        gen_veo_clip(scene["video_prompt"], veo_mp4, google_key)
        print(f" ✓  ({VEO_SECS}s clip)")

        # 2 — Compose: transcode + preserve native Veo audio (lip-synced)
        compose_scene(veo_mp4, comp_mp4)
        scene_mp4s.append(comp_mp4)

    # Final assembly
    concat_scenes(scene_mp4s, output_mp4)

    size_mb   = os.path.getsize(output_mp4) / 1e6
    total_dur = sum(probe_duration(s) for s in scene_mp4s)
    print(f"\n✅  Done: {output_mp4}")
    print(f"   {size_mb:.1f} MB  |  ~{total_dur:.0f}s total  |  720×1280  |  24fps")
    print(f"\nActual API cost: ~${veo_cost:.2f} Veo  (native audio — no TTS charge)")

    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
