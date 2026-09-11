from atrium.command import Command as BaseCommand


class Command(BaseCommand):
    type = "space.create"

    async def run(self, app, client, message: dict) -> None:
        name = message.get("space")
        if not isinstance(name, str):
            await app.send(client, "error", message="space required")
            return

        space = app.clean_space_name(name)
        if not space:
            await app.send(client, "error", message="invalid space")
            return

        if space in app.spaces:
            await app.send(client, "error", message="space already exists")
            return

        layout_id = app.valid_layout_id(message.get("layout_id"))
        description = message.get("description")
        if not isinstance(description, str):
            description = ""

        created = await app.create_space_in_mongo(
            space=space,
            name=name,
            description=description,
            layout_id=layout_id,
            owner_id=client.id,
            owner=client.name,
        )
        if not created:
            await app.send(client, "error", message="space already exists")
            return

        await app.send(
            client,
            "space.created",
            space=space,
            current_space=app.space_view(space),
            layout=app.layout_for_space(space),
            layouts=app.layout_list(),
            spaces=app.space_list(),
        )
