"""
video_render_veo3_poc.py — 3-scene POC cut of the Bigfoot Goods Receipt video.

Uses Veo 3's native audio generation — no TTS overlay.
Dialogue is embedded in each video_prompt so Veo generates speech and
lip movement together, producing natural sync.

Scenes:
  01_intro          — Bigfoot introduces himself on the dock
  05_movement_type  — "One. Oh. One." (most memorable teaching moment)
  13_outro          — Bigfoot waves goodbye, golden hour

Cost estimate (Veo 3 Fast):  3 clips × 8s × $0.15 = ~$3.60  (no TTS cost)
Output: poc/output/bigfoot_goods_receipt_poc.mp4

Run:
  python3 poc/generators/video_render_veo3_poc.py
"""

import sys, os
from pathlib import Path
import tempfile, shutil

sys.path.insert(0, str(Path(__file__).parent))
from video_render_veo3 import (
    VEO_MODEL, VEO_SECS, ASPECT, DAVE, SANDRA, MARCUS,
    load_keys, gen_veo_clip,
    compose_scene, concat_scenes, probe_duration,
)

# ── 3-scene POC subset ────────────────────────────────────────────────────────
# Three distinct characters so the cast concept is visible even in a 3-clip test.
# Dialogue embedded in video_prompt — Veo generates lip-synced native audio.

POC_SCENES = [
    {
        "id": "01_intro",
        "character": "Dave (Receiving Lead — dark reddish-brown fur, orange vest)",
        "video_prompt": (
            f"Handheld selfie-vlog footage of {DAVE}, walking toward the camera "
            "while talking enthusiastically and waving, a busy distribution center "
            "loading dock with delivery trucks behind him, natural daylight, "
            "slight handheld camera shake, photorealistic. "
            "Dave speaks to camera: 'Hey what's up! I'm Dave from Receiving. "
            "Today we're covering Goods Receipt in SAP MIGO. Let's get into it!'"
        ),
    },
    {
        "id": "05_movement_type",
        "character": "Sandra (Compliance — silver-grey fur, red vest)",
        "video_prompt": (
            f"Selfie vlog of {SANDRA}, holding up three fingers counting one-zero-one, "
            "mouthing the numbers exaggeratedly, wagging her finger at the camera "
            "with a stern but funny expression, warehouse computer station behind her, "
            "handheld camera, photorealistic. "
            "Sandra speaks to camera: 'Movement type must be 101. "
            "Not 103. Not 501. One. Oh. One. Every single time.'"
        ),
    },
    {
        "id": "13_outro",
        "character": "Marcus (Cold Chain — jet-black fur, yellow vest)",
        "video_prompt": (
            f"Selfie vlog of {MARCUS}, giving a big enthusiastic wave goodbye to the camera "
            "at a distribution center receiving dock at golden hour, sunlight streaming in, "
            "other warehouse workers waving in the background, huge warm grin, "
            "slowly stepping back from camera, cinematic golden light, photorealistic. "
            "Marcus speaks to camera: 'That's a wrap on Goods Receipt! "
            "Questions? Hit your team lead or check the portal. Stay safe out there!'"
        ),
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    keys = load_keys()
    # Only Google key needed — no TTS
    if not keys.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set. Add it to poc/.env")
        sys.exit(1)

    google_key = keys["GOOGLE_API_KEY"]

    out_dir = Path(__file__).parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_mp4 = str(out_dir / "bigfoot_goods_receipt_poc.mp4")

    tmp   = tempfile.mkdtemp(prefix="ztt_poc_")
    total = len(POC_SCENES)
    veo_cost = total * VEO_SECS * (0.15 if "fast" in VEO_MODEL else 0.40)

    print(f"Workspace : {tmp}")
    print(f"Scenes    : {total}  (POC — intro + 101 lesson + outro)")
    print(f"Veo model : {VEO_MODEL}  ({VEO_SECS}s clips, {ASPECT})")
    print(f"Audio     : Veo 3 native (lip-synced, no TTS)")
    print(f"Est. cost : ~${veo_cost:.2f}\n")

    scene_mp4s = []

    for i, scene in enumerate(POC_SCENES):
        print(f"[{i+1:02d}/{total}] {scene['id']}  [{scene['character']}]")

        veo_mp4  = os.path.join(tmp, f"veo_{i:02d}.mp4")
        comp_mp4 = os.path.join(tmp, f"scene_{i:02d}.mp4")

        print(f"       Veo 3 generating (video + audio) …", end="", flush=True)
        gen_veo_clip(scene["video_prompt"], veo_mp4, google_key)
        print(f" ✓  ({VEO_SECS}s clip)")

        compose_scene(veo_mp4, comp_mp4)
        scene_mp4s.append(comp_mp4)

    concat_scenes(scene_mp4s, output_mp4)

    size_mb   = os.path.getsize(output_mp4) / 1e6
    total_dur = sum(probe_duration(s) for s in scene_mp4s)
    print(f"\n✅  Done: {output_mp4}")
    print(f"   {size_mb:.1f} MB  |  ~{total_dur:.0f}s total  |  9:16 portrait")
    print(f"   Cost: ~${veo_cost:.2f}  (Veo native audio — no TTS charge)")

    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
