class Command:
    type = ""
    requires_name = True

    async def run(self, app, client, message: dict) -> None:
        raise NotImplementedError
