from busy_bee.domain.service import DomainIntelligenceService


def test_generate_recommendations_covers_domains() -> None:
    service = DomainIntelligenceService()
    recs = service.generate_recommendations()
    assert len(recs) == 6
    assert any(rec.domain == "finance" for rec in recs)
