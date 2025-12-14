"""
Gridiron Database Models
SQLite with SQLAlchemy for users, sessions, and query history
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gridiron.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User model for authenticated users"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # OAuth provider info
    provider = Column(String, nullable=False)  # 'google', 'twitter', 'email'
    provider_id = Column(String, nullable=True)  # Provider's user ID
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    
    # Subscription (for future use)
    is_premium = Column(Boolean, default=False)
    query_count = Column(Integer, default=0)


class Session(Base):
    """Session model for JWT refresh tokens"""
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    refresh_token = Column(String, unique=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    
    # Device info (optional)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)


class QueryHistory(Base):
    """Query history for saved queries"""
    __tablename__ = "query_history"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    query = Column(String, nullable=False)
    response_headline = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
