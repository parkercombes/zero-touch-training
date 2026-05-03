# DJI Mavic 3 Pro — Source Library

Reference assets for the `drone_anatomy` scenario (and any future Mavic 3 Pro scenarios).

## Tracked in this repo

- `build-report.md` — what was built using these assets, with mid-build trust calibration notes
- `inventory.md` — catalog of source photos (read the warning header before relying on it)
- `mavic3pro_camera_array_side.png` — Hasselblad camera array, side angle
- `mavic3pro_front_view_propsout.png` — front view with propellers extended
- `mavic3pro_top_down.png` — top-down view, propellers extended
- `mavic3pro_front_low_angle.png` — front-low angle, top vision sensors visible
- `mavic3pro_underbelly.png` — underbelly view, bottom vision sensors visible

These five photos are the ones referenced by `poc/generators/scenarios/drone_anatomy.py`.

## Not tracked (intentionally)

- `DJI_Mavic_3_Pro_User_Manual_EN.pdf` (30 MB) — download from https://www.dji.com/mavic-3-pro/downloads. Save to this folder. Used for narrative/consequence text in the scenario module, not loaded at runtime.
- 36 other screenshots from the DJI product page — kept locally for reference but not used by any scenario. The `inventory.md` catalog describes all 41 originals; the 36 unused ones can be re-sourced from https://www.dji.com/mavic-3-pro by scrolling the product page.

## Source

All photographs and the user manual are publicly available DJI marketing/documentation collateral. Asset source tier in the index: `oem_marketing`.

