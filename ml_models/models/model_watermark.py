"""
SENTINELS OF INTEGRITY — Neural Network Watermarking
Embeds a watermark into model weights to prevent model stealing.
(TechStack.txt §1: "Neural Network Watermarking to prevent Model Stealing")
"""

import hashlib
import torch
import torch.nn as nn
import logging

logger = logging.getLogger("sentinels.ml.watermark")


class ModelWatermarker:
    """Embeds and verifies watermarks in neural network weights."""

    def __init__(self, watermark_key: str = "sentinels-integrity-v1"):
        self.key = watermark_key
        self.key_hash = hashlib.sha256(watermark_key.encode()).hexdigest()

    def embed_watermark(self, model: nn.Module, layer_name: str = "classifier.4.weight") -> bool:
        """Embed watermark bits into specified layer weights."""
        target = dict(model.named_parameters()).get(layer_name)
        if target is None:
            logger.warning(f"Layer '{layer_name}' not found")
            return False

        watermark_bits = self._key_to_bits()
        with torch.no_grad():
            flat = target.data.flatten()
            for i, bit in enumerate(watermark_bits[:min(len(watermark_bits), len(flat))]):
                sign = 1.0 if bit == 1 else -1.0
                flat[i] = abs(flat[i]) * sign
            target.data = flat.view(target.shape)

        logger.info(f"Watermark embedded in '{layer_name}' ({len(watermark_bits)} bits)")
        return True

    def verify_watermark(self, model: nn.Module, layer_name: str = "classifier.4.weight") -> tuple[bool, float]:
        """Verify watermark presence. Returns (is_present, accuracy)."""
        target = dict(model.named_parameters()).get(layer_name)
        if target is None:
            return False, 0.0

        watermark_bits = self._key_to_bits()
        flat = target.data.flatten()
        matches = 0
        total = min(len(watermark_bits), len(flat))

        for i in range(total):
            expected_sign = 1 if watermark_bits[i] == 1 else -1
            actual_sign = 1 if flat[i] >= 0 else -1
            if expected_sign == actual_sign:
                matches += 1

        accuracy = matches / total if total > 0 else 0.0
        is_present = accuracy > 0.85
        return is_present, accuracy

    def _key_to_bits(self) -> list[int]:
        """Convert watermark key hash to bit sequence."""
        return [int(b) for char in self.key_hash for b in format(ord(char), '08b')]
