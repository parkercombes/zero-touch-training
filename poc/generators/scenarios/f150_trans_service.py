"""
scenarios/f150_trans_service.py — Ford F-150 Shift Lever & Seal Service
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Training domain: HARDWARE
  - 7-step maintenance procedure (shift lever removal → seal replacement
    → mount inspection → reassembly)
  - Safety verification (jackstands, battery disconnect) before undercar work
  - Torque specifications matter — wrong values damage soft aluminum housings
  - Covers common DIY maintenance that prevents expensive shop visits

Source material: Haynes manual Chapter 7 Part A — Manual Transmission
  Pages are scanned photographs stored in docs/F150/page_*.png

To adapt for a different vehicle procedure:
  1. Copy this file
  2. Update SCENARIO metadata
  3. Replace tutorial steps with new procedure
  4. Add source photos to docs/ and update _PAGE_DIR
  5. Run: python3 ui_trainer.py scenarios/f150_trans_service
"""

from pathlib import Path
from PIL import Image, ImageDraw

from scenarios.base_hardware import (
    W, H, fnt,
    HARDWARE_BRANDING,
    HW_STEEL, HW_ORANGE, HW_GREEN, HW_BLUE, HW_RED,
    HW_WHITE, HW_BG, HW_LABEL, HW_BORDER,
    load_base_image, annotate_region, draw_callout,
    draw_component_label, new_hardware_screen,
    hardware_status_banner, placeholder_note,
)

# ── Source page images ───────────────────────────────────────────────────────
# Scanned manual pages extracted from the PDF at 200 DPI.
_PAGE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "F150"

# Page dimensions at 200 DPI (approximate):
#   page_1.png: 1345 x 2000  (shift lever, torque specs, general info)
#   page_2.png: 1379 x 2000  (oil seal, mount check)
#   page_3.png: 1424 x 2000  (mount removal, transmission R&I)
#   page_4.png: 1348 x 2000  (installation, overhaul info)


# ── Vehicle-specific branding override ───────────────────────────────────────
F150_BRANDING = {
    **HARDWARE_BRANDING,
    "level_descriptions": [
        "Study the manual photos. No time pressure. Learn each component and tool.",
        "Follow each step with visual guidance. Build proper technique.",
        "No highlights. Hints cost time. Wrong moves show real consequences.",
        "Timed scenario. No help. Prove you can service it under pressure.",
    ],
}


# ── Scenario definition ─────────────────────────────────────────────────────

