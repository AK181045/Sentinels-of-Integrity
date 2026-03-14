"""
SENTINELS OF INTEGRITY — Trust Scorer
Generates {is_synthetic, confidence, artifacts} output.
(Design.txt §2: Step 3 output format)
"""

import logging

logger = logging.getLogger("sentinels.ml.inference.scorer")


class TrustScorer:
    """Converts raw ML outputs into the standardized trust score format."""

    def __init__(self, confidence_threshold: float = 0.7):
        self.threshold = confidence_threshold

    def compute(self, ml_result: dict, freq_result: dict) -> dict:
        """Compute final ML trust score from model + frequency results."""
        confidence = ml_result.get("confidence", 0.0)
        is_synthetic = confidence > self.threshold

        # Collect detected artifacts
        artifacts = list(ml_result.get("artifacts", []))
        if freq_result.get("ghosting_detected"):
            artifacts.append("ghosting")
        if freq_result.get("spectral_anomaly_score", 0) > 0.4:
            artifacts.append("spectral_anomaly")

        return {
            "is_synthetic": is_synthetic,
            "confidence": confidence,
            "artifacts": artifacts,
            "model_version": "xception-gru-v1",
            "spatial": ml_result.get("spatial"),
            "temporal": ml_result.get("temporal"),
            "frequency": freq_result,
        }
