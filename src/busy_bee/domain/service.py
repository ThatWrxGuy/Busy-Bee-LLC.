from __future__ import annotations

from busy_bee.core.models import DomainSignal, Recommendation
from busy_bee.domain.registry import DOMAINS


class DomainIntelligenceService:
    """Starter domain service with placeholder scoring and recommendations."""

    def collect_signals(self) -> list[DomainSignal]:
        return [
            DomainSignal(domain=domain, name="baseline_signal", value=75.0, source="starter")
            for domain in DOMAINS
        ]

    def generate_recommendations(self) -> list[Recommendation]:
        recs: list[Recommendation] = []
        for idx, domain in enumerate(DOMAINS, start=1):
            recs.append(
                Recommendation(
                    id=f"rec_{idx}",
                    domain=domain,
                    title=f"Strengthen {domain.replace('_', ' ')} operating cadence",
                    rationale="Starter recommendation generated from baseline domain health.",
                    requires_human_approval=(domain == "finance"),
                )
            )
        return recs
