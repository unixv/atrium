import { State } from "../state";
import type { CatalogItem, Member, Point, RoomItem } from "../types";
import { drawCharacter } from "./characterSprite";
import { drawMessageBubbles } from "./messageBubbles";
import { spriteImage } from "./spriteImages";
import { openTile } from "./worldLayout";

type ScreenPoint = { x: number; y: number };
type SceneEntity = { depth: number; draw: () => void };
type MotionState = { dirX: number; dirY: number; phase: number; lastTime: number; moving: boolean };

const DEFAULT_COLORS = {
  wallLeft: "#52677c",
  wallRight: "#43586e",
  wallTop: "#92a8b9",
  trim: "#d6e5ef",
  trimDark: "#273d55",
  trimSoft: "#7f98ad",
  floorA: "#a8a99f",
  floorB: "#999d97",
  floorLine: "#646e71",
  floorEdge: "#2d3740",
  glassA: "#bde8f8",
  glassB: "#77b6d1",
  dark: "#06080b",
};

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}

export class RoomRenderer {
  ctx: CanvasRenderingContext2D;
  tileW = 48;
  tileH = 24;
  ox = 0;
  oy = 0;
  wallHeight = 108;
  hover: Point | null = null;
  private motion = new Map<string, MotionState>();
  private roomCache: HTMLCanvasElement | null = null;
  private roomCacheKey = "";

  constructor(private canvas: HTMLCanvasElement, private state: State) {
    this.ctx = canvas.getContext("2d")!;
  }

  start() {
    window.addEventListener("resize", () => this.resize());
    this.resize();
    this.draw();
  }

  private color(name: keyof typeof DEFAULT_COLORS) {
    return this.state.layout.palette?.[name] ?? DEFAULT_COLORS[name];
  }

  resize() {
    this.roomCacheKey = "";
    const rect = this.canvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    this.canvas.width = Math.max(520, Math.floor(rect.width * ratio));
    this.canvas.height = Math.max(360, Math.floor(rect.height * ratio));
    this.ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    this.ctx.imageSmoothingEnabled = true;

    const cols = this.state.layout.width;
    const rows = this.state.layout.height;
    const safeRight = 24;
    const safeLeft = 24;
    const usableWidth = Math.max(420, rect.width - safeLeft - safeRight);
    const usableHeight = Math.max(320, rect.height - 22);
    const maxByWidth = Math.floor(usableWidth / ((cols + rows) * 0.45));
    const maxByHeight = Math.floor(usableHeight / ((cols + rows) * 0.245 + 4.05));
    this.tileW = Math.max(34, Math.min(74, maxByWidth, maxByHeight));
    if (this.tileW % 2 !== 0) this.tileW -= 1;
    this.tileH = Math.max(15, Math.floor(this.tileW / 2));
    this.wallHeight = Math.max(92, Math.floor(this.tileW * 2.42));

    const floorHeight = (cols + rows) * this.tileH / 2;
    const totalHeight = this.wallHeight + floorHeight + this.tileH + 18;
    const centerLeft = safeLeft;
    const centerRight = rect.width - safeRight;
    this.ox = Math.floor((centerLeft + centerRight) / 2);
    this.oy = Math.floor((rect.height - totalHeight) / 2) + this.wallHeight + 10;
  }

  tileToScreen(x: number, y: number): ScreenPoint {
    return {
      x: this.ox + (x - y) * this.tileW / 2,
      y: this.oy + (x + y) * this.tileH / 2,
    };
  }

  screenToTile(clientX: number, clientY: number) {
    const rect = this.canvas.getBoundingClientRect();
    const lx = clientX - rect.left - this.ox;
    const ly = clientY - rect.top - this.oy;
    const rawX = (lx / (this.tileW / 2) + ly / (this.tileH / 2)) / 2;
    const rawY = (ly / (this.tileH / 2) - lx / (this.tileW / 2)) / 2;
    const x = Math.floor(rawX + 0.5);
    const y = Math.floor(rawY + 0.5);
    if (!openTile(this.state.layout, x, y)) return null;
    return { x, y };
  }

