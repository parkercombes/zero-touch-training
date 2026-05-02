"""
scenarios/drone_preflight.py — Consumer Drone Pre-Flight Inspection (HW/SW Fusion)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Training domain: FUSION (hardware + software in one scenario)

Why this scenario exists
  This is the third PoC area. The first two (SAP MIGO and AR-15 / F-150 hardware)
  proved that the engine handles software-only and hardware-only domains. This
  scenario proves the engine handles MIXED domains in one ordered procedure
  without engine code changes — alternating hardware photo annotation and
  software app screens within a single trainer.

  Why drone pre-flight: it is genuinely interleaved (operators do alternate HW
  and SW checks every flight), commercial-only (no defense classification or
  IP issues), and the asset categories that would feed a real version of this
  scenario map cleanly to assets every drone OEM and operator already maintains.

Scope
  Six steps, 3 hardware + 3 software, alternating. Just enough to demonstrate
  step-type alternation. NOT a complete pre-flight — a real deployment would
  expand to ~12 steps and source real photographs and app captures.

Mockup substitutes used here (and what they'd be in production)
  Step images       : Pillow-drawn placeholders         → OEM marketing photos / Playwright app captures
  Procedure         : Inferred from public Part 107 +   → Operator manual / IETM
                      manufacturer pre-flight guidance
  Failure modes     : Public crash reports / forum lore → FMEA, maintenance history
  Branding          : Generic safety-orange / steel     → OEM-specific branding token

To adapt for a real customer's airframe + app
  1. Copy this file
  2. Update SCENARIO metadata (airframe model, app name, role)
  3. Replace placeholder PNGs with real photos / captures
  4. Update tutorial steps with actual procedure + hotspots
  5. Run: python3 ui_trainer.py scenarios/<your_scenario>

The leave-behind asset checklist for production deployment is in
docs/hw-sw-fusion-required-assets.md.
"""

from PIL import Image, ImageDraw

from scenarios.base import (
    fnt, W, H,
    new_screen, draw_shell_bar, draw_field, draw_button,
    draw_status_banner, draw_card, draw_subheader,
)
from scenarios.base_hardware import (
    HARDWARE_BRANDING,
    HW_STEEL, HW_ORANGE, HW_GREEN, HW_BLUE, HW_RED,
    HW_WHITE, HW_BG, HW_LABEL, HW_BORDER,
    new_hardware_screen, placeholder_note as hw_placeholder_note,
    draw_component_label, hardware_status_banner,
)


# ── Branding ────────────────────────────────────────────────────────────────
# Fusion scenarios use the hardware palette as a base because hardware steps
# anchor the "physical reality" frame. Software steps appear inside this same
# palette so the trainee experiences one consistent interface, not two stitched
# together. A real customer would override these with their OEM's brand colors.
DRONE_BRANDING = {
    **HARDWARE_BRANDING,
    "level_descriptions": [
        "Walk through the pre-flight inspection. Hardware checks alternate with app checks. No timer.",
        "Follow each step with visual guidance. Build the alternation rhythm.",
        "No highlights. Skipping a check has consequences. Hints cost time.",
        "Timed pre-flight. No help. Prove you can clear an aircraft for flight.",
    ],
}


# ── Step image generators ───────────────────────────────────────────────────
# Each function returns a Pillow Image. In production these would be real
# photographs (hardware) or Playwright captures (software). Drawing them
# in code here keeps the PoC self-contained and lets the engine and asset
# pipeline be evaluated independently of imagery sourcing.
#
# Each renderer takes hl=True/False to produce two versions:
#   hl=True   → hotspot highlighted (used in Level 1 GUIDED / FOLLOW ALONG)
#   hl=False  → neutral, no highlight (Levels 0, 2, 3)


def _hotspot_overlay(d, hotspot, color=HW_ORANGE):
    """Draw a translucent highlight box + border over a hotspot region."""
    x, y = hotspot["x"], hotspot["y"]
    w, h = hotspot["w"], hotspot["h"]
    # Border
    d.rectangle([x - 4, y - 4, x + w + 4, y + h + 4], outline=color, width=4)


