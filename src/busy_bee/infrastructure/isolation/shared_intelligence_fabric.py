"""
Shared Intelligence Fabric - Coordination Layer
BB-ARCH-ISO-001: Agent & Engine Isolation Architecture

This module implements the Shared Intelligence Fabric that enables communication
between isolated agents while maintaining isolation boundaries.

Directive: BB-ARCH-ISO-001
Section: 9 - Shared Intelligence Fabric

Fabric Components:
- Event Bus: Message routing between agents
- Life Signal Graph: Cross-domain signal visualization
- Strategy Registry: Strategy storage and discovery
- Recommendation Ledger: Track recommendations
- Confidence Scoring Engine: Evaluate confidence
- Risk Engine: Aggregate risk assessment

Agents communicate ONLY through this fabric.
Direct agent-to-agent manipulation is prohibited.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import uuid
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the fabric"""
    SIGNAL_RECEIVED = "signal_received"
    INSIGHT_GENERATED = "insight_generated"
    RECOMMENDATION_CREATED = "recommendation_created"
    RISK_SIGNAL = "risk_signal"
    STRATEGY_REGISTERED = "strategy_registered"
    DOMAIN_UPDATE = "domain_update"
    EXECUTIVE_BRIEF = "executive_brief"


@dataclass
class FabricEvent:
    """Event in the shared intelligence fabric"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.SIGNAL_RECEIVED
    source_agent_id: str = ""
    source_domain: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0  # Higher priority events processed first
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source_agent_id": self.source_agent_id,
            "source_domain": self.source_domain,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority
        }


class EventBus:
    """
    Event Bus - Routes events between agents.
    
    This is the primary communication channel for agents.
    Agents publish events and subscribe to relevant event types.
    """
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._event_history: List[FabricEvent] = []
        self._max_history = 1000
        self._lock = threading.RLock()
        
    def subscribe(self, event_type: EventType, callback: Callable[[FabricEvent], None]) -> None:
        """Subscribe to an event type"""
        with self._lock:
            self._subscribers[event_type].append(callback)
            logger.info(f"Subscribed to event type: {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[FabricEvent], None]) -> None:
        """Unsubscribe from an event type"""
        with self._lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                
    def publish(self, event: FabricEvent) -> None:
        """Publish an event to all subscribers"""
        with self._lock:
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
            
            # Notify subscribers
            subscribers = self._subscribers.get(event.event_type, [])
            for callback in subscribers:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Event callback error: {e}")
    
    def get_history(
        self, 
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[FabricEvent]:
        """Get event history"""
        with self._lock:
            events = self._event_history
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            return events[-limit:]


class StrategyRegistry:
    """
    Strategy Registry - Stores and discovers strategies.
    
    Agents register strategies which can then be evaluated
    and selected by the Executive Council.
    """
    
    def __init__(self):
        self._strategies: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        
    def register_strategy(
        self,
        strategy_id: str,
        agent_id: str,
        domain: str,
        strategy_data: Dict[str, Any]
    ) -> None:
        """Register a strategy"""
        with self._lock:
            self._strategies[strategy_id] = {
                "strategy_id": strategy_id,
                "agent_id": agent_id,
                "domain": domain,
                "data": strategy_data,
                "created_at": datetime.now(),
                "status": "active"
            }
            logger.info(f"Registered strategy: {strategy_id} from {agent_id}")
    
    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get a strategy by ID"""
        return self._strategies.get(strategy_id)
    
    def get_strategies_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all strategies for a domain"""
        return [
            s for s in self._strategies.values()
            if s["domain"] == domain
        ]
    
    def get_all_strategies(self) -> List[Dict[str, Any]]:
        """Get all strategies"""
        return list(self._strategies.values())
    
    def update_strategy_status(self, strategy_id: str, status: str) -> bool:
        """Update strategy status"""
        with self._lock:
            if strategy_id in self._strategies:
                self._strategies[strategy_id]["status"] = status
                return True
            return False


class RecommendationLedger:
    """
    Recommendation Ledger - Tracks all recommendations.
    
    Maintains a complete record of all recommendations
    for audit and tracking purposes.
    """
    
    def __init__(self):
        self._recommendations: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        
    def add_recommendation(
        self,
        recommendation_id: str,
        agent_id: str,
        domain: str,
        recommendation: Dict[str, Any]
    ) -> None:
        """Add a recommendation to the ledger"""
        with self._lock:
            self._recommendations[recommendation_id] = {
                "recommendation_id": recommendation_id,
                "agent_id": agent_id,
                "domain": domain,
                "recommendation": recommendation,
                "status": "pending",
                "created_at": datetime.now(),
                "evaluated_at": None,
                "outcome": None
            }
            logger.info(f"Added recommendation: {recommendation_id} from {agent_id}")
    
    def update_status(
        self,
        recommendation_id: str,
        status: str,
        outcome: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update recommendation status"""
        with self._lock:
            if recommendation_id in self._recommendations:
                rec = self._recommendations[recommendation_id]
                rec["status"] = status
                rec["evaluated_at"] = datetime.now()
                if outcome:
                    rec["outcome"] = outcome
                return True
            return False
    
    def get_recommendation(self, recommendation_id: str) -> Optional[Dict[str, Any]]:
        """Get a recommendation by ID"""
        return self._recommendations.get(recommendation_id)
    
    def get_recommendations_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all recommendations for a domain"""
        return [
            r for r in self._recommendations.values()
            if r["domain"] == domain
        ]
    
    def get_pending_recommendations(self) -> List[Dict[str, Any]]:
        """Get all pending recommendations"""
        return [
            r for r in self._recommendations.values()
            if r["status"] == "pending"
        ]


class ConfidenceScorer:
    """
    Confidence Scoring Engine - Evaluates confidence in insights.
    
    Provides confidence scoring for agent insights
    based on multiple factors.
    """
    
    def __init__(self):
        self._scoring_weights = {
            "data_quality": 0.3,
            "source_reliability": 0.25,
            "historical_accuracy": 0.2,
            "cross_domain_validation": 0.15,
            "timeliness": 0.1
        }
        
    def score_confidence(
        self,
        insight_data: Dict[str, Any],
        agent_history: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate confidence score for an insight"""
        
        scores = {}
        
        # Data quality score
        data_quality = insight_data.get("data_quality", 0.5)
        scores["data_quality"] = data_quality * self._scoring_weights["data_quality"]
        
        # Source reliability
        source = insight_data.get("source", "unknown")
        source_scores = {
            "api": 0.9,
            "sensor": 0.85,
            "user_input": 0.7,
            "inferred": 0.5,
            "unknown": 0.3
        }
        source_reliability = source_scores.get(source, 0.5)
        scores["source_reliability"] = source_reliability * self._scoring_weights["source_reliability"]
        
        # Historical accuracy (if available)
        if agent_history:
            historical_accuracy = agent_history.get("accuracy", 0.5)
        else:
            historical_accuracy = 0.5
        scores["historical_accuracy"] = historical_accuracy * self._scoring_weights["historical_accuracy"]
        
        # Cross-domain validation
        cross_domain_supported = insight_data.get("cross_domain_validation", False)
        cross_domain_score = 0.8 if cross_domain_supported else 0.4
        scores["cross_domain_validation"] = cross_domain_score * self._scoring_weights["cross_domain_validation"]
        
        # Timeliness
        age_minutes = insight_data.get("age_minutes", 0)
        if age_minutes < 60:
            timeliness = 1.0
        elif age_minutes < 3600:
            timeliness = 0.8
        elif age_minutes < 86400:
            timeliness = 0.5
        else:
            timeliness = 0.2
        scores["timeliness"] = timeliness * self._scoring_weights["timeliness"]
        
        # Total score
        total_score = sum(scores.values())
        
        # Determine confidence level
        if total_score >= 0.75:
            confidence_level = "high"
        elif total_score >= 0.5:
            confidence_level = "medium"
        else:
            confidence_level = "low"
            
        return {
            "total_score": total_score,
            "confidence_level": confidence_level,
            "component_scores": scores,
            "factors": list(scores.keys())
        }


