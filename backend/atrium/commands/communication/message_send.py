from atrium.command import Command as BaseCommand


class Command(BaseCommand):
    type = "message.send"

    async def run(self, app, client, message: dict) -> None:
        if not client.space:
            await app.send(client, "error", message="join a space first")
            return

        text = f"{client.name}: {message.get('message')}"
        if not isinstance(text, str):
            await app.send(client, "error", message="message required")
            return

        text = text.strip()[:500]
        if not text:
            await app.send(client, "error", message="message required")
            return

        await app.publish(client.space, "message.created", space=client.space, member=client.view(), message=text)
