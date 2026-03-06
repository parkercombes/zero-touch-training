"""
scenarios/ar15_field_strip.py — AR-15 Safe Field Strip & Cleaning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Training domain: HARDWARE
  - 8-step field strip procedure (clear → disassemble → inspect → reassemble)
  - Safety verification mandatory before any disassembly
  - Correct sequence prevents damage to components and injury
  - Emphasises muscle memory and procedural discipline

To adapt for a different firearm:
  1. Copy this file (e.g. glock19_field_strip.py, m4_field_strip.py)
  2. Update SCENARIO metadata (id, title, site, role)
  3. Update tutorial steps (goals, instructions, hotspots, consequences)
  4. Replace placeholder screens with real photographs
  5. Run: python3 ui_trainer.py scenarios/your_scenario
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


# ── Scenario definition ───────────────────────────────────────────────────────

SCENARIO = {
    "id":               "ar15_field_strip",
    "title":            "AR-15 Safe Field Strip & Cleaning",
    "site":             "Range Safety Training Center",
    "role":             "Armorer Trainee",
    "training_domain":  "hardware",
    "branding":         HARDWARE_BRANDING,
    "handling_profile": None,
    "tutorial": [
        # ── Step 1: Verify clear ──────────────────────────────────────────
        {
            "screen":      "step1_verify_clear.png",
            "goal":        "Verify the weapon is clear",
            "instruction": "Remove the magazine and lock the bolt to the rear. Visually and physically inspect the chamber.",
            "hint":        "Press the magazine release, pull the charging handle, and lock the bolt open. Look into the ejection port.",
            "hotspot":     {"x": 480, "y": 200, "w": 280, "h": 120},
            "feedback":    "Weapon verified clear. Magazine removed, bolt locked, chamber empty.",
            "consequence": "Skipping clearance verification is the #1 cause of negligent discharges during maintenance. Every cleaning-related accident starts with someone who 'knew' it was unloaded.",
            "explore_info": [
                "Ejection port — the opening on the right side of the upper receiver. When the bolt is locked back, you can see directly into the chamber through here.",
                "Magazine release — button on the right side, just above the trigger guard. Press to drop the magazine.",
                "Charging handle — T-shaped handle at the rear of the upper receiver. Pull rearward to cycle the bolt.",
                "Bolt catch — paddle on the left side of the lower receiver. Press upward to lock the bolt to the rear.",
                "Chamber — where the round sits. Must be visually AND physically clear (finger check) before any work begins.",
                "Forward assist — round button on right side of upper receiver. Not used during clearing. Pushes bolt forward into battery.",
            ],
        },
        # ── Step 2: Separate upper and lower ──────────────────────────────
        {
            "screen":      "step2_takedown_pins.png",
            "goal":        "Push out the takedown pins",
            "instruction": "Push the rear takedown pin from left to right, then the front pivot pin. Separate upper and lower receivers.",
            "hint":        "Use your thumb or a punch. Rear pin first, then front. They only need to go halfway — don't force them all the way out.",
            "hotspot":     {"x": 540, "y": 340, "w": 180, "h": 60},
            "feedback":    "Pins pushed. Upper and lower receivers separated cleanly.",
            "consequence": "Forcing the pins with a hard tool can wallop the finish and deform the pin holes. Over time, loose pin holes cause receiver wobble and accuracy loss. Always push — never hammer.",
            "explore_info": [
                "Rear takedown pin — connects the rear of the upper and lower receivers. Push left-to-right to disengage.",
                "Front pivot pin — connects the front of the upper and lower receivers. Push left-to-right after the rear pin.",
                "Upper receiver — houses the bolt carrier group, barrel, and handguard. The 'top half.'",
                "Lower receiver — houses the trigger group, magazine well, buffer tube, and stock. The serialised part (legally the 'firearm').",
                "Tip — if a pin is stiff, tap gently with a brass punch. Never use steel on aluminum.",
            ],
        },
        # ── Step 3: Remove charging handle + BCG ─────────────────────────
        {
            "screen":      "step3_remove_bcg.png",
            "goal":        "Remove the bolt carrier group and charging handle",
            "instruction": "With the upper receiver separated, pull the charging handle rearward and lift out the bolt carrier group (BCG).",
            "hint":        "Tilt the upper receiver so the BCG slides toward you. Pull the charging handle partway back, then slide it out from its channel.",
            "hotspot":     {"x": 300, "y": 180, "w": 320, "h": 140},
            "feedback":    "BCG and charging handle removed. Upper receiver is now empty.",
            "consequence": "Yanking the BCG without tilting the receiver can gouge the inside of the upper. Carbon buildup makes it sticky — patience prevents scratches on the bearing surfaces.",
            "explore_info": [
                "Bolt carrier group (BCG) — the heart of the rifle. Contains the bolt, cam pin, firing pin, and gas key. This is where all the action happens.",
                "Charging handle — rides in a channel on top of the upper receiver. Must be pulled back before the BCG can exit.",
                "Gas key — the small tube on top of the bolt carrier. Connects to the gas tube. If the screws are loose, you get short-stroking.",
                "Bolt — the cylindrical piece at the front of the BCG. Has locking lugs that engage the barrel extension.",
                "Cam pin — holds the bolt in the carrier and controls rotation. Remove before the bolt can come out.",
            ],
        },
        # ── Step 4: Disassemble the bolt ──────────────────────────────────
        {
            "screen":      "step4_disassemble_bolt.png",
            "goal":        "Remove the firing pin and cam pin from the bolt carrier",
            "instruction": "Push out the firing pin retaining pin, remove the firing pin, then lift out the cam pin. Slide the bolt out last.",
            "hint":        "Retaining pin first (it's the small cotter pin at the rear). Then the firing pin drops out. Rotate the cam pin 90° and lift.",
            "hotspot":     {"x": 400, "y": 260, "w": 240, "h": 100},
            "feedback":    "Bolt disassembled. Firing pin, cam pin, and bolt separated for inspection.",
            "consequence": "Removing the cam pin before the firing pin bends the retaining pin and can crack the carrier. Sequence matters: retaining pin → firing pin → cam pin → bolt. Every time.",
            "explore_info": [
                "Firing pin retaining pin — small cotter pin at the rear of the bolt carrier. Prevents the firing pin from falling out. Remove first.",
                "Firing pin — long thin pin that strikes the primer. Once the retaining pin is out, it slides out the back of the carrier.",
                "Cam pin — sits in a slot in the bolt carrier. Rotate 90° to align with the removal slot, then lift straight up.",
                "Bolt — after the cam pin is out, the bolt slides forward out of the carrier. Note the extractor and ejector.",
                "Extractor — spring-loaded claw on the bolt face. Grips the cartridge rim during extraction. Check the spring tension.",
                "Ejector — spring-loaded plunger in the bolt face. Kicks the spent case out the ejection port.",
            ],
        },
        # ── Step 5: Inspect and clean ─────────────────────────────────────
        {
            "screen":      "step5_inspect_clean.png",
            "goal":        "Inspect bolt face and lugs for wear or damage",
            "instruction": "Examine the bolt face for pitting, cracks, or carbon buildup. Check all locking lugs for even wear. Clean with solvent and a brush.",
            "hint":        "Look at the bolt face straight-on under good light. Carbon on the lugs is normal — cracks or chips are not.",
            "hotspot":     {"x": 380, "y": 200, "w": 260, "h": 200},
            "feedback":    "Bolt face and lugs inspected. No cracks. Carbon removed. Ready for lubrication.",
            "consequence": "A cracked bolt lug can shear off under pressure, causing a catastrophic failure. A pitted bolt face causes poor primer strikes and misfires. 30 seconds of inspection prevents a malfunction under fire.",
            "explore_info": [
                "Bolt face — the flat front surface of the bolt. Should be smooth with no pitting. Carbon buildup here causes headspace issues.",
                "Locking lugs — the star-shaped protrusions that lock into the barrel extension. All lugs must show even wear. Uneven wear = alignment problem.",
                "Extractor — check for a strong spring. Weak extractors cause failure-to-extract (FTE) malfunctions.",
                "Gas rings — three rings on the bolt body (like piston rings). Stack the gaps — if you can see through all three gaps at once, replace them.",
                "Firing pin tip — should be rounded, not mushroomed or flat. A deformed tip causes light strikes.",
            ],
        },
        # ── Step 6: Lubricate ─────────────────────────────────────────────
        {
            "screen":      "step6_lubricate.png",
            "goal":        "Apply lubricant to the bolt carrier group",
            "instruction": "Apply a thin film of CLP to the bolt body, cam pin channel, and bolt carrier rails. Don't over-lubricate.",
            "hint":        "A few drops on each contact surface. Wipe excess. The bolt carrier rails and cam pin slot are the critical friction points.",
            "hotspot":     {"x": 320, "y": 280, "w": 300, "h": 80},
            "feedback":    "BCG lubricated. Thin film on all bearing surfaces. No excess pooling.",
            "consequence": "Too little lube causes metal-on-metal wear and premature part failure. Too much attracts dust and carbon, creating an abrasive paste. The bolt carrier rails and cam pin slot are where most friction occurs — focus there.",
            "explore_info": [
                "Bolt carrier rails — the two raised tracks on the outside of the bolt carrier. These ride in channels inside the upper receiver. Primary friction surface.",
                "Cam pin slot — the channel where the cam pin sits. Rotation here drives the bolt's locking/unlocking cycle. Must be lubricated.",
                "Bolt body — the cylindrical section behind the bolt face. Apply a thin film — it cycles thousands of times per range session.",
                "CLP (Cleaner, Lubricant, Protectant) — the standard military-issue all-in-one solution. Apply sparingly.",
                "Tip — 'If it moves, lube it. If it doesn't move, don't.' Over-lubrication is almost as bad as under-lubrication in a dusty environment.",
            ],
        },
        # ── Step 7: Reassemble ────────────────────────────────────────────
        {
            "screen":      "step7_reassemble.png",
            "goal":        "Reassemble the bolt carrier group",
            "instruction": "Slide bolt into carrier, insert cam pin (rotate 90°), drop firing pin in from the rear, replace retaining pin.",
            "hint":        "Reverse order: bolt → cam pin → firing pin → retaining pin. The cam pin only goes in one way — align the hole.",
            "hotspot":     {"x": 380, "y": 240, "w": 280, "h": 120},
            "feedback":    "BCG reassembled. All pins seated. Bolt rotates freely in the carrier.",
            "consequence": "Forgetting the firing pin retaining pin means the firing pin can walk out under recoil. Best case: misfires. Worst case: the pin drops into the trigger group and the rifle goes full-auto uncontrolled. Always verify the retaining pin is seated.",
            "explore_info": [
                "Assembly order — bolt → cam pin → firing pin → retaining pin. Exact reverse of disassembly. Sequence is critical.",
                "Cam pin orientation — the flat side faces outward. If it doesn't drop in smoothly, rotate 90°. Never force it.",
                "Firing pin — slides in from the rear of the bolt carrier. Should move freely. If it sticks, check for carbon in the channel.",
                "Retaining pin — snaps into the hole at the rear of the carrier. Verify it's fully seated (flush with the carrier surface).",
                "Function check — after assembly, push the bolt tail. The bolt should rotate and extend smoothly. If it binds, disassemble and re-check.",
            ],
        },
        # ── Step 8: Close and function check ──────────────────────────────
        {
            "screen":      "step8_function_check.png",
            "goal":        "Rejoin receivers and perform a function check",
            "instruction": "Seat the BCG and charging handle in the upper. Pivot the upper onto the lower and push both pins home. Perform a function check.",
            "hint":        "Front pivot pin first, then rear takedown pin. Pull charging handle to charge. Pull trigger — hammer should fall. Safety on, pull trigger — nothing. Safety off, pull trigger — hammer falls.",
            "hotspot":     {"x": 500, "y": 310, "w": 240, "h": 80},
            "feedback":    "Receivers joined. Function check passed: trigger, safety, bolt release all verified. Weapon is clean, lubed, and mission-ready.",
            "consequence": "Skipping the function check means you won't know if you reassembled something wrong until the rifle fails at the worst possible moment. A 15-second function check catches 99% of reassembly errors — trigger reset, safety engagement, and bolt lockback.",
            "explore_info": [
                "Pivot pin (front) — seat first. Aligns the front lug of the upper into the lower receiver.",
                "Takedown pin (rear) — push home last. Locks the receivers together.",
                "Function check procedure — (1) Charge the weapon. (2) Point safe direction, pull trigger: click. (3) Safety ON, pull trigger: no click. (4) Safety OFF, pull trigger: click. (5) Lock bolt back, release with bolt catch: bolt goes forward.",
                "Charging handle — must be fully seated before closing the receivers. If it's proud, the upper won't pivot down.",
                "Buffer tube — houses the buffer and recoil spring in the stock. If the BCG doesn't cycle smoothly, check that the buffer retainer is seated.",
            ],
        },
    ],
    "mission": {
        "title":      "Range Day Prep",
        "briefing":   "Your squad is heading to the range in 15 minutes. Field strip, inspect, clean, lube, and reassemble your M4. Sergeant is watching.",
        "par_clicks":  12,
        "time_limit":  300,
        "narratives": [
            "Sergeant Rodriguez is doing spot inspections. Your rifle better be spotless.",
            "Range goes hot in 10 minutes. The rest of the squad is already done.",
            "New armorer trainee is watching you. Show proper technique — they're learning from your example.",
            "Post-deployment maintenance check. Every weapon gets stripped and inspected before turn-in.",
        ],
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# SCREEN GENERATORS — placeholder diagrams (replace with real photos later)
# ═════════════════════════════════════════════════════════════════════════════

def _draw_rifle_silhouette(d, x=100, y=200, w=1000, h=250, label="AR-15 / M4"):
    """Draw a simplified rifle outline as a placeholder base."""
    # Stock
    d.rounded_rectangle([x, y + 60, x + 180, y + h - 30], radius=8,
                        fill=(200, 200, 200), outline=HW_BORDER, width=2)
    d.text((x + 20, y + 100), "Stock / Buffer Tube", font=fnt(10), fill=HW_LABEL)
    # Lower receiver
    d.rounded_rectangle([x + 170, y + 40, x + 480, y + h - 10], radius=6,
                        fill=(210, 210, 210), outline=HW_BORDER, width=2)
    d.text((x + 200, y + 55), "Lower Receiver", font=fnt(11, bold=True), fill=HW_LABEL)
    # Trigger guard
    d.rounded_rectangle([x + 280, y + h - 50, x + 380, y + h + 10], radius=10,
                        fill=(220, 220, 220), outline=HW_BORDER, width=1)
    d.text((x + 285, y + h - 35), "Trigger", font=fnt(9), fill=HW_LABEL)
    # Magazine well
    d.rectangle([x + 320, y + h + 5, x + 380, y + h + 80],
                fill=(195, 195, 195), outline=HW_BORDER, width=1)
    d.text((x + 325, y + h + 15), "Mag\nWell", font=fnt(9), fill=HW_LABEL)
    # Upper receiver
    d.rounded_rectangle([x + 170, y, x + 700, y + 80], radius=6,
                        fill=(190, 190, 190), outline=HW_BORDER, width=2)
    d.text((x + 200, y + 10), "Upper Receiver", font=fnt(11, bold=True), fill=HW_LABEL)
    # Barrel + handguard
    d.rounded_rectangle([x + 480, y + 10, x + w, y + 70], radius=4,
                        fill=(180, 180, 180), outline=HW_BORDER, width=2)
    d.text((x + 520, y + 25), "Handguard / Barrel", font=fnt(11, bold=True), fill=HW_LABEL)
    # Ejection port
    d.rectangle([x + 420, y + 20, x + 480, y + 65],
                fill=(160, 160, 160), outline=HW_STEEL, width=1)
    d.text((x + 425, y + 30), "Ejection\nPort", font=fnt(9), fill=HW_LABEL)
    # Charging handle
    d.rectangle([x + 170, y - 15, x + 240, y + 5],
                fill=(175, 175, 175), outline=HW_BORDER, width=1)
    d.text((x + 175, y - 12), "CH", font=fnt(9, bold=True), fill=HW_LABEL)
    # Forward assist
    d.ellipse([x + 395, y + 20, x + 420, y + 50],
              fill=(170, 170, 170), outline=HW_BORDER, width=1)
    d.text((x + 398, y + 28), "FA", font=fnt(8), fill=HW_LABEL)


def _draw_bcg(d, x=300, y=180, w=600, h=280):
    """Draw a simplified bolt carrier group diagram."""
    # Carrier body
    d.rounded_rectangle([x, y + 60, x + w, y + 180], radius=8,
                        fill=(200, 200, 200), outline=HW_BORDER, width=2)
    d.text((x + 20, y + 80), "Bolt Carrier", font=fnt(13, bold=True), fill=HW_LABEL)
    # Gas key
    d.rectangle([x + 80, y + 30, x + 180, y + 65],
                fill=(185, 185, 185), outline=HW_BORDER, width=2)
    d.text((x + 90, y + 40), "Gas Key", font=fnt(10, bold=True), fill=HW_LABEL)
    # Bolt (front)
    d.ellipse([x - 40, y + 70, x + 40, y + 170],
              fill=(180, 180, 180), outline=HW_STEEL, width=2)
    d.text((x - 30, y + 105), "Bolt\nFace", font=fnt(10, bold=True), fill=HW_LABEL)
    # Cam pin
    d.rectangle([x + 60, y + 100, x + 100, y + 145],
                fill=(170, 170, 170), outline=HW_STEEL, width=1)
    d.text((x + 63, y + 108), "Cam\nPin", font=fnt(9), fill=HW_LABEL)
    # Firing pin channel (line through carrier)
    d.line([(x + w - 20, y + 120), (x - 30, y + 120)],
           fill=HW_STEEL, width=1)
    d.text((x + w - 100, y + 125), "Firing Pin", font=fnt(10), fill=HW_LABEL)
    # Retaining pin
    d.ellipse([x + w - 25, y + 110, x + w - 5, y + 130],
              fill=HW_ORANGE, outline=HW_STEEL, width=1)
    d.text((x + w + 5, y + 110), "Ret. Pin", font=fnt(9), fill=HW_LABEL)
    # Carrier rails
    d.rectangle([x + 10, y + 175, x + w - 10, y + 190],
                fill=(175, 175, 175), outline=HW_BORDER, width=1)
    d.text((x + 200, y + 176), "Carrier Rails (lube here)", font=fnt(10), fill=HW_LABEL)


def screen_step1_verify_clear(hl=True):
    """Full rifle view with ejection port / chamber as target."""
    img, d = new_hardware_screen("AR-15 Field Strip — Step 1: Verify Clear")
    _draw_rifle_silhouette(d)
    # Hotspot on ejection port / chamber area
    hs = SCENARIO["tutorial"][0]["hotspot"]
    annotate_region(img, hs, label="1", hl=hl)
    if not hl:
        # Decoys: magazine release and forward assist
        annotate_region(img, {"x": 380, "y": 350, "w": 80, "h": 60}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 200, "y": 200, "w": 120, "h": 50}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "SAFETY FIRST: Remove magazine. Lock bolt open. Inspect chamber." if hl
                           else "Verify the weapon is clear before proceeding.", ok=True)
    placeholder_note(d)
    return img


def screen_step2_takedown_pins(hl=True):
    """Rifle view focusing on takedown pins between upper and lower."""
    img, d = new_hardware_screen("AR-15 Field Strip — Step 2: Takedown Pins")
    _draw_rifle_silhouette(d)
    hs = SCENARIO["tutorial"][1]["hotspot"]
    annotate_region(img, hs, label="2", hl=hl)
    if not hl:
        annotate_region(img, {"x": 280, "y": 420, "w": 100, "h": 50}, label="?", hl=False, decoy=True)
    # Draw pin callouts
    if hl:
        draw_callout(img, 580, 345, "Rear Takedown Pin", anchor="right")
        draw_callout(img, 550, 380, "Front Pivot Pin", anchor="right")
    hardware_status_banner(d, "Push pins left-to-right. Rear first, then front." if hl
                           else "Separate the upper and lower receivers.", ok=True)
    placeholder_note(d)
    return img


def screen_step3_remove_bcg(hl=True):
    """Upper receiver with BCG visible, target on BCG."""
    img, d = new_hardware_screen("AR-15 Field Strip — Step 3: Remove BCG")
    # Draw just the upper receiver portion
    d.rounded_rectangle([60, 160, 1200, 400], radius=8,
                        fill=(220, 220, 220), outline=HW_BORDER, width=2)
    d.text((80, 170), "Upper Receiver (separated)", font=fnt(13, bold=True), fill=HW_LABEL)
    # BCG inside
    d.rounded_rectangle([280, 200, 900, 360], radius=6,
                        fill=(195, 195, 195), outline=HW_STEEL, width=2)
    d.text((300, 210), "Bolt Carrier Group (BCG)", font=fnt(12, bold=True), fill=HW_LABEL)
    # Charging handle
    d.rectangle([100, 180, 290, 220], fill=(185, 185, 185), outline=HW_BORDER, width=1)
    d.text((110, 190), "Charging Handle", font=fnt(11), fill=HW_LABEL)
    hs = SCENARIO["tutorial"][2]["hotspot"]
    annotate_region(img, hs, label="3", hl=hl)
    if not hl:
        annotate_region(img, {"x": 100, "y": 180, "w": 190, "h": 40}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Tilt upper, slide BCG rearward, then remove charging handle." if hl
                           else "Remove the bolt carrier group and charging handle.", ok=True)
    placeholder_note(d)
    return img


def screen_step4_disassemble_bolt(hl=True):
    """BCG exploded view with firing pin, cam pin, bolt."""
    img, d = new_hardware_screen("AR-15 Field Strip — Step 4: Disassemble Bolt")
    _draw_bcg(d)
    hs = SCENARIO["tutorial"][3]["hotspot"]
    annotate_region(img, hs, label="4", hl=hl)
    if not hl:
        # Decoy on gas key and carrier rails
        annotate_region(img, {"x": 380, "y": 210, "w": 100, "h": 35}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 310, "y": 355, "w": 280, "h": 35}, label="?", hl=False, decoy=True)
    if hl:
        draw_callout(img, 365, 300, "Ret.Pin → FP → Cam → Bolt", anchor="left")
    hardware_status_banner(d, "Order: Retaining pin → Firing pin → Cam pin → Bolt" if hl
                           else "Disassemble the bolt carrier group.", ok=True)
    placeholder_note(d)
    return img


def screen_step5_inspect_clean(hl=True):
    """Close-up of bolt face and locking lugs."""
    img, d = new_hardware_screen("AR-15 Field Strip — Step 5: Inspect & Clean")
    # Large bolt face close-up
    cx, cy, r = 640, 360, 180
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=(190, 190, 190), outline=HW_STEEL, width=3)
    d.text((cx - 40, cy - 10), "Bolt Face", font=fnt(14, bold=True), fill=HW_LABEL)
    # Locking lugs (star pattern)
    import math
    for i in range(7):
        angle = i * (2 * math.pi / 7) - math.pi / 2
        lx = cx + int(r * 0.7 * math.cos(angle))
        ly = cy + int(r * 0.7 * math.sin(angle))
        d.rounded_rectangle([lx - 15, ly - 8, lx + 15, ly + 8], radius=3,
                            fill=(175, 175, 175), outline=HW_BORDER, width=1)
    d.text((cx - 60, cy + r + 10), "Locking Lugs (7)", font=fnt(11), fill=HW_LABEL)
    # Extractor
    d.rectangle([cx + r - 30, cy - 20, cx + r + 20, cy + 20],
                fill=(170, 170, 170), outline=HW_STEEL, width=1)
    d.text((cx + r + 25, cy - 8), "Extractor", font=fnt(10), fill=HW_LABEL)
    # Ejector
    d.ellipse([cx - 5, cy + 40, cx + 5, cy + 50],
              fill=HW_ORANGE, outline=HW_STEEL, width=1)
    d.text((cx + 10, cy + 38), "Ejector", font=fnt(10), fill=HW_LABEL)

    hs = SCENARIO["tutorial"][4]["hotspot"]
    annotate_region(img, hs, label="5", hl=hl)
    if not hl:
        annotate_region(img, {"x": cx + r - 30, "y": cy - 20, "w": 50, "h": 40},
                        label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Check for cracks, pitting, carbon. Clean with solvent and brush." if hl
                           else "Inspect the bolt face and locking lugs.", ok=True)
    placeholder_note(d)
    return img


def screen_step6_lubricate(hl=True):
    """BCG with lube points highlighted."""
    img, d = new_hardware_screen("AR-15 Field Strip — Step 6: Lubricate")
    _draw_bcg(d)
    hs = SCENARIO["tutorial"][5]["hotspot"]
    annotate_region(img, hs, label="6", hl=hl)
    if hl:
        # Draw lube point indicators
        lube_points = [(340, 265), (500, 265), (660, 265)]
        for lx, ly in lube_points:
            d.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=HW_GREEN, outline=HW_WHITE, width=1)
        d.text((340, 300), "← lube points (carrier rails + cam slot)", font=fnt(10), fill=HW_GREEN)
    if not hl:
        annotate_region(img, {"x": 380, "y": 210, "w": 100, "h": 35}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Thin film of CLP on carrier rails, cam slot, bolt body. Wipe excess." if hl
                           else "Lubricate the bolt carrier group.", ok=True)
    placeholder_note(d)
    return img


def screen_step7_reassemble(hl=True):
    """BCG assembly view — reverse order."""
    img, d = new_hardware_screen("AR-15 Field Strip — Step 7: Reassemble BCG")
    _draw_bcg(d)
    hs = SCENARIO["tutorial"][6]["hotspot"]
    annotate_region(img, hs, label="7", hl=hl)
    if hl:
        draw_callout(img, 380, 380, "Bolt → Cam → FP → Ret.Pin", anchor="right")
    if not hl:
        annotate_region(img, {"x": 860, "y": 290, "w": 50, "h": 40}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Reverse order: Bolt → Cam pin → Firing pin → Retaining pin." if hl
                           else "Reassemble the bolt carrier group.", ok=True)
    placeholder_note(d)
    return img


def screen_step8_function_check(hl=True):
    """Full rifle reassembled, target on takedown pin area."""
    img, d = new_hardware_screen("AR-15 Field Strip — Step 8: Close & Function Check")
    _draw_rifle_silhouette(d)
    hs = SCENARIO["tutorial"][7]["hotspot"]
    annotate_region(img, hs, label="8", hl=hl)
    if not hl:
        annotate_region(img, {"x": 280, "y": 420, "w": 100, "h": 50}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 200, "y": 200, "w": 120, "h": 50}, label="?", hl=False, decoy=True)
    if hl:
        draw_callout(img, 500, 400, "Push pins home", anchor="right")
    hardware_status_banner(d, "Pivot upper onto lower. Pins home. Function check: trigger, safety, bolt catch." if hl
                           else "Rejoin receivers and perform function check.", ok=True)
    placeholder_note(d)
    return img


# ── Screen generator registry ────────────────────────────────────────────────

SCREEN_GENERATORS = {
    "step1_verify_clear.png":      screen_step1_verify_clear,
    "step2_takedown_pins.png":     screen_step2_takedown_pins,
    "step3_remove_bcg.png":        screen_step3_remove_bcg,
    "step4_disassemble_bolt.png":  screen_step4_disassemble_bolt,
    "step5_inspect_clean.png":     screen_step5_inspect_clean,
    "step6_lubricate.png":         screen_step6_lubricate,
    "step7_reassemble.png":        screen_step7_reassemble,
    "step8_function_check.png":    screen_step8_function_check,
}


def generate_screens(screens_dir):
    """Generate placeholder PNGs into screens_dir/ and screens_neutral/."""
    screens_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = screens_dir.parent / "screens_neutral"
    neutral_dir.mkdir(parents=True, exist_ok=True)

    for fname, fn in SCREEN_GENERATORS.items():
        fn(hl=True).save(str(screens_dir / fname))
        fn(hl=False).save(str(neutral_dir / fname))

    return list(SCREEN_GENERATORS.keys())
