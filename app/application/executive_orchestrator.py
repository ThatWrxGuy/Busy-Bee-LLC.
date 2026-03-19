# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Executive Orchestrator - CEO Layer for Decision Compression.

This is the central intelligence authority that:
- Aggregates all domain outputs
- Resolves conflicts between recommendations
- Ranks by urgency, impact, risk
- Limits output to top items
- Determines system status and strategic posture
"""

from typing import Any, Optional
from dataclasses import dataclass, field

from app.product.executive_brief_dto import ExecutiveBrief, ExecutiveSystemView
from app.product.recommendation_dto import ProductRecommendation
from app.product.executive_brief_builder import ExecutiveBriefBuilder


@dataclass
class OrchestratorConfig:
    """Configuration for the ExecutiveOrchestrator."""
    max_priorities: int = 3
    max_risks: int = 3
    max_recommendations: int = 5
    min_confidence_threshold: int = 30


class ExecutiveOrchestrator:
    """Central authority for executive-level decision compression.
    
    This component implements the CORE ARCHITECTURAL PRINCIPLE:
    INTELLIGENCE → ORCHESTRATION → PRODUCT FORMATTING → USER DECISION → OUTCOME → LEARNING
    
    All intelligence outputs MUST pass through this orchestrator
    before being surfaced to users.
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self._brief_builder = ExecutiveBriefBuilder()
        self._domain_intelligence: dict[str, Any] = {}
        self._recommendations: list[ProductRecommendation] = []
        self._signals: list[Any] = []
    
    def aggregate_domain_output(
        self,
        domain: str,
        score: int,
        summary: str,
        recommendations: Optional[list[ProductRecommendation]] = None,
    ) -> "ExecutiveOrchestrator":
        """Aggregate domain intelligence output.
        
        This is the entry point for all domain intelligence.
        """
        self._domain_intelligence[domain] = {
            "score": score,
            "summary": summary,
            "recommendations": recommendations or [],
        }
        
        if recommendations:
            self._recommendations.extend(recommendations)
        
        return self
    
    def add_signal(self, signal: Any) -> "ExecutiveOrchestrator":
        """Add a signal to the orchestration context."""
        self._signals.append(signal)
        return self
    
    def add_recommendation(self, recommendation: ProductRecommendation) -> "ExecutiveOrchestrator":
        """Add a recommendation directly."""
        self._recommendations.append(recommendation)
        return self
    
    def generate_executive_brief(
        self,
        period: str = "",
        title: str = "Executive Brief",
    ) -> ExecutiveBrief:
        """Generate the standardized executive brief.
        
        This compresses all intelligence into the required format:
        - System Status
        - Strategic Posture
        - Top Priorities (max 3)
        - Critical Risks (max 3)
        - Domain Scores
        - Recommendations (max 5)
        - Confidence Score
        """
        # Build domain outputs
        for domain, data in self._domain_intelligence.items():
            self._brief_builder.add_domain_output(
                domain=domain,
                score=data["score"],
                summary=data["summary"],
            )
        
        # Add recommendations
        for rec in self._recommendations:
            self._brief_builder.add_recommendation(rec)
        
        # Add signals
        for sig in self._signals:
            self._brief_builder.add_signal(sig)
        
        # Build the brief
        brief = self._brief_builder.build(period=period, title=title)
        
        # Apply limits
        self._apply_limits(brief.system_view)
        
        return brief
    
    def generate_dashboard_view(self) -> dict:
        """Generate dashboard-ready view."""
        brief = self.generate_executive_brief()
        
        return {
            "system_status": brief.system_view.system_status,
            "strategic_posture": brief.system_view.strategic_posture,
            "confidence_score": brief.system_view.confidence_score,
            "domain_scores": brief.system_view.domain_scores,
            "top_recommendations": [
                r.to_dict() for r in brief.system_view.recommendations[:3]
            ],
        }
    
    def _apply_limits(self, system_view: ExecutiveSystemView) -> None:
        """Apply output limits to the system view."""
        # Limit priorities
        system_view.top_priorities = system_view.top_priorities[:self.config.max_priorities]
        
        # Limit risks
        system_view.critical_risks = system_view.critical_risks[:self.config.max_risks]
        
        # Limit recommendations
        system_view.recommendations = system_view.recommendations[:self.config.max_recommendations]
    
    def resolve_conflicts(
        self,
        recommendations: list[ProductRecommendation],
    ) -> list[ProductRecommendation]:
        """Resolve conflicts between recommendations.
        
        Returns deduplicated, prioritized list.
        """
        # Remove duplicates by domain + title
        seen: set[tuple[str, str]] = set()
        unique: list[ProductRecommendation] = []
        
        for rec in recommendations:
            key = (rec.domain, rec.title)
            if key not in seen:
                seen.add(key)
                unique.append(rec)
        
        # Sort by urgency and confidence
        urgency_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        return sorted(
            unique,
            key=lambda r: (
                urgency_weights.get(r.urgency, 0),
                r.confidence,
            ),
            reverse=True
        )
    
    def calculate_strategic_posture(
        self,
        domain_scores: dict[str, int],
        recommendations: list[ProductRecommendation],
    ) -> str:
        """Calculate the strategic posture."""
        if not domain_scores:
            return "neutral"
        
        avg_score = sum(domain_scores.values()) / len(domain_scores)
        
        # Check for urgent recommendations
        urgent = sum(1 for r in recommendations if r.urgency == "critical")
        
        if avg_score < 40 or urgent >= 2:
            return "defensive"
        elif avg_score > 70 and urgent == 0:
            return "offensive"
        elif urgent > 0:
            return "opportunistic"
        
        return "neutral"
    
    def get_pending_approvals(
        self,
        recommendations: Optional[list[ProductRecommendation]] = None,
    ) -> list[ProductRecommendation]:
        """Get recommendations that require user approval."""
        recs = recommendations or self._recommendations
        return [
            r for r in recs
            if r.requires_approval and r.status in ("generated", "presented")
        ]
    
    def reset(self) -> None:
        """Reset the orchestrator state."""
        self._domain_intelligence = {}
        self._recommendations = []
        self._signals = []
        self._brief_builder = ExecutiveBriefBuilder()
