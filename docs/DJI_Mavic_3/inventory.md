> ⚠ **KNOWN ERRORS — see build-report.md before relying on this catalog.**
>
> The screenshot classifications in this inventory contain at least one confirmed
> error (10:40:14 vs 10:40:38 mis-classification, caught during scenario build).
> A second-pass verification against the actual photos has not been completed.
> If you use this inventory to source assets for a new scenario, open each
> photo and confirm the classification before relying on it.
>
> Filenames in this inventory still reference the original macOS `Screenshot 2026-05-02 at HH.MM.SS AM.png`
> form. Five of the photos have since been renamed (mavic3pro_camera_array_side.png,
> mavic3pro_front_view_propsout.png, mavic3pro_top_down.png, mavic3pro_front_low_angle.png,
> mavic3pro_underbelly.png) — these correspond to 10:33:50, 10:40:46, 10:40:38,
> 10:41:09, and 10:41:03 respectively.

# DJI Mavic 3 Pro — Source Material Inventory

**Date catalogued:** 2026-05-02
**Folder:** `docs/DJI_Mavic_3/`
**Catalogued by:** Claude (Cowork)

---

## TL;DR — Read this first

You collected DJI's **marketing/product page** material, not training-usable material.

- **Manual (PDF):** real, usable. 126 pages, embedded text layer, full TOC including Pre-Flight Checklist, Preparing the Aircraft, Activating, Binding, Updating Firmware, Flight Modes, RTH, etc. Good source for narratives, consequences, and procedural steps.
- **Screenshots (37 PNGs):** all from the DJI Mavic 3 Pro product page (`dji.com/mavic-3-pro`). They are marketing collateral — feature-highlight photography, accessory thumbnails, and 360° product-viewer poses. **Zero app UI screens. Zero procedural step diagrams. Zero in-context capture of a real workflow.**

**What this means for the hardware pilot scenario:** the screenshots cover **about 1/3 of what you need**. The clean drone-exterior poses are actually decent for hardware-annotation hotspots (props, gimbal, vision sensors, battery latch). But you have **nothing** for the software side (DJI Fly app activation, calibration, takeoff, settings) and **nothing** for procedural how-to capture (e.g., "remove gimbal protector," "unfold front arms before rear arms"). The manual has the *text* of those steps but no diagrams in usable form.

If your goal was "infer the captured task from the screenshot sequence" — the answer is **there is no captured task**. The 7-minute capture window (10:33 → 10:41) is consistent with someone scrolling and screenshotting the marketing page top-to-bottom, not capturing a workflow.

