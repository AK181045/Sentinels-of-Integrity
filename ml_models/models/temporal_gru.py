"""
SENTINELS OF INTEGRITY — Bi-directional GRU Temporal Analyzer
Analyzes frame-to-frame consistency for temporal deepfake artifacts.
Architecture: Bi-directional GRU (Design.txt §3)
"""

import torch
import torch.nn as nn


class TemporalGRU(nn.Module):
    """
    Bi-directional GRU for temporal consistency analysis.

    Takes a sequence of frame-level CNN features and produces
    temporal consistency scores to detect:
    - Flickering between real/fake frames
    - Temporal discontinuities
    - Unnatural motion patterns
    """

    def __init__(
        self,
        input_dim: int = 1024,
        hidden_size: int = 256,
        num_layers: int = 2,
        bidirectional: bool = True,
        dropout: float = 0.3,
        num_classes: int = 2,
    ):
        super().__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1

        # Bi-GRU layers
        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        # Attention mechanism for frame importance weighting
        gru_output_dim = hidden_size * self.num_directions
        self.attention = nn.Sequential(
            nn.Linear(gru_output_dim, 128),
            nn.Tanh(),
            nn.Linear(128, 1),
        )

        # Classifier
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(gru_output_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes),
        )

        self.feature_dim = gru_output_dim

    def forward(self, frame_features: torch.Tensor) -> torch.Tensor:
        """
        Args:
            frame_features: (batch, seq_len, input_dim) — CNN features per frame
        Returns:
            logits: (batch, num_classes)
        """
        gru_out, _ = self.gru(frame_features)  # (batch, seq_len, hidden*2)

        # Attention-weighted aggregation
        attn_weights = self.attention(gru_out)  # (batch, seq_len, 1)
        attn_weights = torch.softmax(attn_weights, dim=1)
        context = torch.sum(gru_out * attn_weights, dim=1)  # (batch, hidden*2)

        logits = self.classifier(context)
        return logits

    def get_temporal_scores(self, frame_features: torch.Tensor) -> dict:
        """Get per-sequence temporal analysis scores."""
        with torch.no_grad():
            gru_out, _ = self.gru(frame_features)
            attn_weights = self.attention(gru_out)
            attn_weights = torch.softmax(attn_weights, dim=1)

            # Find frames with highest attention (potential anomalies)
            attn_flat = attn_weights.squeeze(-1)  # (batch, seq_len)
            threshold = attn_flat.mean() + 2 * attn_flat.std()
            anomaly_mask = attn_flat > threshold
            anomaly_frames = anomaly_mask[0].nonzero(as_tuple=True)[0].tolist()

            # Overall temporal consistency
            context = torch.sum(gru_out * attn_weights, dim=1)
            logits = self.classifier(context)
            probs = torch.softmax(logits, dim=1)

            return {
                "temporal_consistency": float(probs[0, 0]),
                "frames_analyzed": frame_features.shape[1],
                "anomaly_frames": anomaly_frames,
            }