def _hw_step_propellers(hl=True):
    """Step 1 — top-down view of drone with four propellers, one slightly off."""
    img = Image.new("RGB", (W, H), HW_BG)
    d = ImageDraw.Draw(img)

    # Body — central hexagon-ish shape
    cx, cy = W // 2, H // 2
    body_size = 80
    d.rectangle([cx - body_size, cy - body_size, cx + body_size, cy + body_size],
                fill=HW_STEEL, outline=HW_LABEL, width=3)
    d.text((cx - 30, cy - 8), "MINI 4", fill=HW_WHITE, font=fnt(14, bold=True))

    # Four arms extending diagonally + propellers
    arm_len = 200
    propeller_positions = [
        (cx - arm_len, cy - arm_len, "FL", True),    # front-left, OK
        (cx + arm_len, cy - arm_len, "FR", True),    # front-right, OK
        (cx - arm_len, cy + arm_len, "RL", False),   # rear-left, MISSEATED (highlighted)
        (cx + arm_len, cy + arm_len, "RR", True),    # rear-right, OK
    ]
    for px, py, label, ok in propeller_positions:
        # Arm
        d.line([cx, cy, px, py], fill=HW_STEEL, width=8)
        # Propeller hub
        prop_color = HW_ORANGE if not ok else HW_LABEL
        d.ellipse([px - 35, py - 35, px + 35, py + 35], outline=prop_color, width=4 if not ok else 2)
        # Propeller blades (two crossed lines)
        d.line([px - 50, py - 10, px + 50, py + 10], fill=prop_color, width=6 if not ok else 4)
        d.line([px - 50, py + 10, px + 50, py - 10], fill=prop_color, width=6 if not ok else 4)
        d.text((px - 12, py + 40), label, fill=HW_LABEL, font=fnt(13, bold=True))

    hardware_status_banner(d, "PRE-FLIGHT — Visual Inspection", ok=True)
    draw_component_label(img, 60, 60, 200, 30, "Aircraft Top View", "Inspect all four propellers")

    if hl:
        _hotspot_overlay(d, {"x": 380, "y": 480, "w": 130, "h": 130})
    return img


def _hw_step_battery(hl=True):
    """Step 3 — battery latched into airframe, with latch detail."""
    img = Image.new("RGB", (W, H), HW_BG)
    d = ImageDraw.Draw(img)

    # Drone body cutaway
    d.rectangle([320, 200, 960, 480], fill=HW_STEEL, outline=HW_LABEL, width=3)
    d.text((350, 215), "AIRCRAFT BODY (rear view)", fill=HW_WHITE, font=fnt(13, bold=True))

    # Battery slot
    d.rectangle([400, 260, 880, 440], fill=(40, 40, 40), outline=HW_LABEL, width=2)
    d.text((430, 280), "INTELLIGENT FLIGHT BATTERY", fill=HW_WHITE, font=fnt(14, bold=True))
    # Capacity LEDs
    for i, lit in enumerate([True, True, True, False]):  # 75% indicator
        led_color = HW_GREEN if lit else (60, 60, 60)
        d.ellipse([450 + i * 30, 320, 470 + i * 30, 340], fill=led_color, outline=HW_WHITE)
    d.text((450, 350), "75% (3 of 4 LEDs)", fill=HW_WHITE, font=fnt(12))

    # Latch — on the right edge, the focal point
    latch_x, latch_y = 880, 350
    d.rectangle([latch_x - 10, latch_y - 30, latch_x + 30, latch_y + 30],
                fill=HW_ORANGE, outline=HW_LABEL, width=2)
    d.text((latch_x + 40, latch_y - 10), "LATCH", fill=HW_LABEL, font=fnt(13, bold=True))
    d.text((latch_x + 40, latch_y + 6), "Must click", fill=HW_LABEL, font=fnt(11))

    hardware_status_banner(d, "PRE-FLIGHT — Battery Check", ok=True)
    draw_component_label(img, 60, 60, 200, 30, "Battery Compartment", "Verify latch fully seated")

    if hl:
        _hotspot_overlay(d, {"x": 870, "y": 320, "w": 60, "h": 60})
    return img


