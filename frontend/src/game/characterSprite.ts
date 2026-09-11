import type { Avatar, Member } from "../types";

type DrawOptions = {
  walking?: boolean;
  walkPhase?: number;
  dirX?: number;
  dirY?: number;
};

const DEFAULT_AVATAR: Required<Avatar> = {
  avatar_preset: "spiky_red",
  skin_color: "#c58455",
  hair_style: "spiky",
  hair_color: "#1b1717",
  shirt_style: "hoodie",
  shirt_color: "#b83232",
  pants_style: "straight",
  pants_color: "#2e3742",
  shoe_style: "sneakers",
  shoe_color: "#f0f0f0",
};

type NormalAvatar = Required<Avatar>;

type Facing = "south" | "north" | "east" | "west";

type PartRect = [number, number, number, number];

type BodyProfile = {
  torsoW: number;
  shoulderW: number;
  headW: number;
  headH: number;
};

const BODY_PROFILES: Record<string, BodyProfile> = {
  spiky_red: { torsoW: 15, shoulderW: 19, headW: 15, headH: 16 },
  pony_black: { torsoW: 14, shoulderW: 18, headW: 14, headH: 16 },
  messy_blue: { torsoW: 15, shoulderW: 19, headW: 15, headH: 16 },
  mohawk_skull: { torsoW: 15, shoulderW: 19, headW: 15, headH: 16 },
  hood_green: { torsoW: 16, shoulderW: 20, headW: 15, headH: 16 },
  blonde_pink: { torsoW: 14, shoulderW: 18, headW: 14, headH: 16 },
  curly_coat: { torsoW: 16, shoulderW: 20, headW: 15, headH: 16 },
  blue_bob: { torsoW: 14, shoulderW: 18, headW: 14, headH: 16 },
};

function avatar(value?: Avatar): NormalAvatar {
  return { ...DEFAULT_AVATAR, ...(value ?? {}) };
}

function memberAvatar(memberOrAvatar?: Member | Avatar): NormalAvatar {
  if (memberOrAvatar && "id" in memberOrAvatar) return avatar(memberOrAvatar.avatar);
  return avatar(memberOrAvatar);
}

function hexToRgb(hex: string) {
  const safe = /^#[0-9a-f]{6}$/i.test(hex) ? hex : "#777777";
  return {
    r: parseInt(safe.slice(1, 3), 16),
    g: parseInt(safe.slice(3, 5), 16),
    b: parseInt(safe.slice(5, 7), 16),
  };
}

function rgbToHex(r: number, g: number, b: number) {
  const c = (value: number) => Math.max(0, Math.min(255, Math.round(value))).toString(16).padStart(2, "0");
  return `#${c(r)}${c(g)}${c(b)}`;
}

function shade(hex: string, amount: number) {
  const { r, g, b } = hexToRgb(hex);
  return rgbToHex(r + amount, g + amount, b + amount);
}

function fill(ctx: CanvasRenderingContext2D, color: string, rect: PartRect) {
  ctx.fillStyle = color;
  ctx.fillRect(...rect);
}

function strokeRect(ctx: CanvasRenderingContext2D, rect: PartRect) {
  ctx.strokeStyle = "#0b0d10";
  ctx.lineWidth = 1;
  ctx.strokeRect(rect[0] + 0.5, rect[1] + 0.5, rect[2] - 1, rect[3] - 1);
}

function box(ctx: CanvasRenderingContext2D, color: string, rect: PartRect, shadeAmount = -28) {
  fill(ctx, shade(color, shadeAmount), [rect[0] + 1, rect[1] + 1, rect[2], rect[3]]);
  fill(ctx, color, rect);
  fill(ctx, shade(color, 28), [rect[0] + 1, rect[1] + 1, Math.max(1, rect[2] - 4), 2]);
  strokeRect(ctx, rect);
}

function polygon(ctx: CanvasRenderingContext2D, color: string, points: Array<[number, number]>) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(points[0][0], points[0][1]);
  for (const point of points.slice(1)) ctx.lineTo(point[0], point[1]);
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = "#0b0d10";
  ctx.lineWidth = 1;
  ctx.stroke();
}

function faceDirection(options: DrawOptions): Facing {
  const dx = options.dirX ?? 0;
  const dy = options.dirY ?? 1;
  if (Math.abs(dx) > Math.abs(dy)) return dx >= 0 ? "east" : "west";
  return dy < 0 ? "north" : "south";
}

function profile(a: NormalAvatar): BodyProfile {
  return BODY_PROFILES[a.avatar_preset] ?? BODY_PROFILES.spiky_red;
}

