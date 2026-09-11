from datetime import datetime, timezone

from atrium.command import Command as BaseCommand
from atrium.database import mongo
from atrium.models.avatar import avatar_from_any, normalize_avatar


class Command(BaseCommand):
    type = "avatar.update"

    async def run(self, app, client, message: dict) -> None:
        incoming = message.get("avatar")
        if not isinstance(incoming, dict):
            await app.send(client, "error", message="avatar required")
            return

        merged = client.avatar.view()
        merged.update(incoming)
        normalized = normalize_avatar(merged)
        client.avatar = avatar_from_any(normalized)

        await mongo.collection("users").update_one(
            {"id": client.id},
            {"$set": {"avatar": normalized, "updated_at": datetime.now(timezone.utc)}},
        )

        payload = {"member": client.view()}
        if client.space:
            await app.publish(client.space, "avatar.updated", space=client.space, **payload)
        else:
            await app.send(client, "avatar.updated", **payload)
