"""
Simulation Engine - Digital testing ground for strategies
Part of Layer 1: Strategic Intelligence Core
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class SimulationResult:
    """Results from a strategy simulation"""
    hypothesis_id: str
    simulation_type: str  # market, life_scenario, capital, risk_stress
    success_rate: float
    risk_score: float
    outcomes: List[Dict[str, Any]]
    metrics: Dict[str, float]
    executed_at: datetime
    duration_ms: float


class SimulationEngine:
    """
    Simulation Engine acts as a digital testing ground.
    
    Simulation types:
    - Market simulations
    - Life scenario simulations
    - Capital allocation simulations
    - Risk stress tests
    """
    
    def __init__(self):
        self.simulation_history: List[SimulationResult] = []
    
    def simulate(
        self,
        hypothesis_id: str,
        simulation_type: str,
        parameters: Dict[str, Any]
    ) -> SimulationResult:
        """Run a simulation for a given hypothesis"""
        
        start_time = datetime.now()
        
        # Route to appropriate simulation type
        if simulation_type == "market":
            result = self._simulate_market(hypothesis_id, parameters)
        elif simulation_type == "life_scenario":
            result = self._simulate_life_scenario(hypothesis_id, parameters)
        elif simulation_type == "capital":
            result = self._simulate_capital(hypothesis_id, parameters)
        elif simulation_type == "risk_stress":
            result = self._simulate_risk_stress(hypothesis_id, parameters)
        else:
            result = self._default_simulation(hypothesis_id, parameters)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        
        result.executed_at = end_time
        result.duration_ms = duration
        
        self.simulation_history.append(result)
        return result
    
    def _simulate_market(self, hypothesis_id: str, params: Dict[str, Any]) -> SimulationResult:
        """Simulate market conditions for a strategy"""
        # Simplified market simulation
        base_success = params.get("base_success_rate", 0.6)
        market_conditions = params.get("market_conditions", "neutral")
        
        # Adjust based on market conditions
        condition_modifiers = {
            "bull": 0.15,
            "neutral": 0.0,
            "bear": -0.2,
            "volatile": -0.1
        }
        
        success_rate = base_success + condition_modifiers.get(market_conditions, 0.0)
        success_rate = max(0.0, min(1.0, success_rate))
        
        outcomes = [
            {"scenario": "best_case", "probability": 0.2, "outcome": "exceeds_targets"},
            {"scenario": "expected", "probability": 0.5, "outcome": "meets_targets"},
            {"scenario": "worst_case", "probability": 0.3, "outcome": "below_targets"}
        ]
        
        risk_score = 1.0 - success_rate
        
        return SimulationResult(
            hypothesis_id=hypothesis_id,
            simulation_type="market",
            success_rate=success_rate,
            risk_score=risk_score,
            outcomes=outcomes,
            metrics={
                "expected_value": success_rate * params.get("potential_return", 10000),
                "volatility": 0.15 if market_conditions == "volatile" else 0.08
            },
            executed_at=datetime.now(),
            duration_ms=0
        )
    
    def _simulate_life_scenario(self, hypothesis_id: str, params: Dict[str, Any]) -> SimulationResult:
        """Simulate life scenario outcomes"""
        timeline_years = params.get("timeline_years", 5)
        impact_factors = params.get("impact_factors", {})
        
        # Calculate life impact score
        health_impact = impact_factors.get("health", 0.5)
        financial_impact = impact_factors.get("financial", 0.5)
        relationships_impact = impact_factors.get("relationships", 0.5)
        
        success_rate = (health_impact + financial_impact + relationships_impact) / 3.0
        risk_score = 1.0 - success_rate
        
        outcomes = [
            {"scenario": "optimal", "probability": 0.25, "outcome": "all_goals_achieved"},
            {"scenario": "good", "probability": 0.45, "outcome": "most_goals_achieved"},
            {"scenario": "challenging", "probability": 0.30, "outcome": "some_goals_missed"}
        ]
        
        return SimulationResult(
            hypothesis_id=hypothesis_id,
            simulation_type="life_scenario",
            success_rate=success_rate,
            risk_score=risk_score,
            outcomes=outcomes,
            metrics={
                "timeline_years": timeline_years,
                "life_quality_score": success_rate * 10,
                "sustainability": 0.75
            },
            executed_at=datetime.now(),
            duration_ms=0
        )
    
    def _simulate_capital(self, hypothesis_id: str, params: Dict[str, Any]) -> SimulationResult:
        """Simulate capital allocation outcomes"""
        initial_capital = params.get("initial_capital", 100000)
        allocation = params.get("allocation", {})
        expected_returns = params.get("expected_returns", {})
        
        # Calculate portfolio projection
        total_return = 0
        for asset_class, percentage in allocation.items():
            base_return = expected_returns.get(asset_class, 0.05)
            return_for_class = initial_capital * percentage * base_return
            total_return += return_for_class
        
        success_rate = min(1.0, total_return / (initial_capital * 0.1))  # 10% as baseline
        risk_score = 1.0 - success_rate
        
        outcomes = [
            {"scenario": "growth", "probability": 0.4, "outcome": "capital_grows"},
            {"scenario": "stable", "probability": 0.45, "outcome": "capital_stable"},
            {"scenario": "decline", "probability": 0.15, "outcome": "capital_declines"}
        ]
        
        return SimulationResult(
            hypothesis_id=hypothesis_id,
            simulation_type="capital",
            success_rate=success_rate,
            risk_score=risk_score,
            outcomes=outcomes,
            metrics={
                "initial_capital": initial_capital,
                "projected_return": total_return,
                "roi_percentage": (total_return / initial_capital) * 100
            },
            executed_at=datetime.now(),
            duration_ms=0
        )
    
    def _simulate_risk_stress(self, hypothesis_id: str, params: Dict[str, Any]) -> SimulationResult:
        """Run risk stress tests"""
        baseline_risk = params.get("baseline_risk", 0.3)
        stress_scenarios = params.get("stress_scenarios", ["market_crash", "health_crisis"])
        
        # Calculate stress impact
        stress_impacts = {
            "market_crash": 0.4,
            "health_crisis": 0.3,
            "job_loss": 0.35,
            "relationship_crisis": 0.25
        }
        
        max_impact = max(stress_impacts.get(s, 0.2) for s in stress_scenarios)
        stressed_risk = min(1.0, baseline_risk + max_impact)
        
        success_rate = 1.0 - stressed_risk
        risk_score = stressed_risk
        
        outcomes = [
            {"scenario": s, "probability": 1.0/len(stress_scenarios), "outcome": f"{s}_tested"}
            for s in stress_scenarios
        ]
        
        return SimulationResult(
            hypothesis_id=hypothesis_id,
            simulation_type="risk_stress",
            success_rate=success_rate,
            risk_score=risk_score,
            outcomes=outcomes,
            metrics={
                "baseline_risk": baseline_risk,
                "stressed_risk": stressed_risk,
                "risk_increase": max_impact
            },
            executed_at=datetime.now(),
            duration_ms=0
        )
    
    def _default_simulation(self, hypothesis_id: str, params: Dict[str, Any]) -> SimulationResult:
        """Default simulation when type is unknown"""
        return SimulationResult(
            hypothesis_id=hypothesis_id,
            simulation_type="default",
            success_rate=0.5,
            risk_score=0.5,
            outcomes=[],
            metrics={},
            executed_at=datetime.now(),
            duration_ms=0
        )
    
    def get_simulation_history(self, hypothesis_id: Optional[str] = None) -> List[SimulationResult]:
        """Get simulation history, optionally filtered by hypothesis"""
        if hypothesis_id:
            return [r for r in self.simulation_history if r.hypothesis_id == hypothesis_id]
        return self.simulation_history
