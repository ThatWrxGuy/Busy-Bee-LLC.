"""
Intelligence Cycle Scheduler

Manages scheduled intelligence cycles for continuous operation.

Supports:
- Hourly: signal refresh
- Daily: strategic intelligence cycle  
- Weekly: strategic review
- Monthly: macro planning
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import threading
import time
import logging


logger = logging.getLogger(__name__)


class CycleFrequency(Enum):
    """Frequency of intelligence cycles"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class CycleStatus(Enum):
    """Status of a cycle"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CycleSchedule:
    """Schedule configuration for a cycle type"""
    frequency: CycleFrequency
    enabled: bool = True
    interval: int = 1  # Number of periods between runs
    hour: int = 0  # Hour of day (for daily/weekly/monthly)
    day_of_week: int = 0  # 0=Monday for weekly
    day_of_month: int = 1  # For monthly
    
    def get_next_run(self, now: datetime) -> datetime:
        """Calculate next run time"""
        if self.frequency == CycleFrequency.HOURLY:
            return now + timedelta(hours=self.interval)
        
        elif self.frequency == CycleFrequency.DAILY:
            next_run = now.replace(hour=self.hour, minute=0, second=0, microsecond=0)
            if now.hour >= self.hour:
                next_run += timedelta(days=self.interval)
            return next_run
        
        elif self.frequency == CycleFrequency.WEEKLY:
            days_until = (self.day_of_week - now.weekday()) % 7
            if days_until == 0 and now.hour >= self.hour:
                days_until = 7
            next_run = now + timedelta(days=days_until)
            next_run = next_run.replace(hour=self.hour, minute=0, second=0, microsecond=0)
            return next_run
        
        elif self.frequency == CycleFrequency.MONTHLY:
            # Simple monthly: same day next month
            try:
                next_run = now.replace(day=self.day_of_month, hour=self.hour, minute=0, second=0, microsecond=0)
                if now.day >= self.day_of_month:
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)
            except ValueError:
                # Handle months with fewer days
                next_run = (now.replace(day=1, hour=self.hour, minute=0, second=0, microsecond=0) 
                           + timedelta(days=32)).replace(day=1)
            return next_run
        
        return now + timedelta(hours=1)


@dataclass
class CycleExecution:
    """Record of a cycle execution"""
    cycle_id: str
    cycle_type: str
    frequency: CycleFrequency
    start_time: datetime
    end_time: Optional[datetime] = None
    status: CycleStatus = CycleStatus.PENDING
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Get execution duration"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class CycleScheduler:
    """
    Scheduler for intelligence cycles.
    
    Manages:
    - Scheduling of different cycle types
    - Execution of cycles at scheduled times
    - History of cycle executions
    """
    
    def __init__(self):
        self._schedules: Dict[str, CycleSchedule] = {}
        self._history: List[CycleExecution] = []
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._callbacks: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        
        # Default schedules
        self._setup_default_schedules()
    
    def _setup_default_schedules(self) -> None:
        """Setup default cycle schedules"""
        # Hourly signal refresh
        self.add_schedule(
            "signal_refresh",
            CycleSchedule(
                frequency=CycleFrequency.HOURLY,
                enabled=True,
                interval=1
            )
        )
        
        # Daily strategic cycle
        self.add_schedule(
            "strategic_cycle",
            CycleSchedule(
                frequency=CycleFrequency.DAILY,
                enabled=True,
                hour=6  # 6 AM
            )
        )
        
        # Weekly strategic review
        self.add_schedule(
            "weekly_review",
            CycleSchedule(
                frequency=CycleFrequency.WEEKLY,
                enabled=True,
                hour=9,
                day_of_week=0  # Monday
            )
        )
        
        # Monthly macro planning
        self.add_schedule(
            "monthly_planning",
            CycleSchedule(
                frequency=CycleFrequency.MONTHLY,
                enabled=True,
                hour=8,
                day_of_month=1
            )
        )
    
    def add_schedule(self, cycle_type: str, schedule: CycleSchedule) -> None:
        """Add or update a cycle schedule"""
        with self._lock:
            self._schedules[cycle_type] = schedule
            logger.info(f"Added schedule: {cycle_type} ({schedule.frequency.value})")
    
    def remove_schedule(self, cycle_type: str) -> bool:
        """Remove a cycle schedule"""
        with self._lock:
            if cycle_type in self._schedules:
                del self._schedules[cycle_type]
                return True
            return False
    
    def get_schedule(self, cycle_type: str) -> Optional[CycleSchedule]:
        """Get a cycle schedule"""
        return self._schedules.get(cycle_type)
    
    def get_all_schedules(self) -> Dict[str, CycleSchedule]:
        """Get all cycle schedules"""
        return dict(self._schedules)
    
    def register_callback(self, cycle_type: str, callback: Callable) -> None:
        """Register callback for a cycle type"""
        self._callbacks[cycle_type] = callback
        logger.info(f"Registered callback for: {cycle_type}")
    
    def get_next_runs(self) -> Dict[str, datetime]:
        """Get next run times for all enabled schedules"""
        now = datetime.now()
        next_runs = {}
        
        with self._lock:
            for cycle_type, schedule in self._schedules.items():
                if schedule.enabled:
                    next_runs[cycle_type] = schedule.get_next_run(now)
        
        return next_runs
    
    def run_cycle(self, cycle_type: str) -> CycleExecution:
        """Manually run a specific cycle"""
        if cycle_type not in self._schedules:
            return CycleExecution(
                cycle_id=f"{cycle_type}_{int(time.time())}",
                cycle_type=cycle_type,
                frequency=CycleFrequency.DAILY,
                start_time=datetime.now(),
                status=CycleStatus.FAILED,
                error="Unknown cycle type"
            )
        
        schedule = self._schedules[cycle_type]
        
        execution = CycleExecution(
            cycle_id=f"{cycle_type}_{int(time.time())}",
            cycle_type=cycle_type,
            frequency=schedule.frequency,
            start_time=datetime.now(),
            status=CycleStatus.RUNNING
        )
        
        try:
            # Execute callback if registered
            if cycle_type in self._callbacks:
                callback = self._callbacks[cycle_type]
                result = callback()
                execution.result = result if isinstance(result, dict) else {"result": result}
            
            execution.status = CycleStatus.COMPLETED
            
        except Exception as e:
            execution.status = CycleStatus.FAILED
            execution.error = str(e)
            logger.error(f"Cycle {cycle_type} failed: {e}")
        
        execution.end_time = datetime.now()
        
        # Store in history
        with self._lock:
            self._history.append(execution)
            # Keep last 100 executions
            if len(self._history) > 100:
                self._history = self._history[-100:]
        
        return execution
    
    def get_history(
        self,
        cycle_type: Optional[str] = None,
        limit: int = 10
    ) -> List[CycleExecution]:
        """Get execution history"""
        with self._lock:
            if cycle_type:
                filtered = [e for e in self._history if e.cycle_type == cycle_type]
            else:
                filtered = self._history
            return filtered[-limit:]
    
    def get_scheduler_status(self) -> Dict:
        """Get scheduler status"""
        now = datetime.now()
        next_runs = self.get_next_runs()
        
        with self._lock:
            return {
                "running": self._running,
                "schedules": {
                    cycle_type: {
                        "frequency": sched.frequency.value,
                        "enabled": sched.enabled,
                        "next_run": next_runs.get(cycle_type, None).isoformat() if cycle_type in next_runs else None
                    }
                    for cycle_type, sched in self._schedules.items()
                },
                "callbacks_registered": list(self._callbacks.keys()),
                "total_executions": len(self._history)
            }
    
    def start(self, check_interval: int = 60) -> None:
        """Start the scheduler"""
        if self._running:
            return
        
        self._running = True
        
        def scheduler_loop():
            while self._running:
                now = datetime.now()
                
                # Check each schedule
                for cycle_type, next_run in self.get_next_runs().items():
                    if now >= next_run:
                        logger.info(f"Running scheduled cycle: {cycle_type}")
                        self.run_cycle(cycle_type)
                
                # Sleep until next check
                time.sleep(check_interval)
        
        self._scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        logger.info("Scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler"""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")


# Global scheduler
_global_scheduler: Optional[CycleScheduler] = None


def get_cycle_scheduler() -> CycleScheduler:
    """Get the global cycle scheduler"""
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = CycleScheduler()
    return _global_scheduler


__all__ = [
    "CycleScheduler",
    "CycleSchedule",
    "CycleExecution",
    "CycleFrequency",
    "CycleStatus",
    "get_cycle_scheduler",
]
