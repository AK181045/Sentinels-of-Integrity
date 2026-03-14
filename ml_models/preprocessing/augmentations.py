"""
SENTINELS OF INTEGRITY — Data Augmentation Pipeline
"""

import numpy as np
import cv2
from typing import Callable


class AugmentationPipeline:
    """Composable augmentation pipeline for training data."""

    def __init__(self, augmentations: list[Callable] = None):
        self.augmentations = augmentations or self.default_augmentations()

    @staticmethod
    def default_augmentations() -> list[Callable]:
        return [
            RandomHorizontalFlip(p=0.5),
            RandomBrightness(delta=0.2, p=0.5),
            RandomCompression(quality_range=(60, 95), p=0.3),
            RandomGaussianNoise(std=0.02, p=0.3),
            RandomRotation(max_angle=10, p=0.3),
        ]

    def __call__(self, frame: np.ndarray) -> np.ndarray:
        for aug in self.augmentations:
            frame = aug(frame)
        return frame


class RandomHorizontalFlip:
    def __init__(self, p=0.5): self.p = p
    def __call__(self, img):
        return np.fliplr(img).copy() if np.random.random() < self.p else img


class RandomBrightness:
    def __init__(self, delta=0.2, p=0.5): self.delta, self.p = delta, p
    def __call__(self, img):
        if np.random.random() < self.p:
            factor = 1.0 + np.random.uniform(-self.delta, self.delta)
            return np.clip(img * factor, 0, 255).astype(img.dtype)
        return img


class RandomCompression:
    def __init__(self, quality_range=(60, 95), p=0.3):
        self.quality_range, self.p = quality_range, p
    def __call__(self, img):
        if np.random.random() < self.p:
            q = np.random.randint(*self.quality_range)
            _, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, q])
            return cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return img


class RandomGaussianNoise:
    def __init__(self, std=0.02, p=0.3): self.std, self.p = std, p
    def __call__(self, img):
        if np.random.random() < self.p:
            noise = np.random.normal(0, self.std * 255, img.shape)
            return np.clip(img + noise, 0, 255).astype(img.dtype)
        return img


class RandomRotation:
    def __init__(self, max_angle=10, p=0.3): self.max_angle, self.p = max_angle, p
    def __call__(self, img):
        if np.random.random() < self.p:
            angle = np.random.uniform(-self.max_angle, self.max_angle)
            h, w = img.shape[:2]
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
            return cv2.warpAffine(img, M, (w, h))
        return img
