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

# ── Reference diagram ─────────────────────────────────────────────────────────
# Path to the AR-15 parts breakdown diagram (relative to the repo root).
# load_base_image() will resize it to the 1280×720 canvas.
_DIAGRAM_DIR = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "AR-15"
_DIAGRAM_PATH = _DIAGRAM_DIR / "ar15-parts-breakdown-drawing-1024x683.webp"


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
            "hotspot":     {"x": 480, "y": 265, "w": 220, "h": 100},
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
            "hotspot":     {"x": 360, "y": 345, "w": 385, "h": 55},
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
            "hotspot":     {"x": 320, "y": 155, "w": 155, "h": 65},
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
            "hotspot":     {"x": 320, "y": 220, "w": 400, "h": 90},
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
            "hotspot":     {"x": 530, "y": 230, "w": 200, "h": 100},
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
            "hotspot":     {"x": 330, "y": 230, "w": 310, "h": 80},
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
            "hotspot":     {"x": 300, "y": 200, "w": 440, "h": 120},
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
            "hotspot":     {"x": 370, "y": 340, "w": 370, "h": 70},
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
        "learning_objectives": {
            0: [
                "Identify every major component on the AR-15",
                "Understand how the 8-step field strip sequence flows",
                "Learn where each part lives on the diagram",
            ],
            1: [
                "Follow the correct 8-step disassembly/reassembly sequence",
                "Build muscle memory for the procedure with guided prompts",
                "Understand why each step matters for safety",
            ],
            2: [
                "Perform the full procedure from memory",
                "Identify the real-world consequences of each mistake",
                "Complete the sequence with minimal hint usage",
            ],
            3: [
                "Execute the full field strip under time pressure",
                "Demonstrate procedural mastery with zero assists",
                "Beat the par time for your unit's readiness standard",
            ],
        },
    },
    # ── 3D Exploded View ─────────────────────────────────────────────────
    # Component data for the interactive Three.js briefing screen.
    # Each component has a shape type, geometry parameters, colors,
    # assembled/exploded positions, and step association.
    "exploded_view": {
        "components": [
            # ── Buttstock (Step 8) ───────────────────────────────────────
            {"name": "Buttstock", "shape": "extrude", "step": 8, "color": 0x3a3a3a,
             "depth": 1.0, "translate": [0, 0, -0.5],
             "points": [[-1.8,-0.9],[-1.6,-1.0],[0.0,-1.0],[0.3,-0.7],[0.3,-0.3],[0.3,0.3],[0.3,0.7],[0.0,1.0],[-0.4,1.0],[-1.2,0.7],[-1.7,0.5],[-2.0,0.1],[-2.0,-0.3],[-1.9,-0.7]],
             "assembledPos": [-9.5, -0.5, 0], "explodedPos": [-13.5, -0.5, 0]},
            # ── Buffer Tube (Step 8) ─────────────────────────────────────
            {"name": "Buffer Tube", "shape": "cylinder", "step": 8, "color": 0xa8a8a8,
             "radiusTop": 0.45, "radiusBottom": 0.45, "height": 5.5, "segments": 16,
             "rotateZ": 1.5708,
             "assembledPos": [-6, -0.5, 0], "explodedPos": [-9, -0.5, 0]},
            # ── Upper Receiver (Step 3) ──────────────────────────────────
            {"name": "Upper Receiver", "shape": "extrude", "step": 3, "color": 0xa8a8a8,
             "depth": 1.3, "translate": [0, 0, -0.65],
             "points": [[-3.5,-0.6],[3.5,-0.6],[3.5,-0.2],[3.5,0.2],[3.5,0.4],[3.4,0.45],[3.3,0.55],[2.8,0.55],[2.7,0.60],[2.5,0.60],[2.4,0.55],[2.0,0.55],[1.9,0.60],[1.7,0.60],[1.6,0.55],[1.2,0.55],[1.1,0.60],[0.9,0.60],[0.8,0.55],[0.4,0.55],[0.3,0.60],[0.1,0.60],[0.0,0.55],[-0.4,0.55],[-0.5,0.60],[-0.7,0.60],[-0.8,0.55],[-1.2,0.55],[-1.3,0.60],[-1.5,0.60],[-1.6,0.55],[-2.0,0.55],[-2.1,0.60],[-2.3,0.60],[-2.4,0.55],[-2.8,0.55],[-2.9,0.60],[-3.1,0.60],[-3.2,0.55],[-3.5,0.50],[-3.5,0.0]],
             "assembledPos": [0, 0.3, 0], "explodedPos": [0, 2.5, 0]},
            # ── Lower Receiver (Step 2) ──────────────────────────────────
            {"name": "Lower Receiver", "shape": "extrude", "step": 2, "color": 0xa8a8a8,
             "depth": 1.3, "translate": [0, 0, -0.65],
             "points": [[-3.0,0.5],[2.5,0.5],[2.5,0.2],[2.3,-0.1],[2.0,-0.2],[2.0,-2.0],[1.8,-2.3],[1.0,-2.3],[0.8,-2.0],[0.8,-1.0],[0.7,-1.3],[0.5,-1.5],[0.2,-1.6],[-0.1,-1.5],[-0.3,-1.3],[-0.4,-1.0],[-0.4,-0.5],[-0.6,-0.3],[-0.8,-0.2],[-1.5,-0.2],[-2.0,-0.1],[-2.8,0.0],[-3.0,0.1]],
             "assembledPos": [-0.5, -0.5, 0], "explodedPos": [-0.5, -0.5, -3.0]},
            # ── Pistol Grip (Step 8) ─────────────────────────────────────
            {"name": "Pistol Grip", "shape": "extrude", "step": 8, "color": 0x3a3a3a,
             "depth": 1.0, "translate": [0, 0, -0.5],
             "points": [[-0.1,0.3],[0.4,0.3],[0.5,0.1],[0.55,-0.3],[0.5,-0.8],[0.45,-1.2],[0.4,-1.6],[0.35,-1.9],[0.2,-2.1],[0.0,-2.2],[-0.2,-2.1],[-0.35,-1.9],[-0.4,-1.5],[-0.4,-1.0],[-0.35,-0.5],[-0.2,-0.1],[-0.1,0.1]],
             "assembledPos": [-1.0, -1.5, 0], "explodedPos": [-1.0, -1.5, -3.0]},
            # ── Trigger (Step 8) ─────────────────────────────────────────
            {"name": "Trigger", "shape": "extrude", "step": 8, "color": 0x505050,
             "depth": 0.25, "translate": [0, 0, -0.125],
             "points": [[-0.06,0.0],[0.06,0.0],[0.08,-0.2],[0.10,-0.5],[0.06,-0.6],[-0.06,-0.6],[-0.10,-0.5],[-0.08,-0.2]],
             "assembledPos": [0.2, -1.1, 0], "explodedPos": [0.2, -1.1, -3.0]},
            # ── Magazine (Step 1) ────────────────────────────────────────
            {"name": "Magazine", "shape": "extrude", "step": 1, "color": 0x505050,
             "depth": 0.8, "translate": [0, 0, -0.4],
             "points": [[-0.45,0.0],[0.45,0.0],[0.42,-0.8],[0.38,-1.8],[0.33,-2.8],[0.25,-3.2],[0.10,-3.4],[-0.10,-3.4],[-0.25,-3.2],[-0.33,-2.8],[-0.38,-1.8],[-0.42,-0.8]],
             "assembledPos": [1.2, -1.5, 0], "explodedPos": [1.2, -1.5, -4.0]},
            # ── Handguard (Step 5) ───────────────────────────────────────
            {"name": "Handguard", "shape": "extrude", "step": 5, "color": 0x505050,
             "depth": 1.2, "translate": [0, 0, -0.6],
             "points": [[0.0,-0.7],[10.0,-0.65],[10.0,-0.55],[10.2,-0.45],[10.2,0.45],[10.0,0.55],[10.0,0.65],[9.5,0.65],[9.5,0.72],[9.0,0.72],[9.0,0.65],[8.2,0.65],[8.2,0.72],[7.7,0.72],[7.7,0.65],[6.9,0.65],[6.9,0.72],[6.4,0.72],[6.4,0.65],[5.6,0.65],[5.6,0.72],[5.1,0.72],[5.1,0.65],[4.3,0.65],[4.3,0.72],[3.8,0.72],[3.8,0.65],[3.0,0.65],[3.0,0.72],[2.5,0.72],[2.5,0.65],[1.5,0.65],[1.5,0.72],[1.0,0.72],[1.0,0.65],[0.0,0.7]],
             "holes": [[[0.3,-0.4],[9.7,-0.4],[9.7,0.4],[0.3,0.4]]],
             "assembledPos": [3.0, 0.3, 0], "explodedPos": [6.0, 0.3, 2.5]},
            # ── Barrel (Step 5) ──────────────────────────────────────────
            {"name": "Barrel", "shape": "extrude", "step": 5, "color": 0x8a8a8a,
             "depth": 0.5, "translate": [0, 0, -0.25],
             "points": [[0.0,-0.3],[4.0,-0.3],[4.5,-0.28],[10.0,-0.22],[13.0,-0.20],[13.0,0.20],[10.0,0.22],[4.5,0.28],[4.0,0.3],[0.0,0.3]],
             "assembledPos": [3.5, 0.3, 0], "explodedPos": [9.0, 0.3, 0]},
            # ── Muzzle Brake (Step 5) ────────────────────────────────────
            {"name": "Muzzle Brake", "shape": "extrude", "step": 5, "color": 0x606060,
             "depth": 0.5, "translate": [0, 0, -0.25],
             "points": [[0.0,-0.22],[0.1,-0.35],[0.3,-0.35],[0.4,-0.30],[0.5,-0.35],[0.6,-0.30],[0.7,-0.35],[0.8,-0.30],[0.9,-0.35],[1.0,-0.30],[1.1,-0.25],[1.2,-0.10],[1.2,0.10],[1.1,0.25],[1.0,0.30],[0.9,0.35],[0.8,0.30],[0.7,0.35],[0.6,0.30],[0.5,0.35],[0.4,0.30],[0.3,0.35],[0.1,0.35],[0.0,0.22]],
             "assembledPos": [16.5, 0.3, 0], "explodedPos": [22, 0.3, 0]},
            # ── Gas Tube (Step 5) ────────────────────────────────────────
            {"name": "Gas Tube", "shape": "cylinder", "step": 5, "color": 0x8a8a8a,
             "radiusTop": 0.06, "radiusBottom": 0.06, "height": 8, "segments": 8,
             "rotateZ": 1.5708,
             "assembledPos": [6, 0.9, 0], "explodedPos": [12, 1.8, 0]},
            # ── Front Sight (Step 5) ─────────────────────────────────────
            {"name": "Front Sight", "shape": "extrude", "step": 5, "color": 0x505050,
             "depth": 0.15, "translate": [0, 0, -0.075],
             "points": [[-0.25,0.0],[0.25,0.0],[0.20,0.2],[0.12,0.6],[0.08,0.8],[0.04,0.95],[0.02,1.1],[-0.02,1.1],[-0.04,0.95],[-0.08,0.8],[-0.12,0.6],[-0.20,0.2]],
             "assembledPos": [13.5, 0.9, 0], "explodedPos": [19, 2.0, 0]},
            # ── Bolt Carrier Group (Step 4) ──────────────────────────────
            {"name": "Bolt Carrier Group", "shape": "extrude", "step": 4, "color": 0x8a8a8a,
             "depth": 0.6, "translate": [0, 0, -0.3],
             "points": [[-2.8,-0.30],[2.2,-0.30],[2.4,-0.28],[2.6,-0.20],[2.7,-0.10],[2.7,0.10],[2.6,0.20],[2.4,0.28],[2.2,0.30],[0.8,0.30],[0.7,0.45],[0.5,0.48],[-0.5,0.48],[-0.7,0.45],[-0.8,0.30],[-2.8,0.30],[-2.8,0.15],[-2.9,0.05],[-2.9,-0.05],[-2.8,-0.15]],
             "assembledPos": [0, 0.3, 0], "explodedPos": [0, 5.0, 0]},
            # ── Cam Pin (Step 4) ─────────────────────────────────────────
            {"name": "Cam Pin", "shape": "cylinder", "step": 4, "color": 0x8a8a8a,
             "radiusTop": 0.08, "radiusBottom": 0.08, "height": 0.6, "segments": 6,
             "assembledPos": [1.5, 0.3, 0], "explodedPos": [3.0, 7.5, 1.0]},
            # ── Firing Pin (Step 4) ──────────────────────────────────────
            {"name": "Firing Pin", "shape": "cylinder", "step": 4, "color": 0x8a8a8a,
             "radiusTop": 0.04, "radiusBottom": 0.04, "height": 4.5, "segments": 6,
             "rotateZ": 1.5708,
             "assembledPos": [0, 0.3, 0], "explodedPos": [0, 8.0, 0]},
            # ── Retaining Pin (Step 4) ───────────────────────────────────
            {"name": "Retaining Pin", "shape": "cylinder", "step": 4, "color": 0xd4a840,
             "radiusTop": 0.03, "radiusBottom": 0.03, "height": 0.5, "segments": 6,
             "rotateX": 1.5708,
             "assembledPos": [-2.2, 0.3, 0], "explodedPos": [-2.2, 8.5, 1.5]},
            # ── Charging Handle (Step 3) ─────────────────────────────────
            {"name": "Charging Handle", "shape": "extrude", "step": 3, "color": 0xa8a8a8,
             "depth": 0.6, "translate": [0, 0, -0.3],
             "points": [[-1.5,-0.08],[1.5,-0.08],[1.5,0.08],[-1.0,0.08],[-1.0,0.18],[-1.2,0.22],[-1.6,0.22],[-1.8,0.18],[-1.8,-0.18],[-1.6,-0.22],[-1.2,-0.22],[-1.0,-0.18],[-1.0,-0.08],[-1.5,-0.08]],
             "assembledPos": [-2, 0.85, 0], "explodedPos": [-2, 4.0, -2.5]},
            # ── Takedown Pins (Step 2) ───────────────────────────────────
            {"name": "Rear Takedown Pin", "shape": "cylinder", "step": 2, "color": 0x8a8a8a,
             "radiusTop": 0.09, "radiusBottom": 0.09, "height": 1.4, "segments": 8,
             "rotateX": 1.5708,
             "assembledPos": [-2.5, 0.0, 0], "explodedPos": [-2.5, 0.0, -4.5]},
            {"name": "Front Pivot Pin", "shape": "cylinder", "step": 2, "color": 0x8a8a8a,
             "radiusTop": 0.09, "radiusBottom": 0.09, "height": 1.4, "segments": 8,
             "rotateX": 1.5708,
             "assembledPos": [2.0, 0.0, 0], "explodedPos": [2.0, 0.0, -4.5]},
            # ── Safety Selector (Step 8) ─────────────────────────────────
            {"name": "Safety Selector", "shape": "cylinder", "step": 8, "color": 0x505050,
             "radiusTop": 0.2, "radiusBottom": 0.2, "height": 0.1, "segments": 8,
             "rotateX": 1.5708,
             "assembledPos": [-1.5, -0.2, 0.66], "explodedPos": [-1.5, -0.2, -2.3]},
            # ── Shell Deflector (Step 1) ─────────────────────────────────
            {"name": "Shell Deflector", "shape": "sphere", "step": 1, "color": 0xa8a8a8,
             "radius": 0.3, "arc": 3.14159,
             "assembledPos": [0.5, 0.5, 0.65], "explodedPos": [0.5, 2.8, 1.8]},
            # ── Bolt Catch (Step 1) ──────────────────────────────────────
            {"name": "Bolt Catch", "shape": "extrude", "step": 1, "color": 0x505050,
             "depth": 0.08,
             "points": [[0,0],[0.15,0],[0.15,0.5],[0.1,0.6],[0.05,0.6],[0,0.5]],
             "assembledPos": [1.0, -0.2, -0.66], "explodedPos": [1.0, -0.2, -3.7]},
        ],
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# SCREEN GENERATORS — real AR-15 parts breakdown diagram
# ═════════════════════════════════════════════════════════════════════════════

def _diagram_screen(title):
    """Load the real AR-15 diagram as a base, overlay the steel shell bar.

    Returns (img, draw) — same contract as new_hardware_screen().
    """
    img = load_base_image(str(_DIAGRAM_PATH))
    d = ImageDraw.Draw(img)
    # Steel-grey shell bar with title
    d.rectangle([0, 0, W, 48], fill=HW_STEEL)
    d.text((20, 14), title, font=fnt(16, bold=True), fill=HW_WHITE)
    return img, d


def screen_step1_verify_clear(hl=True):
    """Full rifle — ejection port / magazine release as target."""
    img, d = _diagram_screen("AR-15 Field Strip — Step 1: Verify Clear")
    hs = SCENARIO["tutorial"][0]["hotspot"]
    annotate_region(img, hs, label="1", hl=hl)
    if hl:
        draw_callout(img, 650, 280, "Ejection Port", anchor="right")
        draw_callout(img, 500, 310, "Magazine Release", anchor="left")
    if not hl:
        # Decoys: forward assist and trigger area
        annotate_region(img, {"x": 420, "y": 100, "w": 100, "h": 60}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 510, "y": 400, "w": 100, "h": 60}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "SAFETY FIRST: Remove magazine. Lock bolt open. Inspect chamber." if hl
                           else "Verify the weapon is clear before proceeding.", ok=True)
    return img


