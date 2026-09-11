from atrium.auth import AuthError, register_user
from atrium.command import Command as BaseCommand
from atrium.commands.auth._helpers import apply_public_user


class Command(BaseCommand):
    requires_name = False
    type = "auth.register"

    async def run(self, app, client, message: dict) -> None:
        try:
            user, token = await register_user(
                message.get("name"),
                message.get("password"),
                message.get("email"),
            )
        except AuthError as exc:
            await app.send(client, "auth.rejected", message=str(exc))
            return

        apply_public_user(client, user)
        await app.send(client, "auth.accepted", member=client.view(), token=token)