SCENARIO = {
    "id":               "f150_trans_service",
    "title":            "F-150 Shift Lever & Seal Service",
    "site":             "Home Garage / Field Maintenance",
    "role":             "Maintenance Technician",
    "training_domain":  "hardware",
    "asset_source":     "textbook",
    "branding":         F150_BRANDING,
    "handling_profile": None,
    "tutorial": [
        # ── Step 1: Remove shift lever boot ─────────────────────────────
        {
            "screen":      "step1_remove_boot.png",
            "goal":        "Remove the shift lever boot and retainer clips",
            "instruction": "Remove the shift lever boot retainer clips and pull up the boot to expose the shift lever mounting hardware.",
            "hint":        "The retainer clips are spring clips around the base of the boot. Pry gently — they pop free. Pull the rubber boot straight up.",
            "hotspot":     {"x": 90, "y": 240, "w": 280, "h": 250},
            "feedback":    "Boot retainer clips removed. Shift lever boot pulled up. Mounting hardware exposed.",
            "consequence": "Tearing the boot by prying too aggressively means you'll need a replacement. A torn boot lets water and debris into the transmission tunnel, causing corrosion on the shift linkage and eventually hard shifting.",
            "explore_info": [
                "Shift lever boot — the rubber or leather cover that seals the shift lever opening in the floor. Keeps road noise, exhaust fumes, and moisture out of the cabin.",
                "Retainer clips — spring steel clips that hold the boot to the floor pan. Usually 4 clips around the perimeter.",
                "Shift lever — the stick you grab to change gears. Mounted on an eccentric stud that allows adjustment.",
                "Floor pan opening — the hole in the transmission tunnel where the shift lever passes through. Should be sealed when reassembled.",
                "Inner boot — a second rubber boot below the outer one, attached with 4 screws. Provides additional sealing.",
            ],
        },
        # ── Step 2: Remove shift lever nut and lever ────────────────────
        {
            "screen":      "step2_remove_lever.png",
            "goal":        "Remove the shift lever using the eccentric stud technique",
            "instruction": "Remove the shift lever nut and install it on the other side of the stud. Tighten the nut to remove the eccentric stud, then lift out the shift lever.",
            "hint":        "The nut threads onto the stud — move it to the OTHER side so tightening pulls the stud out instead of holding it in. This is the factory removal method.",
            "hotspot":     {"x": 400, "y": 240, "w": 280, "h": 250},
            "feedback":    "Shift lever nut reversed on stud. Eccentric stud extracted. Shift lever lifted out cleanly.",
            "consequence": "Trying to pry the lever out without using the nut-reversal technique bends the eccentric stud. A bent stud means sloppy shifter feel and the lever won't center properly in the gates. Replacement studs are hard to find.",
            "explore_info": [
                "Eccentric stud — an off-center mounting stud that allows fine adjustment of shift lever position. The eccentricity lets you center the lever in the shift pattern.",
                "Nut reversal technique — the factory method for removal. Threading the nut onto the opposite side turns the nut into a puller. Much cleaner than prying.",
                "Shift lever seating — the lever sits in a socket on the transmission tailshaft housing extension. It must be fully seated on reassembly.",
                "Illustration 2.2a — shows the nut being moved to the opposite side of the stud.",
                "Illustration 2.2b — shows tightening the reversed nut to extract the eccentric stud and lever.",
            ],
        },
        # ── Step 3: Remove inner shift lever boot ───────────────────────
        {
            "screen":      "step3_inner_boot.png",
            "goal":        "Remove the inner shift lever boot",
            "instruction": "Remove the four boot retaining screws from the inner shift lever boot (the black rubber square-shaped boot below the shift lever). Remove the boot.",
            "hint":        "Four screws, one at each corner of the square rubber boot. A stubby screwdriver helps in the tight space. Keep the screws — they're specific to this application.",
            "hotspot":     {"x": 480, "y": 280, "w": 260, "h": 220},
            "feedback":    "Four retaining screws removed. Inner boot lifted out. Transmission tunnel opening fully exposed.",
            "consequence": "Cross-threading the screws on reinstallation strips the threads in the floor pan. You'll need to tap new threads or use a larger screw. Take your time — these are small screws in soft metal.",
            "explore_info": [
                "Inner boot — the secondary seal below the outer boot. Square-shaped black rubber. Sits directly on the transmission tunnel.",
                "Four retaining screws — small Phillips-head screws at each corner. They thread into the floor pan.",
                "Transmission tunnel — the raised section of the floor pan that the driveshaft and transmission pass through.",
                "Sealing surfaces — both the inner and outer boots must seal properly to prevent exhaust fumes from entering the cabin. A CO leak here is a safety hazard.",
            ],
        },
        # ── Step 4: Raise vehicle and inspect for leaks ─────────────────
        {
            "screen":      "step4_raise_inspect.png",
            "goal":        "Raise the vehicle and inspect the extension housing seal",
            "instruction": "Raise the vehicle and support it securely on jackstands. Inspect the extension housing area at the rear of the transmission for oil leaks. Look for wetness on the front of the driveshaft.",
            "hint":        "The extension housing seal is at the very back of the transmission, where the driveshaft connects. If you see oil on the front U-joint area of the driveshaft, the seal is leaking.",
            "hotspot":     {"x": 60, "y": 130, "w": 460, "h": 260},
            "feedback":    "Vehicle raised and supported on jackstands. Extension housing area inspected. Leak confirmed at the seal — oil visible on driveshaft yoke.",
            "consequence": "Working under a vehicle supported only by a jack is how people die in home garages. A hydraulic jack can fail, bleed down, or get knocked. Jackstands on solid ground are non-negotiable. Every year mechanics are crushed because they skipped this step.",
            "explore_info": [
                "Extension housing — the aluminum housing at the rear of the transmission that contains the output shaft and rear seal. The driveshaft yoke slides into it.",
                "Extension housing seal — a lip seal that prevents transmission fluid from leaking out around the output shaft. Common wear item.",
                "Driveshaft yoke — the front end of the driveshaft that slides into the transmission output shaft. If the seal leaks, you'll see oil on the yoke surface.",
                "Jackstands — rated support stands placed under the vehicle frame. NEVER work under a vehicle supported only by a jack.",
                "Transmission fluid — if the level drops from a seal leak, the transmission can overheat and fail. A $5 seal prevents a $2,000+ rebuild.",
            ],
        },
        # ── Step 5: Remove old extension housing seal ───────────────────
        {
            "screen":      "step5_remove_seal.png",
            "goal":        "Remove the old extension housing seal",
            "instruction": "Remove the driveshaft (Chapter 8). Using a soft-face hammer, carefully tap off the dust shield. Using a screwdriver or seal removal tool, pry out the extension housing seal. Do not damage the splines on the output shaft.",
            "hint":        "Pry evenly around the seal — don't dig the screwdriver into the aluminum bore. The seal sits in a machined bore and should pry out without excessive force.",
            "hotspot":     {"x": 60, "y": 130, "w": 460, "h": 260},
            "feedback":    "Driveshaft removed. Dust shield off. Old seal pried out cleanly without bore damage. Output shaft splines intact.",
            "consequence": "Gouging the aluminum seal bore with a screwdriver means the new seal won't seat properly and will leak from day one. The bore surface must be smooth and round. If you damage it, the housing needs to be replaced — a $300+ part plus labor.",
            "explore_info": [
                "Seal removal tool — a hooked tool designed to pry seals out without damaging the bore. A flat-blade screwdriver works but requires more care.",
                "Dust shield — a thin metal shield in front of the seal that keeps road debris away. Tap gently to remove — don't bend it.",
                "Seal bore — the machined recess in the extension housing where the seal press-fits. Must remain smooth and round.",
                "Output shaft splines — the grooved shaft that the driveshaft yoke slides onto. Scratching these causes vibration.",
                "Illustration 3.4 — shows the seal being pried out with a removal tool.",
            ],
        },
        # ── Step 6: Install new seal ────────────────────────────────────
        {
            "screen":      "step6_install_seal.png",
            "goal":        "Install the new extension housing seal",
            "instruction": "Using a seal driver or a large deep socket, install the new extension housing seal. Drive it squarely into the bore and make sure it's completely seated. Reinstall the dust shield.",
            "hint":        "The seal must go in SQUARE — if it cocks to one side, it will leak. A large socket that matches the outer diameter of the seal works as a driver. Tap evenly around the circumference.",
            "hotspot":     {"x": 200, "y": 150, "w": 400, "h": 280},
            "feedback":    "New seal driven squarely into bore. Fully seated. Dust shield tapped back into place. Seal lip facing inward toward transmission.",
            "consequence": "Installing the seal crooked is the #1 cause of 'new seal still leaks' complaints. The seal lip must contact the output shaft evenly around its entire circumference. A cocked seal leaks immediately, and you'll have to pull the driveshaft again to redo it.",
            "explore_info": [
                "Seal driver — a tool sized to press the seal in evenly. Match the outside diameter of the seal. A large deep socket works in a pinch.",
                "Seal orientation — the lip (spring) side faces INWARD toward the transmission fluid. The flat side faces outward. Installing it backward guarantees a leak.",
                "Seating depth — the seal should be flush with or slightly below the surface of the bore. Don't drive it too deep.",
                "Illustration 3.5 — shows the new seal being driven in with a seal driver or large deep socket.",
                "Grease the lip — apply a thin film of transmission fluid or grease to the seal lip before installing the driveshaft. Dry installation can cut the lip.",
            ],
        },
        # ── Step 7: Check transmission mount ────────────────────────────
        {
            "screen":      "step7_check_mount.png",
            "goal":        "Check the transmission mount for wear",
            "instruction": "Insert a large screwdriver or prybar into the space between the transmission and crossmember. Try to lever the transmission up and down. If it moves easily, the mount rubber is worn and must be replaced.",
            "hint":        "You're checking for separation of the rubber insulator from the metal plates. Any visible cracking, tearing, or easy movement means replacement. Torque mount-to-crossmember nuts to 72 ft-lbs.",
            "hotspot":     {"x": 60, "y": 380, "w": 360, "h": 280},
            "feedback":    "Transmission mount inspected. Rubber shows cracking — mount scheduled for replacement. Mount-to-crossmember nut torque verified at 72 ft-lbs.",
            "consequence": "A worn transmission mount lets the transmission shift under load, which stresses the driveshaft U-joints, exhaust connections, and shift linkage. Symptoms include clunking on acceleration, vibration at speed, and shifter slop that gets worse over time. A $40 mount prevents hundreds in cascading damage.",
            "explore_info": [
                "Transmission mount — a rubber-bonded-to-metal insulator that supports the transmission weight and absorbs vibration. Located between the transmission and the crossmember.",
                "Crossmember — the structural steel beam that spans the frame rails under the transmission. The mount bolts to it from below.",
                "Prybar test — the standard check for mount condition. A good mount allows minimal movement. Excessive movement means the rubber has separated.",
                "Mount-to-crossmember nuts — torque to 72 ft-lbs per spec. Under-torqued nuts allow the mount to shift; over-torqued nuts crack the crossmember.",
                "Illustration 4.1 — shows the prybar inserted between transmission and crossmember to test mount condition.",
                "Cascade failure — a bad mount stresses the driveshaft angles, which kills U-joints. U-joint failure at highway speed can be catastrophic.",
            ],
        },
    ],
    "mission": {
        "title":      "Weekend Wrench Session",
        "briefing":   "Your F-150 has a transmission fluid leak and the shifter feels sloppy. You've got the parts and the afternoon. Fix the seal, check the mount, and get it road-ready before Monday.",
        "par_clicks":  10,
        "time_limit":  300,
        "narratives": [
            "Your wife's car is blocked in the garage until this truck moves. Clock's ticking.",
            "Parts store closes at 5. If you need anything else, you better find out now.",
            "Your buddy said he could do this in an hour. Let's see if you can beat that.",
            "The inspection is next week. This leak will fail you. Get it done right.",
        ],
        "learning_objectives": {
            0: [
                "Identify shift lever mounting components and the eccentric stud",
                "Understand extension housing seal location and function",
                "Learn transmission mount inspection technique",
            ],
            1: [
                "Follow the correct removal sequence for shift lever components",
                "Practice the nut-reversal technique for eccentric stud removal",
                "Build technique for seal removal without bore damage",
            ],
            2: [
                "Perform the full service procedure from memory",
                "Identify real-world consequences of common mistakes",
                "Complete the service with minimal hint usage",
            ],
            3: [
                "Execute the full service under time pressure",
                "Demonstrate mastery of all torque specs and techniques",
                "Prove you can do this in your own garage",
            ],
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# SCREEN GENERATORS — cropped manual page photographs
# ═════════════════════════════════════════════════════════════════════════════

def _page_screen(page_num, title, crop_box=None):
    """Load a manual page, optionally crop, resize to canvas, add shell bar.

    Args:
        page_num: 1-based page number (maps to page_{n}.png)
        title:    Title text for the steel shell bar
        crop_box: Optional (left, upper, right, lower) crop tuple in
                  source pixel coordinates.  If None, uses full page.

    Returns:
        (img, draw)
    """
    page_path = _PAGE_DIR / f"page_{page_num}.png"

    if page_path.exists():
        img = Image.open(page_path).convert("RGB")
        if crop_box:
            img = img.crop(crop_box)
        img = img.resize((W, H), Image.LANCZOS)
    else:
        # Fallback placeholder
        img = Image.new("RGB", (W, H), HW_BG)
        d = ImageDraw.Draw(img)
        d.text((W // 2 - 200, H // 2),
               f"[ Manual page {page_num} not found ]",
               font=fnt(18), fill=(140, 140, 140))

    d = ImageDraw.Draw(img)
    # Steel-grey shell bar with title
    d.rectangle([0, 0, W, 48], fill=HW_STEEL)
    d.text((20, 14), title, font=fnt(16, bold=True), fill=HW_WHITE)
    return img, d


# ── Crop regions (source pixel coordinates at 200 DPI) ───────────────────
# Page 1 (1345x2000): shift lever illustrations at bottom
_P1_SHIFT_LEVER_LEFT  = (0,    1150, 680,  2000)   # Illustration 2.2a
_P1_SHIFT_LEVER_RIGHT = (440,  1150, 1345, 2000)   # Illustration 2.2b + text
_P1_FULL_BOTTOM       = (0,    1050, 1345, 2000)   # Both illustrations + procedure text

# Page 2 (1379x2000): seal illustrations at top, mount at bottom
_P2_SEAL_TOP          = (0,    0,    1379, 700)    # Illustrations 3.4 and 3.5
_P2_SEAL_LEFT         = (0,    0,    690,  700)    # Illustration 3.4 (removal)
_P2_SEAL_RIGHT        = (640,  0,    1379, 700)    # Illustration 3.5 (install)
_P2_MOUNT_BOTTOM      = (0,    900,  1379, 2000)   # Illustrations 4.1, 4.2 + text

# Page 3 (1424x2000): transmission R&I photos
_P3_UPPER             = (0,    0,    1424, 500)    # Mount bolts illustration 4.3 + 5.21


def screen_step1_remove_boot(hl=True):
    """Page 1 bottom — shift lever illustration 2.2a as primary target."""
    img, d = _page_screen(1, "F-150 Service — Step 1: Remove Shift Lever Boot",
                          crop_box=_P1_FULL_BOTTOM)
    hs = SCENARIO["tutorial"][0]["hotspot"]
    annotate_region(img, hs, label="1", hl=hl)
    if hl:
        draw_callout(img, 200, 270, "Boot retainer clips", anchor="right")
        draw_callout(img, 150, 380, "Pull boot up", anchor="right")
    if not hl:
        annotate_region(img, {"x": 500, "y": 300, "w": 120, "h": 80},
                        label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 800, "y": 250, "w": 100, "h": 60},
                        label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Pry retainer clips gently. Pull boot straight up." if hl
                           else "Remove the shift lever boot and retainer clips.", ok=True)
    return img


def screen_step2_remove_lever(hl=True):
    """Page 1 bottom — illustration 2.2b, eccentric stud removal."""
    img, d = _page_screen(1, "F-150 Service — Step 2: Remove Shift Lever",
                          crop_box=_P1_FULL_BOTTOM)
    hs = SCENARIO["tutorial"][1]["hotspot"]
    annotate_region(img, hs, label="2", hl=hl)
    if hl:
        draw_callout(img, 520, 280, "Reverse nut onto stud", anchor="right")
        draw_callout(img, 500, 380, "Tighten to extract", anchor="right")
    if not hl:
        annotate_region(img, {"x": 100, "y": 350, "w": 120, "h": 80},
                        label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 820, "y": 400, "w": 100, "h": 60},
                        label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Move nut to other side of stud. Tighten to pull stud out." if hl
                           else "Remove the shift lever using the nut reversal technique.", ok=True)
    return img


def screen_step3_inner_boot(hl=True):
    """Page 1 bottom — text area showing inner boot removal procedure."""
    img, d = _page_screen(1, "F-150 Service — Step 3: Remove Inner Boot",
                          crop_box=_P1_FULL_BOTTOM)
    hs = SCENARIO["tutorial"][2]["hotspot"]
    annotate_region(img, hs, label="3", hl=hl)
    if hl:
        draw_callout(img, 620, 340, "4 retaining screws", anchor="left")
    if not hl:
        annotate_region(img, {"x": 200, "y": 280, "w": 130, "h": 80},
                        label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 500, "y": 400, "w": 110, "h": 60},
                        label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Four screws at corners. Stubby screwdriver for tight space." if hl
                           else "Remove the inner shift lever boot (4 screws).", ok=True)
    return img


def screen_step4_raise_inspect(hl=True):
    """Page 2 top — seal area, extension housing illustrations 3.4/3.5."""
    img, d = _page_screen(2, "F-150 Service — Step 4: Raise Vehicle & Inspect",
                          crop_box=_P2_SEAL_TOP)
    hs = SCENARIO["tutorial"][3]["hotspot"]
    annotate_region(img, hs, label="4", hl=hl)
    if hl:
        draw_callout(img, 300, 200, "Extension housing seal", anchor="right")
        draw_callout(img, 200, 300, "Check for oil on driveshaft", anchor="right")
    if not hl:
        annotate_region(img, {"x": 600, "y": 200, "w": 140, "h": 80},
                        label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 900, "y": 300, "w": 120, "h": 70},
                        label="?", hl=False, decoy=True)
    hardware_status_banner(d, "SAFETY: Jackstands on solid ground. NEVER just a jack." if hl
                           else "Raise vehicle, support on jackstands, inspect seal area.", ok=True)
    return img