function drawHair(ctx: CanvasRenderingContext2D, a: NormalAvatar, cx: number, top: number, facing: Facing) {
  const color = a.hair_color;
  const dark = shade(color, -36);
  const light = shade(color, 30);
  const style = a.hair_style;

  if (style === "buzz") {
    box(ctx, color, [cx - 7, top + 1, 14, 5]);
    return;
  }

  if (style === "bob") {
    box(ctx, color, [cx - 9, top + 1, 18, 14]);
    fill(ctx, a.skin_color, [cx - 6, top + 8, 12, 9]);
    strokeRect(ctx, [cx - 6, top + 8, 12, 9]);
    fill(ctx, light, [cx - 7, top + 3, 8, 2]);
    return;
  }

  if (style === "curly") {
    for (const [x, y] of [[-8, 3], [-5, 0], [-1, 2], [3, 0], [7, 4], [-7, 8], [6, 9]]) {
      box(ctx, color, [cx + x, top + y, 5, 5], -22);
    }
    return;
  }

  if (style === "spiky") {
    polygon(ctx, dark, [[cx - 9, top + 7], [cx - 6, top - 5], [cx - 2, top + 5]]);
    polygon(ctx, color, [[cx - 5, top + 5], [cx, top - 7], [cx + 4, top + 6]]);
    polygon(ctx, dark, [[cx + 2, top + 6], [cx + 8, top - 3], [cx + 8, top + 10]]);
    fill(ctx, light, [cx - 2, top + 1, 5, 2]);
    return;
  }

  if (style === "side_part") {
    box(ctx, color, [cx - 8, top + 1, 16, 8]);
    polygon(ctx, dark, [[cx + 1, top + 2], [cx + 9, top + 5], [cx + 6, top + 13], [cx + 1, top + 10]]);
    fill(ctx, light, [cx - 5, top + 3, 7, 2]);
    return;
  }

  // short
  box(ctx, color, [cx - 8, top + 1, 16, 7]);
  fill(ctx, dark, [cx - 8, top + 7, 4, 4]);
  if (facing === "west") fill(ctx, dark, [cx - 9, top + 8, 3, 5]);
  if (facing === "east") fill(ctx, dark, [cx + 6, top + 8, 3, 5]);
}

function drawEyes(ctx: CanvasRenderingContext2D, cx: number, y: number, facing: Facing) {
  if (facing === "north") return;
  const offset = facing === "east" ? 2 : facing === "west" ? -2 : 0;
  fill(ctx, "#ffffff", [cx - 5 + offset, y, 3, 4]);
  fill(ctx, "#ffffff", [cx + 3 + offset, y, 3, 4]);
  fill(ctx, "#111111", [cx - 4 + offset, y + 1, 1, 2]);
  fill(ctx, "#111111", [cx + 4 + offset, y + 1, 1, 2]);
  fill(ctx, "#6e3d2b", [cx - 1 + offset, y + 8, 4, 1]);
}

function drawHead(ctx: CanvasRenderingContext2D, a: NormalAvatar, cx: number, top: number, facing: Facing) {
  const p = profile(a);
  const w = p.headW;
  const h = p.headH;
  const side = facing === "east" ? 2 : facing === "west" ? -2 : 0;
  box(ctx, a.skin_color, [cx - Math.floor(w / 2) + side, top + 7, w, h], -18);
  fill(ctx, shade(a.skin_color, 28), [cx - Math.floor(w / 2) + side + 2, top + 9, 5, 2]);
  drawEyes(ctx, cx + side, top + 16, facing);
  drawHair(ctx, a, cx + side, top, facing);
}

function drawBody(ctx: CanvasRenderingContext2D, a: NormalAvatar, cx: number, top: number, facing: Facing, walking: boolean, phase: number, sitting: boolean) {
  const p = profile(a);
  const torsoH = sitting ? 15 : 20;
  const torsoTop = top + 27;
  const legTop = torsoTop + torsoH - 1;
  const bob = walking && !sitting ? Math.sin(phase * Math.PI * 2) : 0;
  const legLift = walking && !sitting ? Math.round(Math.sin(phase * Math.PI * 2) * 2) : 0;

  const shirt = a.shirt_color;
  const pants = a.pants_color;
  const shoes = a.shoe_color;

  // arms behind/side
  box(ctx, a.skin_color, [cx - p.shoulderW / 2 - 3, torsoTop + 4 + bob, 4, 13], -18);
  box(ctx, a.skin_color, [cx + p.shoulderW / 2 - 1, torsoTop + 4 - bob, 4, 13], -18);

  // top
  if (a.shirt_style === "hoodie") {
    box(ctx, shirt, [cx - p.torsoW / 2 - 1, torsoTop, p.torsoW + 2, torsoH + 2]);
    fill(ctx, shade(shirt, 24), [cx - 3, torsoTop + 3, 6, 2]);
    fill(ctx, "rgba(255,255,255,.55)", [cx - 2, torsoTop + 5, 1, 7]);
    fill(ctx, "rgba(255,255,255,.55)", [cx + 2, torsoTop + 5, 1, 7]);
  } else if (a.shirt_style === "jacket") {
    box(ctx, shade(shirt, -18), [cx - p.torsoW / 2 - 2, torsoTop, p.torsoW + 4, torsoH + 2]);
    box(ctx, "#f3f0de", [cx - 3, torsoTop + 2, 6, torsoH - 1], -12);
  } else if (a.shirt_style === "stripe") {
    box(ctx, shirt, [cx - p.torsoW / 2, torsoTop, p.torsoW, torsoH + 1]);
    for (let y = torsoTop + 4; y < torsoTop + torsoH; y += 5) fill(ctx, shade(shirt, 38), [cx - p.torsoW / 2 + 1, y, p.torsoW - 2, 2]);
  } else {
    box(ctx, shirt, [cx - p.torsoW / 2, torsoTop, p.torsoW, torsoH + 1]);
  }

  if (sitting) {
    box(ctx, pants, [cx - 9, legTop + 3, 8, 9], -26);
    box(ctx, pants, [cx + 1, legTop + 3, 8, 9], -26);
    box(ctx, shoes, [cx - 11, legTop + 11, 10, 4], -20);
    box(ctx, shoes, [cx + 1, legTop + 11, 10, 4], -20);
    return;
  }

  const pantsH = a.pants_style === "shorts" ? 10 : 17;
  box(ctx, pants, [cx - 8, legTop, 7, pantsH + legLift], -24);
  box(ctx, pants, [cx + 1, legTop, 7, pantsH - legLift], -24);
  if (a.pants_style === "cuffed") {
    fill(ctx, shade(pants, 28), [cx - 8, legTop + pantsH - 2 + legLift, 7, 2]);
    fill(ctx, shade(pants, 28), [cx + 1, legTop + pantsH - 2 - legLift, 7, 2]);
  }

  const shoeY = legTop + pantsH + 1;
  const shoeColor = a.shoe_style === "loafers" ? shade(shoes, -18) : shoes;
  box(ctx, shoeColor, [cx - 10, shoeY + legLift, 10, 5], -20);
  box(ctx, shoeColor, [cx + 1, shoeY - legLift, 10, 5], -20);
  if (a.shoe_style === "sneakers") {
    fill(ctx, "#ffffff", [cx - 8, shoeY + 1 + legLift, 7, 2]);
    fill(ctx, "#ffffff", [cx + 3, shoeY + 1 - legLift, 7, 2]);
  }
}

