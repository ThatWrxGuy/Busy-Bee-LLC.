"""
Reporting Trigger Engine

Triggers executive brief and report generation based on events and schedules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of reports"""
    EXECUTIVE_BRIEF = "executive_brief"
    DOMAIN_REPORT = "domain_report"
    STRATEGY_REPORT = "strategy_report"
    RISK_REPORT = "risk_report"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_REVIEW = "monthly_review"


class ReportTriggerType(Enum):
    """Types of report triggers"""
    SCHEDULE = "schedule"
    EVENT = "event"
    MANUAL = "manual"
    COUNCIL_DECISION = "council_decision"


@dataclass
class ReportTrigger:
    """A trigger for report generation"""
    trigger_id: str
    trigger_type: ReportTriggerType
    report_type: ReportType
    name: str
    description: str
    
    # Configuration
    enabled: bool = True
    priority: int = 5  # 1-10
    
    # Domains to include (empty = all)
    domains: List[str] = field(default_factory=list)
    
    # Scheduling
    schedule_time: Optional[str] = None  # e.g., "06:00" for daily
    
    # Tracking
    last_triggered: Optional[datetime] = None
    last_report_id: Optional[str] = None
    trigger_count: int = 0


@dataclass
class ReportTriggerResult:
    """Result of report trigger"""
    trigger_id: str
    timestamp: datetime
    triggered: bool
    
    report_type: ReportType
    generated: bool = False
    report_id: Optional[str] = None
    
    message: str = ""
    error: Optional[str] = None


