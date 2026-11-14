from datetime import date

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.models import Room
from app.db.postgres import get_session
from app.schemas.room import RoomResponse
from app.services.booking import list_availability

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomResponse])
def list_rooms(db: Session = Depends(get_session)):
    rooms = db.scalars(select(Room).where(Room.active.is_(True)).order_by(Room.code)).all()
    return [RoomResponse(id=str(room.id), code=room.code, active=room.active) for room in rooms]


@router.get("/availability", tags=["availability"])
def availability(from_date: date = Query(alias="from"), days: int = Query(default=14, ge=1, le=28),
                 db: Session = Depends(get_session)):
    return list_availability(db, from_date, days)
