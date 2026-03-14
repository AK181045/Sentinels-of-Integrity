"""
SENTINELS OF INTEGRITY — File Handler Utility
Handles temporary file storage with hash-only persistence.
Security: Never stores raw video files — only SHA-256 hashes.
"""

import os
import tempfile
import logging

logger = logging.getLogger("sentinels.utils.file_handler")

TEMP_DIR = os.path.join(tempfile.gettempdir(), "sentinels_tmp")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def ensure_temp_dir():
    os.makedirs(TEMP_DIR, exist_ok=True)


async def save_temp_file(content: bytes, filename: str) -> str:
    ensure_temp_dir()
    filepath = os.path.join(TEMP_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    logger.info(f"Temp file saved: {filepath} ({len(content)} bytes)")
    return filepath


async def cleanup_temp_file(filepath: str):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Temp file cleaned: {filepath}")
    except OSError as e:
        logger.error(f"Failed to clean temp file: {e}")


def validate_file_size(content: bytes) -> bool:
    return len(content) <= MAX_FILE_SIZE
