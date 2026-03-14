# Sentinels of Integrity — API Reference

## Base URL

```
Development: http://localhost:8000/api/v1
Production:  https://api.sentinelsofintegrity.com/api/v1
```

## Authentication

All endpoints (except `/health`) require a JWT bearer token:

```
Authorization: Bearer <jwt_token>
```

Tokens are signed with RS256 (RSA + SHA-256). In development mode, unauthenticated requests are allowed for testing.

---

## Endpoints

### `GET /health`

Health check — liveness probe for Kubernetes.

**Response 200:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-13T10:30:00Z",
  "services": {
    "api": { "status": "up" },
    "database": { "status": "up" },
    "redis": { "status": "up" },
    "ml_engine": { "status": "up" },
    "blockchain_rpc": { "status": "up" }
  },
  "version": "v1"
}
```

---

### `GET /health/ready`

Readiness probe — returns 503 if critical dependencies are unavailable.

**Response 200:**
```json
{ "ready": true, "timestamp": "2026-03-13T10:30:00Z" }
```

---

### `POST /detect`

Submit media for deepfake detection and provenance verification.

**Request Body:**
```json
{
  "media_hash": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
  "media_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "platform": "youtube",
  "media_type": "video",
  "options": {
    "skip_blockchain": false,
    "detailed_report": false,
    "max_frames": 0,
    "confidence_threshold": 0.7
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `media_hash` | string (64 hex) | ✅ | SHA-256 hash computed client-side |
| `media_url` | string (URL) | ✅ | Media URL on the platform |
| `platform` | enum | ✅ | `youtube`, `twitter`, or `tiktok` |
| `media_type` | enum | ❌ | `video` (default), `image`, `audio` |
| `options` | object | ❌ | Analysis configuration |

**Response 200:**
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "media_hash": "abcdef...",
  "media_url": "https://...",
  "platform": "youtube",
  "sentinels_score": 85.3,
  "verdict": "authentic",
  "ml_result": {
    "is_synthetic": false,
    "confidence": 0.12,
    "artifacts": [],
    "model_version": "xception-gru-v1",
    "spatial": {
      "face_consistency_score": 0.95,
      "edge_artifact_score": 0.04,
      "faces_detected": 1
    },
    "temporal": {
      "temporal_consistency": 0.97,
      "frames_analyzed": 90,
      "anomaly_frames": []
    },
    "frequency": {
      "spectral_anomaly_score": 0.06,
      "ghosting_detected": false
    }
  },
  "blockchain_result": {
    "is_registered": true,
    "author": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD68",
    "registration_tx": "0xabc123...",
    "edit_history": [],
    "zk_verified": false
  },
  "status": "completed",
  "analyzed_at": "2026-03-13T10:30:00Z"
}
```

**Error Responses:**
- `422` — Validation error (invalid hash, URL, or platform)
- `429` — Rate limit exceeded
- `504` — Analysis timed out

---

### `GET /verify`

Blockchain hash lookup for content provenance.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `media_hash` | string (64 hex) | ✅ | SHA-256 hash to verify |
| `include_history` | boolean | ❌ | Include edit history (default: false) |

**Response 200:**
```json
{
  "content_hash": "abcdef...",
  "is_registered": true,
  "author": "0x742d35Cc...",
  "registration_tx": "0xabc123...",
  "edit_history": [
    {
      "editor": "0x...",
      "edit_hash": "def456...",
      "timestamp": "2026-03-10T08:00:00Z",
      "description": "Cropped and color corrected"
    }
  ],
  "zk_verified": false,
  "lookup_latency_ms": 45.2
}
```

**Target Latency:** < 500ms

---

### `POST /verify/register`

Register original content on the blockchain.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `media_hash` | string (64 hex) | ✅ | SHA-256 hash of original media |
| `creator_address` | string (42 chars) | ✅ | Ethereum address (0x...) |

---

### `GET /reports`

List past Trust Reports with pagination and filtering.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `platform` | string | — | Filter by platform |
| `verdict` | string | — | Filter by verdict |
| `limit` | int (1-100) | 20 | Max results |
| `offset` | int (≥0) | 0 | Pagination offset |

---

### `GET /reports/{report_id}`

Retrieve a full Trust Report by ID.

---

### `GET /reports/stats/summary`

Aggregated statistics across all analyses.

**Response 200:**
```json
{
  "total_analyses": 15420,
  "verdicts": { "authentic": 12801, "suspicious": 2100, "synthetic": 519 },
  "avg_score": 72.4,
  "avg_latency_ms": 1850.3
}
```

---

## Rate Limiting

All endpoints (except `/health`) are rate limited:
- **Default:** 100 requests per 60 seconds per IP
- **Headers:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`
- **Status:** `429 Too Many Requests` when exceeded

## Error Format

All errors follow this structure:
```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "detail": "Technical detail (if applicable)"
}
```
