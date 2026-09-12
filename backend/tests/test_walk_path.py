import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from atrium.commands.movement.walk_path import Command


class WalkPathTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = SimpleNamespace(
            space="main", x=4, y=4, facing="south",
            posture="sitting", sitting_item_id="chair",
        )
        self.client.view = lambda: {
            "x": self.client.x, "y": self.client.y,
            "posture": self.client.posture,
        }
        self.app = SimpleNamespace(
            send=AsyncMock(), publish=AsyncMock(),
            open_tile_for_space=AsyncMock(return_value=True),
        )

    async def walk(self, path):
        await Command().run(self.app, self.client, {"path": path})

    async def test_adjacent_path_moves_and_stands(self):
        await self.walk([{"x": 5, "y": 4}, {"x": 6, "y": 4}])
        self.assertEqual((self.client.x, self.client.y), (6, 4))
        self.assertEqual(self.client.facing, "east")
        self.assertEqual(self.client.posture, "standing")
        self.assertIsNone(self.client.sitting_item_id)
        self.app.send.assert_awaited_once()
        self.assertEqual(self.app.send.await_args.args[1], "position.accepted")
        self.app.publish.assert_awaited_once()

    async def test_first_waypoint_cannot_teleport(self):
        await self.walk([{"x": 10, "y": 4}, {"x": 11, "y": 4}])
        self.assertEqual((self.client.x, self.client.y), (4, 4))
        self.assertEqual(self.client.posture, "sitting")
        self.app.send.assert_awaited_once_with(
            self.client, "position.rejected", x=4, y=4
        )
        self.app.publish.assert_not_awaited()

    async def test_first_diagonal_cannot_cut_corner(self):
        async def open_tile(space, x, y):
            return (x, y) != (5, 4)

        self.app.open_tile_for_space.side_effect = open_tile
        await self.walk([{"x": 5, "y": 5}])
        self.assertEqual((self.client.x, self.client.y), (4, 4))
        self.app.send.assert_awaited_once_with(
            self.client, "position.rejected", x=4, y=4
        )

    async def test_boolean_coordinate_is_rejected(self):
        await self.walk([{"x": True, "y": 4}])
        self.app.send.assert_awaited_once_with(
            self.client, "position.rejected", x=4, y=4
        )


if __name__ == "__main__":
    unittest.main()