class ReportingTriggerEngine:
    """
    Engine for triggering report generation.
    
    Handles:
    - Scheduled report generation
    - Event-triggered reports
    - Council decision reports
    - Manual report requests
    """
    
    def __init__(self):
        self._triggers: Dict[str, ReportTrigger] = {}
        self._callbacks: List[Callable] = []
        self._report_history: List[ReportTriggerResult] = []
        
        # Setup default triggers
        self._setup_default_triggers()
    
    def _setup_default_triggers(self) -> None:
        """Setup default report triggers"""
        # Daily executive brief
        self.add_trigger(ReportTrigger(
            trigger_id="daily_brief",
            trigger_type=ReportTriggerType.SCHEDULE,
            report_type=ReportType.EXECUTIVE_BRIEF,
            name="Daily Executive Brief",
            description="Generate daily executive brief",
            priority=8,
            schedule_time="06:00"
        ))
        
        # Weekly summary
        self.add_trigger(ReportTrigger(
            trigger_id="weekly_summary",
            trigger_type=ReportTriggerType.SCHEDULE,
            report_type=ReportType.WEEKLY_SUMMARY,
            name="Weekly Summary",
            description="Generate weekly strategic summary",
            priority=6,
            schedule_time="09:00"  # Monday 9 AM
        ))
        
        # Monthly review
        self.add_trigger(ReportTrigger(
            trigger_id="monthly_review",
            trigger_type=ReportTriggerType.SCHEDULE,
            report_type=ReportType.MONTHLY_REVIEW,
            name="Monthly Review",
            description="Generate monthly comprehensive review",
            priority=7,
            schedule_time="08:00"  # 1st of month
        ))
        
        # Council decision report
        self.add_trigger(ReportTrigger(
            trigger_id="council_decision",
            trigger_type=ReportTriggerType.COUNCIL_DECISION,
            report_type=ReportType.EXECUTIVE_BRIEF,
            name="Council Decision Report",
            description="Generate report after council decisions",
            priority=9
        ))
    
    def add_trigger(self, trigger: ReportTrigger) -> None:
        """Add a report trigger"""
        self._triggers[trigger.trigger_id] = trigger
        logger.info(f"Added report trigger: {trigger.name}")
    
    def remove_trigger(self, trigger_id: str) -> bool:
        """Remove a trigger"""
        if trigger_id in self._triggers:
            del self._triggers[trigger_id]
            return True
        return False
    
    def get_trigger(self, trigger_id: str) -> Optional[ReportTrigger]:
        """Get a trigger"""
        return self._triggers.get(trigger_id)
    
    def register_callback(self, callback: Callable) -> None:
        """Register callback for report triggers"""
        self._callbacks.append(callback)
    
    def evaluate_schedule_triggers(self) -> List[ReportTriggerResult]:
        """Evaluate all schedule-based triggers"""
        results = []
        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M")
        
        for trigger in self._triggers.values():
            if not trigger.enabled:
                continue
            
            if trigger.trigger_type != ReportTriggerType.SCHEDULE:
                continue
            
            # Check if schedule matches
            should_trigger = False
            
            if trigger.schedule_time == current_time_str:
                should_trigger = True
            
            # Also check if not triggered today
            if trigger.last_triggered:
                last_date = trigger.last_triggered.date()
                if last_date == current_time.date():
                    should_trigger = False
            
            if should_trigger:
                result = self._generate_report(trigger)
                results.append(result)
        
        return results
    
    def trigger_on_event(
        self,
        event_type: str,
        context: Dict[str, Any] = None
    ) -> List[ReportTriggerResult]:
        """Trigger reports based on events"""
        results = []
        context = context or {}
        
        # Find event-based triggers
        event_triggers = [
            t for t in self._triggers.values()
            if t.enabled and t.trigger_type == ReportTriggerType.EVENT
        ]
        
        for trigger in event_triggers:
            result = self._generate_report(trigger, context)
            results.append(result)
        
        return results
    
    def _generate_report(
        self,
        trigger: ReportTrigger,
        context: Dict[str, Any] = None
    ) -> ReportTriggerResult:
        """Generate a report for the trigger"""
        context = context or {}
        
        result = ReportTriggerResult(
            trigger_id=trigger.trigger_id,
            timestamp=datetime.now(),
            triggered=True,
            report_type=trigger.report_type,
            message=f"Generating {trigger.report_type.value}"
        )
        
        try:
            # Call registered callbacks
            for callback in self._callbacks:
                callback_result = callback(trigger, context)
                
                if callback_result:
                    result.generated = True
                    result.report_id = callback_result.get("report_id")
                    result.message = callback_result.get("message", "Report generated")
        
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            result.error = str(e)
            result.message = f"Error: {str(e)}"
        
        # Update trigger state
        trigger.last_triggered = datetime.now()
        trigger.last_report_id = result.report_id
        trigger.trigger_count += 1
        
        # Store in history
        self._report_history.append(result)
        if len(self._report_history) > 100:
            self._report_history = self._report_history[-100:]
        
        return result
    
    def manual_trigger(
        self,
        trigger_id: str,
        context: Dict[str, Any] = None
    ) -> Optional[ReportTriggerResult]:
        """Manually trigger a report"""
        trigger = self._triggers.get(trigger_id)
        if not trigger:
            # Create temporary trigger for manual generation
            return None
        
        return self._generate_report(trigger, context)
    
    def generate_report_now(
        self,
        report_type: ReportType,
        domains: List[str] = None,
        context: Dict[str, Any] = None
    ) -> ReportTriggerResult:
        """Generate a report immediately"""
        context = context or {}
        
        result = ReportTriggerResult(
            trigger_id="manual",
            timestamp=datetime.now(),
            triggered=True,
            report_type=report_type
        )
        
        # Find matching trigger or create one
        trigger = ReportTrigger(
            trigger_id="manual_generation",
            trigger_type=ReportTriggerType.MANUAL,
            report_type=report_type,
            name="Manual Report",
            description="Manual report generation",
            domains=domains or []
        )
        
        result = self._generate_report(trigger, context)
        
        return result
    
    def get_trigger_status(self) -> Dict:
        """Get status of all report triggers"""
        return {
            "total_triggers": len(self._triggers),
            "enabled_triggers": sum(1 for t in self._triggers.values() if t.enabled),
            "triggers": [
                {
                    "id": t.trigger_id,
                    "name": t.name,
                    "type": t.trigger_type.value,
                    "report_type": t.report_type.value,
                    "enabled": t.enabled,
                    "schedule_time": t.schedule_time,
                    "last_triggered": t.last_triggered.isoformat() if t.last_triggered else None,
                    "trigger_count": t.trigger_count
                }
                for t in self._triggers.values()
            ],
            "recent_reports": len(self._report_history)
        }


# Global instance
_reporting_engine: Optional[ReportingTriggerEngine] = None


def get_reporting_trigger_engine() -> ReportingTriggerEngine:
    """Get the global reporting trigger engine"""
    global _reporting_engine
    if _reporting_engine is None:
        _reporting_engine = ReportingTriggerEngine()
    return _reporting_engine


__all__ = [
    "ReportingTriggerEngine",
    "ReportTrigger",
    "ReportTriggerResult",
    "ReportType",
    "ReportTriggerType",
    "get_reporting_trigger_engine",
]
