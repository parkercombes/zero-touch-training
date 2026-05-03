"""
scenarios/drone_anatomy.py — DJI Mavic 3 Pro Anatomy & Pre-Flight Visual Inspection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Training domain: HARDWARE (real photos, no software UI)

Why this scenario exists
  drone_preflight.py is the FUSION PoC — it alternates HW/SW steps with
  Pillow-drawn placeholders. This scenario takes the same engine in the
  opposite direction: pure hardware, real photos, single domain. Five steps
  of "click the part you should inspect before takeoff."

  The training value is real — these are the actual things a Part 107 operator
  should visually verify before every flight, and they're the failure modes
  most commonly skipped under hurry.

Source assets
  Real DJI marketing photographs from docs/DJI_Mavic_3/. They aren't
  procedural step-by-step shots (that material doesn't exist for this
  airframe in our archive), but they're high-resolution clean isolated
  drone photos suitable for component identification.

  See docs/DJI_Mavic_3/inventory.md for the full source catalog and gap
  analysis — about 15% of what a complete pre-flight scenario would need
  is present here. This scenario uses what's actually usable.

Letterboxing
  Source photos have varying aspect ratios. To avoid distorting the drone,
  this module letterbox-pads each source to fit the 1280×720 canvas instead
  of stretching (which is what base_hardware.load_base_image does).
  Hotspot coordinates are in post-letterbox canvas space.

To extend
  Add steps for: storage cover removal, arm unfolding sequence, battery
  insertion, prop CW/CCW orientation. All require photos we don't have.
  Either shoot them yourself or fall back to PIL-drawn placeholders
  following the drone_preflight.py pattern.
"""

from pathlib import Path
from PIL import Image, ImageDraw

from scenarios.base_hardware import (
    W, H, fnt,
    HARDWARE_BRANDING,
    HW_STEEL, HW_ORANGE, HW_GREEN, HW_BLUE, HW_RED,
    HW_WHITE, HW_BG, HW_LABEL, HW_BORDER,
    annotate_region, draw_callout,
    hardware_status_banner,
)


# ── Source photo directory ──────────────────────────────────────────────────
# poc/generators/scenarios/drone_anatomy.py → up 4 → repo root → docs/DJI_Mavic_3
_PHOTO_DIR = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "DJI_Mavic_3"


# ── Aircraft-specific branding override ─────────────────────────────────────
DRONE_BRANDING = {
    **HARDWARE_BRANDING,
    "level_descriptions": [
        "Walk around the aircraft. No timer. Click each part to learn what it does and what to look for.",
        "Inspect each component in order. Visual guidance highlights the target.",
        "No highlights. Skip a check and the consequence shows you what could go wrong.",
        "Timed pre-flight visual inspection. No help. Prove you can clear an aircraft for takeoff.",
    ],
}


# ── Letterbox helper ────────────────────────────────────────────────────────
# load_base_image() in base_hardware.py uses .resize((W,H)) which STRETCHES
# the image, distorting drone proportions. We need aspect-preserving fit so
# components stay where they look like they are in the source. This helper
# replaces it for this scenario.
def _resolve_photo(filename):
    """Find a source photo by exact name or by glob fallback.

    macOS Screenshot writes filenames using U+202F (narrow no-break space)
    before AM/PM, not a regular ASCII space. Source filenames in this module
    are typed with regular spaces for readability, so we glob-match if the
    exact lookup misses.
    """
    exact = _PHOTO_DIR / filename
    if exact.exists():
        return exact
    # Build a glob pattern: replace " AM"/" PM" with "*AM"/"*PM" so either
    # space variant matches. Also tolerate any whitespace difference around
    # other tokens by allowing single-character wildcards.
    pattern = filename.replace(" AM.", "*AM.").replace(" PM.", "*PM.")
    matches = sorted(_PHOTO_DIR.glob(pattern))
    if matches:
        return matches[0]
    return exact  # return the non-existent path so caller can detect miss


