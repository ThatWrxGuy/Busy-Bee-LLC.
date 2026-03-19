"""
Agent Orchestrator - BB-ARCH-ISO-002
Agent Sandbox & Container Runtime Architecture

This module implements the Agent Orchestrator responsible for:
- Agent lifecycle management
- Sandbox deployment
- Agent health monitoring
- Resource allocation
- Restart policies
- Scaling decisions

Directive: BB-ARCH-ISO-002
Section: 8 - Agent Orchestrator
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import uuid
import logging
import time

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent lifecycle status"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    IDLE = "idle"
    PROCESSING = "processing"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    RECOVERING = "recovering"


class RuntimeMode(Enum):
    """Runtime execution modes"""
    DEVELOPMENT = "development"     # Local Python sandboxes
    CONTAINER = "container"         # Docker containers
    KUBERNETES = "kubernetes"       # Kubernetes pods
    MICROVM = "microvm"             # Firecracker microVMs


@dataclass
class AgentConfig:
    """Configuration for an agent"""
    agent_id: str
    name: str
    domain: str
    runtime_mode: RuntimeMode = RuntimeMode.DEVELOPMENT
    
    # Resource limits
    max_cpu_percent: float = 20.0
    max_memory_mb: int = 512
    max_reasoning_time_seconds: float = 5.0
    
    # Restart policy
    max_restart_attempts: int = 3
    restart_delay_seconds: float = 1.0
    
    # Health monitoring
    health_check_interval_seconds: float = 60.0
    unhealthy_threshold: int = 3
    
    # Entry point
    entry_point: str = ""


@dataclass
class AgentHealth:
    """Health information for an agent"""
    agent_id: str
    status: AgentStatus
    last_check: datetime
    restart_count: int = 0
    total_uptime_seconds: float = 0.0
    last_start_time: Optional[datetime] = None
    last_stop_time: Optional[datetime] = None
    consecutive_failures: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentContainer:
    """Represents an agent's container/sandbox"""
    container_id: str
    agent_id: str
    config: AgentConfig
    status: AgentStatus = AgentStatus.PENDING
    health: Optional[AgentHealth] = None
    capabilities: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "container_id": self.container_id,
            "agent_id": self.agent_id,
            "config": {
                "agent_id": self.config.agent_id,
                "name": self.config.name,
                "domain": self.config.domain,
                "runtime_mode": self.config.runtime_mode.value,
            },
            "status": self.status.value,
            "capabilities": self.capabilities,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None
        }