  setHoverFromClient(clientX: number, clientY: number) { this.hover = this.screenToTile(clientX, clientY); }
  clearHover() { this.hover = null; }

  private diamondPath(p: ScreenPoint, inflate = 0) {
    const halfW = this.tileW / 2 + inflate;
    const halfH = this.tileH / 2 + inflate * 0.5;
    this.ctx.beginPath();
    this.ctx.moveTo(p.x, p.y - inflate * 0.5);
    this.ctx.lineTo(p.x + halfW, p.y + halfH);
    this.ctx.lineTo(p.x, p.y + this.tileH + inflate * 0.5);
    this.ctx.lineTo(p.x - halfW, p.y + halfH);
    this.ctx.closePath();
  }

  private fillPoly(points: ScreenPoint[], color: string | CanvasGradient) {
    this.ctx.fillStyle = color;
    this.ctx.beginPath();
    this.ctx.moveTo(points[0].x, points[0].y);
    for (const point of points.slice(1)) this.ctx.lineTo(point.x, point.y);
    this.ctx.closePath();
    this.ctx.fill();
  }

  private strokePoly(points: ScreenPoint[], color: string, width = 1) {
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = width;
    this.ctx.beginPath();
    this.ctx.moveTo(points[0].x, points[0].y);
    for (const point of points.slice(1)) this.ctx.lineTo(point.x, point.y);
    this.ctx.closePath();
    this.ctx.stroke();
    this.ctx.lineWidth = 1;
  }

  private offset(point: ScreenPoint, dx: number, dy: number): ScreenPoint { return { x: point.x + dx, y: point.y + dy }; }

  private drawBackground() {
    const w = this.canvas.clientWidth;
    const h = this.canvas.clientHeight;
    this.ctx.clearRect(0, 0, w, h);
    const bg = this.ctx.createLinearGradient(0, 0, 0, h);
    bg.addColorStop(0, "#21384a");
    bg.addColorStop(0.46, "#101c27");
    bg.addColorStop(1, "#05090d");
    this.ctx.fillStyle = bg;
    this.ctx.fillRect(0, 0, w, h);

    const glow = this.ctx.createRadialGradient(w * 0.52, h * 0.36, 20, w * 0.52, h * 0.36, Math.max(w, h) * 0.52);
    glow.addColorStop(0, "rgba(255, 232, 190, .13)");
    glow.addColorStop(0.52, "rgba(151, 207, 230, .035)");
    glow.addColorStop(1, "rgba(0,0,0,0)");
    this.ctx.fillStyle = glow;
    this.ctx.fillRect(0, 0, w, h);

    this.ctx.fillStyle = "rgba(255,255,255,.007)";
    for (let y = 0; y < h; y += 10) this.ctx.fillRect(0, y, w, 1);
  }

  private drawFloorShadow() {
    const cols = this.state.layout.width;
    const rows = this.state.layout.height;
    const back = this.tileToScreen(0, 0);
    const right = this.tileToScreen(cols - 1, 0);
    const front = this.tileToScreen(cols - 1, rows - 1);
    const left = this.tileToScreen(0, rows - 1);
    this.ctx.fillStyle = "rgba(0,0,0,.30)";
    this.ctx.beginPath();
    this.ctx.moveTo(back.x, back.y + this.tileH + 16);
    this.ctx.lineTo(right.x + this.tileW / 2 + 8, right.y + this.tileH / 2 + 16);
    this.ctx.lineTo(front.x + 8, front.y + this.tileH + 32);
    this.ctx.lineTo(left.x - this.tileW / 2 - 8, left.y + this.tileH / 2 + 32);
    this.ctx.closePath();
    this.ctx.fill();
  }

