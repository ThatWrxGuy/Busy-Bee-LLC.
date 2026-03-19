# BB-REP-001 Merge Report

## Sources
1. Busy Bee V2 user-supplied archive imported fully into `src/busy_bee` and preserved in `vendor/source_busy_bee_v2_snapshot`.
2. Busy Bee Holdings LLC governance/legal scaffold imported into `src/busy_bee_holdings_llc`.
3. BOD-personal Busy-Bee-V1.3 integration prepared via import target and snapshot metadata.

## Canonical entrypoint
- `app/api/main.py`

## Integration decisions
- Busy Bee V2 remains the primary application/ML/service package under `src/busy_bee`.
- Holdings governance, ownership, and legal-packaging logic lives under `src/busy_bee_holdings_llc`.
- Unified API exposes holdings endpoints and mounts the imported V2 app under `/v2`.
- BOD-personal remains import-ready because bulk upstream code retrieval was not executed during offline packaging.

## Preserved provenance
- `vendor/source_busy_bee_v2_snapshot/`
- `vendor/source_bod_personal_snapshot/README_snapshot.md`

## Next recommended merge step
Run the BOD-personal import helper in a network-enabled environment you control, review conflicts,
and map PSIP / layer1-3 modules into the canonical package layout.
