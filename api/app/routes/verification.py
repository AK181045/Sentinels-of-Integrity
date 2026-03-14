"""
=============================================================================
SENTINELS OF INTEGRITY — Verification Route
GET /api/v1/verify — Blockchain hash lookup for content provenance.
=============================================================================

Data Flow Step 4: BLOCKCHAIN_LOOKUP → {is_registered, author, edit_history}
Target Latency: < 500ms (Design.txt §5)
=============================================================================
"""

import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from app.models.schemas import BlockchainVerificationResponse
from app.services.blockchain_service import BlockchainService
from app.middleware.auth import get_current_user

logger = logging.getLogger("sentinels.api.verification")

router = APIRouter()


@router.get("/verify", response_model=BlockchainVerificationResponse)
async def verify_content(
    media_hash: str = Query(
        ...,
        min_length=64,
        max_length=64,
        pattern=r"^[a-fA-F0-9]{64}$",
        description="SHA-256 hex hash of the media content (64 hex characters)",
    ),
    include_history: bool = Query(
        default=False,
        description="Include full edit history from blockchain",
    ),
    user: dict = Depends(get_current_user),
):
    """
    Verify media provenance via blockchain hash lookup.

    Checks the Polygon zkEVM ledger for:
    - Whether the content hash is registered (original content)
    - The registered author/creator address
    - Edit history and modification chain
    - ZK proof verification status

    **Target Latency:** < 500ms
    """
    logger.info(f"Verification request | hash={media_hash[:16]}... | history={include_history}")

    try:
        blockchain_service = BlockchainService()
        result = await blockchain_service.verify_hash(
            content_hash=media_hash,
            include_history=include_history,
        )

        logger.info(
            f"Verification completed | hash={media_hash[:16]}... | "
            f"registered={result.is_registered}"
        )
        return result

    except TimeoutError:
        logger.error(f"Blockchain lookup timed out | hash={media_hash[:16]}...")
        raise HTTPException(
            status_code=504,
            detail="Blockchain lookup timed out. RPC node may be unresponsive.",
        )
    except Exception as e:
        logger.error(f"Verification failed | hash={media_hash[:16]}... | error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during blockchain verification.",
        )


@router.post("/verify/register")
async def register_content(
    media_hash: str = Query(
        ...,
        min_length=64,
        max_length=64,
        pattern=r"^[a-fA-F0-9]{64}$",
        description="SHA-256 hex hash of the original media",
    ),
    creator_address: str = Query(
        ...,
        pattern=r"^0x[a-fA-F0-9]{40}$",
        description="Ethereum address of the content creator",
    ),
    user: dict = Depends(get_current_user),
):
    """
    Register original content on the blockchain.

    Mints an "Integrity Hash" on Polygon zkEVM, establishing
    provenance for the content creator.

    Requires multi-sig approval (3-of-5 validators) for execution.
    """
    logger.info(
        f"Content registration request | hash={media_hash[:16]}... | "
        f"creator={creator_address[:10]}..."
    )

    try:
        blockchain_service = BlockchainService()
        tx_hash = await blockchain_service.register_content(
            content_hash=media_hash,
            creator_address=creator_address,
        )

        return {
            "status": "registered",
            "content_hash": media_hash,
            "creator_address": creator_address,
            "transaction_hash": tx_hash,
            "network": "polygon_zkevm",
        }

    except Exception as e:
        logger.error(f"Registration failed | error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Content registration failed.",
        )
