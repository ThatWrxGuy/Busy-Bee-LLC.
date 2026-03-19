"""
Intelligence Reporting - BB-DOM-003: Domain Reporting & Executive Intelligence Doctrine

This module implements the canonical intelligence reporting framework.

Intelligence Product Hierarchy:
- Level 1: Agent Insight (Specialist Agents)
- Level 2: Governor Alert (Governor Agents)
- Level 3: Domain Intelligence Report (Chief Officers)
- Level 4: Council Strategic Assessment (Executive Council)
- Level 5: Executive Brief (Busy Bee System)
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


# ============== ENUMS ==============

class ImpactLevel(Enum):
    """Impact level for insights (BB-DOM-003 Section 4)"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    STRATEGIC = "strategic"


class PriorityLevel(Enum):
    """Priority level for recommendations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DomainMomentum(Enum):
    """Domain momentum state (BB-DOM-003 Section 6)"""
    ACCELERATING = "accelerating"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


class AlertType(Enum):
    """Governor alert types (BB-DOM-003 Section 5)"""
    RISK_THRESHOLD_BREACH = "risk_threshold_breach"
    POLICY_VIOLATION = "policy_violation"
    CAPACITY_OVERLOAD = "capacity_overload"
    STRATEGIC_MISALIGNMENT = "strategic_misalignment"
    BEHAVIORAL_INSTABILITY = "behavioral_instability"
    DOMAIN_IMBALANCE = "domain_imbalance"


class AlertSeverity(Enum):
    """Governor alert severity"""
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============== LEVEL 1: AGENT INSIGHT ==============

@dataclass
class AgentInsight:
    """
    Agent Insight Contract (BB-DOM-003 Section 4)
    
    Specialist agents transform signals into domain reasoning.
    """
    insight_id: str
    agent_name: str
    agent_role: str  # observer, strategist, governor
    domain: str
    timestamp: datetime
    
    # Content
    summary: str
    signal_basis: List[str]  # Signal IDs
    analysis: str
    
    # Scores (0-100)
    opportunity_score: float = 0.0
    risk_score: float = 0.0
    confidence: float = 0.5
    
    # Recommendation
    recommended_action: str = ""
    time_horizon: str = "medium_term"  # immediate, short_term, medium_term, long_term
    impact_level: ImpactLevel = ImpactLevel.MODERATE
    priority: PriorityLevel = PriorityLevel.MEDIUM
    
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "domain": self.domain,
            "timestamp": self.timestamp.isoformat(),
            "summary": self.summary,
            "signal_basis": self.signal_basis,
            "analysis": self.analysis,
            "opportunity_score": self.opportunity_score,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "recommended_action": self.recommended_action,
            "time_horizon": self.time_horizon,
            "impact_level": self.impact_level.value,
            "priority": self.priority.value,
            "tags": self.tags
        }


# ============== LEVEL 2: GOVERNOR ALERT ==============

@dataclass
class GovernorAlert:
    """
    Governor Alert Contract (BB-DOM-003 Section 5)
    
    Governor agents enforce discipline and platform safety.
    Alerts may override strategist recommendations.
    """
    alert_id: str
    governor_agent: str
    domain: str
    timestamp: datetime
    
    # Alert details
    alert_type: AlertType
    severity: AlertSeverity
    trigger_signals: List[str]
    risk_assessment: str
    
    # Response
    constraint: str = ""
    recommended_response: str = ""
    
    # Escalation
    escalation_required: bool = False
    council_visibility: bool = False
    confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "governor_agent": self.governor_agent,
            "domain": self.domain,
            "timestamp": self.timestamp.isoformat(),
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "trigger_signals": self.trigger_signals,
            "risk_assessment": self.risk_assessment,
            "constraint": self.constraint,
            "recommended_response": self.recommended_response,
            "escalation_required": self.escalation_required,
            "council_visibility": self.council_visibility,
            "confidence": self.confidence
        }
    
    def should_escalate(self) -> bool:
        """Check if this alert requires council escalation"""
        return self.escalation_required or self.severity == AlertSeverity.CRITICAL


# ============== LEVEL 3: DOMAIN INTELLIGENCE REPORT ==============

@dataclass
class StrategicRecommendation:
    """
    Strategic Recommendation Schema (BB-DOM-003 Section 7)
    """
    recommendation_id: str
    domain: str
    
    title: str
    description: str
    rationale: str
    
    expected_benefit: float  # 0-100
    expected_risk: float  # 0-100
    
    urgency: PriorityLevel
    impact_score: float  # 0-100
    confidence: float  # 0-1
    
    required_resources: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    reversibility: str = "medium"  # high, medium, low
    time_horizon: str = "medium_term"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "domain": self.domain,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "expected_benefit": self.expected_benefit,
            "expected_risk": self.expected_risk,
            "urgency": self.urgency.value,
            "impact_score": self.impact_score,
            "confidence": self.confidence,
            "required_resources": self.required_resources,
            "dependencies": self.dependencies,
            "reversibility": self.reversibility,
            "time_horizon": self.time_horizon
        }
    
    def priority_score(self) -> float:
        """Calculate priority score (BB-DOM-003 Section 11)"""
        # Factors: impact_score, urgency, confidence, reversibility
        urgency_map = {
            PriorityLevel.LOW: 0.25,
            PriorityLevel.MEDIUM: 0.5,
            PriorityLevel.HIGH: 0.75,
            PriorityLevel.CRITICAL: 1.0
        }
        
        reversibility_map = {"high": 1.0, "medium": 0.5, "low": 0.25}
        
        score = (
            (self.impact_score / 100) * 0.4 +
            urgency_map.get(self.urgency, 0.5) * 0.3 +
            self.confidence * 0.2 +
            reversibility_map.get(self.reversibility, 0.5) * 0.1
        )
        return min(1.0, score)


@dataclass
class DomainIntelligenceReport:
    """
    Domain Intelligence Report (BB-DOM-003 Section 6)
    
    Chief Officer synthesizes domain intelligence.
    """
    domain: str
    chief_officer: str
    report_timestamp: datetime
    
    # Domain state
    domain_state: str  # summary of current state
    signal_summary: Dict[str, Any]  # key signals affecting domain
    
    # Analysis
    key_trends: List[str] = field(default_factory=list)
    top_opportunities: List[str] = field(default_factory=list)
    top_risks: List[str] = field(default_factory=list)
    
    # Governor constraints
    governor_constraints: List[str] = field(default_factory=list)
    
    # Recommendations
    domain_priority_recommendations: List[StrategicRecommendation] = field(default_factory=list)
    
    # Momentum
    domain_momentum: DomainMomentum = DomainMomentum.STABLE
    confidence: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "chief_officer": self.chief_officer,
            "report_timestamp": self.report_timestamp.isoformat(),
            "domain_state": self.domain_state,
            "signal_summary": self.signal_summary,
            "key_trends": self.key_trends,
            "top_opportunities": self.top_opportunities,
            "top_risks": self.top_risks,
            "governor_constraints": self.governor_constraints,
            "recommendations": [r.to_dict() for r in self.domain_priority_recommendations],
            "domain_momentum": self.domain_momentum.value,
            "confidence": self.confidence
        }
    
    def get_top_recommendation(self) -> Optional[StrategicRecommendation]:
        """Get the highest priority recommendation"""
        if not self.domain_priority_recommendations:
            return None
        return max(self.domain_priority_recommendations, key=lambda r: r.priority_score())


# ============== LEVEL 4: COUNCIL STRATEGIC ASSESSMENT ==============

@dataclass
class CouncilAssessment:
    """
    Council Strategic Assessment (BB-DOM-003 Section 9)
    
    Executive Council produces cross-domain synthesis.
    """
    assessment_timestamp: datetime
    
    # Cross-domain analysis
    cross_domain_priorities: List[str] = field(default_factory=list)
    cross_domain_conflicts: List[Dict[str, str]] = field(default_factory=list)
    
    major_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    major_risks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Resource and governance
    resource_competition: List[Dict[str, str]] = field(default_factory=list)
    governor_escalations: List[str] = field(default_factory=list)
    
    # Strategic alignment
    strategic_alignment: str = ""
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    confidence: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "assessment_timestamp": self.assessment_timestamp.isoformat(),
            "cross_domain_priorities": self.cross_domain_priorities,
            "cross_domain_conflicts": self.cross_domain_conflicts,
            "major_opportunities": self.major_opportunities,
            "major_risks": self.major_risks,
            "resource_competition": self.resource_competition,
            "governor_escalations": self.governor_escalations,
            "strategic_alignment": self.strategic_alignment,
            "recommended_actions": self.recommended_actions,
            "confidence": self.confidence
        }


# ============== LEVEL 5: EXECUTIVE BRIEF ==============

@dataclass
class ExecutiveBrief:
    """
    Executive Brief (BB-DOM-003 Section 10)
    
    Final product delivered to the CEO.
    Maximum 3-6 sentences for executive summary.
    """
    brief_timestamp: datetime
    
    # Executive summary (3-6 sentences)
    executive_summary: str = ""
    
    # Top items
    top_3_priorities: List[str] = field(default_factory=list)
    major_opportunities: List[str] = field(default_factory=list)
    critical_risks: List[str] = field(default_factory=list)
    
    # Action items
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    constraints_and_watchouts: List[str] = field(default_factory=list)
    
    # Outlook
    strategic_outlook: str = ""
    confidence: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "brief_timestamp": self.brief_timestamp.isoformat(),
            "executive_summary": self.executive_summary,
            "top_3_priorities": self.top_3_priorities,
            "major_opportunities": self.major_opportunities,
            "critical_risks": self.critical_risks,
            "recommended_actions": self.recommended_actions,
            "constraints_and_watchouts": self.constraints_and_watchouts,
            "strategic_outlook": self.strategic_outlook,
            "confidence": self.confidence
        }
    
    def format_brief(self) -> str:
        """Format brief as readable text"""
        lines = [
            "=" * 60,
            "EXECUTIVE BRIEF",
            f"Date: {self.brief_timestamp.strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            "",
            f"EXECUTIVE SUMMARY: {self.executive_summary}",
            "",
            "TOP PRIORITIES",
            "-" * 40
        ]
        
        for i, p in enumerate(self.top_3_priorities[:3], 1):
            lines.append(f"{i}. {p}")
        
        lines.extend([
            "",
            "MAJOR OPPORTUNITIES",
            "-" * 40
        ])
        
        for opp in self.major_opportunities[:3]:
            lines.append(f"• {opp}")
        
        lines.extend([
            "",
            "CRITICAL RISKS",
            "-" * 40
        ])
        
        for risk in self.critical_risks[:3]:
            lines.append(f"⚠ {risk}")
        
        lines.extend([
            "",
            "RECOMMENDED ACTIONS",
            "-" * 40
        ])
        
        for action in self.recommended_actions[:5]:
            lines.append(f"[{action.get('priority', '?').upper()}] {action.get('title', '?')}")
        
        lines.extend([
            "",
            "STRATEGIC OUTLOOK",
            "-" * 40,
            self.strategic_outlook,
            "",
            f"Confidence: {self.confidence:.0%}"
        ])
        
        return "\n".join(lines)


# ============== INTELLIGENCE PIPELINE ==============

class IntelligencePipeline:
    """
    Intelligence Pipeline Manager (BB-DOM-003 Section 3)
    
    Manages the flow from Signals → Agents → Domains → Council → CEO
    """
    
    def __init__(self):
        # Store all intelligence artifacts
        self.agent_insights: List[AgentInsight] = []
        self.governor_alerts: List[GovernorAlert] = []
        self.domain_reports: List[DomainIntelligenceReport] = []
        self.council_assessments: List[CouncilAssessment] = []
        self.executive_briefs: List[ExecutiveBrief] = []
        
        # Counters for IDs
        self._insight_counter = 0
        self._alert_counter = 0
        self._report_counter = 0
        self._recommendation_counter = 0
    
    # --- Level 1: Agent Insights ---
    
    def add_insight(self, insight: AgentInsight) -> str:
        """Add an agent insight"""
        self._insight_counter += 1
        insight.insight_id = f"insight_{self._insight_counter}"
        self.agent_insights.append(insight)
        return insight.insight_id
    
    def get_insights_by_domain(self, domain: str) -> List[AgentInsight]:
        """Get insights for a domain"""
        return [i for i in self.agent_insights if i.domain == domain]
    
    # --- Level 2: Governor Alerts ---
    
    def add_alert(self, alert: GovernorAlert) -> str:
        """Add a governor alert"""
        self._alert_counter += 1
        alert.alert_id = f"alert_{self._alert_counter}"
        self.governor_alerts.append(alert)
        return alert.alert_id
    
    def get_alerts_by_domain(self, domain: str) -> List[GovernorAlert]:
        """Get alerts for a domain"""
        return [a for a in self.governor_alerts if a.domain == domain]
    
    def get_critical_alerts(self) -> List[GovernorAlert]:
        """Get alerts requiring escalation"""
        return [a for a in self.governor_alerts if a.should_escalate()]
    
    # --- Level 3: Domain Reports ---
    
    def add_domain_report(self, report: DomainIntelligenceReport) -> str:
        """Add a domain intelligence report"""
        self._report_counter += 1
        self.domain_reports.append(report)
        return f"report_{self._report_counter}"
    
    def get_latest_report(self, domain: str) -> Optional[DomainIntelligenceReport]:
        """Get most recent report for domain"""
        domain_reports = [r for r in self.domain_reports if r.domain == domain]
        if domain_reports:
            return max(domain_reports, key=lambda r: r.report_timestamp)
        return None
    
    # --- Level 4: Council Assessment ---
    
    def create_council_assessment(
        self,
        domain_reports: List[DomainIntelligenceReport],
        critical_alerts: List[GovernorAlert]
    ) -> CouncilAssessment:
        """Create council strategic assessment from domain reports"""
        
        assessment = CouncilAssessment(
            assessment_timestamp=datetime.now()
        )
        
        # Aggregate cross-domain priorities
        all_recommendations = []
        for report in domain_reports:
            all_recommendations.extend(report.domain_priority_recommendations)
        
        # Rank recommendations
        all_recommendations.sort(key=lambda r: r.priority_score(), reverse=True)
        
        # Extract top priorities
        assessment.cross_domain_priorities = [
            r.title for r in all_recommendations[:5]
        ]
        
        # Detect conflicts (same domain recommending opposite actions)
        # Simplified: just collect all top risks
        assessment.major_risks = []
        for report in domain_reports:
            assessment.major_risks.extend([
                {"domain": report.domain, "risk": r}
                for r in report.top_risks[:2]
            ])
        
        # Governor escalations
        assessment.governor_escalations = [
            a.alert_id for a in critical_alerts
        ]
        
        # Top opportunities
        assessment.major_opportunities = []
        for report in domain_reports:
            assessment.major_opportunities.extend([
                {"domain": report.domain, "opportunity": o}
                for o in report.top_opportunities[:2]
            ])
        
        # Recommended actions
        assessment.recommended_actions = [
            {"title": r.title, "domain": r.domain, "priority": r.urgency.value}
            for r in all_recommendations[:5]
        ]
        
        # Strategic alignment
        if all_recommendations:
            assessment.strategic_alignment = "Recommendations align with strategic goals"
        
        self.council_assessments.append(assessment)
        return assessment
    
    # --- Level 5: Executive Brief ---
    
    def create_executive_brief(
        self,
        council_assessment: CouncilAssessment,
        domain_reports: List[DomainIntelligenceReport]
    ) -> ExecutiveBrief:
        """Create executive brief from council assessment"""
        
        brief = ExecutiveBrief(
            brief_timestamp=datetime.now()
        )
        
        # Executive summary (synthesize from assessment)
        if council_assessment.recommended_actions:
            top_action = council_assessment.recommended_actions[0]
            brief.executive_summary = (
                f"Priority focus on {top_action['domain']}: {top_action['title']}. "
                f"Current intelligence identifies {len(council_assessment.major_risks)} critical risks "
                f"and {len(council_assessment.major_opportunities)} key opportunities "
                f"requiring immediate attention."
            )
        
        # Top 3 priorities
        brief.top_3_priorities = council_assessment.cross_domain_priorities[:3]
        
        # Major opportunities
        brief.major_opportunities = [
            o.get('opportunity', str(o)) 
            for o in council_assessment.major_opportunities[:3]
        ]
        
        # Critical risks
        brief.critical_risks = [
            r.get('risk', str(r))
            for r in council_assessment.major_risks[:3]
        ]
        
        # Recommended actions
        brief.recommended_actions = council_assessment.recommended_actions[:5]
        
        # Strategic outlook
        brief.strategic_outlook = council_assessment.strategic_alignment or "Stable operations with identified improvement areas."
        
        # Confidence
        brief.confidence = sum(r.confidence for r in domain_reports) / len(domain_reports) if domain_reports else 0.7
        
        self.executive_briefs.append(brief)
        return brief
    
    # --- Full Pipeline ---
    
    def run_full_pipeline(
        self,
        domain_data: Dict[str, Dict[str, Any]]
    ) -> ExecutiveBrief:
        """
        Run the full intelligence pipeline.
        
        Args:
            domain_data: Dict mapping domain names to their state data
        """
        
        # For now, create synthetic insights from domain data
        # In real implementation, these would come from agents
        
        for domain, data in domain_data.items():
            # Create domain report
            report = DomainIntelligenceReport(
                domain=domain,
                chief_officer=f"Chief {domain.title()} Officer",
                report_timestamp=datetime.now(),
                domain_state=data.get("state", "operational"),
                signal_summary=data.get("signals", {}),
                key_trends=data.get("trends", []),
                top_opportunities=data.get("opportunities", []),
                top_risks=data.get("risks", []),
                domain_momentum=DomainMomentum(data.get("momentum", "stable")),
                confidence=data.get("confidence", 0.7)
            )
            
            # Add recommendations if provided
            for rec_data in data.get("recommendations", []):
                self._recommendation_counter += 1
                rec = StrategicRecommendation(
                    recommendation_id=f"rec_{self._recommendation_counter}",
                    domain=domain,
                    title=rec_data.get("title", ""),
                    description=rec_data.get("description", ""),
                    rationale=rec_data.get("rationale", ""),
                    expected_benefit=rec_data.get("benefit", 50),
                    expected_risk=rec_data.get("risk", 30),
                    urgency=PriorityLevel(rec_data.get("urgency", "medium")),
                    impact_score=rec_data.get("impact", 50),
                    confidence=rec_data.get("confidence", 0.7)
                )
                report.domain_priority_recommendations.append(rec)
            
            self.add_domain_report(report)
        
        # Create council assessment
        assessment = self.create_council_assessment(
            self.domain_reports,
            self.get_critical_alerts()
        )
        
        # Create executive brief
        brief = self.create_executive_brief(assessment, self.domain_reports)
        
        return brief


__all__ = [
    # Enums
    "ImpactLevel",
    "PriorityLevel", 
    "DomainMomentum",
    "AlertType",
    "AlertSeverity",
    
    # Contracts
    "AgentInsight",
    "GovernorAlert",
    "StrategicRecommendation",
    "DomainIntelligenceReport",
    "CouncilAssessment",
    "ExecutiveBrief",
    
    # Pipeline
    "IntelligencePipeline",
]
