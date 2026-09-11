import uuid
from datetime import datetime, timezone

from atrium.command import Command as BaseCommand
from atrium.database import mongo
from atrium.models.item_catalog import catalog_item


class Command(BaseCommand):
    type = "item.place"

    async def run(self, app, client, message: dict) -> None:
        if not client.space:
            await app.send(client, "error", message="join a space first")
            return
        if not app.can_build(client):
            await app.send(client, "error", message="only the owner can build here")
            return

        item = catalog_item(message.get("item_id"))
        if not item:
            await app.send(client, "error", message="unknown item")
            return

        x = message.get("x")
        y = message.get("y")
        if not isinstance(x, int) or not isinstance(y, int):
            await app.send(client, "error", message="x and y required")
            return
        if not await app.item_position_is_open(client.space, item, x, y):
            await app.send(client, "error", message="item does not fit there")
            return

        doc = {
            "id": str(uuid.uuid4()),
            "space_id": client.space,
            "item_id": item["id"],
            "x": x,
            "y": y,
            "rotation": int(message.get("rotation", 0)) if isinstance(message.get("rotation"), int) else 0,
            "owner_id": client.id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        await mongo.collection("space_items").insert_one(doc)
        view = app.item_view(doc)

        await app.publish(client.space, "item.placed", space=client.space, item=view)
