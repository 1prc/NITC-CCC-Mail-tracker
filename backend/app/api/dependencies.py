"""Authentication and role authorization dependencies."""

import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.db.mongo import get_database
from app.domain.roles import UserRole

bearer = HTTPBearer(auto_error=False)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret_key, algorithms=["HS256"])
        if not ObjectId.is_valid(payload["sub"]):
            raise ValueError("Invalid user identifier")
        user = get_database().users.find_one({"_id": ObjectId(payload["sub"]), "active": True})
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired credentials") from None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired credentials")
    return user


def require_roles(*roles: UserRole):
    def dependency(user: dict = Depends(current_user)) -> dict:
        if user.get("role") not in {role.value for role in roles}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency
