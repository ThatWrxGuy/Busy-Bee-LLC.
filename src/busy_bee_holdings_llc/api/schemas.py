from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class BriefRequest(BaseModel):
    founder: str = "Christopher Jordon Byrne"
    posture: str = "Selective Advance"
    strategic_cycle_id: str = "cycle-001"
    summary: str = "Initial strategic cycle"
    focus_areas: list[str] = Field(default_factory=lambda: ["finance", "governance", "platform"])
    user_name: str | None = None
    goal: str | None = None
    risk_tolerance: str | None = None
    time_horizon_days: int | None = None

class DecisionRequest(BaseModel):
    action_type: str
    title: str
    description: str
    estimated_value_usd: float = 0.0
    executive_brief_present: bool = False
    founder_approved: bool = False
    trust_approved: bool = False
    board_supermajority: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

class DecisionResponse(BaseModel):
    approved: bool
    reason: str
    brief: dict[str, Any] | None = None
