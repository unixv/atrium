from atrium.command import Command as BaseCommand


class Command(BaseCommand):
    type = "space.members"

    async def run(self, app, client, message: dict) -> None:
        if not client.space:
            await app.send(client, "error", message="join a space first")
            return
        await app.send(client, "space.members", space=client.space, members=app.members_in_space(client.space))
