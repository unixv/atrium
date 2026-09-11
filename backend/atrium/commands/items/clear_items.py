from atrium.command import Command as BaseCommand
from atrium.database import mongo


class Command(BaseCommand):
    type = "items.clear"

    async def run(self, app, client, message: dict) -> None:
        if not client.space:
            await app.send(client, "error", message="join a space first")
            return
        if not app.can_build(client):
            await app.send(client, "error", message="only the owner can build here")
            return

        await mongo.collection("space_items").delete_many({"space_id": client.space})
        await app.publish(client.space, "items.cleared", space=client.space)
