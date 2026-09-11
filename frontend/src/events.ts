import { App } from "./app";
import type { Feature } from "./features";
import { isMember, isRoomItem, isSpace } from "./guards";
import type { Message, SpaceLayoutOption } from "./types";
import { updateControls } from "./ui/controls";
import { normalizeLayout } from "./game/worldLayout";
import { renderMembers } from "./ui/members";
import { renderSpaces } from "./ui/spaces";

function normalizeLayoutOptions(value: unknown): SpaceLayoutOption[] | null {
  if (!Array.isArray(value)) return null;
  const layouts: SpaceLayoutOption[] = [];
  for (const item of value) {
    const layout = item as { id?: unknown; name?: unknown; width?: unknown; height?: unknown };
    if (!layout || typeof layout.id !== "string") continue;
    layouts.push({
      id: layout.id,
      name: typeof layout.name === "string" && layout.name.trim() ? layout.name : layout.id,
      width: typeof layout.width === "number" ? layout.width : undefined,
      height: typeof layout.height === "number" ? layout.height : undefined,
    });
  }
  return layouts;
}

function refreshUi(app: App, features: Feature[]) {
  renderSpaces(app);
  renderMembers(app);
  updateControls(app);
  for (const feature of features) feature.refresh?.();
}

export function handleMessage(app: App, features: Feature[], message: Message) {
  for (const feature of features) {
    if (feature.handle?.(message)) {
      refreshUi(app, features);
      return;
    }
  }

  if (message.type === "identity.required") {
    app.el.status.textContent = "login required";
    if (isMember(message.member)) app.state.me = message.member;
  }

  if ((message.type === "identity.assigned" || message.type === "identity.updated") && isMember(message.member)) {
    const hadName = app.state.hasName();
    app.state.me = message.member;
    app.state.saveMember(message.member);
    app.el.status.textContent = app.state.hasName() ? "online" : "login required";
    if (!hadName && app.state.hasName() && !app.state.me.space) app.send({ type: "space.join", space: app.state.currentSpace || "main" });
  }

  if (message.type === "server.ready") app.send({ type: "spaces.list" });

  if (message.type === "spaces.list" || message.type === "space.created" || message.type === "space.updated") {
    if (Array.isArray(message.spaces)) app.state.spaces = message.spaces.filter(isSpace);
    const layouts = normalizeLayoutOptions(message.layouts);
    if (layouts) app.state.availableLayouts = layouts;
  }

  if (message.type === "space.created" && typeof message.space === "string") app.send({ type: "space.join", space: message.space });

  if (message.type === "space.updated") {
    if (isSpace(message.current_space)) app.state.currentSpaceInfo = message.current_space;
  }

  if (message.type === "space.joined") {
    app.state.currentSpace = String(message.space ?? "main");
    app.state.currentSpaceInfo = isSpace(message.current_space) ? message.current_space : null;
    app.state.layout = normalizeLayout(message.layout);
    app.state.clearSpaceView();
    app.state.canBuild = message.can_build === true;
    if (Array.isArray(message.items)) app.state.items = message.items.filter(isRoomItem);
    window.requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));

    if (Array.isArray(message.members)) for (const member of message.members) if (isMember(member)) app.state.saveMember(member);
    if (isMember(message.member)) {
      app.state.me = message.member;
      app.state.saveMember(message.member);
    }

    app.send({ type: "spaces.list" });
    app.send({ type: "inventory.list" });
  }

  if (message.type === "position.path" && isMember(message.member)) {
    const path = Array.isArray(message.path)
      ? message.path
          .filter(point => point && typeof point.x === "number" && typeof point.y === "number")
          .map(point => ({ x: Math.trunc(point.x), y: Math.trunc(point.y) }))
      : [];
    app.state.saveMember(message.member);
    if (path.length > 0) app.state.setRoute(message.member.id, path);
  }

  if (message.type === "position.accepted" && isMember(message.member)) {
    app.state.saveMember(message.member);
  }

  if (message.type === "member.joined" || message.type === "member.updated" || message.type === "position.updated") {
    if (isMember(message.member)) app.state.saveMember(message.member);
  }

  if (message.type === "member.left" && isMember(message.member)) app.state.removeMember(message.member.id);

  if (message.type === "space.members") {
    app.state.members.clear();
    app.state.drawn.clear();
    if (Array.isArray(message.members)) for (const member of message.members) if (isMember(member)) app.state.saveMember(member);
  }

  if (message.type === "message.created" && isMember(message.member)) {
    app.state.saveMember(message.member);
    const text = String(message.message ?? "").slice(0, 160);
    const now = Date.now();
    app.state.bubbles.push({ id: app.state.bubbleId++, memberId: message.member.id, text, created: now, until: now + 6800 });
    app.addChat(text);
  }

  if (message.type === "position.rejected") {
    app.state.walkQueue = [];
    app.state.walking = false;
    if (app.state.me?.id) app.state.routes.delete(app.state.me.id);
    app.send({ type: "space.members" });
  }

  if (message.type === "error") app.addChat(String(message.message ?? "error"));

  refreshUi(app, features);
}