def screen_step2_takedown_pins(hl=True):
    """Full rifle — takedown pins between upper and lower receivers."""
    img, d = _diagram_screen("AR-15 Field Strip — Step 2: Takedown Pins")
    hs = SCENARIO["tutorial"][1]["hotspot"]
    annotate_region(img, hs, label="2", hl=hl)
    if hl:
        draw_callout(img, 390, 370, "Rear Takedown Pin", anchor="left")
        draw_callout(img, 710, 375, "Front Pivot Pin", anchor="right")
    if not hl:
        annotate_region(img, {"x": 510, "y": 420, "w": 100, "h": 60}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 180, "y": 300, "w": 100, "h": 60}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Push pins left-to-right. Rear first, then front." if hl
                           else "Separate the upper and lower receivers.", ok=True)
    return img


def screen_step3_remove_bcg(hl=True):
    """Full rifle — charging handle and upper receiver as target for BCG removal."""
    img, d = _diagram_screen("AR-15 Field Strip — Step 3: Remove BCG")
    hs = SCENARIO["tutorial"][2]["hotspot"]
    annotate_region(img, hs, label="3", hl=hl)
    if hl:
        draw_callout(img, 370, 170, "Charging Handle", anchor="right")
        draw_callout(img, 430, 200, "BCG exits here", anchor="right")
    if not hl:
        annotate_region(img, {"x": 430, "y": 100, "w": 100, "h": 50}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 750, "y": 250, "w": 120, "h": 60}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Tilt upper, slide BCG rearward, then remove charging handle." if hl
                           else "Remove the bolt carrier group and charging handle.", ok=True)
    return img


