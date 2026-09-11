from copy import deepcopy
from typing import Any


DEFAULT_LAYOUT_ID = "loft_corner"

LAYOUTS: dict[str, dict[str, Any]] = {
    "loft_corner": {
        "id": "loft_corner",
        "name": "Loft Corner",
        "width": 24,
        "height": 18,
        "start": {"x": 12, "y": 9},
        "blocked": [],
        "palette": {
            "wallLeft": "#8da0ad",
            "wallRight": "#788f9e",
            "wallTop": "#e6f0f5",
            "trim": "#f6fbff",
            "trimDark": "#435e73",
            "trimSoft": "#abc1d1",
            "floorA": "#b9b7ad",
            "floorB": "#a8a79f",
            "floorLine": "#858a83",
            "floorEdge": "#32393d",
            "glassA": "#d7f6fb",
            "glassB": "#8ccbdc",
            "dark": "#06080b",
        },
        "walls": {"west": True, "north": True},
        "windows": [
            {"wall": "west", "start": 2, "size": 5},
            {"wall": "west", "start": 9, "size": 5},
            {"wall": "north", "start": 6, "size": 5},
        ],
        "doors": [{"wall": "north", "start": 21, "size": 2}],
    },
    "clean_studio": {
        "id": "clean_studio",
        "name": "Clean Studio",
        "width": 14,
        "height": 14,
        "start": {"x": 8, "y": 7},
        "blocked": [],
        "palette": {
            "wallLeft": "#dbcbae",
            "wallRight": "#cfbd9d",
            "wallTop": "#f5ead8",
            "trim": "#fff7e8",
            "trimDark": "#7f684f",
            "trimSoft": "#bfa98a",
            "floorA": "#c1c6bd",
            "floorB": "#adb6af",
            "floorLine": "#89918c",
            "floorEdge": "#313b39",
            "glassA": "#d8f5fb",
            "glassB": "#93cfe0",
            "dark": "#07090c",
        },
        "walls": {"west": True, "north": True},
        "windows": [
            {"wall": "west", "start": 3, "size": 4},
            {"wall": "north", "start": 5, "size": 4},
        ],
        "doors": [{"wall": "north", "start": 11, "size": 2}],
    },
    "wide_gallery": {
        "id": "wide_gallery",
        "name": "Wide Gallery",
        "width": 30,
        "height": 16,
        "start": {"x": 15, "y": 8},
        "blocked": [],
        "palette": {
            "wallLeft": "#59596a",
            "wallRight": "#48495b",
            "wallTop": "#a3a5b8",
            "trim": "#d8d9e6",
            "trimDark": "#303145",
            "trimSoft": "#858899",
            "floorA": "#b2aa9b",
            "floorB": "#a0988c",
            "floorLine": "#82786e",
            "floorEdge": "#302b27",
            "glassA": "#cde4ed",
            "glassB": "#99bfd0",
            "dark": "#060608",
        },
        "walls": {"west": True, "north": True},
        "windows": [
            {"wall": "west", "start": 2, "size": 4},
            {"wall": "west", "start": 8, "size": 4},
            {"wall": "north", "start": 8, "size": 5},
            {"wall": "north", "start": 16, "size": 5},
        ],
        "doors": [{"wall": "north", "start": 27, "size": 2}],
    },
}


def layout_view(layout_id: str | None = None) -> dict[str, Any]:
    layout = LAYOUTS.get(layout_id or DEFAULT_LAYOUT_ID) or LAYOUTS[DEFAULT_LAYOUT_ID]
    return deepcopy(layout)


def layout_start(layout_id: str | None = None) -> tuple[int, int]:
    layout = layout_view(layout_id)
    start = layout.get("start") or {}
    return int(start.get("x", 0)), int(start.get("y", 0))


def open_tile(x: int, y: int, layout_id: str | None = None) -> bool:
    layout = layout_view(layout_id)
    width = int(layout.get("width", 0))
    height = int(layout.get("height", 0))
    blocked = {tuple(item) for item in layout.get("blocked", []) if isinstance(item, list) and len(item) == 2}
    return 0 <= x < width and 0 <= y < height and (x, y) not in blocked


def layout_size(layout_id: str | None = None) -> tuple[int, int]:
    layout = layout_view(layout_id)
    return int(layout["width"]), int(layout["height"])
