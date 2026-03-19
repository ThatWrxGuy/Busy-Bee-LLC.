# BB-ARCH-PROD-002 — Phase 1 Restructure

## Purpose

This package executes **Phase 1** of the Busy Bee dual-track architecture:

- establish a monorepo layout
- separate product entry points from shared intelligence
- prepare the codebase for later tenant context, SaaS isolation, and connector scoping
- preserve backward compatibility where practical during migration

## Target Structure

```text
apps/
  busybee-saas/
  busybee-personal/
packages/
  contracts/
  ml-intelligence/
  core-agents/
  orchestration/
  strategy-engine/
  governance/
  connectors/
  domain-finance/
  domain-health/
  domain-career/
  ui-system/
infrastructure/
  auth/
  tenant/
  billing/
  observability/
  data/
```

## Phase 1 Scope

1. Create monorepo folders.
2. Move shared ML code from `app/ml` to `packages/ml-intelligence/app/ml`.
3. Leave compatibility shims at `app/ml/*` so existing imports keep working during transition.
4. Create two product entry points:
   - `apps/busybee-saas`
   - `apps/busybee-personal`
5. Add the first shared runtime contract:
   - `TenantContext`
6. Create package placeholders for later phases.

## Migration Policy

### Non-negotiable rule

All intelligence must live in `packages/`, not in `apps/`.

### Apps are allowed to own

- HTTP / UI entry points
- auth/session bootstrap
- request parsing
- product-specific composition

### Apps are not allowed to own

- agent logic
- model training/inference logic
- domain scoring logic
- governance decisions
- connector business logic

## Compatibility Strategy

The included migration script writes a shim `app/ml/__init__.py` that re-exports from `packages.ml_intelligence.app.ml`.

That means old imports such as:

```python
from app.ml.inference.gateway import InferenceGateway
```

can continue to work temporarily after the move, while new code should be updated toward the package path.

## Immediate Next Step After Phase 1

Phase 2 should introduce:

- `TenantContext` injection through request lifecycle
- SaaS middleware enforcing tenant scope
- per-tenant connector credential isolation
- app import boundary lint rules

## Execution

Run from the repository root:

```bash
python scripts/phase1_restructure.py
```

## Notes

- The script is conservative. It creates missing directories and only moves `app/ml` if present.
- Existing files are not overwritten unless they are known generated placeholders/shims.
- If your repo layout differs, adjust the move map inside the script before execution.
