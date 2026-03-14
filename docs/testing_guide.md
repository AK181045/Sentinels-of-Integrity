# Sentinels of Integrity — Testing Guide

## Test Structure

```
tests/
├── conftest.py                    ← Shared fixtures
├── unit/
│   ├── test_detection_service.py  ← Detection orchestration
│   ├── test_blockchain_service.py ← Blockchain verification
│   ├── test_score_aggregator.py   ← Score computation
│   ├── test_trust_scorer.py       ← ML trust scoring
│   ├── test_schemas.py            ← Pydantic validation
│   ├── test_sanitizer.py          ← Input sanitization
│   ├── test_frame_extractor.py    ← Video frame extraction
│   ├── test_frequency_analyzer.py ← FFT/DCT analysis
│   ├── test_ml_models.py          ← CNN/GRU architecture
│   ├── test_watermark.py          ← Neural network watermarking
│   ├── test_steganography.py      ← DCT steganography
│   ├── test_metrics.py            ← ML metric computation
│   └── test_rust_hasher.py        ← Rust FFI boundary
├── integration/
│   ├── test_api_endpoints.py      ← Full API cycle
│   ├── test_middleware.py         ← Rate limiting + sanitization
│   └── test_ml_pipeline.py        ← ML pipeline end to end
└── e2e/
    └── test_full_detection_flow.py ← Extension → API → Report
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests only
pytest tests/e2e/ -v

# Specific test file
pytest tests/unit/test_score_aggregator.py -v

# With coverage
pytest tests/ --cov=api --cov=ml_models --cov-report=html

# Skip slow tests
pytest tests/ -v -m "not slow"

# Skip tests requiring Rust core
pytest tests/ -v -m "not rust"
```

## Test Categories

### Unit Tests (16 files)
- Pure function tests with no external dependencies
- Mock all external services (ML engine, blockchain RPC, database)
- Target: < 5 seconds total

### Integration Tests (3 files)
- Test component interactions (API middleware, ML pipeline)
- Use in-memory databases and mock services
- Target: < 30 seconds total

### E2E Tests (1 file)
- Full request/response cycle through FastAPI
- Simulate browser extension requests
- Tests all three platforms (YouTube, Twitter/X, TikTok)
- Target: < 60 seconds total

### Rust Core Tests
```bash
cd api/rust_core
cargo test
```
Tests hashing, encryption, signing, and cross-module workflows.

### Solidity Tests
```bash
cd contracts
npx hardhat test
```

## Key Test Scenarios

| Scenario | File | What It Tests |
|----------|------|---------------|
| Score boundaries | `test_score_aggregator.py` | Authentic ≥70, Suspicious 40-69, Synthetic <40 |
| Blockchain boost | `test_score_aggregator.py` | Registered content gets higher score |
| XSS prevention | `test_sanitizer.py` | Script tags rejected by middleware |
| SQL injection | `test_sanitizer.py` | DROP TABLE patterns detected |
| Schema validation | `test_schemas.py` | Invalid SHA-256 hashes rejected |
| Rate limiting | `test_middleware.py` | 429 returned when limit exceeded |
| ML pipeline | `test_ml_pipeline.py` | Frames → Faces → Frequency → Score |
| Watermark roundtrip | `test_watermark.py` | Embed then verify succeeds |
| Stego roundtrip | `test_steganography.py` | DCT embed/extract recovery |
| Full E2E flow | `test_full_detection_flow.py` | Extension → API → Trust Report |

## Writing New Tests

Follow this pattern:

```python
class TestFeatureName:
    @pytest.fixture
    def setup(self):
        return FeatureUnderTest()

    def test_happy_path(self, setup):
        result = setup.do_thing(valid_input)
        assert result.is_correct

    def test_edge_case(self, setup):
        result = setup.do_thing(edge_input)
        assert result.handles_gracefully

    def test_error_case(self, setup):
        with pytest.raises(ExpectedError):
            setup.do_thing(bad_input)
```