def screen_step4_disassemble_bolt(hl=True):
    """Full rifle — upper receiver area where BCG components are."""
    img, d = _diagram_screen("AR-15 Field Strip — Step 4: Disassemble Bolt")
    hs = SCENARIO["tutorial"][3]["hotspot"]
    annotate_region(img, hs, label="4", hl=hl)
    if hl:
        draw_callout(img, 500, 250, "Ret.Pin → FP → Cam → Bolt", anchor="right")
    if not hl:
        annotate_region(img, {"x": 750, "y": 260, "w": 140, "h": 60}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 400, "y": 400, "w": 120, "h": 50}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Order: Retaining pin → Firing pin → Cam pin → Bolt" if hl
                           else "Disassemble the bolt carrier group.", ok=True)
    return img


def screen_step5_inspect_clean(hl=True):
    """Full rifle — front upper area where bolt face and barrel extension meet."""
    img, d = _diagram_screen("AR-15 Field Strip — Step 5: Inspect & Clean")
    hs = SCENARIO["tutorial"][4]["hotspot"]
    annotate_region(img, hs, label="5", hl=hl)
    if hl:
        draw_callout(img, 680, 260, "Bolt Face & Lugs", anchor="right")
        draw_callout(img, 560, 310, "Check for cracks / pitting", anchor="left")
    if not hl:
        annotate_region(img, {"x": 330, "y": 155, "w": 120, "h": 50}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 800, "y": 260, "w": 120, "h": 60}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Check for cracks, pitting, carbon. Clean with solvent and brush." if hl
                           else "Inspect the bolt face and locking lugs.", ok=True)
    return img


