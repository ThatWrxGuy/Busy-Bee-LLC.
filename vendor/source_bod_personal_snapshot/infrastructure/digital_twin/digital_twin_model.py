"""
Digital Twin Model

BB-INF-008: Life Signal Graph & Personal Digital Twin Engine

A computational model of the user's life system for simulation and prediction.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import random
import logging

from ..life_graph.graph_models import Domain, NodeType


logger = logging.getLogger(__name__)


class TwinState(Enum):
    """State of the digital twin"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SIMULATING = "simulating"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class LifeVariable:
    """A variable in the life system model"""
    name: str
    domain: Domain
    current_value: float
    min_value: float
    max_value: float
    
    # Dynamics
    growth_rate: float = 0.0  # Expected change per time unit
    volatility: float = 0.1   # Random variation
    
    # Relationships
    depends_on: List[str] = field(default_factory=list)
    influences: List[str] = field(default_factory=list)
    
    # History
    history: List[Tuple[datetime, float]] = field(default_factory=list)
    
    def add_history(self, timestamp: datetime, value: float) -> None:
        """Add a value to history"""
        self.history.append((timestamp, value))
        # Keep last 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
    
    def project(self, time_steps: int) -> List[float]:
        """Project future values"""
        values = [self.current_value]
        value = self.current_value
        
        for _ in range(time_steps):
            # Base growth
            value = value + self.growth_rate
            
            # Add some noise
            noise = random.gauss(0, self.volatility * abs(value))
            value = value + noise
            
            # Clamp to bounds
            value = max(self.min_value, min(self.max_value, value))
            values.append(value)
        
        return values


@dataclass
class DomainModel:
    """Model for a specific life domain"""
    domain: Domain
    variables: Dict[str, LifeVariable] = field(default_factory=dict)
    
    # Domain-specific parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def get_variable(self, name: str) -> Optional[LifeVariable]:
        """Get a variable by name"""
        return self.variables.get(name)
    
    def add_variable(self, variable: LifeVariable) -> None:
        """Add a variable to the domain model"""
        self.variables[variable.name] = variable
    
    def simulate_step(self) -> Dict[str, float]:
        """Simulate one time step"""
        changes = {}
        
        # Calculate changes for each variable
        for name, var in self.variables.items():
            change = var.growth_rate
            
            # Add influence from dependencies
            for dep_name in var.depends_on:
                if dep_name in self.variables:
                    dep_var = self.variables[dep_name]
                    # Simple influence: dependent variable's value affects this one
                    influence = (dep_var.current_value - dep_var.min_value) / (dep_var.max_value - dep_var.min_value + 0.001)
                    change += influence * 0.1
            
            # Add noise
            change += random.gauss(0, var.volatility)
            
            # Apply change
            new_value = var.current_value + change
            new_value = max(var.min_value, min(var.max_value, new_value))
            
            changes[name] = new_value
            var.current_value = new_value
            var.add_history(datetime.now(), new_value)
        
        return changes