def _hw_step_gimbal(hl=True):
    """Step 5 — gimbal at front of aircraft, full range of motion test."""
    img = Image.new("RGB", (W, H), HW_BG)
    d = ImageDraw.Draw(img)

    # Drone front view
    d.rectangle([400, 220, 880, 460], fill=HW_STEEL, outline=HW_LABEL, width=3)
    d.text((430, 235), "AIRCRAFT (front view)", fill=HW_WHITE, font=fnt(13, bold=True))

    # Gimbal mount — arc showing motion range
    gx, gy = 640, 380
    # Gimbal body
    d.ellipse([gx - 40, gy - 40, gx + 40, gy + 40], fill=(20, 20, 20), outline=HW_ORANGE, width=3)
    # Camera lens
    d.ellipse([gx - 20, gy - 20, gx + 20, gy + 20], fill=(80, 80, 80), outline=HW_WHITE, width=2)
    d.ellipse([gx - 12, gy - 12, gx + 12, gy + 12], fill=(20, 20, 20))
    # Motion arrows — pitch / yaw / roll
    d.arc([gx - 80, gy - 80, gx + 80, gy + 80], start=200, end=340, fill=HW_ORANGE, width=3)
    d.text((gx - 100, gy + 60), "↓ pitch", fill=HW_LABEL, font=fnt(12))
    d.text((gx + 50, gy + 60), "yaw →", fill=HW_LABEL, font=fnt(12))
    d.text((gx - 30, gy - 90), "↺ roll", fill=HW_LABEL, font=fnt(12))

    hardware_status_banner(d, "PRE-FLIGHT — Gimbal Self-Test", ok=True)
    draw_component_label(img, 60, 60, 220, 30, "Gimbal & Camera", "Confirms 3-axis motion on power-up")

    if hl:
        _hotspot_overlay(d, {"x": 600, "y": 340, "w": 80, "h": 80})
    return img


def _sw_step_app_open(hl=True):
    """Step 2 — DJI Fly-style app home screen, connection status visible."""
    img, d = new_screen("Drone Control App")
    draw_shell_bar(d, title="Drone Fly", initials="OP")

    # Aircraft connection card
    draw_card(d, 60, 110, 1220, 240, title="Aircraft Connection")
    d.text((90, 150), "AIRCRAFT", fill=HW_LABEL, font=fnt(13, bold=True))
    d.text((90, 175), "Mini 4 Pro · Connected", fill=HW_GREEN, font=fnt(16, bold=True))
    d.text((90, 205), "Firmware: v01.04.0500    App: v1.13.4", fill=HW_LABEL, font=fnt(12))
    d.text((90, 225), "✓ Compatible", fill=HW_GREEN, font=fnt(13))

    # The action button — the hotspot
    draw_button(d, 880, 160, 300, 70, "OPEN FLIGHT", primary=True, highlight=hl)

    # Below: signal indicators
    draw_card(d, 60, 270, 1220, 480, title="Pre-Flight Status")
    d.text((90, 310), "Signal:    ████████░░ 80%", fill=HW_LABEL, font=fnt(13))
    d.text((90, 340), "GPS:       Searching... (4/12 satellites)", fill=HW_ORANGE, font=fnt(13))
    d.text((90, 370), "Storage:   23.4 GB free", fill=HW_LABEL, font=fnt(13))
    d.text((90, 400), "Battery:   ▓▓▓░ 75%   (~22 min flight time)", fill=HW_LABEL, font=fnt(13))

    draw_status_banner(d, "Tap OPEN FLIGHT to enter pre-flight checklist", ok=True)
    return img


