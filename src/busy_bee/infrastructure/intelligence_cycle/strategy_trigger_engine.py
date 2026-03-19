"""
Strategy Trigger Engine

Monitors signals and triggers strategy generation when significant changes occur.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of strategy triggers"""
    SIGNAL_CHANGE = "signal_change"
    THRESHOLD_BREACH = "threshold_breach"
    SCHEDULE = "schedule"
    MANUAL = "manual"


class TriggerSeverity(Enum):
    """Severity of trigger"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class StrategyTrigger:
    """A trigger for strategy generation"""
    trigger_id: str
    trigger_type: TriggerType
    name: str
    description: str
    
    # Conditions
    domain: Optional[str] = None
    metric_pattern: Optional[str] = None
    threshold: Optional[float] = None
    comparison: str = ">"  # >, <, >=, <=, ==, !=
    
    # Configuration
    severity: TriggerSeverity = TriggerSeverity.MEDIUM
    enabled: bool = True
    cooldown_minutes: int = 60
    
    # Tracking
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def should_fire(self, current_value: float, previous_value: float) -> bool:
        """Check if trigger should fire"""
        if not self.enabled:
            return False
        
        # Check cooldown
        if self.last_triggered:
            elapsed = (datetime.now() - self.last_triggered).total_seconds() / 60
            if elapsed < self.cooldown_minutes:
                return False
        
        # Check threshold comparison
        if self.threshold is None:
            return False
        
        if self.comparison == ">":
            return current_value > self.threshold
        elif self.comparison == "<":
            return current_value < self.threshold
        elif self.comparison == ">=":
            return current_value >= self.threshold
        elif self.comparison == "<=":
            return current_value <= self.threshold
        elif self.comparison == "==":
            return current_value == self.threshold
        elif self.comparison == "!=":
            return current_value != self.threshold
        
        return False


@dataclass
class TriggerResult:
    """Result of trigger evaluation"""
    trigger_id: str
    trigger_type: TriggerType
    timestamp: datetime
    fired: bool
    
    metric_name: Optional[str] = None
    current_value: Optional[float] = None
    previous_value: Optional[float] = None
    threshold: Optional[float] = None
    
    message: str = ""
    severity: TriggerSeverity = TriggerSeverity.MEDIUM


class StrategyTriggerEngine:
    """
    Engine for triggering strategy generation based on signal changes.
    
    Monitors:
    - Signal value changes
    - Threshold breaches
    - Scheduled triggers
    
    When triggered:
    - Calls strategy generation
    - Runs tournament
    - Escalates to council if needed
    """
    
    def __init__(self):
        self._triggers: Dict[str, StrategyTrigger] = {}
        self._callbacks: List[Callable] = []
        self._last_values: Dict[str, float] = {}
        
        # Setup default triggers
        self._setup_default_triggers()
    
    def _setup_default_triggers(self) -> None:
        """Setup default strategy triggers"""
        # High debt increase
        self.add_trigger(StrategyTrigger(
            trigger_id="debt_increase",
            trigger_type=TriggerType.THRESHOLD_BREACH,
            name="Debt Increase Alert",
            description="Triggered when debt increases significantly",
            domain="finance",
            metric_pattern="debt",
            threshold=1000,
            comparison=">",
            severity=TriggerSeverity.HIGH
        ))
        
        # Low sleep
        self.add_trigger(StrategyTrigger(
            trigger_id="sleep_deficit",
            trigger_type=TriggerType.THRESHOLD_BREACH,
            name="Sleep Deficit Alert",
            description="Triggered when sleep drops below threshold",
            domain="health",
            metric_pattern="sleep",
            threshold=6,
            comparison="<",
            severity=TriggerSeverity.MEDIUM
        ))
        
        # Large market movement
        self.add_trigger(StrategyTrigger(
            trigger_id="market_move",
            trigger_type=TriggerType.THRESHOLD_BREACH,
            name="Market Movement Alert",
            description="Triggered on significant market changes",
            domain="finance",
            metric_pattern="market",
            threshold=5,
            comparison=">",
            severity=TriggerSeverity.HIGH
        ))
        
        # New opportunity
        self.add_trigger(StrategyTrigger(
            trigger_id="new_opportunity",
            trigger_type=TriggerType.SIGNAL_CHANGE,
            name="New Opportunity",
            description="Triggered on new opportunity signal",
            domain="career",
            metric_pattern="opportunity",
            severity=TriggerSeverity.MEDIUM
        ))
    
    def add_trigger(self, trigger: StrategyTrigger) -> None:
        """Add a strategy trigger"""
        self._triggers[trigger.trigger_id] = trigger
        logger.info(f"Added trigger: {trigger.name}")
    
    def remove_trigger(self, trigger_id: str) -> bool:
        """Remove a trigger"""
        if trigger_id in self._triggers:
            del self._triggers[trigger_id]
            return True
        return False
    
    def get_trigger(self, trigger_id: str) -> Optional[StrategyTrigger]:
        """Get a trigger"""
        return self._triggers.get(trigger_id)
    
    def register_callback(self, callback: Callable) -> None:
        """Register callback to be called when triggers fire"""
        self._callbacks.append(callback)
    
    def evaluate_signals(self, signals: List[Dict]) -> List[TriggerResult]:
        """Evaluate all triggers against current signals"""
        results = []
        
        for trigger in self._triggers.values():
            result = self._evaluate_trigger(trigger, signals)
            results.append(result)
            
            if result.fired:
                self._fire_trigger(trigger, result)
        
        return results
    
    def _evaluate_trigger(
        self,
        trigger: StrategyTrigger,
        signals: List[Dict]
    ) -> TriggerResult:
        """Evaluate a single trigger"""
        # Filter signals by domain and pattern
        matching_signals = [
            s for s in signals
            if (not trigger.domain or s.get("domain") == trigger.domain)
            and (not trigger.metric_pattern or trigger.metric_pattern in s.get("metric_name", ""))
        ]
        
        if not matching_signals:
            return TriggerResult(
                trigger_id=trigger.trigger_id,
                trigger_type=trigger.trigger_type,
                timestamp=datetime.now(),
                fired=False,
                message="No matching signals"
            )
        
        # Get current and previous values
        signal = matching_signals[0]
        current_value = float(signal.get("metric_value", 0))
        
        key = f"{trigger.domain or ''}:{trigger.metric_pattern or ''}"
        previous_value = self._last_values.get(key, current_value)
        
        # Check if should fire
        fired = False
        if trigger.trigger_type in [TriggerType.THRESHOLD_BREACH, TriggerType.SIGNAL_CHANGE]:
            if trigger.threshold is not None:
                fired = trigger.should_fire(current_value, previous_value)
            else:
                # Just changed
                fired = current_value != previous_value
        
        # Update last value
        self._last_values[key] = current_value
        
        return TriggerResult(
            trigger_id=trigger.trigger_id,
            trigger_type=trigger.trigger_type,
            timestamp=datetime.now(),
            fired=fired,
            metric_name=signal.get("metric_name"),
            current_value=current_value,
            previous_value=previous_value,
            threshold=trigger.threshold,
            message=f"Value: {current_value}, Previous: {previous_value}",
            severity=trigger.severity
        )
    
    def _fire_trigger(self, trigger: StrategyTrigger, result: TriggerResult) -> None:
        """Fire a trigger"""
        trigger.last_triggered = datetime.now()
        trigger.trigger_count += 1
        
        logger.info(f"Trigger fired: {trigger.name} - {result.message}")
        
        # Call registered callbacks
        for callback in self._callbacks:
            try:
                callback(trigger, result)
            except Exception as e:
                logger.error(f"Trigger callback error: {e}")
    
    def manual_trigger(self, trigger_id: str) -> Optional[TriggerResult]:
        """Manually trigger a specific trigger"""
        trigger = self._triggers.get(trigger_id)
        if not trigger:
            return None
        
        # Fire with current values
        result = TriggerResult(
            trigger_id=trigger.trigger_id,
            trigger_type=TriggerType.MANUAL,
            timestamp=datetime.now(),
            fired=True,
            message="Manually triggered",
            severity=trigger.severity
        )
        
        self._fire_trigger(trigger, result)
        return result
    
    def get_trigger_status(self) -> Dict:
        """Get status of all triggers"""
        return {
            "total_triggers": len(self._triggers),
            "enabled_triggers": sum(1 for t in self._triggers.values() if t.enabled),
            "triggers": [
                {
                    "id": t.trigger_id,
                    "name": t.name,
                    "type": t.trigger_type.value,
                    "enabled": t.enabled,
                    "severity": t.severity.value,
                    "last_triggered": t.last_triggered.isoformat() if t.last_triggered else None,
                    "trigger_count": t.trigger_count
                }
                for t in self._triggers.values()
            ]
        }


# Global instance
_trigger_engine: Optional[StrategyTriggerEngine] = None


def get_strategy_trigger_engine() -> StrategyTriggerEngine:
    """Get the global strategy trigger engine"""
    global _trigger_engine
    if _trigger_engine is None:
        _trigger_engine = StrategyTriggerEngine()
    return _trigger_engine


__all__ = [
    "StrategyTriggerEngine",
    "StrategyTrigger",
    "TriggerResult",
    "TriggerType",
    "TriggerSeverity",
    "get_strategy_trigger_engine",
]
