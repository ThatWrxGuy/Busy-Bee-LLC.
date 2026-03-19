"""
Signal System - Manages signal routing between agents
Infrastructure Layer
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict


class SignalPriority(Enum):
    """Signal priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class SignalStatus(Enum):
    """Signal processing status"""
    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROUTED = "routed"


@dataclass
class Signal:
    """A signal in the system"""
    id: str
    source: str  # Which agent/component sent it
    signal_type: str
    domain: str
    payload: Dict[str, Any]
    priority: SignalPriority = SignalPriority.NORMAL
    status: SignalStatus = SignalStatus.RECEIVED
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SignalRoute:
    """A route for signal delivery"""
    id: str
    signal_type: str
    domain: str
    target: str  # Agent or component ID
    priority: SignalPriority


class SignalSystem:
    """
    Signal System manages signal routing between agents.
    
    All state must flow through this system.
    
    Pipeline:
    Signal → Detection → Analysis → Strategy Generation → Simulation → Risk Evaluation → Council Review → Executive Brief
    """
    
    def __init__(self):
        self.signals: List[Signal] = []
        self.routes: List[SignalRoute] = []
        self.handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.signal_queue: List[str] = []  # Signal IDs in priority order
        self.processing_history: List[Dict[str, Any]] = []
    
    def emit(
        self,
        source: str,
        signal_type: str,
        domain: str,
        payload: Dict[str, Any],
        priority: SignalPriority = SignalPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Signal:
        """Emit a new signal"""
        signal = Signal(
            id=f"sig_{len(self.signals) + 1}_{datetime.now().timestamp()}",
            source=source,
            signal_type=signal_type,
            domain=domain,
            payload=payload,
            priority=priority,
            metadata=metadata or {}
        )
        
        self.signals.append(signal)
        self._update_queue(signal)
        
        # Notify handlers
        self._notify_handlers(signal)
        
        return signal
    
    def route(
        self,
        signal_id: str,
        target: str
    ) -> bool:
        """Manually route a signal to a target"""
        signal = self.get_signal(signal_id)
        
        if not signal:
            return False
        
        signal.status = SignalStatus.ROUTED
        
        route = SignalRoute(
            id=f"route_{len(self.routes) + 1}",
            signal_type=signal.signal_type,
            domain=signal.domain,
            target=target,
            priority=signal.priority
        )
        
        self.routes.append(route)
        
        self.processing_history.append({
            "signal_id": signal_id,
            "action": "routed",
            "target": target,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def register_handler(
        self,
        signal_type: str,
        handler: Callable[[Signal], None]
    ):
        """Register a handler for a signal type"""
        self.handlers[signal_type].append(handler)
    
    def _notify_handlers(self, signal: Signal):
        """Notify relevant handlers of a new signal"""
        handlers = self.handlers.get(signal.signal_type, [])
        
        for handler in handlers:
            try:
                handler(signal)
            except Exception as e:
                self.processing_history.append({
                    "signal_id": signal.id,
                    "action": "handler_error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def _update_queue(self, signal: Signal):
        """Update the signal queue based on priority"""
        # Insert based on priority
        inserted = False
        
        for i, sig_id in enumerate(self.signal_queue):
            sig = next((s for s in self.signals if s.id == sig_id), None)
            if sig and signal.priority.value > sig.priority.value:
                self.signal_queue.insert(i, signal.id)
                inserted = True
                break
        
        if not inserted:
            self.signal_queue.append(signal.id)
    
    def get_signal(self, signal_id: str) -> Optional[Signal]:
        """Get a signal by ID"""
        return next((s for s in self.signals if s.id == signal_id), None)
    
    def get_signals_by_domain(self, domain: str) -> List[Signal]:
        """Get all signals for a domain"""
        return [s for s in self.signals if s.domain == domain]
    
    def get_signals_by_type(self, signal_type: str) -> List[Signal]:
        """Get all signals of a type"""
        return [s for s in self.signals if s.signal_type == signal_type]
    
    def get_pending_signals(self) -> List[Signal]:
        """Get pending signals"""
        pending = []
        for sig_id in self.signal_queue:
            sig = self.get_signal(sig_id)
            if sig and sig.status == SignalStatus.RECEIVED:
                pending.append(sig)
        return pending
    
    def process_signal(self, signal_id: str) -> bool:
        """Mark a signal as processing"""
        signal = self.get_signal(signal_id)
        
        if not signal:
            return False
        
        signal.status = SignalStatus.PROCESSING
        
        self.processing_history.append({
            "signal_id": signal_id,
            "action": "processing",
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def complete_signal(self, signal_id: str) -> bool:
        """Mark a signal as completed"""
        signal = self.get_signal(signal_id)
        
        if not signal:
            return False
        
        signal.status = SignalStatus.COMPLETED
        
        self.processing_history.append({
            "signal_id": signal_id,
            "action": "completed",
            "timestamp": datetime.now().isoformat()
        })
        
        # Remove from queue
        if signal_id in self.signal_queue:
            self.signal_queue.remove(signal_id)
        
        return True
    
    def get_signal_summary(self) -> Dict[str, Any]:
        """Get signal system summary"""
        return {
            "total_signals": len(self.signals),
            "pending": len([s for s in self.signals if s.status == SignalStatus.RECEIVED]),
            "processing": len([s for s in self.signals if s.status == SignalStatus.PROCESSING]),
            "completed": len([s for s in self.signals if s.status == SignalStatus.COMPLETED]),
            "by_domain": {
                domain: len([s for s in self.signals if s.domain == domain])
                for domain in set(s.domain for s in self.signals)
            },
            "by_type": {
                stype: len([s for s in self.signals if s.signal_type == stype])
                for stype in set(s.signal_type for s in self.signals)
            }
        }