See [§4 Recommendation](#4-recommendation) for what to do next.

---

## 1. Manual

| Field | Value |
|---|---|
| File | `DJI_Mavic_3_Pro_User_Manual_EN.pdf` |
| Size | 30 MB |
| Pages | 126 |
| Source | DJI (Adobe InDesign 15.0, PDF Library 15.0) |
| Version | v1.4 (2024.08) |
| Encryption | AES, `print:yes copy:no change:no` (text extraction works via pdftotext anyway) |
| Text layer | Yes — extracted to `outputs/manual.txt` (5,464 lines) |

### Manual sections most relevant to a pilot scenario

| Section | Page | Why it matters |
|---|---|---|
| Preparing the Aircraft | 10 | First-flight steps: remove storage cover, charge & install battery, unfold arms (front before rear), remove gimbal protector |
| Preparing the Remote Controller | 11 | Charge, install/screw control sticks, unfold antennas, power on, activate |
| Activating the DJI Mavic 3 Pro Aircraft | 12 | Requires DJI Fly app + internet |
| Binding the Aircraft and Remote Controller | 12 | Post-activation step |
| Updating Firmware | 12 | Trigger via DJI Fly prompt |
| Pre-Flight Checklist | 23 | Prime source for "consequence" narratives |
| Auto Takeoff/Landing | 24 | Core flight procedure |
| Starting/Stopping the Motors | 24 | CSC stick combo — the "wrong way to do it" failure mode |
| Smart RTH / Low Battery RTH / Failsafe RTH | 46-49 | High-stakes scenarios for explore_info / consequences |
| Inserting/Removing the Battery | 64 | Hardware procedure |
| Attaching/Detaching the Propellers | 58 | Hardware procedure — high consequence (wrong rotation = crash) |
| DJI Fly App → Camera View → Buttons Description | 92 | The closest the manual gets to UI screenshots, but still text-only |

### Sections to skim or skip for v1
Specifications (104), Camera Function Matrix (112), Enhanced Transmission / Cellular Dongle (114), C2 Certification (120), FAR Remote ID (125), After-Sales (125).

---

## 2. Screenshots — full classification

All 37 screenshots are from a single browsing session of `dji.com/mavic-3-pro` (the official product page) between 10:33:35 AM and 10:41:09 AM on 2026-05-02. Evidence:

- Orange `#orange` accent matches DJI brand
- "Click and drag the image to view" hint visible in two screenshots → 360° product viewer
- Bottom-of-image tab labels ("Multi-Directional Awareness | Enhanced Zoom Precision | …" and "Waypoint Flight | Cruise Control | Advanced RTH") match the product page's tabbed sections
- Aspect ratios and styling are consistent with the marketing site, not the manual or the DJI Fly app

### Group A — Camera & feature highlights (9 files)
Marketing photography with overlay copy. Useful as reference, not as procedural source.

| File | Subject | Overlay text |
|---|---|---|
| 10:33:35 | 3-camera Hasselblad array, centered | "HASSELBLAD" |
| 10:33:50 | Camera array, side-on | "4/3 CMOS Hasselblad Camera — 24mm eq., f/2.8-f/11, 20 MP" |
| 10:34:03 | Camera array, side-on | "1/1.3" CMOS Medium Tele Camera — 70mm eq., 3x Optical Zoom, f/2.8, 48 MP" |
| 10:34:13 | Camera array, side-on | "1/2" CMOS Tele Camera — 166mm eq., 7x Optical Zoom, 28x Hybrid, f/3.4, 12 MP" |
| 10:34:31 | Camera array, rotated close-up | "4/3 CMOS Hasselblad Camera" (variant of 10:33:50) |
| 10:35:05 | Side profile of Mavic 3 Pro Cine | "Apple ProRes / 1TB SSD" |
| 10:35:17 | Camera array, alt close-up | "1/1.3" CMOS Medium Tele" (variant of 10:34:03) |
| 10:35:40 | Aircraft with battery cutaway highlighted | "Extended Flight Time / 43 mins" |
| 10:37:08 | Hand holding RC Pro | "Flagship Video Transmission / 1080p 60fps / 15km" |

### Group B — Person-with-device lifestyle shots (9 files)
Hands holding remote controllers showing camera view, or people standing with drone. The screen content visible is decorative aerial footage — **not real DJI Fly UI states**.

| File | Subject | Tab/context |
|---|---|---|
| 10:35:49 | RC Pro showing daytime aerial of buildings | "Multi-Directional Awareness" tab |
| 10:35:58 | RC Pro showing aerial of buildings (closer) | "Enhanced Zoom Precision" tab |
| 10:36:10 | RC Pro showing night cityscape | "Nocturnal Assistance" tab |
| 10:36:55 | RC Pro showing zoomed aerial | "Enhanced Zoom Precision" tab |
| 10:37:13 | Dark aerial w/ RTH path overlay | "Advanced RTH" tab |
| 10:37:29 | Hand on RC button, blurred | "Cruise Control" tab |
| 10:37:49 | Macro close-up of RC button press | "Cruise Control" tab |
| 10:38:05 | Person holding RC outdoors | "FocusTrack / MasterShots / QuickShots / …" tab strip |
| 10:38:46 | People standing, drone airborne, goggles user | (DJI Goggles section) |

### Group C — Accessory product thumbnails (8 files)
Vertical thumbnail tiles from the "Accessories" section of the product page.

| File | Item |
|---|---|
| 10:38:57 | DJI RC Pro (full feature card with description) |
| 10:38:58 | DJI RC Pro (compact thumbnail) |
| 10:39:03 | DJI Mavic 3 Pro Wide-Angle Lens |
| 10:39:11 | DJI Mavic 3 Series 100W Battery Charging Hub |
| 10:39:15 | DJI Goggles Integra Motion Combo |
| 10:39:22 | DJI 65W Car Charger |
| 10:39:27 | DJI Mavic 3 Series Intelligent Flight Battery |
| 10:39:32 | DJI Mavic 3 Pro ND Filters Set |

### Group D — 360° product viewer poses (11 files)
Clean isolated drone shots, multiple angles, both folded and unfolded. **These are the only files with hotspot-annotation potential** — they're high-res, well-lit, on solid black background, and show external components clearly.

| File | Pose | Annotation potential |
|---|---|---|
| 10:39:48 | Unfolded — three-quarter view, props extended | Best for: gimbal, props, body, arms |
| 10:39:56 | Folded — three-quarter view | Best for: storage state contrast |
| 10:40:08 | Unfolded — front view (props folded down) | Front vision sensors visible |
| 10:40:14 | Top-down, props extended | Body shape, prop layout |
| 10:40:18 | Front close-up, folded | Camera array detail |
| 10:40:27 | Front close-up, alt angle | Vision sensor positions |
| 10:40:38 | Rear three-quarter, folded | Rear sensors, body |
| 10:40:46 | Front view "MAVIC 3 PRO CINE" badge, props extended | Wing badge, gimbal |
| 10:40:54 | Side perspective, props extended | Profile, battery latch area |
| 10:41:03 | Rear/underbelly perspective, props extended | **Belly: front vision sensors, gimbal mount, landing gear** |
| 10:41:09 | Front-low angle, props extended | Camera array, top vision sensors |

---

## 3. Coverage gap analysis

What a hardware pilot scenario for "DJI Mavic 3 Pro pre-flight setup & first launch" actually needs, mapped to what you have:

| Required asset | Have it? | What's available |
|---|---|---|
| Photo of drone in storage state (folded, gimbal cover on) | Partial | Group D 10:39:56 / 10:40:18 — folded but **gimbal cover not visible**; would need to fake or label |
| Photo: removing storage cover | ❌ | None |
| Photo: battery in charger | ❌ | Group C has accessory thumbnails of charger and battery, but not in-use |
| Photo: battery insertion into drone | ❌ | None |
| Photo: unfolding arms (front before rear) | ❌ | None — only end-state poses |
| Photo: gimbal protector removal | ❌ | None |
| Photo: prop installation (CW vs CCW orientation) | ❌ | None |
| Photo: remote controller w/ sticks unscrewed (stored) | Partial | Group C 10:38:58 (thumbnail, low res) |
| Photo: remote controller w/ sticks installed | ✓ | Group B has many |
| Screenshot: DJI Fly app — activation flow | ❌ | None |
| Screenshot: DJI Fly app — firmware update | ❌ | None |
| Screenshot: DJI Fly app — compass calibration | ❌ | None |
| Screenshot: DJI Fly app — camera view (real UI) | ❌ | None — only marketing renders w/ HUD |
| Screenshot: DJI Fly app — RTH settings | ❌ | None |
| Screenshot: DJI Fly app — pre-flight checklist warnings | ❌ | None |

**Net:** ~15% of what's needed. The drone-exterior poses (Group D) are usable for a "name the parts" exploration screen, and that's about it.

---

## 4. Recommendation

Three honest options, ordered by my preference:

### Option 1 — Pivot the scenario to what the assets actually support: "Drone Anatomy & Pre-Flight Visual Inspection"
A short, **one-screen-deep** scenario that uses the Group D poses to teach component identification: locate the gimbal, the front vision sensors, the rear vision sensors, the props, the battery latch, the antennas. Maps cleanly to the existing engine contract (image + hotspot rect + label) and would prove the photo-annotation pipeline (Phase 2 of `PLAN_hardware_extension.md`) end-to-end with **real photos** instead of placeholder PIL boxes. Doesn't require any procedural shots you don't have.

**Cost:** lowest. Could be a working trainer in a single session. Would actually validate the hardware extension.

### Option 2 — Build the procedural scenario, generate the missing assets
Use the manual text to script the steps, then either (a) shoot the missing photos yourself if you own a Mavic 3 Pro, or (b) use placeholder PIL diagrams (per Phase 3 of the plan) until photos exist. The DJI Fly UI screens you'd need to either screenshot from your own phone or stub with mock UI.

**Cost:** medium-high. You're back to needing real source material before this becomes useful.

### Option 3 — Drop the drone, use AR-15 / oil-change as originally planned
Pick one of the originals from `PLAN_hardware_extension.md`. They're more constrained domains where you can shoot reference photos with hardware you actually have.

**Cost:** wastes the manual extraction work, but keeps you on the documented plan.

**My pick: Option 1.** It's the only path that uses what you collected and proves something architecturally meaningful (real photos through the photo-annotation hotspot pipeline). If it works, Option 2 becomes a natural follow-up.

---

## 5. Files in this folder

| File | Size | Purpose |
|---|---|---|
| `DJI_Mavic_3_Pro_User_Manual_EN.pdf` | 30 MB | Source manual |
| `Screenshot 2026-05-02 at 10.33.35 AM.png` … `10.41.09 AM.png` | 16 KB – 880 KB | 37 marketing-page captures (see §2) |
| `inventory.md` | this file | This catalog |
