"""
video_casts.py — Character cast definitions for Veo 3 video generation.

Two casts of equivalent structure (Dave/Sandra/Marcus/Keisha — receiving lead,
compliance, cold chain, QA), interchangeable via the same scene template.

Casts:
  CAST_BIGFOOT  — Sasquatch employees (the original "memorable demo" cast).
  CAST_HUMAN    — Photorealistic human warehouse workers (the "serious" cast
                  for stakeholders who balk at the Bigfoot framing).

The SCENE_TEMPLATE list contains all 13 scenes, with character-specific phrasing
abstracted into per-cast tokens (e.g. {finger_descriptor}, {breath_in_cold},
{background_workers}). Each cast supplies these tokens. Callers select a cast
and call build_scenes(cast) to get the rendered SCENES list ready for Veo.

Usage:
    from video_casts import CAST_BIGFOOT, CAST_HUMAN, build_scenes
    scenes = build_scenes(CAST_HUMAN)        # 13 fully-rendered scenes
    poc_scenes = build_poc_scenes(CAST_HUMAN)  # 3-scene subset for $3.60 demo
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


# ── Cast definition ──────────────────────────────────────────────────────────
@dataclass
class Cast:
    """A complete cast of four characters plus species-specific prompt tokens.

    Tokens are short phrases interpolated into scene prompts so the same scene
    template renders cleanly for either cast. If you add a new cast, fill in
    every token. Missing tokens fall back to species-neutral defaults that may
    not match perfectly — set them deliberately.
    """
    name: str                          # short id, e.g. "bigfoot", "human"
    label: str                         # display label, e.g. "Bigfoot Cast"

    # Four character cards — full description strings, embedded verbatim
    # into Veo prompts. Same character archetypes across casts so dialogue
    # and role behaviour stay identical.
    dave: str
    sandra: str
    marcus: str
    keisha: str

    # Species-specific tokens. These plug into SCENE_TEMPLATE.
    finger_descriptor: str             # e.g. "large furry" vs ""
    thumbs_up_descriptor: str          # e.g. "big furry" vs ""
    breath_in_cold: str                # e.g. "breath visibly fogging in the cold air"
    frost_descriptor: str              # e.g. "frost forming on his black fur" vs "frost on his beard"
    background_workers: str            # short phrase for outro crowd
    background_workers_outro: str      # longer phrase with color cues for outro
    species_intro_note: str = ""       # optional flavour line in scene 01

    def fmt(self, template: str) -> str:
        """Apply this cast's tokens to a scene template string.

        Empty-string substitutions (e.g. finger_descriptor="" for humans)
        can leave double spaces — collapse those before returning so Veo
        sees clean prose.
        """
        import re
        rendered = template.format(
            DAVE=self.dave,
            SANDRA=self.sandra,
            MARCUS=self.marcus,
            KEISHA=self.keisha,
            finger=self.finger_descriptor,
            thumbs_up=self.thumbs_up_descriptor,
            breath=self.breath_in_cold,
            frost=self.frost_descriptor,
            bg_workers=self.background_workers,
            bg_workers_outro=self.background_workers_outro,
        )
        # Collapse runs of spaces produced by empty-token substitutions.
        # Don't touch newlines or tabs.
        return re.sub(r" {2,}", " ", rendered)


# ── Cast: Bigfoot (original) ─────────────────────────────────────────────────
CAST_BIGFOOT = Cast(
    name="bigfoot",
    label="Bigfoot Cast",
    dave=(
        "Dave, a 7-foot sasquatch with dark reddish-brown fur, broad shoulders, "
        "a wide friendly face with amber eyes, wearing a bright orange GLOBALMART SE-DC "
        "safety vest and a yellow employee ID badge clipped to the left strap"
    ),
    sandra=(
        "Sandra, a 7-foot sasquatch with silver-grey fur, sharp focused eyes, "
        "wearing a red COMPLIANCE safety vest with a laminated badge on a lanyard, "
        "clipboard in hand, authoritative posture"
    ),
    marcus=(
        "Marcus, a 7-foot sasquatch with jet-black fur and a relaxed confident posture, "
        "wearing a yellow RECEIVING safety vest and a blue hard hat, "
        "breath visibly fogging in the cold air"
    ),
    keisha=(
        "Keisha, a 7-foot sasquatch with auburn reddish fur and precise attentive manner, "
        "wearing a white QUALITY ASSURANCE safety vest with a QA logo patch, "
        "holding a tablet computer"
    ),
    finger_descriptor="large furry",
    thumbs_up_descriptor="big furry",
    breath_in_cold="breath visibly fogging in the cold air",
    frost_descriptor="frost forming on his black fur",
    background_workers="other Sasquatch workers",
    background_workers_outro=(
        "other Sasquatch workers — one with silver-grey fur, "
        "one with jet-black fur, one with auburn fur — "
    ),
)


# ── Cast: Human warehouse workers ────────────────────────────────────────────
CAST_HUMAN = Cast(
    name="human",
    label="Warehouse Worker Cast",
    dave=(
        "Dave, a fit 40-year-old man with a short brown beard and warm brown eyes, "
        "broad-shouldered and tall, wearing a bright orange GLOBALMART SE-DC "
        "safety vest over a long-sleeve work shirt, a yellow employee ID badge "
        "clipped to the left strap, work-worn hands"
    ),
    sandra=(
        "Sandra, a focused 45-year-old woman with grey-streaked hair pulled into "
        "a low ponytail, sharp attentive eyes, wearing a red COMPLIANCE safety vest "
        "with a laminated badge on a lanyard, clipboard in hand, authoritative posture"
    ),
    marcus=(
        "Marcus, a confident Black man in his late 30s with a close-cropped beard, "
        "relaxed posture, wearing a yellow RECEIVING safety vest and a blue hard hat, "
        "breath visibly fogging in the cold air"
    ),
    keisha=(
        "Keisha, an attentive Black woman in her early 30s with locs pulled back, "
        "precise careful manner, wearing a white QUALITY ASSURANCE safety vest "
        "with a QA logo patch, holding a tablet computer"
    ),
    # No "furry" qualifiers needed for humans
    finger_descriptor="",
    thumbs_up_descriptor="",
    breath_in_cold="breath visibly fogging in the cold air",
    frost_descriptor="frost on his beard and jacket collar",
    background_workers="other warehouse workers",
    background_workers_outro=(
        "other warehouse workers — a woman with grey-streaked hair in a red vest, "
        "a man with a hard hat in a yellow vest, "
        "and a woman in a white QA vest — "
    ),
)


# ── Scene template ───────────────────────────────────────────────────────────
# Same 13 scenes, abstracted with {tokens} that get filled by Cast.fmt().
# Note: {DAVE}, {SANDRA}, etc. are full character descriptions; lowercase tokens
# like {finger}, {breath} are species-specific qualifiers that may be empty.
SCENE_TEMPLATE = [
    {
        "id": "01_intro",
        "character": "Dave",
        "narration": (
            "Hey, what's up everybody. It's Dave from Receiving, coming at you live "
            "from the dock at GlobalMart Southeast Distribution Center. "
            "Today we're walking through Goods Receipt in SAP MIGO. Let's get into it."
        ),
        "video_prompt": (
            "Handheld selfie-vlog footage of {DAVE}, walking toward the camera "
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
            "Selfie vlog footage of {DAVE}, gesturing broadly toward a delivery truck "
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
            "Selfie vlog shot of {SANDRA}, holding up a printed purchase order document "
            "close to the camera and tapping it emphatically with one {finger} finger, "
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
            "Selfie vlog of {DAVE}, sitting at a warehouse office computer, "
            "leaning toward the camera while pointing at the monitor with one {finger} finger, "
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
            "Selfie vlog of {SANDRA}, holding up three fingers counting one-zero-one, "
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
            "Selfie vlog footage of {DAVE}, walking along warehouse shelving with a clipboard, "
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
            "Selfie vlog of {KEISHA}, kneeling beside a pallet of refrigerated food products, "
            "scanning a barcode label with a handheld scanner while glancing at the camera, "
            "cold storage area, {breath}, earnest expression, "
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
            "Selfie vlog of {MARCUS}, standing inside a walk-in freezer, "
            "{frost}, turning to point at a temperature zone sign on the wall "
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
            "Selfie vlog of {KEISHA}, standing at a QA inspection station, "
            "holding up a {thumbs_up} thumbs up at the camera, then turning to gesture "
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
            "Selfie vlog of {DAVE}, pressing a keyboard key with great ceremony "
            "using one {finger} finger, filming himself with wide excited eyes, "
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
            "Selfie vlog of {SANDRA}, wagging a {finger} finger sternly at the camera "
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
            "Selfie vlog of {DAVE}, standing at a whiteboard in a warehouse break room "
            "pointing at three numbered items, then looking back at camera with an encouraging smile "
            "and giving a thumbs up, {bg_workers} visible at break tables in background, "
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
            "Selfie vlog of {DAVE}, giving a big enthusiastic wave goodbye to the camera "
            "at a distribution center receiving dock at golden hour, sunlight streaming in, "
            "{bg_workers_outro}waving in the background, huge warm grin, "
            "slowly stepping back from camera, cinematic golden light, photorealistic. "
            "Dave speaks to camera: 'That's a wrap! Questions? Check the job aid on the portal. "
            "I'm Dave, I work here, and stay safe out there on those docks!'"
        ),
    },
]


# 3-scene POC subset — must match scene IDs in SCENE_TEMPLATE
POC_SCENE_IDS = ("01_intro", "05_movement_type", "13_outro")


# ── Builders ─────────────────────────────────────────────────────────────────
CASTS = {
    "bigfoot": CAST_BIGFOOT,
    "human": CAST_HUMAN,
}


def get_cast(name: str) -> Cast:
    """Look up a cast by short name; raises clearly if unknown."""
    if name not in CASTS:
        valid = ", ".join(sorted(CASTS.keys()))
        raise ValueError(f"Unknown cast '{name}'. Available: {valid}")
    return CASTS[name]


def build_scenes(cast: Cast) -> list[dict]:
    """Return 13 fully-rendered scene dicts for the chosen cast."""
    rendered = []
    for scene in SCENE_TEMPLATE:
        rendered.append({
            "id": scene["id"],
            "character": scene["character"],
            "narration": scene["narration"],          # narration is cast-agnostic
            "video_prompt": cast.fmt(scene["video_prompt"]),
        })
    return rendered


def build_poc_scenes(cast: Cast) -> list[dict]:
    """Return the 3-scene POC subset (intro + 101 lesson + outro) for cast."""
    full = build_scenes(cast)
    return [s for s in full if s["id"] in POC_SCENE_IDS]
