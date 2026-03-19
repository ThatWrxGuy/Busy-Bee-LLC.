# BB-ARCH-PROD-002: Phase 1 Restructure

## Status: ✅ Complete

This document describes the Phase 1 restructure of the Busy Bee monorepo.

## New Structure

```
busy-bee-llc/
├── apps/                          # Product entry points
│   ├── busybee-saas/              # SaaS product (future)
│   └── busybee-personal/          # Personal product (future)
├── packages/                      # Shared intelligence (MUST live here)
│   ├── ml-intelligence/          # BB-INT-ML-001 ML layer
│   ├── contracts/                # Shared contracts (TenantContext)
│   ├── core-agents/              # Agent implementations
│   ├── orchestration/            # Agent orchestration
│   ├── strategy-engine/          # Strategy tournament
│   ├── governance/               # Governance policies
│   ├── connectors/               # External integrations
│   ├── domain-finance/           # Finance domain
│   ├── domain-health/           # Health domain
│   ├── domain-career/           # Career domain
│   └── ui-system/               # Shared UI components
├── infrastructure/               # Cross-cutting infrastructure
│   ├── auth/                     # Authentication
│   ├── tenant/                   # Tenant management
│   ├── billing/                  # Billing (SaaS)
│   ├── observability/            # Logging, metrics
│   └── data/                     # Data pipelines
├── app/                          # Legacy compatibility shims
│   └── ml/                       # Re-exports from packages/ml-intelligence
└── docs/                         # Architecture documentation
```

## Key Principles

### Apps Own (HTTP/UI)
- HTTP / UI entry points
- Auth/session bootstrap
- Request parsing
- Product-specific composition

### Packages Own (Intelligence)
- Agent logic
- Model training/inference
- Domain scoring
- Governance decisions
- Connector business logic

## Migration Status

| Component | Old Location | New Location | Status |
|-----------|-------------|--------------|--------|
| ML Layer | `app/ml/*` | `packages/ml-intelligence/app/ml/*` | ✅ Moved |
| TenantContext | N/A | `packages/contracts/` | ✅ Created |
| SaaS App | N/A | `apps/busybee-saas/` | ✅ Created |
| Personal App | N/A | `apps/busybee-personal/` | ✅ Created |

## Backward Compatibility

The `app/ml/__init__.py` module re-exports from `packages/ml_intelligence.app.ml`:

```python
# Old import (still works)
from app.ml.inference.gateway import InferenceGateway

# New import (preferred)
from packages.ml_intelligence.app.ml.inference.gateway import InferenceGateway
```

## Phase 2 (Next)

- TenantContext injection through request lifecycle
- SaaS middleware enforcing tenant scope
- Per-tenant connector credential isolation
- App import boundary lint rules

## References

- [BB-ARCH-PROD-002 Full Specification](./docs/BB-ARCH-PROD-002_Phase_1_Restructure.md)
- [BB-INT-ML-001 ML Intelligence Layer](./docs/BB-INT-ML-001_Machine_Learning_Intelligence_Layer.md)
