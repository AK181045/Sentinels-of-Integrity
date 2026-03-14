"""
=============================================================================
SENTINELS OF INTEGRITY — Application Configuration
Environment-based config with secrets management.
=============================================================================

Security (TechStack.txt §2):
- Secrets Management via HashiCorp Vault (HSM integration)
- All sensitive values loaded from environment variables
=============================================================================
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ---- General ----
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    DEBUG: bool = Field(default=True, description="Enable debug mode (exposes /docs)")
    API_VERSION: str = Field(default="v1", description="API version string")
    HOST: str = Field(default="0.0.0.0", description="Server bind host")
    PORT: int = Field(default=8000, description="Server bind port")

    # ---- Database ----
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://sentinels:password@localhost:5432/sentinels_db",
        description="PostgreSQL connection string",
    )

    # ---- Redis (Rate Limiting) ----
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for rate limiting",
    )
    RATE_LIMIT_MAX_REQUESTS: int = Field(default=100, description="Max requests per window")
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60, description="Sliding window in seconds")

    # ---- Security ----
    JWT_PRIVATE_KEY_PATH: str = Field(
        default="./keys/private.pem",
        description="Path to RSA private key for JWT signing",
    )
    JWT_PUBLIC_KEY_PATH: str = Field(
        default="./keys/public.pem",
        description="Path to RSA public key for JWT verification",
    )
    JWT_ALGORITHM: str = Field(default="RS256", description="JWT signing algorithm")
    JWT_EXPIRY_SECONDS: int = Field(default=3600, description="JWT token expiry (1 hour)")

    AES_KEY_PATH: str = Field(
        default="./keys/aes.key",
        description="Path to AES-256 key for data encryption at rest",
    )

    # ---- CORS ----
    CORS_ALLOWED_ORIGINS: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins (wildcard for local testing)",
    )

    # ---- ML Engine ----
    ML_ENGINE_URL: str = Field(
        default="http://localhost:8001",
        description="ML inference service URL",
    )
    ML_TIMEOUT_SECONDS: float = Field(
        default=10.0,
        description="Timeout for ML inference requests",
    )

    # ---- Blockchain ----
    BLOCKCHAIN_RPC_URL: str = Field(
        default="https://rpc.cardona.zkevm-rpc.com",
        description="Polygon zkEVM RPC endpoint",
    )
    CONTENT_REGISTRY_ADDRESS: Optional[str] = Field(
        default=None,
        description="Deployed ContentRegistry contract address",
    )
    INTEGRITY_HASH_ADDRESS: Optional[str] = Field(
        default=None,
        description="Deployed IntegrityHash contract address",
    )
    BLOCKCHAIN_PRIVATE_KEY: Optional[str] = Field(
        default=None,
        description="Private key for contract interactions (loaded from Vault)",
    )

    # ---- HashiCorp Vault ----
    VAULT_ENABLED: bool = Field(default=False, description="Enable Vault secrets management")
    VAULT_URL: str = Field(default="http://localhost:8200", description="Vault server URL")
    VAULT_TOKEN: Optional[str] = Field(default=None, description="Vault access token")
    VAULT_SECRET_PATH: str = Field(
        default="secret/data/sentinels",
        description="Vault KV path for secrets",
    )

    # ---- Logging ----
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format: json or text")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton settings instance
settings = Settings()