def screen_step5_remove_seal(hl=True):
    """Page 2 — illustration 3.4 (seal removal with tool)."""
    img, d = _page_screen(2, "F-150 Service — Step 5: Remove Old Seal",
                          crop_box=_P2_SEAL_LEFT)
    hs = SCENARIO["tutorial"][4]["hotspot"]
    annotate_region(img, hs, label="5", hl=hl)
    if hl:
        draw_callout(img, 350, 250, "Seal removal tool", anchor="right")
        draw_callout(img, 200, 180, "Don't gouge the bore", anchor="right")
    if not hl:
        annotate_region(img, {"x": 600, "y": 300, "w": 120, "h": 70},
                        label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 400, "y": 450, "w": 130, "h": 60},
                        label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Pry evenly around the seal. Protect the bore surface." if hl
                           else "Remove the old extension housing seal.", ok=True)
    return img


def screen_step6_install_seal(hl=True):
    """Page 2 — illustration 3.5 (seal installation with driver/socket)."""
    img, d = _page_screen(2, "F-150 Service — Step 6: Install New Seal",
                          crop_box=_P2_SEAL_RIGHT)
    hs = SCENARIO["tutorial"][5]["hotspot"]
    annotate_region(img, hs, label="6", hl=hl)
    if hl:
        draw_callout(img, 350, 220, "Seal driver / deep socket", anchor="right")
        draw_callout(img, 300, 340, "Drive SQUARE into bore", anchor="right")
    if not hl:
        annotate_region(img, {"x": 100, "y": 250, "w": 130, "h": 70},
                        label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 650, "y": 350, "w": 110, "h": 60},
                        label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Lip side faces IN. Drive squarely. Must be fully seated." if hl
                           else "Install the new extension housing seal.", ok=True)
    return img


