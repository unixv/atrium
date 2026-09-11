from atrium.command import Command as BaseCommand
from atrium.world import layout_start


class Command(BaseCommand):
    type = "space.join"

    async def run(self, app, client, message: dict) -> None:
        raw = message.get("space")
        if not isinstance(raw, str):
            await app.send(client, "error", message="space required")
            return

        space = app.clean_space_name(raw)
        if not space:
            await app.send(client, "error", message="invalid space")
            return

        if space not in app.spaces:
            exists = await app.load_space_from_mongo(space)
            if not exists:
                await app.send(client, "error", message="space does not exist")
                return

        if client.space:
            previous = client.space
            app.spaces.get(previous, set()).discard(client)
            await app.publish(previous, "member.left", space=previous, member=client.view())

        client.space = space
        client.x, client.y = layout_start(app.layout_id_for_space(space))
        app.spaces.setdefault(space, set()).add(client)

        await app.send(
            client,
            "space.joined",
            space=space,
            current_space=app.space_view(space),
            can_build=app.can_build(client, space),
            layout=app.layout_for_space(space),
            items=await app.items_for_space(space),
            member=client.view(),
            members=app.members_in_space(space),
        )
        await app.publish(space, "member.joined", space=space, member=client.view(), exclude=client)
