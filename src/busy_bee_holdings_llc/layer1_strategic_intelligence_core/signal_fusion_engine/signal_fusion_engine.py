"""
Signal Fusion Engine - Fuses and correlates signals from multiple sources
Part of Layer 1: Strategic Intelligence Core
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class Signal:
    """A raw signal from a data source"""
    id: str
    source: str  # finance_api, health_app, career_platform, etc.
    signal_type: str  # opportunity_signal, risk_signal, trend, anomaly
    domain: str  # finance, health, career, relationships, intelligence, life_architecture
    title: str
    description: str
    raw_data: Dict[str, Any]
    strength: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


@dataclass
class FusedSignal:
    """A signal that has been fused from multiple sources"""
    id: str
    constituent_signals: List[str]  # Signal IDs that were fused
    signal_type: str
    domain: str
    title: str
    description: str
    aggregated_strength: float
    aggregated_confidence: float
    correlations: Dict[str, float]  # Correlation between sources
    created_at: datetime = field(default_factory=datetime.now)


class SignalFusionEngine:
    """
    Signal Fusion Engine fuses and correlates signals from multiple sources.
    
    Responsibilities:
    - Receive signals from all domains
    - Identify correlated signals
    - Fuse related signals into higher-quality insights
    - Route signals to appropriate processing
    """
    
    def __init__(self):
        self.raw_signals: List[Signal] = []
        self.fused_signals: List[FusedSignal] = []
        self.signal_index: Dict[str, List[str]] = defaultdict(list)  # domain -> signal_ids
    
    def ingest_signal(
        self,
        source: str,
        signal_type: str,
        domain: str,
        title: str,
        description: str,
        raw_data: Dict[str, Any],
        strength: float,
        confidence: float,
        tags: Optional[List[str]] = None
    ) -> Signal:
        """Ingest a new signal from a source"""
        signal = Signal(
            id=f"signal_{len(self.raw_signals) + 1}_{datetime.now().timestamp()}",
            source=source,
            signal_type=signal_type,
            domain=domain,
            title=title,
            description=description,
            raw_data=raw_data,
            strength=strength,
            confidence=confidence,
            tags=tags or []
        )
        
        self.raw_signals.append(signal)
        self.signal_index[domain].append(signal.id)
        
        return signal
    
    def fuse_signals(
        self,
        signal_ids: List[str],
        fused_title: str,
        fused_description: str
    ) -> Optional[FusedSignal]:
        """Fuse multiple signals into a single higher-quality signal"""
        signals = [s for s in self.raw_signals if s.id in signal_ids]
        
        if len(signals) < 2:
            return None
        
        # Aggregate strength and confidence
        aggregated_strength = sum(s.strength for s in signals) / len(signals)
        aggregated_confidence = sum(s.confidence for s in signals) / len(signals)
        
        # Calculate correlations between sources
        sources = list(set(s.source for s in signals))
        correlations = {s: 1.0 / len(sources) for s in sources}
        
        fused = FusedSignal(
            id=f"fused_{len(self.fused_signals) + 1}_{datetime.now().timestamp()}",
            constituent_signals=signal_ids,
            signal_type=signals[0].signal_type,
            domain=signals[0].domain,
            title=fused_title,
            description=fused_description,
            aggregated_strength=aggregated_strength,
            aggregated_confidence=aggregated_confidence,
            correlations=correlations
        )
        
        self.fused_signals.append(fused)
        return fused
    
    def auto_fuse_by_domain(self, domain: str, min_signals: int = 2) -> List[FusedSignal]:
        """Automatically fuse related signals within a domain"""
        domain_signals = [s for s in self.raw_signals if s.domain == domain]
        
        if len(domain_signals) < min_signals:
            return []
        
        # Group by signal type
        by_type = defaultdict(list)
        for signal in domain_signals:
            by_type[signal.signal_type].append(signal)
        
        fused = []
        for signal_type, signals in by_type.items():
            if len(signals) >= min_signals:
                fused_signal = self.fuse_signals(
                    signal_ids=[s.id for s in signals],
                    fused_title=f"Combined {signal_type} for {domain}",
                    fused_description=f"Fused {len(signals)} {signal_type} signals in {domain} domain"
                )
                if fused_signal:
                    fused.append(fused_signal)
        
        return fused
    
    def get_signals_by_domain(self, domain: str) -> List[Signal]:
        """Get all signals for a domain"""
        signal_ids = self.signal_index.get(domain, [])
        return [s for s in self.raw_signals if s.id in signal_ids]
    
    def get_signals_by_type(self, signal_type: str) -> List[Signal]:
        """Get all signals of a specific type"""
        return [s for s in self.raw_signals if s.signal_type == signal_type]
    
    def find_correlated_signals(self, signal_id: str, threshold: float = 0.5) -> List[Signal]:
        """Find signals correlated with a given signal"""
        source_signal = next((s for s in self.raw_signals if s.id == signal_id), None)
        
        if not source_signal:
            return []
        
        correlated = []
        
        # Find signals in same domain with similar strength
        for signal in self.raw_signals:
            if signal.id == signal_id:
                continue
            
            # Same domain
            if signal.domain == source_signal.domain:
                # Check strength similarity
                strength_diff = abs(signal.strength - source_signal.strength)
                if strength_diff <= (1 - threshold):
                    correlated.append(signal)
        
        return correlated
    
    def get_signal_summary(self) -> Dict[str, Any]:
        """Get a summary of all signals"""
        by_domain = defaultdict(int)
        by_type = defaultdict(int)
        by_source = defaultdict(int)
        
        for signal in self.raw_signals:
            by_domain[signal.domain] += 1
            by_type[signal.signal_type] += 1
            by_source[signal.source] += 1
        
        return {
            "total_raw_signals": len(self.raw_signals),
            "total_fused_signals": len(self.fused_signals),
            "by_domain": dict(by_domain),
            "by_type": dict(by_type),
            "by_source": dict(by_source),
            "summary_generated_at": datetime.now().isoformat()
        }
    
    def route_signals(
        self,
        domain: Optional[str] = None,
        signal_type: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> List[Signal]:
        """Route signals based on filters"""
        routed = self.raw_signals
        
        if domain:
            routed = [s for s in routed if s.domain == domain]
        
        if signal_type:
            routed = [s for s in routed if s.signal_type == signal_type]
        
        if min_confidence > 0:
            routed = [s for s in routed if s.confidence >= min_confidence]
        
        return routed
