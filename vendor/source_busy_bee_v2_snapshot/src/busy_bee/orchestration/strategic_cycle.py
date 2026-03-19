from __future__ import annotations

from busy_bee.schemas.briefs import ExecutiveBrief
from busy_bee.services.briefs import BriefService


class StrategicCycleOrchestrator:
    def __init__(self) -> None:
        self.brief_service = BriefService()

    def run_cycle(self) -> ExecutiveBrief:
        return self.brief_service.generate_executive_brief()
