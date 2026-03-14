"""
SENTINELS OF INTEGRITY — ML Engine Configuration
Hyperparameters, paths, and security settings.
"""

from dataclasses import dataclass, field


@dataclass
class MLConfig:
    # Input specs (Design.txt §3)
    input_size: tuple[int, int] = (299, 299)
    frame_rate: int = 30
    max_frames: int = 300

    # Xception CNN config
    cnn_backbone: str = "xception"
    cnn_pretrained: bool = True
    cnn_num_classes: int = 2

    # Bi-GRU temporal config
    gru_hidden_size: int = 256
    gru_num_layers: int = 2
    gru_bidirectional: bool = True
    gru_dropout: float = 0.3

    # Ensemble config
    ensemble_weights: dict = field(default_factory=lambda: {
        "cnn": 0.6,
        "temporal": 0.3,
        "frequency": 0.1,
    })

    # Training config
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    num_epochs: int = 50
    early_stopping_patience: int = 7

    # Opacus differential privacy (TechStack.txt §1)
    dp_enabled: bool = True
    dp_epsilon: float = 8.0
    dp_delta: float = 1e-5
    dp_max_grad_norm: float = 1.0

    # ART adversarial robustness (TechStack.txt §1)
    art_enabled: bool = True
    art_eps: float = 0.03
    art_eps_step: float = 0.007

    # Target KPIs (PRD.txt §5)
    target_accuracy: float = 0.96
    target_latency_ms: int = 3000

    # Paths
    checkpoint_dir: str = "./checkpoints"
    data_dir: str = "./data"
    log_dir: str = "./logs"

    # Datasets
    dataset: str = "celeb_df_v2"  # celeb_df_v2, faceforensics, dfdc

    # Model watermarking (TechStack.txt §1)
    watermark_enabled: bool = True
    watermark_key: str = "sentinels-integrity-v1"


config = MLConfig()
