"""Small async-compatible SQLite document store for Atrium's existing commands.

This intentionally supports only the Mongo-shaped operations used by Atrium.
Data lives outside deployed releases. SQLite is the authoritative store.
"""
import asyncio
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

TABLES = frozenset(("users", "spaces", "space_items"))
DuplicateKeyError = sqlite3.IntegrityError


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"unsupported SQLite document field: {type(value)!r}")


def _matches(document, query):
    return all(document.get(k) == v for k, v in query.items())


class Cursor:
    def __init__(self, collection, query):
        self.collection = collection
        self.query = query
        self.order = []

    def sort(self, fields):
        self.order = fields
        return self

    async def _iterate(self):
        docs = await self.collection._all(self.query)
        # Stable sorts from last key to first, like Mongo's compound sort.
        for field, direction in reversed(self.order):
            docs.sort(key=lambda d: (d.get(field) is None, d.get(field) or ""),
                      reverse=direction < 0)
        for doc in docs:
            yield doc

    def __aiter__(self):
        return self._iterate()


class Collection:
    def __init__(self, store, name):
        self.store = store
        if name not in TABLES:
            raise ValueError(f"invalid collection {name!r}")
        self.name = name

    async def create_index(self, field, unique=False):
        # Indexed unique usernames prevent duplicates across concurrent logins.
        if self.name == "users" and field == "name_lower" and unique:
            async with self.store.lock:
                self.store.conn.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS users_name_lower "
                    "ON users(json_extract(doc, '$.name_lower'))"
                )
        # IDs are unique by PRIMARY KEY. Other data is small in this beta.

    async def _all(self, query):
        async with self.store.lock:
            rows = self.store.conn.execute(
                f"SELECT doc FROM {self.name}"
            ).fetchall()
        return [doc for row in rows
                if _matches((doc := json.loads(row[0])), query)]

    def _one_unlocked(self, query):
        for (raw,) in self.store.conn.execute(f"SELECT doc FROM {self.name}"):
            doc = json.loads(raw)
            if _matches(doc, query):
                return doc
        return None

    def find(self, query):
        return Cursor(self, query)

    async def find_one(self, query):
        async with self.store.lock:
            return self._one_unlocked(query)

    def _save_unlocked(self, doc, insert=False):
        key = doc.get("id")
        if not isinstance(key, str) or not key:
            raise ValueError(f"{self.name} document requires a string id")
        raw = json.dumps(doc, default=_json_default, separators=(",", ":"))
        if insert:
            self.store.conn.execute(
                f"INSERT INTO {self.name} (id, doc) VALUES (?, ?)", (key, raw)
            )
        else:
            self.store.conn.execute(
                f"UPDATE {self.name} SET doc=? WHERE id=?", (raw, key)
            )

    async def insert_one(self, doc):
        async with self.store.lock:
            with self.store.conn:
                self._save_unlocked(doc, insert=True)
        return SimpleNamespace(inserted_id=doc["id"])

    async def update_one(self, query, update, upsert=False):
        async with self.store.lock:
            with self.store.conn:
                doc = self._one_unlocked(query)
                if doc is None:
                    if not upsert:
                        return SimpleNamespace(matched_count=0, modified_count=0)
                    doc = dict(query)
                    doc.update(update.get("$setOnInsert", {}))
                    doc.update(update.get("$set", {}))
                    self._save_unlocked(doc, insert=True)
                    return SimpleNamespace(matched_count=0, modified_count=0,
                                           upserted_id=doc["id"])
                doc.update(update.get("$set", {}))
                self._save_unlocked(doc)
                return SimpleNamespace(matched_count=1, modified_count=1)

    async def find_one_and_update(self, query, update, return_document=True):
        async with self.store.lock:
            with self.store.conn:
                doc = self._one_unlocked(query)
                if doc is None:
                    return None
                doc.update(update.get("$set", {}))
                self._save_unlocked(doc)
                return doc

    async def _delete(self, query, many):
        async with self.store.lock:
            with self.store.conn:
                docs = [json.loads(raw) for (raw,) in
                        self.store.conn.execute(f"SELECT doc FROM {self.name}")]
                ids = [doc["id"] for doc in docs if _matches(doc, query)]
                if not many:
                    ids = ids[:1]
                for key in ids:
                    self.store.conn.execute(
                        f"DELETE FROM {self.name} WHERE id=?", (key,)
                    )
                return SimpleNamespace(deleted_count=len(ids))

    async def delete_one(self, query):
        return await self._delete(query, False)

    async def delete_many(self, query):
        return await self._delete(query, True)


class SQLiteStore:
    def __init__(self, path=None):
        self.path = path or os.environ.get(
            "ATRIUM_DB_PATH", "/var/lib/atrium/atrium.sqlite3"
        )
        self.conn = None
        self.lock = asyncio.Lock()

    async def connect(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, timeout=5, isolation_level="DEFERRED")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        for table in TABLES:
            self.conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table} "
                "(id TEXT PRIMARY KEY, doc TEXT NOT NULL)"
            )
        self.conn.commit()

    async def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def collection(self, name):
        if self.conn is None:
            raise RuntimeError("SQLite is not connected")
        return Collection(self, name)


db = SQLiteStore()
