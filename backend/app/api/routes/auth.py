from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import current_user
from app.db.mongo import get_database
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services.auth import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = get_database().users.find_one({"username": payload.username.strip().lower(), "active": True})
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    safe_user = UserResponse(
        id=str(user["_id"]), username=user["username"],
        display_name=user.get("display_name", user["username"]), role=user["role"],
    )
    return TokenResponse(access_token=create_access_token(str(user["_id"]), user["role"]), user=safe_user)


@router.get("/me", response_model=UserResponse)
def me(user: dict = Depends(current_user)):
    return UserResponse(
        id=str(user["_id"]), username=user["username"],
        display_name=user.get("display_name", user["username"]), role=user["role"],
    )
