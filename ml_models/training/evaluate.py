"""
SENTINELS OF INTEGRITY — Model Evaluation
Evaluates model on Celeb-DF v2 / FaceForensics++ / DFDC.
Target: >= 96% accuracy (PRD.txt §5)
"""

import torch
import logging
from ml_models.utils.metrics import compute_metrics

logger = logging.getLogger("sentinels.ml.training.evaluate")


def evaluate(model, data_loader, device, dataset_name: str = "celeb_df_v2"):
    """Evaluate model and return detailed metrics."""
    model.eval()
    all_preds, all_labels, all_probs = [], [], []

    with torch.no_grad():
        for frames, freq_scores, labels in data_loader:
            frames = frames.to(device)
            freq_scores = freq_scores.to(device)
            outputs = model(frames, freq_scores)
            probs = torch.softmax(outputs, dim=1)[:, 1]
            preds = (probs > 0.5).long()

            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.tolist())
            all_probs.extend(probs.cpu().tolist())

    metrics = compute_metrics(all_labels, all_preds, all_probs)
    logger.info(
        f"Evaluation on {dataset_name} | "
        f"Acc={metrics['accuracy']:.4f} | "
        f"AUC={metrics['auc']:.4f} | "
        f"F1={metrics['f1']:.4f} | "
        f"FPR={metrics['fpr']:.4f}"
    )
    return metrics
