from dataclasses import dataclass, field
from typing import Any

from atrium.models.avatar import Avatar


@dataclass(eq=False)
class Client:
    socket: Any
    id: str
    name: str | None = None
    space: str | None = None
    x: int = 0
    y: int = 0
    avatar: Avatar = field(default_factory=Avatar)
    facing: str = "south"
    posture: str = "standing"
    sitting_item_id: str | None = None

    def view(self) -> dict:
        return {
            "id": self.id,
            "name": self.name or "",
            "space": self.space,
            "x": self.x,
            "y": self.y,
            "facing": self.facing,
            "posture": self.posture,
            "sitting_item_id": self.sitting_item_id,
            "avatar": self.avatar.view(),
        }
