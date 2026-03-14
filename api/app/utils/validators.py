"""
SENTINELS OF INTEGRITY — Input Validators
Validation utilities for API inputs.
"""

import re

SHA256_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")
ETH_ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")
URL_MAX_LENGTH = 4096


def is_valid_sha256(value: str) -> bool:
    return bool(SHA256_PATTERN.match(value))


def is_valid_eth_address(value: str) -> bool:
    return bool(ETH_ADDRESS_PATTERN.match(value))


def is_valid_platform(value: str) -> bool:
    return value.lower() in ("youtube", "twitter", "tiktok")


def is_valid_url(value: str) -> bool:
    if len(value) > URL_MAX_LENGTH:
        return False
    return value.startswith(("http://", "https://"))


def sanitize_hash(value: str) -> str:
    return value.lower().strip()