  private drawWalls() {
    const cols = this.state.layout.width;
    const rows = this.state.layout.height;
    const back = this.tileToScreen(0, 0);
    const right = this.tileToScreen(cols - 1, 0);
    const left = this.tileToScreen(0, rows - 1);

    if (this.state.layout.walls?.west !== false) {
      const wall = [back, left, this.offset(left, 0, -this.wallHeight), this.offset(back, 0, -this.wallHeight)];
      const grad = this.ctx.createLinearGradient(back.x, back.y - this.wallHeight, left.x, left.y);
      grad.addColorStop(0, this.color("wallTop"));
      grad.addColorStop(0.16, this.color("wallLeft"));
      grad.addColorStop(1, this.color("wallLeft"));
      this.fillPoly(wall, grad);
      this.strokePoly(wall, "#19283a", 2);
    }
    if (this.state.layout.walls?.north !== false) {
      const wall = [back, right, this.offset(right, 0, -this.wallHeight), this.offset(back, 0, -this.wallHeight)];
      const grad = this.ctx.createLinearGradient(back.x, back.y - this.wallHeight, right.x, right.y);
      grad.addColorStop(0, this.color("wallTop"));
      grad.addColorStop(0.18, this.color("wallRight"));
      grad.addColorStop(1, this.color("wallRight"));
      this.fillPoly(wall, grad);
      this.strokePoly(wall, "#19283a", 2);
    }

    this.drawWallTopLine(back, left, right);
    if (this.state.layout.walls?.north !== false) this.drawWallTrim(back, right, true);
    if (this.state.layout.walls?.west !== false) this.drawWallTrim(back, left, false);
    this.drawWindows();
    this.drawDoors();
  }

  private drawWallTopLine(back: ScreenPoint, left: ScreenPoint, right: ScreenPoint) {
    this.ctx.strokeStyle = "rgba(255,255,255,.32)";
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    if (this.state.layout.walls?.west !== false) this.ctx.moveTo(left.x, left.y - this.wallHeight + 2);
    this.ctx.lineTo(back.x, back.y - this.wallHeight + 2);
    if (this.state.layout.walls?.north !== false) this.ctx.lineTo(right.x, right.y - this.wallHeight + 2);
    this.ctx.stroke();

    this.ctx.strokeStyle = this.color("wallTop");
    this.ctx.lineWidth = 6;
    this.ctx.beginPath();
    if (this.state.layout.walls?.west !== false) this.ctx.moveTo(left.x, left.y - this.wallHeight + 7);
    this.ctx.lineTo(back.x, back.y - this.wallHeight + 7);
    if (this.state.layout.walls?.north !== false) this.ctx.lineTo(right.x, right.y - this.wallHeight + 7);
    this.ctx.stroke();
    this.ctx.lineWidth = 1;
  }

  private drawWallTrim(from: ScreenPoint, to: ScreenPoint, horizontal: boolean) {
    for (const [offset, color, width] of [[this.wallHeight - 18, this.color("trim"), 4], [this.wallHeight - 25, this.color("trimDark"), 2], [28, this.color("trimSoft"), 3], [21, this.color("trimDark"), 2]] as const) {
      this.ctx.strokeStyle = color;
      this.ctx.lineWidth = width;
      this.ctx.beginPath();
      this.ctx.moveTo(from.x, from.y - offset);
      this.ctx.lineTo(to.x, to.y - offset);
      this.ctx.stroke();
    }

    const count = horizontal ? Math.floor(this.state.layout.width / 2) : Math.floor(this.state.layout.height / 2);
    this.ctx.strokeStyle = "rgba(255,255,255,.16)";
    this.ctx.lineWidth = 1;
    for (let i = 1; i < count; i++) {
      const p = horizontal ? this.tileToScreen(i * 2, 0) : this.tileToScreen(0, i * 2);
      this.ctx.beginPath();
      this.ctx.moveTo(p.x, p.y - 54);
      this.ctx.lineTo(p.x, p.y - 28);
      this.ctx.stroke();
    }
  }

