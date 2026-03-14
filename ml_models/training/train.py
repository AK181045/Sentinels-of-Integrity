"""
SENTINELS OF INTEGRITY — Training Loop
Trains ensemble model with optional Opacus differential privacy.
"""

import os
import logging
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from ml_models.config import config
from ml_models.models.ensemble import EnsembleDetector
from ml_models.training.losses import FocalLoss

logger = logging.getLogger("sentinels.ml.training")


def train(resume_from: str = None):
    """Main training entry point."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Training on {device} | DP={config.dp_enabled}")

    # Initialize model
    model = EnsembleDetector().to(device)
    if resume_from and os.path.exists(resume_from):
        model.load_state_dict(torch.load(resume_from, map_location=device))
        logger.info(f"Resumed from {resume_from}")

    # Loss and optimizer
    criterion = FocalLoss(alpha=0.75, gamma=2.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.num_epochs)

    # Opacus differential privacy (TechStack.txt §1)
    if config.dp_enabled:
        try:
            from opacus import PrivacyEngine
            privacy_engine = PrivacyEngine()
            # Note: model, optimizer, data_loader would be wrapped here
            logger.info(f"DP enabled: ε={config.dp_epsilon}, δ={config.dp_delta}")
        except ImportError:
            logger.warning("Opacus not installed — training without DP")

    # TODO: Load actual dataset
    # train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    # val_loader = DataLoader(val_dataset, batch_size=config.batch_size)

    os.makedirs(config.checkpoint_dir, exist_ok=True)
    best_val_loss = float("inf")
    patience_counter = 0

    for epoch in range(config.num_epochs):
        model.train()
        epoch_loss = 0.0
        # TODO: Iterate over train_loader
        # for batch_idx, (frames, freq_scores, labels) in enumerate(train_loader):
        #     frames, freq_scores, labels = frames.to(device), freq_scores.to(device), labels.to(device)
        #     optimizer.zero_grad()
        #     outputs = model(frames, freq_scores)
        #     loss = criterion(outputs, labels)
        #     loss.backward()
        #     optimizer.step()
        #     epoch_loss += loss.item()

        scheduler.step()

        # Validation
        # val_loss = validate(model, val_loader, criterion, device)

        # Early stopping
        # if val_loss < best_val_loss:
        #     best_val_loss = val_loss
        #     patience_counter = 0
        #     torch.save(model.state_dict(), f"{config.checkpoint_dir}/best_model.pth")
        # else:
        #     patience_counter += 1
        #     if patience_counter >= config.early_stopping_patience:
        #         logger.info(f"Early stopping at epoch {epoch}")
        #         break

        logger.info(f"Epoch {epoch+1}/{config.num_epochs} | Loss: {epoch_loss:.4f}")

    logger.info("Training complete")


if __name__ == "__main__":
    train()
