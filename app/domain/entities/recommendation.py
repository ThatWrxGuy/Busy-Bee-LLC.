# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Recommendation Entity - Core domain entity for recommendations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Recommendation:
    """Core domain entity for recommendations.
    
    This is the internal representation. The ProductRecommendation DTO
    is the external-facing format.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = ""
    title: str = ""
    description: str = ""
    reasoning: str = ""  # Why generated
    expected_impact: str = ""  # Impact if implemented
    risk_assessment: str = ""  # Risk if ignored
    
    # Scoring
    urgency_score: int = 50  # 0-100
    impact_score: int = 50   # 0-100
    confidence_score: int = 50  # 0-100
    overall_score: int = 50  # Calculated
    
    # Status lifecycle
    status: str = "generated"  # generated → presented → approved/rejected/deferred → converted → completed → outcome
    created_at: datetime = field(default_factory=datetime.utcnow)
    presented_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    outcome_recorded_at: Optional[datetime] = None
    
    # Decision info
    decision_notes: str = ""
    decided_by: str = ""  # User who decided
    
    # Outcome tracking
    outcome_notes: str = ""
    outcome_success: Optional[bool] = None
    
    def calculate_overall_score(self) -> int:
        """Calculate overall priority score."""
        # Weighted average: urgency 40%, impact 35%, confidence 25%
        self.overall_score = int(
            self.urgency_score * 0.4 +
            self.impact_score * 0.35 +
            self.confidence_score * 0.25
        )
        return self.overall_score
    
    def present(self) -> None:
        """Mark as presented to user."""
        self.status = "presented"
        self.presented_at = datetime.utcnow()
    
    def approve(self, notes: str = "") -> None:
        """Approve the recommendation."""
        self.status = "approved"
        self.decided_at = datetime.utcnow()
        self.decision_notes = notes
    
    def reject(self, notes: str = "") -> None:
        """Reject the recommendation."""
        self.status = "rejected"
        self.decided_at = datetime.utcnow()
        self.decision_notes = notes
    
    def defer(self, notes: str = "") -> None:
        """Defer the recommendation."""
        self.status = "deferred"
        self.decided_at = datetime.utcnow()
        self.decision_notes = notes
    
    def convert_to_action(self) -> None:
        """Convert to actionable item."""
        self.status = "converted_to_action"
    
    def complete(self, notes: str = "") -> None:
        """Mark as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.outcome_notes = notes
        self.outcome_success = True
    
    def record_outcome(self, notes: str, success: bool) -> None:
        """Record the outcome."""
        self.status = "outcome_recorded"
        self.outcome_recorded_at = datetime.utcnow()
        self.outcome_notes = notes
        self.outcome_success = success
    
    def requires_approval(self) -> bool:
        """Check if this recommendation requires user approval."""
        # Financial recommendations always require approval
        if self.domain in ("finance", "wealth", "investment"):
            return True
        return self.urgency_score >= 70 or self.impact_score >= 70
