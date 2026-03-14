"""
SENTINELS OF INTEGRITY — Custom Loss Functions
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """Focal Loss — down-weights easy examples, focuses on hard negatives."""

    def __init__(self, alpha: float = 0.75, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()


class WeightedBCELoss(nn.Module):
    """Weighted Binary Cross-Entropy for imbalanced datasets."""

    def __init__(self, pos_weight: float = 2.0):
        super().__init__()
        self.pos_weight = torch.tensor([pos_weight])

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        return F.binary_cross_entropy_with_logits(
            inputs, targets.float(), pos_weight=self.pos_weight.to(inputs.device)
        )
