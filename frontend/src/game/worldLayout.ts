import type { Point, SpaceLayout } from "../types";

export const DEFAULT_LAYOUT: SpaceLayout = {
  id: "local_fallback",
  name: "Fallback",
  width: 24,
  height: 18,
  start: { x: 12, y: 9 },
  blocked: [],
  palette: {
    wallLeft: "#586f82",
    wallRight: "#465d71",
    wallTop: "#9eb3c2",
    trim: "#d9e8ee",
    trimDark: "#2b455d",
    trimSoft: "#8aa4b7",
    floorA: "#b2aaa0",
    floorB: "#9e9a93",
    floorLine: "#6c6963",
    floorEdge: "#2b3034",
    glassA: "#c4eef8",
    glassB: "#80bfd8",
    dark: "#06080b",
  },
  walls: { west: true, north: true },
  windows: [
    { wall: "west", start: 2, size: 5 },
    { wall: "west", start: 9, size: 5 },
    { wall: "north", start: 6, size: 5 },
  ],
  doors: [{ wall: "north", start: 21, size: 2 }],
};

function pointFrom(value: unknown): Point | null {
  if (Array.isArray(value) && value.length === 2 && typeof value[0] === "number" && typeof value[1] === "number") {
    return { x: value[0], y: value[1] };
  }

  const point = value as Point;
  if (point && typeof point.x === "number" && typeof point.y === "number") return { x: point.x, y: point.y };
  return null;
}

export function normalizeLayout(value: unknown): SpaceLayout {
  const raw = value as Partial<SpaceLayout> | undefined;
  if (!raw || typeof raw !== "object") return DEFAULT_LAYOUT;

  const width = typeof raw.width === "number" && raw.width > 3 ? Math.floor(raw.width) : DEFAULT_LAYOUT.width;
  const height = typeof raw.height === "number" && raw.height > 3 ? Math.floor(raw.height) : DEFAULT_LAYOUT.height;
  const start = pointFrom(raw.start) ?? DEFAULT_LAYOUT.start;
  const blocked = Array.isArray(raw.blocked)
    ? raw.blocked.map(pointFrom).filter((point): point is Point => Boolean(point))
    : DEFAULT_LAYOUT.blocked;

  return {
    id: typeof raw.id === "string" ? raw.id : DEFAULT_LAYOUT.id,
    name: typeof raw.name === "string" ? raw.name : undefined,
    width,
    height,
    start,
    blocked,
    palette: raw.palette && typeof raw.palette === "object" ? raw.palette : {},
    walls: raw.walls && typeof raw.walls === "object" ? raw.walls : DEFAULT_LAYOUT.walls,
    windows: Array.isArray(raw.windows) ? raw.windows : DEFAULT_LAYOUT.windows,
    doors: Array.isArray(raw.doors) ? raw.doors : DEFAULT_LAYOUT.doors,
  };
}

export function openTile(layout: SpaceLayout, x: number, y: number) {
  return x >= 0 && x < layout.width && y >= 0 && y < layout.height && !layout.blocked.some(point => point.x === x && point.y === y);
}
