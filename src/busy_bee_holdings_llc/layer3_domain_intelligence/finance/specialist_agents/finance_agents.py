"""
Finance Domain Specialist Agents
Part of BB-DOM-001: Domain Intelligence Expansion Framework

Agents:
1. Financial Planner (Strategist) - Budgeting, saving strategies
2. Investment Strategist (Strategist) - Investment recommendations
3. Risk Governor (Governor) - Financial risk management
4. Portfolio Architect (Strategist) - Portfolio construction
5. Macro Analyst (Observer) - Economic monitoring
6. Options Intelligence (Strategist) - Alternative investment opportunities
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from layer3_domain_intelligence.base_specialist_agent import (
    SpecialistAgent, ObserverAgent, StrategistAgent, GovernorAgent,
    AgentSignal, AgentInsight, AgentRole
)


# ============== FINANCE AGENTS ==============

class FinancialPlannerAgent(StrategistAgent):
    """
    Financial Planner - Budgeting and saving strategies
    
    Role: Strategist
    Responsibilities: Create budgets, optimize savings, plan expenses
    """
    
    def __init__(self):
        super().__init__("finance_planner", "Financial Planner", "finance")
        self.budget_categories = {}
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        """Process financial signals for planning insights"""
        signal_type = signal.signal_type
        
        if signal_type == "income_change":
            return self._analyze_income_change(signal)
        elif signal_type == "expense_pattern":
            return self._analyze_expense_pattern(signal)
        elif signal_type == "savings_opportunity":
            return self._identify_savings_opportunity(signal)
        
        return None
    
    def _analyze_income_change(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        new_income = data.get("new_income", 0)
        
        recommendation = "Maintain current savings rate"
        if new_income > data.get("previous_income", 0):
            recommendation = f"Increase savings by {(new_income - data.get('previous_income', 0)) * 0.3:.0f}/month"
        
        return self.create_insight(
            insight_type="budget_recommendation",
            title="Income Change Detected",
            description=f"New income level: ${new_income:,.0f}. {recommendation}",
            confidence=0.85,
            priority="high",
            data={"new_income": new_income, "recommendation": recommendation}
        )
    
    def _analyze_expense_pattern(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        category = data.get("category", "general")
        amount = data.get("amount", 0)
        
        return self.create_insight(
            insight_type="expense_analysis",
            title=f"Expense Pattern: {category}",
            description=f"Detected ${amount:,.0f} in {category}. Review for optimization.",
            confidence=0.75,
            priority="medium",
            data={"category": category, "amount": amount}
        )
    
    def _identify_savings_opportunity(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        potential_savings = data.get("potential_savings", 0)
        
        return self.create_insight(
            insight_type="savings_opportunity",
            title="Savings Opportunity Found",
            description=f"Potential monthly savings: ${potential_savings:,.0f}",
            confidence=0.8,
            priority="high",
            data={"potential_savings": potential_savings}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["budget_creation", "savings_optimization", "expense_analysis"],
            "signal_types": ["income_change", "expense_pattern", "savings_opportunity"]
        }


class InvestmentStrategistAgent(StrategistAgent):
    """
    Investment Strategist - Investment recommendations
    
    Role: Strategist
    Responsibilities: Analyze markets, recommend investments, timing decisions
    """
    
    def __init__(self):
        super().__init__("investment_strategist", "Investment Strategist", "finance")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        """Process investment-related signals"""
        signal_type = signal.signal_type
        
        if signal_type == "market_opportunity":
            return self._analyze_market_opportunity(signal)
        elif signal_type == "portfolio_imbalance":
            return self._suggest_rebalancing(signal)
        elif signal_type == "investment_signal":
            return self._evaluate_investment(signal)
        
        return None
    
    def _analyze_market_opportunity(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        sector = data.get("sector", "general")
        strength = data.get("strength", 0.5)
        
        action = "Hold current positions"
        if strength > 0.7:
            action = f"Consider increasing allocation to {sector}"
        elif strength < 0.3:
            action = f"Reduce exposure to {sector}"
        
        return self.create_insight(
            insight_type="market_recommendation",
            title=f"Market Opportunity: {sector}",
            description=action,
            confidence=strength,
            priority="high" if strength > 0.7 else "medium",
            data={"sector": sector, "strength": strength}
        )
    
    def _suggest_rebalancing(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        current_allocation = data.get("current_allocation", {})
        
        return self.create_insight(
            insight_type="rebalancing_recommendation",
            title="Portfolio Rebalancing Needed",
            description=f"Current allocation differs from target. Review {list(current_allocation.keys())}.",
            confidence=0.8,
            priority="medium",
            data=current_allocation
        )
    
    def _evaluate_investment(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        investment = data.get("investment", "Unknown")
        expected_return = data.get("expected_return", 0)
        
        verdict = "Neutral - do your research"
        if expected_return > 0.15:
            verdict = "Attractive - consider allocation"
        elif expected_return < 0.05:
            verdict = "Low return - not recommended"
        
        return self.create_insight(
            insight_type="investment_evaluation",
            title=f"Investment Evaluation: {investment}",
            description=verdict,
            confidence=0.7,
            priority="medium",
            data={"investment": investment, "expected_return": expected_return}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["market_analysis", "investment_recommendations", "timing_decisions"],
            "signal_types": ["market_opportunity", "portfolio_imbalance", "investment_signal"]
        }


class FinanceRiskGovernorAgent(GovernorAgent):
    """
    Risk Governor - Financial risk management
    
    Role: Governor
    Responsibilities: Enforce risk limits, detect financial risks, maintain alignment
    """
    
    def __init__(self):
        super().__init__("finance_risk_governor", "Risk Governor", "finance")
        self.risk_limits = {
            "max_single_position": 0.25,  # 25% max in single asset
            "max_leverage": 1.5,
            "min_emergency_fund": 6  # months
        }
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        """Process risk-related signals"""
        signal_type = signal.signal_type
        
        if signal_type == "position_size":
            return self._check_position_size(signal)
        elif signal_type == "leverage_warning":
            return self._check_leverage(signal)
        elif signal_type == "emergency_fund_check":
            return self._check_emergency_fund(signal)
        
        return None
    
    def _check_position_size(self, signal: AgentSignal) -> Optional[AgentInsight]:
        data = signal.data
        position_size = data.get("position_size", 0)
        
        if position_size > self.risk_limits["max_single_position"]:
            return self.create_insight(
                insight_type="risk_violation",
                title="Position Size Risk",
                description=f"Position at {position_size:.0%} exceeds limit of {self.risk_limits['max_single_position']:.0%}",
                confidence=0.95,
                priority="critical",
                data={"position_size": position_size, "limit": self.risk_limits["max_single_position"]}
            )
        
        return self.create_insight(
            insight_type="risk_clear",
            title="Position Size Acceptable",
            description=f"Position at {position_size:.0%} within limits",
            confidence=0.95,
            priority="low",
            data={"position_size": position_size}
        )
    
    def _check_leverage(self, signal: AgentSignal) -> Optional[AgentInsight]:
        data = signal.data
        leverage = data.get("leverage", 1.0)
        
        if leverage > self.risk_limits["max_leverage"]:
            return self.create_insight(
                insight_type="risk_alert",
                title="High Leverage Warning",
                description=f"Leverage at {leverage:.1f}x exceeds safe limit of {self.risk_limits['max_leverage']:.1f}x",
                confidence=0.9,
                priority="critical",
                data={"leverage": leverage}
            )
        
        return None
    
    def _check_emergency_fund(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        months = data.get("months_covered", 0)
        
        if months < self.risk_limits["min_emergency_fund"]:
            return self.create_insight(
                insight_type="risk_warning",
                title="Emergency Fund Low",
                description=f"Only {months} months emergency fund. Recommended: {self.risk_limits['min_emergency_fund']} months.",
                confidence=0.9,
                priority="high",
                data={"months_covered": months, "recommended": self.risk_limits["min_emergency_fund"]}
            )
        
        return self.create_insight(
            insight_type="risk_clear",
            title="Emergency Fund Adequate",
            description=f"Emergency fund covers {months} months - within guidelines",
            confidence=0.9,
            priority="low",
            data={"months_covered": months}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "governor",
            "capabilities": ["risk_assessment", "limit_enforcement", "risk_alerts"],
            "signal_types": ["position_size", "leverage_warning", "emergency_fund_check"],
            "limits": self.risk_limits
        }


class PortfolioArchitectAgent(StrategistAgent):
    """
    Portfolio Architect - Portfolio construction
    
    Role: Strategist
    Responsibilities: Design portfolios, optimize allocation, manage diversification
    """
    
    def __init__(self):
        super().__init__("portfolio_architect", "Portfolio Architect", "finance")
        self.target_allocations = {
            "stocks": 0.60,
            "bonds": 0.25,
            "cash": 0.10,
            "alternatives": 0.05
        }
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        """Process portfolio design signals"""
        signal_type = signal.signal_type
        
        if signal_type == "new_capital":
            return self._design_allocation(signal)
        elif signal_type == "allocation_review":
            return self._review_allocation(signal)
        elif signal_type == "goal_change":
            return self._adjust_for_goal(signal)
        
        return None
    
    def _design_allocation(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        capital = data.get("capital", 0)
        
        allocation = {k: v * capital for k, v in self.target_allocations.items()}
        
        return self.create_insight(
            insight_type="allocation_design",
            title="New Portfolio Allocation",
            description=f"Recommended allocation for ${capital:,.0f}",
            confidence=0.8,
            priority="high",
            data={"total": capital, "allocation": allocation}
        )
    
    def _review_allocation(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        current = data.get("current", {})
        
        deviations = []
        for asset, target in self.target_allocations.items():
            current_pct = current.get(asset, 0)
            diff = abs(current_pct - target)
            if diff > 0.05:
                deviations.append(f"{asset}: {current_pct:.0%} vs {target:.0%}")
        
        if deviations:
            return self.create_insight(
                insight_type="allocation_review",
                title="Portfolio Deviations Detected",
                description=f"Adjust allocations: {', '.join(deviations)}",
                confidence=0.85,
                priority="medium",
                data={"deviations": deviations}
            )
        
        return self.create_insight(
            insight_type="allocation_ok",
            title="Portfolio Well-Balanced",
            description="All allocations within target ranges",
            confidence=0.85,
            priority="low",
            data={}
        )
    
    def _adjust_for_goal(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        goal = data.get("goal", "growth")
        timeline = data.get("timeline_years", 10)
        
        if goal == "preservation":
            new_alloc = {"stocks": 0.30, "bonds": 0.50, "cash": 0.15, "alternatives": 0.05}
        elif goal == "income":
            new_alloc = {"stocks": 0.40, "bonds": 0.45, "cash": 0.10, "alternatives": 0.05}
        else:  # growth
            new_alloc = {"stocks": 0.75, "bonds": 0.15, "cash": 0.05, "alternatives": 0.05}
        
        return self.create_insight(
            insight_type="goal_based_allocation",
            title=f"Adjusted for {goal} goal ({timeline} years)",
            description=f"New target allocation based on goal",
            confidence=0.75,
            priority="high",
            data={"goal": goal, "timeline": timeline, "allocation": new_alloc}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["portfolio_design", "allocation_optimization", "diversification"],
            "signal_types": ["new_capital", "allocation_review", "goal_change"]
        }


class MacroAnalystAgent(ObserverAgent):
    """
    Macro Analyst - Economic monitoring
    
    Role: Observer
    Responsibilities: Monitor economic indicators, detect trends, provide situational awareness
    """
    
    def __init__(self):
        super().__init__("macro_analyst", "Macro Analyst", "finance")
        self.indicators = {}
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        """Process macroeconomic signals"""
        signal_type = signal.signal_type
        
        if signal_type == "interest_rate":
            return self._analyze_interest_rate(signal)
        elif signal_type == "inflation":
            return self._analyze_inflation(signal)
        elif signal_type == "gdp_growth":
            return self._analyze_gdp(signal)
        elif signal_type == "employment":
            return self._analyze_employment(signal)
        
        return None
    
    def _analyze_interest_rate(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        rate = data.get("rate", 0)
        change = data.get("change", 0)
        
        outlook = "neutral"
        if change > 0.5:
            outlook = "tightening - negative for stocks"
        elif change < -0.5:
            outlook = "easing - positive for stocks"
        
        return self.create_insight(
            insight_type="macro_observation",
            title=f"Interest Rate: {rate:.2f}%",
            description=f"Rate change: {change:+.2f}%. Market outlook: {outlook}",
            confidence=0.85,
            priority="high" if abs(change) > 1 else "medium",
            data={"rate": rate, "change": change, "outlook": outlook}
        )
    
    def _analyze_inflation(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        rate = data.get("rate", 0)
        
        analysis = "stable"
        if rate > 5:
            analysis = "high - consider inflation protection"
        elif rate > 3:
            analysis = "elevated - monitor closely"
        
        return self.create_insight(
            insight_type="macro_observation",
            title=f"Inflation Rate: {rate:.1f}%",
            description=analysis,
            confidence=0.8,
            priority="high" if rate > 5 else "medium",
            data={"rate": rate}
        )
    
    def _analyze_gdp(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        growth = data.get("growth", 0)
        
        assessment = "moderate growth"
        if growth > 3:
            assessment = "strong growth - positive"
        elif growth < 0:
            assessment = "contraction - negative"
        
        return self.create_insight(
            insight_type="macro_observation",
            title=f"GDP Growth: {growth:.1f}%",
            description=assessment,
            confidence=0.75,
            priority="medium",
            data={"growth": growth}
        )
    
    def _analyze_employment(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        rate = data.get("rate", 0)
        
        assessment = "normal"
        if rate < 4:
            assessment = "very tight - wage pressure"
        elif rate > 8:
            assessment = "weak - economic concern"
        
        return self.create_insight(
            insight_type="macro_observation",
            title=f"Employment Rate: {rate:.1f}%",
            description=assessment,
            confidence=0.8,
            priority="medium",
            data={"rate": rate}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "observer",
            "capabilities": ["economic_monitoring", "trend_detection", "market_context"],
            "signal_types": ["interest_rate", "inflation", "gdp_growth", "employment"]
        }


class OptionsIntelligenceAgent(StrategistAgent):
    """
    Options Intelligence - Alternative investment opportunities
    
    Role: Strategist
    Responsibilities: Discover alternatives, evaluate non-traditional investments
    """
    
    def __init__(self):
        super().__init__("options_intelligence", "Options Intelligence", "finance")
        self.alternative_types = ["real_estate", "commodities", "crypto", "private_equity", "collectibles"]
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        """Process alternative investment signals"""
        signal_type = signal.signal_type
        
        if signal_type == "alternative_opportunity":
            return self._evaluate_alternative(signal)
        elif signal_type == "diversification_need":
            return self._suggest_alternatives(signal)
        elif signal_type == "market_gap":
            return self._identify_gap(signal)
        
        return None
    
    def _evaluate_alternative(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        alt_type = data.get("type", "unknown")
        expected_return = data.get("expected_return", 0)
        risk = data.get("risk", 0.5)
        
        score = (expected_return * 0.6) + ((1 - risk) * 0.4)
        
        verdict = "Consider"
        if score > 0.7:
            verdict = "Strong opportunity"
        elif score < 0.4:
            verdict = "Not recommended"
        
        return self.create_insight(
            insight_type="alternative_evaluation",
            title=f"Alternative: {alt_type.title()}",
            description=f"{verdict} - Return: {expected_return:.0%}, Risk: {risk:.0%}",
            confidence=0.65,
            priority="medium",
            data={"type": alt_type, "score": score}
        )
    
    def _suggest_alternatives(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        current_allocation = data.get("current_allocation", [])
        
        # Suggest alternatives not currently in portfolio
        suggestions = [a for a in self.alternative_types if a not in current_allocation]
        
        return self.create_insight(
            insight_type="alternative_suggestion",
            title="Diversification Options",
            description=f"Consider adding: {', '.join(suggestions[:3])}",
            confidence=0.7,
            priority="medium",
            data={"suggestions": suggestions}
        )
    
    def _identify_gap(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        gap_type = data.get("gap_type", "unknown")
        
        suggestions = {
            "liquidity": "Consider money market or short-term bonds",
            "volatility": "Consider adding defensive assets",
            "correlation": "Consider international diversification",
            "yield": "Consider dividend stocks or REITs"
        }
        
        return self.create_insight(
            insight_type="gap_identification",
            title=f"Portfolio Gap: {gap_type}",
            description=suggestions.get(gap_type, "Review portfolio structure"),
            confidence=0.7,
            priority="medium",
            data={"gap_type": gap_type}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["alternative_analysis", "opportunity_discovery", "gap_identification"],
            "signal_types": ["alternative_opportunity", "diversification_need", "market_gap"]
        }