  private wallPoint(wall: "west" | "north", position: number) {
    return wall === "west" ? this.tileToScreen(0, position) : this.tileToScreen(position, 0);
  }

  private drawWindowPanel(wall: "west" | "north", start: number, size: number) {
    const max = wall === "west" ? this.state.layout.height - 1 : this.state.layout.width - 1;
    const a = this.wallPoint(wall, clamp(start, 0, max));
    const b = this.wallPoint(wall, clamp(start + size, 0, max));
    const xOffset = wall === "west" ? 10 : -10;
    const topA = this.offset(a, xOffset, -this.wallHeight + 30);
    const topB = this.offset(b, xOffset, -this.wallHeight + 30);
    const botB = this.offset(b, xOffset, -this.wallHeight + 80);
    const botA = this.offset(a, xOffset, -this.wallHeight + 80);
    const glass = this.ctx.createLinearGradient(topA.x, topA.y, botB.x, botB.y);
    glass.addColorStop(0, this.color("glassA"));
    glass.addColorStop(.55, this.color("glassB"));
    glass.addColorStop(1, "#4c8ca9");
    this.ctx.fillStyle = glass;
    this.ctx.beginPath();
    this.ctx.moveTo(topA.x, topA.y);
    this.ctx.lineTo(topB.x, topB.y);
    this.ctx.lineTo(botB.x, botB.y);
    this.ctx.lineTo(botA.x, botA.y);
    this.ctx.closePath();
    this.ctx.fill();
    this.strokePoly([topA, topB, botB, botA], "#26384b", 2);

    this.ctx.strokeStyle = "rgba(255,255,255,.52)";
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    this.ctx.moveTo(topA.x + 15, topA.y + 7);
    this.ctx.lineTo(botB.x - 22, botB.y - 11);
    this.ctx.moveTo(topA.x + 34, topA.y + 10);
    this.ctx.lineTo(botB.x + 1, botB.y - 12);
    this.ctx.stroke();
  }

  private drawWindows() {
    for (const windowDef of this.state.layout.windows ?? []) this.drawWindowPanel(windowDef.wall, windowDef.start, windowDef.size);
  }

  private drawDoorPanel(wall: "west" | "north", start: number, size: number) {
    const max = wall === "west" ? this.state.layout.height - 1 : this.state.layout.width - 1;
    const a = this.wallPoint(wall, clamp(start, 0, max));
    const b = this.wallPoint(wall, clamp(start + size, 0, max));
    const xOffset = wall === "west" ? 8 : 2;
    const topA = this.offset(a, xOffset, -this.wallHeight + 23);
    const topB = this.offset(b, xOffset, -this.wallHeight + 23);
    const botB = this.offset(b, xOffset, -this.wallHeight + 90);
    const botA = this.offset(a, xOffset, -this.wallHeight + 90);
    this.fillPoly([topA, topB, botB, botA], this.color("dark"));
    this.strokePoly([topA, topB, botB, botA], "#0f1f2f", 2);
  }

  private drawDoors() {
    for (const doorDef of this.state.layout.doors ?? []) this.drawDoorPanel(doorDef.wall, doorDef.start, doorDef.size);
  }

  private drawFloorTile(x: number, y: number) {
    const p = this.tileToScreen(x, y);
    this.diamondPath(p);
    const grad = this.ctx.createLinearGradient(p.x, p.y, p.x, p.y + this.tileH);
    grad.addColorStop(0, (x + y) % 2 === 0 ? this.color("floorA") : "#bec4bd");
    grad.addColorStop(0.58, (x + y) % 2 === 0 ? "#afb8b1" : "#aab3ad");
    grad.addColorStop(1, (x + y) % 2 === 0 ? "#9fa9a4" : this.color("floorB"));
    this.ctx.fillStyle = grad;
    this.ctx.fill();
    this.ctx.strokeStyle = this.color("floorLine");
    this.ctx.globalAlpha = 0.18;
    this.ctx.lineWidth = 1;
    this.ctx.stroke();
    this.ctx.globalAlpha = 1;

    this.ctx.strokeStyle = "rgba(255,255,255,.08)";
    this.ctx.beginPath();
    this.ctx.moveTo(p.x - this.tileW / 2 + 3, p.y + this.tileH / 2);
    this.ctx.lineTo(p.x, p.y + 2);
    this.ctx.stroke();
  }

