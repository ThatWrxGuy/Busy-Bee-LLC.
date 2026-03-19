"""
Runtime Isolator - Layer 4: Runtime Execution Isolation
BB-ARCH-ISO-001: Agent & Engine Isolation Architecture

This module implements runtime isolation for engines, ensuring fault containment
and graceful degradation when engines fail.

Directive: BB-ARCH-ISO-001
Layer: 4 - Runtime Execution Isolation

Core Engines Isolated:
- Signal Ingestion Engine
- Life Signal Graph Engine
- Strategy Tournament Engine
- Digital Twin Simulation Engine
- Recommendation Engine
- Memory Engine
- Execution Workflow Engine
- Audit & Compliance Engine
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import time
import logging
import traceback

logger = logging.getLogger(__name__)


class EngineStatus(Enum):
    """Engine status states"""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    STOPPED = "stopped"


class EngineType(Enum):
    """Types of engines in the system"""
    SIGNAL_INGESTION = "signal_ingestion"
    LIFE_SIGNAL_GRAPH = "life_signal_graph"
    STRATEGY_TOURNAMENT = "strategy_tournament"
    DIGITAL_TWIN_SIMULATION = "digital_twin_simulation"
    RECOMMENDATION = "recommendation"
    MEMORY = "memory"
    EXECUTION_WORKFLOW = "execution_workflow"
    AUDIT_COMPLIANCE = "audit_compliance"


@dataclass
class EngineHealth:
    """Health information for an engine"""
    engine_id: str
    status: EngineStatus
    last_check: datetime
    failure_count: int = 0
    last_failure: Optional[str] = None
    last_failure_time: Optional[datetime] = None
    last_success: Optional[datetime] = None
    avg_execution_time_ms: float = 0.0
    total_executions: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineConfig:
    """Configuration for an isolated engine"""
    engine_id: str
    engine_type: EngineType
    timeout_ms: int = 30000  # Default 30 second timeout
    max_retries: int = 3
    retry_delay_ms: int = 1000
    enable_degraded_mode: bool = True
    failure_threshold: int = 5  # Failures before stopping
    health_check_interval_ms: int = 60000  # 1 minute


class IsolatedEngine(ABC):
    """
    Abstract base class for isolated engines.
    
    Each engine runs in its own execution context with:
    - Timeout protection
    - Error handling and recovery
    - Health monitoring
    - Graceful degradation
    
    When an engine fails:
    1. Detect failure
    2. Isolate failing engine
    3. Activate degraded mode
    4. Log incident
    5. Trigger self-healing
    """
    
    def __init__(self, config: EngineConfig):
        self.config = config
        self._status = EngineStatus.INITIALIZING
        self._health = EngineHealth(
            engine_id=config.engine_id,
            status=EngineStatus.INITIALIZING,
            last_check=datetime.now()
        )
        self._lock = threading.RLock()
        self._callbacks: Dict[str, List[Callable]] = {
            "on_failure": [],
            "on_recovery": [],
            "on_status_change": []
        }
        
    @property
    def status(self) -> EngineStatus:
        """Get current engine status"""
        return self._status
    
    @property
    def health(self) -> EngineHealth:
        """Get engine health information"""
        return self._health
    
    @property
    def engine_id(self) -> str:
        """Get engine ID"""
        return self.config.engine_id
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback for engine events"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, *args, **kwargs) -> None:
        """Trigger registered callbacks"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")
    
    def _update_status(self, new_status: EngineStatus) -> None:
        """Update engine status"""
        with self._lock:
            old_status = self._status
            self._status = new_status
            self._health.status = new_status
            self._health.last_check = datetime.now()
            
            if old_status != new_status:
                logger.info(f"Engine {self.config.engine_id} status: {old_status.value} -> {new_status.value}")
                self._trigger_callbacks("on_status_change", old_status, new_status)
    
    def execute_with_isolation(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with runtime isolation.
        
        This wraps the function with:
        - Timeout protection
        - Error handling
        - Health tracking
        - Recovery logic
        """
        start_time = time.time()
        
        try:
            self._update_status(EngineStatus.HEALTHY)
            
            # Execute with timeout
            result = self._execute_with_timeout(func, *args, **kwargs)
            
            # Track success
            execution_time = (time.time() - start_time) * 1000
            self._track_success(execution_time)
            
            return result
            
        except TimeoutError:
            self._track_failure("Execution timeout")
            self._update_status(EngineStatus.FAILED)
            raise
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self._track_failure(error_msg)
            
            # Check if should stop
            if self._health.failure_count >= self.config.failure_threshold:
                logger.error(f"Engine {self.config.engine_id} exceeded failure threshold, stopping")
                self._update_status(EngineStatus.FAILED)
                self._trigger_callbacks("on_failure", error_msg)
            elif self.config.enable_degraded_mode:
                self._update_status(EngineStatus.DEGRADED)
            else:
                self._update_status(EngineStatus.FAILED)
                
            raise
            
    def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with timeout"""
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
                
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.config.timeout_ms / 1000)
        
        if thread.is_alive():
            raise TimeoutError(f"Execution exceeded timeout of {self.config.timeout_ms}ms")
            
        if exception[0]:
            raise exception[0]
            
        return result[0]
    
    def _track_success(self, execution_time_ms: float) -> None:
        """Track successful execution"""
        with self._lock:
            self._health.total_executions += 1
            self._health.last_success = datetime.now()
            
            # Update average execution time
            total = self._health.avg_execution_time_ms * (self._health.total_executions - 1)
            self._health.avg_execution_time_ms = (total + execution_time_ms) / self._health.total_executions
            
            # Reset failure count on success
            if self._health.status == EngineStatus.DEGRADED:
                self._health.failure_count = 0
                self._update_status(EngineStatus.HEALTHY)
    
    def _track_failure(self, error_msg: str) -> None:
        """Track failed execution"""
        with self._lock:
            self._health.failure_count += 1
            self._health.last_failure = error_msg
            self._health.last_failure_time = datetime.now()
            
            logger.warning(f"Engine {self.config.engine_id} failure #{self._health.failure_count}: {error_msg}")
    
    def start(self) -> None:
        """Start the engine"""
        self._update_status(EngineStatus.HEALTHY)
        logger.info(f"Engine {self.config.engine_id} started")
        
    def stop(self) -> None:
        """Stop the engine"""
        self._update_status(EngineStatus.STOPPED)
        logger.info(f"Engine {self.config.engine_id} stopped")
        
    def recover(self) -> bool:
        """
        Attempt to recover the engine.
        Returns True if recovery was successful.
        """
        with self._lock:
            self._update_status(EngineStatus.RECOVERING)
            
            try:
                # Reset failure count
                self._health.failure_count = 0
                
                # Perform recovery (implemented by subclass)
                self._perform_recovery()
                
                self._update_status(EngineStatus.HEALTHY)
                self._trigger_callbacks("on_recovery")
                logger.info(f"Engine {self.config.engine_id} recovered successfully")
                return True
                
            except Exception as e:
                logger.error(f"Engine {self.config.engine_id} recovery failed: {e}")
                self._update_status(EngineStatus.FAILED)
                return False
    
    @abstractmethod
    def _perform_recovery(self) -> None:
        """Implement engine-specific recovery logic"""
        pass
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process data through the engine"""
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get engine capabilities"""
        return {
            "engine_id": self.config.engine_id,
            "engine_type": self.config.engine_type.value,
            "status": self._status.value,
            "timeout_ms": self.config.timeout_ms,
            "max_retries": self.config.max_retries
        }


