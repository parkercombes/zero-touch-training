#!/usr/bin/env python3
"""
veo3_test_clip.py — Single-clip Veo 3 API test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generates one 8-second Veo 3 clip to validate the API key and model access
before running the full 13-scene video (~$41.60).

Cost: ~$3.20 (one 8s clip at Veo 3 Standard $0.40/s)

Usage:
  python3 veo3_test_clip.py
  # Key loaded from poc/.env: GOOGLE_API_KEY
"""

import os, sys, time
from pathlib import Path

VEO_MODEL  = "veo-3.0-generate-001"        # also available: veo-3.0-fast-generate-001 (~60% cheaper)
VEO_SECS   = 8
ASPECT     = "9:16"
POLL_SECS  = 20
MAX_POLLS  = 60

TEST_PROMPT = (
    "Handheld selfie-vlog footage of Bigfoot, a large friendly sasquatch wearing an orange "
    "warehouse safety vest and employee badge, walking toward the camera while talking "
    "enthusiastically and waving, a busy distribution center loading dock with delivery "
    "trucks behind him, natural daylight, slight handheld camera shake, photorealistic"
)


def load_google_key():
    key = os.environ.get("GOOGLE_API_KEY", "")
    if key:
        return key
    for ep in [Path(__file__).parent.parent / ".env", Path(".env")]:
        if ep.exists():
            for line in ep.read_text().splitlines():
                if line.startswith("GOOGLE_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    if val:
                        return val
    return None


def main():
    key = load_google_key()
    if not key:
        print("ERROR: GOOGLE_API_KEY not set in environment or poc/.env")
        sys.exit(1)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("ERROR: google-genai not installed. Run: pip install google-genai")
        sys.exit(1)

    out_dir = Path(__file__).parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = str(out_dir / "veo3_test_clip.mp4")

    client = genai.Client(api_key=key)

    print(f"Model  : {VEO_MODEL}")
    print(f"Clip   : {VEO_SECS}s  {ASPECT}")
    print(f"Cost   : ~${VEO_SECS * 0.40:.2f}")
    print(f"Output : {out_mp4}")
    print(f"\nPrompt : {TEST_PROMPT[:80]}…\n")
    print("Submitting to Veo 3 …")

    operation = client.models.generate_videos(
        model=VEO_MODEL,
        prompt=TEST_PROMPT,
        config=types.GenerateVideosConfig(
            aspect_ratio=ASPECT,
            duration_seconds=VEO_SECS,
        ),
    )

    print("Waiting for generation ", end="", flush=True)
    for attempt in range(MAX_POLLS):
        if operation.done:
            break
        time.sleep(POLL_SECS)
        operation = client.operations.get(operation)
        print(".", end="", flush=True)

    print()

    if not operation.done:
        print("ERROR: Timed out after 20 minutes.")
        sys.exit(1)

    if operation.error:
        print(f"ERROR: Veo generation failed — {operation.error.message}")
        sys.exit(1)

    videos = operation.result.generated_videos
    if not videos:
        print("ERROR: No video returned.")
        sys.exit(1)

    print("Downloading clip …")
    video_bytes = client.files.download(file=videos[0].video)
    with open(out_mp4, "wb") as f:
        f.write(bytes(video_bytes))

    size_mb = os.path.getsize(out_mp4) / 1e6
    print(f"\n✅  Done: {out_mp4}  ({size_mb:.1f} MB)")
    print(f"   Open with:  open \"{out_mp4}\"")


if __name__ == "__main__":
    main()
