from atrium.auth import AuthError, create_token, user_from_token
from atrium.command import Command as BaseCommand
from atrium.commands.auth._helpers import apply_public_user


class Command(BaseCommand):
    requires_name = False
    type = "auth.resume"

    async def run(self, app, client, message: dict) -> None:
        try:
            user = await user_from_token(message.get("token"))
        except AuthError as exc:
            await app.send(client, "auth.rejected", message=str(exc))
            return

        apply_public_user(client, user)
        await app.send(client, "auth.accepted", member=client.view(), token=create_token(user))
