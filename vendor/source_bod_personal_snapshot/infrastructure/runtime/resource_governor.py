"""
Resource Governor - BB-ARCH-ISO-002
Agent Sandbox & Container Runtime Architecture

This module implements the Resource Governor that enforces:
- CPU limits
- Memory limits
- Execution time limits

Directive: BB-ARCH-ISO-002
Section: 7 - Agent Resource Governance
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import time
import resource
import logging

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources"""
    CPU = "cpu"
    MEMORY = "memory"
    EXECUTION_TIME = "execution_time"
    NETWORK = "network"


class ResourceLimitExceeded(Exception):
    """Exception raised when a resource limit is exceeded"""
    def __init__(self, resource_type: ResourceType, limit: float, current: float):
        self.resource_type = resource_type
        self.limit = limit
        self.current = current
        super().__init__(f"{resource_type.value} limit exceeded: {current}/{limit}")


@dataclass
class ResourceLimit:
    """A single resource limit"""
    resource_type: ResourceType
    limit: float
    unit: str
    soft_limit: Optional[float] = None  # Warning threshold
    
    def is_exceeded(self, current: float) -> bool:
        return current > self.limit
        
    def is_warning(self, current: float) -> bool:
        if self.soft_limit:
            return current > self.soft_limit
        return False


@dataclass
class AgentResources:
    """Resource usage for an agent"""
    agent_id: str
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    execution_time_seconds: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "cpu_percent": self.cpu_percent,
            "memory_mb": self.memory_mb,
            "execution_time_seconds": self.execution_time_seconds,
            "last_updated": self.last_updated.isoformat()
        }


