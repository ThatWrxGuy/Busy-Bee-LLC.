# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Executive Dashboard Service.

Generates daily executive briefs aggregating all domain intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from busybee_contracts.tenant_context import TenantContext
from infrastructure.connectors.health_monitor import get_health_monitor, ConnectorHealthStatus


@dataclass
class DomainSummary:
    """Summary of a domain's status."""
    domain: str
    status: str
    last_update: datetime | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    alerts: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)


@dataclass
class Alert:
    """An alert or warning."""
    id: str
    severity: str  # critical, warning, info
    domain: str
    message: str
    timestamp: datetime
    action_required: bool = False


@dataclass
class Opportunity:
    """An identified opportunity."""
    id: str
    domain: str
    title: str
    description: str
    potential_impact: str
    recommended_action: str
    timestamp: datetime


@dataclass
class ExecutiveBrief:
    """Daily executive brief for a tenant."""
    tenant_id: str
    generated_at: datetime
    user_id: str
    
    # Domain summaries
    domains: dict[str, DomainSummary] = field(default_factory=dict)
    
    # Alerts and opportunities
    alerts: list[Alert] = field(default_factory=list)
    opportunities: list[Opportunity] = field(default_factory=list)
    
    # Approval queue
    pending_approvals: list[dict[str, Any]] = field(default_factory=list)
    
    # Overall health
    overall_status: str = "healthy"
    health_score: int = 100
    
    # Connector status
    connectors: dict[str, str] = field(default_factory=dict)