def _load_letterboxed(filename, title):
    """Load a photo from _PHOTO_DIR, letterbox-fit to (W, H), add shell bar.

    Returns (img, draw, content_box) where content_box = (l, t, r, b) gives
    the bounding rect of the actual image content within the canvas (the
    rest is HW_BG padding). Useful for callers that want to verify hotspot
    placement, but most callers just use img+draw.
    """
    src_path = _resolve_photo(filename)
    if src_path.exists():
        src = Image.open(src_path).convert("RGB")
        sw, sh = src.size
        target_ratio = W / H
        src_ratio = sw / sh

        if src_ratio > target_ratio:
            # Source wider than canvas → fit to width, letterbox top/bottom
            new_w = W
            new_h = round(W * sh / sw)
            resized = src.resize((new_w, new_h), Image.LANCZOS)
            ox, oy = 0, (H - new_h) // 2
        else:
            # Source taller than canvas → fit to height, letterbox left/right
            new_h = H
            new_w = round(H * sw / sh)
            resized = src.resize((new_w, new_h), Image.LANCZOS)
            ox, oy = (W - new_w) // 2, 0

        canvas = Image.new("RGB", (W, H), (15, 15, 15))  # dark to match DJI photos
        canvas.paste(resized, (ox, oy))
        content_box = (ox, oy, ox + new_w, oy + new_h)
    else:
        # Fallback placeholder — same pattern as f150
        canvas = Image.new("RGB", (W, H), HW_BG)
        d = ImageDraw.Draw(canvas)
        d.text((W // 2 - 200, H // 2),
               f"[ Source photo not found: {filename} ]",
               font=fnt(18), fill=(140, 140, 140))
        content_box = (0, 0, W, H)

    d = ImageDraw.Draw(canvas)
    # Steel-grey shell bar with title
    d.rectangle([0, 0, W, 48], fill=HW_STEEL)
    d.text((20, 14), title, font=fnt(16, bold=True), fill=HW_WHITE)
    return canvas, d, content_box


# ── Scenario definition ─────────────────────────────────────────────────────
# Hotspot coordinates are tuned by-eye against the post-letterbox 1280×720
# canvas. Each step's screen function calls _load_letterboxed and the source
# photo is positioned per the math in that helper. If a source photo is
# replaced or the letterbox helper changes, hotspots must be re-tuned.
SCENARIO = {
    "id":               "drone_anatomy",
    "title":            "DJI Mavic 3 Pro — Anatomy & Pre-Flight Visual Inspection",
    "site":             "Commercial Operator — Generic Worksite",
    "role":             "Remote Pilot (Part 107)",
    "training_domain":  "hardware",
    "asset_source":     "oem_marketing",
    "branding":         DRONE_BRANDING,
    "handling_profile": None,
    "tutorial": [
        # ── Step 1 — Inspect the camera array ─────────────────────────────
        {
            "screen":      "step1_camera_array.png",
            "goal":        "Inspect the Hasselblad camera lens for fingerprints, dust, or moisture",
            "instruction": "Locate the wide-angle Hasselblad lens (the bottom-center of the three-lens array). Verify the front element is clean and the lens cap is removed.",
            "hint":        "The Hasselblad 4/3 CMOS wide is the LARGEST of the three lenses, sitting at the bottom of the triangular housing. It does the heavy lifting for most flights.",
            # Source: 1149×659, fit-to-height → new_w=1256, ox=12, oy=0.
            # Bottom-center Hasselblad wide lens at canvas ≈ (780, 540), ~200px diameter.
            "hotspot":     {"x": 680, "y": 450, "w": 200, "h": 200},
            "feedback":    "Hasselblad wide identified. Lens clear, no debris. Aircraft cleared for that camera.",
            "consequence": "A fingerprint on the wide-angle lens shows up as a soft halo across every shot. For a $400/hour commercial inspection flight, the operator either reshoots (burning a full battery and the daylight window) or delivers unusable footage. Wipe the lens with a microfiber cloth before every flight, every time.",
            "explore_info": [
                "Hasselblad 4/3 CMOS wide — 24mm equivalent, f/2.8–f/11, 20 MP. The primary photo/video camera. Used for ~80% of commercial work.",
                "1/1.3-inch medium tele — 70mm equivalent, 3× optical zoom, f/2.8, 48 MP. Mid-range subject framing.",
                "1/2-inch tele — 166mm equivalent, 7× optical (28× hybrid) zoom, f/3.4, 12 MP. Distant subject detail.",
                "Why three cameras — different focal lengths without changing lenses or losing flight time. Each is a separate optical path with its own sensor.",
                "What to look for — fingerprints (halos), dust (specks), moisture (foggy), and that the protective gimbal cover is removed before power-on.",
            ],
        },

        # ── Step 2 — Inspect the gimbal mount ─────────────────────────────
        {
            "screen":      "step2_gimbal.png",
            "goal":        "Verify the 3-axis gimbal moves freely and the protector is removed",
            "instruction": "Find the gimbal — the stabilized camera mount at the front-underside of the aircraft. Confirm no transport-protector clip is attached and that the gimbal hangs naturally from its mount.",
            "hint":        "The gimbal is the dark assembly directly below the camera array, between the front arms. On the ground (powered off) it should hang slightly loose.",
            # Source: 602×226, fit-to-width → new_w=1280, oy=119. Content y in [119, 600].
            # Gimbal/camera assembly at canvas ≈ (570, 380) to (710, 470).
            "hotspot":     {"x": 570, "y": 370, "w": 150, "h": 110},
            "feedback":    "Gimbal hangs free, no transport clip attached. Cleared for power-on self-test.",
            "consequence": "Powering on with the gimbal protector still attached forces the gimbal motors to fight against a fixed obstruction. The aircraft errors out, but if the operator clears the error and tries again without removing the clip, the gimbal motors can burn out — a $400 repair and a grounded aircraft until parts arrive. The protector is the single most-forgotten pre-flight removal.",
            "explore_info": [
                "Gimbal — 3-axis stabilized camera mount. Compensates for aircraft pitch, roll, and yaw to produce smooth video.",
                "Transport protector — a small plastic clip that immobilizes the gimbal during transport. Must be removed before power-on.",
                "Self-test sweep — on power-up the gimbal moves through its full range automatically. Watch for smooth motion on all three axes; any jerk or stuck axis = abort flight.",
                "Ribbon cable — a flat flex cable runs from the airframe to the gimbal. Can crack from repeated unfolding stress; symptom is intermittent video or gimbal drop.",
            ],
        },

        # ── Step 3 — Inspect the propellers ───────────────────────────────
        {
            "screen":      "step3_propellers.png",
            "goal":        "Inspect all four propellers for cracks, chips, or warping",
            "instruction": "Examine each propeller blade. Click on the front-left propeller to start the inspection. Confirm: no cracks, no nicks deeper than 1 mm, no warping when sighted edge-on.",
            "hint":        "Front-left is the propeller in the upper-left of this top-down view. Cracks hide near the hub where the blade meets the mounting; nicks show on the leading edge.",
            # Source: 686×585 (10:40:38, the actual top-down photo). Fit-to-height → new_w=844, ox=218.
            # Front-left propeller (hub + blades) spans canvas ≈ (180, 130) to (470, 320).
            "hotspot":     {"x": 180, "y": 130, "w": 280, "h": 220},
            "feedback":    "Front-left propeller inspected. No cracks, leading edge clean, no warp. Move on to FR, RL, RR.",
            "consequence": "A cracked propeller is silent until throttle-up. The crack opens under centripetal load and the blade fragments — sometimes within seconds of takeoff. The aircraft loses lift on that arm and crashes within a few rotor diameters of the takeoff point. This is the single most common cause of preventable hull losses in small commercial UAS, and it is always caught at pre-flight or never caught at all.",
            "explore_info": [
                "Propeller — the lifting surface. Carbon-fiber composite on the Mavic 3 Pro. Generates lift via rotation; fails by cracking near the hub or chipping on the leading edge.",
                "CW/CCW pairs — diagonally opposite propellers spin the same direction (e.g. FL and RR are CW, FR and RL are CCW). Mounting one on the wrong arm = no lift.",
                "1 mm nick rule — any nick deeper than 1 mm on the leading edge degrades aerodynamics enough to require replacement. Quick check with a fingernail.",
                "Warping — sight along the blade edge-on. A warped blade vibrates at high RPM and loosens its mount mid-flight.",
                "Replace pairs — if you replace one prop, replace its diagonal partner too. Mismatched mass causes vibration that shows up in footage.",
            ],
        },

        # ── Step 4 — Inspect top forward vision sensors ──────────────────
        {
            "screen":      "step4_top_vision.png",
            "goal":        "Verify the forward vision sensors are clean and unobstructed",
            "instruction": "Locate the two forward-facing vision sensors on top of the airframe (the dark circular lenses above the camera array). Confirm both are clean — no fingerprints, no dust, no stickers.",
            "hint":        "The top vision sensors are the two small dark dots on the upper front of the body, just above and behind the main camera. They look like tiny camera lenses.",
            # Source: 613×419, fit-to-height → new_w=1053, ox=113, oy=0.
            # Forward vision sensors (the two small dark dots on the upper-front body)
            # at canvas ≈ (590, 240) and (680, 240).
            "hotspot":     {"x": 560, "y": 220, "w": 170, "h": 80},
            "feedback":    "Forward vision sensors clean. Obstacle avoidance system has eyes.",
            "consequence": "Dirty or obstructed vision sensors don't fail loudly — they fail silently. The aircraft thinks the obstacle path is clear and flies into it. A common scenario: a sticker from the previous owner that the new operator never noticed; or condensation from a humid morning that nobody wiped. Result: a $2000 hull dropped into a tree because the aircraft believed there wasn't a tree there.",
            "explore_info": [
                "Forward vision sensors — two small cameras on the top-front of the body. Provide stereoscopic depth perception forward of the aircraft.",
                "Obstacle avoidance — the aircraft uses these (plus other vision sensors) to detect and route around obstacles in flight modes that support APAS.",
                "What blocks them — fingerprints, condensation, dust, ND filter cases that overhang, propeller guards mounted incorrectly, or stickers/decals.",
                "How to test — DJI Fly app shows a vision system status indicator. If sensors are obstructed it warns at startup; if smudged it warns mid-flight.",
            ],
        },

        # ── Step 5 — Inspect bottom vision sensors ────────────────────────
        {
            "screen":      "step5_bottom_vision.png",
            "goal":        "Verify the downward vision sensors and landing pad are clean",
            "instruction": "Look at the underside of the aircraft. Find the downward vision sensor cluster (the dark recessed area near the front-belly). Confirm the lenses are clean and the landing pad is dry and unobstructed.",
            "hint":        "Flip the aircraft mentally — you're looking at the belly here. The vision sensor cluster is on the front-underside, between the gimbal and the body.",
            # Source: 658×577, fit-to-height → new_w=821, ox=229, oy=0.
            # Belly sensor cluster (the recessed slatted area with two dark
            # sensor lenses) at canvas ≈ (480, 350) to (650, 410).
            "hotspot":     {"x": 470, "y": 340, "w": 200, "h": 80},
            "feedback":    "Bottom vision sensors clean, landing pad clear. Aircraft can hold position and land precisely.",
            "consequence": "Bottom vision sensors are what let the aircraft hold position when GPS is weak (under bridges, near tall buildings) and what let it land precisely on a small pad. Dirty or wet sensors = position drift in flight and missed landings on tight rooftops or marine vessels. For inspection work, drift takes the camera off the subject. For landing on a moving platform (boat deck, vehicle roof), a missed landing is a hull loss.",
            "explore_info": [
                "Downward vision sensors — stereo cameras on the belly. Provide ground-relative position when GPS is degraded or unavailable indoors.",
                "Time-of-flight sensor — a separate IR rangefinder that measures altitude above ground. Combined with the cameras for precision landing.",
                "Why this matters indoors — without GPS, these sensors are the ONLY thing keeping the aircraft from drifting into walls. A blocked sensor turns indoor flight into a coin flip.",
                "Landing precision — for autonomous return-to-home, the aircraft uses these sensors to land within ~10 cm of takeoff. Dirty sensors = wider miss radius.",
                "Cleaning — microfiber cloth, no solvent. The lenses have an anti-reflective coating that breaks down with isopropyl.",
            ],
        },
    ],
    "mission": {
        "title":      "Pre-Flight Visual Inspection",
        "briefing":   "You're the operator. The aircraft has been sitting in a case overnight — it might be perfect, or someone might have left the gimbal protector on, smudged a vision sensor, or chipped a prop. Five components stand between this aircraft and the air. Walk around, eyes open, every flight.",
        "par_clicks":  5,
        "time_limit":  180,
        "narratives": [
            "First flight of the morning. Cold case, low light, the temptation to skip the walk-around is highest right now.",
            "Rental aircraft, returned by a previous operator. You don't know what's been done to this airframe — assume nothing is right until you've checked it yourself.",
            "Humid coastal site. Condensation on every glass surface. Wipe before powering on, not after the first error message.",
            "Crew of two; the other operator handed you the aircraft and said 'it's good to go.' Other operators are wrong sometimes. Your name is on the Part 107.",
        ],
        "learning_objectives": {
            0: [
                "Identify the three Hasselblad cameras and their roles (wide / medium tele / tele)",
                "Locate the gimbal, the four propellers, and both pairs of vision sensors",
                "Understand why each component is on the visual pre-flight list",
            ],
            1: [
                "Walk through the inspection in a consistent order (front → top → underside)",
                "Recognize the failure modes each visual check is meant to catch",
                "Build muscle memory for the walk-around so it takes under 60 seconds",
            ],
            2: [
                "Perform the inspection from memory with no on-screen highlights",
                "Recognize when a check has surfaced a real problem vs. a false alarm",
                "Decide when to abort the flight vs. clean and re-inspect",
            ],
            3: [
                "Complete the full inspection in under three minutes",
                "Demonstrate that no component was skipped under time pressure",
                "Hand a cleared aircraft to a wing pilot or to your own takeoff sequence",
            ],
        },
    },
}


# ── Screen generators ───────────────────────────────────────────────────────
# Each function loads its source photo, applies letterbox, draws shell bar,
# annotates the hotspot (or decoys for neutral mode), and writes the status
# banner. Hotspot coords are the same dict used in SCENARIO[tutorial][i].

def _step1_camera_array(hl=True):
    img, d, _ = _load_letterboxed(
        "mavic3pro_camera_array_side.png",
        "Pre-Flight 1/5 — Camera Array Inspection",
    )
    hs = SCENARIO["tutorial"][0]["hotspot"]
    annotate_region(img, hs, label="1", hl=hl)
    if not hl:
        # Decoys — the upper two lenses (medium tele on left, tele on right)
        annotate_region(img, {"x": 540, "y": 130, "w": 200, "h": 200}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 800, "y": 130, "w": 200, "h": 200}, label="?", hl=False, decoy=True)
    hardware_status_banner(
        d,
        "Click the wide-angle Hasselblad lens (bottom-center of the 3-lens array)." if hl
        else "Identify and inspect the wide-angle Hasselblad lens.",
        ok=True,
    )
    return img


