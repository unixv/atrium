import type { CatalogItem, Member, RoomItem, Space } from "./types";

export function isMember(value: unknown): value is Member {
  const m = value as Member;
  return Boolean(
    m &&
      typeof m.id === "string" &&
      typeof m.name === "string" &&
      typeof m.x === "number" &&
      typeof m.y === "number"
  );
}

export function isSpace(value: unknown): value is Space {
  const s = value as Space;
  return Boolean(s && typeof s.id === "string" && typeof s.name === "string" && typeof s.members === "number");
}

export function isCatalogItem(value: unknown): value is CatalogItem {
  const item = value as CatalogItem;
  return Boolean(item && typeof item.id === "string" && typeof item.name === "string" && typeof item.sprite === "string");
}

export function isRoomItem(value: unknown): value is RoomItem {
  const item = value as RoomItem;
  return Boolean(
    item &&
      typeof item.id === "string" &&
      typeof item.item_id === "string" &&
      typeof item.sprite === "string" &&
      typeof item.x === "number" &&
      typeof item.y === "number"
  );
}
