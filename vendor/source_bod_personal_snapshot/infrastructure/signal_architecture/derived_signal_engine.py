"""
Derived Signal Engine - BB-DOM-002: Domain Signal Architecture

The Derived Signal Engine combines raw signals to produce intelligence-ready features.

Phase 3: Derived Signal Engine, Governor Escalation, Memory Integration
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

from .signal_schema import Signal, SignalClass, SignalPriority, SignalDomain, SignalFactory
from .global_signal_bus import GlobalSignalBus


@dataclass
class DerivedSignalRule:
    """A rule for generating derived signals"""
    rule_id: str
    name: str
    description: str
    input_signal_types: List[str]
    compute_fn: Callable[[List[Signal]], float]
    output_signal_type: str
    output_unit: str
    confidence_fn: Callable[[List[Signal]], float] = None


class DerivedSignalEngine:
    """
    Derived Signal Generation Engine (BB-DOM-002 Section 15)
    
    Its job is to:
    - combine raw signals
    - detect patterns
    - compute scores
    - identify trend shifts
    - produce intelligence-ready features
    
    Derived signals re-enter the Global Signal Bus after validation.
    """
    
    def __init__(self, signal_bus: GlobalSignalBus, signal_factory: SignalFactory):
        self.signal_bus = signal_bus
        self.signal_factory = signal_factory
        self.rules: List[DerivedSignalRule] = []
        self.generated_signals: List[Signal] = []
        
        # Register default rules
        self._register_default_rules()
    
    def _register_default_rules(self):
        """Register default derived signal rules"""
        
        # ========== FINANCE DERIVED SIGNALS ==========
        
        # Financial Stress Score (BB-DOM-002 Section 11.1)
        self.add_rule(DerivedSignalRule(
            rule_id="financial_stress",
            name="Financial Stress Score",
            description="Combined measure of financial pressure",
            input_signal_types=["cash_flow", "debt_ratio", "liquidity_level", "spending"],
            compute_fn=lambda signals: self._compute_financial_stress(signals),
            output_signal_type="financial_stress_score",
            output_unit="score"
        ))
        
        # Portfolio Concentration Risk
        self.add_rule(DerivedSignalRule(
            rule_id="concentration_risk",
            name="Portfolio Concentration Risk",
            description="Risk from lack of diversification",
            input_signal_types=["portfolio_allocation"],
            compute_fn=lambda signals: self._compute_concentration_risk(signals),
            output_signal_type="concentration_risk",
            output_unit="percentage"
        ))
        
        # ========== HEALTH DERIVED SIGNALS ==========
        
        # Burnout Probability (BB-DOM-002 Section 11.2)
        self.add_rule(DerivedSignalRule(
            rule_id="burnout_probability",
            name="Burnout Probability",
            description="Risk of burnout from combined factors",
            input_signal_types=["sleep_duration", "hours_worked", "stress_log", "recovery_score"],
            compute_fn=lambda signals: self._compute_burnout_probability(signals),
            output_signal_type="burnout_probability",
            output_unit="percentage",
            confidence_fn=lambda s: 0.7
        ))
        
        # Recovery Deficit
        self.add_rule(DerivedSignalRule(
            rule_id="recovery_deficit",
            name="Recovery Deficit",
            description="Gap between needed and actual recovery",
            input_signal_types=["sleep_duration", "recovery_score", "fatigue_score"],
            compute_fn=lambda signals: self._compute_recovery_deficit(signals),
            output_signal_type="recovery_deficit",
            output_unit="hours"
        ))
        
        # ========== CAREER DERIVED SIGNALS ==========
        
        # Career Leverage Score
        self.add_rule(DerivedSignalRule(
            rule_id="career_leverage",
            name="Career Leverage Score",
            description="Overall career bargaining position",
            input_signal_types=["skill_gap_index", "performance_trend", "opportunity_pipeline", "income_growth_rate"],
            compute_fn=lambda signals: self._compute_career_leverage(signals),
            output_signal_type="career_leverage_score",
            output_unit="score"
        ))
        
        # ========== RELATIONSHIPS DERIVED SIGNALS ==========
        
        # Relationship Strain Index (BB-DOM-002 Section 11.4)
        self.add_rule(DerivedSignalRule(
            rule_id="relationship_strain",
            name="Relationship Strain Index",
            description="Overall relationship pressure measure",
            input_signal_types=["partner_time", "conflict_frequency", "communication_frequency"],
            compute_fn=lambda signals: self._compute_relationship_strain(signals),
            output_signal_type="relationship_strain_index",
            output_unit="score"
        ))
        
        # ========== LIFE ARCHITECTURE DERIVED SIGNALS ==========
        
        # Life Balance Risk
        self.add_rule(DerivedSignalRule(
            rule_id="life_balance_risk",
            name="Life Balance Risk",
            description="Risk of life imbalance",
            input_signal_types=["calendar_density", "work_hours", "social_time", "restoration_time"],
            compute_fn=lambda signals: self._compute_life_balance_risk(signals),
            output_signal_type="life_balance_risk",
            output_unit="score"
        ))
    
    def add_rule(self, rule: DerivedSignalRule):
        """Add a derived signal rule"""
        self.rules.append(rule)
    
    def evaluate_rules(self, signals: List[Signal]) -> List[Signal]:
        """Evaluate all rules against current signals"""
        generated = []
        
        for rule in self.rules:
            # Get relevant input signals
            inputs = self._get_input_signals(signals, rule.input_signal_types)
            
            if len(inputs) >= len(rule.input_signal_types) * 0.5:  # At least 50% of inputs
                try:
                    # Compute derived value
                    value = rule.compute_fn(inputs)
                    
                    # Compute confidence
                    confidence = 0.5
                    if rule.confidence_fn:
                        confidence = rule.confidence_fn(inputs)
                    else:
                        confidence = min(0.9, 0.3 + (len(inputs) / len(rule.input_signal_types)) * 0.5)
                    
                    # Determine priority
                    priority = SignalPriority.MEDIUM
                    if value > 0.7:
                        priority = SignalPriority.HIGH
                    if value > 0.9:
                        priority = SignalPriority.CRITICAL
                    
                    # Create derived signal
                    derived = self.signal_factory.create_derived_signal(
                        signal_type=rule.output_signal_type,
                        source_signals=inputs,
                        computed_value=value,
                        unit=rule.output_unit,
                        confidence=confidence,
                        priority=priority,
                        tags=["derived", rule.name.lower().replace(" ", "_")]
                    )
                    
                    generated.append(derived)
                    self.generated_signals.append(derived)
                    
                except Exception as e:
                    # Log but continue
                    pass
        
        return generated
    
    def _get_input_signals(self, signals: List[Signal], types: List[str]) -> List[Signal]:
        """Get signals matching required types"""
        return [s for s in signals if s.signal_type in types]
    
    # ========== COMPUTATION FUNCTIONS ==========
    
    def _compute_financial_stress(self, signals: List[Signal]) -> float:
        """Compute financial stress from multiple signals"""
        score = 0.0
        weights = {"cash_flow": 0.3, "debt_ratio": 0.3, "liquidity_level": 0.2, "spending": 0.2}
        
        for sig in signals:
            w = weights.get(sig.signal_type, 0.1)
            if sig.normalized_value is not None:
                score += (1 - sig.normalized_value) * w
            elif isinstance(sig.value, (int, float)):
                score += (sig.value / 100) * w
        
        return min(1.0, max(0.0, score))
    
    def _compute_concentration_risk(self, signals: List[Signal]) -> float:
        """Compute portfolio concentration risk"""
        if not signals:
            return 0.5
        
        # Simplified: assume signals contain allocation data
        max_allocation = 0.0
        for sig in signals:
            if isinstance(sig.value, dict):
                for allocation in sig.value.values():
                    if isinstance(allocation, (int, float)) and allocation > max_allocation:
                        max_allocation = allocation
        
        return min(1.0, max_allocation)
    
    def _compute_burnout_probability(self, signals: List[Signal]) -> float:
        """Compute burnout probability from health signals"""
        score = 0.0
        
        for sig in signals:
            if sig.signal_type == "sleep_duration":
                # Less sleep = higher burnout
                if sig.value < 6:
                    score += 0.4
                elif sig.value < 7:
                    score += 0.2
            elif sig.signal_type == "hours_worked":
                # More hours = higher burnout
                if sig.value > 50:
                    score += 0.4
                elif sig.value > 40:
                    score += 0.2
            elif sig.signal_type == "stress_log":
                score += (sig.normalized_value or sig.value / 10) * 0.3
        
        return min(1.0, max(0.0, score))
    
    def _compute_recovery_deficit(self, signals: List[Signal]) -> float:
        """Compute recovery deficit in hours"""
        needed = 8.0  # Base needed sleep
        actual = 0.0
        
        for sig in signals:
            if sig.signal_type == "sleep_duration":
                actual = sig.value
        
        return max(0.0, needed - actual)
    
    def _compute_career_leverage(self, signals: List[Signal]) -> float:
        """Compute career leverage score"""
        score = 0.0
        
        for sig in signals:
            if sig.normalized_value is not None:
                score += sig.normalized_value * 0.25
            elif isinstance(sig.value, (int, float)):
                score += (sig.value / 10) * 0.25
        
        return min(1.0, max(0.0, score))
    
    def _compute_relationship_strain(self, signals: List[Signal]) -> float:
        """Compute relationship strain index"""
        score = 0.0
        
        for sig in signals:
            if sig.signal_type == "partner_time":
                # Less time = more strain
                if sig.value < 2:  # hours per week
                    score += 0.4
                elif sig.value < 5:
                    score += 0.2
            elif sig.signal_type == "conflict_frequency":
                score += (sig.normalized_value or sig.value / 10) * 0.4
            elif sig.signal_type == "communication_frequency":
                score += (1 - (sig.normalized_value or 0.5)) * 0.2
        
        return min(1.0, max(0.0, score))
    
    def _compute_life_balance_risk(self, signals: List[Signal]) -> float:
        """Compute life balance risk"""
        score = 0.0
        
        for sig in signals:
            if sig.signal_type == "calendar_density":
                score += (sig.normalized_value or sig.value / 100) * 0.4
            elif sig.signal_type == "work_hours":
                if sig.value > 50:
                    score += 0.4
                elif sig.value > 40:
                    score += 0.2
            elif sig.signal_type == "restoration_time":
                score += (1 - (sig.normalized_value or 0.5)) * 0.2
        
        return min(1.0, max(0.0, score))


__all__ = [
    "DerivedSignalEngine",
    "DerivedSignalRule",
]
