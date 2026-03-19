"""
Global Signal Bus - BB-DOM-002: Domain Signal Architecture

The Global Signal Bus provides:
- decoupled signal distribution
- cross-domain awareness
- reusable signal access
- consistent routing
- observability into signal flow

Phase 2: Global Signal Bus, Routing Engine, Live Store
"""

from typing import Dict, List, Callable, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from enum import Enum

from .signal_schema import Signal, SignalClass, SignalPriority, SignalDomain


class RoutingType(Enum):
    """Signal routing types (BB-DOM-002 Section 10)"""
    PRIMARY = "primary"       # Main owning domain
    SECONDARY = "secondary"  # Related domains
    GLOBAL = "global"        # Platform-wide


@dataclass
class SignalRoute:
    """A routing rule for signals"""
    route_id: str
    signal_type: str
    source_domain: SignalDomain
    target_domains: List[SignalDomain]
    routing_type: RoutingType
    priority_boost: int = 0  # Boost priority for cross-domain


@dataclass
class SignalSubscription:
    """A subscription to signals"""
    subscription_id: str
    subscriber_id: str
    signal_types: List[str]
    domains: List[SignalDomain]
    callback: Callable[[Signal], None]
    priority_filter: SignalPriority = SignalPriority.LOW


class GlobalSignalBus:
    """
    Global Signal Bus - The canonical routing layer (BB-DOM-002 Section 9)
    
    Acts as the central transport mechanism between:
    - ingestion systems
    - signal storage
    - domain intelligence systems
    - governance systems
    - simulation engines
    - reporting systems
    
    Architectural Rule:
    Domains may not exchange signals directly.
    All inter-domain signal movement must pass through the Global Signal Bus.
    """
    
    def __init__(self):
        # Live signal store
        self.live_signals: Dict[str, Signal] = {}
        
        # Signal history
        self.signal_history: List[Signal] = []
        self.max_history = 10000
        
        # Subscriptions
        self.subscriptions: List[SignalSubscription] = []
        
        # Routing rules
        self.routing_rules: List[SignalRoute] = []
        
        # Domain routing map (primary routes)
        self._setup_default_routes()
        
        # Signal statistics
        self.stats = {
            "total_signals": 0,
            "by_class": defaultdict(int),
            "by_domain": defaultdict(int),
            "by_priority": defaultdict(int),
            "routed_cross_domain": 0
        }
    
    def _setup_default_routes(self):
        """Setup default routing rules (BB-DOM-002 Section 10)"""
        
        # Finance -> Primary
        self.add_route(SignalRoute(
            route_id="finance_primary",
            signal_type="*",
            source_domain=SignalDomain.FINANCE,
            target_domains=[SignalDomain.FINANCE],
            routing_type=RoutingType.PRIMARY
        ))
        
        # Cross-domain: sleep debt -> Health, Career, Life Architecture
        self.add_route(SignalRoute(
            route_id="sleep_debt_secondary",
            signal_type="sleep_debt",
            source_domain=SignalDomain.HEALTH,
            target_domains=[SignalDomain.HEALTH, SignalDomain.CAREER, SignalDomain.LIFE_ARCHITECTURE],
            routing_type=RoutingType.SECONDARY,
            priority_boost=1
        ))
        
        # Cross-domain: market volatility -> Finance, Intelligence
        self.add_route(SignalRoute(
            route_id="market_volatility_secondary",
            signal_type="volatility*",
            source_domain=SignalDomain.FINANCE,
            target_domains=[SignalDomain.FINANCE, SignalDomain.INTELLIGENCE],
            routing_type=RoutingType.SECONDARY,
            priority_boost=1
        ))
        
        # Cross-domain: relationship conflict -> Relationships, Life Architecture
        self.add_route(SignalRoute(
            route_id="conflict_secondary",
            signal_type="conflict_event",
            source_domain=SignalDomain.RELATIONSHIPS,
            target_domains=[SignalDomain.RELATIONSHIPS, SignalDomain.LIFE_ARCHITECTURE],
            routing_type=RoutingType.SECONDARY,
            priority_boost=1
        ))
        
        # Global: severe stress -> all domains
        self.add_route(SignalRoute(
            route_id="severe_stress_global",
            signal_type="burnout_probability",
            source_domain=SignalDomain.HEALTH,
            target_domains=list(SignalDomain),
            routing_type=RoutingType.GLOBAL,
            priority_boost=2
        ))
        
        # Global: liquidity crisis -> all domains
        self.add_route(SignalRoute(
            route_id="liquidity_global",
            signal_type="liquidity_level",
            source_domain=SignalDomain.FINANCE,
            target_domains=list(SignalDomain),
            routing_type=RoutingType.GLOBAL,
            priority_boost=2
        ))
    
    def add_route(self, route: SignalRoute):
        """Add a routing rule"""
        self.routing_rules.append(route)
    
    def publish(self, signal: Signal) -> List[SignalDomain]:
        """
        Publish a signal to the bus.
        Returns list of domains the signal was routed to.
        """
        # Add to live store
        self.live_signals[signal.signal_id] = signal
        
        # Add to history
        self.signal_history.append(signal)
        if len(self.signal_history) > self.max_history:
            self.signal_history = self.signal_history[-self.max_history:]
        
        # Update stats
        self.stats["total_signals"] += 1
        self.stats["by_class"][signal.signal_class.value] += 1
        for domain in signal.domain_targets:
            self.stats["by_domain"][domain.value] += 1
        self.stats["by_priority"][signal.priority.value] += 1
        
        # Route signal
        routed_domains = self._route_signal(signal)
        
        # Notify subscribers
        self._notify_subscribers(signal)
        
        return routed_domains
    
    def _route_signal(self, signal: Signal) -> List[SignalDomain]:
        """Route signal to appropriate domains"""
        routed = set()
        
        # Find matching routes
        for rule in self.routing_rules:
            if self._matches_route(signal, rule):
                for domain in rule.target_domains:
                    if domain not in signal.domain_targets:
                        # Add cross-domain target
                        signal.domain_targets.append(domain)
                        routed.add(domain)
                        self.stats["routed_cross_domain"] += 1
        
        return list(routed)
    
    def _matches_route(self, signal: Signal, rule: SignalRoute) -> bool:
        """Check if signal matches routing rule"""
        # Check source domain
        if rule.source_domain != SignalDomain.ALL:
            # Signal should have this as primary domain
            # For now, assume signal's first domain is primary
            pass
        
        # Check signal type pattern
        if rule.signal_type == "*":
            return True
        elif "*" in rule.signal_type:
            prefix = rule.signal_type.replace("*", "")
            return signal.signal_type.startswith(prefix)
        else:
            return signal.signal_type == rule.signal_type
    
    def subscribe(
        self,
        subscriber_id: str,
        signal_types: List[str],
        domains: List[SignalDomain],
        callback: Callable[[Signal], None],
        priority_filter: SignalPriority = SignalPriority.LOW
    ) -> str:
        """Subscribe to signals"""
        subscription = SignalSubscription(
            subscription_id=f"sub_{len(self.subscriptions)}_{datetime.now().timestamp()}",
            subscriber_id=subscriber_id,
            signal_types=signal_types,
            domains=domains,
            callback=callback,
            priority_filter=priority_filter
        )
        self.subscriptions.append(subscription)
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from signals"""
        self.subscriptions = [
            s for s in self.subscriptions
            if s.subscription_id != subscription_id
        ]
        return True
    
    def _notify_subscribers(self, signal: Signal):
        """Notify relevant subscribers"""
        for sub in self.subscriptions:
            # Check if subscriber wants this signal
            if not self._matches_subscription(signal, sub):
                continue
            
            # Check priority filter
            priority_order = [SignalPriority.LOW, SignalPriority.MEDIUM, SignalPriority.HIGH, SignalPriority.CRITICAL]
            signal_prio_idx = priority_order.index(signal.priority)
            filter_prio_idx = priority_order.index(sub.priority_filter)
            
            if signal_prio_idx < filter_prio_idx:
                continue  # Signal priority too low
            
            try:
                sub.callback(signal)
            except Exception as e:
                # Log but don't fail
                pass
    
    def _matches_subscription(self, signal: Signal, subscription: SignalSubscription) -> bool:
        """Check if signal matches subscription"""
        # Check signal type
        if subscription.signal_types:
            matched = False
            for stype in subscription.signal_types:
                if stype == "*" or signal.signal_type.startswith(stype.replace("*", "")):
                    matched = True
                    break
            if not matched:
                return False
        
        # Check domain
        if subscription.domains:
            if not any(d in signal.domain_targets for d in subscription.domains):
                return False
        
        return True
    
    def get_signals(
        self,
        domain: SignalDomain = None,
        signal_class: SignalClass = None,
        priority: SignalPriority = None,
        limit: int = 100
    ) -> List[Signal]:
        """Query signals from the bus"""
        results = list(self.live_signals.values())
        
        if domain:
            results = [s for s in results if domain in s.domain_targets]
        
        if signal_class:
            results = [s for s in results if s.signal_class == signal_class]
        
        if priority:
            results = [s for s in results if s.priority == priority]
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda s: s.timestamp, reverse=True)
        
        return results[:limit]
    
    def get_latest(self, domain: SignalDomain, limit: int = 10) -> List[Signal]:
        """Get latest signals for a domain"""
        return self.get_signals(domain=domain, limit=limit)
    
    def get_expired_signals(self) -> List[Signal]:
        """Get signals that have expired"""
        return [s for s in self.live_signals.values() if s.is_expired()]
    
    def cleanup_expired(self):
        """Remove expired signals from live store"""
        expired = self.get_expired_signals()
        for signal in expired:
            del self.live_signals[signal.signal_id]
        return len(expired)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get signal bus statistics"""
        return {
            "total_signals": self.stats["total_signals"],
            "live_signals": len(self.live_signals),
            "by_class": dict(self.stats["by_class"]),
            "by_domain": dict(self.stats["by_domain"]),
            "by_priority": dict(self.stats["by_priority"]),
            "cross_domain_routes": self.stats["routed_cross_domain"],
            "active_subscriptions": len(self.subscriptions),
            "routing_rules": len(self.routing_rules)
        }


