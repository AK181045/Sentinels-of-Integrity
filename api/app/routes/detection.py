"""
=============================================================================
SENTINELS OF INTEGRITY — Detection Route
POST /api/v1/detect — Submit media for deepfake analysis.
=============================================================================

Data Flow Step 1-2: Extension sends media URL/hash → API triggers ML + Blockchain.
=============================================================================
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.models.schemas import (
    MediaAnalysisRequest,
    MediaAnalysisResponse,
    AnalysisStatus,
)
from app.services.detection_service import DetectionService
from app.services.score_aggregator import ScoreAggregator
from app.middleware.auth import get_current_user

logger = logging.getLogger("sentinels.api.detection")

router = APIRouter()


@router.post("/detect", response_model=MediaAnalysisResponse)
async def detect_media(
    request: MediaAnalysisRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """
    Submit media for deepfake detection and provenance verification.

    This endpoint:
    1. Validates the incoming request (sanitized by middleware)
    2. Triggers ML inference and blockchain lookup in parallel
    3. Aggregates results into a Sentinels Score
    4. Returns a Trust Report

    **Latency targets:**
    - Hash lookup: < 500ms
    - Full ML scan: < 3 seconds
    """
    report_id = str(uuid.uuid4())
    logger.info(
        f"Detection request received | report_id={report_id} | "
        f"platform={request.platform} | media_hash={request.media_hash[:16]}..."
    )

    try:
        detection_service = DetectionService()

        # Run ML inference and blockchain lookup in parallel
        ml_result, blockchain_result = await detection_service.analyze(
            media_hash=request.media_hash,
            media_url=str(request.media_url),
            platform=request.platform,
            options=request.options,
        )

        # Aggregate into Sentinels Score
        aggregator = ScoreAggregator()
        sentinels_score, verdict = aggregator.compute_score(ml_result, blockchain_result)

        response = MediaAnalysisResponse(
            report_id=report_id,
            media_hash=request.media_hash,
            media_url=str(request.media_url),
            platform=request.platform,
            sentinels_score=sentinels_score,
            verdict=verdict,
            ml_result=ml_result,
            blockchain_result=blockchain_result,
            status=AnalysisStatus.COMPLETED,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
        )

        # Store report asynchronously (don't block the response)
        background_tasks.add_task(
            detection_service.store_report, report_id, response.model_dump()
        )

        logger.info(
            f"Detection completed | report_id={report_id} | "
            f"score={sentinels_score:.1f} | verdict={verdict}"
        )
        return response

    except TimeoutError:
        logger.error(f"Detection timed out | report_id={report_id}")
        raise HTTPException(
            status_code=504,
            detail="Analysis timed out. The media may be too large for real-time processing.",
        )
    except Exception as e:
        logger.error(f"Detection failed | report_id={report_id} | error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during analysis.",
        )


@router.get("/detect/{report_id}", response_model=MediaAnalysisResponse)
async def get_detection_result(
    report_id: str,
    user: dict = Depends(get_current_user),
):
    """Retrieve a previously generated detection report by ID."""
    detection_service = DetectionService()
    report = await detection_service.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report
