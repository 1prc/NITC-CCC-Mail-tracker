"""Deterministic extraction and parsing of booking email bodies."""

import re
from email.message import Message

from app.domain.booking import BookingInput

FIELD_PATTERNS = {
    "room_code": r"(?im)^\s*(?:room|terminal)\s*[:=-]\s*(T[1-6])\s*$",
    "booking_date": r"(?im)^\s*(?:date|booking date)\s*[:=-]\s*(\d{4}-\d{2}-\d{2})\s*$",
    "start_time": r"(?im)^\s*(?:start|start time)\s*[:=-]\s*(\d{1,2}:\d{2})\s*$",
    "end_time": r"(?im)^\s*(?:end|end time)\s*[:=-]\s*(\d{1,2}:\d{2})\s*$",
    "purpose": r"(?im)^\s*purpose\s*[:=-]\s*(.+?)\s*$",
}


def extract_text(message: Message) -> str:
    parts = message.walk() if message.is_multipart() else [message]
    texts = []
    for part in parts:
        if part.get_content_type() != "text/plain" or part.get_content_disposition() == "attachment":
            continue
        raw = part.get_payload(decode=True)
        if raw is None:
            continue
        charset = part.get_content_charset() or "utf-8"
        texts.append(raw.decode(charset, errors="replace"))
    return "\n".join(texts)


def parse_booking(body: str) -> BookingInput:
    values = {}
    for field, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, body)
        if not match:
            raise ValueError(f"Missing or malformed {field}")
        values[field] = match.group(1).strip()
    for field in ("start_time", "end_time"):
        if re.fullmatch(r"\d:\d{2}", values[field]):
            values[field] = "0" + values[field]
    return BookingInput(**values)
