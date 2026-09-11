#!/usr/bin/env python3
"""Extract the approved Atrium reference sheet into individual transparent PNG sprites.

The source sheet is intentionally kept in frontend/public/assets/reference so a beginner can
replace it and regenerate the same file names later.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "frontend/public/assets/reference/atrium_reference_sheet.png"
OUT_AVATARS = ROOT / "frontend/public/assets/avatars"
OUT_ITEMS = ROOT / "frontend/public/assets/items"

# Manual crops from the approved generated reference sheet.
# Values are left, top, right, bottom in source pixels.
AVATAR_CROPS = {
    "spiky_red": (83, 83, 199, 375),
    "pony_black": (247, 83, 372, 373),
    "messy_blue": (434, 88, 550, 374),
    "mohawk_skull": (610, 84, 712, 373),
    "hood_green": (769, 93, 884, 373),
    "blonde_pink": (935, 93, 1056, 372),
    "curly_coat": (1103, 93, 1222, 375),
    "blue_bob": (1267, 100, 1377, 373),
}
ITEM_CROPS = {
    "royal_chair": (77, 402, 321, 750),
    "reception_desk": (385, 459, 724, 749),
    "work_desk": (780, 439, 1115, 766),
    "floor_lamp": (1219, 451, 1327, 728),
    "floor_plant": (50, 772, 196, 1024),
    "display_case": (240, 785, 456, 1052),
    "world_globe": (487, 813, 643, 1032),
    "map_board": (710, 790, 901, 1042),
    "coffee_table": (950, 849, 1150, 1036),
    "lounge_chair": (1179, 768, 1409, 1049),
}


def transparent_crop(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    crop = image.crop(box).convert("RGBA")
    pix = crop.load()
    w, h = crop.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            # Remove the white sheet background. Keep darker contact shadows and anti-aliased pixels.
            if r > 235 and g > 235 and b > 235:
                pix[x, y] = (255, 255, 255, 0)
    # Trim fully transparent border and add a tiny padding so outlines do not clip.
    bbox = crop.getbbox()
    if bbox:
        crop = crop.crop(bbox)
    padded = Image.new("RGBA", (crop.width + 8, crop.height + 8), (255, 255, 255, 0))
    padded.alpha_composite(crop, (4, 4))
    return padded


def main() -> None:
    source = Image.open(SOURCE).convert("RGB")
    OUT_AVATARS.mkdir(parents=True, exist_ok=True)
    OUT_ITEMS.mkdir(parents=True, exist_ok=True)

    for name, box in AVATAR_CROPS.items():
        transparent_crop(source, box).save(OUT_AVATARS / f"{name}.png")

    for name, box in ITEM_CROPS.items():
        transparent_crop(source, box).save(OUT_ITEMS / f"{name}.png")

    print(f"wrote {len(AVATAR_CROPS)} avatars and {len(ITEM_CROPS)} items")


if __name__ == "__main__":
    main()
