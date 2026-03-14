"""
SENTINELS OF INTEGRITY — IBM ART Adversarial Robustness
Defends against adversarial patches that trick the AI.
(TechStack.txt §1: "Robustness Library (ART)")
"""

import logging
import numpy as np

logger = logging.getLogger("sentinels.ml.adversarial.art")


class ARTDefense:
    """Wrapper around IBM Adversarial Robustness Toolbox."""

    def __init__(self, model, eps: float = 0.03, eps_step: float = 0.007):
        self.model = model
        self.eps = eps
        self.eps_step = eps_step
        self._classifier = None

    def _get_classifier(self):
        """Lazy-load ART classifier wrapper."""
        if self._classifier is None:
            try:
                from art.estimators.classification import PyTorchClassifier
                import torch.nn as nn
                self._classifier = PyTorchClassifier(
                    model=self.model,
                    loss=nn.CrossEntropyLoss(),
                    input_shape=(3, 299, 299),
                    nb_classes=2,
                )
            except ImportError:
                logger.error("ART not installed. Run: pip install adversarial-robustness-toolbox")
        return self._classifier

    def adversarial_training_batch(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Generate adversarial examples for training robustness."""
        classifier = self._get_classifier()
        if classifier is None:
            return x

        try:
            from art.attacks.evasion import ProjectedGradientDescent
            attack = ProjectedGradientDescent(classifier, eps=self.eps, eps_step=self.eps_step, max_iter=10)
            return attack.generate(x=x)
        except Exception as e:
            logger.error(f"ART adversarial generation failed: {e}")
            return x

    def detect_adversarial(self, x: np.ndarray) -> tuple[bool, float]:
        """Detect if input might be an adversarial example."""
        classifier = self._get_classifier()
        if classifier is None:
            return False, 0.0

        try:
            from art.defences.detector.evasion import BinaryInputDetector
            # Simplified detection via prediction variance
            preds = classifier.predict(x)
            confidence = float(np.max(preds))
            is_adversarial = confidence < 0.6  # Low confidence may indicate adversarial
            return is_adversarial, 1.0 - confidence
        except Exception:
            return False, 0.0


class PatchDetector:
    """Detects adversarial patches in input frames."""

    def __init__(self, patch_size_threshold: float = 0.05):
        self.threshold = patch_size_threshold

    def detect_patch(self, frame: np.ndarray) -> tuple[bool, list]:
        """Detect potential adversarial patches via color discontinuity analysis."""
        import cv2
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) if len(frame.shape) == 3 else frame
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        suspicious = []
        frame_area = frame.shape[0] * frame.shape[1]
        for cnt in contours:
            area = cv2.contourArea(cnt)
            ratio = area / frame_area
            if self.threshold < ratio < 0.3:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect = w / max(h, 1)
                if 0.5 < aspect < 2.0:  # Roughly square patches
                    suspicious.append({"x": x, "y": y, "w": w, "h": h, "area_ratio": ratio})

        return len(suspicious) > 0, suspicious
