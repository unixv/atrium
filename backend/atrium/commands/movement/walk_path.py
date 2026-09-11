from atrium.command import Command as BaseCommand


class Command(BaseCommand):
    type = "position.walk"

    async def run(self, app, client, message: dict) -> None:
        if not client.space:
            await app.send(client, "error", message="join a space first")
            return

        raw_path = message.get("path")
        if not isinstance(raw_path, list) or not raw_path:
            await app.send(client, "error", message="path required")
            return
        if len(raw_path) > 96:
            await app.send(client, "error", message="path too long")
            return

        path: list[dict[str, int]] = []
        last_x: int | None = None
        last_y: int | None = None

        for raw_point in raw_path:
            if not isinstance(raw_point, dict):
                await app.send(client, "position.rejected", x=client.x, y=client.y)
                return

            x = raw_point.get("x")
            y = raw_point.get("y")
            if not isinstance(x, int) or not isinstance(y, int):
                await app.send(client, "position.rejected", x=client.x, y=client.y)
                return

            if last_x is not None and last_y is not None:
                dx = x - last_x
                dy = y - last_y
                if abs(dx) > 1 or abs(dy) > 1 or (dx == 0 and dy == 0):
                    await app.send(client, "position.rejected", x=client.x, y=client.y)
                    return

                if dx != 0 and dy != 0:
                    # Prevent diagonal corner cutting on the authoritative side too.
                    if not await app.open_tile_for_space(client.space, last_x + dx, last_y):
                        await app.send(client, "position.rejected", x=client.x, y=client.y)
                        return
                    if not await app.open_tile_for_space(client.space, last_x, last_y + dy):
                        await app.send(client, "position.rejected", x=client.x, y=client.y)
                        return

            if not await app.open_tile_for_space(client.space, x, y):
                await app.send(client, "position.rejected", x=client.x, y=client.y)
                return

            path.append({"x": x, "y": y})
            last_x = x
            last_y = y

        if path:
            previous_x = client.x
            previous_y = client.y
            final_x = path[-1]["x"]
            final_y = path[-1]["y"]
            dx = final_x - previous_x
            dy = final_y - previous_y
            if abs(dx) >= abs(dy) and dx != 0:
                client.facing = "east" if dx > 0 else "west"
            elif dy != 0:
                client.facing = "south" if dy > 0 else "north"
            client.x = final_x
            client.y = final_y
            client.posture = "standing"
            client.sitting_item_id = None
        member = client.view()

        await app.send(client, "position.accepted", space=client.space, member=member)
        await app.publish(client.space, "position.path", exclude=client, space=client.space, member=member, path=path)
