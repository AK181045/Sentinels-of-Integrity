"""
=============================================================================
SENTINELS OF INTEGRITY — Unit Test: ML Metrics
Tests the metrics computation utility.
=============================================================================
"""

import pytest
from ml_models.utils.metrics import compute_metrics


class TestMetrics:
    """Tests for compute_metrics."""

    def test_perfect_predictions(self):
        labels = [0, 0, 1, 1]
        predictions = [0, 0, 1, 1]
        metrics = compute_metrics(labels, predictions)
        assert metrics["accuracy"] == 1.0
        assert metrics["f1"] == 1.0
        assert metrics["fpr"] == 0.0
        assert metrics["fnr"] == 0.0

    def test_all_wrong_predictions(self):
        labels = [0, 0, 1, 1]
        predictions = [1, 1, 0, 0]
        metrics = compute_metrics(labels, predictions)
        assert metrics["accuracy"] == 0.0
        assert metrics["fpr"] == 1.0
        assert metrics["fnr"] == 1.0

    def test_auc_with_probabilities(self):
        labels = [0, 0, 1, 1]
        predictions = [0, 0, 1, 1]
        probabilities = [0.1, 0.2, 0.8, 0.9]
        metrics = compute_metrics(labels, predictions, probabilities)
        assert metrics["auc"] == 1.0

    def test_auc_without_probabilities(self):
        metrics = compute_metrics([0, 1], [0, 1])
        assert metrics["auc"] == 0.0  # No probabilities provided

    def test_confusion_matrix_values(self):
        labels = [0, 0, 0, 1, 1, 1]
        predictions = [0, 0, 1, 0, 1, 1]
        metrics = compute_metrics(labels, predictions)
        assert metrics["tp"] == 2
        assert metrics["tn"] == 2
        assert metrics["fp"] == 1
        assert metrics["fn"] == 1

    def test_return_type(self):
        metrics = compute_metrics([0, 1], [0, 1])
        assert isinstance(metrics, dict)
        for key in ["accuracy", "f1", "auc", "fpr", "fnr", "tp", "tn", "fp", "fn"]:
            assert key in metrics
