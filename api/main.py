"""
Gridiron FastAPI Backend
NFL Analytics Orchestrator with OAuth Authentication
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session as DBSession
import os
import secrets

from chains import analyze_query
from r_client import check_r_health
from models import init_db, get_db
from auth import (
    get_google_auth_url, exchange_google_code, get_google_user_info,
    get_twitter_auth_url, exchange_twitter_code, get_twitter_user_info,
    create_or_update_user, create_session_for_user, get_user_from_token,
    verify_token, revoke_session, TokenResponse, FRONTEND_URL
)

# Initialize database
init_db()

app = FastAPI(
    title="Gridiron API",
    description="NFL Analytics powered by nflfastR and LLM",
    version="1.0.0"
)

# Store OAuth state and PKCE verifiers (use Redis in production)
oauth_states: dict = {}

# CORS for SvelteKit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev
        "http://localhost:4173",    # Vite preview
        "http://localhost:3000",
        "http://localhost:57432",   # Our dev port
        os.getenv("FRONTEND_URL", "")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class AnalyzeRequest(BaseModel):
    query: str


class ChartConfig(BaseModel):
    type: str  # 'dot', 'slope', 'sparkline'
    data: list
    xLabel: Optional[str] = None
    yLabel: Optional[str] = None


class AnalyzeResponse(BaseModel):
    headline: str
    summary: str
    chart: Optional[ChartConfig] = None
    raw_data: Optional[dict] = None
    error: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


# Health Check
@app.get("/health")
async def health_check():
    """Check API and R service health"""
    r_status = await check_r_health()
    
    return {
        "status": "ok",
        "api": "healthy",
        "r_service": r_status
    }


# Analysis Endpoint
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Main analysis endpoint.
    Takes a natural language query, generates R code, executes it,
    and synthesizes a memo with visualization config.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        result = await analyze_query(request.query)
        return result
    except Exception as e:
        return AnalyzeResponse(
            headline="Analysis Error",
            summary=f"An error occurred while processing your query: {str(e)}",
            error=str(e)
        )


# ============================================
# Google OAuth
# ============================================

@app.get("/auth/google")
async def google_login():
    """Initiate Google OAuth flow"""
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": "google"}
    
    auth_url = get_google_auth_url(state)
    return {"url": auth_url}


@app.get("/auth/google/callback")
async def google_callback(
    code: str = None, 
    state: str = None, 
    error: str = None,
    db: DBSession = Depends(get_db)
):
    """Handle Google OAuth callback"""
    if error:
        return RedirectResponse(f"{FRONTEND_URL}?error={error}")
    
    if not code or not state or state not in oauth_states:
        return RedirectResponse(f"{FRONTEND_URL}?error=invalid_state")
    
    # Clean up state
    del oauth_states[state]
    
    # Exchange code for tokens
    token_data = await exchange_google_code(code)
    if not token_data:
        return RedirectResponse(f"{FRONTEND_URL}?error=token_exchange_failed")
    
    # Get user info
    user_info = await get_google_user_info(token_data["access_token"])
    if not user_info:
        return RedirectResponse(f"{FRONTEND_URL}?error=user_info_failed")
    
    # Create or update user
    user = create_or_update_user(
        db=db,
        email=user_info.get("email"),
        name=user_info.get("name"),
        avatar_url=user_info.get("picture"),
        provider="google",
        provider_id=user_info.get("id")
    )
    
    # Create session
    tokens = create_session_for_user(db, user)
    
    # Redirect to frontend with tokens
    return RedirectResponse(
        f"{FRONTEND_URL}/auth/callback?access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
    )


# ============================================
# X (Twitter) OAuth
# ============================================

@app.get("/auth/twitter")
async def twitter_login():
    """Initiate Twitter/X OAuth flow"""
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(32)
    
    oauth_states[state] = {
        "provider": "twitter",
        "code_verifier": code_verifier
    }
    
    auth_url = get_twitter_auth_url(state, code_verifier)
    return {"url": auth_url}


@app.get("/auth/twitter/callback")
async def twitter_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: DBSession = Depends(get_db)
):
    """Handle Twitter/X OAuth callback"""
    if error:
        return RedirectResponse(f"{FRONTEND_URL}?error={error}")
    
    if not code or not state or state not in oauth_states:
        return RedirectResponse(f"{FRONTEND_URL}?error=invalid_state")
    
    state_data = oauth_states.pop(state)
    code_verifier = state_data.get("code_verifier", "")
    
    # Exchange code for tokens
    token_data = await exchange_twitter_code(code, code_verifier)
    if not token_data:
        return RedirectResponse(f"{FRONTEND_URL}?error=token_exchange_failed")
    
    # Get user info
    user_info = await get_twitter_user_info(token_data["access_token"])
    if not user_info:
        return RedirectResponse(f"{FRONTEND_URL}?error=user_info_failed")
    
    # Twitter doesn't provide email by default, use username
    email = f"{user_info.get('username')}@twitter.gridiron"
    
    # Create or update user
    user = create_or_update_user(
        db=db,
        email=email,
        name=user_info.get("name"),
        avatar_url=user_info.get("profile_image_url"),
        provider="twitter",
        provider_id=user_info.get("id")
    )
    
    # Create session
    tokens = create_session_for_user(db, user)
    
    # Redirect to frontend with tokens
    return RedirectResponse(
        f"{FRONTEND_URL}/auth/callback?access_token={tokens.access_token}&refresh_token={tokens.refresh_token}"
    )


# ============================================
# Token Management
# ============================================

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: DBSession = Depends(get_db)):
    """Refresh access token using refresh token"""
    payload = verify_token(request.refresh_token, expected_type="refresh")
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return create_session_for_user(db, user)


@app.post("/auth/logout")
async def logout(request: RefreshRequest, db: DBSession = Depends(get_db)):
    """Logout and revoke refresh token"""
    revoked = revoke_session(db, request.refresh_token)
    return {"success": revoked}


@app.get("/auth/me")
async def get_current_user(request: Request, db: DBSession = Depends(get_db)):
    """Get current authenticated user"""
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = auth_header.replace("Bearer ", "")
    user = get_user_from_token(token, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "provider": user.provider
    }


# Import User model for /auth/refresh
from models import User


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
