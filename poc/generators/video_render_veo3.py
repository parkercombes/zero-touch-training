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

# ── Character cast ────────────────────────────────────────────────────────────
# Each character is a distinct Sasquatch employee at GlobalMart SE-DC.
# The full description is embedded in every video_prompt to help Veo stay
# consistent within a character across retries and future runs.
#
# DAVE    — Receiving Lead.     Dark reddish-brown fur, orange vest. Host/narrator.
# SANDRA  — Compliance Officer. Silver-grey fur, red vest. Owns the rule scenes.
# MARCUS  — Cold Chain.         Jet-black fur, yellow vest + blue hard hat. Freezer guy.
# KEISHA  — QA Lead.            Auburn fur, white QA vest + tablet. Quality scenes.

DAVE = (
    "Dave, a 7-foot sasquatch with dark reddish-brown fur, broad shoulders, "
    "a wide friendly face with amber eyes, wearing a bright orange GLOBALMART SE-DC "
    "safety vest and a yellow employee ID badge clipped to the left strap"
)
SANDRA = (
    "Sandra, a 7-foot sasquatch with silver-grey fur, sharp focused eyes, "
    "wearing a red COMPLIANCE safety vest with a laminated badge on a lanyard, "
    "clipboard in hand, authoritative posture"
)
MARCUS = (
    "Marcus, a 7-foot sasquatch with jet-black fur and a relaxed confident posture, "
    "wearing a yellow RECEIVING safety vest and a blue hard hat, "
    "breath visibly fogging in the cold air"
)
KEISHA = (
    "Keisha, a 7-foot sasquatch with auburn reddish fur and precise attentive manner, "
    "wearing a white QUALITY ASSURANCE safety vest with a QA logo patch, "
    "holding a tablet computer"
)

