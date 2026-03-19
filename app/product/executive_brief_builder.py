# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Executive Brief Builder - Convert intelligence to executive format."""

from typing import Any

from app.product.executive_brief_dto import (
    ExecutiveBrief, ExecutiveSystemView, DomainScore
)
from app.product.recommendation_dto import ProductRecommendation


class ExecutiveBriefBuilder:
    """Builds standardized executive briefs from internal intelligence.
    
    This component enforces the Executive Brief Contract by transforming
    raw intelligence outputs into human-consumable CEO-level summaries.
    """
    
    def __init__(self):
        self._domain_outputs: dict[str, Any] = {}
        self._recommendations: list[ProductRecommendation] = []
        self._signals: list[Any] = []
    
    def add_domain_output(self, domain: str, score: int, summary: str) -> "ExecutiveBriefBuilder":
        """Add domain intelligence output."""
        self._domain_outputs[domain] = {"score": score, "summary": summary}
        return self
    
    def add_recommendation(self, recommendation: ProductRecommendation) -> "ExecutiveBriefBuilder":
        """Add a recommendation to the brief."""
        self._recommendations.append(recommendation)
        return self
    
    def add_signal(self, signal: Any) -> "ExecutiveBriefBuilder":
        """Add a signal to the brief."""
        self._signals.append(signal)
        return self
    
    def build(
        self,
        period: str = "",
        title: str = "Executive Brief"
    ) -> ExecutiveBrief:
        """Build the final executive brief.
        
        This compresses all intelligence into the standardized format:
        - System Status
        - Strategic Posture
        - Top Priorities (max 3)
        - Critical Risks (max 3)
        - Domain Scores
        - Recommendations (max 5)
        - Confidence Score
        """
        # Determine system status
        system_status = self._calculate_system_status()
        
        # Determine strategic posture
        strategic_posture = self._calculate_strategic_posture()
        
        # Calculate domain scores
        domain_scores = self._calculate_domain_scores()
        
        # Determine top priorities (max 3)
        top_priorities = self._calculate_priorities()
        
        # Determine critical risks (max 3)
        critical_risks = self._calculate_risks()
        
        # Limit recommendations to top 5
        top_recommendations = sorted(
            self._recommendations,
            key=lambda r: (self._urgency_weight(r.urgency), -r.confidence),
            reverse=True
        )[:5]
        
        # Calculate confidence score
        confidence = self._calculate_confidence(top_recommendations)
        
        # Build system view
        system_view = ExecutiveSystemView(
            system_status=system_status,
            strategic_posture=strategic_posture,
            top_priorities=top_priorities,
            critical_risks=critical_risks,
            domain_scores=domain_scores,
            recommendations=top_recommendations,
            confidence_score=confidence,
        )
        
        return ExecutiveBrief(
            title=title,
            period=period,
            system_view=system_view,
        )
    
    def _calculate_system_status(self) -> str:
        """Calculate overall system status."""
        if not self._domain_outputs:
            return "operational"
        
        scores = [d["score"] for d in self._domain_outputs.values()]
        avg_score = sum(scores) / len(scores) if scores else 50
        
        if avg_score >= 70:
            return "operational"
        elif avg_score >= 40:
            return "degraded"
        else:
            return "offline"
    
    def _calculate_strategic_posture(self) -> str:
        """Calculate strategic posture based on recommendations."""
        if not self._recommendations:
            return "neutral"
        
        # Check for offensive vs defensive indicators
        urgent_count = sum(1 for r in self._recommendations if r.urgency == "critical")
        
        if urgent_count >= 2:
            return "defensive"
        elif urgent_count == 0:
            return "offensive"
        return "neutral"
    
    def _calculate_domain_scores(self) -> dict[str, int]:
        """Extract domain scores."""
        return {domain: data["score"] for domain, data in self._domain_outputs.items()}
    
    def _calculate_priorities(self) -> list[str]:
        """Extract top priorities from recommendations."""
        high_priority = [r for r in self._recommendations if r.urgency in ("critical", "high")]
        return [r.title for r in high_priority[:3]]
    
    def _calculate_risks(self) -> list[str]:
        """Extract critical risks from recommendations."""
        risks = [r.risk_if_ignored for r in self._recommendations if r.risk_if_ignored]
        return risks[:3]
    
    def _calculate_confidence(self, recommendations: list[ProductRecommendation]) -> int:
        """Calculate overall confidence score."""
        if not recommendations:
            return 50
        
        avg_confidence = sum(r.confidence for r in recommendations) / len(recommendations)
        return int(avg_confidence)
    
    def _urgency_weight(self, urgency: str) -> int:
        """Convert urgency to numeric weight for sorting."""
        weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return weights.get(urgency, 0)
