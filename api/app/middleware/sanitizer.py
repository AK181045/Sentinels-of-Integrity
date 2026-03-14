"""
=============================================================================
SENTINELS OF INTEGRITY — Input Sanitization Middleware
All extension data is treated as "untrusted" and sanitized.
=============================================================================

Security Directive (Design.txt §6):
"All inputs from the Browser Extension must be treated as 'Untrusted' and sanitized."
=============================================================================
"""

import logging
import re
import html

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("sentinels.api.sanitizer")

# Patterns that should NEVER appear in API inputs
DANGEROUS_PATTERNS = [
    re.compile(r"<script", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),      # Event handlers: onclick=, onerror=
    re.compile(r"data:text/html", re.IGNORECASE),
    re.compile(r"\.\./", re.IGNORECASE),             # Path traversal
    re.compile(r";\s*(DROP|DELETE|INSERT|UPDATE|ALTER)", re.IGNORECASE),  # SQL injection
    re.compile(r"\$\{.*\}", re.IGNORECASE),          # Template injection
    re.compile(r"{{.*}}", re.IGNORECASE),            # Template injection
]

# Max allowed length for string fields
MAX_STRING_LENGTH = 2048
MAX_URL_LENGTH = 4096


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Sanitizes all incoming request data from the browser extension.

    This middleware:
    1. Checks Content-Length against limits
    2. Scans query parameters for dangerous patterns
    3. Validates Content-Type headers
    4. Logs suspicious requests for security monitoring

    Note: Request body sanitization is handled by Pydantic validators
    in the schema layer (schemas.py), since reading the body in
    middleware would consume the stream.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip sanitization for health checks
        if request.url.path in ("/api/v1/health", "/api/v1/health/ready", "/"):
            return await call_next(request)

        # 1. Check Content-Length (prevent oversized payloads)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 50 * 1024 * 1024:  # 50 MB
            logger.warning(f"Oversized payload rejected | size={content_length}")
            return JSONResponse(
                status_code=413,
                content={"error": "Payload too large. Maximum size: 50 MB."},
            )

        # 2. Scan query parameters for dangerous patterns
        for param_name, param_value in request.query_params.items():
            # Length check
            if len(param_value) > MAX_URL_LENGTH:
                logger.warning(f"Oversized query param | param={param_name}")
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Query parameter '{param_name}' is too long."},
                )

            # Pattern check
            for pattern in DANGEROUS_PATTERNS:
                if pattern.search(param_value):
                    logger.warning(
                        f"Dangerous pattern detected in query param | "
                        f"param={param_name} | pattern={pattern.pattern}"
                    )
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Request contains potentially malicious content."},
                    )

        # 3. Validate Content-Type for POST/PUT requests
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            allowed_types = [
                "application/json",
                "multipart/form-data",
                "application/octet-stream",
            ]
            if content_type and not any(ct in content_type for ct in allowed_types):
                logger.warning(f"Invalid Content-Type | type={content_type}")
                return JSONResponse(
                    status_code=415,
                    content={"error": f"Unsupported Content-Type: {content_type}"},
                )

        return await call_next(request)


def sanitize_string(value: str) -> str:
    """
    Sanitize a string value from user input.
    Used by Pydantic validators in schemas.py.

    - HTML-escapes special characters
    - Strips null bytes
    - Truncates to max length
    """
    if not value:
        return value

    # Remove null bytes
    value = value.replace("\x00", "")

    # HTML-escape
    value = html.escape(value, quote=True)

    # Truncate
    if len(value) > MAX_STRING_LENGTH:
        value = value[:MAX_STRING_LENGTH]

    return value
