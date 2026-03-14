# Sentinels of Integrity — Deployment Guide

## Prerequisites

- Docker & Docker Compose v2+
- Node.js 18+ (for extension and contracts)
- Python 3.11+ (for backend and ML)
- Rust 1.75+ (for core crypto)
- PostgreSQL 16+ (or use Docker)
- Redis 7+ (or use Docker)

---

## Quick Start (Development)

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/sentinels-of-integrity.git
cd sentinels-of-integrity
```

### 2. Backend API

```bash
# Create virtual environment
cd api
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Build Rust core
cd rust_core
cargo build --release
maturin develop --release
cd ..

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Generate RSA keys for JWT
mkdir -p keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem

# Generate AES key
python -c "import secrets; open('keys/aes.key','wb').write(secrets.token_bytes(32))"

# Run the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Database & Redis (Docker)

```bash
# From project root
cd infra
docker-compose up -d db redis
```

### 4. Smart Contracts

```bash
cd contracts
npm install
npx hardhat compile
npx hardhat test
# Deploy to local network:
npx hardhat run scripts/deploy.js --network hardhat
```

### 5. Browser Extension

```bash
cd extension
npm install
npm run build
# Load the `dist/` folder as an unpacked extension in chrome://extensions
```

---

## Docker Compose (Full Stack)

```bash
cd infra
docker-compose up --build
```

This starts:
- **API** on port 8000
- **ML Engine** on port 8001
- **PostgreSQL** on port 5432
- **Redis** on port 6379

---

## Production Deployment (Kubernetes)

### 1. Build and Push Images

```bash
docker build -t sentinels/api:latest ./api
docker build -t sentinels/ml:latest ./ml_models
docker push sentinels/api:latest
docker push sentinels/ml:latest
```

### 2. Deploy to Kubernetes

```bash
kubectl apply -f infra/k8s/redis-deployment.yaml
kubectl apply -f infra/k8s/api-deployment.yaml
kubectl apply -f infra/k8s/ml-deployment.yaml
```

### 3. Deploy Smart Contracts

```bash
cd contracts
BLOCKCHAIN_PRIVATE_KEY=0x... npx hardhat run scripts/deploy.js --network polygon_zkevm_testnet
```

### 4. Security Setup

```bash
# Install Falco for runtime security
helm install falco falcosecurity/falco -f infra/monitoring/falco-rules.yaml

# Configure Prometheus
kubectl apply -f infra/monitoring/prometheus.yml

# Enable Trivy scanning
trivy image --config infra/security/trivy-config.yaml sentinels/api:latest
```

---

## Environment Variables

See `api/.env.example` for the complete list. Critical variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `JWT_PRIVATE_KEY_PATH` | Path to RSA private key (PEM) | ✅ |
| `JWT_PUBLIC_KEY_PATH` | Path to RSA public key (PEM) | ✅ |
| `AES_KEY_PATH` | Path to AES-256 key file | ✅ |
| `ML_ENGINE_URL` | ML inference service URL | ✅ |
| `BLOCKCHAIN_RPC_URL` | Polygon zkEVM RPC endpoint | Production |
| `VAULT_ENABLED` | Enable HashiCorp Vault | Production |

---

## Running Tests

```bash
# Python tests (from project root)
pip install pytest pytest-asyncio httpx
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run E2E tests
pytest tests/e2e/ -v

# Run Rust tests
cd api/rust_core
cargo test

# Run Solidity tests
cd contracts
npx hardhat test
```
