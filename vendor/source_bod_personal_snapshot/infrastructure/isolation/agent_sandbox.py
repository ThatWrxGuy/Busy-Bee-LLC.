"""
Agent Sandbox - Layer 1: Cognitive Isolation
BB-ARCH-ISO-001: Agent & Engine Isolation Architecture

This module implements cognitive isolation for agents, ensuring each agent
operates with clearly defined reasoning boundaries and cannot alter other
agents' internal reasoning processes.

Directive: BB-ARCH-ISO-001
Layer: 1 - Cognitive Isolation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import uuid
import threading
import logging

logger = logging.getLogger(__name__)


class AgentDomain(Enum):
    """Domains as defined in BB-DOM-001"""
    FINANCE = "finance"
    HEALTH = "health"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    INTELLIGENCE = "intelligence"
    LIFE_ARCHITECTURE = "life_architecture"


class AgentType(Enum):
    """Agent types within the system"""
    SPECIALIST = "specialist"  # Domain specialist agents
    CHIEF = "chief"            # Chief officers
    GOVERNOR = "governor"      # Governance agents
    EXECUTIVE = "executive"   # Executive council members


@dataclass
class AgentContext:
    """
    Encapsulates all context provided to an agent.
    This is the ONLY way agents receive external information,
    ensuring controlled input boundaries.
    """
    agent_id: str
    domain: AgentDomain
    available_signals: List[Dict[str, Any]] = field(default_factory=list)
    domain_memory: Dict[str, Any] = field(default_factory=dict)
    shared_intelligence: Dict[str, Any] = field(default_factory=dict)
    agent_working_memory: Dict[str, Any] = field(default_factory=dict)
    
    def get_signal(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific signal from available signals"""
        for sig in self.available_signals:
            if sig.get("id") == signal_id:
                return sig
        return None


