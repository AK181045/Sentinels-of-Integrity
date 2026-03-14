# Sentinels of Integrity — Architecture Overview

## System Architecture

Sentinels of Integrity is a multi-layered deepfake detection and content provenance platform. The system follows a **microservices architecture** with five primary subsystems:

```
┌────────────────────────────────────────────────────────────────────┐
│                    BROWSER EXTENSION (Shield)                       │
│  React + Manifest V3 | Content Scripts | Trust HUD Overlay          │
│  Local SHA-256 hashing (no raw video upload)                        │
└──────────────────────────┬─────────────────────────────────────────┘
                           │ REST API (HTTPS + JWT RS256)
┌──────────────────────────▼─────────────────────────────────────────┐
│                    FASTAPI BACKEND (Gateway)                        │
│  Routes | Middleware (CORS, Rate Limiter, Sanitizer) | Auth         │
│  Orchestrator: dispatches ML + Blockchain in parallel               │
│  Rust Core FFI (SHA-256, AES-256-GCM, RSA signing)                  │
└────────┬───────────────────────────────────────┬───────────────────┘
         │                                       │
┌────────▼────────────┐              ┌──────────▼──────────────────┐
│   ML ENGINE (Brain) │              │   BLOCKCHAIN (Vault)         │
│  Xception CNN        │              │   Polygon zkEVM              │
│  Bi-directional GRU  │              │   IntegrityHash contract     │
│  Frequency Analyzer  │              │   ContentRegistry contract   │
│  Ensemble Fusion     │              │   MultiSig 3-of-5 validation │
│  Opacus DP training  │              │   ZK-Proofs (Circom)         │
│  ART adversarial     │              │   Merkle Tree chunk verify   │
└─────────────────────┘              └─────────────────────────────┘
```

## Data Flow

```
Step 1: Extension captures media URL → computes SHA-256 hash locally
Step 2: Sends { hash, url, platform } to API (JWT-authenticated)
Step 3: API dispatches two parallel tasks:
        ├── ML_INFERENCE → { is_synthetic, confidence, artifacts }
        └── BLOCKCHAIN_LOOKUP → { is_registered, author, edit_history }
Step 4: Score Aggregator combines results:
        └── Weighted fusion: ML(50%) + Spatial(15%) + Temporal(15%) + Frequency(10%) + Blockchain(10%)
Step 5: Returns Trust Report with Sentinels Score (0-100) and Verdict
Step 6: Extension displays Trust HUD overlay on the video
```

## Subsystem Details

### 1. Browser Extension (The Shield)
- **Technology**: React + Vite + Manifest V3
- **Privacy**: Local-first SHA-256 hashing — no raw video ever leaves the browser
- **Security**: Content Security Policy, Subresource Integrity, code obfuscation
- **Platforms**: YouTube, Twitter/X, TikTok

### 2. Backend API (The Gateway)
- **Technology**: Python FastAPI + Rust Core (PyO3 FFI)
- **Authentication**: JWT RS256 via Rust signer
- **Input Security**: All extension data treated as untrusted (sanitization middleware)
- **Rate Limiting**: Redis sliding window to protect GPU nodes from DDoS
- **Encryption**: AES-256-GCM for data at rest via Rust encryption module

### 3. ML Engine (The Brain)
- **Spatial Analysis**: Xception CNN (depthwise separable convolutions, 299x299 input)
- **Temporal Analysis**: Bi-directional GRU with attention mechanism
- **Frequency Analysis**: FFT/DCT spectral ghosting detection
- **Ensemble**: Learned fusion layer combining all three signals
- **Privacy**: Opacus differential privacy (ε=8.0, δ=1e-5)
- **Robustness**: IBM ART adversarial training + patch detection
- **Anti-Theft**: Neural network watermarking via weight sign modulation

### 4. Blockchain (The Vault)
- **Network**: Polygon zkEVM (low gas, EVM compatible)
- **Contracts**: IntegrityHash, ContentRegistry, MultiSigValidator, ZKVerifier, MerkleProof
- **Standard**: C2PA-compatible metadata storage
- **Governance**: 3-of-5 multi-signature validator approvals
- **Privacy**: Zero-knowledge proofs for anonymous verification

### 5. Infrastructure (The Fortress)
- **Orchestration**: Docker Compose (dev) + Kubernetes (production)
- **Monitoring**: Prometheus metrics + Falco runtime IDS
- **Security**: Trivy/Snyk container scanning
- **Logging**: WORM (Write Once Read Many) immutable logs with SHA-256 chain verification

## Security Architecture

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| Extension → API | JWT RS256 + CORS | Authentication & origin validation |
| API Input | Sanitization middleware | XSS, SQLi, path traversal prevention |
| API → ML/Blockchain | Internal network + mTLS | Service-to-service security |
| Data at Rest | AES-256-GCM (Rust) | Encryption of stored hashes |
| ML Training | Opacus DP | Privacy-preserving model training |
| Blockchain | ZK-Proofs | Anonymous content verification |
| Infrastructure | Falco + Trivy + WORM | Runtime protection & audit trail |

## Performance Targets (KPIs)

| Metric | Target | Measured At |
|--------|--------|-------------|
| Detection Accuracy | ≥ 96% | Celeb-DF v2 benchmark |
| API Response (hash lookup) | < 500ms | Blockchain verification |
| API Response (full ML scan) | < 3s | End-to-end detection |
| False Positive Rate | < 2% | Production monitoring |
| Extension Memory | < 50MB | Chrome Task Manager |