class ExecutiveDashboardService:
    """Service for generating executive dashboards and briefs.
    
    Aggregates data from all domains and connectors to provide
    a unified view for the executive control plane.
    """

    def __init__(self) -> None:
        self._health_monitor = get_health_monitor()

    async def generate_executive_brief(
        self,
        context: TenantContext
    ) -> ExecutiveBrief:
        """Generate daily executive brief for a tenant.
        
        Args:
            context: Tenant context
            
        Returns:
            ExecutiveBrief with all domain summaries
        """
        if not context.tenant_id:
            raise ValueError("Cannot generate brief without tenant_id")

        # Get connector statuses
        connectors = self._health_monitor.get_all_statuses(context)

        # Generate domain summaries (would integrate with actual domain services)
        domains = await self._get_domain_summaries(context)

        # Generate alerts
        alerts = await self._generate_alerts(context, domains, connectors)

        # Generate opportunities
        opportunities = await self._generate_opportunities(context, domains)

        # Calculate overall health
        overall_status, health_score = self._calculate_health(connectors, alerts)

        return ExecutiveBrief(
            tenant_id=context.tenant_id,
            generated_at=datetime.utcnow(),
            user_id=context.user_id or "",
            domains=domains,
            alerts=alerts,
            opportunities=opportunities,
            pending_approvals=[],  # Would fetch from policy engine
            overall_status=overall_status,
            health_score=health_score,
            connectors={name: status.value for name, status in connectors.items()}
        )

    async def _get_domain_summaries(
        self,
        context: TenantContext
    ) -> dict[str, DomainSummary]:
        """Get summaries for all domains."""
        # In production, this would aggregate from actual domain services
        domains = {
            "finance": DomainSummary(
                domain="finance",
                status="active",
                last_update=datetime.utcnow(),
                metrics={"portfolio_value": 0, "daily_change": 0},
                alerts=[],
                opportunities=["Review investment allocation"]
            ),
            "health": DomainSummary(
                domain="health",
                status="active",
                last_update=datetime.utcnow(),
                metrics={"steps_today": 0, "sleep_hours": 0},
                alerts=[],
                opportunities=["Optimize sleep schedule"]
            ),
            "career": DomainSummary(
                domain="career",
                status="active",
                last_update=datetime.utcnow(),
                metrics={"meetings_today": 0, "tasks_pending": 0},
                alerts=[],
                opportunities=["Network expansion available"]
            ),
            "relationships": DomainSummary(
                domain="relationships",
                status="active",
                last_update=datetime.utcnow(),
                metrics={"interactions_today": 0},
                alerts=[],
                opportunities=[]
            ),
            "intelligence": DomainSummary(
                domain="intelligence",
                status="active",
                last_update=datetime.utcnow(),
                metrics={"insights_generated": 0},
                alerts=[],
                opportunities=["New market trends detected"]
            ),
            "life_architecture": DomainSummary(
                domain="life_architecture",
                status="active",
                last_update=datetime.utcnow(),
                metrics={"goals_progress": 0},
                alerts=[],
                opportunities=["Quarterly review recommended"]
            ),
        }
        
        return domains

    async def _generate_alerts(
        self,
        context: TenantContext,
        domains: dict[str, DomainSummary],
        connectors: dict[str, ConnectorHealthStatus]
    ) -> list[Alert]:
        """Generate alerts based on current state."""
        alerts = []
        
        # Check connector health
        for name, status in connectors.items():
            if status == ConnectorHealthStatus.ERROR:
                alerts.append(Alert(
                    id=f"connector_{name}",
                    severity="warning",
                    domain="system",
                    message=f"Connector {name} is experiencing errors",
                    timestamp=datetime.utcnow(),
                    action_required=True
                ))
            elif status == ConnectorHealthStatus.EXPIRED:
                alerts.append(Alert(
                    id=f"connector_{name}_expired",
                    severity="warning",
                    domain="system",
                    message=f"Connector {name} credentials have expired",
                    timestamp=datetime.utcnow(),
                    action_required=True
                ))
        
        # Check domain alerts
        for domain_name, summary in domains.items():
            alerts.extend([
                Alert(
                    id=f"{domain_name}_{i}",
                    severity="info",
                    domain=domain_name,
                    message=alert,
                    timestamp=datetime.utcnow(),
                    action_required=False
                )
                for i, alert in enumerate(summary.alerts)
            ])
        
        return alerts

    async def _generate_opportunities(
        self,
        context: TenantContext,
        domains: dict[str, DomainSummary]
    ) -> list[Opportunity]:
        """Generate opportunities based on current state."""
        opportunities = []
        
        for domain_name, summary in domains.items():
            for i, opp in enumerate(summary.opportunities):
                opportunities.append(Opportunity(
                    id=f"{domain_name}_opp_{i}",
                    domain=domain_name,
                    title=opp,
                    description=f"Opportunity in {domain_name}",
                    potential_impact="medium",
                    recommended_action=f"Explore {domain_name} opportunity",
                    timestamp=datetime.utcnow()
                ))
        
        return opportunities

    def _calculate_health(
        self,
        connectors: dict[str, ConnectorHealthStatus],
        alerts: list[Alert]
    ) -> tuple[str, int]:
        """Calculate overall health score."""
        score = 100
        
        # Deduct for connector errors
        error_count = sum(
            1 for s in connectors.values() 
            if s in (ConnectorHealthStatus.ERROR, ConnectorHealthStatus.EXPIRED)
        )
        score -= error_count * 15
        
        # Deduct for alerts
        critical_alerts = sum(1 for a in alerts if a.severity == "critical")
        warning_alerts = sum(1 for a in alerts if a.severity == "warning")
        
        score -= critical_alerts * 20
        score -= warning_alerts * 5
        
        score = max(0, score)
        
        if score >= 90:
            status = "healthy"
        elif score >= 70:
            status = "degraded"
        elif score >= 50:
            status = "warning"
        else:
            status = "critical"
        
        return status, score

    def to_dict(self, brief: ExecutiveBrief) -> dict[str, Any]:
        """Convert brief to dict for API response."""
        return {
            "tenant_id": brief.tenant_id,
            "generated_at": brief.generated_at.isoformat(),
            "user_id": brief.user_id,
            "domains": {
                name: {
                    "domain": summary.domain,
                    "status": summary.status,
                    "last_update": summary.last_update.isoformat() if summary.last_update else None,
                    "metrics": summary.metrics,
                    "alerts": summary.alerts,
                    "opportunities": summary.opportunities,
                }
                for name, summary in brief.domains.items()
            },
            "alerts": [
                {
                    "id": a.id,
                    "severity": a.severity,
                    "domain": a.domain,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat(),
                    "action_required": a.action_required,
                }
                for a in brief.alerts
            ],
            "opportunities": [
                {
                    "id": o.id,
                    "domain": o.domain,
                    "title": o.title,
                    "description": o.description,
                    "potential_impact": o.potential_impact,
                    "recommended_action": o.recommended_action,
                    "timestamp": o.timestamp.isoformat(),
                }
                for o in brief.opportunities
            ],
            "pending_approvals": brief.pending_approvals,
            "overall_status": brief.overall_status,
            "health_score": brief.health_score,
            "connectors": brief.connectors,
        }


# Singleton instance
_dashboard_service: ExecutiveDashboardService | None = None


def get_executive_dashboard() -> ExecutiveDashboardService:
    """Get the default executive dashboard service."""
    global _dashboard_service
    if _dashboard_service is None:
        _dashboard_service = ExecutiveDashboardService()
    return _dashboard_service