  private drawFootprint(x: number, y: number, w: number, h: number, fill: string, stroke: string) {
    for (let ty = y; ty < y + h; ty++) {
      for (let tx = x; tx < x + w; tx++) {
        if (!openTile(this.state.layout, tx, ty)) continue;
        const p = this.tileToScreen(tx, ty);
        this.diamondPath(p, 1.4);
        this.ctx.fillStyle = fill;
        this.ctx.fill();
        this.ctx.strokeStyle = stroke;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        this.ctx.lineWidth = 1;
      }
    }
  }

  private itemFits(item: CatalogItem, x: number, y: number) {
    for (let ty = y; ty < y + item.height; ty++) {
      for (let tx = x; tx < x + item.width; tx++) {
        if (!openTile(this.state.layout, tx, ty)) return false;
        if (this.state.itemAt(tx, ty)) return false;
      }
    }
    return true;
  }

  private drawHoverTile() {
    if (!this.hover) return;
    const selected = this.state.buildMode ? this.state.selectedCatalogItem() : null;
    if (this.state.buildRemoveMode) {
      const existing = this.state.itemAt(this.hover.x, this.hover.y);
      if (existing) {
        this.drawFootprint(existing.x, existing.y, existing.width, existing.height, "rgba(255, 92, 92, .20)", "#ffb0b0");
      } else {
        this.drawFootprint(this.hover.x, this.hover.y, 1, 1, "rgba(255, 92, 92, .10)", "rgba(255,176,176,.7)");
      }
      return;
    }

    if (selected) {
      const fits = this.itemFits(selected, this.hover.x, this.hover.y);
      this.drawFootprint(
        this.hover.x,
        this.hover.y,
        selected.width,
        selected.height,
        fits ? "rgba(255, 217, 105, .18)" : "rgba(255, 90, 90, .20)",
        fits ? "#ffe08a" : "#ffb0b0",
      );
      if (fits) this.drawItemSprite({ ...selected, id: "preview", item_id: selected.id, x: this.hover.x, y: this.hover.y, rotation: 0 }, .66);
      return;
    }

    const p = this.tileToScreen(this.hover.x, this.hover.y);
    this.diamondPath(p, 1.5);
    this.ctx.fillStyle = this.state.buildMode ? "rgba(255, 217, 105, .22)" : "rgba(122, 215, 255, .16)";
    this.ctx.fill();
    this.ctx.strokeStyle = this.state.buildMode ? "#ffe08a" : "#a9d7e8";
    this.ctx.lineWidth = 2;
    this.ctx.stroke();
    this.ctx.lineWidth = 1;
  }

  private drawFrontEdge() {
    const cols = this.state.layout.width;
    const rows = this.state.layout.height;
    const left = this.tileToScreen(0, rows - 1);
    const front = this.tileToScreen(cols - 1, rows - 1);
    const right = this.tileToScreen(cols - 1, 0);
    this.ctx.strokeStyle = this.color("floorEdge");
    this.ctx.lineWidth = 7;
    this.ctx.lineJoin = "round";
    this.ctx.beginPath();
    this.ctx.moveTo(left.x - this.tileW / 2, left.y + this.tileH / 2 + 1);
    this.ctx.lineTo(front.x, front.y + this.tileH + 2);
    this.ctx.lineTo(right.x + this.tileW / 2, right.y + this.tileH / 2 + 1);
    this.ctx.stroke();
    this.ctx.lineWidth = 1;
  }

