# BB-REP-001 Merge Report

## Sources
1. Busy Bee V2 user-supplied archive imported fully into `src/busy_bee` and preserved in `vendor/source_busy_bee_v2_snapshot`.
2. Busy Bee Holdings LLC governance/legal scaffold imported into `src/busy_bee_holdings_llc`.
3. BOD-personal Busy-Bee-V1.3 imported from `vendor/source_bod_personal_snapshot` (2026-03-19).

## Canonical entrypoint
- `app/api/main.py`

## Integration decisions
- Busy Bee V2 remains the primary application/ML/service package under `src/busy_bee`.
- Holdings governance, ownership, and legal-packaging logic lives under `src/busy_bee_holdings_llc`.
- Unified API exposes holdings endpoints and mounts the imported V2 app under `/v2`.
- BOD-personal V1.3 modules now mapped into canonical structure.

## V1.3 Module Mapping (Completed 2026-03-19)

### src/busy_bee_holdings_llc/
| Source (V1.3) | Canonical Path |
|--------------|----------------|
| psip.py, psip_config.py | `psip/` |
| layer1_strategic_intelligence_core/ | `layer1_strategic_intelligence_core/` |
| layer2_governance_layer/ | `layer2_governance_layer/` |
| layer3_domain_intelligence/ | `layer3_domain_intelligence/` |
| briefs_service.py | `briefing/service_v1_3.py` |
| finance_trade_intelligence_service.py | `integrations/finance_trade_intelligence_service.py` |
| tactical_trade_models.py | `integrations/tactical_trade_models.py` |

### src/busy_bee/
| Source (V1.3) | Canonical Path |
|--------------|----------------|
| infrastructure/ | `infrastructure/` |

## Preserved provenance
- `vendor/source_busy_bee_v2_snapshot/`
- `vendor/source_bod_personal_snapshot/` (original import)

## Status
- [x] BOD-personal import executed
- [x] PSIP/layer1-3 modules mapped
- [x] Integration complete
