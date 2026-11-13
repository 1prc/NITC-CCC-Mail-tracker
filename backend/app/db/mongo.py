"""Mongo client lifecycle, collection access, and foundation indexes."""

from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError

_client: MongoClient | None = None
_database = None


def connect_mongo(uri: str, database_name: str) -> None:
    global _client, _database
    _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    _client.admin.command("ping")
    _database = _client[database_name]
    _database.users.create_index([("username", ASCENDING)], unique=True)
    _database.rooms.create_index([("code", ASCENDING)], unique=True)
    _database.bookings.create_index([("room_id", ASCENDING), ("booking_date", ASCENDING), ("status", ASCENDING)])
    _database.booking_requests.create_index([("faculty_user_id", ASCENDING), ("created_at", ASCENDING)])
    _database.booking_requests.create_index([("status", ASCENDING), ("created_at", ASCENDING)])
    _database.slot_allocations.create_index(
        [("room_id", ASCENDING), ("booking_date", ASCENDING), ("slot_id", ASCENDING)], unique=True
    )
    _database.email_logs.create_index(
        [("mailbox_key", ASCENDING), ("message_id", ASCENDING)],
        unique=True,
        partialFilterExpression={"message_id": {"$type": "string"}},
    )
    _database.email_logs.create_index([("mailbox_key", ASCENDING), ("uid_validity", ASCENDING), ("imap_uid", ASCENDING)], unique=True)
    _database.email_logs.create_index([("status", ASCENDING), ("received_at", ASCENDING)])
    _database.audit_logs.create_index([("entity_type", ASCENDING), ("entity_id", ASCENDING), ("created_at", ASCENDING)])
    _database.mailbox_state.create_index([("_id", ASCENDING)], unique=True)


def close_mongo() -> None:
    global _client, _database
    if _client is not None:
        _client.close()
    _client = None
    _database = None


def get_database():
    if _database is None:
        raise RuntimeError("MongoDB is not configured. Set MONGODB_URI in backend/.env.")
    return _database
