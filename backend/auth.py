"""
Authentication utilities for user login and token management.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Header
from .database import get_users_collection
from .models import UserResponse

# Simple in-memory token storage (for demo purposes)
# In production, use Redis or database-backed sessions
_token_store: dict[str, dict] = {}


def generate_token() -> str:
    """Generate a simple session token."""
    return secrets.token_urlsafe(32)


def create_session(user_id: str, user_data: dict) -> str:
    """Create a new session and return token."""
    token = generate_token()
    _token_store[token] = {
        "user_id": user_id,
        "user_data": user_data,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    return token


def get_session(token: str) -> Optional[dict]:
    """Get session data by token."""
    if token not in _token_store:
        return None
    
    session = _token_store[token]
    
    # Check expiration
    if datetime.now() > session["expires_at"]:
        del _token_store[token]
        return None
    
    return session


def delete_session(token: str) -> None:
    """Delete a session token."""
    if token in _token_store:
        del _token_store[token]


async def get_current_user(authorization: Optional[str] = Header(None)) -> UserResponse:
    """
    Dependency to get current authenticated user from Authorization header.
    
    Usage:
        @router.get("/protected")
        async def protected_endpoint(user: UserResponse = Depends(get_current_user)):
            ...
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = parts[1]
    session = get_session(token)
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return UserResponse(**session["user_data"])


async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[UserResponse]:
    """
    Optional dependency to get current user if authenticated, None otherwise.
    """
    if not authorization:
        return None
    
    try:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        token = parts[1]
        session = get_session(token)
        
        if not session:
            return None
        
        return UserResponse(**session["user_data"])
    except Exception:
        return None