class DigitalTwinModel:
    """
    The Personal Digital Twin - a computational model of the user's life system.
    
    Contains:
    - Domain models (Finance, Health, Career, etc.)
    - State variables
    - Projection capabilities
    - Scenario simulation
    """
    
    def __init__(self):
        self.state = TwinState.INITIALIZING
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
        # Domain models
        self.domain_models: Dict[Domain, DomainModel] = {}
        
        # Initialize default domain models
        self._initialize_domain_models()
        
        self.state = TwinState.ACTIVE
    
    def _initialize_domain_models(self) -> None:
        """Initialize default domain models with common variables"""
        
        # Finance Domain
        finance = DomainModel(
            domain=Domain.FINANCE,
            parameters={"currency": "USD"}
        )
        finance.add_variable(LifeVariable(
            name="income",
            domain=Domain.FINANCE,
            current_value=5000,
            min_value=0,
            max_value=100000,
            growth_rate=50,
            volatility=0.05
        ))
        finance.add_variable(LifeVariable(
            name="savings",
            domain=Domain.FINANCE,
            current_value=10000,
            min_value=0,
            max_value=1000000,
            growth_rate=500,
            volatility=0.1,
            depends_on=["income", "expenses"]
        ))
        finance.add_variable(LifeVariable(
            name="debt",
            domain=Domain.FINANCE,
            current_value=5000,
            min_value=0,
            max_value=500000,
            growth_rate=-200,
            volatility=0.02
        ))
        finance.add_variable(LifeVariable(
            name="expenses",
            domain=Domain.FINANCE,
            current_value=3000,
            min_value=0,
            max_value=50000,
            growth_rate=0,
            volatility=0.1
        ))
        self.domain_models[Domain.FINANCE] = finance
        
        # Health Domain
        health = DomainModel(
            domain=Domain.HEALTH,
            parameters={"units": "hours"}
        )
        health.add_variable(LifeVariable(
            name="sleep_hours",
            domain=Domain.HEALTH,
            current_value=7.5,
            min_value=0,
            max_value=12,
            growth_rate=0,
            volatility=0.2
        ))
        health.add_variable(LifeVariable(
            name="energy_level",
            domain=Domain.HEALTH,
            current_value=70,
            min_value=0,
            max_value=100,
            growth_rate=0,
            volatility=0.1,
            depends_on=["sleep_hours"]
        ))
        health.add_variable(LifeVariable(
            name="fitness_level",
            domain=Domain.HEALTH,
            current_value=50,
            min_value=0,
            max_value=100,
            growth_rate=1,
            volatility=0.05
        ))
        self.domain_models[Domain.HEALTH] = health
        
        # Career Domain
        career = DomainModel(
            domain=Domain.CAREER,
            parameters={}
        )
        career.add_variable(LifeVariable(
            name="skill_level",
            domain=Domain.CAREER,
            current_value=60,
            min_value=0,
            max_value=100,
            growth_rate=2,
            volatility=0.05
        ))
        career.add_variable(LifeVariable(
            name="job_satisfaction",
            domain=Domain.CAREER,
            current_value=65,
            min_value=0,
            max_value=100,
            growth_rate=0,
            volatility=0.1,
            depends_on=["work_hours", "energy_level"]
        ))
        career.add_variable(LifeVariable(
            name="work_hours",
            domain=Domain.CAREER,
            current_value=40,
            min_value=0,
            max_value=80,
            growth_rate=0,
            volatility=0.1
        ))
        self.domain_models[Domain.CAREER] = career
        
        # Life Architecture Domain
        life_arch = DomainModel(
            domain=Domain.LIFE_ARCHITECTURE,
            parameters={}
        )
        life_arch.add_variable(LifeVariable(
            name="lifestyle_satisfaction",
            domain=Domain.LIFE_ARCHITECTURE,
            current_value=60,
            min_value=0,
            max_value=100,
            growth_rate=0,
            volatility=0.1,
            depends_on=["financial_freedom", "time_flexibility"]
        ))
        life_arch.add_variable(LifeVariable(
            name="time_flexibility",
            domain=Domain.LIFE_ARCHITECTURE,
            current_value=40,
            min_value=0,
            max_value=100,
            growth_rate=0,
            volatility=0.1
        ))
        life_arch.add_variable(LifeVariable(
            name="financial_freedom",
            domain=Domain.LIFE_ARCHITECTURE,
            current_value=30,
            min_value=0,
            max_value=100,
            growth_rate=2,
            volatility=0.1,
            depends_on=["savings", "income", "expenses"]
        ))
        self.domain_models[Domain.LIFE_ARCHITECTURE] = life_arch
    
    def update_variable(
        self,
        domain: Domain,
        variable_name: str,
        value: float
    ) -> bool:
        """Update a variable value"""
        if domain not in self.domain_models:
            return False
        
        model = self.domain_models[domain]
        if variable_name not in model.variables:
            return False
        
        var = model.variables[variable_name]
        var.current_value = max(var.min_value, min(var.max_value, value))
        var.add_history(datetime.now(), var.current_value)
        
        self.last_updated = datetime.now()
        return True
    
    def get_variable(self, domain: Domain, variable_name: str) -> Optional[LifeVariable]:
        """Get a variable value"""
        if domain not in self.domain_models:
            return None
        return self.domain_models[domain].variables.get(variable_name)
    
    def get_current_state(self) -> Dict:
        """Get current state of all variables"""
        state = {}
        
        for domain, model in self.domain_models.items():
            state[domain.value] = {
                name: {
                    "current": var.current_value,
                    "min": var.min_value,
                    "max": var.max_value,
                    "growth_rate": var.growth_rate
                }
                for name, var in model.variables.items()
            }
        
        return state
    
    def project(
        self,
        time_horizon_days: int,
        time_step_days: int = 1
    ) -> Dict:
        """
        Project future state.
        
        Args:
            time_horizon_days: How far to project
            time_step_days: Size of each time step
            
        Returns:
            Projected values for each domain
        """
        self.state = TwinState.SIMULATING
        
        projections = {}
        
        # Number of steps
        steps = time_horizon_days // time_step_days
        
        # Project each domain
        for domain, model in self.domain_models.items():
            domain_projections = {}
            
            for name, var in model.variables.items():
                projected_values = var.project(steps)
                
                # Create time labels
                timestamps = [
                    datetime.now() + timedelta(days=i * time_step_days)
                    for i in range(len(projected_values))
                ]
                
                domain_projections[name] = {
                    "values": projected_values,
                    "timestamps": [ts.isoformat() for ts in timestamps]
                }
            
            projections[domain.value] = domain_projections
        
        self.state = TwinState.ACTIVE
        
        return projections
    
    def simulate_scenario(
        self,
        scenario_name: str,
        changes: Dict[str, Dict[str, float]],
        time_horizon_days: int = 90
    ) -> Dict:
        """
        Simulate a scenario with specific changes.
        
        Args:
            scenario_name: Name of the scenario
            changes: Dict of {domain: {variable: new_value}} or {variable: delta}
            time_horizon_days: How long to simulate
            
        Returns:
            Scenario results
        """
        # Save current state
        original_state = self.get_current_state()
        
        # Apply changes
        for domain_str, domain_changes in changes.items():
            try:
                domain = Domain(domain_str)
            except ValueError:
                continue
            
            if domain not in self.domain_models:
                continue
            
            model = self.domain_models[domain]
            
            for var_name, change in domain_changes.items():
                if var_name in model.variables:
                    var = model.variables[var_name]
                    
                    # Check if it's an absolute value or delta
                    if isinstance(change, dict) and "value" in change:
                        var.current_value = max(var.min_value, min(var.max_value, change["value"]))
                    else:
                        # It's a delta or absolute value
                        var.current_value = max(var.min_value, min(var.max_value, var.current_value + change))
        
        # Run projection
        results = self.project(time_horizon_days)
        
        # Restore original state
        self._restore_state(original_state)
        
        return {
            "scenario": scenario_name,
            "changes_applied": changes,
            "projections": results,
            "time_horizon_days": time_horizon_days
        }
    
    def _restore_state(self, state: Dict) -> None:
        """Restore state from dict"""
        for domain_str, domain_state in state.items():
            try:
                domain = Domain(domain_str)
            except ValueError:
                continue
            
            if domain not in self.domain_models:
                continue
            
            model = self.domain_models[domain]
            
            for var_name, var_data in domain_state.items():
                if var_name in model.variables:
                    model.variables[var_name].current_value = var_data["current"]
    
    def get_twin_summary(self) -> Dict:
        """Get summary of the digital twin"""
        return {
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "domains": list(self.domain_models.keys()),
            "total_variables": sum(
                len(m.variables) for m in self.domain_models.values()
            )
        }


# Global instance
_digital_twin: Optional[DigitalTwinModel] = None


def get_digital_twin() -> DigitalTwinModel:
    """Get the global digital twin"""
    global _digital_twin
    if _digital_twin is None:
        _digital_twin = DigitalTwinModel()
    return _digital_twin


__all__ = [
    "DigitalTwinModel",
    "LifeVariable",
    "DomainModel",
    "TwinState",
    "get_digital_twin",
]
