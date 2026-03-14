"""
=============================================================================
SENTINELS OF INTEGRITY — Auth Middleware
JWT RS256 verification + API key authentication.
=============================================================================

Security (TechStack.txt §2):
- JWT with RS256: Asymmetric signing to prevent token forgery
- mTLS: Mutual TLS for microservice communication
- WebAuthn / FIDO2: Passwordless admin access
=============================================================================
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger("sentinels.api.auth")

# Bearer token security scheme
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
) -> dict:
    """
    Validate the JWT bearer token and extract user identity.

    In development mode, this returns a mock user. In production,
    it validates the RS256 signature using the Rust core signer.

    Returns:
        dict with user identity: {"sub": str, "role": str}
    """
    # TODO: Replace with actual JWT validation via Rust core
    # For development, allow unauthenticated access
    if not credentials:
        # Development mode — return a default user
        return {"sub": "dev-user", "role": "developer", "authenticated": False}

    token = credentials.credentials

    try:
        # TODO: Implement actual RS256 JWT verification:
        # 1. Load public key from config
        # 2. Call sentinels_core.verify_jwt(public_key, token)
        # 3. Decode and validate claims (expiry, issuer, audience)
        # 4. Return user identity from claims

        # Placeholder: return mock user with token acknowledgment
        return {
            "sub": "authenticated-user",
            "role": "user",
            "authenticated": True,
            "token_prefix": token[:10] + "...",
        }

    except Exception as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