  private drawRoomBase() {
    this.drawBackground();
    this.drawFloorShadow();
    this.drawWalls();
    for (let y = 0; y < this.state.layout.height; y++) {
      for (let x = 0; x < this.state.layout.width; x++) {
        if (!openTile(this.state.layout, x, y)) continue;
        this.drawFloorTile(x, y);
      }
    }
  }

  private itemAnchor(item: Pick<RoomItem, "x" | "y" | "width" | "height" | "anchor_tile_y"> & { layer?: string }) {
    const p = this.tileToScreen(item.x + (item.width - 1) / 2, item.y + (item.height - 1) / 2);
    const defaultY = item.layer === "floor" ? 0.52 : 1.02;
    return { x: p.x, y: p.y + this.tileH * (item.anchor_tile_y ?? defaultY) };
  }

  private drawContactShadow(item: RoomItem | (CatalogItem & { x: number; y: number }), alpha = 1) {
    if (item.shadow === false || (item.layer ?? "object") === "floor") return;
    this.ctx.save();
    this.ctx.globalAlpha = 0.18 * alpha;
    for (let ty = item.y; ty < item.y + item.height; ty++) {
      for (let tx = item.x; tx < item.x + item.width; tx++) {
        const p = this.tileToScreen(tx, ty);
        this.diamondPath({ x: p.x, y: p.y + this.tileH * 0.03 }, -2.8);
        this.ctx.fillStyle = "rgba(0,0,0,.78)";
        this.ctx.fill();
      }
    }
    this.ctx.restore();
  }

  private drawItemSprite(item: RoomItem | (CatalogItem & { id: string; item_id: string; x: number; y: number; rotation?: number }), alpha = 1) {
    const image = spriteImage(item.sprite);
    const anchor = this.itemAnchor(item);
    const drawW = this.tileW * (item.draw_width_tiles ?? Math.max(0.92, item.width * 0.98));
    const ratio = image.naturalHeight && image.naturalWidth ? image.naturalHeight / image.naturalWidth : 0.88;
    const drawH = drawW * ratio;
    const anchorX = item.anchor_x ?? 0.5;
    const anchorY = item.anchor_y ?? ((item.layer ?? "object") === "floor" ? 0.54 : 1.0);
    const x = anchor.x - drawW * anchorX;
    const y = anchor.y - drawH * anchorY;

    this.drawContactShadow(item, alpha);
    if (image.complete && image.naturalWidth > 0) {
      this.ctx.save();
      this.ctx.imageSmoothingEnabled = true;
      this.ctx.globalAlpha = alpha;
      this.ctx.drawImage(image, x, y, drawW, drawH);
      this.ctx.restore();
    }
  }

  private drawFloorItems() {
    const floorItems = this.state.items.filter(item => (item.layer ?? "object") === "floor").sort((a, b) => (a.x + a.y) - (b.x + b.y));
    for (const item of floorItems) this.drawItemSprite(item);
  }

  private drawPoint(memberId: string, targetX: number, targetY: number) {
    const now = performance.now();
    const point = this.state.drawn.get(memberId) ?? { x: targetX, y: targetY };
    const motion = this.motion.get(memberId) ?? { dirX: 0, dirY: 1, phase: 0, lastTime: now, moving: false };
    const dt = Math.min(0.04, Math.max(0, (now - motion.lastTime) / 1000));

    const route = this.state.routes.get(memberId);
    let target = { x: targetX, y: targetY };
    if (route && route.length > 0) target = route[0];

    let dx = target.x - point.x;
    let dy = target.y - point.y;
    let distance = Math.hypot(dx, dy);

    if (route && route.length > 0 && distance < 0.06) {
      point.x = target.x;
      point.y = target.y;
      route.shift();
      if (route.length === 0) this.state.routes.delete(memberId);
      target = route[0] ?? { x: targetX, y: targetY };
      dx = target.x - point.x;
      dy = target.y - point.y;
      distance = Math.hypot(dx, dy);
    }

    if (distance > 6) {
      point.x = targetX;
      point.y = targetY;
      this.state.routes.delete(memberId);
      motion.moving = false;
    } else if (distance > 0.002) {
      const speed = 7.6;
      const step = Math.min(distance, speed * dt);
      const nx = dx / distance;
      const ny = dy / distance;
      point.x += nx * step;
      point.y += ny * step;
      motion.dirX = nx;
      motion.dirY = ny;
      motion.phase = (motion.phase + step * 1.35) % 1;
      motion.moving = distance > 0.035;
    } else {
      point.x = target.x;
      point.y = target.y;
      motion.moving = false;
    }

    motion.lastTime = now;
    this.state.drawn.set(memberId, point);
    this.motion.set(memberId, motion);
    return { point, motion };
  }

