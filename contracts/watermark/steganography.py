"""
SENTINELS OF INTEGRITY — Core Steganography Algorithms
DCT-domain steganography that survives JPEG compression.
"""

import numpy as np
import cv2


class DCTSteganography:
    """DCT-domain steganography for compression-resilient watermarking."""

    def __init__(self, strength: float = 25.0, block_size: int = 8):
        self.strength = strength
        self.block_size = block_size

    def _text_to_bits(self, text: str) -> list[int]:
        return [int(b) for char in text.encode('utf-8') for b in format(char, '08b')]

    def _bits_to_text(self, bits: list[int]) -> str:
        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) == 8:
                chars.append(chr(int(''.join(map(str, byte)), 2)))
        return ''.join(chars)

    def embed(self, frame: np.ndarray, payload: str) -> np.ndarray:
        """Embed payload bits into DCT coefficients of the frame."""
        if len(frame.shape) == 3:
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
            channel = ycrcb[:, :, 0].astype(np.float64)
        else:
            channel = frame.astype(np.float64)

        bits = self._text_to_bits(payload)
        h, w = channel.shape
        bs = self.block_size
        bit_idx = 0

        for i in range(0, h - bs + 1, bs):
            for j in range(0, w - bs + 1, bs):
                if bit_idx >= len(bits):
                    break
                block = channel[i:i+bs, j:j+bs]
                dct_block = cv2.dct(block)
                # Embed in mid-frequency coefficient (4,3)
                if bits[bit_idx] == 1:
                    dct_block[4, 3] = abs(dct_block[4, 3]) + self.strength
                else:
                    dct_block[4, 3] = -(abs(dct_block[4, 3]) + self.strength)
                channel[i:i+bs, j:j+bs] = cv2.idct(dct_block)
                bit_idx += 1

        if len(frame.shape) == 3:
            ycrcb[:, :, 0] = np.clip(channel, 0, 255).astype(np.uint8)
            return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)
        return np.clip(channel, 0, 255).astype(np.uint8)

    def extract(self, frame: np.ndarray, payload_length: int) -> str:
        """Extract payload from DCT coefficients."""
        if len(frame.shape) == 3:
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
            channel = ycrcb[:, :, 0].astype(np.float64)
        else:
            channel = frame.astype(np.float64)

        num_bits = payload_length * 8
        h, w = channel.shape
        bs = self.block_size
        bits = []

        for i in range(0, h - bs + 1, bs):
            for j in range(0, w - bs + 1, bs):
                if len(bits) >= num_bits:
                    break
                block = channel[i:i+bs, j:j+bs]
                dct_block = cv2.dct(block)
                bits.append(1 if dct_block[4, 3] > 0 else 0)

        return self._bits_to_text(bits[:num_bits])
