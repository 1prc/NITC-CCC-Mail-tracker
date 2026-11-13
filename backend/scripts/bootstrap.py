"""Create initial rooms and optionally one administrator from environment settings."""

from datetime import datetime, timezone

from pymongo import ASCENDING, MongoClient

from app.core.config import get_settings
from app.services.auth import hash_password


def main() -> None:
    settings = get_settings()
    if not settings.mongodb_uri:
        raise SystemExit("Set MONGODB_URI in backend/.env before bootstrapping.")
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        db = client[settings.mongodb_database]
        db.users.create_index([("username", ASCENDING)], unique=True)
        db.rooms.create_index([("code", ASCENDING)], unique=True)
        now = datetime.now(timezone.utc)
        for code in ("T1", "T2", "T3", "T4", "T5", "T6"):
            db.rooms.update_one(
                {"code": code},
                {"$setOnInsert": {"code": code, "active": True, "created_at": now}},
                upsert=True,
            )
        username = settings.bootstrap_admin_username.strip().lower()
        password = settings.bootstrap_admin_password
        if password:
            db.users.update_one(
                {"username": username},
                {"$setOnInsert": {
                    "username": username,
                    "password_hash": hash_password(password),
                    "role": "ADMIN",
                    "display_name": "CCC Administrator",
                    "active": True,
                    "created_at": now,
                }},
                upsert=True,
            )
            print("Initial administrator ensured.")
        else:
            print("No bootstrap administrator created; set BOOTSTRAP_ADMIN_PASSWORD to create one.")
        print("Rooms T1–T6 ensured.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
