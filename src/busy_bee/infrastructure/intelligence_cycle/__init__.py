"""
Intelligence Cycle Manager

BB-INF-007: Real Signal Ingestion & Continuous Intelligence Cycle

Orchestrates the complete intelligence cycle:
1. Signal Collection & Refresh
2. Strategy Trigger Evaluation
3. Council Decision Processing
4. Report Generation

This module provides continuous intelligence operation for Busy Bee.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import logging

from .cycle_scheduler import (
    CycleScheduler, CycleSchedule, CycleExecution, CycleFrequency, get_cycle_scheduler
)
from .signal_refresh_engine import SignalRefreshEngine, RefreshResult, get_signal_refresh_engine
from .strategy_trigger_engine import (
    StrategyTriggerEngine, StrategyTrigger, TriggerResult, get_strategy_trigger_engine
)
from .council_trigger_engine import (
    CouncilTriggerEngine, CouncilTrigger, CouncilTriggerResult, get_council_trigger_engine
)
from .reporting_trigger_engine import (
    ReportingTriggerEngine, ReportTrigger, ReportTriggerResult, get_reporting_trigger_engine
)


logger = logging.getLogger(__name__)


@dataclass
class IntelligenceCycleResult:
    """Result of a complete intelligence cycle"""
    timestamp: datetime
    
    # Phase results
    signal_refresh: Optional[RefreshResult] = None
    trigger_results: List[TriggerResult] = field(default_factory=list)
    council_results: List[CouncilTriggerResult] = field(default_factory=list)
    report_results: List[ReportTriggerResult] = field(default_factory=list)
    
    # Summary
    signals_processed: int = 0
    strategies_triggered: int = 0
    council_sessions: int = 0
    reports_generated: int = 0
    
    # Status
    success: bool = True
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0


class IntelligenceCycleManager:
    """
    Main orchestration for the continuous intelligence cycle.
    
    Coordinates:
    - Signal refresh
    - Strategy triggers
    - Council activation
    - Report generation
    
    Operates on configurable schedules.
    """
    
    def __init__(
        self,
        scheduler: Optional[CycleScheduler] = None,
        signal_engine: Optional[SignalRefreshEngine] = None,
        strategy_engine: Optional[StrategyTriggerEngine] = None,
        council_engine: Optional[CouncilTriggerEngine] = None,
        reporting_engine: Optional[ReportingTriggerEngine] = None
    ):
        self.scheduler = scheduler or get_cycle_scheduler()
        self.signal_engine = signal_engine or get_signal_refresh_engine()
        self.strategy_engine = strategy_engine or get_strategy_trigger_engine()
        self.council_engine = council_engine or get_council_trigger_engine()
        self.reporting_engine = reporting_engine or get_reporting_trigger_engine()
        
        # Setup scheduler callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Setup callbacks for scheduled cycles"""
        # Signal refresh
        self.scheduler.register_callback("signal_refresh", self.run_signal_refresh)
        
        # Strategic cycle
        self.scheduler.register_callback("strategic_cycle", self.run_strategic_cycle)
        
        # Weekly review
        self.scheduler.register_callback("weekly_review", self.run_weekly_review)
        
        # Monthly planning
        self.scheduler.register_callback("monthly_planning", self.run_monthly_planning)
    
    def run_full_cycle(self) -> IntelligenceCycleResult:
        """
        Run a complete intelligence cycle.
        
        Pipeline:
        1. Refresh signals
        2. Evaluate strategy triggers
        3. Trigger council if needed
        4. Generate reports
        """
        start_time = datetime.now()
        result = IntelligenceCycleResult(timestamp=start_time)
        
        try:
            # Phase 1: Signal Refresh
            logger.info("Phase 1: Signal Refresh")
            refresh_result = self.signal_engine.refresh_all()
            result.signal_refresh = refresh_result
            result.signals_processed = refresh_result.signals_refreshed
            
            if not refresh_result.success:
                result.errors.extend(refresh_result.errors)
            
            # Phase 2: Strategy Triggers
            logger.info("Phase 2: Strategy Triggers")
            signals = self.signal_engine.ingestion.get_all_signals()
            signal_dicts = [s.to_dict() for s in signals]
            
            trigger_results = self.strategy_engine.evaluate_signals(signal_dicts)
            result.trigger_results = trigger_results
            
            fired_triggers = [t for t in trigger_results if t.fired]
            result.strategies_triggered = len(fired_triggers)
            
            # Phase 3: Council Decision
            logger.info("Phase 3: Council Decision")
            if fired_triggers:
                # Trigger council for high priority items
                high_priority = [
                    t for t in fired_triggers
                    if t.severity.value in ["high", "critical"]
                ]
                
                if high_priority:
                    from .council_trigger_engine import CouncilTriggerType
                    council_result = self.council_engine.evaluate(
                        trigger_type=CouncilTriggerType.STRATEGY_COMPLETE,
                        context={"triggers": fired_triggers}
                    )
                    result.council_results.append(council_result)
                    result.council_sessions = 1
            
            # Phase 4: Report Generation
            logger.info("Phase 4: Report Generation")
            from .reporting_trigger_engine import ReportType
            report_result = self.reporting_engine.generate_report_now(
                report_type=ReportType.EXECUTIVE_BRIEF
            )
            result.report_results.append(report_result)
            result.reports_generated = 1 if report_result.generated else 0
            
            result.success = len(result.errors) == 0
            
        except Exception as e:
            logger.error(f"Intelligence cycle error: {e}")
            result.errors.append(str(e))
            result.success = False
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def run_signal_refresh(self) -> RefreshResult:
        """Run just the signal refresh phase"""
        return self.signal_engine.refresh_all()
    
    def run_strategic_cycle(self) -> IntelligenceCycleResult:
        """Run full strategic cycle"""
        return self.run_full_cycle()
    
    def run_weekly_review(self) -> IntelligenceCycleResult:
        """Run weekly strategic review"""
        result = self.run_full_cycle()
        
        # Additional weekly-specific processing
        logger.info("Running weekly review specific tasks")
        
        return result
    
    def run_monthly_planning(self) -> IntelligenceCycleResult:
        """Run monthly macro planning"""
        result = self.run_full_cycle()
        
        # Additional monthly-specific processing
        logger.info("Running monthly planning specific tasks")
        
        return result
    
    def start_continuous_operation(
        self,
        run_immediately: bool = True
    ) -> None:
        """Start continuous intelligence operation"""
        # Start the cycle scheduler
        self.scheduler.start(check_interval=60)
        
        # Start continuous signal ingestion
        self.signal_engine.ingestion.start_continuous_ingestion(
            interval_seconds=300,  # 5 minutes
            run_immediately=run_immediately
        )
        
        logger.info("Continuous intelligence operation started")
    
    def stop_continuous_operation(self) -> None:
        """Stop continuous intelligence operation"""
        self.scheduler.stop()
        self.signal_engine.ingestion.stop_continuous_ingestion()
        
        logger.info("Continuous intelligence operation stopped")
    
    def get_system_status(self) -> Dict:
        """Get status of entire intelligence system"""
        return {
            "cycle": self.scheduler.get_scheduler_status(),
            "signals": self.signal_engine.get_refresh_status(),
            "triggers": self.strategy_engine.get_trigger_status(),
            "council": self.council_engine.get_trigger_status(),
            "reporting": self.reporting_engine.get_trigger_status()
        }
    
    # Convenience methods for direct access
    
    def add_signal_trigger(
        self,
        trigger_id: str,
        domain: str,
        metric_pattern: str,
        threshold: float,
        comparison: str,
        severity: str = "medium"
    ) -> None:
        """Add a new signal trigger"""
        from .strategy_trigger_engine import TriggerType, TriggerSeverity
        
        trigger = StrategyTrigger(
            trigger_id=trigger_id,
            trigger_type=TriggerType.THRESHOLD_BREACH,
            name=trigger_id.replace("_", " ").title(),
            description=f"Custom trigger for {metric_pattern}",
            domain=domain,
            metric_pattern=metric_pattern,
            threshold=threshold,
            comparison=comparison,
            severity=TriggerSeverity(severity)
        )
        self.strategy_engine.add_trigger(trigger)
    
    def trigger_manual_strategy(self, reason: str, context: Dict = None) -> IntelligenceCycleResult:
        """Manually trigger a strategy evaluation cycle"""
        result = self.run_full_cycle()
        result.errors.append(f"Manual trigger: {reason}")
        return result


# Global instance
_intelligence_cycle: Optional[IntelligenceCycleManager] = None


def get_intelligence_cycle_manager() -> IntelligenceCycleManager:
    """Get the global intelligence cycle manager"""
    global _intelligence_cycle
    if _intelligence_cycle is None:
        _intelligence_cycle = IntelligenceCycleManager()
    return _intelligence_cycle


__all__ = [
    "IntelligenceCycleManager",
    "IntelligenceCycleResult",
    
    # Re-export components
    "CycleScheduler",
    "CycleSchedule", 
    "CycleExecution",
    "CycleFrequency",
    "SignalRefreshEngine",
    "RefreshResult",
    "StrategyTriggerEngine",
    "TriggerResult",
    "CouncilTriggerEngine",
    "CouncilTriggerResult",
    "ReportingTriggerEngine",
    "ReportTriggerResult",
    
    # Helpers
    "get_cycle_scheduler",
    "get_signal_refresh_engine",
    "get_strategy_trigger_engine",
    "get_council_trigger_engine",
    "get_reporting_trigger_engine",
    "get_intelligence_cycle_manager",
]
