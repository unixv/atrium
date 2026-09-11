import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from pymongo import ReturnDocument
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

from atrium.auth import ensure_auth_indexes
from atrium.client import Client
from atrium.database import mongo
from atrium.encoder import Encoder
from atrium.loader import load_commands
from atrium.models.item_catalog import catalog_item
from atrium.world import DEFAULT_LAYOUT_ID, LAYOUTS, layout_view, open_tile


HOST = os.getenv("ATRIUM_HOST", "0.0.0.0")
PORT = int(os.getenv("ATRIUM_PORT", "8787"))
MAX_MESSAGE_SIZE = int(os.getenv("ATRIUM_MAX_MESSAGE_SIZE", "4096"))
LOG_LEVEL = os.getenv("ATRIUM_LOG_LEVEL", "DEBUG").upper()


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.DEBUG),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("atrium")


class Atrium:
    def __init__(self) -> None:
        self.encoder = Encoder()
        self.commands = load_commands()
        self.clients: set[Client] = set()
        self.spaces: dict[str, set[Client]] = {}
        self.space_meta: dict[str, dict[str, Any]] = {}
        log.info("boot commands=%s", sorted(self.commands.keys()))

    async def start(self) -> None:
        log.info("start host=%s port=%s max_message_size=%s", HOST, PORT, MAX_MESSAGE_SIZE)
        await mongo.connect()
        await ensure_auth_indexes()
        await self.ensure_space_indexes()
        await self.ensure_item_indexes()
        await self.load_spaces_from_mongo()
        async with serve(self.connect, HOST, PORT, max_size=MAX_MESSAGE_SIZE):
            log.info("listening url=ws://%s:%s", HOST, PORT)
            await asyncio.Future()

    async def connect(self, socket) -> None:
        client = Client(socket=socket, id=str(uuid.uuid4()))
        self.clients.add(client)
        log.info("connect client_id=%s total_clients=%s", client.id, len(self.clients))

        await self.send(client, "server.ready", name="Atrium")
        await self.send(client, "identity.required", member=client.view(), message="login or register first")

        try:
            async for data in socket:
                await self.receive(client, data)
        except ConnectionClosed as exc:
            log.info("closed client_id=%s code=%s reason=%s", client.id, exc.code, exc.reason)
        except Exception:
            log.exception("connect_failed client_id=%s", client.id)
        finally:
            await self.disconnect(client)

    async def receive(self, client: Client, data) -> None:
        if not isinstance(data, str):
            await self.send(client, "error", message="text messages only")
            return

        try:
            message = self.encoder.decode(data)
        except Exception:
            log.exception("decode_failed client_id=%s raw=%r", client.id, data[:120])
            await self.send(client, "error", message="bad message")
            return

        message_type = message.get("type")
        if not isinstance(message_type, str):
            await self.send(client, "error", message="missing type")
            return

        command = self.commands.get(message_type)
        if not command:
            log.warning("unknown_command client_id=%s type=%s", client.id, message_type)
            await self.send(client, "error", message="unknown type", type=message_type)
            return

        if command.requires_name and not client.name:
            await self.send(client, "identity.required", message="login or register first")
            return

        try:
            await command.run(self, client, message)
        except Exception:
            log.exception("command_failed client_id=%s type=%s message=%s", client.id, message_type, message)
            await self.send(client, "error", message="command failed")

    async def disconnect(self, client: Client) -> None:
        self.clients.discard(client)
        log.info("disconnect client_id=%s name=%s total_clients=%s", client.id, client.name or "unnamed", len(self.clients))

        if client.space:
            space = client.space
            self.spaces.get(space, set()).discard(client)
            await self.publish(space, "member.left", space=space, member=client.view())

    async def send(self, client: Client, message_type: str, **payload) -> None:
        payload["type"] = message_type
        await client.socket.send(self.encoder.encode(payload))

    async def publish(self, target_space: str, message_type: str, exclude: Client | None = None, **payload) -> None:
        for member in list(self.spaces.get(target_space, set())):
            if member is exclude:
                continue
            await self.send(member, message_type, **payload)

    def clean_space_name(self, value: str) -> str | None:
        value = value.strip().lower()[:32]
        if not value:
            return None
        ok = value.replace("-", "").replace("_", "").isalnum()
        return value if ok else None

    def valid_layout_id(self, value: object) -> str:
        return value if isinstance(value, str) and value in LAYOUTS else DEFAULT_LAYOUT_ID

    def space_name(self, space: str) -> str:
        return str(self.space_meta.get(space, {}).get("name") or space)

    def space_description(self, space: str) -> str:
        return str(self.space_meta.get(space, {}).get("description") or "")

    def space_owner_id(self, space: str) -> str | None:
        owner_id = self.space_meta.get(space, {}).get("owner_id")
        return owner_id if isinstance(owner_id, str) else None

    def can_build(self, client: Client, space: str | None = None) -> bool:
        target = space or client.space
        if not target:
            return False
        owner_id = self.space_owner_id(target)
        return owner_id is None or owner_id == client.id

    def layout_id_for_space(self, space: str) -> str:
        return self.valid_layout_id(self.space_meta.get(space, {}).get("layout_id"))

    def layout_for_space(self, space: str) -> dict[str, Any]:
        return layout_view(self.layout_id_for_space(space))

    async def ensure_space_indexes(self) -> None:
        spaces = mongo.collection("spaces")
        await spaces.create_index("id", unique=True)
        await spaces.create_index("owner_id")
        await spaces.create_index("updated_at")

    async def ensure_item_indexes(self) -> None:
        items = mongo.collection("space_items")
        await items.create_index("id", unique=True)
        await items.create_index([("space_id", 1), ("x", 1), ("y", 1)])

    async def ensure_default_space(self) -> None:
        now = datetime.now(timezone.utc)
        await mongo.collection("spaces").update_one(
            {"id": "main"},
            {
                "$setOnInsert": {
                    "id": "main",
                    "name": "Main",
                    "description": "Public starting space.",
                    "layout_id": DEFAULT_LAYOUT_ID,
                    "owner": "system",
                    "owner_id": None,
                    "created_at": now,
                    "updated_at": now,
                }
            },
            upsert=True,
        )

    def normalize_space_doc(self, doc: dict[str, Any]) -> dict[str, Any] | None:
        space_id = self.clean_space_name(str(doc.get("id", "")))
        if not space_id:
            return None

        raw_name = doc.get("name")
        name = raw_name.strip()[:32] if isinstance(raw_name, str) and raw_name.strip() else space_id

        raw_description = doc.get("description")
        description = raw_description.strip()[:180] if isinstance(raw_description, str) else ""

        owner = doc.get("owner") if isinstance(doc.get("owner"), str) else None
        owner_id = doc.get("owner_id") if isinstance(doc.get("owner_id"), str) else None

        return {
            "id": space_id,
            "name": name,
            "description": description,
            "layout_id": self.valid_layout_id(doc.get("layout_id")),
            "owner": owner,
            "owner_id": owner_id,
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }

    def apply_space_doc(self, doc: dict[str, Any]) -> None:
        normalized = self.normalize_space_doc(doc)
        if not normalized:
            return
        self.spaces.setdefault(normalized["id"], set())
        self.space_meta[normalized["id"]] = normalized

    async def load_spaces_from_mongo(self) -> None:
        await self.ensure_default_space()

        seen: set[str] = set()
        async for doc in mongo.collection("spaces").find({}):
            normalized = self.normalize_space_doc(doc)
            if not normalized:
                continue
            self.spaces.setdefault(normalized["id"], set())
            self.space_meta[normalized["id"]] = normalized
            seen.add(normalized["id"])

        for space in list(self.spaces):
            if space in seen or self.spaces.get(space):
                continue
            self.spaces.pop(space, None)
            self.space_meta.pop(space, None)

    async def load_space_from_mongo(self, space: str) -> bool:
        doc = await mongo.collection("spaces").find_one({"id": space})
        if not doc:
            return False
        self.apply_space_doc(doc)
        return True

    async def create_space_in_mongo(
        self,
        space: str,
        name: str,
        description: str,
        layout_id: str,
        owner_id: str | None,
        owner: str | None,
    ) -> bool:
        from pymongo.errors import DuplicateKeyError

        now = datetime.now(timezone.utc)
        doc = {
            "id": space,
            "name": name.strip()[:32],
            "description": description.strip()[:180],
            "layout_id": self.valid_layout_id(layout_id),
            "owner": owner,
            "owner_id": owner_id,
            "created_at": now,
            "updated_at": now,
        }

        try:
            await mongo.collection("spaces").insert_one(doc)
        except DuplicateKeyError:
            return False

        self.apply_space_doc(doc)
        return True

    async def update_space_details(self, space: str, name: str | None = None, description: str | None = None) -> dict[str, Any] | None:
        update: dict[str, Any] = {"updated_at": datetime.now(timezone.utc)}
        if isinstance(name, str) and name.strip():
            update["name"] = name.strip()[:32]
        if isinstance(description, str):
            update["description"] = description.strip()[:180]

        result = await mongo.collection("spaces").find_one_and_update(
            {"id": space},
            {"$set": update},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            self.apply_space_doc(result)
        return result

    def layout_list(self) -> list[dict[str, Any]]:
        return [
            {
                "id": layout_id,
                "name": str(layout.get("name") or layout_id),
                "width": int(layout.get("width", 0)),
                "height": int(layout.get("height", 0)),
            }
            for layout_id, layout in sorted(LAYOUTS.items())
        ]

    def space_view(self, space: str) -> dict[str, Any]:
        meta = self.space_meta.get(space, {"id": space, "name": space, "description": "", "layout_id": DEFAULT_LAYOUT_ID})
        return {
            "id": space,
            "name": str(meta.get("name") or space),
            "description": str(meta.get("description") or ""),
            "owner": meta.get("owner"),
            "owner_id": meta.get("owner_id"),
            "members": len(self.spaces.get(space, set())),
            "layout_id": self.layout_id_for_space(space),
        }

    def space_list(self) -> list[dict[str, Any]]:
        return [self.space_view(space) for space in sorted(self.spaces)]

    def members_in_space(self, space: str) -> list[dict[str, Any]]:
        return [member.view() for member in self.spaces.get(space, set())]

    async def items_for_space(self, space: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        cursor = mongo.collection("space_items").find({"space_id": space}).sort([("y", 1), ("x", 1), ("created_at", 1)])
        async for doc in cursor:
            view = self.item_view(doc)
            if view:
                items.append(view)
        return items

    def item_view(self, doc: dict[str, Any]) -> dict[str, Any] | None:
        catalog = catalog_item(doc.get("item_id"))
        if not catalog:
            return None
        view = {
            "id": doc.get("id"),
            "space_id": doc.get("space_id"),
            "item_id": catalog["id"],
            "name": catalog["name"],
            "sprite": catalog["sprite"],
            "width": catalog["width"],
            "height": catalog["height"],
            "blocks_movement": catalog["blocks_movement"],
            "x": int(doc.get("x", 0)),
            "y": int(doc.get("y", 0)),
            "rotation": int(doc.get("rotation", 0)),
            "owner_id": doc.get("owner_id"),
        }
        for key in (
            "layer",
            "draw_width_tiles",
            "anchor_x",
            "anchor_y",
            "anchor_tile_y",
            "depth_offset",
            "shadow",
            "category",
            "can_sit",
            "seat",
        ):
            if key in catalog:
                view[key] = catalog[key]
        return view

    async def item_blocks_tile(self, space: str, x: int, y: int) -> bool:
        async for doc in mongo.collection("space_items").find({"space_id": space}):
            view = self.item_view(doc)
            if not view or not view["blocks_movement"]:
                continue
            ix, iy = int(view["x"]), int(view["y"])
            iw, ih = int(view["width"]), int(view["height"])
            if ix <= x < ix + iw and iy <= y < iy + ih:
                return True
        return False

    async def open_tile_for_space(self, space: str, x: int, y: int) -> bool:
        if not open_tile(x, y, self.layout_id_for_space(space)):
            return False
        if await self.item_blocks_tile(space, x, y):
            return False
        return True

    async def item_position_is_open(self, space: str, item: dict[str, Any], x: int, y: int) -> bool:
        width = int(item.get("width", 1))
        height = int(item.get("height", 1))
        for ty in range(y, y + height):
            for tx in range(x, x + width):
                if not open_tile(tx, ty, self.layout_id_for_space(space)):
                    return False

        # Keep alpha building predictable: do not stack item bounding boxes yet.
        async for doc in mongo.collection("space_items").find({"space_id": space}):
            existing = self.item_view(doc)
            if not existing:
                continue
            ex, ey = int(existing["x"]), int(existing["y"])
            ew, eh = int(existing["width"]), int(existing["height"])
            overlaps = x < ex + ew and x + width > ex and y < ey + eh and y + height > ey
            if overlaps:
                return False

        return True
