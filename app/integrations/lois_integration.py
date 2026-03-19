# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""LOIS Integration Layer - Sync between Busy Bee and LOIS frontend."""

from typing import Optional
import uuid
from datetime import datetime

from app.product import ProductRecommendation


# LOIS Hive mapping
LOIS_HIVE_MAP = {
    "finance": "Money Hive",
    "health": "Vital Hive", 
    "career": "Career Hive",
    "relationships": "Bond Hive",
    "mind": "Mind Hive",
    "life": "Life Hive",
}

LOIS_URGENCY_MAP = {
    "critical": "Critical",
    "high": "High", 
    "medium": "Medium",
    "low": "Low",
}


def busybee_to_lois_recommendation(rec: ProductRecommendation) -> dict:
    """Convert Busy Bee ProductRecommendation to LOIS format.
    
    Args:
        rec: ProductRecommendation from Busy Bee
        
    Returns:
        Dictionary in LOIS AddRecommendation format
    """
    return {
        "id": rec.id,
        "hive": LOIS_HIVE_MAP.get(rec.domain, "Life Hive"),
        "urgency": LOIS_URGENCY_MAP.get(rec.urgency, "Medium"),
        "title": rec.title,
        "intelligence_signal": rec.why,
        "impact": rec.impact,
        "risk_if_ignored": rec.risk_if_ignored,
        "action_step": rec.action_text,
        "requires_approval": rec.requires_approval,
        "confidence": rec.confidence,
        "status": rec.status,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
        "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
    }


def lois_to_busybee_recommendation(data: dict) -> ProductRecommendation:
    """Convert LOIS recommendation to Busy Bee ProductRecommendation.
    
    Args:
        data: Dictionary from LOIS AddRecommendation form
        
    Returns:
        ProductRecommendation
    """
    # Reverse map hive to domain
    hive_to_domain = {v: k for k, v in LOIS_HIVE_MAP.items()}
    
    return ProductRecommendation(
        id=data.get("id", str(uuid.uuid4())),
        domain=hive_to_domain.get(data.get("hive"), "life"),
        title=data.get("title", ""),
        why=data.get("intelligence_signal", ""),
        impact=data.get("impact", ""),
        action_text=data.get("action_step", ""),
        urgency=data.get("urgency", "medium").lower(),
        confidence=data.get("confidence", 50),
        risk_if_ignored=data.get("risk_if_ignored", ""),
        requires_approval=data.get("requires_approval", True),
    )


class LOISIntegration:
    """Integration layer for syncing between Busy Bee and LOIS.
    
    This class handles:
    1. Format conversion between systems
    2. Bidirectional sync
    3. Chat message formatting
    """
    
    def __init__(self, lois_base_url: str = "https://lois-life-operating-intelligence-s-c8a842a9.base44.app"):
        self.lois_base_url = lois_base_url
    
    def format_for_lois(self, recommendation: ProductRecommendation) -> dict:
        """Format recommendation for LOIS."""
        return busybee_to_lois_recommendation(recommendation)
    
    def format_chat_response(self, recommendation: ProductRecommendation) -> str:
        """Format a recommendation as a chat response."""
        hive = LOIS_HIVE_MAP.get(recommendation.domain, "Life Hive")
        urgency_emoji = {
            "critical": "🔴",
            "high": "🟠", 
            "medium": "🟡",
            "low": "🟢"
        }.get(recommendation.urgency, "⚪")
        
        return f"""## {urgency_emoji} {recommendation.title}

**{hive}** | Confidence: {recommendation.confidence}%

{recommendation.why}

### Action
{recommendation.action_text}

### Risk if Ignored
{recommendation.risk_if_ignored}

---
*Status: {recommendation.status.upper()}*"""
    
    def format_executive_brief_chat(self, brief_dict: dict) -> str:
        """Format executive brief as chat message."""
        sv = brief_dict.get("system_view", {})
        
        status_emoji = {
            "operational": "🟢",
            "degraded": "🟡", 
            "offline": "🔴"
        }.get(sv.get("system_status"), "⚪")
        
        posture_emoji = {
            "offensive": "🟢",
            "defensive": "🔴",
            "neutral": "⚪",
            "opportunistic": "🟠"
        }.get(sv.get("strategic_posture"), "⚪")
        
        lines = [
            "# 🐝 EXECUTIVE BRIEF",
            "",
            f"**Status:** {status_emoji} {sv.get('system_status', 'unknown').upper()}",
            f"**Posture:** {posture_emoji} {sv.get('strategic_posture', 'neutral').upper()}",
            f"**Confidence:** {sv.get('confidence_score', 0)}%",
            "",
            "## 🚨 TOP PRIORITIES",
        ]
        
        for i, p in enumerate(sv.get("top_priorities", []), 1):
            lines.append(f"{i}. {p}")
        
        lines.extend([
            "",
            "## ⚠️ CRITICAL RISKS",
        ])
        
        for r in sv.get("critical_risks", []):
            lines.append(f"- {r}")
        
        lines.extend([
            "",
            "## 📊 DOMAIN SCORES",
        ])
        
        for domain, score in sv.get("domain_scores", {}).items():
            hive = LOIS_HIVE_MAP.get(domain, domain.title())
            lines.append(f"- **{hive}:** {score}/100")
        
        lines.extend([
            "",
            "## 📋 RECOMMENDATIONS",
        ])
        
        for rec in sv.get("recommendations", []):
            lines.append(f"### {rec.get('title', 'Untitled')}")
            lines.append(f"Domain: {rec.get('domain', 'N/A')} | Urgency: {rec.get('urgency', 'N/A')}")
            lines.append(f"Action: {rec.get('action_text', 'N/A')}")
            lines.append("")
        
        return "\n".join(lines)


# Singleton instance
lois_integration = LOISIntegration()


__all__ = [
    "LOISIntegration",
    "lois_integration", 
    "busybee_to_lois_recommendation",
    "lois_to_busybee_recommendation",
]
