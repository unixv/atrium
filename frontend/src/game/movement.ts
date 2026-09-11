import { App } from "../app";
import type { CatalogItem, Point } from "../types";
import { RoomRenderer } from "./roomRenderer";
import { openTile } from "./worldLayout";

function walkable(app: App, x: number, y: number) {
  return openTile(app.state.layout, x, y) && !app.state.itemBlocksTile(x, y);
}

function itemFits(app: App, item: CatalogItem, x: number, y: number) {
  for (let ty = y; ty < y + item.height; ty++) {
    for (let tx = x; tx < x + item.width; tx++) {
      if (!openTile(app.state.layout, tx, ty)) return false;
      if (app.state.itemAt(tx, ty)) return false;
    }
  }
  return true;
}

function buildPath(app: App, from: Point, to: Point) {
  const key = (point: Point) => `${point.x},${point.y}`;
  if (from.x === to.x && from.y === to.y) return [];

  const queue: Point[] = [from];
  const previous = new Map<string, Point | null>();
  previous.set(key(from), null);

  const directions = [
    { x: 1, y: 0 }, { x: -1, y: 0 }, { x: 0, y: 1 }, { x: 0, y: -1 },
    { x: 1, y: 1 }, { x: 1, y: -1 }, { x: -1, y: 1 }, { x: -1, y: -1 },
  ];

  for (let index = 0; index < queue.length; index++) {
    const current = queue[index];
    const neighbors = directions
      .map(dir => ({ x: current.x + dir.x, y: current.y + dir.y, dx: dir.x, dy: dir.y }))
      .sort((a, b) => Math.hypot(a.x - to.x, a.y - to.y) - Math.hypot(b.x - to.x, b.y - to.y));

    for (const next of neighbors) {
      if (!walkable(app, next.x, next.y)) continue;
      if (next.dx !== 0 && next.dy !== 0) {
        // Do not cut diagonally through blocked corners.
        if (!walkable(app, current.x + next.dx, current.y) || !walkable(app, current.x, current.y + next.dy)) continue;
      }

      const nextKey = key(next);
      if (previous.has(nextKey)) continue;
      previous.set(nextKey, current);
      if (next.x === to.x && next.y === to.y) {
        const path: Point[] = [next];
        let cursor = current;
        while (!(cursor.x === from.x && cursor.y === from.y)) {
          path.push(cursor);
          const prior = previous.get(key(cursor));
          if (!prior) break;
          cursor = prior;
        }
        return path.reverse();
      }
      queue.push(next);
    }
  }

  return [];
}

export function walkTo(app: App, x: number, y: number) {
  if (!app.state.hasName()) return app.needsName();
  const me = app.state.me;
  if (!me || !me.space || !walkable(app, x, y)) return;

  const drawn = app.state.drawn.get(me.id) ?? { x: me.x, y: me.y };
  const start = { x: Math.round(drawn.x), y: Math.round(drawn.y) };
  const path = buildPath(app, start, { x, y });
  if (path.length === 0) return;

  // Client prediction: animate immediately and send the full path once. The server
  // validates every step and publishes the same route to other players.
  app.state.setRoute(me.id, path);
  const final = path[path.length - 1];
  const updatedMe = { ...me, x: final.x, y: final.y };
  app.state.me = updatedMe;
  app.state.saveMember(updatedMe);
  app.send({ type: "position.walk", path });
}

export function setupMovement(app: App, renderer: RoomRenderer) {
  app.el.canvas.addEventListener("mousemove", event => renderer.setHoverFromClient(event.clientX, event.clientY));
  app.el.canvas.addEventListener("mouseleave", () => renderer.clearHover());

  app.el.canvas.addEventListener("contextmenu", event => {
    event.preventDefault();
    if (!app.state.buildMode) return;
    const point = renderer.screenToTile(event.clientX, event.clientY);
    if (!point) return;
    const existing = app.state.itemAt(point.x, point.y);
    if (existing) app.send({ type: "item.remove", id: existing.id });
  });

  app.el.canvas.addEventListener("click", event => {
    const point = renderer.screenToTile(event.clientX, event.clientY);
    if (!point) return;

    if (app.state.buildMode) {
      const existing = app.state.itemAt(point.x, point.y);
      if (app.state.buildRemoveMode) {
        if (existing) app.send({ type: "item.remove", id: existing.id });
        return;
      }

      const selected = app.state.selectedCatalogItem();
      if (selected && !existing && itemFits(app, selected, point.x, point.y)) {
        app.send({ type: "item.place", item_id: selected.id, x: point.x, y: point.y });
      }
      return;
    }

    const existing = app.state.itemAt(point.x, point.y);
    if (existing?.can_sit) {
      app.send({ type: "item.use", id: existing.id });
      return;
    }

    walkTo(app, point.x, point.y);
  });
}