class SandboxRuntime(ABC):
    """
    Abstract base class for sandbox runtime implementations.
    
    Different implementations provide different isolation levels:
    - Development: Local subprocess/thread isolation
    - Container: Docker-based isolation
    - Kubernetes: Pod-based isolation
    """
    
    @abstractmethod
    def create_container(self, config: AgentConfig) -> AgentContainer:
        """Create a new agent container"""
        pass
    
    @abstractmethod
    def start_container(self, container: AgentContainer) -> bool:
        """Start an agent container"""
        pass
    
    @abstractmethod
    def stop_container(self, container: AgentContainer) -> bool:
        """Stop an agent container"""
        pass
    
    @abstractmethod
    def destroy_container(self, container: AgentContainer) -> bool:
        """Destroy an agent container"""
        pass
    
    @abstractmethod
    def get_container_status(self, container: AgentContainer) -> AgentStatus:
        """Get current container status"""
        pass
    
    @abstractmethod
    def execute_in_container(
        self, 
        container: AgentContainer, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Execute a function inside the container"""
        pass


class DevelopmentSandbox(SandboxRuntime):
    """
    Development mode sandbox using Python subprocess/thread isolation.
    
    Suitable for development and testing.
    """
    
    def __init__(self):
        self._containers: Dict[str, AgentContainer] = {}
        self._processes: Dict[str, threading.Thread] = {}
        self._lock = threading.RLock()
        
    def create_container(self, config: AgentConfig) -> AgentContainer:
        """Create a new agent container"""
        with self._lock:
            container = AgentContainer(
                container_id=f"dev_{uuid.uuid4().hex[:8]}",
                agent_id=config.agent_id,
                config=config,
                status=AgentStatus.PENDING,
                health=AgentHealth(
                    agent_id=config.agent_id,
                    status=AgentStatus.PENDING,
                    last_check=datetime.now()
                )
            )
            self._containers[container.container_id] = container
            logger.info(f"Created development sandbox: {container.container_id}")
            return container
            
    def start_container(self, container: AgentContainer) -> bool:
        """Start an agent container"""
        with self._lock:
            try:
                container.status = AgentStatus.RUNNING
                container.started_at = datetime.now()
                container.health.status = AgentStatus.RUNNING
                container.health.last_start_time = datetime.now()
                container.health.consecutive_failures = 0
                logger.info(f"Started sandbox: {container.container_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to start sandbox {container.container_id}: {e}")
                container.status = AgentStatus.FAILED
                return False
                
    def stop_container(self, container: AgentContainer) -> bool:
        """Stop an agent container"""
        with self._lock:
            container.status = AgentStatus.STOPPED
            container.health.status = AgentStatus.STOPPED
            container.health.last_stop_time = datetime.now()
            
            # Calculate uptime
            if container.health.last_start_time:
                uptime = (datetime.now() - container.health.last_start_time).total_seconds()
                container.health.total_uptime_seconds += uptime
                
            logger.info(f"Stopped sandbox: {container.container_id}")
            return True
            
    def destroy_container(self, container: AgentContainer) -> bool:
        """Destroy an agent container"""
        with self._lock:
            if container.container_id in self._containers:
                del self._containers[container.container_id]
                logger.info(f"Destroyed sandbox: {container.container_id}")
                return True
            return False
            
    def get_container_status(self, container: AgentContainer) -> AgentStatus:
        """Get current container status"""
        return container.status
        
    def execute_in_container(
        self, 
        container: AgentContainer, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Execute a function inside the container"""
        container.status = AgentStatus.PROCESSING
        
        try:
            result = func(*args, **kwargs)
            container.status = AgentStatus.RUNNING
            return result
        except Exception as e:
            container.status = AgentStatus.FAILED
            container.health.consecutive_failures += 1
            container.health.last_error = str(e)
            raise


class AgentOrchestrator:
    """
    Agent Orchestrator - Manages agent lifecycle and runtime.
    
    Responsibilities (Section 8):
    - start_agent(agent_id)
    - stop_agent(agent_id)
    - restart_agent(agent_id)
    - monitor_agent_health(agent_id)
    - isolate_failed_agent(agent_id)
    
    Integrates with RuntimeIsolator from BB-ARCH-ISO-001.
    """
    
    def __init__(
        self,
        runtime: Optional[SandboxRuntime] = None,
        default_runtime_mode: RuntimeMode = RuntimeMode.DEVELOPMENT
    ):
        self._runtime = runtime or DevelopmentSandbox()
        self._default_runtime_mode = default_runtime_mode
        
        self._agents: Dict[str, AgentContainer] = {}
        self._agent_configs: Dict[str, AgentConfig] = {}
        self._lock = threading.RLock()
        
        # Health monitoring
        self._health_monitor_thread: Optional[threading.Thread] = None
        self._monitoring = False
        
        # Callbacks
        self._on_agent_started: List[Callable] = []
        self._on_agent_stopped: List[Callable] = []
        self._on_agent_failed: List[Callable] = []
        self._on_agent_recovered: List[Callable] = []
        
        # Statistics
        self._stats = {
            "total_agents": 0,
            "running": 0,
            "failed": 0,
            "total_restarts": 0
        }
        
    def register_agent_config(self, config: AgentConfig) -> None:
        """Register agent configuration"""
        with self._lock:
            self._agent_configs[config.agent_id] = config
            logger.info(f"Registered agent config: {config.agent_id}")
            
    def start_agent(self, agent_id: str) -> bool:
        """
        Start an agent.
        
        Implements start_agent(agent_id) from Section 8.
        """
        with self._lock:
            # Get or create config
            config = self._agent_configs.get(agent_id)
            if not config:
                logger.warning(f"No config for agent {agent_id}, using defaults")
                config = AgentConfig(
                    agent_id=agent_id,
                    name=agent_id,
                    domain="general",
                    runtime_mode=self._default_runtime_mode
                )
                
            # Create container
            container = self._runtime.create_container(config)
            self._agents[agent_id] = container
            
            # Start container
            success = self._runtime.start_container(container)
            
            if success:
                self._stats["running"] += 1
                self._trigger_callbacks(self._on_agent_started, container)
                logger.info(f"Started agent: {agent_id}")
            else:
                self._stats["failed"] += 1
                self._trigger_callbacks(self._on_agent_failed, container)
                
            return success
            
    def stop_agent(self, agent_id: str) -> bool:
        """
        Stop an agent.
        
        Implements stop_agent(agent_id) from Section 8.
        """
        with self._lock:
            container = self._agents.get(agent_id)
            if not container:
                logger.warning(f"Agent not found: {agent_id}")
                return False
                
            container.status = AgentStatus.STOPPING
            success = self._runtime.stop_container(container)
            
            if success:
                self._stats["running"] = max(0, self._stats["running"] - 1)
                self._trigger_callbacks(self._on_agent_stopped, container)
                logger.info(f"Stopped agent: {agent_id}")
                
            return success
            
    def restart_agent(self, agent_id: str) -> bool:
        """
        Restart an agent.
        
        Implements restart_agent(agent_id) from Section 8.
        """
        with self._lock:
            container = self._agents.get(agent_id)
            if not container:
                return self.start_agent(agent_id)
                
            # Stop first
            self._runtime.stop_container(container)
            
            # Check restart attempts
            restart_count = container.health.restart_count if container.health else 0
            max_attempts = container.config.max_restart_attempts
            
            if restart_count >= max_attempts:
                logger.error(f"Agent {agent_id} exceeded max restart attempts")
                container.status = AgentStatus.FAILED
                self._stats["failed"] += 1
                self._trigger_callbacks(self._on_agent_failed, container)
                return False
                
            # Wait before restart
            time.sleep(container.config.restart_delay_seconds)
            
            # Restart
            success = self._runtime.start_container(container)
            
            if success:
                container.health.restart_count += 1
                container.health.status = AgentStatus.RUNNING
                self._stats["total_restarts"] += 1
                self._trigger_callbacks(self._on_agent_recovered, container)
                logger.info(f"Restarted agent: {agent_id} (attempt {restart_count + 1})")
                
            return success
            
    def isolate_failed_agent(self, agent_id: str) -> bool:
        """
        Isolate a failed agent.
        
        Implements isolate_failed_agent(agent_id) from Section 8.
        """
        with self._lock:
            container = self._agents.get(agent_id)
            if not container:
                return False
                
            # Stop the agent
            self._runtime.stop_container(container)
            container.status = AgentStatus.FAILED
            
            # Update stats
            self._stats["running"] = max(0, self._stats["running"] - 1)
            self._stats["failed"] += 1
            
            logger.warning(f"Isolated failed agent: {agent_id}")
            self._trigger_callbacks(self._on_agent_failed, container)
            
            return True
            
    def monitor_agent_health(self, agent_id: str) -> AgentHealth:
        """
        Monitor agent health.
        
        Implements monitor_agent_health(agent_id) from Section 8.
        """
        container = self._agents.get(agent_id)
        if not container or not container.health:
            return None
            
        # Update health info
        container.health.last_check = datetime.now()
        container.health.status = container.status
        
        # Check for failures
        if container.health.consecutive_failures >= container.config.unhealthy_threshold:
            logger.warning(f"Agent {agent_id} is unhealthy")
            
        return container.health
        
    def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get current agent status"""
        container = self._agents.get(agent_id)
        return container.status if container else None
        
    def get_agent_health(self, agent_id: str) -> Optional[AgentHealth]:
        """Get agent health information"""
        return self.monitor_agent_health(agent_id)
        
    def get_all_agents(self) -> Dict[str, AgentContainer]:
        """Get all registered agents"""
        return self._agents.copy()
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        with self._lock:
            status_counts = {
                status.value: 0 
                for status in AgentStatus
            }
            
            for container in self._agents.values():
                status_counts[container.status.value] += 1
                
            return {
                "total_agents": len(self._agents),
                "by_status": status_counts,
                "running": self._stats["running"],
                "failed": self._stats["failed"],
                "total_restarts": self._stats["total_restarts"],
                "runtime_mode": self._default_runtime_mode.value
            }
            
    def start_health_monitoring(self) -> None:
        """Start background health monitoring"""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._health_monitor_thread = threading.Thread(
            target=self._health_monitor_loop,
            daemon=True
        )
        self._health_monitor_thread.start()
        logger.info("Started health monitoring")
        
    def stop_health_monitoring(self) -> None:
        """Stop background health monitoring"""
        self._monitoring = False
        if self._health_monitor_thread:
            self._health_monitor_thread.join(timeout=5)
        logger.info("Stopped health monitoring")
        
    def _health_monitor_loop(self) -> None:
        """Background health monitoring loop"""
        while self._monitoring:
            try:
                with self._lock:
                    agents_to_check = list(self._agents.keys())
                    
                for agent_id in agents_to_check:
                    health = self.monitor_agent_health(agent_id)
                    
                    # Auto-restart on failure if within limits
                    if health and health.status == AgentStatus.FAILED:
                        container = self._agents.get(agent_id)
                        if container and container.health.restart_count < container.config.max_restart_attempts:
                            logger.info(f"Auto-restarting failed agent: {agent_id}")
                            self.restart_agent(agent_id)
                            
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                
            time.sleep(60)  # Check every minute
            
    def _trigger_callbacks(self, callbacks: List[Callable], container: AgentContainer) -> None:
        """Trigger registered callbacks"""
        for callback in callbacks:
            try:
                callback(container)
            except Exception as e:
                logger.error(f"Callback error: {e}")
                
    # Event registration
    def on_agent_started(self, callback: Callable) -> None:
        """Register agent started callback"""
        self._on_agent_started.append(callback)
        
    def on_agent_stopped(self, callback: Callable) -> None:
        """Register agent stopped callback"""
        self._on_agent_stopped.append(callback)
        
    def on_agent_failed(self, callback: Callable) -> None:
        """Register agent failed callback"""
        self._on_agent_failed.append(callback)
        
    def on_agent_recovered(self, callback: Callable) -> None:
        """Register agent recovered callback"""
        self._on_agent_recovered.append(callback)


# Global orchestrator instance
_global_orchestrator: Optional[AgentOrchestrator] = None


def get_agent_orchestrator() -> AgentOrchestrator:
    """Get the global agent orchestrator"""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = AgentOrchestrator()
    return _global_orchestrator


def reset_agent_orchestrator() -> None:
    """Reset the global orchestrator (for testing)"""
    global _global_orchestrator
    _global_orchestrator = None
