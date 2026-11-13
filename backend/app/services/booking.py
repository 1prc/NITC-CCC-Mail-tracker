"""Booking lifecycle, availability, and slot collision protection."""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from app.db.mongo import get_database
from app.domain.booking import BookingInput


def _room(db, code: str):
    room = db.rooms.find_one({"code": code, "active": True})
    if room is None:
        raise HTTPException(422, "Unknown or inactive room")
    return room


def _claim_booking(db, request: BookingInput, creator_id: str, source: str, source_id=None):
    room = _room(db, request.room_code)
    now = datetime.now(timezone.utc)
    booking_id = ObjectId()
    allocations = [
        {"room_id": room["_id"], "booking_date": request.booking_date.isoformat(), "slot_id": slot,
         "booking_id": booking_id, "created_at": now}
        for slot in request.slot_ids
    ]
    try:
        db.slot_allocations.insert_many(allocations, ordered=True)
    except DuplicateKeyError:
        db.slot_allocations.delete_many({"booking_id": booking_id})
        raise HTTPException(409, "One or more selected hourly slots are already booked") from None
    booking = {
        "_id": booking_id, "room_id": room["_id"], "room_code": room["code"],
        "booking_date": request.booking_date.isoformat(), "start_minute": request.start_minute,
        "end_minute": request.end_minute, "start_time": request.start_time,
        "end_time": request.end_time, "purpose": request.purpose, "source": source,
        "source_id": source_id, "created_by": creator_id, "status": "CONFIRMED",
        "created_at": now, "updated_at": now,
    }
    try:
        db.bookings.insert_one(booking)
    except Exception:
        db.slot_allocations.delete_many({"booking_id": booking_id})
        raise
    return booking


def _audit(db, actor_id, action, entity_type, entity_id, details=None):
    db.audit_logs.insert_one({
        "actor_user_id": actor_id, "action": action, "entity_type": entity_type,
        "entity_id": str(entity_id), "details": details or {}, "created_at": datetime.now(timezone.utc),
    })


def create_request(payload: BookingInput, faculty: dict):
    db = get_database()
    room = _room(db, payload.room_code)
    now = datetime.now(timezone.utc)
    request = {
        "faculty_user_id": faculty["_id"], "room_id": room["_id"], "room_code": room["code"],
        "booking_date": payload.booking_date.isoformat(), "start_time": payload.start_time,
        "end_time": payload.end_time, "start_minute": payload.start_minute,
        "end_minute": payload.end_minute, "purpose": payload.purpose,
        "status": "PENDING", "created_at": now, "updated_at": now,
    }
    result = db.booking_requests.insert_one(request)
    request["_id"] = result.inserted_id
    return request


def decide_request(request_id: str, admin: dict, approve: bool, note: str = ""):
    db = get_database()
    if not ObjectId.is_valid(request_id):
        raise HTTPException(404, "Request not found")
    request = db.booking_requests.find_one({"_id": ObjectId(request_id)})
    if request is None:
        raise HTTPException(404, "Request not found")
    if request["status"] != "PENDING":
        raise HTTPException(409, "Request has already been reviewed")
    now = datetime.now(timezone.utc)
    if approve:
        payload = BookingInput(
            room_code=request["room_code"], booking_date=request["booking_date"],
            start_time=request["start_time"], end_time=request["end_time"], purpose=request["purpose"],
        )
        claimed = db.booking_requests.update_one(
            {"_id": request["_id"], "status": "PENDING"},
            {"$set": {"status": "PROCESSING", "reviewed_by": admin["_id"], "reviewed_at": now}},
        )
        if claimed.modified_count != 1:
            raise HTTPException(409, "Request was reviewed concurrently")
        try:
            booking = _claim_booking(db, payload, str(admin["_id"]), "FACULTY_REQUEST", request["_id"])
        except Exception:
            db.booking_requests.update_one({"_id": request["_id"], "status": "PROCESSING"},
                                           {"$set": {"status": "PENDING", "reviewed_by": None, "reviewed_at": None}})
            raise
        updated = db.booking_requests.update_one(
            {"_id": request["_id"], "status": "PROCESSING"},
            {"$set": {"status": "APPROVED", "reviewed_by": admin["_id"], "reviewed_at": now,
                      "decision_note": note, "resulting_booking_id": booking["_id"], "updated_at": now}},
        )
        if updated.modified_count != 1:
            db.slot_allocations.delete_many({"booking_id": booking["_id"]})
            db.bookings.delete_one({"_id": booking["_id"]})
            raise HTTPException(409, "Request was reviewed concurrently")
        _audit(db, admin["_id"], "REQUEST_APPROVED", "booking_request", request["_id"])
        return booking
    updated = db.booking_requests.update_one(
        {"_id": request["_id"], "status": "PENDING"},
        {"$set": {"status": "REJECTED", "reviewed_by": admin["_id"], "reviewed_at": now,
                  "decision_note": note, "updated_at": now}},
    )
    if updated.modified_count != 1:
        raise HTTPException(409, "Request was reviewed concurrently")
    _audit(db, admin["_id"], "REQUEST_REJECTED", "booking_request", request["_id"])
    return {"status": "REJECTED", "id": request_id}


def cancel_booking(booking_id: str, admin: dict):
    db = get_database()
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(404, "Booking not found")
    oid = ObjectId(booking_id)
    now = datetime.now(timezone.utc)
    result = db.bookings.update_one({"_id": oid, "status": "CONFIRMED"},
                                    {"$set": {"status": "CANCELLED", "cancelled_by": admin["_id"],
                                              "cancelled_at": now, "updated_at": now}})
    if result.modified_count != 1:
        raise HTTPException(404, "Confirmed booking not found")
    db.slot_allocations.delete_many({"booking_id": oid})
    _audit(db, admin["_id"], "BOOKING_CANCELLED", "booking", oid)
    return {"id": booking_id, "status": "CANCELLED"}


def list_availability(start_date: str, days: int = 7):
    db = get_database()
    rooms = list(db.rooms.find({"active": True}).sort("code", 1))
    from datetime import date, timedelta
    first = date.fromisoformat(start_date)
    last = (first + timedelta(days=days - 1)).isoformat()
    bookings = list(db.bookings.find({"booking_date": {"$gte": start_date, "$lte": last}, "status": "CONFIRMED"}))
    by_room_date: dict[tuple[str, str], list[dict]] = {}
    for b in bookings:
        by_room_date.setdefault((b["room_code"], b["booking_date"]), []).append(b)
    result = []
    for offset in range(days):
        day = (first + timedelta(days=offset)).isoformat()
        for room in rooms:
            entries = sorted(by_room_date.get((room["code"], day), []), key=lambda b: b["start_minute"])
            occupied = {slot for b in entries for slot in range(b["start_minute"] // 60, b["end_minute"] // 60)}
            result.append({
                "date": day, "room_code": room["code"],
                "slots": [{"start": f"{hour:02d}:00", "end": f"{hour + 1:02d}:00",
                           "status": "BOOKED" if hour in occupied else "AVAILABLE"}
                          for hour in range(8, 20)],
                "bookings": [{"id": str(b["_id"]), "start": b["start_time"], "end": b["end_time"]} for b in entries],
            })
    return result
