"""
Council Trigger Engine

Triggers Executive Council review based on strategy outputs and critical events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class CouncilTriggerType(Enum):
    """Types of council triggers"""
    STRATEGY_COMPLETE = "strategy_complete"
    HIGH_PRIORITY_SIGNAL = "high_priority_signal"
    RISK_ALERT = "risk_alert"
    SCHEDULED_REVIEW = "scheduled_review"
    DOMAIN_CRISIS = "domain_crisis"
    MANUAL = "manual"


class CouncilAction(Enum):
    """Actions the council can take"""
    REVIEW_STRATEGIES = "review_strategies"
    EMERGENCY_SESSION = "emergency_session"
    PRIORITY_ROUTING = "priority_routing"
    RISK_ASSESSMENT = "risk_assessment"
    STRATEGIC_REVIEW = "strategic_review"


@dataclass
class CouncilTrigger:
    """A trigger for council activation"""
    trigger_id: str
    trigger_type: CouncilTriggerType
    name: str
    description: str
    
    # Configuration
    priority: int = 5  # 1-10
    enabled: bool = True
    requires_quorum: bool = True
    
    # Domains to involve
    target_domains: List[str] = field(default_factory=list)
    
    # Action
    action: CouncilAction = CouncilAction.REVIEW_STRATEGIES
    
    # Tracking
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class CouncilTriggerResult:
    """Result of council trigger"""
    trigger_id: str
    timestamp: datetime
    triggered: bool
    
    action: CouncilAction
    actioned: bool = False
    
    message: str = ""
    domains_involved: List[str] = field(default_factory=list)


class CouncilTriggerEngine:
    """
    Engine for triggering Executive Council review.
    
    Monitors:
    - Strategy completion
    - High priority signals
    - Risk alerts
    - Domain crises
    
    When triggered:
    - Activates executive council
    - Routes to appropriate domains
    - Schedules review sessions
    """
    
    def __init__(self):
        self._triggers: Dict[str, CouncilTrigger] = {}
        self._callbacks: List[Callable] = []
        
        # Setup default triggers
        self._setup_default_triggers()
    
    def _setup_default_triggers(self) -> None:
        """Setup default council triggers"""
        # Strategy tournament complete
        self.add_trigger(CouncilTrigger(
            trigger_id="strategy_complete",
            trigger_type=CouncilTriggerType.STRATEGY_COMPLETE,
            name="Strategy Tournament Complete",
            description="Triggered when strategy tournament selects winners",
            priority=7,
            action=CouncilAction.REVIEW_STRATEGIES,
            target_domains=["finance", "health", "career"]
        ))
        
        # High priority signal
        self.add_trigger(CouncilTrigger(
            trigger_id="high_priority_signal",
            trigger_type=CouncilTriggerType.HIGH_PRIORITY_SIGNAL,
            name="High Priority Signal",
            description="Triggered on high priority signal detection",
            priority=8,
            action=CouncilAction.PRIORITY_ROUTING,
            requires_quorum=False
        ))
        
        # Risk alert
        self.add_trigger(CouncilTrigger(
            trigger_id="risk_alert",
            trigger_type=CouncilTriggerType.RISK_ALERT,
            name="Risk Alert",
            description="Triggered on significant risk detection",
            priority=9,
            action=CouncilAction.RISK_ASSESSMENT,
            target_domains=["finance", "health", "career"]
        ))
        
        # Domain crisis
        self.add_trigger(CouncilTrigger(
            trigger_id="domain_crisis",
            trigger_type=CouncilTriggerType.DOMAIN_CRISIS,
            name="Domain Crisis",
            description="Triggered on domain-specific crisis",
            priority=10,
            action=CouncilAction.EMERGENCY_SESSION,
            requires_quorum=True
        ))
        
        # Scheduled daily review
        self.add_trigger(CouncilTrigger(
            trigger_id="daily_review",
            trigger_type=CouncilTriggerType.SCHEDULED_REVIEW,
            name="Daily Strategic Review",
            description="Daily council review of strategic status",
            priority=5,
            action=CouncilAction.STRATEGIC_REVIEW,
            target_domains=["finance", "health", "career", "relationships", "intelligence", "life_architecture"]
        ))
    
    def add_trigger(self, trigger: CouncilTrigger) -> None:
        """Add a council trigger"""
        self._triggers[trigger.trigger_id] = trigger
        logger.info(f"Added council trigger: {trigger.name}")
    
    def remove_trigger(self, trigger_id: str) -> bool:
        """Remove a trigger"""
        if trigger_id in self._triggers:
            del self._triggers[trigger_id]
            return True
        return False
    
    def get_trigger(self, trigger_id: str) -> Optional[CouncilTrigger]:
        """Get a trigger"""
        return self._triggers.get(trigger_id)
    
    def register_callback(self, callback: Callable) -> None:
        """Register callback for council triggers"""
        self._callbacks.append(callback)
    
    def evaluate(
        self,
        trigger_type: CouncilTriggerType,
        context: Dict[str, Any] = None
    ) -> CouncilTriggerResult:
        """Evaluate and fire appropriate triggers"""
        context = context or {}
        
        # Find matching triggers
        matching_triggers = [
            t for t in self._triggers.values()
            if t.enabled and t.trigger_type == trigger_type
        ]
        
        if not matching_triggers:
            return CouncilTriggerResult(
                trigger_id="none",
                timestamp=datetime.now(),
                triggered=False,
                action=CouncilAction.REVIEW_STRATEGIES,
                message="No matching triggers"
            )
        
        # Sort by priority
        matching_triggers.sort(key=lambda t: t.priority, reverse=True)
        trigger = matching_triggers[0]
        
        # Fire trigger
        return self._fire_trigger(trigger, context)
    
    def _fire_trigger(
        self,
        trigger: CouncilTrigger,
        context: Dict[str, Any]
    ) -> CouncilTriggerResult:
        """Fire a council trigger"""
        trigger.last_triggered = datetime.now()
        trigger.trigger_count += 1
        
        domains = trigger.target_domains or context.get("domains", [])
        
        logger.info(f"Council trigger fired: {trigger.name}")
        
        result = CouncilTriggerResult(
            trigger_id=trigger.trigger_id,
            timestamp=datetime.now(),
            triggered=True,
            action=trigger.action,
            message=f"Council {trigger.action.value} - {trigger.name}",
            domains_involved=domains
        )
        
        # Call registered callbacks
        for callback in self._callbacks:
            try:
                callback(trigger, result, context)
            except Exception as e:
                logger.error(f"Council trigger callback error: {e}")
        
        return result
    
    def trigger_emergency(
        self,
        domain: str,
        reason: str,
        severity: int = 10
    ) -> CouncilTriggerResult:
        """Trigger emergency council session"""
        # Find crisis trigger
        trigger = self._triggers.get("domain_crisis")
        
        if not trigger:
            return CouncilTriggerResult(
                trigger_id="emergency",
                timestamp=datetime.now(),
                triggered=False,
                action=CouncilAction.EMERGENCY_SESSION,
                message="No crisis trigger configured"
            )
        
        context = {
            "domain": domain,
            "reason": reason,
            "severity": severity
        }
        
        return self._fire_trigger(trigger, context)
    
    def manual_trigger(
        self,
        trigger_id: str,
        context: Dict[str, Any] = None
    ) -> Optional[CouncilTriggerResult]:
        """Manually trigger a specific council trigger"""
        trigger = self._triggers.get(trigger_id)
        if not trigger:
            return None
        
        return self._fire_trigger(trigger, context or {})
    
    def get_trigger_status(self) -> Dict:
        """Get status of all council triggers"""
        return {
            "total_triggers": len(self._triggers),
            "enabled_triggers": sum(1 for t in self._triggers.values() if t.enabled),
            "triggers": [
                {
                    "id": t.trigger_id,
                    "name": t.name,
                    "type": t.trigger_type.value,
                    "priority": t.priority,
                    "enabled": t.enabled,
                    "action": t.action.value,
                    "last_triggered": t.last_triggered.isoformat() if t.last_triggered else None,
                    "trigger_count": t.trigger_count
                }
                for t in self._triggers.values()
            ]
        }


# Global instance
_council_engine: Optional[CouncilTriggerEngine] = None


def get_council_trigger_engine() -> CouncilTriggerEngine:
    """Get the global council trigger engine"""
    global _council_engine
    if _council_engine is None:
        _council_engine = CouncilTriggerEngine()
    return _council_engine


__all__ = [
    "CouncilTriggerEngine",
    "CouncilTrigger",
    "CouncilTriggerResult",
    "CouncilTriggerType",
    "CouncilAction",
    "get_council_trigger_engine",
]
