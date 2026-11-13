from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import current_user, require_roles
from app.db.mongo import get_database
from app.domain.booking import BookingInput
from app.domain.roles import UserRole
from app.services.booking import cancel_booking, create_request, decide_request

router = APIRouter(tags=["booking requests", "admin bookings"])


def _public_request(row: dict) -> dict:
    return {
        "id": str(row["_id"]), "room_code": row["room_code"], "booking_date": row["booking_date"],
        "start_time": row["start_time"], "end_time": row["end_time"], "purpose": row["purpose"],
        "status": row["status"], "created_at": row["created_at"].isoformat(),
        "decision_note": row.get("decision_note"),
    }


@router.post("/booking-requests", status_code=201)
def submit_request(payload: BookingInput, faculty: dict = Depends(require_roles(UserRole.FACULTY))):
    return _public_request(create_request(payload, faculty))


@router.get("/booking-requests/mine")
def my_requests(faculty: dict = Depends(require_roles(UserRole.FACULTY))):
    rows = get_database().booking_requests.find({"faculty_user_id": faculty["_id"]}).sort("created_at", -1)
    return [_public_request(row) for row in rows]


@router.get("/admin/booking-requests")
def admin_requests(status: str = Query(default="PENDING", pattern="^(PENDING|APPROVED|REJECTED|CANCELLED)$"),
                   _: dict = Depends(require_roles(UserRole.ADMIN))):
    rows = get_database().booking_requests.find({"status": status}).sort("created_at", 1).limit(200)
    return [{**_public_request(row), "faculty_user_id": str(row["faculty_user_id"])} for row in rows]


@router.post("/admin/booking-requests/{request_id}/approve")
def approve_request(request_id: str, admin: dict = Depends(require_roles(UserRole.ADMIN))):
    booking = decide_request(request_id, admin, True)
    return {"id": str(booking["_id"]), "status": booking["status"]}


@router.post("/admin/booking-requests/{request_id}/reject")
def reject_request(request_id: str, payload: dict | None = None,
                   admin: dict = Depends(require_roles(UserRole.ADMIN))):
    note = str((payload or {}).get("note", ""))[:500]
    return decide_request(request_id, admin, False, note)


@router.post("/admin/bookings/{booking_id}/cancel")
def cancel(booking_id: str, admin: dict = Depends(require_roles(UserRole.ADMIN))):
    return cancel_booking(booking_id, admin)


@router.post("/admin/users", status_code=201)
def create_user(payload: dict, admin: dict = Depends(require_roles(UserRole.ADMIN))):
    username = str(payload.get("username", "")).strip().lower()
    display_name = str(payload.get("display_name", "")).strip()
    password = str(payload.get("password", ""))
    role = str(payload.get("role", ""))
    if len(username) < 3 or len(username) > 80 or len(password) < 12 or len(display_name) < 1:
        raise HTTPException(422, "Provide username, display name, and password (at least 12 characters)")
    if role not in {"STUDENT", "FACULTY", "ADMIN"}:
        raise HTTPException(422, "Invalid role")
    from pymongo.errors import DuplicateKeyError
    from app.services.auth import hash_password
    try:
        result = get_database().users.insert_one({
            "username": username, "display_name": display_name, "password_hash": hash_password(password),
            "role": role, "active": True,
        })
    except DuplicateKeyError:
        raise HTTPException(409, "Username already exists") from None
    get_database().audit_logs.insert_one({"actor_user_id": admin["_id"], "action": "USER_CREATED",
        "entity_type": "user", "entity_id": str(result.inserted_id), "details": {"role": role},
        "created_at": datetime.now(timezone.utc)})
    return {"id": str(result.inserted_id), "username": username, "display_name": display_name, "role": role}


@router.get("/admin/email-logs")
def email_logs(status: str | None = None, _: dict = Depends(require_roles(UserRole.ADMIN))):
    query = {"status": status} if status else {}
    return [{"id": str(row["_id"]), "sender": row.get("sender", ""), "subject": row.get("subject", ""),
             "received_at": row.get("received_at").isoformat() if row.get("received_at") else None,
             "status": row["status"], "error": row.get("error_detail"), "parsed": row.get("parsed")}
            for row in get_database().email_logs.find(query).sort("received_at", -1).limit(200)]


@router.get("/admin/audit-logs")
def audit_logs(_: dict = Depends(require_roles(UserRole.ADMIN))):
    return [{"id": str(row["_id"]), "actor_user_id": str(row["actor_user_id"]) if row.get("actor_user_id") else None,
             "action": row["action"], "entity_type": row["entity_type"], "entity_id": row["entity_id"],
             "details": row.get("details", {}), "created_at": row["created_at"].isoformat()}
            for row in get_database().audit_logs.find().sort("created_at", -1).limit(200)]