function drawGeneratedAvatar(ctx: CanvasRenderingContext2D, a: NormalAvatar, x: number, y: number, scale: number, facing: Facing, options: DrawOptions, sitting: boolean) {
  const off = document.createElement("canvas");
  off.width = 48;
  off.height = 76;
  const g = off.getContext("2d")!;
  g.imageSmoothingEnabled = false;
  const cx = 24;
  const top = sitting ? 12 : 7;

  drawBody(g, a, cx, top, facing, options.walking === true, options.walkPhase ?? 0, sitting);
  drawHead(g, a, cx, top, facing);

  ctx.save();
  ctx.imageSmoothingEnabled = false;
  if (facing === "west") {
    ctx.translate(x, y);
    ctx.scale(-1, 1);
    ctx.drawImage(off, -24 * scale, -71 * scale, 48 * scale, 76 * scale);
  } else {
    ctx.drawImage(off, x - 24 * scale, y - 71 * scale, 48 * scale, 76 * scale);
  }
  ctx.restore();
}

function drawFootShadow(ctx: CanvasRenderingContext2D, screenX: number, screenY: number, scale: number, mine: boolean, walking: boolean, sitting: boolean) {
  ctx.save();
  ctx.fillStyle = mine ? "rgba(118, 225, 255, .16)" : `rgba(0,0,0,${walking ? .22 : .17})`;
  ctx.beginPath();
  ctx.ellipse(screenX, screenY, (sitting ? 15 : 13) * scale, (sitting ? 5 : 4.5) * scale, 0, 0, Math.PI * 2);
  ctx.fill();
  if (mine) {
    ctx.strokeStyle = "rgba(190, 245, 255, .58)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.ellipse(screenX, screenY, 17 * scale, 6 * scale, 0, 0, Math.PI * 2);
    ctx.stroke();
  }
  ctx.restore();
}

export function drawCharacter(
  ctx: CanvasRenderingContext2D,
  member: Member,
  screenX: number,
  screenY: number,
  scale: number,
  mine: boolean,
  options: DrawOptions = {},
) {
  const a = memberAvatar(member);
  const facing = (member.facing as Facing | undefined) ?? faceDirection(options);
  const sitting = member.posture === "sitting";
  const bob = options.walking && !sitting ? Math.sin((options.walkPhase ?? 0) * Math.PI * 2) * 1.5 * scale : 0;
  drawFootShadow(ctx, screenX, screenY, scale, mine, options.walking === true, sitting);
  drawGeneratedAvatar(ctx, a, screenX, screenY + bob, scale, facing, options, sitting);
}

export function drawAvatarPreview(canvas: HTMLCanvasElement, value?: Avatar) {
  const ctx = canvas.getContext("2d")!;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const bg = ctx.createRadialGradient(canvas.width / 2, canvas.height * .65, 12, canvas.width / 2, canvas.height * .65, 90);
  bg.addColorStop(0, "rgba(130,220,255,.18)");
  bg.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  drawFootShadow(ctx, canvas.width / 2, canvas.height * .80, 2.3, true, false, false);
  drawGeneratedAvatar(ctx, avatar(value), canvas.width / 2, canvas.height * .80, 2.25, "south", {}, false);
}