  private memberEntity(member: Member): SceneEntity {
    const { point, motion } = this.drawPoint(member.id, member.x, member.y);
    const screen = this.tileToScreen(point.x, point.y);
    return {
      depth: point.x + point.y + 0.25,
      draw: () => drawCharacter(this.ctx, member, screen.x, screen.y + this.tileH * 0.50, this.tileW / 64, this.state.me?.id === member.id, {
        walking: motion.moving,
        walkPhase: motion.phase,
        dirX: motion.dirX,
        dirY: motion.dirY,
      }),
    };
  }

  private itemEntity(item: RoomItem): SceneEntity {
    return {
      depth: item.x + item.y + (item.depth_offset ?? Math.max(0.35, (item.width + item.height) * 0.25)),
      draw: () => this.drawItemSprite(item),
    };
  }

  private drawSceneEntities() {
    const entities: SceneEntity[] = [];
    for (const item of this.state.items) {
      if ((item.layer ?? "object") === "floor") continue;
      entities.push(this.itemEntity(item));
    }
    for (const member of this.state.members.values()) entities.push(this.memberEntity(member));
    entities.sort((a, b) => a.depth - b.depth);
    for (const entity of entities) entity.draw();
  }

  private roomCacheFingerprint() {
    return JSON.stringify({
      w: this.canvas.clientWidth,
      h: this.canvas.clientHeight,
      tileW: this.tileW,
      tileH: this.tileH,
      ox: this.ox,
      oy: this.oy,
      wallHeight: this.wallHeight,
      layout: this.state.layout,
    });
  }

  private drawRoomBaseCached() {
    const key = this.roomCacheFingerprint();
    if (!this.roomCache || this.roomCacheKey !== key) {
      const cache = document.createElement("canvas");
      cache.width = Math.max(1, this.canvas.clientWidth);
      cache.height = Math.max(1, this.canvas.clientHeight);
      const cacheCtx = cache.getContext("2d")!;
      cacheCtx.imageSmoothingEnabled = true;
      const oldCtx = this.ctx;
      this.ctx = cacheCtx;
      this.drawRoomBase();
      this.drawFrontEdge();
      this.ctx = oldCtx;
      this.roomCache = cache;
      this.roomCacheKey = key;
    }

    this.ctx.drawImage(this.roomCache, 0, 0, this.canvas.clientWidth, this.canvas.clientHeight);
  }

  private draw = () => {
    this.drawRoomBaseCached();
    this.drawFloorItems();
    this.drawHoverTile();
    this.drawSceneEntities();
    this.state.bubbles = this.state.bubbles.filter(bubble => bubble.until > Date.now() && this.state.members.has(bubble.memberId));
    drawMessageBubbles({
      ctx: this.ctx,
      bubbles: this.state.bubbles,
      members: this.state.members,
      drawn: this.state.drawn,
      project: (x, y) => this.tileToScreen(x, y),
      tileH: this.tileH,
      canvasWidth: this.canvas.clientWidth,
    });
    requestAnimationFrame(this.draw);
  };
}
