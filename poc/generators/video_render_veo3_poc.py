"""
video_render_veo3_poc.py — 3-scene POC cut of the Bigfoot Goods Receipt video.

Uses the same pipeline as video_render_veo3.py but runs only 3 scenes so the
daily Veo quota isn't exhausted during proof-of-concept validation.

Scenes included:
  01_intro          — Bigfoot introduces himself on the dock
  05_movement_type  — "One. Oh. One." (most memorable teaching moment)
  13_outro          — Bigfoot waves goodbye, golden hour

Cost estimate (Veo 3 Fast):  3 clips × 8s × $0.15 = $3.60 + ~$0.06 TTS = ~$3.66
Output: poc/output/bigfoot_goods_receipt_poc.mp4

Run:
  python3 poc/generators/video_render_veo3_poc.py
"""

import sys, os
from pathlib import Path
import tempfile, shutil

# Pull core functions + config from the main pipeline
sys.path.insert(0, str(Path(__file__).parent))
from video_render_veo3 import (
    VEO_MODEL, VEO_SECS, ASPECT, TTS_MODEL, TTS_VOICE,
    load_keys, gen_veo_clip, gen_tts,
    compose_scene, concat_scenes, probe_duration,
)

# ── 3-scene POC subset ────────────────────────────────────────────────────────
POC_SCENES = [
    {
        "id": "01_intro",
        "narration": (
            "Hey, what's up everybody. It's your boy Bigfoot, coming at you live "
            "from the receiving dock at GlobalMart Southeast Distribution Center. "
            "Today we're walking through Goods Receipt in SAP MIGO. Let's get into it."
        ),
        "video_prompt": (
            "Handheld selfie-vlog footage of Bigfoot, a large friendly sasquatch wearing an orange "
            "warehouse safety vest and employee badge, walking toward the camera while talking "
            "enthusiastically and waving, a busy distribution center loading dock with delivery "
            "trucks behind him, natural daylight, slight handheld camera shake, photorealistic"
        ),
    },
    {
        "id": "05_movement_type",
        "narration": (
            "Step three — and listen up because people mess this up all the time. "
            "Your movement type needs to be 101. "
            "That is Goods Receipt against a Purchase Order. "
            "Do not use 103. Do not use 501. "
            "One-oh-one. Say it with me. One. Oh. One."
        ),
        "video_prompt": (
            "Selfie vlog of Bigfoot, a large sasquatch in a warehouse safety vest, "
            "holding up fingers to count one-zero-one while mouthing the numbers exaggeratedly, "
            "wagging his finger at the camera with a stern but funny expression, "
            "warehouse computer station behind him, handheld camera, photorealistic"
        ),
    },
    {
        "id": "13_outro",
        "narration": (
            "And that's a wrap on Goods Receipt in MIGO. "
            "If you have questions, hit up your team lead or check the job aid on the portal. "
            "I'm Bigfoot, I work here, and I will see you in the next one. "
            "Stay safe out there on those docks."
        ),
        "video_prompt": (
            "Selfie vlog of Bigfoot, a large sasquatch in a safety vest, "
            "giving a big enthusiastic wave goodbye to the camera at a distribution center receiving dock, "
            "golden hour sunlight streaming in, other warehouse workers waving in the background, "
            "huge warm grin, slowly stepping back from camera, cinematic golden light, photorealistic"
        ),
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    keys = load_keys()
    missing = [k for k, v in keys.items() if not v]
    if missing:
        for k in missing:
            print(f"ERROR: {k} not set.  Add it to poc/.env as {k}=...")
        sys.exit(1)

    google_key = keys["GOOGLE_API_KEY"]
    openai_key = keys["OPENAI_API_KEY"]

    out_dir = Path(__file__).parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_mp4 = str(out_dir / "bigfoot_goods_receipt_poc.mp4")

    tmp = tempfile.mkdtemp(prefix="ztt_poc_")
    total = len(POC_SCENES)
    veo_cost = total * VEO_SECS * (0.15 if "fast" in VEO_MODEL else 0.40)
    tts_cost = total * 0.02

    print(f"Workspace : {tmp}")
    print(f"Scenes    : {total}  (POC cut — intro + 101 lesson + outro)")
    print(f"Veo model : {VEO_MODEL}  ({VEO_SECS}s clips, {ASPECT})")
    print(f"TTS       : {TTS_MODEL}/{TTS_VOICE}")
    print(f"Est. cost : ~${veo_cost:.2f} Veo  +  ~${tts_cost:.2f} TTS  =  ~${veo_cost + tts_cost:.2f}\n")

    scene_mp4s = []

    for i, scene in enumerate(POC_SCENES):
        print(f"[{i+1:02d}/{total}] {scene['id']}")

        veo_mp4  = os.path.join(tmp, f"veo_{i:02d}.mp4")
        narr_mp3 = os.path.join(tmp, f"narr_{i:02d}.mp3")
        comp_mp4 = os.path.join(tmp, f"scene_{i:02d}.mp4")

        print(f"       Veo 3 generating …", end="", flush=True)
        gen_veo_clip(scene["video_prompt"], veo_mp4, google_key)
        print(f" ✓  ({VEO_SECS}s clip)")

        print(f"       TTS narration …", end="", flush=True)
        gen_tts(scene["narration"], narr_mp3, openai_key)
        narr_dur = probe_duration(narr_mp3)
        print(f" ✓  ({narr_dur:.1f}s)")

        compose_scene(veo_mp4, narr_mp3, comp_mp4)
        scene_mp4s.append(comp_mp4)

    concat_scenes(scene_mp4s, output_mp4)

    size_mb   = os.path.getsize(output_mp4) / 1e6
    total_dur = sum(probe_duration(s) for s in scene_mp4s)
    print(f"\n✅  Done: {output_mp4}")
    print(f"   {size_mb:.1f} MB  |  ~{total_dur:.0f}s total  |  9:16 portrait")
    print(f"   Actual cost: ~${veo_cost:.2f} Veo  +  ~${tts_cost:.2f} TTS  =  ~${veo_cost + tts_cost:.2f}")

    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
