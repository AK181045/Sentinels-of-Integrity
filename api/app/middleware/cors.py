"""
=============================================================================
SENTINELS OF INTEGRITY — CORS Middleware Configuration
=============================================================================
"""

# CORS is configured directly in main.py using FastAPI's CORSMiddleware.
# This module exists for any custom CORS logic if needed in the future.

from app.config import settings

CORS_CONFIG = {
    "allow_origins": settings.CORS_ALLOWED_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["GET", "POST"],
    "allow_headers": ["*"],
    "max_age": 600,
}
