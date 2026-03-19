# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

from fastapi import FastAPI
from fastapi.routing import APIRouter

from busy_bee.api.app import create_app as create_v2_app
from busy_bee_holdings_llc.api.schemas import BriefRequest, DecisionRequest, DecisionResponse
from busy_bee_holdings_llc.briefing.service import ExecutiveBriefService
from busy_bee_holdings_llc.governance.engine import GovernanceEngine
from busy_bee_holdings_llc.governance.policy import load_default_policy
from busy_bee_holdings_llc.ownership.cap_table import default_cap_table

app = FastAPI(title="Busy Bee Holdings LLC", version="0.2.0")
policy = load_default_policy()
engine = GovernanceEngine(policy=policy, cap_table=default_cap_table())
brief_service = ExecutiveBriefService()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/repo/status")
def repo_status() -> dict[str, object]:
    return {
        "repository": "Busy_Bee_Holdings_LLC",
        "integrated_sources": ["Busy Bee V2", "Busy Bee Holdings LLC"],
        "bod_personal_import_ready": True,
    }

@app.post("/briefs/executive", response_model=DecisionResponse)
def executive_brief(payload: BriefRequest) -> DecisionResponse:
    brief = brief_service.generate(payload.model_dump())
    return DecisionResponse(approved=True, reason="brief_generated", brief=brief)

@app.post("/governance/decision", response_model=DecisionResponse)
def evaluate_decision(payload: DecisionRequest) -> DecisionResponse:
    return engine.evaluate(payload)

# Mount /v2 endpoints from the imported Busy Bee V2 app.
v2_app = create_v2_app()
app.mount("/v2", v2_app)