class RiskAggregator:
    """
    Risk Engine - Aggregates risk across domains.
    
    Collects and aggregates risk signals from all domains
    to provide a holistic view of system risk.
    """
    
    def __init__(self):
        self._domain_risks: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._lock = threading.RLock()
        
    def add_risk_signal(
        self,
        domain: str,
        risk_type: str,
        severity: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a risk signal from a domain"""
        with self._lock:
            signal_id = f"risk_{domain}_{uuid.uuid4()}"
            signal = {
                "signal_id": signal_id,
                "domain": domain,
                "risk_type": risk_type,
                "severity": severity,
                "description": description,
                "metadata": metadata or {},
                "timestamp": datetime.now()
            }
            self._domain_risks[domain].append(signal)
            
            logger.info(f"Added risk signal: {signal_id} from {domain}")
            return signal_id
    
    def get_domain_risks(self, domain: str) -> List[Dict[str, Any]]:
        """Get all risk signals for a domain"""
        return self._domain_risks.get(domain, [])
    
    def get_all_risks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all risk signals"""
        return dict(self._domain_risks)
    
    def get_high_severity_risks(self) -> List[Dict[str, Any]]:
        """Get all high severity risk signals"""
        with self._lock:
            risks = []
            for domain_signals in self._domain_risks.values():
                for signal in domain_signals:
                    if signal["severity"] in ("high", "critical"):
                        risks.append(signal)
            return risks
    
    def calculate_aggregate_risk(self) -> Dict[str, Any]:
        """Calculate aggregate risk score across all domains"""
        with self._lock:
            total_risks = sum(len(signals) for signals in self._domain_risks.values())
            high_severity = sum(
                1 for signals in self._domain_risks.values()
                for s in signals if s["severity"] in ("high", "critical")
            )
            
            severity_scores = {
                "low": 1,
                "medium": 2,
                "high": 5,
                "critical": 10
            }
            
            weighted_score = 0
            for signals in self._domain_risks.values():
                for signal in signals:
                    weighted_score += severity_scores.get(signal["severity"], 1)
            
            # Normalize to 0-1
            max_possible = total_risks * 10 if total_risks > 0 else 1
            risk_score = min(weighted_score / max_possible, 1.0)
            
            if risk_score >= 0.7:
                risk_level = "critical"
            elif risk_score >= 0.5:
                risk_level = "high"
            elif risk_score >= 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
                
            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "total_risks": total_risks,
                "high_severity_count": high_severity,
                "domains_affected": len(self._domain_risks)
            }
    
    def clear_domain_risks(self, domain: str) -> None:
        """Clear risk signals for a domain"""
        with self._lock:
            if domain in self._domain_risks:
                self._domain_risks[domain] = []


