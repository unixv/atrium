from atrium.client import Client
from atrium.models.avatar import avatar_from_any


def apply_public_user(client: Client, user: dict) -> None:
    # Use the persisted user id as the member id so the same account is stable
    # across reconnects/resumes.
    client.id = user["id"]
    client.name = user["name"]
    client.avatar = avatar_from_any(user.get("avatar"))