# ── Scene definitions ─────────────────────────────────────────────────────────
# video_prompt: visual action + character card + short spoken dialogue (~20 words).
#   Dialogue embedded so Veo generates lip-synced native audio.
# narration:    full educational content for reference / future use.
SCENES = [
    {
        "id": "01_intro",
        "character": "Dave",
        "narration": (
            "Hey, what's up everybody. It's Dave from Receiving, coming at you live "
            "from the dock at GlobalMart Southeast Distribution Center. "
            "Today we're walking through Goods Receipt in SAP MIGO. Let's get into it."
        ),
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
        "id": "02_what_is_gr",
        "character": "Dave",
        "narration": (
            "So what even is a Goods Receipt? Simple. "
            "The vendor just showed up with a truckload of product. "
            "Goods Receipt is how you tell SAP — yeah, it's here, it's real, put it in inventory. "
            "No GR, no stock. And no stock means your replenishment team is calling you."
        ),
        "video_prompt": (
            f"Selfie vlog footage of {DAVE}, gesturing broadly toward a delivery truck "
            "being unloaded behind him, turning to look at the truck then back at camera "
            "with animated expressions, workers moving pallets in background, "
            "natural loading dock lighting, handheld vlog camera, photorealistic. "
            "Dave speaks to camera: 'Goods Receipt tells SAP the product arrived. "
            "No GR, no stock. No stock, and your replenishment team is calling you.'"
        ),
    },
    {
        "id": "03_find_po",
        "character": "Sandra",
        "narration": (
            "Step one. Before you touch MIGO, you need your Purchase Order number. "
            "Every Goods Receipt at SE-DC has to be tied to a PO — no exceptions. "
            "If someone hands you product and there's no PO, you stop, you call your buyer, "
            "and you do not post that receipt."
        ),
        "video_prompt": (
            f"Selfie vlog shot of {SANDRA}, holding up a printed purchase order document "
            "close to the camera and tapping it emphatically with one large furry finger, "
            "then shaking her head firmly no, receiving desk and shelving visible behind, "
            "handheld camera, photorealistic. "
            "Sandra speaks to camera: 'Before you open MIGO you need your PO number. "
            "No purchase order? You do not post that receipt. No exceptions.'"
        ),
    },
    {
        "id": "04_open_migo",
        "character": "Dave",
        "narration": (
            "Step two. Jump into SAP Fiori and search for MIGO. "
            "Set the action to Goods Receipt and the reference document to Purchase Order. "
            "Then type in your PO number and hit Enter."
        ),
        "video_prompt": (
            f"Selfie vlog of {DAVE}, sitting at a warehouse office computer, "
            "leaning toward the camera while pointing at the monitor with one enormous furry finger, "
            "eyebrows raised in a helpful expression, turning between the screen and the camera, "
            "warm office lighting, slight handheld vlog movement, photorealistic. "
            "Dave speaks to camera: 'Open SAP Fiori, find MIGO. "
            "Action: Goods Receipt. Reference: Purchase Order. Enter your PO and hit go.'"
        ),
    },
    {
        "id": "05_movement_type",
        "character": "Sandra",
        "narration": (
            "Step three. Your movement type needs to be 101. "
            "That is Goods Receipt against a Purchase Order. "
            "Do not use 103. Do not use 501. "
            "One-oh-one. Say it with me. One. Oh. One."
        ),
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
        "id": "06_verify_items",
        "character": "Dave",
        "narration": (
            "Step four. SAP pulls in your PO line items automatically. "
            "Compare what's on screen to what's physically on your dock. "
            "Check the material number, check the quantity, check the unit of measure. "
            "If the vendor shorted you, change the quantity now — not after posting."
        ),
        "video_prompt": (
            f"Selfie vlog footage of {DAVE}, walking along warehouse shelving with a clipboard, "
            "looking at it then back at the camera with a focused expression, "
            "counting boxes on shelves with his finger, shaking his head knowingly, "
            "natural warehouse aisle lighting, handheld camera movement, photorealistic. "
            "Dave speaks to camera: 'SAP loads your line items automatically. "
            "Compare to what's on the dock. If quantities are short, fix it now.'"
        ),
    },
    {
        "id": "07_batch_tracking",
        "character": "Keisha",
        "narration": (
            "Step five. For any perishable or private-label item, "
            "you are required to enter the batch and lot number. "
            "Enterprise says optional. SE-DC says mandatory. "
            "It's how we trace product in a recall. "
            "Scan the lot code off the pallet label and enter it here."
        ),
        "video_prompt": (
            f"Selfie vlog of {KEISHA}, kneeling beside a pallet of refrigerated food products, "
            "scanning a barcode label with a handheld scanner while glancing at the camera, "
            "cold storage area, breath visibly fogging, earnest expression, "
            "cinematic cold blue lighting, handheld camera, photorealistic. "
            "Keisha speaks to camera: 'Perishables require a batch and lot number — "
            "mandatory at SE-DC. Scan the pallet label and enter it in MIGO.'"
        ),
    },
    {
        "id": "08_temp_zone",
        "character": "Marcus",
        "narration": (
            "Step six. SE-DC has three temperature zones — "
            "Zone Foxtrot for frozen, Zone Romeo for refrigerated, Zone Alpha for ambient. "
            "Set the storage location in MIGO to match the product's temperature requirement. "
            "Frozen product in Zone Romeo is a cold chain violation."
        ),
        "video_prompt": (
            f"Selfie vlog of {MARCUS}, standing inside a walk-in freezer, "
            "frost forming on his black fur, turning to point at a temperature zone sign on the wall "
            "then back to camera with an amused expression, breath heavily fogging, "
            "cinematic cold blue freezer lighting, photorealistic. "
            "Marcus speaks to camera: 'Three zones: Foxtrot for frozen, Romeo for refrigerated, "
            "Alpha for ambient. Match the product or it's a cold chain violation.'"
        ),
    },
    {
        "id": "09_quality_flag",
        "character": "Keisha",
        "narration": (
            "Step seven. For perishable and private-label goods, "
            "check the Quality Inspection flag before you post. "
            "This routes the stock to QA for sign-off. "
            "It does not hold up your receipt — QA clears it before it ships. "
            "Check the box. Every single time."
        ),
        "video_prompt": (
            f"Selfie vlog of {KEISHA}, standing at a QA inspection station, "
            "holding up a big furry thumbs up at the camera, then turning to gesture "
            "at product samples on the table beside her, nodding emphatically, "
            "warm inspection area lighting, handheld vlog camera, photorealistic. "
            "Keisha speaks to camera: 'Check the Quality Inspection flag for every perishable "
            "and private-label item. QA clears it before it ships. Every single time.'"
        ),
    },
    {
        "id": "10_post_gr",
        "character": "Dave",
        "narration": (
            "Step eight. The big moment. "
            "You've verified quantities, entered batch numbers, "
            "confirmed your temperature zone, flagged quality inspection. "
            "Click Post. SAP generates a material document, updates inventory, "
            "and triggers the three-way match. That product is officially in the building."
        ),
        "video_prompt": (
            f"Selfie vlog of {DAVE}, pressing a keyboard key with great ceremony "
            "using one enormous furry finger, filming himself with wide excited eyes, "
            "then pumping his fist and doing a small celebration dance, "
            "warehouse environment behind him, dramatic comic lighting, handheld camera, photorealistic. "
            "Dave speaks to camera: 'Everything is verified. Click Post. "
            "SAP creates the material document and updates inventory. It's officially in the building!'"
        ),
    },
    {
        "id": "11_dont_do_this",
        "character": "Sandra",
        "narration": (
            "Three things I see go wrong all the time. "
            "One — posting with no PO. Two — wrong movement type, not 101. "
            "Three — accepting the full PO quantity when the vendor short-shipped. "
            "That breaks your three-way match and your AP team will find you."
        ),
        "video_prompt": (
            f"Selfie vlog of {SANDRA}, wagging a large furry finger sternly at the camera "
            "with a disappointed expression, shaking her head slowly, "
            "then holding up three fingers to count the mistakes one by one, "
            "standing at the receiving dock, natural warehouse lighting, handheld camera, photorealistic. "
            "Sandra speaks to camera: 'Three things I see go wrong: no PO, wrong movement type, "
            "and accepting short quantities. Your AP team will find you.'"
        ),
    },
    {
        "id": "12_recap",
        "character": "Dave",
        "narration": (
            "Quick recap. "
            "One — get your PO number before you open MIGO. "
            "Two — movement type 101, every time. "
            "Three — for perishables: batch number, correct temperature zone, QI flag. "
            "Do those three things and your Goods Receipt is clean."
        ),
        "video_prompt": (
            f"Selfie vlog of {DAVE}, standing at a whiteboard in a warehouse break room "
            "pointing at three numbered items, then looking back at camera with an encouraging smile "
            "and giving a thumbs up, other Sasquatch workers visible at break tables in background, "
            "warm lighting, handheld camera, photorealistic. "
            "Dave speaks to camera: 'Quick recap: get your PO, movement type 101, "
            "and for perishables — batch number, right zone, QI flag. You've got this.'"
        ),
    },
    {
        "id": "13_outro",
        "character": "Dave",
        "narration": (
            "And that's a wrap on Goods Receipt in MIGO. "
            "Questions? Hit up your team lead or check the job aid on the portal. "
            "I'm Dave, I work here, and I will see you in the next one. "
            "Stay safe out there on those docks."
        ),
        "video_prompt": (
            f"Selfie vlog of {DAVE}, giving a big enthusiastic wave goodbye to the camera "
            "at a distribution center receiving dock at golden hour, sunlight streaming in, "
            "other Sasquatch workers — one with silver-grey fur, one with jet-black fur, "
            "one with auburn fur — waving in the background, huge warm grin, "
            "slowly stepping back from camera, cinematic golden light, photorealistic. "
            "Dave speaks to camera: 'That's a wrap! Questions? Check the job aid on the portal. "
            "I'm Dave, I work here, and stay safe out there on those docks!'"
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
    print(f"Audio     : Veo 3 native (lip-synced, no TTS)")
    veo_cost = len(SCENES) * VEO_SECS * (0.15 if "fast" in VEO_MODEL else 0.40)
    print(f"Est. cost : ~${veo_cost:.2f}\n")

    total      = len(SCENES)
    scene_mp4s = []

    for i, scene in enumerate(SCENES):
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