def screen_step7_check_mount(hl=True):
    """Page 2 bottom — illustration 4.1 (mount prybar check)."""
    img, d = _page_screen(2, "F-150 Service — Step 7: Check Transmission Mount",
                          crop_box=_P2_MOUNT_BOTTOM)
    hs = SCENARIO["tutorial"][6]["hotspot"]
    annotate_region(img, hs, label="7", hl=hl)
    if hl:
        draw_callout(img, 300, 450, "Prybar between trans & crossmember", anchor="right")
        draw_callout(img, 250, 550, "Check rubber for cracks", anchor="right")
    if not hl:
        annotate_region(img, {"x": 500, "y": 400, "w": 130, "h": 80},
                        label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 800, "y": 500, "w": 120, "h": 70},
                        label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Lever up/down. Easy movement = worn mount. Torque nuts to 72 ft-lbs." if hl
                           else "Check the transmission mount for wear or separation.", ok=True)
    return img


# ── Screen generator registry ────────────────────────────────────────────────

SCREEN_GENERATORS = {
    "step1_remove_boot.png":    screen_step1_remove_boot,
    "step2_remove_lever.png":   screen_step2_remove_lever,
    "step3_inner_boot.png":     screen_step3_inner_boot,
    "step4_raise_inspect.png":  screen_step4_raise_inspect,
    "step5_remove_seal.png":    screen_step5_remove_seal,
    "step6_install_seal.png":   screen_step6_install_seal,
    "step7_check_mount.png":    screen_step7_check_mount,
}


def generate_screens(screens_dir):
    """Generate annotated manual-photo PNGs into screens_dir/ and screens_neutral/."""
    screens_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = screens_dir.parent / "screens_neutral"
    neutral_dir.mkdir(parents=True, exist_ok=True)

    for fname, fn in SCREEN_GENERATORS.items():
        fn(hl=True).save(str(screens_dir / fname))
        fn(hl=False).save(str(neutral_dir / fname))

    return list(SCREEN_GENERATORS.keys())