@dataclass
class AgentOutput:
    """
    Structured output from an agent.
    Agents MUST publish results through this interface rather than
    directly modifying other agents.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    domain: AgentDomain = AgentDomain.INTELLIGENCE
    insights: List[Dict[str, Any]] = field(default_factory=list)
    risk_signals: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    working_memory_snapshot: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "domain": self.domain.value,
            "insights": self.insights,
            "risk_signals": self.risk_signals,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
            "execution_time_ms": self.execution_time_ms
        }


class AgentSandbox(ABC):
    """
    Abstract base class for agent sandboxes.
    
    Each agent runs in its own sandbox with:
    - Isolated reasoning space
    - Controlled input boundaries
    - Structured output interface
    - No direct access to other agents
    
    The sandbox ensures:
    1. Agents can analyze shared intelligence
    2. Agents cannot alter other agents' reasoning
    3. All outputs go through the Shared Intelligence Fabric
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        domain: AgentDomain,
        allowed_domains: Optional[Set[AgentDomain]] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.domain = domain
        # By default, agents can only access their own domain
        self.allowed_domains = allowed_domains or {domain}
        self._working_memory: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._execution_count = 0
        self._total_execution_time = 0.0
        
    @property
    def working_memory(self) -> Dict[str, Any]:
        """Agent's private temporary reasoning space"""
        return self._working_memory
    
    def clear_working_memory(self):
        """Clear the agent's working memory"""
        with self._lock:
            self._working_memory = {}
            
    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Execute the agent's reasoning within the sandbox.
        
        This is the main entry point for agent execution.
        The context provides all inputs in a controlled manner.
        """
        start_time = datetime.now()
        output = AgentOutput(
            agent_id=self.agent_id,
            domain=self.domain
        )
        
        try:
            # Validate context
            if not self._validate_context(context):
                raise ValueError(f"Invalid context for agent {self.agent_id}")
            
            # Execute reasoning (implemented by subclass)
            result = self._reason(context)
            
            # Populate output
            output.insights = result.get("insights", [])
            output.risk_signals = result.get("risk_signals", [])
            output.recommendations = result.get("recommendations", [])
            output.working_memory_snapshot = self._working_memory.copy()
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} execution failed: {e}")
            output.risk_signals.append({
                "type": "execution_error",
                "severity": "high",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
        finally:
            end_time = datetime.now()
            output.execution_time_ms = (end_time - start_time).total_seconds() * 1000
            with self._lock:
                self._execution_count += 1
                self._total_execution_time += output.execution_time_ms
                
        return output
    
    def _validate_context(self, context: AgentContext) -> bool:
        """Validate that the context is appropriate for this agent"""
        # Check domain access
        if context.domain not in self.allowed_domains:
            logger.warning(
                f"Agent {self.agent_id} attempted to access domain {context.domain}, "
                f"but only has access to {self.allowed_domains}"
            )
            return False
        return True
    
    @abstractmethod
    def _reason(self, context: AgentContext) -> Dict[str, Any]:
        """
        Implement the agent's reasoning logic.
        
        This is where the agent processes inputs and generates outputs.
        Subclasses must implement this method.
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics"""
        with self._lock:
            avg_time = (
                self._total_execution_time / self._execution_count 
                if self._execution_count > 0 else 0
            )
            return {
                "agent_id": self.agent_id,
                "name": self.name,
                "domain": self.domain.value,
                "execution_count": self._execution_count,
                "total_execution_time_ms": self._total_execution_time,
                "average_execution_time_ms": avg_time
            }


class AgentSandboxRegistry:
    """
    Registry for all agent sandboxes.
    Provides centralized access and health monitoring.
    """
    
    def __init__(self):
        self._sandboxes: Dict[str, AgentSandbox] = {}
        self._lock = threading.RLock()
        self._agent_health: Dict[str, Dict[str, Any]] = {}
        
    def register(self, sandbox: AgentSandbox) -> None:
        """Register a new agent sandbox"""
        with self._lock:
            self._sandboxes[sandbox.agent_id] = sandbox
            self._agent_health[sandbox.agent_id] = {
                "status": "healthy",
                "last_execution": None,
                "failure_count": 0,
                "last_failure": None
            }
            logger.info(f"Registered agent sandbox: {sandbox.agent_id}")
            
    def unregister(self, agent_id: str) -> None:
        """Unregister an agent sandbox"""
        with self._lock:
            if agent_id in self._sandboxes:
                del self._sandboxes[agent_id]
                logger.info(f"Unregistered agent sandbox: {agent_id}")
                
    def get(self, agent_id: str) -> Optional[AgentSandbox]:
        """Get an agent sandbox by ID"""
        return self._sandboxes.get(agent_id)
    
    def get_all(self) -> List[AgentSandbox]:
        """Get all registered sandboxes"""
        return list(self._sandboxes.values())
    
    def get_by_domain(self, domain: AgentDomain) -> List[AgentSandbox]:
        """Get all sandboxes for a specific domain"""
        return [
            s for s in self._sandboxes.values() 
            if s.domain == domain
        ]
    
    def update_health(
        self, 
        agent_id: str, 
        status: str, 
        error: Optional[str] = None
    ) -> None:
        """Update agent health status"""
        with self._lock:
            if agent_id in self._agent_health:
                health = self._agent_health[agent_id]
                health["status"] = status
                health["last_execution"] = datetime.now().isoformat()
                
                if status == "failed":
                    health["failure_count"] += 1
                    health["last_failure"] = error
                    
    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all agents"""
        return self._agent_health.copy()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        with self._lock:
            total = len(self._sandboxes)
            healthy = sum(
                1 for h in self._agent_health.values() 
                if h["status"] == "healthy"
            )
            failed = sum(
                1 for h in self._agent_health.values() 
                if h["status"] == "failed"
            )
            
            return {
                "total_agents": total,
                "healthy": healthy,
                "failed": failed,
                "health_percentage": (healthy / total * 100) if total > 0 else 0
            }


# Global registry instance
_global_registry: Optional[AgentSandboxRegistry] = None


def get_agent_registry() -> AgentSandboxRegistry:
    """Get the global agent sandbox registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentSandboxRegistry()
    return _global_registry


def reset_agent_registry() -> None:
    """Reset the global registry (for testing)"""
    global _global_registry
    _global_registry = None
