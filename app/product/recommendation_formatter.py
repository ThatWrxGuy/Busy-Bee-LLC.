# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Recommendation Formatter - Convert internal recommendations to product format."""

from typing import Any, Optional

from app.product.recommendation_dto import ProductRecommendation, UrgencyLevel


class RecommendationFormatter:
    """Formats internal recommendations into ProductRecommendation DTOs.
    
    This ensures all recommendations conform to the product contract
    before being surfaced to users.
    """
    
    def format(
        self,
        domain: str,
        title: str,
        why: str,
        impact: str,
        action_text: str,
        urgency: UrgencyLevel = "medium",
        confidence: int = 50,
        risk_if_ignored: str = "",
        requires_approval: bool = True,
    ) -> ProductRecommendation:
        """Format an internal recommendation into product DTO."""
        return ProductRecommendation(
            domain=domain,
            title=title,
            why=why,
            impact=impact,
            action_text=action_text,
            urgency=urgency,
            confidence=confidence,
            risk_if_ignored=risk_if_ignored,
            requires_approval=requires_approval,
        )
    
    def format_from_dict(self, data: dict[str, Any]) -> ProductRecommendation:
        """Format a dictionary into ProductRecommendation."""
        return ProductRecommendation(
            id=data.get("id", ""),
            domain=data.get("domain", ""),
            title=data.get("title", ""),
            why=data.get("why", ""),
            impact=data.get("impact", ""),
            urgency=data.get("urgency", "medium"),
            action_text=data.get("action_text", ""),
            requires_approval=data.get("requires_approval", True),
            confidence=data.get("confidence", 50),
            risk_if_ignored=data.get("risk_if_ignored", ""),
        )
    
    def rank_recommendations(
        self,
        recommendations: list[ProductRecommendation],
        max_items: int = 5,
    ) -> list[ProductRecommendation]:
        """Rank and limit recommendations.
        
        Priority order:
        1. Urgency (critical > high > medium > low)
        2. Confidence (higher first)
        3. Impact (larger first)
        """
        urgency_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        ranked = sorted(
            recommendations,
            key=lambda r: (
                urgency_weights.get(r.urgency, 0),
                r.confidence,
                len(r.impact) if r.impact else 0,
            ),
            reverse=True
        )
        
        return ranked[:max_items]
    
    def filter_by_domain(
        self,
        recommendations: list[ProductRecommendation],
        domain: str,
    ) -> list[ProductRecommendation]:
        """Filter recommendations by domain."""
        return [r for r in recommendations if r.domain == domain]
    
    def filter_pending(
        self,
        recommendations: list[ProductRecommendation],
    ) -> list[ProductRecommendation]:
        """Filter to pending recommendations (generated, presented)."""
        pending_statuses = ("generated", "presented")
        return [r for r in recommendations if r.status in pending_statuses]
