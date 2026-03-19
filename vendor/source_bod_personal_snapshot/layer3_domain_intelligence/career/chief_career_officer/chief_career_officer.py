"""
Chief Career Officer - Career domain intelligence
Part of Layer 3: Domain Intelligence Systems
"""

from typing import Dict, Any, List
from datetime import datetime
from ...base_chief_officer import ChiefOfficer, DomainSignal, DomainStrategy, DomainReport


class ChiefCareerOfficer(ChiefOfficer):
    """
    Chief Career Officer manages the Career domain.
    
    Responsibilities:
    - Analyze career signals
    - Generate career strategies
    - Monitor career growth
    - Produce career intelligence reports
    """
    
    def __init__(self):
        super().__init__(domain="career", title="Chief Career Officer")
        self.specialist_agents = [
            "skill_development_agent",
            "networking_agent",
            "job_market_agent",
            "leadership_agent"
        ]
        
        # Career state
        self.current_role = ""
        self.skill_level = 0.5
        self.market_value = 0.5
        self.network_strength = 0.5
        self.career_goals = []
    
    def analyze_signals(self, signals: List[DomainSignal]) -> Dict[str, Any]:
        """Analyze career signals"""
        analysis = {
            "domain": self.domain,
            "signal_count": len(signals),
            "signals_analyzed": [],
            "opportunities": [],
            "risks": [],
            "career_indicators": {},
            "analyzed_at": datetime.now().isoformat()
        }
        
        for signal in signals:
            signal_summary = {
                "id": signal.id,
                "type": signal.signal_type,
                "title": signal.title,
                "strength": signal.strength
            }
            analysis["signals_analyzed"].append(signal_summary)
            
            if signal.signal_type == "career_opportunity":
                analysis["opportunities"].append({
                    "title": signal.title,
                    "data": signal.data
                })
            elif signal.signal_type == "career_risk":
                analysis["risks"].append({
                    "title": signal.title,
                    "data": signal.data
                })
        
        analysis["career_indicators"] = self._calculate_career_health()
        
        return analysis
    
    def _calculate_career_health(self) -> Dict[str, Any]:
        """Calculate career health indicators"""
        overall_career = (self.skill_level + self.market_value + self.network_strength) / 3
        
        if overall_career > 0.8:
            status = "excellent"
        elif overall_career > 0.6:
            status = "good"
        elif overall_career > 0.4:
            status = "fair"
        else:
            status = "needs_attention"
        
        return {
            "overall_career": overall_career,
            "skill_level": self.skill_level,
            "market_value": self.market_value,
            "network_strength": self.network_strength,
            "status": status
        }
    
    def generate_strategy(self, analysis: Dict[str, Any]) -> DomainStrategy:
        """Generate a career strategy"""
        career = analysis.get("career_indicators", {})
        opportunities = analysis.get("opportunities", [])
        risks = analysis.get("risks", [])
        
        if career.get("status") == "needs_attention" or len(risks) > 1:
            priority = "critical"
            risk_level = "high"
        elif career.get("status") == "fair":
            priority = "high"
            risk_level = "medium"
        else:
            priority = "medium"
            risk_level = "low"
        
        action_items = []
        
        if self.skill_level < 0.6:
            action_items.append("Develop in-demand skills for your field")
        
        if self.market_value < 0.6:
            action_items.append("Increase visibility and personal branding")
        
        if self.network_strength < 0.6:
            action_items.append("Expand professional network")
        
        if opportunities:
            action_items.append(f"Pursue {len(opportunities)} career opportunities")
        
        if not action_items:
            action_items = ["Maintain current career momentum", "Continue skill development"]
        
        expected_impact = 0.5
        if career.get("status") != "excellent":
            expected_impact += 0.2
        
        strategy = DomainStrategy(
            id=f"strat_{self.domain}_{len(self.strategies) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title=f"Career Strategy - {career.get('status', 'unknown').title()}",
            description=f"Career strategy addressing: {career.get('status', 'unknown')}",
            priority=priority,
            expected_impact=min(1.0, expected_impact),
            risk_level=risk_level,
            action_items=action_items
        )
        
        self.add_strategy(strategy)
        return strategy
    
    def create_report(self) -> DomainReport:
        """Create career intelligence report"""
        career = self._calculate_career_health()
        
        sections = {
            "career_overview": {
                "current_role": self.current_role,
                "overall_career": career["overall_career"],
                "status": career["status"]
            },
            "skill_development": {
                "skill_level": self.skill_level,
                "recommendation": "Continue developing market-relevant skills"
            },
            "market_position": {
                "market_value": self.market_value,
                "recommendation": "Build personal brand and visibility"
            },
            "networking": {
                "network_strength": self.network_strength,
                "recommendation": "Expand and nurture professional relationships"
            }
        }
        
        recommendations = []
        
        if self.skill_level < 0.5:
            recommendations.append("Priority: Identify and develop key skills")
        if self.market_value < 0.5:
            recommendations.append("Priority: Increase market visibility")
        if self.network_strength < 0.5:
            recommendations.append("Priority: Build professional network")
        
        if not recommendations:
            recommendations = [
                "Maintain career momentum",
                "Continue professional development",
                "Nurture professional relationships"
            ]
        
        report = DomainReport(
            id=f"report_{self.domain}_{len(self.reports) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title="Career Intelligence Report",
            sections=sections,
            recommendations=recommendations
        )
        
        self.reports.append(report)
        return report
    
    def update_career_metrics(self, skill: float = None, market: float = None, network: float = None):
        """Update career metrics"""
        if skill is not None:
            self.skill_level = max(0, min(1, skill))
        if market is not None:
            self.market_value = max(0, min(1, market))
        if network is not None:
            self.network_strength = max(0, min(1, network))
    
    def set_role(self, role: str):
        """Set current role"""
        self.current_role = role
