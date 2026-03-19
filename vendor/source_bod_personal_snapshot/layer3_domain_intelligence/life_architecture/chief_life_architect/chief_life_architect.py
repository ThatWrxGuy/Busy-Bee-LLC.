"""
Chief Life Architect - Life Architecture domain intelligence
Part of Layer 3: Domain Intelligence Systems
"""

from typing import Dict, Any, List
from datetime import datetime
from ...base_chief_officer import ChiefOfficer, DomainSignal, DomainStrategy, DomainReport


class ChiefLifeArchitect(ChiefOfficer):
    """
    Chief Life Architect manages the Life Architecture domain.
    
    Responsibilities:
    - Analyze life signals
    - Generate life strategies
    - Monitor life balance
    - Produce life architecture reports
    """
    
    def __init__(self):
        super().__init__(domain="life_architecture", title="Chief Life Architect")
        self.specialist_agents = [
            "life_design_agent",
            "goals_agent",
            "habits_agent",
            "environment_agent"
        ]
        
        # Life Architecture state
        self.purpose_clarity = 0.5
        self.life_balance = 0.5
        self.goal_alignment = 0.5
        self.habit_strength = 0.5
        self.life_goals = []
    
    def analyze_signals(self, signals: List[DomainSignal]) -> Dict[str, Any]:
        """Analyze life architecture signals"""
        analysis = {
            "domain": self.domain,
            "signal_count": len(signals),
            "signals_analyzed": [],
            "opportunities": [],
            "risks": [],
            "life_indicators": {},
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
            
            if signal.signal_type == "life_opportunity":
                analysis["opportunities"].append({
                    "title": signal.title,
                    "data": signal.data
                })
            elif signal.signal_type == "life_risk":
                analysis["risks"].append({
                    "title": signal.title,
                    "data": signal.data
                })
        
        analysis["life_indicators"] = self._calculate_life_health()
        
        return analysis
    
    def _calculate_life_health(self) -> Dict[str, Any]:
        """Calculate life architecture health"""
        overall = (self.purpose_clarity + self.life_balance + 
                   self.goal_alignment + self.habit_strength) / 4
        
        if overall > 0.8:
            status = "excellent"
        elif overall > 0.6:
            status = "good"
        elif overall > 0.4:
            status = "fair"
        else:
            status = "needs_attention"
        
        return {
            "overall": overall,
            "purpose_clarity": self.purpose_clarity,
            "life_balance": self.life_balance,
            "goal_alignment": self.goal_alignment,
            "habit_strength": self.habit_strength,
            "status": status
        }
    
    def generate_strategy(self, analysis: Dict[str, Any]) -> DomainStrategy:
        """Generate a life architecture strategy"""
        life = analysis.get("life_indicators", {})
        opportunities = analysis.get("opportunities", [])
        risks = analysis.get("risks", [])
        
        if life.get("status") == "needs_attention" or len(risks) > 1:
            priority = "critical"
            risk_level = "high"
        elif life.get("status") == "fair":
            priority = "high"
            risk_level = "medium"
        else:
            priority = "medium"
            risk_level = "low"
        
        action_items = []
        
        if self.purpose_clarity < 0.6:
            action_items.append("Clarify life purpose and values")
        
        if self.life_balance < 0.6:
            action_items.append("Improve life balance across domains")
        
        if self.goal_alignment < 0.6:
            action_items.append("Align daily actions with long-term goals")
        
        if self.habit_strength < 0.6:
            action_items.append("Build positive habits")
        
        if opportunities:
            action_items.append(f"Pursue {len(opportunities)} life opportunities")
        
        if not action_items:
            action_items = ["Maintain life architecture", "Continue personal growth"]
        
        expected_impact = 0.5
        if life.get("status") != "excellent":
            expected_impact += 0.2
        
        strategy = DomainStrategy(
            id=f"strat_{self.domain}_{len(self.strategies) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title=f"Life Architecture Strategy - {life.get('status', 'unknown').title()}",
            description=f"Life strategy addressing: {life.get('status', 'unknown')}",
            priority=priority,
            expected_impact=min(1.0, expected_impact),
            risk_level=risk_level,
            action_items=action_items
        )
        
        self.add_strategy(strategy)
        return strategy
    
    def create_report(self) -> DomainReport:
        """Create life architecture report"""
        life = self._calculate_life_health()
        
        sections = {
            "life_overview": {
                "overall": life["overall"],
                "status": life["status"]
            },
            "purpose": {
                "clarity": self.purpose_clarity,
                "recommendation": "Clarify core values and life purpose"
            },
            "balance": {
                "score": self.life_balance,
                "recommendation": "Balance time across life domains"
            },
            "goals": {
                "alignment": self.goal_alignment,
                "recommendation": "Ensure goals align with values"
            },
            "habits": {
                "strength": self.habit_strength,
                "recommendation": "Build and maintain positive habits"
            }
        }
        
        recommendations = []
        
        if self.purpose_clarity < 0.5:
            recommendations.append("Priority: Define life purpose")
        if self.life_balance < 0.5:
            recommendations.append("Priority: Improve life balance")
        if self.goal_alignment < 0.5:
            recommendations.append("Priority: Align goals with values")
        if self.habit_strength < 0.5:
            recommendations.append("Priority: Build positive habits")
        
        if not recommendations:
            recommendations = [
                "Maintain life architecture",
                "Continue personal development",
                "Regularly review and adjust life design"
            ]
        
        report = DomainReport(
            id=f"report_{self.domain}_{len(self.reports) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title="Life Architecture Report",
            sections=sections,
            recommendations=recommendations
        )
        
        self.reports.append(report)
        return report
    
    def update_metrics(self, purpose: float = None, balance: float = None,
                       goals: float = None, habits: float = None):
        """Update life architecture metrics"""
        if purpose is not None:
            self.purpose_clarity = max(0, min(1, purpose))
        if balance is not None:
            self.life_balance = max(0, min(1, balance))
        if goals is not None:
            self.goal_alignment = max(0, min(1, goals))
        if habits is not None:
            self.habit_strength = max(0, min(1, habits))
    
    def add_life_goal(self, goal: str):
        """Add a life goal"""
        self.life_goals.append(goal)
