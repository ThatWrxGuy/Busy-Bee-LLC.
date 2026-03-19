"""
Base Chief Officer - Abstract base for all domain Chief Officers
Part of Layer 3: Domain Intelligence Systems
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DomainSignal:
    """A signal specific to a domain"""
    id: str
    domain: str
    signal_type: str
    title: str
    description: str
    data: Dict[str, Any]
    strength: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DomainStrategy:
    """A strategy recommendation for a domain"""
    id: str
    domain: str
    title: str
    description: str
    priority: str  # critical, high, medium, low
    expected_impact: float
    risk_level: str
    action_items: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "proposed"  # proposed, approved, executing, completed


@dataclass
class DomainReport:
    """A domain intelligence report"""
    id: str
    domain: str
    title: str
    sections: Dict[str, Any]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)


class ChiefOfficer(ABC):
    """
    Abstract base class for all Chief Officers.
    
    Each domain has a Chief Officer responsible for:
    - Managing domain signals
    - Generating domain strategies
    - Producing domain reports
    - Coordinating specialist agents
    """
    
    def __init__(self, domain: str, title: str):
        self.domain = domain
        self.title = title
        self.signals: List[DomainSignal] = []
        self.strategies: List[DomainStrategy] = []
        self.reports: List[DomainReport] = []
        self.specialist_agents: List[str] = []
    
    @abstractmethod
    def analyze_signals(self, signals: List[DomainSignal]) -> Dict[str, Any]:
        """Analyze incoming domain signals"""
        pass
    
    @abstractmethod
    def generate_strategy(self, analysis: Dict[str, Any]) -> DomainStrategy:
        """Generate a domain strategy from analysis"""
        pass
    
    @abstractmethod
    def create_report(self) -> DomainReport:
        """Create a domain intelligence report"""
        pass
    
    def add_signal(self, signal: DomainSignal):
        """Add a signal to the domain"""
        if signal.domain == self.domain:
            self.signals.append(signal)
    
    def add_strategy(self, strategy: DomainStrategy):
        """Add a strategy to the domain"""
        if strategy.domain == self.domain:
            self.strategies.append(strategy)
    
    def get_active_strategies(self) -> List[DomainStrategy]:
        """Get strategies that are in progress"""
        return [s for s in self.strategies if s.status in ["proposed", "approved", "executing"]]
    
    def get_domain_status(self) -> Dict[str, Any]:
        """Get overall domain status"""
        return {
            "domain": self.domain,
            "title": self.title,
            "total_signals": len(self.signals),
            "active_strategies": len(self.get_active_strategies()),
            "completed_strategies": len([s for s in self.strategies if s.status == "completed"]),
            "specialist_agents": self.specialist_agents
        }
