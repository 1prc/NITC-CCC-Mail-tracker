"""FastAPI application entry point for the initial setup milestone."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.db.mongo import close_mongo, connect_mongo
from app.api.routes import auth, bookings, rooms

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.mongodb_uri:
        connect_mongo(settings.mongodb_uri, settings.mongodb_database)
    yield
    close_mongo()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API for the NITC CCC Terminal Booking Tracker.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(rooms.router, prefix=settings.api_prefix)
app.include_router(bookings.router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return process liveness without exposing configuration or secrets."""
    return {"status": "ok"}


@app.get(f"{settings.api_prefix}/", tags=["meta"])
def api_root() -> dict[str, str]:
    return {"name": settings.app_name, "version": "0.1.0"}
