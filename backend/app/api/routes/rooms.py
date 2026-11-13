from datetime import date

from fastapi import APIRouter, Query

from app.db.mongo import get_database
from app.schemas.room import RoomResponse
from app.services.booking import list_availability

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomResponse])
def list_rooms():
    rooms = get_database().rooms.find({"active": True}).sort("code", 1)
    return [RoomResponse(id=str(room["_id"]), code=room["code"], active=room["active"]) for room in rooms]


@router.get("/availability", tags=["availability"])
def availability(from_date: date = Query(alias="from"), days: int = Query(default=7, ge=1, le=7)):
    return list_availability(from_date.isoformat(), days)
