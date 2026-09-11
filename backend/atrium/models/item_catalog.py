from copy import deepcopy
from typing import Any

SPRITE_VERSION = 41


def sprite(name: str) -> str:
    return f"/assets/items/{name}.png?v={SPRITE_VERSION}"


def item(
    id: str,
    name: str,
    category: str,
    png: str,
    width: int,
    height: int,
    *,
    blocks: bool = True,
    layer: str = "object",
    draw_width_tiles: float | None = None,
    anchor_x: float = 0.5,
    anchor_y: float | None = None,
    anchor_tile_y: float | None = None,
    depth_offset: float | None = None,
    shadow: bool | None = None,
    can_sit: bool = False,
    seat: dict[str, int] | None = None,
) -> dict[str, Any]:
    if anchor_y is None:
        anchor_y = 0.56 if layer == "floor" else 0.965
    if anchor_tile_y is None:
        anchor_tile_y = 0.52 if layer == "floor" else 0.90
    if draw_width_tiles is None:
        draw_width_tiles = max(0.85, width * 1.04)
    if depth_offset is None:
        depth_offset = -0.60 if layer == "floor" else max(0.30, (width + height) * 0.18)
    if shadow is None:
        shadow = layer != "floor"

    result = {
        "id": id,
        "name": name,
        "category": category,
        "sprite": sprite(png),
        "width": width,
        "height": height,
        "blocks_movement": blocks,
        "layer": layer,
        "draw_width_tiles": draw_width_tiles,
        "anchor_x": anchor_x,
        "anchor_y": anchor_y,
        "anchor_tile_y": anchor_tile_y,
        "depth_offset": depth_offset,
        "shadow": shadow,
        "can_sit": can_sit,
    }
    if seat is not None:
        result["seat"] = seat
    return result


