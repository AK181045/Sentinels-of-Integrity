"""
SENTINELS OF INTEGRITY — Frame Extractor
Extracts frames from video at 30fps, resized to 299x299.
(Design.txt §3: "Input size: 299x299px frames, 30fps sampling")
"""

import cv2
import numpy as np
import logging
from typing import Optional
from ml_models.config import config

logger = logging.getLogger("sentinels.ml.preprocessing.frames")


class FrameExtractor:
    def __init__(self, target_size: tuple = None, target_fps: int = None, max_frames: int = None):
        self.target_size = target_size or config.input_size
        self.target_fps = target_fps or config.frame_rate
        self.max_frames = max_frames or config.max_frames

    def extract_from_file(self, video_path: str) -> np.ndarray:
        """Extract frames from a video file. Returns (N, H, W, C) array."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_interval = max(1, int(src_fps / self.target_fps))

        frames = []
        idx = 0
        while cap.isOpened() and len(frames) < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            if idx % sample_interval == 0:
                frame = cv2.resize(frame, self.target_size)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)
            idx += 1

        cap.release()
        logger.info(f"Extracted {len(frames)} frames from {video_path}")
        return np.array(frames)

    def extract_from_bytes(self, video_bytes: bytes) -> np.ndarray:
        """Extract frames from video bytes (in-memory)."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        try:
            return self.extract_from_file(tmp_path)
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def normalize_frames(frames: np.ndarray) -> np.ndarray:
        """Normalize pixel values to [0, 1]."""
        return frames.astype(np.float32) / 255.0
