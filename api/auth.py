"""
Gridiron Authentication Module
Google and X (Twitter) OAuth2 + JWT session management
"""

import os
import secrets
import httpx
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from models import User, Session, get_db

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID", "")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET", "")
TWITTER_REDIRECT_URI = os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8000/auth/twitter/callback")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:57432")


# Pydantic models
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserInfo(BaseModel):
    id: str
    email: str
    name: Optional[str]
    avatar_url: Optional[str]
    provider: str


# JWT Functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        return payload
    except JWTError:
        return None


def get_user_from_token(token: str, db: DBSession) -> Optional[User]:
    """Get user from access token"""
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    return db.query(User).filter(User.id == user_id).first()


# Google OAuth
def get_google_auth_url(state: str) -> str:
    """Generate Google OAuth authorization URL"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent"
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"


async def exchange_google_code(code: str) -> Optional[dict]:
    """Exchange Google authorization code for tokens"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_REDIRECT_URI
            }
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()


async def get_google_user_info(access_token: str) -> Optional[dict]:
    """Get user info from Google"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()


# X (Twitter) OAuth 2.0
def get_twitter_auth_url(state: str, code_challenge: str) -> str:
    """Generate Twitter OAuth2 authorization URL"""
    params = {
        "response_type": "code",
        "client_id": TWITTER_CLIENT_ID,
        "redirect_uri": TWITTER_REDIRECT_URI,
        "scope": "tweet.read users.read offline.access",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "plain"  # Use S256 in production
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://twitter.com/i/oauth2/authorize?{query}"


async def exchange_twitter_code(code: str, code_verifier: str) -> Optional[dict]:
    """Exchange Twitter authorization code for tokens"""
    import base64
    
    credentials = base64.b64encode(
        f"{TWITTER_CLIENT_ID}:{TWITTER_CLIENT_SECRET}".encode()
    ).decode()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": TWITTER_REDIRECT_URI,
                "code_verifier": code_verifier
            }
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()


async def get_twitter_user_info(access_token: str) -> Optional[dict]:
    """Get user info from Twitter"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.twitter.com/2/users/me?user.fields=profile_image_url",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        return data.get("data")


# User Management
def create_or_update_user(
    db: DBSession,
    email: str,
    name: Optional[str],
    avatar_url: Optional[str],
    provider: str,
    provider_id: Optional[str] = None
) -> User:
    """Create or update a user after OAuth"""
    import uuid
    
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Update existing user
        user.last_login = datetime.utcnow()
        if name:
            user.name = name
        if avatar_url:
            user.avatar_url = avatar_url
    else:
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            avatar_url=avatar_url,
            provider=provider,
            provider_id=provider_id
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    return user


def create_session_for_user(db: DBSession, user: User) -> TokenResponse:
    """Create access and refresh tokens for a user"""
    import uuid
    
    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})
    
    # Store refresh token in database
    session = Session(
        id=str(uuid.uuid4()),
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(session)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "provider": user.provider
        }
    )


def revoke_session(db: DBSession, refresh_token: str) -> bool:
    """Revoke a session by refresh token"""
    session = db.query(Session).filter(
        Session.refresh_token == refresh_token,
        Session.is_revoked == False
    ).first()
    
    if session:
        session.is_revoked = True
        db.commit()
        return True
    
    return False