# ============== SIGNAL ESCALATOR ==============

class SignalEscalator:
    """
    Handles signal escalation to governors and executive council (BB-DOM-002 Section 18)
    """
    
    def __init__(self, signal_bus: GlobalSignalBus):
        self.signal_bus = signal_bus
        self.escalation_history: List[Dict[str, Any]] = []
    
    def should_escalate(self, signal: Signal) -> bool:
        """Determine if signal should be escalated"""
        # Critical priority always escalates
        if signal.priority == SignalPriority.CRITICAL:
            return True
        
        # High priority with cross-domain impact
        if signal.priority == SignalPriority.HIGH:
            if len(signal.domain_targets) > 1:
                return True
        
        # Derived risk signals
        if signal.signal_class == SignalClass.DERIVED:
            if any(tag in signal.tags for tag in ["risk", "warning", "alert"]):
                return True
        
        return False
    
    def escalate(self, signal: Signal, reason: str) -> Dict[str, Any]:
        """Escalate a signal"""
        escalation = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "target_domains": signal.domain_targets
        }
        
        self.escalation_history.append(escalation)
        
        return escalation
    
    def get_recent_escalations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent escalations"""
        return self.escalation_history[-limit:]


__all__ = [
    "GlobalSignalBus",
    "SignalRoute",
    "SignalSubscription",
    "SignalEscalator",
    "RoutingType",
]