ITEM_CATALOG: dict[str, dict[str, Any]] = {
    # Seating
    "royal_chair": item("royal_chair", "Royal Chair", "Seating", "royal_chair", 2, 2, draw_width_tiles=1.70, anchor_tile_y=0.94, depth_offset=0.58, can_sit=True, seat={"x": 1, "y": 1}),
    "lounge_chair": item("lounge_chair", "Lounge Chair", "Seating", "lounge_chair", 1, 1, draw_width_tiles=1.10, anchor_tile_y=0.92, depth_offset=0.36, can_sit=True, seat={"x": 0, "y": 0}),
    "lounge_seat": item("lounge_seat", "Lounge Seat", "Seating", "lounge_seat", 2, 1, draw_width_tiles=1.75, anchor_tile_y=0.91, depth_offset=0.38, can_sit=True, seat={"x": 0, "y": 0}),
    "office_chair": item("office_chair", "Office Chair", "Seating", "office_chair", 1, 1, draw_width_tiles=1.02, anchor_tile_y=0.91, depth_offset=0.34, can_sit=True, seat={"x": 0, "y": 0}),
    "cube_seat": item("cube_seat", "Cube Seat", "Seating", "cube_seat", 1, 1, draw_width_tiles=0.92, anchor_tile_y=0.90, depth_offset=0.30, can_sit=True, seat={"x": 0, "y": 0}),
    "pouf_coral": item("pouf_coral", "Ottoman", "Seating", "pouf_coral", 1, 1, draw_width_tiles=0.92, anchor_tile_y=0.90, depth_offset=0.30, can_sit=True, seat={"x": 0, "y": 0}),

    # Desks and tables
    "reception_desk": item("reception_desk", "Reception Desk", "Desks", "reception_desk", 3, 1, draw_width_tiles=2.70, anchor_tile_y=0.91, depth_offset=0.46),
    "executive_desk": item("executive_desk", "Executive Desk", "Desks", "executive_desk", 3, 2, draw_width_tiles=2.95, anchor_tile_y=0.91, depth_offset=0.50),
    "work_desk": item("work_desk", "Work Desk", "Desks", "work_desk", 2, 1, draw_width_tiles=2.05, anchor_tile_y=0.91, depth_offset=0.44),
    "work_terminal": item("work_terminal", "Work Terminal", "Desks", "work_terminal", 2, 1, draw_width_tiles=2.12, anchor_tile_y=0.91, depth_offset=0.44),
    "drink_counter": item("drink_counter", "Service Counter", "Desks", "drink_counter", 3, 1, draw_width_tiles=2.50, anchor_tile_y=0.91, depth_offset=0.45),
    "coffee_table": item("coffee_table", "Coffee Table", "Tables", "coffee_table", 2, 1, blocks=False, draw_width_tiles=1.50, anchor_tile_y=0.89, depth_offset=0.28),
    "glass_table": item("glass_table", "Glass Table", "Tables", "glass_table", 2, 1, blocks=False, draw_width_tiles=1.72, anchor_tile_y=0.89, depth_offset=0.28),

    # Display
    "display_case": item("display_case", "Display Case", "Display", "display_case", 1, 1, draw_width_tiles=1.10, anchor_tile_y=0.915, depth_offset=0.38),
    "trophy_case": item("trophy_case", "Trophy Case", "Display", "trophy_case", 2, 1, draw_width_tiles=1.82, anchor_tile_y=0.915, depth_offset=0.42),
    "marble_plinth": item("marble_plinth", "Marble Plinth", "Display", "marble_plinth", 1, 1, draw_width_tiles=0.98, anchor_tile_y=0.91, depth_offset=0.34),
    "bubble_sculpture": item("bubble_sculpture", "Bubble Sculpture", "Display", "bubble_sculpture", 1, 1, draw_width_tiles=1.00, anchor_tile_y=0.93, depth_offset=0.42),
    "info_kiosk": item("info_kiosk", "Info Kiosk", "Display", "info_kiosk", 1, 1, draw_width_tiles=0.96, anchor_tile_y=0.92, depth_offset=0.38),
    "world_globe": item("world_globe", "World Globe", "Display", "world_globe", 1, 1, draw_width_tiles=0.88, anchor_tile_y=0.915, depth_offset=0.39),
    "map_board": item("map_board", "Map Board", "Display", "map_board", 2, 1, draw_width_tiles=1.70, anchor_tile_y=0.92, depth_offset=0.45),
    "wall_monitor": item("wall_monitor", "Display Monitor", "Display", "wall_monitor", 1, 1, draw_width_tiles=1.05, anchor_tile_y=0.92, depth_offset=0.37),
    "divider_panel": item("divider_panel", "Divider Panel", "Display", "divider_panel", 2, 1, draw_width_tiles=1.85, anchor_tile_y=0.92, depth_offset=0.43),

    # Decor
    "floor_plant": item("floor_plant", "Floor Plant", "Decor", "floor_plant", 1, 1, draw_width_tiles=0.92, anchor_tile_y=0.915, depth_offset=0.39),
    "floor_planter": item("floor_planter", "Planter", "Decor", "floor_planter", 1, 1, draw_width_tiles=1.02, anchor_tile_y=0.915, depth_offset=0.39),
    "plant_stand": item("plant_stand", "Plant Stand", "Decor", "plant_stand", 1, 1, draw_width_tiles=0.98, anchor_tile_y=0.92, depth_offset=0.40),
    "floor_lamp": item("floor_lamp", "Floor Lamp", "Decor", "floor_lamp", 1, 1, draw_width_tiles=0.74, anchor_tile_y=0.92, depth_offset=0.42),
    "lamp_glow": item("lamp_glow", "Glow Lamp", "Decor", "lamp_glow", 1, 1, draw_width_tiles=0.86, anchor_tile_y=0.92, depth_offset=0.42),
    "signal_mast": item("signal_mast", "Signal Mast", "Decor", "signal_mast", 1, 1, draw_width_tiles=0.70, anchor_tile_y=0.93, depth_offset=0.43),
    "filing_cabinet": item("filing_cabinet", "Filing Cabinet", "Decor", "filing_cabinet", 1, 1, draw_width_tiles=0.96, anchor_tile_y=0.91, depth_offset=0.34),
    "crate_walnut": item("crate_walnut", "Walnut Crate", "Decor", "crate_walnut", 1, 1, draw_width_tiles=0.88, anchor_tile_y=0.90, depth_offset=0.32),
    "book_stack": item("book_stack", "Book Stack", "Decor", "book_stack", 1, 1, blocks=False, draw_width_tiles=0.72, anchor_tile_y=0.88, depth_offset=0.24),

    # Floor pieces
    "rug_ocean": item("rug_ocean", "Ocean Rug", "Floor", "rug_ocean", 3, 2, blocks=False, layer="floor", draw_width_tiles=2.65, anchor_y=0.56, anchor_tile_y=0.52, depth_offset=-0.65, shadow=False),
    "runner_sky": item("runner_sky", "Sky Runner", "Floor", "runner_sky", 4, 1, blocks=False, layer="floor", draw_width_tiles=3.25, anchor_y=0.56, anchor_tile_y=0.52, depth_offset=-0.65, shadow=False),
    "floor_marker": item("floor_marker", "Floor Marker", "Floor", "floor_marker", 1, 1, blocks=False, layer="floor", draw_width_tiles=0.88, anchor_y=0.56, anchor_tile_y=0.52, depth_offset=-0.66, shadow=False),
}


def catalog_list() -> list[dict[str, Any]]:
    return [deepcopy(item) for item in ITEM_CATALOG.values()]


def catalog_item(item_id: object) -> dict[str, Any] | None:
    if not isinstance(item_id, str):
        return None
    item = ITEM_CATALOG.get(item_id)
    return deepcopy(item) if item else None