class RuntimeIsolator:
    """
    Manager for all isolated engines.
    
    Provides:
    - Engine registration
    - Health monitoring
    - Fault containment
    - Degraded mode coordination
    - Self-healing triggers
    """
    
    def __init__(self):
        self._engines: Dict[str, IsolatedEngine] = {}
        self._lock = threading.RLock()
        self._system_health: Dict[str, Any] = {}
        
    def register_engine(self, engine: IsolatedEngine) -> None:
        """Register an engine with the isolator"""
        with self._lock:
            self._engines[engine.engine_id] = engine
            logger.info(f"Registered engine: {engine.engine_id}")
            
    def unregister_engine(self, engine_id: str) -> None:
        """Unregister an engine"""
        with self._lock:
            if engine_id in self._engines:
                del self._engines[engine_id]
                logger.info(f"Unregistered engine: {engine_id}")
                
    def get_engine(self, engine_id: str) -> Optional[IsolatedEngine]:
        """Get an engine by ID"""
        return self._engines.get(engine_id)
    
    def get_engine_health(self, engine_id: str) -> Optional[EngineHealth]:
        """Get health information for an engine"""
        engine = self._engines.get(engine_id)
        return engine.health if engine else None
    
    def get_all_health(self) -> Dict[str, EngineHealth]:
        """Get health for all engines"""
        return {
            engine_id: engine.health
            for engine_id, engine in self._engines.items()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        with self._lock:
            total = len(self._engines)
            healthy = sum(
                1 for e in self._engines.values()
                if e.status == EngineStatus.HEALTHY
            )
            degraded = sum(
                1 for e in self._engines.values()
                if e.status == EngineStatus.DEGRADED
            )
            failed = sum(
                1 for e in self._engines.values()
                if e.status == EngineStatus.FAILED
            )
            
            return {
                "total_engines": total,
                "healthy": healthy,
                "degraded": degraded,
                "failed": failed,
                "health_percentage": (healthy / total * 100) if total > 0 else 0,
                "requires_attention": failed > 0 or degraded > 0
            }
    
    def execute_engine(self, engine_id: str, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function through an isolated engine.
        
        This provides the runtime isolation wrapper for any engine operation.
        """
        engine = self._engines.get(engine_id)
        if not engine:
            raise ValueError(f"Engine not found: {engine_id}")
            
        return engine.execute_with_isolation(func, *args, **kwargs)
    
    def isolate_engine(self, engine_id: str) -> bool:
        """
        Isolate a failing engine.
        
        Returns True if isolation was successful.
        """
        engine = self._engines.get(engine_id)
        if not engine:
            return False
            
        engine.stop()
        logger.warning(f"Isolated engine: {engine_id}")
        return True
    
    def recover_engine(self, engine_id: str) -> bool:
        """Attempt to recover an engine"""
        engine = self._engines.get(engine_id)
        if not engine:
            return False
            
        return engine.recover()
    
    def activate_degraded_mode(self) -> Dict[str, Any]:
        """
        Activate degraded mode across all engines.
        
        Returns information about which engines are available.
        """
        available_engines = {}
        
        with self._lock:
            for engine_id, engine in self._engines.items():
                if engine.status == EngineStatus.HEALTHY:
                    available_engines[engine_id] = {
                        "status": "available",
                        "capabilities": engine.get_capabilities()
                    }
                else:
                    available_engines[engine_id] = {
                        "status": engine.status.value,
                        "reason": engine.health.last_failure
                    }
                    
        logger.warning(f"Degraded mode activated. Available engines: {list(available_engines.keys())}")
        return available_engines


# Global runtime isolator instance
_global_runtime_isolator: Optional[RuntimeIsolator] = None


def get_runtime_isolator() -> RuntimeIsolator:
    """Get the global runtime isolator"""
    global _global_runtime_isolator
    if _global_runtime_isolator is None:
        _global_runtime_isolator = RuntimeIsolator()
    return _global_runtime_isolator


def reset_runtime_isolator() -> None:
    """Reset the global runtime isolator (for testing)"""
    global _global_runtime_isolator
    _global_runtime_isolator = None
