# Sentinels of Integrity — Security Model

## Overview

Sentinels of Integrity implements a **Zero-Trust Security Architecture**, where no component trusts any other component by default. Every interaction is authenticated, authorized, encrypted, and logged.

## Security Layers

### Layer 1: Browser Extension → API

| Control | Implementation | Purpose |
|---------|---------------|---------|
| Authentication | JWT RS256 (Rust signer) | Token forgery prevention |
| Transport | HTTPS / TLS 1.3 | Data-in-transit encryption |
| Origin Validation | CORS whitelist | Prevent unauthorized API access |
| Input Sanitization | Middleware + Pydantic | XSS, SQLi, path traversal defense |
| Rate Limiting | Redis sliding window | DDoS protection for GPU nodes |
| Privacy | Local SHA-256 hashing | No raw video ever uploaded |

### Layer 2: API → Data Layer

| Control | Implementation | Purpose |
|---------|---------------|---------|
| Encryption at Rest | AES-256-GCM (Rust) | Protect stored hashes |
| Database Auth | Connection string rotation | Prevent unauthorized DB access |
| Secrets Management | HashiCorp Vault (optional) | Centralized secret storage |
| Key Management | PEM files + Vault | RSA/AES key lifecycle |

### Layer 3: ML Engine Security

| Control | Implementation | Purpose |
|---------|---------------|---------|
| Differential Privacy | Opacus (ε=8.0, δ=1e-5) | Privacy-preserving training |
| Adversarial Defense | IBM ART library | Robustness against adversarial patches |
| Model Watermarking | Weight sign modulation | Anti-model-theft protection |
| Input Validation | Frame size/format checks | Prevent malformed input attacks |

### Layer 4: Blockchain Security

| Control | Implementation | Purpose |
|---------|---------------|---------|
| Multi-Sig Governance | 3-of-5 validators | Prevent unauthorized ledger updates |
| ZK-Proofs | Circom + Groth16 | Anonymous content verification |
| Merkle Trees | Chunk-level verification | Detect media chunk swapping |
| Immutable Records | Polygon zkEVM | Tamper-proof provenance |

### Layer 5: Infrastructure Security

| Control | Implementation | Purpose |
|---------|---------------|---------|
| Container Scanning | Trivy + Snyk | Vulnerability detection |
| Runtime Security | Falco IDS | Detect unauthorized processes |
| Immutable Logging | WORM storage | Tamper-proof audit trail |
| Network Policies | Kubernetes NetworkPolicies | Microservice isolation |

## Threat Model

### Threat 1: Token Forgery
- **Risk:** Attacker creates fake JWT tokens
- **Mitigation:** RS256 asymmetric signing (Rust core). Private key never leaves the server.
- **Detection:** JWT signature verification on every request

### Threat 2: Adversarial Patches
- **Risk:** Attacker adds imperceptible patches to fool the ML model
- **Mitigation:** IBM ART adversarial training + PGD attacks during training
- **Detection:** Adversarial patch detector in preprocessing pipeline

### Threat 3: Model Theft
- **Risk:** Competitor extracts and replicates the detection model
- **Mitigation:** Neural network watermarking, API rate limiting, model obfuscation
- **Detection:** Watermark verification on suspicious models

### Threat 4: DDoS on GPU Nodes
- **Risk:** Excessive requests overwhelm GPU inference
- **Mitigation:** Redis rate limiting (100 req/60s), request queuing
- **Detection:** Prometheus metrics + alerting

### Threat 5: Blockchain Manipulation
- **Risk:** Single validator corrupts ledger entries
- **Mitigation:** 3-of-5 multi-sig requirement for all updates
- **Detection:** On-chain event monitoring

### Threat 6: Data Exfiltration
- **Risk:** Attacker accesses stored media content
- **Mitigation:** Data minimization (only hashes stored, never raw media), AES-256-GCM encryption
- **Detection:** Falco rules for sensitive file access

## Security Directives (from Design.txt §6)

1. ✅ **Data Minimization:** Only SHA-256 hashes stored on the server. Never raw video.
2. ✅ **Memory Safety:** All critical crypto operations in Rust (prevents buffer overflows, use-after-free).
3. ✅ **Tamper-Proof Logging:** WORM logging with SHA-256 hash chains.
4. ✅ **Encryption at Rest:** AES-256-GCM via Rust core for all stored data.
5. ✅ **Input Sanitization:** All browser extension data treated as untrusted.
6. ✅ **Zero Trust:** No implicit trust between components.

## Compliance Considerations

- **GDPR:** No personal data is stored (only content hashes). Privacy by design.
- **C2PA:** Content Credentials standard compliance for provenance metadata.
- **SOC 2:** WORM logging + access controls support audit requirements.
