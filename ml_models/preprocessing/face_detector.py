"""
SENTINELS OF INTEGRITY — Face Detector & Cropper
Detects and crops faces from frames for focused deepfake analysis.
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger("sentinels.ml.preprocessing.face")


class FaceDetector:
    """Face detection using OpenCV's DNN or MTCNN."""

    def __init__(self, margin: float = 0.3, min_confidence: float = 0.7):
        self.margin = margin
        self.min_confidence = min_confidence
        # Use OpenCV's built-in face detector as default
        self.detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def detect_faces(self, frame: np.ndarray) -> list[dict]:
        """Detect faces and return bounding boxes with confidence."""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame
        faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        results = []
        for (x, y, w, h) in faces:
            margin_x = int(w * self.margin)
            margin_y = int(h * self.margin)
            results.append({
                "x": max(0, x - margin_x),
                "y": max(0, y - margin_y),
                "w": w + 2 * margin_x,
                "h": h + 2 * margin_y,
                "confidence": 0.9,  # CascadeClassifier doesn't provide confidence
            })
        return results

    def crop_faces(self, frame: np.ndarray, target_size: tuple = (299, 299)) -> list[np.ndarray]:
        """Detect and crop faces from a frame, resized to target."""
        faces = self.detect_faces(frame)
        crops = []
        for face in faces:
            x, y, w, h = face["x"], face["y"], face["w"], face["h"]
            crop = frame[y:y+h, x:x+w]
            if crop.size > 0:
                crop = cv2.resize(crop, target_size)
                crops.append(crop)
        return crops

    def process_video_frames(self, frames: np.ndarray, target_size: tuple = (299, 299)) -> np.ndarray:
        """Process all frames, returning face crops (or original if no face found)."""
        processed = []
        for frame in frames:
            crops = self.crop_faces(frame, target_size)
            if crops:
                processed.append(crops[0])  # Use the first/largest face
            else:
                processed.append(cv2.resize(frame, target_size))
        return np.array(processed)