def screen_step6_lubricate(hl=True):
    """Full rifle — BCG area with lube point callouts."""
    img, d = _diagram_screen("AR-15 Field Strip — Step 6: Lubricate")
    hs = SCENARIO["tutorial"][5]["hotspot"]
    annotate_region(img, hs, label="6", hl=hl)
    if hl:
        # Draw lube point indicators on the upper receiver area
        lube_pts = [(370, 260), (460, 260), (580, 260)]
        for lx, ly in lube_pts:
            d.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=HW_GREEN, outline=HW_WHITE, width=1)
        draw_callout(img, 470, 290, "CLP on rails + cam slot", anchor="right")
    if not hl:
        annotate_region(img, {"x": 700, "y": 230, "w": 140, "h": 60}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 420, "y": 400, "w": 100, "h": 50}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Thin film of CLP on carrier rails, cam slot, bolt body. Wipe excess." if hl
                           else "Lubricate the bolt carrier group.", ok=True)
    return img


def screen_step7_reassemble(hl=True):
    """Full rifle — upper receiver area for BCG reassembly."""
    img, d = _diagram_screen("AR-15 Field Strip — Step 7: Reassemble BCG")
    hs = SCENARIO["tutorial"][6]["hotspot"]
    annotate_region(img, hs, label="7", hl=hl)
    if hl:
        draw_callout(img, 500, 250, "Bolt → Cam → FP → Ret.Pin", anchor="right")
    if not hl:
        annotate_region(img, {"x": 750, "y": 240, "w": 140, "h": 60}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 130, "y": 300, "w": 100, "h": 50}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Reverse order: Bolt → Cam pin → Firing pin → Retaining pin." if hl
                           else "Reassemble the bolt carrier group.", ok=True)
    return img


