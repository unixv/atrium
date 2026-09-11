export type Message = Record<string, unknown>;

export type Avatar = {
  avatar_preset?: string;
  skin_color?: string;
  hair_style?: string;
  hair_color?: string;
  shirt_style?: string;
  shirt_color?: string;
  pants_style?: string;
  pants_color?: string;
  shoe_style?: string;
  shoe_color?: string;
};

export type Member = {
  id: string;
  name: string;
  space: string | null;
  x: number;
  y: number;
  facing?: "north" | "south" | "east" | "west";
  posture?: "standing" | "sitting";
  sitting_item_id?: string | null;
  avatar?: Avatar;
};

export type Point = { x: number; y: number };

export type SpaceLayout = {
  id: string;
  name?: string;
  width: number;
  height: number;
  start: Point;
  blocked: Point[];
  palette?: Record<string, string>;
  walls?: { west?: boolean; north?: boolean };
  windows?: Array<{ wall: "west" | "north"; start: number; size: number }>;
  doors?: Array<{ wall: "west" | "north"; start: number; size: number }>;
};

export type SpaceLayoutOption = {
  id: string;
  name: string;
  width?: number;
  height?: number;
};

export type Space = {
  id: string;
  name: string;
  description?: string;
  owner?: string | null;
  owner_id?: string | null;
  members: number;
  layout_id?: string;
};

export type ItemLayer = "floor" | "object";

export type ItemRender = {
  layer?: ItemLayer;
  draw_width_tiles?: number;
  anchor_x?: number;
  anchor_y?: number;
  anchor_tile_y?: number;
  depth_offset?: number;
  shadow?: boolean;
};

export type RoomItem = {
  id: string;
  space_id?: string;
  item_id: string;
  name: string;
  sprite: string;
  width: number;
  height: number;
  blocks_movement: boolean;
  category?: string;
  x: number;
  y: number;
  rotation?: number;
  owner_id?: string | null;
  can_sit?: boolean;
  seat?: Point;
} & ItemRender;

export type CatalogItem = {
  id: string;
  name: string;
  sprite: string;
  width: number;
  height: number;
  blocks_movement: boolean;
  category?: string;
  can_sit?: boolean;
  seat?: Point;
} & ItemRender;

export type Bubble = {
  id: number;
  memberId: string;
  text: string;
  created: number;
  until: number;
};

export type ChatLine = { text: string };
