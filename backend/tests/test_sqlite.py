import tempfile
import unittest
from pathlib import Path
from sqlite3 import IntegrityError

from atrium.database.sqlite import SQLiteStore


class SQLiteTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "atrium.sqlite3")
        self.db = SQLiteStore(self.path)
        await self.db.connect()

    async def asyncTearDown(self):
        await self.db.close()
        self.tmp.cleanup()

    async def test_insert_query_and_restart(self):
        users = self.db.collection("users")
        await users.create_index("name_lower", unique=True)
        await users.insert_one({"id": "a", "name_lower": "alice", "avatar": {"shirt": "blue"}})
        self.assertEqual((await users.find_one({"id": "a"}))["avatar"]["shirt"], "blue")
        with self.assertRaises(IntegrityError):
            await users.insert_one({"id": "b", "name_lower": "alice"})
        await self.db.close()
        await self.db.connect()
        self.assertEqual((await self.db.collection("users").find_one(
            {"name_lower": "alice"}))["id"], "a")

    async def test_upsert_updates_and_order(self):
        spaces = self.db.collection("spaces")
        await spaces.update_one({"id": "main"},
            {"$setOnInsert": {"name": "Main", "updated_at": "2026-01-01"}}, upsert=True)
        await spaces.update_one({"id": "main"}, {"$setOnInsert": {"name": "Bad"}}, upsert=True)
        self.assertEqual((await spaces.find_one({"id": "main"}))["name"], "Main")
        changed = await spaces.find_one_and_update(
            {"id": "main"}, {"$set": {"description": "Ready"}})
        self.assertEqual(changed["description"], "Ready")
        items = self.db.collection("space_items")
        await items.insert_one({"id": "1", "space_id": "main", "y": 3, "x": 1})
        await items.insert_one({"id": "2", "space_id": "main", "y": 1, "x": 1})
        ordered = [d["id"] async for d in items.find({"space_id": "main"}).sort(
            [("y", 1), ("x", 1)])]
        self.assertEqual(ordered, ["2", "1"])
        self.assertEqual((await items.delete_one({"id": "2", "space_id": "main"})).deleted_count, 1)
        self.assertEqual((await items.delete_many({"space_id": "main"})).deleted_count, 1)


if __name__ == "__main__":
    unittest.main()
