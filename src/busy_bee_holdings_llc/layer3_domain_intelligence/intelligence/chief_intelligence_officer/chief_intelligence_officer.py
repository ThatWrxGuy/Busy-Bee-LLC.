"""
Chief Intelligence Officer - Intelligence domain intelligence
Part of Layer 3: Domain Intelligence Systems
"""

from typing import Dict, Any, List
from datetime import datetime
from ...base_chief_officer import ChiefOfficer, DomainSignal, DomainStrategy, DomainReport


class ChiefIntelligenceOfficer(ChiefOfficer):
    """
    Chief Intelligence Officer manages the Intelligence domain.
    
    Responsibilities:
    - Analyze intelligence signals
    - Generate intelligence strategies
    - Monitor information sources
    - Produce intelligence reports
    """
    
    def __init__(self):
        super().__init__(domain="intelligence", title="Chief Intelligence Officer")
        self.specialist_agents = [
            "research_agent",
            "trend_analysis_agent",
            "competitor_intel_agent",
            "market_intelligence_agent"
        ]
        
        # Intelligence state
        self.research_depth = 0.5
        self.trend_awareness = 0.5
        self.competitor_intel = 0.5
        self.market_intel = 0.5
    
    def analyze_signals(self, signals: List[DomainSignal]) -> Dict[str, Any]:
        """Analyze intelligence signals"""
        analysis = {
            "domain": self.domain,
            "signal_count": len(signals),
            "signals_analyzed": [],
            "opportunities": [],
            "risks": [],
            "intelligence_indicators": {},
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
            
            if signal.signal_type == "intelligence_opportunity":
                analysis["opportunities"].append({
                    "title": signal.title,
                    "data": signal.data
                })
            elif signal.signal_type == "intelligence_risk":
                analysis["risks"].append({
                    "title": signal.title,
                    "data": signal.data
                })
        
        analysis["intelligence_indicators"] = self._calculate_intelligence_capability()
        
        return analysis
    
    def _calculate_intelligence_capability(self) -> Dict[str, Any]:
        """Calculate intelligence capability"""
        overall = (self.research_depth + self.trend_awareness + 
                   self.competitor_intel + self.market_intel) / 4
        
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
            "research_depth": self.research_depth,
            "trend_awareness": self.trend_awareness,
            "competitor_intel": self.competitor_intel,
            "market_intel": self.market_intel,
            "status": status
        }
    
    def generate_strategy(self, analysis: Dict[str, Any]) -> DomainStrategy:
        """Generate an intelligence strategy"""
        intel = analysis.get("intelligence_indicators", {})
        opportunities = analysis.get("opportunities", [])
        risks = analysis.get("risks", [])
        
        if intel.get("status") == "needs_attention" or len(risks) > 1:
            priority = "critical"
            risk_level = "high"
        elif intel.get("status") == "fair":
            priority = "high"
            risk_level = "medium"
        else:
            priority = "medium"
            risk_level = "low"
        
        action_items = []
        
        if self.research_depth < 0.6:
            action_items.append("Deepen research capabilities")
        
        if self.trend_awareness < 0.6:
            action_items.append("Improve trend analysis")
        
        if self.competitor_intel < 0.6:
            action_items.append("Enhance competitor intelligence")
        
        if self.market_intel < 0.6:
            action_items.append("Expand market intelligence")
        
        if opportunities:
            action_items.append(f"Capitalize on {len(opportunities)} intelligence opportunities")
        
        if not action_items:
            action_items = ["Maintain intelligence gathering", "Continue monitoring trends"]
        
        expected_impact = 0.5
        if intel.get("status") != "excellent":
            expected_impact += 0.2
        
        strategy = DomainStrategy(
            id=f"strat_{self.domain}_{len(self.strategies) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title=f"Intelligence Strategy - {intel.get('status', 'unknown').title()}",
            description=f"Intelligence strategy addressing: {intel.get('status', 'unknown')}",
            priority=priority,
            expected_impact=min(1.0, expected_impact),
            risk_level=risk_level,
            action_items=action_items
        )
        
        self.add_strategy(strategy)
        return strategy
    
    def create_report(self) -> DomainReport:
        """Create intelligence report"""
        intel = self._calculate_intelligence_capability()
        
        sections = {
            "intelligence_overview": {
                "overall": intel["overall"],
                "status": intel["status"]
            },
            "research": {"depth": self.research_depth},
            "trends": {"awareness": self.trend_awareness},
            "competitors": {"intel": self.competitor_intel},
            "market": {"intelligence": self.market_intel}
        }
        
        recommendations = []
        
        if self.research_depth < 0.5:
            recommendations.append("Priority: Develop research capabilities")
        if self.trend_awareness < 0.5:
            recommendations.append("Priority: Improve trend monitoring")
        if self.competitor_intel < 0.5:
            recommendations.append("Priority: Enhance competitor analysis")
        if self.market_intel < 0.5:
            recommendations.append("Priority: Expand market intelligence")
        
        if not recommendations:
            recommendations = [
                "Maintain intelligence capabilities",
                "Continue monitoring key areas",
                "Share intelligence insights"
            ]
        
        report = DomainReport(
            id=f"report_{self.domain}_{len(self.reports) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title="Intelligence Report",
            sections=sections,
            recommendations=recommendations
        )
        
        self.reports.append(report)
        return report
    
    def update_metrics(self, research: float = None, trends: float = None,
                       competitors: float = None, market: float = None):
        """Update intelligence metrics"""
        if research is not None:
            self.research_depth = max(0, min(1, research))
        if trends is not None:
            self.trend_awareness = max(0, min(1, trends))
        if competitors is not None:
            self.competitor_intel = max(0, min(1, competitors))
        if market is not None:
            self.market_intel = max(0, min(1, market))
