# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""
Busy Bee Holdings LLC - Executive Intelligence Platform

This API implements BB-ARCH-PROD-001:
- Product Layer: Standardized DTOs for frontend consumption
- Application Layer: ExecutiveOrchestrator for decision compression
- Domain Layer: Core business entities and lifecycle

All endpoints return product DTOs only.
"""

from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from busy_bee.api.app import create_app as create_v2_app
from busy_bee_holdings_llc.api.schemas import BriefRequest, DecisionRequest, DecisionResponse
from busy_bee_holdings_llc.briefing.service import ExecutiveBriefService
from busy_bee_holdings_llc.governance.engine import GovernanceEngine
from busy_bee_holdings_llc.governance.policy import load_default_policy
from busy_bee_holdings_llc.ownership.cap_table import default_cap_table

# Product layer imports
from app.product import (
    ProductRecommendation,
    ExecutiveBrief,
    ExecutiveSystemView,
    DashboardView,
)
from app.application import ExecutiveOrchestrator

app = FastAPI(
    title="Busy Bee Holdings LLC",
    version="0.3.0",
    description="Executive Intelligence Platform - BB-ARCH-PROD-001 Compliant"
)
policy = load_default_policy()
engine = GovernanceEngine(policy=policy, cap_table=default_cap_table())
brief_service = ExecutiveBriefService()

# Initialize ExecutiveOrchestrator
orchestrator = ExecutiveOrchestrator()

# In-memory storage for recommendations (would be DB in production)
_recommendations_db: dict[str, ProductRecommendation] = {}


# ==================== HEALTH & STATUS ====================

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.3.0"}


@app.get("/repo/status")
def repo_status() -> dict[str, object]:
    return {
        "repository": "Busy_Bee_Holdings_LLC",
        "integrated_sources": ["Busy Bee V2", "Busy Bee Holdings LLC", "BOD-personal V1.3"],
        "bod_personal_import_ready": True,
        "product_layer_active": True,
    }


# ==================== BRIEFS (BB-ARCH-PROD-001) ====================

class GenerateBriefRequest(BaseModel):
    """Request to generate an executive brief."""
    period: str = "Weekly"
    include_domains: Optional[list[str]] = None


@app.get("/briefs/latest")
def get_latest_brief() -> dict:
    """Get the latest executive brief.
    
    Returns product-formatted brief in Executive Brief Contract format:
    - System Status
    - Strategic Posture
    - Top Priorities
    - Critical Risks
    - Domain Scores
    - Recommendations
    - Confidence Score
    """
    # Generate a brief using the orchestrator
    brief = orchestrator.generate_executive_brief(
        period="Weekly",
        title="Executive Brief"
    )
    return brief.to_dict()


@app.post("/briefs/generate")
def generate_brief(payload: GenerateBriefRequest) -> dict:
    """Generate a new executive brief."""
    brief = orchestrator.generate_executive_brief(
        period=payload.period,
        title="Executive Brief"
    )
    return brief.to_dict()


# ==================== RECOMMENDATIONS (BB-ARCH-PROD-001) ====================

class GenerateRecommendationRequest(BaseModel):
    """Request to generate a recommendation."""
    domain: str
    title: str
    why: str
    impact: str
    action_text: str
    urgency: str = "medium"
    confidence: int = 50
    risk_if_ignored: str = ""
    requires_approval: bool = True


@app.get("/recommendations")
def get_recommendations(
    domain: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """Get recommendations.
    
    Returns product-formatted recommendations only.
    Filters by domain and status if provided.
    """
    recs = list(_recommendations_db.values())
    
    if domain:
        recs = [r for r in recs if r.domain == domain]
    if status:
        recs = [r for r in recs if r.status == status]
    
    # Sort by urgency and confidence
    urgency_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    recs = sorted(
        recs,
        key=lambda r: (urgency_weights.get(r.urgency, 0), r.confidence),
        reverse=True
    )[:limit]
    
    return {
        "recommendations": [r.to_dict() for r in recs],
        "total": len(recs),
    }


@app.post("/recommendations/generate")
def generate_recommendation(payload: GenerateRecommendationRequest) -> dict:
    """Generate a new recommendation."""
    rec = ProductRecommendation(
        domain=payload.domain,
        title=payload.title,
        why=payload.why,
        impact=payload.impact,
        action_text=payload.action_text,
        urgency=payload.urgency,
        confidence=payload.confidence,
        risk_if_ignored=payload.risk_if_ignored,
        requires_approval=payload.requires_approval,
    ).present()
    
    _recommendations_db[rec.id] = rec
    
    # Also add to orchestrator
    orchestrator.add_recommendation(rec)
    
    return rec.to_dict()


@app.post("/recommendations/{rec_id}/approve")
def approve_recommendation(rec_id: str, notes: str = "") -> dict:
    """Approve a recommendation."""
    if rec_id not in _recommendations_db:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    rec = _recommendations_db[rec_id]
    rec.approve()
    
    return rec.to_dict()


@app.post("/recommendations/{rec_id}/reject")
def reject_recommendation(rec_id: str, notes: str = "") -> dict:
    """Reject a recommendation."""
    if rec_id not in _recommendations_db:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    rec = _recommendations_db[rec_id]
    rec.reject()
    
    return rec.to_dict()


@app.post("/recommendations/{rec_id}/defer")
def defer_recommendation(rec_id: str, notes: str = "") -> dict:
    """Defer a recommendation."""
    if rec_id not in _recommendations_db:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    rec = _recommendations_db[rec_id]
    rec.defer()
    
    return rec.to_dict()


# ==================== DOMAINS (BB-ARCH-PROD-001) ====================

@app.get("/domains")
def get_domains() -> dict:
    """Get all domain summaries."""
    # Get from orchestrator
    brief = orchestrator.generate_executive_brief()
    return {
        "domains": [
            {"name": domain, "score": score}
            for domain, score in brief.system_view.domain_scores.items()
        ]
    }


@app.get("/domains/{domain}")
def get_domain(domain: str) -> dict:
    """Get detailed domain information."""
    # Placeholder - would integrate with domain layer
    brief = orchestrator.generate_executive_brief()
    score = brief.system_view.domain_scores.get(domain, 50)
    
    # Get recommendations for this domain
    domain_recs = [
        r.to_dict() for r in _recommendations_db.values()
        if r.domain == domain
    ]
    
    return {
        "name": domain,
        "score": score,
        "recommendations": domain_recs,
    }


# ==================== SIGNALS (BB-ARCH-PROD-001) ====================

class SignalInput(BaseModel):
    """Signal input model."""
    domain: str
    type: str
    content: str
    priority: str = "info"


@app.post("/signals")
def add_signal(signal: SignalInput) -> dict:
    """Add a signal to the system."""
    orchestrator.add_signal(signal.model_dump())
    return {"status": "added", "signal": signal.model_dump()}


@app.get("/signals")
def get_signals(limit: int = 20) -> dict:
    """Get recent signals."""
    # Placeholder - would integrate with signal system
    return {"signals": [], "total": 0}


# ==================== DECISIONS (BB-ARCH-PROD-001) ====================

@app.get("/decisions")
def get_decisions(
    status: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """Get decision history."""
    recs = list(_recommendations_db.values())
    
    # Filter to decided recommendations
    decided = [r for r in recs if r.status in ("approved", "rejected", "deferred")]
    
    if status:
        decided = [r for r in decided if r.status == status]
    
    return {
        "decisions": [r.to_dict() for r in decided[:limit]],
        "total": len(decided),
    }


class OutcomeInput(BaseModel):
    """Record outcome of a decision."""
    recommendation_id: str
    success: bool
    notes: str = ""


@app.post("/outcomes")
def record_outcome(outcome: OutcomeInput) -> dict:
    """Record the outcome of a decision."""
    if outcome.recommendation_id not in _recommendations_db:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    rec = _recommendations_db[outcome.recommendation_id]
    rec.record_outcome()
    rec.outcome_notes = outcome.notes
    rec.outcome_success = outcome.success
    
    return rec.to_dict()


# ==================== LEGACY ENDPOINTS (Backward Compatible) ====================

@app.post("/briefs/executive", response_model=DecisionResponse)
def executive_brief_legacy(payload: BriefRequest) -> DecisionResponse:
    """Legacy endpoint - generates executive brief."""
    brief = brief_service.generate(payload.model_dump())
    return DecisionResponse(approved=True, reason="brief_generated", brief=brief)


@app.post("/governance/decision", response_model=DecisionResponse)
def evaluate_decision(payload: DecisionRequest) -> DecisionResponse:
    """Legacy endpoint - evaluate governance decision."""
    return engine.evaluate(payload)


# ==================== MOUNT V2 ====================

# Mount /v2 endpoints from the imported Busy Bee V2 app.
v2_app = create_v2_app()
app.mount("/v2", v2_app)

# Include chat API
from app.api.chat import router as chat_router
app.include_router(chat_router)
