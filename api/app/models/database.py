"""
=============================================================================
SENTINELS OF INTEGRITY — Database Models
PostgreSQL database models via SQLAlchemy async.
=============================================================================
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Integer, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# =============================================================================
# Database Engine & Session
# =============================================================================
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# =============================================================================
# Models
# =============================================================================
class AnalysisReport(Base):
    """Stores completed Trust Reports."""
    __tablename__ = "analysis_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    media_hash = Column(String(64), nullable=False, index=True)
    media_url = Column(Text, nullable=False)
    platform = Column(String(20), nullable=False, index=True)

    # Sentinels Score
    sentinels_score = Column(Float, nullable=False)
    verdict = Column(String(20), nullable=False, index=True)

    # ML Results
    ml_is_synthetic = Column(Boolean, nullable=False)
    ml_confidence = Column(Float, nullable=False)
    ml_artifacts = Column(JSON, default=list)
    ml_model_version = Column(String(50))

    # Blockchain Results
    blockchain_is_registered = Column(Boolean, default=False)
    blockchain_author = Column(String(42))  # Ethereum address
    blockchain_tx_hash = Column(String(66))

    # Metadata
    analyzed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    latency_ms = Column(Float, default=0.0)
    full_report = Column(JSON)  # Complete JSON report for detailed retrieval

    def __repr__(self):
        return f"<AnalysisReport(id={self.id}, score={self.sentinels_score}, verdict={self.verdict})>"


class ContentRegistration(Base):
    """Tracks content registered on the blockchain."""
    __tablename__ = "content_registrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_hash = Column(String(64), nullable=False, unique=True, index=True)
    creator_address = Column(String(42), nullable=False, index=True)
    transaction_hash = Column(String(66), nullable=False)
    block_number = Column(Integer)
    registered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    metadata_json = Column(JSON)

    def __repr__(self):
        return f"<ContentRegistration(hash={self.content_hash[:16]}..., creator={self.creator_address[:10]}...)>"


class RateLimitEntry(Base):
    """Rate limiting tracking table (backup for Redis)."""
    __tablename__ = "rate_limits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_ip = Column(String(45), nullable=False, index=True)  # IPv6 max length
    endpoint = Column(String(100), nullable=False)
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# =============================================================================
# Database Utilities
# =============================================================================
async def init_db():
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncSession:
    """Dependency injection for database sessions."""
    async with async_session() as session:
        yield session
