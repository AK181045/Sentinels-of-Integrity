# 🛡️ Sentinels of Integrity

> **AI-Powered Truth Guard** — Real-time defense against synthetic media.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Rust 1.80+](https://img.shields.io/badge/Rust-1.80+-orange.svg)](https://rust-lang.org)
[![Polygon zkEVM](https://img.shields.io/badge/Blockchain-Polygon%20zkEVM-purple.svg)](https://polygon.technology)

---

## 🎯 What Is This?

Sentinels of Integrity is a **three-pillar system** that detects deepfakes and verifies media authenticity in real time:

| Pillar | Technology | Purpose |
|--------|-----------|---------|
| 🧠 **ML Detection Engine** | Xception CNN + Bi-GRU | Frame-by-frame deepfake analysis with ≥96% accuracy |
| 🔗 **Blockchain Vault** | Polygon zkEVM + Circom ZK | Cryptographic provenance & content registration |
| 🌐 **Browser Extension** | React + Manifest V3 | Real-time Trust HUD overlay on YouTube, X, TikTok |

---

## 🏗️ Architecture

```
Extension → API → ML Inference + Blockchain Lookup → Sentinels Score → Trust HUD
```

1. **Extension** sends media URL/hash to the API
2. **API** triggers ML inference and blockchain lookup in parallel
3. **ML Engine** returns `{is_synthetic, confidence, artifacts}`
4. **Blockchain** returns `{is_registered, author, edit_history}`
5. **Score Aggregator** combines results into a **Sentinels Score (0–100)**
6. **Extension** renders the Trust HUD overlay on the video

---

## 📁 Project Structure

```
├── api/            # Zero-Trust Backend (Rust core + FastAPI)
├── ml_models/      # ML Training & Inference (PyTorch)
├── contracts/      # Solidity Smart Contracts + ZK Circuits
├── extension/      # Hardened Browser Extension (React/Vite)
├── shared/         # Shared Protobuf schemas & type definitions
├── infra/          # Docker, Kubernetes, monitoring, security
├── tests/          # Unit, integration, and E2E tests
└── docs/           # Architecture, API reference, deployment guides
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+
- **Rust** 1.80+
- **Node.js** 18+
- **Docker** & Docker Compose
- **Hardhat** (for smart contracts)

### 1. Clone & Setup

```bash
git clone https://github.com/your-org/sentinels-of-integrity.git
cd sentinels-of-integrity
```

### 2. Start All Services (Docker)

```bash
docker-compose -f infra/docker-compose.yml up --build
```

### 3. Run Individual Components

```bash
# Backend API
cd api && pip install -r requirements.txt && uvicorn app.main:app --reload

# ML Engine
cd ml_models && pip install -r requirements.txt && python -m training.train

# Smart Contracts
cd contracts && npm install && npx hardhat compile

# Browser Extension
cd extension && npm install && npm run dev
```

---

## 🔒 Security

- **Data Minimization**: Never stores raw video — SHA-256 hashes only
- **Memory Safety**: Critical crypto primitives written in Rust
- **Encryption**: AES-256-GCM for all data at rest
- **Adversarial Defense**: IBM ART robustness + adversarial patch detection
- **Differential Privacy**: Opacus during model training
- **ZK Privacy**: Circom zero-knowledge proofs for anonymous verification
- **Extension Hardening**: CSP, SRI, code obfuscation, local-first hashing

---

## 🎯 KPIs

| Metric | Target |
|--------|--------|
| Detection Accuracy | ≥ 96% on Celeb-DF v2 |
| Hash Lookup Latency | < 500ms |
| Full ML Scan Latency | < 3 seconds |
| Daily Verifications | ≥ 5 per active user |

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
