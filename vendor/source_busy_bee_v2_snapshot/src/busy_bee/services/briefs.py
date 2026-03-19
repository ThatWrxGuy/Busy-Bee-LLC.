from __future__ import annotations

from busy_bee.domain.service import DomainIntelligenceService
from busy_bee.schemas.briefs import ExecutiveBrief, StrategicRecommendation


class BriefService:
    def __init__(self) -> None:
        self.domain_service = DomainIntelligenceService()

    def generate_executive_brief(self) -> ExecutiveBrief:
        recs = self.domain_service.generate_recommendations()
        return ExecutiveBrief(
            system_status="Healthy",
            strategic_posture="Selective Advance",
            top_priorities=[
                "Stabilize operating cadence across all domains",
                "Keep human approval in the loop for finance actions",
                "Expand signal ingestion and real scoring logic",
            ],
            recommendations=[
                StrategicRecommendation(
                    id=rec.id,
                    domain=rec.domain,
                    title=rec.title,
                    rationale=rec.rationale,
                    requires_human_approval=rec.requires_human_approval,
                )
                for rec in recs
            ],
        )
