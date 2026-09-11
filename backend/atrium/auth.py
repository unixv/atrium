import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from pymongo.errors import DuplicateKeyError

from atrium.database import mongo
from atrium.models.avatar import DEFAULT_AVATAR, normalize_avatar


JWT_SECRET = os.getenv("ATRIUM_JWT_SECRET", "secret")
JWT_ALGORITHM = "HS256"
JWT_TTL_HOURS = int(os.getenv("ATRIUM_JWT_TTL_HOURS", "168"))

NAME_RE = re.compile(r"^(?=.*[a-zA-Z0-9])[a-zA-Z0-9_!.,?]{3,24}$")
EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

DEFAULT_SCOPES = {
    "player:regular",
}


class AuthError(Exception):
    pass


async def ensure_auth_indexes() -> None:
    users = mongo.collection("users")
    await users.create_index("id", unique=True)
    await users.create_index("name_lower", unique=True)


def validate_name(value: Any) -> str:
    if not isinstance(value, str):
        raise AuthError("name required")

    name = value.strip()

    if not NAME_RE.match(name):
        raise AuthError(
            "name must be 3-24 characters, include at least one letter or number, and only use letters, numbers, underscores, !, ., commas, or ?"
        )

    return name


def validate_password(value: Any) -> str:
    if not isinstance(value, str):
        raise AuthError("password required")

    if len(value) < 8:
        raise AuthError("password must be at least 8 characters")

    if len(value.encode("utf-8")) > 72:
        raise AuthError("password is too long")

    return value


def validate_email(value: Any) -> str:
    if not isinstance(value, str):
        raise AuthError("email required")

    email = value.strip()

    if not EMAIL_RE.match(email):
        raise AuthError("invalid email")

    return email


def normalize_scopes(value: Any) -> list[str]:
    if not isinstance(value, list):
        return sorted(DEFAULT_SCOPES)

    scopes = []

    for item in value:
        if isinstance(item, str) and item.strip():
            scopes.append(item.strip())

    return sorted(set(scopes))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def public_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "name": user["name"],
        "avatar": normalize_avatar(user.get("avatar")),
        "scopes": normalize_scopes(user.get("scopes")),
    }


def create_token(user: dict) -> str:
    now = datetime.now(timezone.utc)

    return jwt.encode(
        {
            "sub": user["id"],
            "name": user["name"],
            "scopes": normalize_scopes(user.get("scopes")),
            "iat": now,
            "exp": now + timedelta(hours=JWT_TTL_HOURS),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        raise AuthError("invalid token")


async def register_user(name_value: Any, password_value: Any, email_value: Any) -> tuple[dict, str]:
    name = validate_name(name_value)
    password = validate_password(password_value)
    email = validate_email(email_value)

    users = mongo.collection("users")

    user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "name_lower": name.lower(),
        "password_hash": hash_password(password),
        "email": email,
        "avatar": dict(DEFAULT_AVATAR),
        "scopes": sorted(DEFAULT_SCOPES),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    try:
        await users.insert_one(user)
    except DuplicateKeyError:
        raise AuthError("name already taken")

    return public_user(user), create_token(user)


async def login_user(name_value: Any, password_value: Any) -> tuple[dict, str]:
    name = validate_name(name_value)
    password = validate_password(password_value)

    users = mongo.collection("users")
    user = await users.find_one({"name_lower": name.lower()})

    if not user:
        raise AuthError("invalid name or password")

    if not check_password(password, user["password_hash"]):
        raise AuthError("invalid name or password")

    return public_user(user), create_token(user)


async def user_from_token(token_value: Any) -> dict:
    if not isinstance(token_value, str) or not token_value.strip():
        raise AuthError("token required")

    payload = decode_token(token_value)
    user_id = payload.get("sub")

    if not isinstance(user_id, str):
        raise AuthError("invalid token")

    users = mongo.collection("users")
    user = await users.find_one({"id": user_id})

    if not user:
        raise AuthError("user not found")

    return public_user(user)


def has_scope(user: dict, scope: str) -> bool:
    scopes = set(normalize_scopes(user.get("scopes")))
    return scope in scopes


def require_scope(user: dict, scope: str) -> None:
    if not has_scope(user, scope):
        raise AuthError(f"missing scope: {scope}")