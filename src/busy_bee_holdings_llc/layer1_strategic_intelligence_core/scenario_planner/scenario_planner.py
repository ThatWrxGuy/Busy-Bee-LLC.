"""
Scenario Planner - Plans and evaluates strategic scenarios
Part of Layer 1: Strategic Intelligence Core
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ScenarioType(Enum):
    """Types of scenarios"""
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic" 
    REALISTIC = "realistic"
    CRISIS = "crisis"


class Timeframe(Enum):
    """Scenario timeframes"""
    IMMEDIATE = "immediate"  # 0-3 months
    SHORT_TERM = "short_term"  # 3-12 months
    MEDIUM_TERM = "medium_term"  # 1-3 years
    LONG_TERM = "long_term"  # 3-10 years


@dataclass
class Scenario:
    """A strategic scenario"""
    id: str
    name: str
    description: str
    scenario_type: ScenarioType
    timeframe: Timeframe
    domain: str
    assumptions: List[str]
    key_variables: Dict[str, Any]
    projected_outcomes: Dict[str, float]
    probability: float  # 0.0 - 1.0
    created_at: datetime = field(default_factory=datetime.now)


class ScenarioPlanner:
    """
    Scenario Planner creates and evaluates strategic scenarios.
    
    Responsibilities:
    - Generate multiple scenarios
    - Evaluate scenario probabilities
    - Support strategic planning
    """
    
    def __init__(self):
        self.scenarios: List[Scenario] = []
    
    def create_scenario(
        self,
        name: str,
        description: str,
        scenario_type: ScenarioType,
        timeframe: Timeframe,
        domain: str,
        assumptions: List[str],
        key_variables: Dict[str, Any]
    ) -> Scenario:
        """Create a new scenario"""
        scenario = Scenario(
            id=f"scenario_{len(self.scenarios) + 1}_{datetime.now().timestamp()}",
            name=name,
            description=description,
            scenario_type=scenario_type,
            timeframe=timeframe,
            domain=domain,
            assumptions=assumptions,
            key_variables=key_variables,
            projected_outcomes={},
            probability=0.5  # Default probability
        )
        self.scenarios.append(scenario)
        return scenario
    
    def generate_domain_scenarios(
        self,
        domain: str,
        current_state: Dict[str, Any]
    ) -> List[Scenario]:
        """Generate multiple scenarios for a domain"""
        scenarios = []
        
        # Optimistic scenario
        optimistic = self.create_scenario(
            name=f"{domain} - Optimistic",
            description=f"Best case scenario for {domain}",
            scenario_type=ScenarioType.OPTIMISTIC,
            timeframe=Timeframe.SHORT_TERM,
            domain=domain,
            assumptions=[
                "All favorable conditions materialize",
                "No major disruptions occur",
                "Resources are abundant"
            ],
            key_variables={**current_state, "modifier": 1.3}
        )
        optimistic.probability = 0.2
        scenarios.append(optimistic)
        
        # Realistic scenario
        realistic = self.create_scenario(
            name=f"{domain} - Realistic",
            description=f"Most likely scenario for {domain}",
            scenario_type=ScenarioType.REALISTIC,
            timeframe=Timeframe.SHORT_TERM,
            domain=domain,
            assumptions=[
                "Current trends continue",
                "Some challenges arise but are manageable",
                "Resources are stable"
            ],
            key_variables={**current_state, "modifier": 1.0}
        )
        realistic.probability = 0.5
        scenarios.append(realistic)
        
        # Pessimistic scenario
        pessimistic = self.create_scenario(
            name=f"{domain} - Pessimistic",
            description=f"Worst case scenario for {domain}",
            scenario_type=ScenarioType.PESSIMISTIC,
            timeframe=Timeframe.SHORT_TERM,
            domain=domain,
            assumptions=[
                "Major challenges arise",
                "Resources become constrained",
                "External pressures increase"
            ],
            key_variables={**current_state, "modifier": 0.7}
        )
        pessimistic.probability = 0.2
        scenarios.append(pessimistic)
        
        # Crisis scenario
        crisis = self.create_scenario(
            name=f"{domain} - Crisis",
            description=f"Crisis scenario for {domain}",
            scenario_type=ScenarioType.CRISIS,
            timeframe=Timeframe.IMMEDIATE,
            domain=domain,
            assumptions=[
                "Major disruption occurs",
                "Emergency response required",
                "Significant resource allocation needed"
            ],
            key_variables={**current_state, "modifier": 0.4}
        )
        crisis.probability = 0.1
        scenarios.append(crisis)
        
        return scenarios
    
    def evaluate_scenario(self, scenario_id: str, outcomes: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate scenario outcomes"""
        scenario = next((s for s in self.scenarios if s.id == scenario_id), None)
        
        if not scenario:
            return {"error": "Scenario not found"}
        
        scenario.projected_outcomes = outcomes
        
        # Calculate expected value
        expected_value = sum(
            outcome * scenario.probability 
            for outcome in outcomes.values()
        )
        
        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "projected_outcomes": outcomes,
            "expected_value": expected_value,
            "probability": scenario.probability,
            "evaluated_at": datetime.now().isoformat()
        }
    
    def get_scenarios_by_domain(self, domain: str) -> List[Scenario]:
        """Get all scenarios for a domain"""
        return [s for s in self.scenarios if s.domain == domain]
    
    def compare_scenarios(
        self,
        domain: str,
        timeframe: Optional[Timeframe] = None
    ) -> Dict[str, Any]:
        """Compare scenarios for a domain"""
        scenarios = self.get_scenarios_by_domain(domain)
        
        if timeframe:
            scenarios = [s for s in scenarios if s.timeframe == timeframe]
        
        if not scenarios:
            return {"error": "No scenarios found"}
        
        # Sort by probability
        sorted_scenarios = sorted(scenarios, key=lambda s: s.probability, reverse=True)
        
        return {
            "domain": domain,
            "timeframe": timeframe.value if timeframe else "all",
            "scenarios": [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.scenario_type.value,
                    "probability": s.probability,
                    "assumptions": s.assumptions
                }
                for s in sorted_scenarios
            ],
            "most_likely": sorted_scenarios[0].name if sorted_scenarios else None,
            "compared_at": datetime.now().isoformat()
        }
