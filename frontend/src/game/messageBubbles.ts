import type { Bubble, Member, Point } from "../types";

type BubbleBox = { x: number; y: number; w: number; h: number };

type BubbleRenderInput = {
  ctx: CanvasRenderingContext2D;
  bubbles: Bubble[];
  members: Map<string, Member>;
  drawn: Map<string, Point>;
  project: (x: number, y: number) => { x: number; y: number };
  tileH: number;
  canvasWidth: number;
};

function roundedRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function boxFor(ctx: CanvasRenderingContext2D, text: string, x: number, y: number, canvasWidth: number): BubbleBox {
  text = text.slice(0, 52);
  ctx.font = "13px Verdana, Arial, sans-serif";
  const w = Math.min(280, Math.max(62, ctx.measureText(text).width + 22));
  return {
    x: Math.max(8, Math.min(canvasWidth - w - 8, x - w / 2)),
    y: Math.max(8, y),
    w,
    h: 28,
  };
}

function overlaps(a: BubbleBox, b: BubbleBox) {
  return a.x < b.x + b.w + 6 && a.x + a.w + 6 > b.x && a.y < b.y + b.h + 8 && a.y + a.h + 8 > b.y;
}

function drawBubble(ctx: CanvasRenderingContext2D, text: string, box: BubbleBox, alpha: number) {
  text = text.slice(0, 52);
  ctx.save();
  ctx.globalAlpha = alpha;

  ctx.fillStyle = "rgba(0,0,0,.28)";
  roundedRect(ctx, box.x + 2, box.y + 3, box.w, box.h, 9);
  ctx.fill();

  ctx.fillStyle = "#fff7e7";
  roundedRect(ctx, box.x, box.y, box.w, box.h, 9);
  ctx.fill();
  ctx.strokeStyle = "#344052";
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.fillStyle = "#fff7e7";
  ctx.beginPath();
  ctx.moveTo(box.x + box.w / 2 - 6, box.y + box.h - 1);
  ctx.lineTo(box.x + box.w / 2 + 6, box.y + box.h - 1);
  ctx.lineTo(box.x + box.w / 2, box.y + box.h + 8);
  ctx.closePath();
  ctx.fill();
  ctx.strokeStyle = "#344052";
  ctx.stroke();

  ctx.font = "13px Verdana, Arial, sans-serif";
  ctx.fillStyle = "#182233";
  ctx.textAlign = "center";
  ctx.fillText(text, box.x + box.w / 2, box.y + 18);
  ctx.restore();
}

export function drawMessageBubbles(input: BubbleRenderInput) {
  const now = Date.now();
  const active = input.bubbles
    .filter(bubble => bubble.until > now && input.members.has(bubble.memberId))
    .sort((a, b) => b.created - a.created);
  const placed: BubbleBox[] = [];

  for (const bubble of active) {
    const member = input.members.get(bubble.memberId);
    if (!member) continue;

    const point = input.drawn.get(member.id) ?? { x: member.x, y: member.y };
    const anchor = input.project(point.x, point.y);
    const age = (now - bubble.created) / 1000;
    const alpha = Math.min(1, Math.max(0.18, (bubble.until - now) / 900));
    let box = boxFor(input.ctx, bubble.text, anchor.x, anchor.y - input.tileH * 3.8 - age * 10, input.canvasWidth);

    while (placed.some(other => overlaps(box, other))) {
      box = { ...box, y: box.y - 34 };
      if (box.y <= 8) break;
    }

    placed.push(box);
    drawBubble(input.ctx, bubble.text, box, alpha);
  }
}