def screen_step8_function_check(hl=True):
    """Full rifle — rejoin receivers at takedown pins, function check."""
    img, d = _diagram_screen("AR-15 Field Strip — Step 8: Close & Function Check")
    hs = SCENARIO["tutorial"][7]["hotspot"]
    annotate_region(img, hs, label="8", hl=hl)
    if hl:
        draw_callout(img, 400, 360, "Push pins home", anchor="left")
        draw_callout(img, 700, 365, "Function check", anchor="right")
    if not hl:
        annotate_region(img, {"x": 510, "y": 420, "w": 100, "h": 60}, label="?", hl=False, decoy=True)
        annotate_region(img, {"x": 180, "y": 170, "w": 100, "h": 50}, label="?", hl=False, decoy=True)
    hardware_status_banner(d, "Pivot upper onto lower. Pins home. Function check: trigger, safety, bolt catch." if hl
                           else "Rejoin receivers and perform function check.", ok=True)
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
    """Generate annotated diagram PNGs into screens_dir/ and screens_neutral/."""
    screens_dir.mkdir(parents=True, exist_ok=True)
    neutral_dir = screens_dir.parent / "screens_neutral"
    neutral_dir.mkdir(parents=True, exist_ok=True)

    for fname, fn in SCREEN_GENERATORS.items():
        fn(hl=True).save(str(screens_dir / fname))
        fn(hl=False).save(str(neutral_dir / fname))

    return list(SCREEN_GENERATORS.keys())
