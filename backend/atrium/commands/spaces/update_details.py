from atrium.command import Command as BaseCommand


class Command(BaseCommand):
    type = "space.update"

    async def run(self, app, client, message: dict) -> None:
        if not client.space:
            await app.send(client, "error", message="join a space first")
            return

        if not app.can_build(client):
            await app.send(client, "error", message="only the owner can edit this space")
            return

        name = message.get("name")
        description = message.get("description")
        if not isinstance(name, str):
            name = None
        if not isinstance(description, str):
            description = None

        await app.update_space_details(client.space, name=name, description=description)
        payload = {
            "space": client.space,
            "current_space": app.space_view(client.space),
            "spaces": app.space_list(),
        }
        await app.send(client, "space.updated", **payload)
        await app.publish(client.space, "space.updated", exclude=client, **payload)
