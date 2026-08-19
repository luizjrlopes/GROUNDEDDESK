from __future__ import annotations
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User
from .domain import can

bearer = HTTPBearer(auto_error=False)

def issue_token(user: User) -> str:
    payload={"sub":user.id,"org":user.org_id,"role":user.role,"name":user.name,"exp":datetime.now(timezone.utc)+timedelta(minutes=settings.jwt_ttl_minutes)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not creds: raise HTTPException(401,"Missing bearer token")
    try: payload=jwt.decode(creds.credentials, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc: raise HTTPException(401,"Invalid token") from exc
    user=db.get(User,payload.get("sub"))
    if not user: raise HTTPException(401,"Unknown user")
    return user

def require(permission: str):
    def dep(user: User = Depends(current_user)) -> User:
        if not can(user.role, permission): raise HTTPException(403,f"Permission required: {permission}")
        return user
    return dep
