import re
from dataclasses import asdict, dataclass
from typing import Any

HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

AVATAR_PRESETS = ["spiky_red", "pony_black", "messy_blue", "mohawk_skull", "hood_green", "blonde_pink", "curly_coat", "blue_bob"]
HAIR_STYLES = ["short", "side_part", "curly", "spiky", "bob", "buzz"]
SHIRT_STYLES = ["tee", "jacket", "hoodie", "stripe"]
PANTS_STYLES = ["straight", "cuffed", "shorts"]
SHOE_STYLES = ["sneakers", "boots", "loafers"]

DEFAULT_AVATAR = {
    "avatar_preset": "spiky_red",
    "skin_color": "#b8754c",
    "hair_style": "short",
    "hair_color": "#211513",
    "shirt_style": "tee",
    "shirt_color": "#4d8fd6",
    "pants_style": "straight",
    "pants_color": "#263247",
    "shoe_style": "sneakers",
    "shoe_color": "#111722",
}

STYLE_OPTIONS = {
    "avatar_preset": AVATAR_PRESETS,
    "hair_style": HAIR_STYLES,
    "shirt_style": SHIRT_STYLES,
    "pants_style": PANTS_STYLES,
    "shoe_style": SHOE_STYLES,
}

COLOR_FIELDS = {
    "skin_color",
    "hair_color",
    "shirt_color",
    "pants_color",
    "shoe_color",
}

LEGACY_COLOR_NAMES = {
    "black": "#211513",
    "brown": "#59351f",
    "blonde": "#e2bb5f",
    "red": "#9b3d2e",
    "gray": "#888078",
    "purple": "#5d3d72",
}


@dataclass
class Avatar:
    avatar_preset: str = DEFAULT_AVATAR["avatar_preset"]
    skin_color: str = DEFAULT_AVATAR["skin_color"]
    hair_style: str = DEFAULT_AVATAR["hair_style"]
    hair_color: str = DEFAULT_AVATAR["hair_color"]
    shirt_style: str = DEFAULT_AVATAR["shirt_style"]
    shirt_color: str = DEFAULT_AVATAR["shirt_color"]
    pants_style: str = DEFAULT_AVATAR["pants_style"]
    pants_color: str = DEFAULT_AVATAR["pants_color"]
    shoe_style: str = DEFAULT_AVATAR["shoe_style"]
    shoe_color: str = DEFAULT_AVATAR["shoe_color"]

    def view(self) -> dict[str, str]:
        return asdict(self)


def normalize_color(value: Any, fallback: str) -> str:
    if not isinstance(value, str):
        return fallback

    raw = value.strip()
    lowered = raw.lower()
    if lowered in LEGACY_COLOR_NAMES:
        return LEGACY_COLOR_NAMES[lowered]
    if HEX_COLOR_RE.match(raw):
        return raw.lower()
    return fallback


def normalize_avatar(value: Any) -> dict[str, str]:
    source = value if isinstance(value, dict) else {}
    avatar = dict(DEFAULT_AVATAR)

    for field in COLOR_FIELDS:
        avatar[field] = normalize_color(source.get(field), avatar[field])

    for field, options in STYLE_OPTIONS.items():
        incoming = source.get(field)
        if isinstance(incoming, str) and incoming in options:
            avatar[field] = incoming

    # Compatibility for older users that only have avatar.hair_color.
    if "hair_color" in source:
        avatar["hair_color"] = normalize_color(source.get("hair_color"), avatar["hair_color"])

    return avatar


def avatar_from_any(value: Any) -> Avatar:
    return Avatar(**normalize_avatar(value))
