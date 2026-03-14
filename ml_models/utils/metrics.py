"""
SENTINELS OF INTEGRITY — ML Metrics
Accuracy, F1, AUC, and FPR computation.
"""

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix


def compute_metrics(labels: list, predictions: list, probabilities: list = None) -> dict:
    """Compute comprehensive classification metrics."""
    acc = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average="binary")

    auc = 0.0
    if probabilities:
        try:
            auc = roc_auc_score(labels, probabilities)
        except ValueError:
            pass

    # False Positive Rate
    tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "accuracy": float(acc),
        "f1": float(f1),
        "auc": float(auc),
        "fpr": float(fpr),
        "fnr": float(fnr),
        "tp": int(tp), "tn": int(tn),
        "fp": int(fp), "fn": int(fn),
    }
