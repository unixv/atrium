from atrium.command import Command as BaseCommand


class Command(BaseCommand):
    requires_name = False
    type = "spaces.list"

    async def run(self, app, client, message: dict) -> None:
        await app.load_spaces_from_mongo()
        await app.send(client, "spaces.list", spaces=app.space_list(), layouts=app.layout_list())
