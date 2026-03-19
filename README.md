# Busy Bee Holdings LLC

Unified repository scaffold for the Busy Bee platform.

This package merges three layers into one GitHub-ready repository:
- Busy Bee V2 source code imported into `src/busy_bee`
- Busy Bee Holdings governance, cap table, and legal system imported into `src/busy_bee_holdings_llc`
- BOD-personal Busy-Bee-V1.3 integration targets and import directives under `imports/bod_personal_v13/`

## What is included
- Unified FastAPI entrypoint at `app/api/main.py`
- Governance engine with dual-key and board-supermajority checks
- Executive brief endpoint and bridge layer
- Cap table / ownership defaults for Busy Bee Holdings LLC
- Legal templates, proprietary license file, and third-party notices
- Source provenance preserved in `vendor/`

## Important licensing note
This repository applies a proprietary wrapper to new Busy Bee Holdings LLC materials.
Third-party and upstream source rights must still be respected. Public-source imports from BOD-personal should only be completed if you control or are authorized to use that upstream repository.

## Quickstart
```bash
pip install -e .[dev]
uvicorn app.api.main:app --reload
pytest
```
