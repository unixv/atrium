from atrium.command import Command as BaseCommand


class Command(BaseCommand):
    requires_name = False
    type = "help"

    async def run(self, app, client, message: dict) -> None:
        await app.send(client, "help", commands=sorted(app.commands.keys()))
