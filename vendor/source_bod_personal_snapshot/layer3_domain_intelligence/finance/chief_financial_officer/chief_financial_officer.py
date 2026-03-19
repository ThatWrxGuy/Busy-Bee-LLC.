"""
Chief Financial Officer - Finance domain intelligence
Part of Layer 3: Domain Intelligence Systems
"""

from typing import Dict, Any, List
from datetime import datetime
from ...base_chief_officer import ChiefOfficer, DomainSignal, DomainStrategy, DomainReport


class ChiefFinancialOfficer(ChiefOfficer):
    """
    Chief Financial Officer manages the Finance domain.
    
    Responsibilities:
    - Analyze financial signals
    - Generate financial strategies
    - Monitor portfolio risk
    - Produce finance intelligence reports
    """
    
    def __init__(self):
        super().__init__(domain="finance", title="Chief Financial Officer")
        self.specialist_agents = [
            "investment_agent",
            "budget_agent", 
            "tax_agent",
            "cash_flow_agent"
        ]
        
        # Financial state
        self.portfolio_value = 0.0
        self.monthly_income = 0.0
        self.monthly_expenses = 0.0
        self.assets = {}
        self.liabilities = {}
    
    def analyze_signals(self, signals: List[DomainSignal]) -> Dict[str, Any]:
        """Analyze financial signals"""
        analysis = {
            "domain": self.domain,
            "signal_count": len(signals),
            "signals_analyzed": [],
            "opportunities": [],
            "risks": [],
            "market_indicators": {},
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
            
            # Categorize by signal type
            if signal.signal_type == "investment_opportunity":
                analysis["opportunities"].append({
                    "title": signal.title,
                    "strength": signal.strength,
                    "data": signal.data
                })
            elif signal.signal_type == "market_risk":
                analysis["risks"].append({
                    "title": signal.title,
                    "strength": signal.strength,
                    "data": signal.data
                })
        
        # Calculate financial health indicators
        analysis["financial_health"] = self._calculate_financial_health()
        
        return analysis
    
    def _calculate_financial_health(self) -> Dict[str, Any]:
        """Calculate financial health indicators"""
        net_worth = self.portfolio_value + sum(self.assets.values()) - sum(self.liabilities.values())
        
        cash_flow = self.monthly_income - self.monthly_expenses
        
        savings_rate = (cash_flow / self.monthly_income) if self.monthly_income > 0 else 0
        
        # Health status
        if savings_rate > 0.2 and net_worth > 100000:
            health_status = "excellent"
        elif savings_rate > 0.1 and net_worth > 50000:
            health_status = "good"
        elif savings_rate > 0:
            health_status = "fair"
        else:
            health_status = "needs_attention"
        
        return {
            "net_worth": net_worth,
            "monthly_cash_flow": cash_flow,
            "savings_rate": savings_rate,
            "portfolio_value": self.portfolio_value,
            "total_assets": sum(self.assets.values()),
            "total_liabilities": sum(self.liabilities.values()),
            "status": health_status
        }
    
    def generate_strategy(self, analysis: Dict[str, Any]) -> DomainStrategy:
        """Generate a financial strategy"""
        health = analysis.get("financial_health", {})
        opportunities = analysis.get("opportunities", [])
        risks = analysis.get("risks", [])
        
        # Determine priority based on health and opportunities
        if health.get("status") == "needs_attention" or len(risks) > 2:
            priority = "critical"
            risk_level = "high"
        elif health.get("status") in ["fair", "good"]:
            priority = "high"
            risk_level = "medium"
        else:
            priority = "medium"
            risk_level = "low"
        
        # Generate action items
        action_items = []
        
        if health.get("savings_rate", 0) < 0.1:
            action_items.append("Increase savings rate to at least 10%")
        
        if opportunities:
            action_items.append(f"Evaluate {len(opportunities)} investment opportunities")
        
        if risks:
            action_items.append(f"Mitigate {len(risks)} identified financial risks")
        
        if not action_items:
            action_items = ["Maintain current financial position", "Continue monitoring markets"]
        
        # Calculate expected impact
        expected_impact = 0.5
        if health.get("status") != "excellent":
            expected_impact += 0.2
        if opportunities:
            expected_impact += 0.1 * len(opportunities)
        
        strategy = DomainStrategy(
            id=f"strat_{self.domain}_{len(self.strategies) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title=f"Finance Strategy - {health.get('status', 'unknown').title()}",
            description=f"Financial strategy addressing current health: {health.get('status', 'unknown')}",
            priority=priority,
            expected_impact=min(1.0, expected_impact),
            risk_level=risk_level,
            action_items=action_items
        )
        
        self.add_strategy(strategy)
        return strategy
    
    def create_report(self) -> DomainReport:
        """Create finance intelligence report"""
        health = self._calculate_financial_health()
        
        sections = {
            "capital_posture": {
                "net_worth": health["net_worth"],
                "portfolio_value": health["portfolio_value"],
                "total_assets": health["total_assets"],
                "total_liabilities": health["total_liabilities"]
            },
            "cash_flow": {
                "monthly_income": self.monthly_income,
                "monthly_expenses": self.monthly_expenses,
                "monthly_cash_flow": health["monthly_cash_flow"],
                "savings_rate": health["savings_rate"]
            },
            "portfolio_risk": {
                "diversification": "moderate",  # Would be calculated in real implementation
                "volatility": "moderate"
            },
            "health_status": health["status"]
        }
        
        # Generate recommendations
        recommendations = []
        
        if health["savings_rate"] < 0.1:
            recommendations.append("Priority: Increase emergency fund savings")
        
        if health["total_liabilities"] > health["total_assets"] * 0.5:
            recommendations.append("Priority: Reduce high-interest debt")
        
        if not recommendations:
            recommendations = [
                "Continue current investment strategy",
                "Review portfolio allocation quarterly",
                "Maintain emergency fund at 6 months expenses"
            ]
        
        report = DomainReport(
            id=f"report_{self.domain}_{len(self.reports) + 1}_{datetime.now().timestamp()}",
            domain=self.domain,
            title="Finance Intelligence Report",
            sections=sections,
            recommendations=recommendations
        )
        
        self.reports.append(report)
        return report
    
    def update_portfolio(self, portfolio_value: float):
        """Update portfolio value"""
        self.portfolio_value = portfolio_value
    
    def update_cash_flow(self, income: float, expenses: float):
        """Update cash flow"""
        self.monthly_income = income
        self.monthly_expenses = expenses
    
    def add_asset(self, name: str, value: float):
        """Add an asset"""
        self.assets[name] = value
    
    def add_liability(self, name: str, amount: float):
        """Add a liability"""
        self.liabilities[name] = amount