def _step2_gimbal(hl=True):
    img, d, _ = _load_letterboxed(
        "mavic3pro_front_view_propsout.png",
        "Pre-Flight 2/5 — Gimbal Mount Inspection",
    )
    hs = SCENARIO["tutorial"][1]["hotspot"]
    annotate_region(img, hs, label="2", hl=hl)
    if not hl:
        # Decoys — propeller hubs at the corners
        annotate_region(img, {"x": 80, "y": 250, "w": 130, "h": 80}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 1080, "y": 250, "w": 130, "h": 80}, label="?", hl=False, decoy=True)
    hardware_status_banner(
        d,
        "Click the gimbal — the camera mount hanging below the body." if hl
        else "Verify the 3-axis gimbal moves freely and the transport clip is removed.",
        ok=True,
    )
    return img


def _step3_propellers(hl=True):
    img, d, _ = _load_letterboxed(
        "mavic3pro_top_down.png",
        "Pre-Flight 3/5 — Propeller Inspection",
    )
    hs = SCENARIO["tutorial"][2]["hotspot"]
    annotate_region(img, hs, label="3", hl=hl)
    if not hl:
        # Decoys — front-right and rear-left props (top-down view, all 4 props visible)
        annotate_region(img, {"x": 720, "y": 130, "w": 280, "h": 220}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 180, "y": 380, "w": 280, "h": 220}, label="?", hl=False, decoy=True)
    hardware_status_banner(
        d,
        "Click the front-left propeller to begin inspection." if hl
        else "Inspect each propeller for cracks, nicks, and warping. Start with front-left.",
        ok=True,
    )
    return img


