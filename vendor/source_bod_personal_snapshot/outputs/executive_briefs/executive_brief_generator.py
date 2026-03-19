"""
Executive Brief Generator - Produces executive-level decision guidance
Outputs Layer
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutiveBrief:
    """Executive Brief - Primary report format"""
    id: str
    date: datetime
    strategic_priorities: List[str]
    major_opportunities: List[Dict[str, Any]]
    critical_risks: List[Dict[str, Any]]
    recommended_actions: List[Dict[str, Any]]
    domain_summaries: Dict[str, str]
    generated_at: datetime = field(default_factory=datetime.now)
    # BB-FIN-021: Tactical trade intelligence section
    tactical_trade_insights: List[Dict[str, Any]] = field(default_factory=list)


class ExecutiveBriefGenerator:
    """
    Executive Brief Generator produces executive-level decision guidance.
    
    Primary report format containing:
    - Strategic priorities
    - Major opportunities
    - Critical risks
    - Recommended actions
    """
    
    def __init__(self):
        self.briefs: List[ExecutiveBrief] = []
    
    def generate(
        self,
        domain_reports: Dict[str, Dict[str, Any]],
        strategy_status: Dict[str, Any],
        risk_summary: Dict[str, Any],
        tactical_trade_insights: List[Dict[str, Any]] = None
    ) -> ExecutiveBrief:
        """Generate an executive brief"""
        
        # Extract strategic priorities
        priorities = self._extract_priorities(domain_reports, strategy_status)
        
        # Extract major opportunities
        opportunities = self._extract_opportunities(domain_reports)
        
        # Extract critical risks
        risks = self._extract_risks(risk_summary, domain_reports)
        
        # Generate recommended actions
        actions = self._generate_actions(priorities, opportunities, risks)
        
        # Create domain summaries
        domain_summaries = {
            domain: report.get("summary", "No summary available")
            for domain, report in domain_reports.items()
        }
        
        brief = ExecutiveBrief(
            id=f"brief_{len(self.briefs) + 1}_{datetime.now().timestamp()}",
            date=datetime.now(),
            strategic_priorities=priorities,
            major_opportunities=opportunities,
            critical_risks=risks,
            recommended_actions=actions,
            domain_summaries=domain_summaries,
            tactical_trade_insights=tactical_trade_insights or []
        )
        
        self.briefs.append(brief)
        return brief
    
    def _extract_priorities(
        self,
        domain_reports: Dict[str, Dict[str, Any]],
        strategy_status: Dict[str, Any]
    ) -> List[str]:
        """Extract strategic priorities from domains"""
        priorities = []
        
        for domain, report in domain_reports.items():
            recommendations = report.get("recommendations", [])
            if recommendations:
                priorities.append(f"[{domain.upper()}] {recommendations[0]}")
        
        # Add strategy-based priorities
        active_strategies = strategy_status.get("active_strategies", [])
        if active_strategies:
            priorities.append(f"Execute {len(active_strategies)} active strategies")
        
        return priorities[:5]  # Top 5
    
    def _extract_opportunities(self, domain_reports: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract major opportunities"""
        opportunities = []
        
        for domain, report in domain_reports.items():
            # Handle both dict and DomainStrategy objects
            opportunities_list = report.get("opportunities", [])
            for opp in opportunities_list:
                if hasattr(opp, 'title'):
                    # It's a DomainStrategy object
                    opportunities.append({
                        "domain": domain,
                        "title": opp.title,
                        "strength": opp.expected_impact
                    })
                elif isinstance(opp, dict):
                    opportunities.append({
                        "domain": domain,
                        "title": opp.get("title", "Opportunity"),
                        "strength": opp.get("strength", 0.5)
                    })
        
        return opportunities[:5]
    
    def _extract_risks(
        self,
        risk_summary: Dict[str, Any],
        domain_reports: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract critical risks"""
        risks = []
        
        # From risk summary
        critical = risk_summary.get("critical_risks", [])
        for risk in critical:
            risks.append({
                "domain": risk.get("domain", "unknown"),
                "title": risk.get("name", "Risk"),
                "level": "critical"
            })
        
        # From domain reports
        for domain, report in domain_reports.items():
            if "risks" in report:
                for risk in report["risks"][:1]:
                    risks.append({
                        "domain": domain,
                        "title": risk.get("title", "Risk"),
                        "level": "domain"
                    })
        
        return risks[:5]
    
    def _generate_actions(
        self,
        priorities: List[str],
        opportunities: List[Dict[str, Any]],
        risks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommended actions"""
        actions = []
        
        # Address risks first
        for risk in risks[:2]:
            actions.append({
                "type": "risk_mitigation",
                "priority": "high",
                "description": f"Address: {risk.get('title', 'Risk')}",
                "domain": risk.get("domain", "unknown")
            })
        
        # Pursue opportunities
        for opp in opportunities[:2]:
            actions.append({
                "type": "opportunity_pursuit",
                "priority": "medium",
                "description": f"Pursue: {opp.get('title', 'Opportunity')}",
                "domain": opp.get("domain", "unknown")
            })
        
        # Execute priorities
        for priority in priorities[:1]:
            actions.append({
                "type": "priority_execution",
                "priority": "high",
                "description": priority,
                "domain": "all"
            })
        
        return actions
    
    def format_brief(self, brief: ExecutiveBrief) -> str:
        """Format brief as readable text"""
        lines = [
            "=" * 60,
            "EXECUTIVE BRIEF",
            f"Date: {brief.date.strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            "",
            "STRATEGIC PRIORITIES",
            "-" * 40
        ]
        
        for i, p in enumerate(brief.strategic_priorities, 1):
            lines.append(f"{i}. {p}")
        
        lines.extend([
            "",
            "MAJOR OPPORTUNITIES",
            "-" * 40
        ])
        
        for opp in brief.major_opportunities:
            lines.append(f"• [{opp.get('domain', '?')}] {opp.get('title', '?')}")
        
        lines.extend([
            "",
            "CRITICAL RISKS",
            "-" * 40
        ])
        
        for risk in brief.critical_risks:
            lines.append(f"⚠ [{risk.get('domain', '?')}] {risk.get('title', '?')}")
        
        lines.extend([
            "",
            "RECOMMENDED ACTIONS",
            "-" * 40
        ])
        
        for action in brief.recommended_actions:
            lines.append(f"[{action.get('priority', '?').upper()}] {action.get('description', '?')}")
        
        lines.extend([
            "",
            "DOMAIN SUMMARIES",
            "-" * 40
        ])
        
        for domain, summary in brief.domain_summaries.items():
            lines.append(f"{domain.upper()}: {summary}")
        
        return "\n".join(lines)
    
    def get_latest_brief(self) -> Optional[ExecutiveBrief]:
        """Get the most recent brief"""
        return self.briefs[-1] if self.briefs else None
