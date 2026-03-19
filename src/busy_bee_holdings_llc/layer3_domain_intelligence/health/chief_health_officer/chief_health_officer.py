"""
Chief Health Officer - Health domain intelligence
Part of Layer 3: Domain Intelligence Systems
"""

from typing import Dict, Any, List
from datetime import datetime
from ...base_chief_officer import ChiefOfficer, DomainSignal, DomainStrategy, DomainReport


class ChiefHealthOfficer(ChiefOfficer):
    """
    Chief Health Officer manages the Health domain.
    
    Responsibilities:
    - Analyze health signals
    - Generate health strategies
    - Monitor wellness metrics
    - Produce health intelligence reports
    """
    
    def __init__(self):
        super().__init__(domain="health", title="Chief Health Officer")
        self.specialist_agents = [
            "fitness_agent",
            "nutrition_agent",
            "sleep_agent",
            "mental_health_agent"
        ]
        
        # Health state
        self.fitness_level = 0.5  # 0-1
        self.sleep_quality = 0.5  # 0-1
        self.stress_level = 0.5  # 0-1
        self.health_goals = {}
    
    def analyze_signals(self, signals: List[DomainSignal]) -> Dict[str, Any]:
        """Analyze health signals"""
        analysis = {
            "domain": self.domain,
            "signal_count": len(signals),
            "signals_analyzed": [],
            "opportunities": [],
            "risks": [],
            "wellness_indicators": {},
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
            
            if signal.signal_type == "wellness_opportunity":
                analysis["opportunities"].append({
                    "title": signal.title,
                    "data": signal.data
                })
            elif signal.signal_type == "health_risk":
                analysis["risks"].append({
                    "title": signal.title,
                    "data": signal.data
                })
        
        analysis["wellness_indicators"] = self._calculate_wellness()
        
        return analysis
    
    def _calculate_wellness(self) -> Dict[str, Any]:
        """Calculate wellness indicators"""
        overall_wellness = (self.fitness_level + self.sleep_quality + (1 - self.stress_level)) / 3
        
        if overall_wellness > 0.8:
            status = "excellent"
        elif overall_wellness > 0.6:
            status = "good"
        elif overall_wellness > 0.4:
            status = "fair"
        else:
            status = "needs_attention"
        
        return {
            "overall_wellness": overall_wellness,
            "fitness_level": self.fitness_level,
            "sleep_quality": self.sleep_quality,
            "stress_level": self.stress_level,
            "status": status
        }
    
    def generate_strategy(self, analysis: Dict[str, Any]) -> DomainStrategy:
        """Generate a health strategy"""
        wellness = analysis.get("wellness_indicators", {})
        risks = analysis.get("risks", [])
        
        if wellness.get("status") == "needs_attention" or len(risks) > 1:
            priority = "critical"
            risk_level = "high"
        elif wellness.get("status") == "fair":
            priority = "high"
            risk_level = "medium"
        else:
            priority = "medium"
            risk_level = "low"
        
        action_items = []
        
        if self.fitness_level < 0.6:
            action_items.append("Increase physical activity to 150 min/week")
        
        if self.sleep_quality < 0.6:
            action_items.append("Improve sleep hygiene and aim for 7-8 hours")
        
        if self.stress_level > 0.6:
            action_items.append("Implement stress management techniques")
        
        if not action_items:
            action_items = ["Maintain current wellness routines", "Continue tracking health metrics"]
        
        expected_impact = 0.6
        if wellness.get("status") != "excellent":
            expected_impact += 0.2
        
        strategy = DomainStrategy(
            id=f"strat_{self.domain}_{len(self.strategies) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title=f"Health Strategy - {wellness.get('status', 'unknown').title()}",
            description=f"Health strategy addressing wellness: {wellness.get('status', 'unknown')}",
            priority=priority,
            expected_impact=min(1.0, expected_impact),
            risk_level=risk_level,
            action_items=action_items
        )
        
        self.add_strategy(strategy)
        return strategy
    
    def create_report(self) -> DomainReport:
        """Create health intelligence report"""
        wellness = self._calculate_wellness()
        
        sections = {
            "wellness_overview": {
                "overall_wellness": wellness["overall_wellness"],
                "status": wellness["status"]
            },
            "fitness": {
                "level": self.fitness_level,
                "recommendation": "Maintain or improve current activity"
            },
            "sleep": {
                "quality": self.sleep_quality,
                "recommendation": "Aim for consistent sleep schedule"
            },
            "stress": {
                "level": self.stress_level,
                "recommendation": "Practice regular stress management"
            }
        }
        
        recommendations = []
        
        if self.fitness_level < 0.5:
            recommendations.append("Priority: Establish regular exercise routine")
        if self.sleep_quality < 0.5:
            recommendations.append("Priority: Address sleep issues")
        if self.stress_level > 0.7:
            recommendations.append("Priority: High stress level - seek support")
        
        if not recommendations:
            recommendations = [
                "Maintain current wellness routines",
                "Continue regular health check-ups",
                "Track health metrics consistently"
            ]
        
        report = DomainReport(
            id=f"report_{self.domain}_{len(self.reports) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title="Health Intelligence Report",
            sections=sections,
            recommendations=recommendations
        )
        
        self.reports.append(report)
        return report
    
    def update_metrics(self, fitness: float = None, sleep: float = None, stress: float = None):
        """Update health metrics"""
        if fitness is not None:
            self.fitness_level = max(0, min(1, fitness))
        if sleep is not None:
            self.sleep_quality = max(0, min(1, sleep))
        if stress is not None:
            self.stress_level = max(0, min(1, stress))