def _step4_top_vision(hl=True):
    img, d, _ = _load_letterboxed(
        "mavic3pro_front_low_angle.png",
        "Pre-Flight 4/5 — Forward Vision Sensors",
    )
    hs = SCENARIO["tutorial"][3]["hotspot"]
    annotate_region(img, hs, label="4", hl=hl)
    if not hl:
        # Decoys — left propeller hub and the camera array (the obvious lens, not a sensor)
        annotate_region(img, {"x": 220, "y": 250, "w": 160, "h": 140}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 560, "y": 320, "w": 170, "h": 100}, label="?", hl=False, decoy=True)
    hardware_status_banner(
        d,
        "Click the forward vision sensors — the two dark dots on top of the body." if hl
        else "Verify the forward vision sensors are clean.",
        ok=True,
    )
    return img


def _step5_bottom_vision(hl=True):
    img, d, _ = _load_letterboxed(
        "mavic3pro_underbelly.png",
        "Pre-Flight 5/5 — Bottom Vision Sensors",
    )
    hs = SCENARIO["tutorial"][4]["hotspot"]
    annotate_region(img, hs, label="5", hl=hl)
    if not hl:
        # Decoys — gimbal/camera assembly on right and motor mount on left arm
        annotate_region(img, {"x": 700, "y": 220, "w": 180, "h": 130}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 230, "y": 200, "w": 140, "h": 110}, label="?", hl=False, decoy=True)
    hardware_status_banner(
        d,
        "Click the downward vision sensor cluster on the belly." if hl
        else "Verify the downward vision sensors and landing pad are clean.",
        ok=True,
    )
    return img


# ── Screen registry ─────────────────────────────────────────────────────────
SCREEN_GENERATORS = {
    "step1_camera_array.png":  _step1_camera_array,
    "step2_gimbal.png":        _step2_gimbal,
    "step3_propellers.png":    _step3_propellers,
    "step4_top_vision.png":    _step4_top_vision,
    "step5_bottom_vision.png": _step5_bottom_vision,
}


def generate_screens(screens_dir):
    """Generate annotated PNGs into screens_dir/ (highlighted) and screens_neutral/."""
    screens_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = screens_dir.parent / "screens_neutral"
    neutral_dir.mkdir(parents=True, exist_ok=True)

    for fname, fn in SCREEN_GENERATORS.items():
        fn(hl=True).save(str(screens_dir / fname))
        fn(hl=False).save(str(neutral_dir / fname))

    return list(SCREEN_GENERATORS.keys())
