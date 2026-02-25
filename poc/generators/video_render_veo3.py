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
VEO_MODEL  = "veo-3.0-generate-preview"    # swap "veo-3.0-fast-generate-preview" to cut cost ~60%
VEO_SECS   = 8                             # 4, 6, or 8
ASPECT     = "9:16"                        # portrait (matches our 720x1280 target)
TTS_MODEL  = "tts-1-hd"
TTS_VOICE  = "nova"
POLL_SECS  = 20                            # how often to check Veo generation status
MAX_POLLS  = 60                            # 60 × 20s = 20 min max wait per clip

# ── Scene definitions ────────────────────────────────────────────────────────
# video_prompt: describe motion, camera movement, and physical action — Veo needs it
# narration:    the TTS voice-over; clip will loop to match its duration
SCENES = [
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
        "id": "02_what_is_gr",
        "narration": (
            "So what even is a Goods Receipt? Simple. "
            "The vendor just showed up with a truckload of product. "
            "Goods Receipt is how you tell SAP — yeah, it's here, it's real, put it in inventory. "
            "No GR, no stock. And no stock means your replenishment team is calling you. "
            "Trust me, you don't want that."
        ),
        "video_prompt": (
            "Selfie vlog footage of Bigfoot, a large friendly sasquatch in an orange safety vest, "
            "gesturing broadly toward a delivery truck being unloaded behind him, turning to look "
            "at the truck and back at camera with animated expressions, workers moving pallets in "
            "the background, natural warehouse loading dock lighting, handheld vlog camera, photorealistic"
        ),
    },
    {
        "id": "03_find_po",
        "narration": (
            "Step one. Before you touch MIGO, you need your Purchase Order number. "
            "Every Goods Receipt at SE-DC has to be tied to a PO — no exceptions. "
            "If someone hands you product and there's no PO, you stop, you call your buyer, "
            "and you do not post that receipt. I don't care how nice the delivery driver is."
        ),
        "video_prompt": (
            "Selfie vlog shot of Bigfoot, a large sasquatch in a safety vest, "
            "holding up a printed purchase order document close to the camera and tapping it "
            "emphatically with one large furry finger, then shaking his head no firmly, "
            "receiving desk and shelving visible behind, handheld camera, photorealistic"
        ),
    },
    {
        "id": "04_open_migo",
        "narration": (
            "Step two. Jump into SAP Fiori and search for MIGO — that's M-I-G-O. "
            "This is your Goods Movement transaction. "
            "When it opens, make sure the action is set to Goods Receipt "
            "and the reference document is Purchase Order. "
            "Then type in your PO number and hit Enter."
        ),
        "video_prompt": (
            "Selfie vlog of Bigfoot, a large sasquatch, sitting at a warehouse office computer "
            "leaning toward the camera while pointing at the monitor with one enormous furry finger, "
            "eyebrows raised in a helpful expression, turning between the screen and the camera, "
            "warm office lighting, slight handheld vlog movement, photorealistic"
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
        "id": "06_verify_items",
        "narration": (
            "Step four. SAP pulls in your PO line items automatically. "
            "Now you compare what's on screen to what's physically on your dock. "
            "Check the material number, check the quantity, check the unit of measure. "
            "If the vendor shorted you twenty cases of frozen burritos, "
            "you change the quantity here — you do not just accept the PO quantity and move on."
        ),
        "video_prompt": (
            "Selfie vlog footage of Bigfoot, a large sasquatch, walking along warehouse shelving "
            "with a clipboard, looking at it then back at the camera with a focused expression, "
            "counting boxes on shelves with his finger, shaking his head knowingly, "
            "natural warehouse aisle lighting, handheld camera movement, photorealistic"
        ),
    },
    {
        "id": "07_batch_tracking",
        "narration": (
            "Step five — and this one is specific to Southeast DC. "
            "For any perishable or private-label item, "
            "you are required to enter the batch and lot number. "
            "This is not optional at our site. Enterprise says optional. SE-DC says mandatory. "
            "It's how we trace product back if there's ever a recall. "
            "Scan the lot code off the pallet label and enter it here."
        ),
        "video_prompt": (
            "Selfie vlog of Bigfoot, a large sasquatch wearing a safety vest over a hoodie, "
            "kneeling beside a pallet of refrigerated food products in a cold storage area, "
            "scanning a barcode label with a handheld scanner while glancing at the camera, "
            "breath visibly fogging in the cold air, earnest expression, "
            "cinematic cold blue lighting, handheld camera, photorealistic"
        ),
    },
    {
        "id": "08_temp_zone",
        "narration": (
            "Step six. SE-DC has three temperature zones — "
            "Zone Foxtrot for frozen, Zone Romeo for refrigerated, Zone Alpha for ambient. "
            "You must set the storage location in MIGO to match the product's temperature requirement. "
            "Frozen product going into Zone Romeo is a cold chain violation. "
            "And that is a very bad day for everyone, including me."
        ),
        "video_prompt": (
            "Selfie vlog of Bigfoot, a large sasquatch with frost forming on his fur, "
            "standing inside a walk-in freezer, turning to point at a temperature zone sign on "
            "the wall then back to camera with an amused expression, breath heavily fogging, "
            "safety vest visible, cinematic cold blue freezer lighting, photorealistic"
        ),
    },
    {
        "id": "09_quality_flag",
        "narration": (
            "Step seven. For perishable and private-label goods, "
            "you need to check the Quality Inspection flag before you post. "
            "This puts the stock into inspection status automatically "
            "and routes it to the QA team for sign-off. "
            "It does not hold up your receipt — it just means QA has to clear it before it ships out. "
            "Check the box. Every single time."
        ),
        "video_prompt": (
            "Selfie vlog of Bigfoot, a large sasquatch in a warehouse safety vest, "
            "standing at a QA inspection station holding up a big furry thumbs up at the camera, "
            "then turning to gesture at product samples on the table beside him, "
            "nodding emphatically, warm inspection area lighting, handheld vlog camera, photorealistic"
        ),
    },
    {
        "id": "10_post_gr",
        "narration": (
            "Step eight. The big moment. "
            "You've verified your quantities, entered your batch numbers, "
            "confirmed your temperature zone, flagged quality inspection. "
            "Now you click Post. "
            "SAP generates a material document, updates inventory, "
            "and triggers the three-way match with your PO and your invoice. "
            "That product is now officially in the building."
        ),
        "video_prompt": (
            "Selfie vlog of Bigfoot, a large sasquatch, pressing a keyboard key with great ceremony "
            "using one enormous furry finger, filming himself with wide excited eyes, "
            "then pumping his fist and doing a small celebration dance, "
            "warehouse environment behind him, dramatic comic lighting, handheld camera, photorealistic"
        ),
    },
    {
        "id": "11_dont_do_this",
        "narration": (
            "Alright, real talk. Three things I see go wrong out here all the time. "
            "One — posting a Goods Receipt with no PO. Don't do it. "
            "Two — wrong movement type. I said one-oh-one, not one-oh-three. "
            "Three — accepting the full PO quantity when the vendor only delivered part of it. "
            "That breaks your three-way match and your AP team will find you."
        ),
        "video_prompt": (
            "Selfie vlog of Bigfoot, a large sasquatch in a safety vest, "
            "wagging a large furry finger sternly at the camera with a disappointed parent expression, "
            "shaking his head slowly, then holding up three fingers to count the mistakes one by one, "
            "standing at the receiving dock, natural warehouse lighting, handheld camera, photorealistic"
        ),
    },
    {
        "id": "12_recap",
        "narration": (
            "Quick recap before I let you go. "
            "One — get your PO number before you even open MIGO. "
            "Two — movement type 101, every time. "
            "Three — for perishables, enter the batch number, set the right temperature zone, "
            "and check the quality inspection flag. "
            "Do those three things and your Goods Receipt is clean."
        ),
        "video_prompt": (
            "Selfie vlog of Bigfoot, a large sasquatch in a safety vest, "
            "standing at a whiteboard in a warehouse break room pointing at three numbered items, "
            "then looking back at camera with an encouraging smile and giving a thumbs up, "
            "other workers visible at break tables in background, warm lighting, handheld camera, photorealistic"
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
def gen_veo_clip(prompt, out_mp4, google_api_key):
    """Generate a Veo 3 video clip. Polls until done, downloads to out_mp4."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("\n  ERROR: google-genai not installed. Run: pip install google-genai")
        sys.exit(1)

    client = genai.Client(api_key=google_api_key)

    # Start generation
    operation = client.models.generate_videos(
        model=VEO_MODEL,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio=ASPECT,
            duration_seconds=VEO_SECS,
            enhance_prompt=True,
        ),
    )

    # Poll until complete
    for attempt in range(MAX_POLLS):
        if operation.done:
            break
        time.sleep(POLL_SECS)
        operation = client.operations.get(operation)
        elapsed = (attempt + 1) * POLL_SECS
        print(f"    [{elapsed}s] waiting for Veo …", end="\r", flush=True)

    print()  # newline after polling dots

    if not operation.done:
        raise RuntimeError("Veo generation timed out after 20 minutes")

    if operation.error:
        raise RuntimeError(f"Veo generation failed: {operation.error.message}")

    videos = operation.result.generated_videos
    if not videos:
        raise RuntimeError("Veo returned no video output")

    # Download video to file
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


def compose_scene(veo_mp4, narr_mp3, out_mp4):
    """
    Loop the Veo clip to match narration length, strip Veo audio, mix in TTS.
    Result: a single MP4 with real Veo video + TTS narration.
    """
    narr_dur = probe_duration(narr_mp3)

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", veo_mp4,   # loop video
        "-i", narr_mp3,                          # narration
        "-map", "0:v",                           # video from Veo (no Veo audio)
        "-map", "1:a",                           # audio from TTS
        "-t", str(narr_dur),                     # trim to narration length
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
    output_mp4 = str(out_dir / "bigfoot_goods_receipt_veo3.mp4")

    tmp = tempfile.mkdtemp(prefix="ztt_veo3_")
    print(f"Workspace : {tmp}")
    print(f"Scenes    : {len(SCENES)}")
    print(f"Veo model : {VEO_MODEL}  ({VEO_SECS}s clips, {ASPECT})")
    print(f"TTS       : {TTS_MODEL}/{TTS_VOICE}")
    veo_cost = len(SCENES) * VEO_SECS * (0.15 if "fast" in VEO_MODEL else 0.40)
    tts_cost = len(SCENES) * 0.02
    print(f"Est. cost : ~${veo_cost:.2f} Veo  +  ~${tts_cost:.2f} TTS  =  ~${veo_cost + tts_cost:.2f}\n")

    total      = len(SCENES)
    scene_mp4s = []

    for i, scene in enumerate(SCENES):
        print(f"[{i+1:02d}/{total}] {scene['id']}")

        veo_mp4  = os.path.join(tmp, f"veo_{i:02d}.mp4")
        narr_mp3 = os.path.join(tmp, f"narr_{i:02d}.mp3")
        comp_mp4 = os.path.join(tmp, f"scene_{i:02d}.mp4")

        # 1 — Generate Veo clip
        print(f"       Veo 3 generating …", end="", flush=True)
        gen_veo_clip(scene["video_prompt"], veo_mp4, google_key)
        print(f" ✓  ({VEO_SECS}s clip)")

        # 2 — Generate TTS narration
        print(f"       TTS narration …", end="", flush=True)
        gen_tts(scene["narration"], narr_mp3, openai_key)
        narr_dur = probe_duration(narr_mp3)
        print(f" ✓  ({narr_dur:.1f}s)")

        # 3 — Compose: loop clip to narration length + mix audio
        compose_scene(veo_mp4, narr_mp3, comp_mp4)
        scene_mp4s.append(comp_mp4)

    # Final assembly
    concat_scenes(scene_mp4s, output_mp4)

    size_mb   = os.path.getsize(output_mp4) / 1e6
    total_dur = sum(probe_duration(s) for s in scene_mp4s)
    print(f"\n✅  Done: {output_mp4}")
    print(f"   {size_mb:.1f} MB  |  ~{total_dur:.0f}s total  |  720×1280  |  24fps")
    print(f"\nActual API cost: ~${veo_cost:.2f} Veo  +  ~${tts_cost:.2f} TTS  =  ~${veo_cost + tts_cost:.2f}")

    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
