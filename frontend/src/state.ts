import type { Bubble, CatalogItem, ChatLine, Member, Point, RoomItem, Space, SpaceLayout, SpaceLayoutOption } from "./types";
import { DEFAULT_LAYOUT } from "./game/worldLayout";

export class State {
  members = new Map<string, Member>();
  drawn = new Map<string, Point>();
  bubbles: Bubble[] = [];
  chatLines: ChatLine[] = [];

  spaces: Space[] = [];
  availableLayouts: SpaceLayoutOption[] = [];
  currentSpaceInfo: Space | null = null;
  layout: SpaceLayout = DEFAULT_LAYOUT;

  items: RoomItem[] = [];
  catalog: CatalogItem[] = [];
  canBuild = false;
  buildMode = false;
  selectedItemId: string | null = null;
  buildRemoveMode = false;

  me: Member | null = null;
  currentSpace = "main";
  walkQueue: Point[] = [];
  walking = false;

  // Smooth client-side routes. Members still store their final server-authoritative
  // tile in members/me; routes only control how the renderer travels there.
  routes = new Map<string, Point[]>();
  bubbleId = 1;

  hasName() {
    return Boolean(this.me?.name.trim());
  }

  saveMember(member: Member) {
    if (!this.drawn.has(member.id)) this.drawn.set(member.id, { x: member.x, y: member.y });
    this.members.set(member.id, member);
    if (this.me?.id === member.id) this.me = member;
  }

  removeMember(memberId: string) {
    this.members.delete(memberId);
    this.drawn.delete(memberId);
    this.bubbles = this.bubbles.filter(bubble => bubble.memberId !== memberId);
  }

  clearSpaceView() {
    this.members.clear();
    this.drawn.clear();
    this.bubbles = [];
    this.chatLines.length = 0;
    this.walkQueue = [];
    this.walking = false;
    this.routes.clear();
    this.items = [];
    this.canBuild = false;
    this.buildMode = false;
    this.buildRemoveMode = false;
  }

  itemAt(x: number, y: number) {
    return this.items.find(item => x >= item.x && x < item.x + item.width && y >= item.y && y < item.y + item.height) ?? null;
  }

  itemBlocksTile(x: number, y: number) {
    return this.items.some(item => item.blocks_movement && x >= item.x && x < item.x + item.width && y >= item.y && y < item.y + item.height);
  }

  selectedCatalogItem() {
    return this.catalog.find(item => item.id === this.selectedItemId) ?? null;
  }

  setRoute(memberId: string, path: Point[]) {
    const cleaned = path
      .filter(point => Number.isInteger(point.x) && Number.isInteger(point.y))
      .map(point => ({ x: point.x, y: point.y }));

    if (cleaned.length === 0) {
      this.routes.delete(memberId);
      return;
    }

    this.routes.set(memberId, cleaned);
  }
}