def _sw_step_gps_lock(hl=True):
    """Step 4 — GPS satellite lock screen, count and accuracy."""
    img, d = new_screen("Drone Control App")
    draw_shell_bar(d, title="Drone Fly · Pre-Flight", initials="OP")

    draw_card(d, 60, 110, 1220, 380, title="Position Lock")
    d.text((90, 160), "GPS Satellites:", fill=HW_LABEL, font=fnt(14, bold=True))
    d.text((90, 195), "14 / 12 minimum", fill=HW_GREEN, font=fnt(28, bold=True))
    d.text((90, 240), "✓ Lock acquired", fill=HW_GREEN, font=fnt(14))

    d.text((90, 290), "Horizontal Accuracy: 1.2 m", fill=HW_LABEL, font=fnt(13))
    d.text((90, 320), "Vertical Accuracy:   2.1 m", fill=HW_LABEL, font=fnt(13))

    # Map placeholder — the highlighted region
    d.rectangle([700, 150, 1180, 460], fill=(220, 230, 220), outline=HW_BORDER, width=2)
    d.text((720, 170), "Position", fill=HW_LABEL, font=fnt(13, bold=True))
    # Crosshair pin
    cx, cy = 940, 305
    d.line([cx - 30, cy, cx + 30, cy], fill=HW_RED, width=2)
    d.line([cx, cy - 30, cx, cy + 30], fill=HW_RED, width=2)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=HW_RED, outline=HW_WHITE, width=2)

    # Geofence status — ALSO IMPORTANT
    draw_card(d, 60, 410, 1220, 580, title="Airspace")
    d.text((90, 450), "NFZ Status:   ✓ Clear", fill=HW_GREEN, font=fnt(14, bold=True))
    d.text((90, 480), "Class:        Class G (uncontrolled)", fill=HW_LABEL, font=fnt(13))
    d.text((90, 510), "Max altitude: 400 ft AGL (Part 107)", fill=HW_LABEL, font=fnt(13))
    d.text((90, 540), "TFR check:   No active TFRs", fill=HW_GREEN, font=fnt(13))

    draw_status_banner(d, "Confirm satellite count is ≥ 12 before takeoff", ok=True)

    if hl:
        _hotspot_overlay(d, {"x": 90, "y": 195, "w": 300, "h": 60})
    return img


def _sw_step_rth_altitude(hl=True):
    """Step 6 — Return-to-home altitude configuration before arming."""
    img, d = new_screen("Drone Control App")
    draw_shell_bar(d, title="Drone Fly · Flight Settings", initials="OP")

    draw_card(d, 60, 110, 1220, 380, title="Return-to-Home (RTH) Configuration")
    d.text((90, 160), "RTH Altitude:", fill=HW_LABEL, font=fnt(14, bold=True))

    # The numeric input field — this is the hotspot
    draw_field(d, 90, 195, 300, 50, "", "120 m", highlight=hl)
    d.text((420, 215), "Default: 30 m  ·  Recommended for this site: 120 m", fill=HW_LABEL, font=fnt(13))

    # Reasoning
    d.text((90, 280), "Local obstacles within 500 m:", fill=HW_LABEL, font=fnt(13, bold=True))
    d.text((90, 310), "  • Cell tower:    98 m AGL", fill=HW_LABEL, font=fnt(13))
    d.text((90, 335), "  • Office tower: 105 m AGL", fill=HW_LABEL, font=fnt(13))
    d.text((90, 360), "  ⚠  RTH altitude must exceed tallest obstacle.", fill=HW_RED, font=fnt(13, bold=True))

    # Mode selection
    draw_card(d, 60, 410, 1220, 580, title="Flight Mode")
    d.text((90, 450), "○ Cine     ● Normal     ○ Sport", fill=HW_LABEL, font=fnt(14, bold=True))
    d.text((90, 480), "Normal: balanced response, full obstacle sensing active.", fill=HW_LABEL, font=fnt(13))

    # CTA at the bottom
    draw_button(d, 880, 510, 300, 60, "READY TO ARM", primary=True)

    draw_status_banner(d, "Set RTH altitude above local obstacles before arming", ok=True)
    return img


# ── Step image registry ─────────────────────────────────────────────────────
# Maps screen filename → renderer. ui_trainer.py calls these to generate PNGs.
SCREEN_GENERATORS = {
    "step1_propellers.png":   _hw_step_propellers,
    "step2_app_open.png":     _sw_step_app_open,
    "step3_battery.png":      _hw_step_battery,
    "step4_gps_lock.png":     _sw_step_gps_lock,
    "step5_gimbal.png":       _hw_step_gimbal,
    "step6_rth_altitude.png": _sw_step_rth_altitude,
}


