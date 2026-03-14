"""
SENTINELS OF INTEGRITY — Dataset Loader
Loads FaceForensics++, Celeb-DF v2, and DFDC datasets.
"""

import os
import torch
from torch.utils.data import Dataset
import numpy as np
import cv2
from ml_models.config import config
from ml_models.preprocessing.augmentations import AugmentationPipeline


class DeepfakeDataset(Dataset):
    """Generic deepfake dataset loader."""

    def __init__(self, root_dir: str, split: str = "train", augment: bool = True):
        self.root_dir = root_dir
        self.split = split
        self.augment = augment and split == "train"
        self.augmentation = AugmentationPipeline() if self.augment else None
        self.target_size = config.input_size
        self.samples = self._load_samples()

    def _load_samples(self) -> list[tuple[str, int]]:
        """Load file paths and labels. Returns [(path, label), ...]"""
        samples = []
        split_dir = os.path.join(self.root_dir, self.split)
        for label_name, label in [("real", 0), ("fake", 1)]:
            class_dir = os.path.join(split_dir, label_name)
            if os.path.isdir(class_dir):
                for fname in os.listdir(class_dir):
                    if fname.endswith(('.mp4', '.avi', '.png', '.jpg')):
                        samples.append((os.path.join(class_dir, fname), label))
        return samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]

        if path.endswith(('.png', '.jpg')):
            frame = cv2.imread(path)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, self.target_size)
        else:
            # Load video: extract a subset of frames
            frame = self._load_video_frames(path)

        if self.augment and self.augmentation:
            frame = self.augmentation(frame)

        tensor = torch.from_numpy(frame).float().permute(2, 0, 1) / 255.0
        return tensor, torch.tensor(label, dtype=torch.long)

    def _load_video_frames(self, path: str) -> np.ndarray:
        """Load a single representative frame from video."""
        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        mid = total // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return cv2.resize(frame, self.target_size)
        return np.zeros((*self.target_size, 3), dtype=np.uint8)
