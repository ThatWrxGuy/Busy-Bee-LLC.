"""
Base Specialist Agent - Abstract base for all specialist agents
Part of BB-DOM-001: Domain Intelligence Expansion Framework
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentRole(Enum):
    """Specialist agent roles as defined in BB-DOM-001"""
    OBSERVER = "observer"      # Detect patterns, signals, anomalies
    STRATEGIST = "strategist"  # Generate plans, recommendations
    GOVERNOR = "governor"      # Ensure safety, alignment, discipline


@dataclass
class AgentSignal:
    """Input signal to an agent"""
    id: str
    source: str
    signal_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentInsight:
    """Output insight from an agent"""
    id: str
    agent_id: str
    agent_role: AgentRole
    insight_type: str
    title: str
    description: str
    confidence: float  # 0.0 - 1.0
    priority: str  # critical, high, medium, low
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class SpecialistAgent(ABC):
    """
    Abstract base class for all specialist agents.
    
    Roles (BB-DOM-001):
    - Observer: Detect patterns, signals, anomalies
    - Strategist: Generate plans, recommendations  
    - Governor: Ensure safety, alignment, discipline
    
    All agents must:
    - Process signals through the domain pipeline
    - Produce structured insights
    - Not execute actions directly
    """
    
    def __init__(self, agent_id: str, name: str, role: AgentRole, domain: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.domain = domain
        self.insights: List[AgentInsight] = []
        self.processed_signals: List[str] = []  # Signal IDs
    
    @abstractmethod
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        """Process an input signal and produce an insight"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        pass
    
    def create_insight(
        self,
        insight_type: str,
        title: str,
        description: str,
        confidence: float,
        priority: str = "medium",
        data: Optional[Dict[str, Any]] = None
    ) -> AgentInsight:
        """Helper to create an insight"""
        insight = AgentInsight(
            id=f"insight_{self.agent_id}_{len(self.insights) + 1}_{datetime.now().timestamp()}",
            agent_id=self.agent_id,
            agent_role=self.role,
            insight_type=insight_type,
            title=title,
            description=description,
            confidence=confidence,
            priority=priority,
            data=data or {}
        )
        self.insights.append(insight)
        return insight
    
    def get_latest_insights(self, limit: int = 5) -> List[AgentInsight]:
        """Get latest insights"""
        return self.insights[-limit:]
    
    def clear_insights(self):
        """Clear stored insights"""
        self.insights = []


# Observer Agents - Detect patterns, signals, anomalies
class ObserverAgent(SpecialistAgent):
    """Base class for Observer agents"""
    
    def __init__(self, agent_id: str, name: str, domain: str):
        super().__init__(agent_id, name, AgentRole.OBSERVER, domain)


# Strategist Agents - Generate plans, recommendations
class StrategistAgent(SpecialistAgent):
    """Base class for Strategist agents"""
    
    def __init__(self, agent_id: str, name: str, domain: str):
        super().__init__(agent_id, name, AgentRole.STRATEGIST, domain)


# Governor Agents - Ensure safety, alignment, discipline
class GovernorAgent(SpecialistAgent):
    """Base class for Governor agents"""
    
    def __init__(self, agent_id: str, name: str, domain: str):
        super().__init__(agent_id, name, AgentRole.GOVERNOR, domain)
