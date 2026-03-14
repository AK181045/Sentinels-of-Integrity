"""
SENTINELS OF INTEGRITY — Inference Pipeline
Full pipeline: frame → face → frequency → CNN → GRU → score
Target latency: < 3 seconds (Design.txt §5)
"""

import time
import logging
import torch
import numpy as np
from ml_models.config import config
from ml_models.preprocessing.frame_extractor import FrameExtractor
from ml_models.preprocessing.face_detector import FaceDetector
from ml_models.preprocessing.frequency_analyzer import FrequencyAnalyzer
from ml_models.inference.trust_scorer import TrustScorer

logger = logging.getLogger("sentinels.ml.inference")


class InferencePipeline:
    """End-to-end inference pipeline for deepfake detection."""

    def __init__(self, model_path: str = None, device: str = None):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.frame_extractor = FrameExtractor()
        self.face_detector = FaceDetector()
        self.frequency_analyzer = FrequencyAnalyzer()
        self.trust_scorer = TrustScorer()
        self.model = None

        if model_path:
            self._load_model(model_path)

    def _load_model(self, path: str):
        from ml_models.models.ensemble import EnsembleDetector
        self.model = EnsembleDetector().to(self.device)
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.eval()
        logger.info(f"Model loaded from {path}")

    def analyze_video(self, video_path: str) -> dict:
        """Full video analysis pipeline. Returns trust report dict."""
        start = time.time()

        # 1. Extract frames
        frames = self.frame_extractor.extract_from_file(video_path)

        # 2. Detect and crop faces
        face_frames = self.face_detector.process_video_frames(frames)

        # 3. Frequency analysis
        freq_result = self.frequency_analyzer.analyze_video(frames)

        # 4. ML inference
        ml_result = self._run_model(face_frames, freq_result)

        # 5. Compute trust score
        report = self.trust_scorer.compute(ml_result, freq_result)
        report["latency_ms"] = (time.time() - start) * 1000

        logger.info(f"Analysis complete | latency={report['latency_ms']:.0f}ms")
        return report

    def _run_model(self, frames: np.ndarray, freq_result: dict) -> dict:
        """Run the ensemble model on preprocessed frames."""
        if self.model is None:
            logger.warning("No model loaded — returning mock result")
            return {"is_synthetic": False, "confidence": 0.1, "artifacts": []}

        with torch.no_grad():
            # Prepare frame tensor
            tensor = torch.from_numpy(frames).float().permute(0, 3, 1, 2) / 255.0
            tensor = tensor.unsqueeze(0).to(self.device)  # (1, T, C, H, W)
            freq_score = torch.tensor([[freq_result["spectral_anomaly_score"]]]).to(self.device)

            result = self.model.predict(tensor, freq_score)
            return result

    def analyze_hash(self, media_hash: str) -> dict:
        """Analyze by hash (used when only hash is available from extension)."""
        logger.info(f"Hash-only analysis | hash={media_hash[:16]}...")
        return {
            "is_synthetic": False,
            "confidence": 0.0,
            "artifacts": ["hash_only_no_media"],
            "model_version": config.cnn_backbone + "-" + config.temporal_model,
        }
