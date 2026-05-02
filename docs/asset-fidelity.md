# Asset Fidelity Tiers

## What this is

Zero-Touch Training compiles training from real organizational assets — that's the premise. But the PoC scenarios in this repository sit at different fidelity tiers depending on what assets were available when each scenario was built. This document is the honest accounting of which scenarios use what.

The point is **truth in advertising**. When demoing, the index shows each scenario's fidelity tier so audiences see exactly what kind of asset is feeding the training. "This is a drawing" or "this is a manual scan" or "this is a captured screen" — labeled, not hidden.

This is not a credibility hierarchy where higher = better. Different tiers are appropriate for different purposes. A Pillow placeholder during Phase 1 was the right call. A Pillow placeholder in a buyer pitch is not.

## Tiers

In rough order of asset realism:

| Tier | Source | When appropriate | When inappropriate |
|---|---|---|---|
| 🔴 **Placeholder** | Pillow-drawn schematics | Phase 1 engine and pedagogy validation, before real assets are sourced | Buyer pitches, public demos, anything that circulates outside the team |
| 🟡 **Textbook scan** | Photographs from Chilton, Haynes, technical manuals, training publications | Demo where source attribution is acceptable; convincing for hardware procedures | When OEM IP rights are unclear; when scan quality is below readability threshold |
| 🟢 **OEM marketing** | Publicly available OEM product photography, app store screenshots, datasheet diagrams | Strong default for commercial products with public marketing assets | When marketing angles don't show what an operator actually sees in the field |
| 🟢 **Captured** | Live screen captures via Playwright, screen recording, native screenshots from running systems | The right tier for any software the team has access to (ERPNext, Fiori sandbox, the customer's app on a test device) | When the system isn't accessible or when version drift between capture and current state is a concern |
| 🟢 **Photographed** | Custom photography of the actual hardware in operator-perspective angles | The highest fidelity for hardware; matches exactly what a trainee sees in the field | When budget or hardware access doesn't permit; takes meaningful effort |

The 🟡 and 🟢 tiers are all "real assets" for the purposes of the buyer pitch. The 🔴 tier is the one to phase out.

## Current scenario status

As of May 2026:

| Scenario | Domain | Tier | Notes |
|---|---|---|---|
| `sedc_goods_receipt` | Software (SAP) | 🔴 Placeholder | Pillow-drawn Fiori screens. Migration target: ERPNext capture. |
| `standard_dry_gr` | Software (SAP) | 🟢 Captured | ERPNext Playwright capture pipeline. Reference implementation. |
| `regulated_pharma` | Software (SAP) | 🔴 Placeholder | Same migration path as sedc. |
| `hazmat_gr` | Software (SAP) | 🔴 Placeholder | Same migration path as sedc. |
| `serialized_gr` | Software (SAP) | 🔴 Placeholder | Same migration path as sedc. |
| `ar15_field_strip` | Hardware | 🔴 Placeholder | Migration target: publicly available FN/Colt manual photos or military training materials. |
| `f150_trans_service` | Hardware | 🟡 Textbook scan | Chilton manual scans. Functional but lower resolution. |
| `drone_preflight` | Fusion | 🔴 Placeholder | Migration target: DJI Mini 4 Pro marketing photos + DJI Fly app store screenshots. In progress May 2026. |

Of eight scenarios, **one is real-asset, one is textbook scan, six are placeholder**. The phase-out work is the bulk of remaining Phase 2 visual fidelity effort.

## Migration plan

In rough ROI order — easiest with most demo impact first:

1. **Drone (HW/SW fusion)** — DJI marketing photos and DJI Fly app store screenshots. Both publicly available, no rights friction. Direct payoff for the fusion demo. *In progress.*
2. **AR-15 field strip** — Publicly available FN/Colt disassembly photos exist in many places (manufacturer manuals, military TM excerpts, training materials). Source them, drop them in `docs/AR15/`, update the scenario to load real images. ~one session of work.
3. **Five SAP scenarios via ERPNext** — `standard_dry_gr` already uses Playwright capture. Apply the same pipeline to the other four (`sedc_goods_receipt`, `regulated_pharma`, `hazmat_gr`, `serialized_gr`). ~30 min capture session per scenario, plus scenario-module rewiring to load captured PNGs instead of calling Pillow renderers. ~half a session per scenario, two sessions total.
4. **F-150 fidelity upgrade (optional)** — already textbook tier, which is acceptable. Custom photography of an actual F-150 transmission service would be the upgrade. Low priority unless a specific demo requires it.

Total effort estimate: 4-5 focused sessions to migrate everything off Pillow.

## Adding `asset_source` to the index

Each scenario will declare its current tier as a top-level SCENARIO field:

```python
SCENARIO = {
    "id": "drone_preflight",
    # ...
    "asset_source": "placeholder",   # or "textbook", "oem_marketing", "captured", "photographed"
    # ...
}
```

The index generator reads this and renders a colored indicator on each scenario card matching the tier. Audiences see at a glance what's drawn vs. what's real, and the demo is structurally honest.

When a scenario migrates to a new tier, the field updates and the indicator changes — that's the only signal needed. No separate tracking spreadsheet, no out-of-sync documentation.

## Why we're not lying about the placeholder scenarios in the meantime

The "asset checklist" leave-behind in `docs/hw-sw-fusion-required-assets.md` already explicitly tells buyers what assets the production version requires. It calls out PoC substitutes as substitutes. The index indicator is the same idea applied per-scenario: honest about where each scenario sits *today*, not a claim about where it has to stay.

A buyer who sees "🔴 Placeholder" on a scenario card and asks "why is that one drawn?" gets the right answer: *because we haven't migrated that one yet, here's what we'd source for production* — same answer the leave-behind already gives, just surfaced earlier in the demo.

A buyer who sees no indicator and assumes everything is real assets is the failure mode this prevents.

## Document Change Log

| Date | Change |
|---|---|
| 2026-05-02 | Initial version. Status table reflects post-fusion-PoC reality. |
