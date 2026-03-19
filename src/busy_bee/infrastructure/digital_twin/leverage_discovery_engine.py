"""
Leverage Discovery Engine

BB-INF-008: Life Signal Graph & Personal Digital Twin Engine

Identifies high-leverage actions that produce the greatest impact across life domains.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import logging

from ..life_graph.graph_models import Domain
from ..digital_twin.digital_twin_model import DigitalTwinModel, get_digital_twin


logger = logging.getLogger(__name__)


@dataclass
class LeverageOpportunity:
    """A high-leverage strategic opportunity"""
    opportunity_id: str
    name: str
    description: str
    
    # Impact analysis
    primary_domain: Domain
    affected_domains: List[Domain]
    
    # Metrics
    leverage_score: float
    impact_magnitude: float
    confidence: float
    
    # Action
    action_type: str
    action_description: str
    
    def to_dict(self) -> Dict:
        return {
            "opportunity_id": self.opportunity_id,
            "name": self.name,
            "description": self.description,
            "primary_domain": self.primary_domain.value,
            "affected_domains": [d.value for d in self.affected_domains],
            "leverage_score": self.leverage_score,
            "impact_magnitude": self.impact_magnitude,
            "confidence": self.confidence,
            "action_type": self.action_type,
            "action_description": self.action_description
        }


@dataclass
class LeverageResult:
    """Result of leverage discovery"""
    timestamp: datetime
    opportunities: List[LeverageOpportunity]
    analysis: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "opportunities": [o.to_dict() for o in self.opportunities],
            "analysis": self.analysis
        }


class LeverageDiscoveryEngine:
    """
    Discovers high-leverage strategic opportunities across the life system.
    
    A leverage point is where a small action produces disproportionate positive effects.
    
    Examples:
    - Sleep improvement → energy, productivity, mood, relationships
    - Debt reduction → stress reduction, financial freedom, career optionality
    - Skill development → income, confidence, opportunities
    """
    
    # Known leverage patterns
    LEVERAGE_PATTERNS = {
        # Sleep is a massive leverage point
        "sleep_improvement": {
            "name": "Sleep Optimization",
            "description": "Improving sleep has cascading benefits across all domains",
            "primary_domain": Domain.HEALTH,
            "affected_domains": [Domain.HEALTH, Domain.CAREER, Domain.RELATIONSHIPS, Domain.LIFE_ARCHITECTURE],
            "action_type": "health_intervention",
            "base_leverage": 0.9
        },
        
        # Financial foundation enables everything
        "debt_elimination": {
            "name": "Debt Elimination",
            "description": "Eliminating high-interest debt provides massive financial leverage",
            "primary_domain": Domain.FINANCE,
            "affected_domains": [Domain.FINANCE, Domain.LIFE_ARCHITECTURE, Domain.HEALTH],
            "action_type": "financial_optimization",
            "base_leverage": 0.85
        },
        
        # Emergency fund provides security
        "emergency_fund": {
            "name": "Emergency Fund Builder",
            "description": "Building 3-6 month emergency fund provides security and optionality",
            "primary_domain": Domain.FINANCE,
            "affected_domains": [Domain.FINANCE, Domain.CAREER, Domain.LIFE_ARCHITECTURE],
            "action_type": "financial_security",
            "base_leverage": 0.8
        },
        
        # Skill development compounds
        "skill_development": {
            "name": "Skill Development",
            "description": "Developing high-value skills compounds career and income",
            "primary_domain": Domain.CAREER,
            "affected_domains": [Domain.CAREER, Domain.FINANCE, Domain.LIFE_ARCHITECTURE],
            "action_type": "career_investment",
            "base_leverage": 0.75
        },
        
        # Exercise benefits everything
        "fitness_improvement": {
            "name": "Fitness Routine",
            "description": "Regular exercise improves health, energy, and mental clarity",
            "primary_domain": Domain.HEALTH,
            "affected_domains": [Domain.HEALTH, Domain.CAREER, Domain.RELATIONSHIPS],
            "action_type": "health_habit",
            "base_leverage": 0.7
        },
        
        # Time blocking increases productivity
        "time_blocking": {
            "name": "Time Blocking System",
            "description": "Structured time allocation improves all domain productivity",
            "primary_domain": Domain.LIFE_ARCHITECTURE,
            "affected_domains": [Domain.LIFE_ARCHITECTURE, Domain.CAREER, Domain.HEALTH],
            "action_type": "productivity_system",
            "base_leverage": 0.65
        },
        
        # Network building creates opportunities
        "network_building": {
            "name": "Professional Network",
            "description": "Building professional network creates career opportunities",
            "primary_domain": Domain.CAREER,
            "affected_domains": [Domain.CAREER, Domain.FINANCE],
            "action_type": "relationship_investment",
            "base_leverage": 0.6
        },
        
        # Financial investment compounding
        "investment_start": {
            "name": "Start Investing",
            "description": "Starting early with investing harnesses compound growth",
            "primary_domain": Domain.FINANCE,
            "affected_domains": [Domain.FINANCE, Domain.LIFE_ARCHITECTURE],
            "action_type": "wealth_building",
            "base_leverage": 0.7
        }
    }
    
    def __init__(self, digital_twin: DigitalTwinModel = None):
        self.digital_twin = digital_twin or get_digital_twin()
    
    def discover_leverage_opportunities(
        self,
        current_state: Dict = None,
        limit: int = 10
    ) -> LeverageResult:
        """
        Discover high-leverage opportunities.
        
        Args:
            current_state: Current state from digital twin
            limit: Maximum opportunities to return
            
        Returns:
            LeverageResult with opportunities
        """
        opportunities = []
        current_state = current_state or self.digital_twin.get_current_state()
        
        for pattern_key, pattern in self.LEVERAGE_PATTERNS.items():
            # Calculate leverage score based on current state
            leverage_score = self._calculate_leverage_score(
                pattern, current_state
            )
            
            # Skip if leverage is too low
            if leverage_score < 0.3:
                continue
            
            # Calculate impact magnitude
            impact_magnitude = self._calculate_impact_magnitude(
                pattern, current_state
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                pattern, current_state
            )
            
            # Create opportunity
            opportunity = LeverageOpportunity(
                opportunity_id=f"leverage_{pattern_key}",
                name=pattern["name"],
                description=pattern["description"],
                primary_domain=pattern["primary_domain"],
                affected_domains=pattern["affected_domains"],
                leverage_score=leverage_score,
                impact_magnitude=impact_magnitude,
                confidence=confidence,
                action_type=pattern["action_type"],
                action_description=self._generate_action_description(pattern, current_state)
            )
            
            opportunities.append(opportunity)
        
        # Sort by leverage score
        opportunities.sort(key=lambda x: x.leverage_score, reverse=True)
        
        # Limit results
        opportunities = opportunities[:limit]
        
        # Build analysis
        analysis = {
            "total_patterns_evaluated": len(self.LEVERAGE_PATTERNS),
            "opportunities_found": len(opportunities),
            "highest_leverage_domain": opportunities[0].primary_domain.value if opportunities else None,
            "average_leverage_score": sum(o.leverage_score for o in opportunities) / len(opportunities) if opportunities else 0
        }
        
        return LeverageResult(
            timestamp=datetime.now(),
            opportunities=opportunities,
            analysis=analysis
        )
    
    def _calculate_leverage_score(
        self,
        pattern: Dict,
        current_state: Dict
    ) -> float:
        """Calculate leverage score based on current state"""
        base_leverage = pattern.get("base_leverage", 0.5)
        
        # Adjust based on current state needs
        primary_domain = pattern["primary_domain"]
        domain_state = current_state.get(primary_domain.value, {})
        
        # Higher leverage if domain is in poor state
        domain_score = self._evaluate_domain_need(domain_state)
        
        # Adjust base leverage by domain need
        adjusted_leverage = base_leverage * (1 + domain_score) / 2
        
        return min(adjusted_leverage, 1.0)
    
    def _evaluate_domain_need(self, domain_state: Dict) -> float:
        """Evaluate how much a domain needs intervention (0-1)"""
        if not domain_state:
            return 0.5
        
        # Look for common indicators
        needs = []
        
        # Finance needs
        if "debt" in domain_state:
            debt = domain_state["debt"].get("current", 0)
            if debt > 10000:
                needs.append(0.8)
            elif debt > 5000:
                needs.append(0.5)
        
        if "savings" in domain_state:
            savings = domain_state["savings"].get("current", 0)
            if savings < 5000:
                needs.append(0.7)
        
        # Health needs
        if "sleep_hours" in domain_state:
            sleep = domain_state["sleep_hours"].get("current", 8)
            if sleep < 6:
                needs.append(0.9)
            elif sleep < 7:
                needs.append(0.5)
        
        if "energy_level" in domain_state:
            energy = domain_state["energy_level"].get("current", 50)
            if energy < 40:
                needs.append(0.7)
        
        # Career needs
        if "job_satisfaction" in domain_state:
            satisfaction = domain_state["job_satisfaction"].get("current", 50)
            if satisfaction < 40:
                needs.append(0.7)
        
        # Life architecture needs
        if "time_flexibility" in domain_state:
            flexibility = domain_state["time_flexibility"].get("current", 50)
            if flexibility < 30:
                needs.append(0.6)
        
        if not needs:
            return 0.3
        
        return sum(needs) / len(needs)
    
    def _calculate_impact_magnitude(
        self,
        pattern: Dict,
        current_state: Dict
    ) -> float:
        """Calculate potential impact magnitude"""
        # Number of affected domains
        affected_count = len(pattern.get("affected_domains", []))
        
        # Base impact from number of domains
        domain_impact = min(affected_count / 5, 1.0) * 0.5
        
        # Add domain-specific potential
        potential = 0.5
        
        # More potential if domain is below optimal
        primary_domain = pattern["primary_domain"]
        domain_state = current_state.get(primary_domain.value, {})
        
        if domain_state:
            for var_name, var_data in domain_state.items():
                current = var_data.get("current", 50)
                max_val = var_data.get("max", 100)
                min_val = var_data.get("min", 0)
                
                # Room for improvement
                room = (max_val - current) / (max_val - min_val)
                potential = max(potential, room)
        
        return (domain_impact + potential) / 2
    
    def _calculate_confidence(
        self,
        pattern: Dict,
        current_state: Dict
    ) -> float:
        """Calculate confidence in the leverage opportunity"""
        # Base confidence from pattern
        confidence = 0.7
        
        # Higher confidence if we have good data for affected domains
        domains_with_data = 0
        for domain in pattern.get("affected_domains", []):
            if domain.value in current_state:
                domains_with_data += 1
        
        data_coverage = domains_with_data / len(pattern.get("affected_domains", [1]))
        confidence = confidence * 0.5 + data_coverage * 0.5
        
        return confidence
    
    def _generate_action_description(
        self,
        pattern: Dict,
        current_state: Dict
    ) -> str:
        """Generate specific action description"""
        action_type = pattern.get("action_type", "")
        
        primary_domain = pattern["primary_domain"]
        domain_state = current_state.get(primary_domain.value, {})
        
        if action_type == "health_intervention":
            sleep = domain_state.get("sleep_hours", {}).get("current", 7)
            if sleep < 7:
                return f"Increase sleep to 7-8 hours. Current: {sleep} hours."
            return "Maintain and optimize sleep schedule."
        
        elif action_type == "financial_optimization":
            debt = domain_state.get("debt", {}).get("current", 0)
            if debt > 0:
                return f"Focus on debt elimination. Current debt: ${debt:.0f}"
            return "Maintain debt-free status."
        
        elif action_type == "financial_security":
            savings = domain_state.get("savings", {}).get("current", 0)
            return f"Build emergency fund to 3-6 months expenses. Current: ${savings:.0f}"
        
        elif action_type == "career_investment":
            skill = domain_state.get("skill_level", {}).get("current", 50)
            return f"Invest in skill development. Current level: {skill:.0f}/100"
        
        elif action_type == "health_habit":
            fitness = domain_state.get("fitness_level", {}).get("current", 50)
            return f"Establish regular exercise routine. Current fitness: {fitness:.0f}/100"
        
        elif action_type == "productivity_system":
            flexibility = domain_state.get("time_flexibility", {}).get("current", 50)
            return f"Implement time blocking. Current flexibility: {flexibility:.0f}/100"
        
        return f"Implement {pattern['name']} strategy."
    
    def simulate_leverage_impact(
        self,
        opportunity_id: str,
        time_horizon_days: int = 90
    ) -> Dict:
        """
        Simulate the impact of a leverage opportunity.
        
        Returns:
            Simulation results
        """
        # Find the opportunity pattern
        pattern_key = opportunity_id.replace("leverage_", "")
        pattern = self.LEVERAGE_PATTERNS.get(pattern_key)
        
        if not pattern:
            return {"error": "Opportunity not found"}
        
        # Build scenario changes
        changes = {}
        
        # Determine changes based on opportunity type
        if pattern["primary_domain"] == Domain.HEALTH:
            changes["health"] = {"sleep_hours": 1.0}  # Add 1 hour
            changes["health"] = {"energy_level": 15}  # Boost
        
        elif pattern["primary_domain"] == Domain.FINANCE:
            changes["finance"] = {"debt": -1000}  # Reduce debt
        
        elif pattern["primary_domain"] == Domain.CAREER:
            changes["career"] = {"skill_level": 10}  # Increase skills
        
        # Run simulation
        result = self.digital_twin.simulate_scenario(
            scenario_name=pattern["name"],
            changes=changes,
            time_horizon_days=time_horizon_days
        )
        
        return result


# Global instance
_leverage_engine: Optional[LeverageDiscoveryEngine] = None


def get_leverage_discovery_engine() -> LeverageDiscoveryEngine:
    """Get the global leverage discovery engine"""
    global _leverage_engine
    if _leverage_engine is None:
        _leverage_engine = LeverageDiscoveryEngine()
    return _leverage_engine


__all__ = [
    "LeverageDiscoveryEngine",
    "LeverageOpportunity",
    "LeverageResult",
    "get_leverage_discovery_engine",
]
