"""
Edge Discovery Engine - Identifies emerging opportunities and edge cases
Part of Layer 1: Strategic Intelligence Core
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Edge:
    """An identified edge opportunity or risk"""
    id: str
    name: str
    description: str
    category: str  # opportunity, risk, trend, anomaly
    potential_impact: float  # -1.0 to 1.0 (negative = risk, positive = opportunity)
    confidence: float  # 0.0 - 1.0
    timeframe: str  # immediate, short_term, medium_term, long_term
    domain: str
    discovered_at: datetime
    status: str = "discovered"  # discovered, analyzed, integrated


class EdgeDiscoveryEngine:
    """
    Edge Discovery Engine identifies emerging opportunities and edge cases.
    
    Responsibilities:
    - Detect emerging trends
    - Identify edge opportunities
    - Surface anomalies
    """
    
    def __init__(self):
        self.edges: List[Edge] = []
        self.trend_indicators: Dict[str, Any] = {}
    
    def discover_edges(self, signals: List[Dict[str, Any]]) -> List[Edge]:
        """Discover edges from incoming signals"""
        discovered = []
        
        for signal in signals:
            edge = self._analyze_signal_for_edge(signal)
            if edge:
                discovered.append(edge)
                self.edges.append(edge)
        
        return discovered
    
    def _analyze_signal_for_edge(self, signal: Dict[str, Any]) -> Optional[Edge]:
        """Analyze a signal to determine if it represents an edge"""
        signal_type = signal.get("type", "")
        strength = signal.get("strength", 0.5)
        
        # Look for edge-indicating signals
        if signal_type in ["emerging_trend", "anomaly", "market_shift", "technology_shift"]:
            edge = Edge(
                id=f"edge_{len(self.edges) + 1}_{datetime.now().timestamp()}",
                name=signal.get("title", "Unnamed Edge"),
                description=signal.get("description", ""),
                category="opportunity" if strength > 0.5 else "risk",
                potential_impact=strength * (1 if strength > 0.5 else -1),
                confidence=signal.get("confidence", 0.5),
                timeframe=signal.get("timeframe", "short_term"),
                domain=signal.get("domain", "general"),
                discovered_at=datetime.now()
            )
            return edge
        
        return None
    
    def analyze_trends(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """Analyze current trends in the system"""
        edges = self.edges
        if domain:
            edges = [e for e in self.edges if e.domain == domain]
        
        opportunities = [e for e in edges if e.potential_impact > 0]
        risks = [e for e in edges if e.potential_impact < 0]
        
        return {
            "total_edges": len(edges),
            "opportunities": len(opportunities),
            "risks": len(risks),
            "high_impact_count": len([e for e in edges if abs(e.potential_impact) > 0.7]),
            "domains_covered": list(set(e.domain for e in edges)),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def get_strategic_edges(self, threshold: float = 0.6) -> List[Edge]:
        """Get edges with high potential impact above threshold"""
        return [
            e for e in self.edges 
            if abs(e.potential_impact) >= threshold
        ]
    
    def update_edge_status(self, edge_id: str, status: str) -> bool:
        """Update the status of an edge"""
        for edge in self.edges:
            if edge.id == edge_id:
                edge.status = status
                return True
        return False
