import asyncio
import base64
import json

from websockets.asyncio.client import connect


def encode(message: dict) -> str:
    return base64.b64encode(json.dumps(message, separators=(",", ":")).encode()).decode()


def decode(data: str) -> dict:
    return json.loads(base64.b64decode(data).decode())


async def main() -> None:
    async with connect("ws://127.0.0.1:8787") as socket:
        for _ in range(2):
            print("<-", decode(await socket.recv()))

        messages = [
            {"type": "identity.set", "name": "andrew"},
            {"type": "spaces.list"},
            {"type": "space.join", "space": "main"},
            {"type": "message.send", "message": "hello from smoke test"},
            {"type": "position.set", "x": 2, "y": 5},
            {"type": "space.members"},
            {"type": "ping"},
        ]

        for message in messages:
            print("->", message)
            await socket.send(encode(message))
            print("<-", decode(await socket.recv()))


if __name__ == "__main__":
    asyncio.run(main())
