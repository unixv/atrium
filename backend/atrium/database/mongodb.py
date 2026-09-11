import os
from typing import Any

from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase


class Mongo:
    def __init__(
        self,
        uri: str | None = None,
        database_name: str | None = None,
    ) -> None:
        self.uri = uri or os.getenv(
            "ATRIUM_MONGO_URI",
            "mongodb://atrium:atrium-dev-password@mongo:27017/atrium?authSource=admin",
        )
        self.database_name = database_name or os.getenv("ATRIUM_MONGO_DATABASE", "atrium")
        self.client: AsyncMongoClient[dict[str, Any]] | None = None
        self.db: AsyncDatabase[dict[str, Any]] | None = None

    async def connect(self) -> None:
        self.client = AsyncMongoClient(self.uri)
        self.db = self.client[self.database_name]
        await self.client.admin.command("ping")

    async def close(self) -> None:
        if self.client:
            await self.client.close()

        self.client = None
        self.db = None

    def collection(self, name: str) -> AsyncCollection[dict[str, Any]]:
        if self.db is None:
            raise RuntimeError("Mongo is not connected")

        return self.db[name]


mongo = Mongo()