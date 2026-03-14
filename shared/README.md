# 📦 Shared — Cross-Module Definitions

This directory contains shared schemas, type definitions, and constants used across all modules of Sentinels of Integrity.

## Structure

```
shared/
├── schemas/                    # Protobuf definitions
│   ├── trust_report.proto      # Trust Report (API → Extension)
│   ├── media_request.proto     # Media analysis request (Extension → API)
│   └── blockchain_event.proto  # Blockchain event schemas
├── types/
│   ├── index.d.ts              # TypeScript types (Extension + Node.js)
│   └── constants.py            # Python constants (API + ML Engine)
└── README.md
```

## Usage

### Python (Backend / ML Engine)
```python
from shared.types.constants import Platform, Verdict, ML_INPUT_SIZE
```

### TypeScript (Extension)
```typescript
import type { TrustReport, MediaAnalysisRequest } from '@shared/types';
```

## Guidelines

- **All cross-module data contracts** must be defined here first.
- **Protobuf schemas** are the source of truth — TypeScript and Python types should mirror them.
- **Constants** should never be duplicated across modules; import from here.
