"""Mailbox message processing with durable deduplication and visible outcomes."""

from datetime import datetime, timezone
from email import message_from_bytes
from email.utils import parsedate_to_datetime

from pymongo.errors import DuplicateKeyError

from app.db.mongo import get_database
from app.email.parser import extract_text, parse_booking
from app.services.booking import _claim_booking, _audit


def process_message(mailbox_key: str, uid_validity: str, uid: int, raw_message: bytes,
                    allowed_senders: set[str]):
    db = get_database()
    message = message_from_bytes(raw_message)
    message_id = (message.get("Message-ID") or "").strip()
    sender = (message.get("From") or "").strip()
    subject = (message.get("Subject") or "").strip()
    received = datetime.now(timezone.utc)
    try:
        received = parsedate_to_datetime(message.get("Date")) if message.get("Date") else received
        if received.tzinfo is None:
            received = received.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        pass
    identity = {"mailbox_key": mailbox_key, "uid_validity": str(uid_validity), "imap_uid": int(uid)}
    record = {**identity, "message_id": message_id or None, "sender": sender, "subject": subject,
              "received_at": received, "status": "RECEIVED", "attempt_count": 0,
              "created_at": datetime.now(timezone.utc)}
    try:
        result = db.email_logs.insert_one(record)
        log_id = result.inserted_id
    except DuplicateKeyError:
        existing = db.email_logs.find_one(identity)
        if existing is None and message_id:
            existing = db.email_logs.find_one({"mailbox_key": mailbox_key, "message_id": message_id})
        if existing and existing.get("status") in {"PROCESSED", "INVALID", "CONFLICT"}:
            return existing["status"]
        if existing is None:
            raise
        log_id = existing["_id"]
    db.email_logs.update_one({"_id": log_id}, {"$set": {"status": "PROCESSING", "updated_at": datetime.now(timezone.utc)},
                              "$inc": {"attempt_count": 1}})
    sender_addr = sender.rsplit("<", 1)[-1].rstrip("> ").lower()
    if allowed_senders and sender_addr not in allowed_senders:
        db.email_logs.update_one({"_id": log_id}, {"$set": {"status": "INVALID", "error_code": "UNTRUSTED_SENDER",
                                                               "error_detail": "Sender is not in configured allowlist"}})
        return "INVALID"
    try:
        body = extract_text(message)
        if not any(key in body.lower() for key in ("room:", "terminal:", "booking date:", "purpose:")):
            db.email_logs.update_one({"_id": log_id}, {"$set": {"status": "INVALID", "error_code": "NOT_BOOKING_EMAIL",
                                                                   "error_detail": "Message does not match the configured booking format"}})
            return "INVALID"
        booking_input = parse_booking(body)
        db.email_logs.update_one({"_id": log_id}, {"$set": {"parsed": booking_input.model_dump(mode="json")}})
        booking = _claim_booking(db, booking_input, "gmail-worker", "EMAIL", log_id)
        db.email_logs.update_one({"_id": log_id}, {"$set": {"status": "PROCESSED", "booking_id": booking["_id"],
                                                               "processed_at": datetime.now(timezone.utc)}})
        _audit(db, None, "EMAIL_BOOKING_IMPORTED", "booking", booking["_id"], {"email_log_id": str(log_id)})
        return "PROCESSED"
    except Exception as error:
        from fastapi import HTTPException
        if isinstance(error, HTTPException) and error.status_code == 409:
            status, code = "CONFLICT", "BOOKING_CONFLICT"
        elif isinstance(error, (ValueError, TypeError)):
            status, code = "INVALID", "INVALID_BOOKING_DATA"
        else:
            status, code = "FAILED", "PROCESSING_ERROR"
        detail = str(error.detail) if isinstance(error, HTTPException) else str(error)
        db.email_logs.update_one({"_id": log_id}, {"$set": {"status": status, "error_code": code,
                                                                "error_detail": detail[:500]}})
        return status