class ResourceGovernor:
    """
    Resource Governor - Enforces resource limits for agents.
    
    Section 7: Agent Resource Governance
    
    CPU Limits
        max_cpu_percent = 20%
    
    Memory Limits  
        max_memory = 512MB
    
    Execution Limits
        max_reasoning_time = 5 seconds
    
    If limits are exceeded:
        - terminate execution
        - log incident
        - trigger recovery
    """
    
    def __init__(self):
        self._limits: Dict[str, Dict[ResourceType, ResourceLimit]] = {}
        self._usage: Dict[str, AgentResources] = {}
        self._lock = threading.RLock()
        
        # Default limits
        self._default_limits = {
            ResourceType.CPU: ResourceLimit(ResourceType.CPU, 20.0, "%", soft_limit=15.0),
            ResourceType.MEMORY: ResourceLimit(ResourceType.MEMORY, 512.0, "MB", soft_limit=400.0),
            ResourceType.EXECUTION_TIME: ResourceLimit(ResourceType.EXECUTION_TIME, 5.0, "seconds", soft_limit=4.0)
        }
        
        # Callbacks
        self._on_limit_exceeded: List[Callable] = []
        self._on_warning: List[Callable] = []
        
    def set_limits(self, agent_id: str, limits: Dict[ResourceType, ResourceLimit]) -> None:
        """Set resource limits for an agent"""
        with self._lock:
            self._limits[agent_id] = limits
            logger.info(f"Set resource limits for agent {agent_id}")
            
    def get_limits(self, agent_id: str) -> Dict[ResourceType, ResourceLimit]:
        """Get resource limits for an agent"""
        with self._lock:
            return self._limits.get(agent_id, self._default_limits)
            
    def check_limits(self, agent_id: str) -> Dict[str, Any]:
        """
        Check current resource usage against limits.
        
        Returns dict with status and any violations.
        """
        with self._lock:
            limits = self.get_limits(agent_id)
            usage = self._usage.get(agent_id)
            
            if not usage:
                return {"status": "unknown", "violations": []}
                
            violations = []
            warnings = []
            
            # Check CPU
            cpu_limit = limits.get(ResourceType.CPU)
            if cpu_limit:
                if cpu_limit.is_exceeded(usage.cpu_percent):
                    violations.append({
                        "resource": "cpu",
                        "limit": cpu_limit.limit,
                        "current": usage.cpu_percent
                    })
                elif cpu_limit.is_warning(usage.cpu_percent):
                    warnings.append({
                        "resource": "cpu",
                        "soft_limit": cpu_limit.soft_limit,
                        "current": usage.cpu_percent
                    })
                    
            # Check Memory
            mem_limit = limits.get(ResourceType.MEMORY)
            if mem_limit:
                if mem_limit.is_exceeded(usage.memory_mb):
                    violations.append({
                        "resource": "memory",
                        "limit": mem_limit.limit,
                        "current": usage.memory_mb
                    })
                elif mem_limit.is_warning(usage.memory_mb):
                    warnings.append({
                        "resource": "memory",
                        "soft_limit": mem_limit.soft_limit,
                        "current": usage.memory_mb
                    })
                    
            # Check Execution Time
            exec_limit = limits.get(ResourceType.EXECUTION_TIME)
            if exec_limit:
                if exec_limit.is_exceeded(usage.execution_time_seconds):
                    violations.append({
                        "resource": "execution_time",
                        "limit": exec_limit.limit,
                        "current": usage.execution_time_seconds
                    })
                elif exec_limit.is_warning(usage.execution_time_seconds):
                    warnings.append({
                        "resource": "execution_time",
                        "soft_limit": exec_limit.soft_limit,
                        "current": usage.execution_time_seconds
                    })
                    
            status = "ok"
            if violations:
                status = "violation"
                self._trigger_limit_exceeded(agent_id, violations)
            elif warnings:
                status = "warning"
                self._trigger_warning(agent_id, warnings)
                
            return {
                "status": status,
                "violations": violations,
                "warnings": warnings,
                "usage": usage.to_dict()
            }
            
    def update_usage(self, agent_id: str, cpu_percent: float = None, memory_mb: float = None, execution_time_seconds: float = None) -> None:
        """Update resource usage for an agent"""
        with self._lock:
            if agent_id not in self._usage:
                self._usage[agent_id] = AgentResources(agent_id=agent_id)
                
            usage = self._usage[agent_id]
            
            if cpu_percent is not None:
                usage.cpu_percent = cpu_percent
            if memory_mb is not None:
                usage.memory_mb = memory_mb
            if execution_time_seconds is not None:
                usage.execution_time_seconds = execution_time_seconds
                
            usage.last_updated = datetime.now()
            
    def increment_execution_time(self, agent_id: str, seconds: float) -> None:
        """Increment execution time counter"""
        with self._lock:
            if agent_id not in self._usage:
                self._usage[agent_id] = AgentResources(agent_id=agent_id)
            self._usage[agent_id].execution_time_seconds += seconds
            
    def reset_usage(self, agent_id: str) -> None:
        """Reset resource usage for an agent"""
        with self._lock:
            if agent_id in self._usage:
                self._usage[agent_id] = AgentResources(agent_id=agent_id)
                
    def get_usage(self, agent_id: str) -> Optional[AgentResources]:
        """Get current resource usage for an agent"""
        return self._usage.get(agent_id)
        
    def get_all_usage(self) -> Dict[str, AgentResources]:
        """Get resource usage for all agents"""
        return self._usage.copy()
        
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system-wide resource summary"""
        with self._lock:
            total_cpu = sum(u.cpu_percent for u in self._usage.values())
            total_memory = sum(u.memory_mb for u in self._usage.values())
            agents_over_limit = 0
            
            for agent_id in self._usage:
                check = self.check_limits(agent_id)
                if check["status"] == "violation":
                    agents_over_limit += 1
                    
            return {
                "total_agents": len(self._usage),
                "total_cpu_percent": total_cpu,
                "total_memory_mb": total_memory,
                "agents_over_limit": agents_over_limit,
                "average_cpu": total_cpu / len(self._usage) if self._usage else 0,
                "average_memory": total_memory / len(self._usage) if self._usage else 0
            }
            
    def _trigger_limit_exceeded(self, agent_id: str, violations: List[Dict]) -> None:
        """Trigger callbacks when limit is exceeded"""
        logger.warning(f"Resource limit exceeded for agent {agent_id}: {violations}")
        for callback in self._on_limit_exceeded:
            try:
                callback(agent_id, violations)
            except Exception as e:
                logger.error(f"Limit exceeded callback error: {e}")
                
    def _trigger_warning(self, agent_id: str, warnings: List[Dict]) -> None:
        """Trigger callbacks on warning"""
        for callback in self._on_warning:
            try:
                callback(agent_id, warnings)
            except Exception as e:
                logger.error(f"Warning callback error: {e}")
                
    def on_limit_exceeded(self, callback: Callable) -> None:
        """Register limit exceeded callback"""
        self._on_limit_exceeded.append(callback)
        
    def on_warning(self, callback: Callable) -> None:
        """Register warning callback"""
        self._on_warning.append(callback)


class ExecutionTimer:
    """
    Context manager for timing agent execution.
    
    Automatically tracks execution time and enforces limits.
    """
    
    def __init__(self, governor: ResourceGovernor, agent_id: str, max_seconds: float):
        self.governor = governor
        self.agent_id = agent_id
        self.max_seconds = max_seconds
        self.start_time = None
        self.elapsed = 0
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        
        # Update governor
        self.governor.increment_execution_time(self.agent_id, self.elapsed)
        
        # Check limit
        if self.elapsed > self.max_seconds:
            raise ResourceLimitExceeded(
                ResourceType.EXECUTION_TIME,
                self.max_seconds,
                self.elapsed
            )
            
        return False  # Don't suppress exceptions


# Global resource governor instance
_global_resource_governor: Optional[ResourceGovernor] = None


def get_resource_governor() -> ResourceGovernor:
    """Get the global resource governor"""
    global _global_resource_governor
    if _global_resource_governor is None:
        _global_resource_governor = ResourceGovernor()
    return _global_resource_governor


def reset_resource_governor() -> None:
    """Reset the global resource governor (for testing)"""
    global _global_resource_governor
    _global_resource_governor = None
