from atrium.command import Command as BaseCommand
from atrium.database import mongo


class Command(BaseCommand):
    type = "item.use"

    async def run(self, app, client, message: dict) -> None:
        if not client.space:
            await app.send(client, "error", message="join a space first")
            return

        item_id = message.get("id")
        if not isinstance(item_id, str):
            await app.send(client, "error", message="item id required")
            return

        doc = await mongo.collection("space_items").find_one({"id": item_id, "space_id": client.space})
        if not doc:
            await app.send(client, "error", message="item not found")
            return

        item = app.item_view(doc)
        if not item or not item.get("can_sit"):
            await app.send(client, "error", message="item cannot be used")
            return

        seat = item.get("seat") if isinstance(item.get("seat"), dict) else {"x": 0, "y": 0}
        seat_x = int(item["x"]) + int(seat.get("x", 0))
        seat_y = int(item["y"]) + int(seat.get("y", 0))
        layout = app.layout_for_space(client.space)
        if not (0 <= seat_x < int(layout.get("width", 0)) and 0 <= seat_y < int(layout.get("height", 0))):
            await app.send(client, "error", message="seat is out of bounds")
            return

        client.x = seat_x
        client.y = seat_y
        client.posture = "sitting"
        client.sitting_item_id = item_id
        client.facing = "south"
        await app.publish(client.space, "member.updated", space=client.space, member=client.view())
