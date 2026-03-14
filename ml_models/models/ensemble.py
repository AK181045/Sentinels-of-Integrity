"""
SENTINELS OF INTEGRITY — Ensemble Model
Combines Xception CNN (spatial) + Bi-GRU (temporal) + Frequency analysis.
"""

import torch
import torch.nn as nn
from ml_models.models.xception_cnn import XceptionCNN
from ml_models.models.temporal_gru import TemporalGRU
from ml_models.config import config


class EnsembleDetector(nn.Module):
    """
    Ensemble detector combining spatial (CNN), temporal (GRU),
    and frequency domain analysis for robust deepfake detection.
    """

    def __init__(self):
        super().__init__()
        self.cnn = XceptionCNN(num_classes=2, pretrained=config.cnn_pretrained)
        self.temporal = TemporalGRU(
            input_dim=self.cnn.feature_dim,
            hidden_size=config.gru_hidden_size,
            num_layers=config.gru_num_layers,
            bidirectional=config.gru_bidirectional,
            dropout=config.gru_dropout,
        )

        # Fusion layer
        cnn_out = 2
        temporal_out = 2
        freq_in = 1  # Frequency anomaly score
        fusion_in = cnn_out + temporal_out + freq_in

        self.fusion = nn.Sequential(
            nn.Linear(fusion_in, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(64, 2),
        )

        self.weights = config.ensemble_weights

    def forward(self, frames: torch.Tensor, freq_score: torch.Tensor) -> torch.Tensor:
        """
        Args:
            frames: (batch, num_frames, C, H, W) — video frames
            freq_score: (batch, 1) — frequency domain anomaly score
        Returns:
            logits: (batch, 2) — [real, fake] logits
        """
        batch, num_frames, C, H, W = frames.shape

        # Spatial: extract CNN features per frame
        flat = frames.view(batch * num_frames, C, H, W)
        cnn_features = self.cnn.extract_features(flat)       # (B*T, 1024)
        cnn_features = cnn_features.view(batch, num_frames, -1)  # (B, T, 1024)

        # Spatial logits (use the last frame's CNN output)
        cnn_logits = self.cnn.classifier(cnn_features[:, -1, :])  # (B, 2)

        # Temporal logits
        temporal_logits = self.temporal(cnn_features)  # (B, 2)

        # Fusion
        combined = torch.cat([cnn_logits, temporal_logits, freq_score], dim=1)
        output = self.fusion(combined)
        return output

    def predict(self, frames: torch.Tensor, freq_score: torch.Tensor) -> dict:
        """Full prediction with detailed breakdown."""
        with torch.no_grad():
            logits = self.forward(frames, freq_score)
            probs = torch.softmax(logits, dim=1)
            return {
                "is_synthetic": bool(probs[0, 1] > 0.5),
                "confidence": float(probs[0, 1]),
                "real_probability": float(probs[0, 0]),
                "fake_probability": float(probs[0, 1]),
            }
