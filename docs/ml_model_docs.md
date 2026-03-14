# Sentinels of Integrity — ML Model Documentation

## Model Architecture

### Overview

The detection engine uses an **ensemble of three analysis modules**:

```
Video Input → Frame Extraction (30fps, 299x299)
                    │
                    ├──→ Xception CNN (Spatial)  ── weight: 60%
                    │         │
                    │    Feature vectors (1024-d)
                    │         │
                    │         ▼
                    ├──→ Bi-GRU (Temporal)     ── weight: 30%
                    │
                    └──→ FFT/DCT (Frequency)   ── weight: 10%
                              │
                              ▼
                    Learned Fusion Layer → Binary Classification
                              │
                              ▼
                    Trust Score (0-100) + Verdict
```

### 1. Xception CNN (Spatial Analysis)

- **Architecture:** Modified Xception with depthwise separable convolutions
- **Input:** 299 × 299 × 3 (RGB frames)
- **Feature Output:** 1024-dimensional vector
- **Analyzes:** Face consistency, edge blending artifacts, ghosting patterns
- **Key Layers:**
  - Entry Flow: 2 conv layers (3→32→64 channels)
  - Middle Flow: 7 Xception blocks (64→728 channels)
  - Exit Flow: 1 Xception block + AdaptiveAvgPool
  - Classifier: Dropout(0.5) → FC(1024→512) → ReLU → Dropout(0.3) → FC(512→2)

### 2. Bi-directional GRU (Temporal Analysis)

- **Architecture:** 2-layer bidirectional GRU with attention
- **Input:** Sequence of CNN feature vectors (seq_len × 1024)
- **Hidden Size:** 256 per direction (512 total)
- **Attention:** Learned attention weights for frame importance
- **Analyzes:** Frame-to-frame consistency, temporal discontinuities, unnatural motion
- **Anomaly Detection:** Frames with attention weights > mean + 2σ are flagged

### 3. Frequency Analyzer (Spectral Domain)

- **Method:** 2D FFT magnitude spectrum analysis
- **Detects:** High-frequency energy anomalies indicative of GAN generation artifacts
- **Ghosting:** Compares high-frequency vs total energy ratio (threshold: 0.3)
- **DCT:** Additional DCT analysis for JPEG artifact comparison

### 4. Ensemble Fusion

- **Fusion Layer:** FC(5→64) → ReLU → Dropout(0.3) → FC(64→2)
- **Input Concatenation:** CNN logits (2) + GRU logits (2) + freq score (1) = 5
- **Training:** End-to-end with focal loss (α=0.75, γ=2.0)

## Training Configuration

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning Rate | 1e-4 |
| Weight Decay | 1e-5 |
| Scheduler | Cosine Annealing |
| Batch Size | 32 |
| Max Epochs | 50 |
| Early Stopping | 7 epochs patience |
| Loss Function | Focal Loss (α=0.75, γ=2.0) |

## Privacy & Security

### Differential Privacy (Opacus)
- **Epsilon (ε):** 8.0
- **Delta (δ):** 1e-5
- **Max Gradient Norm:** 1.0
- **Purpose:** Prevent model memorization of training data

### Adversarial Robustness (IBM ART)
- **Attack Method:** PGD (Projected Gradient Descent)
- **Perturbation Budget (ε):** 0.03
- **Step Size:** 0.007
- **Purpose:** Defend against adversarial patches

### Neural Network Watermarking
- **Method:** Weight sign modulation in classifier layer
- **Verification Threshold:** 85% bit accuracy
- **Purpose:** Detect unauthorized model copies

## Datasets

| Dataset | Real Videos | Fake Videos | Use |
|---------|-------------|-------------|-----|
| Celeb-DF v2 | 890 | 5,639 | Primary benchmark |
| FaceForensics++ | 1,000 | 4,000 | Multi-method training |
| DFDC | 19,154 | 100,000 | Scale testing |

## Performance Targets

| Metric | Target | Benchmark |
|--------|--------|-----------|
| Accuracy | ≥ 96% | Celeb-DF v2 |
| AUC | ≥ 0.98 | Celeb-DF v2 |
| FPR | < 2% | Cross-dataset |
| Inference Latency | < 3s | 90 frames, GPU |
