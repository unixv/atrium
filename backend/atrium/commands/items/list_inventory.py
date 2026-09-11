from atrium.command import Command as BaseCommand
from atrium.models.item_catalog import catalog_list


class Command(BaseCommand):
    type = "inventory.list"

    async def run(self, app, client, message: dict) -> None:
        space = client.space
        await app.send(
            client,
            "inventory.list",
            catalog=catalog_list(),
            items=await app.items_for_space(space) if space else [],
            can_build=app.can_build(client) if space else False,
        )