def generate_screens(screens_dir):
    """Generate annotated PNGs into screens_dir/ and screens_neutral/."""
    screens_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = screens_dir.parent / "screens_neutral"
    neutral_dir.mkdir(parents=True, exist_ok=True)

    for fname, fn in SCREEN_GENERATORS.items():
        fn(hl=True).save(str(screens_dir / fname))
        fn(hl=False).save(str(neutral_dir / fname))

    return list(SCREEN_GENERATORS.keys())


# ── Scenario definition ─────────────────────────────────────────────────────
SCENARIO = {
    "id":               "drone_preflight",
    "title":            "Drone Pre-Flight Inspection (HW/SW Fusion PoC)",
    "site":             "Commercial Operator — Generic Worksite",
    "role":             "Remote Pilot (Part 107)",
    # "fusion" is a new training_domain value. The React engine doesn't branch
    # on it — IS_HARDWARE check returns false (it's not "hardware"), so the
    # engine treats steps as software-style by default. Hardware-style step
    # images simply look like hardware photos within that same engine flow.
    # This is what we wanted to validate: no engine code changes needed.
    "training_domain":  "fusion",
    "asset_source":     "placeholder",
    "branding":         DRONE_BRANDING,
    "handling_profile": None,
    "tutorial": [
        # ── Step 1 (HW) — Propeller seating ────────────────────────────────
        {
            "screen":      "step1_propellers.png",
            "step_kind":   "hardware",
            "goal":        "Verify all four propellers are seated and matched (CW/CCW)",
            "instruction": "Inspect each propeller. Confirm the locking mechanism is fully engaged and that CW/CCW propellers are on the correct arms.",
            "hint":        "One of the four propellers is highlighted — look for the one that doesn't match the others. A misseated propeller will appear loose or off-axis.",
            "hotspot":     {"x": 380, "y": 480, "w": 130, "h": 130},  # rear-left propeller
            "feedback":    "Propeller misseat caught. The trainee identified the rear-left propeller before takeoff.",
            "consequence": "An unseated propeller separates in flight within seconds of throttle-up. The aircraft loses lift on that arm and crashes within a few rotor diameters of the takeoff point. This is one of the most common preventable causes of small-UAS hull losses, and it is always caught at pre-flight or never caught at all.",
            "explore_info": [
                "Propeller — generates lift. Rotates one direction only; FL and RR are CW, FR and RL are CCW (or vice versa per OEM).",
                "Hub — locks the propeller to the motor shaft via a quarter-turn or push-and-twist mechanism.",
                "Why this matters in pre-flight — propellers are removed for transport. They are also the single point that fails most often in flight, and the failure is silent until throttle-up.",
            ],
        },
        # ── Step 2 (SW) — Open app, confirm aircraft binding ──────────────
        {
            "screen":      "step2_app_open.png",
            "step_kind":   "software",
            "goal":        "Confirm the aircraft is paired and on a compatible firmware",
            "instruction": "Open the flight app. Verify the aircraft model, firmware version, and that it reports as Connected and Compatible.",
            "hint":        "Tap the OPEN FLIGHT button to enter the pre-flight checklist. Note the firmware and app version match the compatible list.",
            "hotspot":     {"x": 880, "y": 160, "w": 300, "h": 70},  # OPEN FLIGHT button
            "feedback":    "Aircraft connection confirmed: Mini 4 Pro, firmware v01.04.0500, app v1.13.4 — compatible.",
            "consequence": "An aircraft on mismatched firmware will throttle some flight modes silently. The operator gets in the air thinking they have full obstacle sensing, discovers mid-flight that obstacle avoidance is disabled, and finds out from a tree. Always read the version banner before opening flight.",
            "explore_info": [
                "Firmware — embedded software on the aircraft. Updated periodically by the OEM.",
                "App version — the operator's mobile/tablet app. Must be on the OEM's compatibility matrix for the firmware version.",
                "Why this matters — firmware/app mismatches degrade flight features without obvious warnings. The compatibility check is a one-second tap that prevents silent feature loss.",
            ],
        },
        # ── Step 3 (HW) — Battery latched ─────────────────────────────────
        {
            "screen":      "step3_battery.png",
            "step_kind":   "hardware",
            "goal":        "Confirm battery is fully latched into the airframe",
            "instruction": "Press the battery firmly into the compartment until the latch clicks. Visually verify there is no gap between battery and airframe.",
            "hint":        "The latch is on the right edge of the battery compartment. It should sit flush — any gap means it isn't fully engaged.",
            "hotspot":     {"x": 870, "y": 320, "w": 60, "h": 60},  # the latch
            "feedback":    "Battery latch fully engaged. Click confirmed.",
            "consequence": "A battery that vibrates loose mid-flight cuts power to the motors instantaneously. The aircraft drops from altitude with no glide. This failure mode killed enough commercial sUAS programs that DJI added a redundant latch sensor in firmware — but that sensor only catches a fully unlatched battery, not a half-seated one. Mechanical click is still the gold-standard check.",
            "explore_info": [
                "Battery — the Intelligent Flight Battery powers both the motors and the avionics. Hot-swappable on the ground.",
                "Latch — the physical mechanism that holds the battery in place against vibration and the upward thrust component.",
                "LED indicator — battery state-of-charge. 4 LEDs = 100%, 1 LED = ≤25%. Pre-flight minimum is typically 50%.",
            ],
        },
        # ── Step 4 (SW) — GPS satellite lock ──────────────────────────────
        {
            "screen":      "step4_gps_lock.png",
            "step_kind":   "software",
            "goal":        "Confirm GPS satellite count meets minimum for stable hover",
            "instruction": "Wait for satellite count to reach ≥ 12 before arming. Verify horizontal accuracy is < 2 m and that no NFZ alert is active for your location.",
            "hint":        "The satellite count is at the top of the Position Lock card. If it's still searching (orange), wait — never take off on a partial lock.",
            "hotspot":     {"x": 90, "y": 195, "w": 300, "h": 60},  # the satellite count number
            "feedback":    "GPS lock acquired: 14 satellites, 1.2 m horizontal accuracy. Airspace clear.",
            "consequence": "Taking off on a weak GPS lock means the aircraft can't hold position. It drifts on a windy day until it either hits something or the operator manually fights it back. In a worst case, the drift takes the aircraft outside the operator's visual line of sight (a Part 107 violation) before they realize it's drifting.",
            "explore_info": [
                "Satellite count — number of GPS/GNSS satellites the aircraft has lock on. More = more accurate position.",
                "Horizontal accuracy — the radius of position uncertainty. Under 2 m is good for autonomous hover; over 5 m is unsafe.",
                "NFZ (No-Fly Zone) — geofenced airspace where takeoff is blocked. Includes airports, stadiums during events, and active TFRs.",
                "Part 107 — the FAA Part 107 small UAS rule, the regulatory framework for commercial sUAS operations.",
            ],
        },
        # ── Step 5 (HW) — Gimbal motion check ─────────────────────────────
        {
            "screen":      "step5_gimbal.png",
            "step_kind":   "hardware",
            "goal":        "Verify gimbal moves through full range on power-up self-test",
            "instruction": "Watch the gimbal during the power-up sequence. It should pitch, yaw, and roll through its full range. No grinding, no stuck axes.",
            "hint":        "The gimbal is at the front of the aircraft. On a clean power-up it makes a smooth motion sweep. Any jerkiness or stuck axis means a bad gimbal motor or a transport-lock that wasn't removed.",
            "hotspot":     {"x": 600, "y": 340, "w": 80, "h": 80},  # gimbal body
            "feedback":    "Gimbal motion confirmed across all three axes. Self-test complete.",
            "consequence": "A stuck gimbal that flies anyway produces unstable footage — every frame jitters because the gimbal is fighting against a stuck axis. For commercial operators, that's a wasted flight. For inspection or mapping work, it's a missed deliverable. Worse cases: a gimbal that disconnects mid-flight because of a damaged ribbon cable, dropping the camera assembly.",
            "explore_info": [
                "Gimbal — 3-axis stabilized mount for the camera. Compensates for aircraft motion to produce smooth video.",
                "Self-test — automatic motion sweep on power-up that verifies each motor and axis works.",
                "Transport lock — a small clip some OEMs ship to immobilize the gimbal during transport. Easy to forget. Causes immediate self-test failure.",
            ],
        },
        # ── Step 6 (SW) — RTH altitude config ─────────────────────────────
        {
            "screen":      "step6_rth_altitude.png",
            "step_kind":   "software",
            "goal":        "Set Return-to-Home altitude above local obstacles",
            "instruction": "Set the RTH altitude in the field. The value must exceed the tallest obstacle within 500 m of the takeoff point (here: 105 m office tower → set 120 m or higher).",
            "hint":        "The RTH altitude field is at the top of the Return-to-Home card. Default is 30 m — too low for this site. Set 120 m.",
            "hotspot":     {"x": 90, "y": 195, "w": 300, "h": 50},  # the RTH altitude input
            "feedback":    "RTH altitude set to 120 m, clearing the 105 m office tower with margin.",
            "consequence": "If the aircraft loses controller signal and triggers RTH at the default 30 m, it climbs to 30 m and flies straight back to launch — directly into the 105 m office tower it just took off near. RTH-into-obstacle is one of the most preventable hull losses in commercial operation. The operator's responsibility is to know the obstacles and set the altitude above them, every flight, even if the takeoff site looks the same as yesterday.",
            "explore_info": [
                "RTH (Return-to-Home) — the autonomous flight mode the aircraft enters on signal loss, low battery, or operator command.",
                "RTH altitude — the altitude the aircraft climbs to before flying back to the home point. Must exceed obstacles in the return path.",
                "Home point — the GPS coordinate the aircraft considers its takeoff origin. Set automatically on satellite lock.",
                "Why operator-set, not automatic — the OEM doesn't know your site's obstacles. Setting RTH altitude is the operator's affirmative pre-flight decision.",
            ],
        },
    ],
    # Mission dict — this is what the engine expects. Without it, the level-select
    # click handlers throw on `mission.time_limit` and the React tree dies (black screen).
    "mission": {
        "title":      "Pre-Flight Inspection",
        "briefing":   "You're the operator. Six checks stand between this aircraft and the air. Three are physical — propellers, battery, gimbal. Three are software — app connection, GPS lock, RTH altitude. Skip any of them and you're trusting luck. Walk through it like a pro.",
        "par_clicks":  6,
        "time_limit":  240,
        "narratives": [
            "First flight of the morning. Cold battery, half-light, hurry — the temptation to rush is highest right now.",
            "New site. You've never flown here before. Obstacles you haven't seen, airspace you haven't checked. The default RTH altitude is the wrong altitude for this site.",
            "Firmware updated last night. The aircraft and app updated in the truck overnight. Compatibility is not guaranteed. The version banner is more important today than usual.",
            "Rental aircraft, returned by a previous operator. You don't know what's been done to this airframe. Inspect every step.",
        ],
        "learning_objectives": {
            0: [
                "Identify the four physical pre-flight checks: propellers, battery latch, gimbal motion",
                "Identify the three software pre-flight checks: app connection, GPS lock, RTH altitude",
                "Understand why pre-flight alternates between hardware and software",
            ],
            1: [
                "Follow the correct alternation rhythm: physical → app → physical → app",
                "Build muscle memory for visual inspection and app navigation in sequence",
                "Recognize the most common preventable failure modes",
            ],
            2: [
                "Perform the full pre-flight from memory with minimal hints",
                "Recognize when a step's failure mode is mechanical vs. configurational",
                "Make the RTH altitude decision based on local obstacles",
            ],
            3: [
                "Execute the full pre-flight under time pressure",
                "Demonstrate that no check was skipped under hurry",
                "Clear the aircraft for flight in under four minutes",
            ],
        },
    },
}
