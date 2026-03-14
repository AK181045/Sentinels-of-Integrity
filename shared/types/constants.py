"""
=============================================================================
SENTINELS OF INTEGRITY — Shared Python Constants
Used by the backend API and ML engine modules.
=============================================================================
"""

from enum import Enum
from typing import Final

# =============================================================================
# Version
# =============================================================================
PROJECT_VERSION: Final[str] = "0.1.0"
API_VERSION: Final[str] = "v1"

# =============================================================================
# Platforms
# =============================================================================
class Platform(str, Enum):
    """Supported media platforms."""
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    TIKTOK = "tiktok"

SUPPORTED_PLATFORMS: Final[list[str]] = [p.value for p in Platform]

# =============================================================================
# Media Types
# =============================================================================
class MediaType(str, Enum):
    """Supported media types for analysis."""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"

SUPPORTED_MEDIA_TYPES: Final[list[str]] = [m.value for m in MediaType]

# =============================================================================
# Verdict Levels
# =============================================================================
class Verdict(str, Enum):
    """Trust verdict classification."""
    AUTHENTIC = "authentic"         # Score >= 70
    SUSPICIOUS = "suspicious"       # Score 40-69
    SYNTHETIC = "synthetic"         # Score < 40

# Score thresholds for verdict determination
SCORE_THRESHOLD_AUTHENTIC: Final[float] = 70.0
SCORE_THRESHOLD_SUSPICIOUS: Final[float] = 40.0

# =============================================================================
# ML Engine Constants
# =============================================================================
# Input specifications (from Design.txt §3)
ML_INPUT_SIZE: Final[tuple[int, int]] = (299, 299)   # pixels
ML_FRAME_RATE: Final[int] = 30                         # fps sampling
ML_DEFAULT_CONFIDENCE_THRESHOLD: Final[float] = 0.7

# Target KPIs (from PRD.txt §5)
TARGET_ACCURACY: Final[float] = 0.96          # >= 96%
TARGET_HASH_LATENCY_MS: Final[int] = 500      # < 500ms
TARGET_SCAN_LATENCY_MS: Final[int] = 3000     # < 3 seconds

# Model architectures
CNN_BACKBONE: Final[str] = "xception"
TEMPORAL_MODEL: Final[str] = "bi-gru"

# Datasets
DATASETS: Final[dict[str, str]] = {
    "faceforensics": "FaceForensics++",
    "celeb_df": "Celeb-DF v2",
    "dfdc": "DeepFake Detection Challenge",
}

# =============================================================================
# Blockchain Constants
# =============================================================================
# Network (from Design.txt §4 / TechStack.txt §3)
BLOCKCHAIN_NETWORK: Final[str] = "polygon_zkevm"
HASH_ALGORITHM: Final[str] = "SHA-256"
SIGNING_STANDARD: Final[str] = "EIP-712"
PROVENANCE_STANDARD: Final[str] = "C2PA"

# Multi-sig configuration
MULTISIG_REQUIRED_APPROVALS: Final[int] = 3
MULTISIG_TOTAL_VALIDATORS: Final[int] = 5

# =============================================================================
# Security Constants (from TechStack.txt)
# =============================================================================
ENCRYPTION_ALGORITHM: Final[str] = "AES-256-GCM"
JWT_ALGORITHM: Final[str] = "RS256"
RATE_LIMIT_WINDOW_SECONDS: Final[int] = 60
RATE_LIMIT_MAX_REQUESTS: Final[int] = 100

# =============================================================================
# Detected Artifact Labels
# =============================================================================
class ArtifactType(str, Enum):
    """Types of deepfake artifacts detectable by the ML engine."""
    GHOSTING = "ghosting"
    FACE_WARP = "face_warp"
    EDGE_BLENDING = "edge_blending"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    SPECTRAL_ANOMALY = "spectral_anomaly"
    COMPRESSION_ARTIFACT = "compression_artifact"
    LIGHTING_MISMATCH = "lighting_mismatch"

ARTIFACT_LABELS: Final[list[str]] = [a.value for a in ArtifactType]