class SharedIntelligenceFabric:
    """
    Shared Intelligence Fabric - Main coordinator.
    
    Integrates all fabric components:
    - Event Bus
    - Strategy Registry
    - Recommendation Ledger
    - Confidence Scoring Engine
    - Risk Engine
    
    This is the ONLY way agents communicate.
    Direct agent-to-agent manipulation is prohibited.
    """
    
    def __init__(self):
        self.event_bus = EventBus()
        self.strategy_registry = StrategyRegistry()
        self.recommendation_ledger = RecommendationLedger()
        self.confidence_scorer = ConfidenceScorer()
        self.risk_engine = RiskAggregator()
        
        self._lock = threading.RLock()
        
    def publish_event(
        self,
        event_type: EventType,
        source_agent_id: str,
        source_domain: str,
        payload: Dict[str, Any],
        priority: int = 0
    ) -> FabricEvent:
        """Publish an event to the fabric"""
        event = FabricEvent(
            event_type=event_type,
            source_agent_id=source_agent_id,
            source_domain=source_domain,
            payload=payload,
            priority=priority
        )
        self.event_bus.publish(event)
        return event
    
    def subscribe_to_events(
        self,
        event_type: EventType,
        callback: Callable[[FabricEvent], None]
    ) -> None:
        """Subscribe to an event type"""
        self.event_bus.subscribe(event_type, callback)
    
    def register_strategy(
        self,
        strategy_id: str,
        agent_id: str,
        domain: str,
        strategy_data: Dict[str, Any]
    ) -> None:
        """Register a strategy"""
        self.strategy_registry.register_strategy(
            strategy_id, agent_id, domain, strategy_data
        )
        
        # Publish event
        self.publish_event(
            EventType.STRATEGY_REGISTERED,
            agent_id,
            domain,
            {"strategy_id": strategy_id, "data": strategy_data}
        )
    
    def add_recommendation(
        self,
        recommendation_id: str,
        agent_id: str,
        domain: str,
        recommendation: Dict[str, Any]
    ) -> None:
        """Add a recommendation"""
        self.recommendation_ledger.add_recommendation(
            recommendation_id, agent_id, domain, recommendation
        )
        
        # Publish event
        self.publish_event(
            EventType.RECOMMENDATION_CREATED,
            agent_id,
            domain,
            {"recommendation_id": recommendation_id}
        )
    
    def add_risk_signal(
        self,
        domain: str,
        risk_type: str,
        severity: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a risk signal"""
        signal_id = self.risk_engine.add_risk_signal(
            domain, risk_type, severity, description, metadata
        )
        
        # Publish event
        self.publish_event(
            EventType.RISK_SIGNAL,
            domain,
            domain,
            {"signal_id": signal_id, "severity": severity}
        )
        
        return signal_id
    
    def score_confidence(
        self,
        insight_data: Dict[str, Any],
        agent_history: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Score confidence for an insight"""
        return self.confidence_scorer.score_confidence(insight_data, agent_history)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get fabric system status"""
        return {
            "event_history_size": len(self.event_bus._event_history),
            "strategies_registered": len(self.strategy_registry._strategies),
            "recommendations_tracked": len(self.recommendation_ledger._recommendations),
            "aggregate_risk": self.risk_engine.calculate_aggregate_risk()
        }


# Global fabric instance
_global_fabric: Optional[SharedIntelligenceFabric] = None


def get_shared_intelligence_fabric() -> SharedIntelligenceFabric:
    """Get the global shared intelligence fabric"""
    global _global_fabric
    if _global_fabric is None:
        _global_fabric = SharedIntelligenceFabric()
    return _global_fabric


def reset_shared_intelligence_fabric() -> None:
    """Reset the global fabric (for testing)"""
    global _global_fabric
    _global_fabric = None
