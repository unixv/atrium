from atrium.command import Command as BaseCommand
from atrium.database import mongo


class Command(BaseCommand):
    type = "item.remove"

    async def run(self, app, client, message: dict) -> None:
        if not client.space:
            await app.send(client, "error", message="join a space first")
            return
        if not app.can_build(client):
            await app.send(client, "error", message="only the owner can build here")
            return

        item_id = message.get("id")
        if not isinstance(item_id, str):
            await app.send(client, "error", message="item id required")
            return

        result = await mongo.collection("space_items").delete_one({"id": item_id, "space_id": client.space})
        if result.deleted_count < 1:
            await app.send(client, "error", message="item not found")
            return

        await app.publish(client.space, "item.removed", space=client.space, id=item_id)
