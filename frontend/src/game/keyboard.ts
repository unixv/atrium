import type { Point } from "../types";

const MOVE_KEYS: Readonly<Record<string, Point>> = {
  ArrowUp: { x: 0, y: -1 },
  ArrowDown: { x: 0, y: 1 },
  ArrowLeft: { x: -1, y: 0 },
  ArrowRight: { x: 1, y: 0 },
  w: { x: 0, y: -1 },
  s: { x: 0, y: 1 },
  a: { x: -1, y: 0 },
  d: { x: 1, y: 0 },
};

export function movementDelta(key: string): Point | undefined {
  return MOVE_KEYS[key.length === 1 ? key.toLowerCase() : key];
}

export function acceptsGameKeys(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return true;
  return !target.closest("input, textarea, select, button, [contenteditable='true']");
}
