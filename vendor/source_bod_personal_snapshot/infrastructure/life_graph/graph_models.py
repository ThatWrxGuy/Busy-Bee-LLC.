"""
Life Signal Graph - Core Data Models

BB-INF-008: Life Signal Graph & Personal Digital Twin Engine

This module provides the core graph data structures for modeling
the user's life as an interconnected system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid


class NodeType(Enum):
    """Types of nodes in the life graph"""
    SIGNAL = "signal"           # Raw signal data
    STATE = "state"             # Derived state
    ASSET = "asset"             # Resources/assets
    OPPORTUNITY = "opportunity"  # Detected opportunities
    RISK = "risk"              # Detected threats
    STRATEGY = "strategy"       # Strategies under evaluation


class Domain(Enum):
    """Life domains"""
    FINANCE = "finance"
    HEALTH = "health"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    INTELLIGENCE = "intelligence"
    LIFE_ARCHITECTURE = "life_architecture"


class InfluenceType(Enum):
    """Types of causal influence"""
    CAUSAL_POSITIVE = "causal_positive"   # A causes B (positive)
    CAUSAL_NEGATIVE = "causal_negative"   # A causes B (negative)
    CORRELATION = "correlation"           # A correlates with B
    ENABLES = "enables"                   # A enables B
    CONSTRAINS = "constrains"             # A constrains B


@dataclass
class GraphNode:
    """
    A node in the Life Signal Graph.
    
    Represents a life entity - signal, state, asset, opportunity, risk, or strategy.
    """
    node_id: str
    node_type: NodeType
    name: str
    domain: Domain
    
    # Value
    value: Any = None
    value_type: str = "numeric"  # numeric, boolean, text, array
    
    # Quality
    confidence: float = 0.5
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Organization
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Relationships
    incoming_edges: List[str] = field(default_factory=list)  # edge IDs
    outgoing_edges: List[str] = field(default_factory=list)  # edge IDs
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "name": self.name,
            "domain": self.domain.value,
            "value": self.value,
            "value_type": self.value_type,
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
            "incoming_edges": self.incoming_edges,
            "outgoing_edges": self.outgoing_edges
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GraphNode':
        """Create from dictionary"""
        return cls(
            node_id=data["node_id"],
            node_type=NodeType(data["node_type"]),
            name=data["name"],
            domain=Domain(data["domain"]),
            value=data.get("value"),
            value_type=data.get("value_type", "numeric"),
            confidence=data.get("confidence", 0.5),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            incoming_edges=data.get("incoming_edges", []),
            outgoing_edges=data.get("outgoing_edges", [])
        )


@dataclass
class GraphEdge:
    """
    An edge in the Life Signal Graph.
    
    Represents a relationship or influence between nodes.
    """
    edge_id: str
    source_node_id: str
    target_node_id: str
    influence_type: InfluenceType
    
    # Strength
    weight: float = 0.5  # 0-1 strength of influence
    
    # Quality
    confidence: float = 0.5
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Evidence
    evidence: List[str] = field(default_factory=list)  # Supporting signals
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "influence_type": self.influence_type.value,
            "weight": self.weight,
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat(),
            "evidence": self.evidence,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GraphEdge':
        """Create from dictionary"""
        return cls(
            edge_id=data["edge_id"],
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            influence_type=InfluenceType(data["influence_type"]),
            weight=data.get("weight", 0.5),
            confidence=data.get("confidence", 0.5),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            evidence=data.get("evidence", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class InfluenceChain:
    """A chain of influence through the graph"""
    chain_id: str
    nodes: List[str]  # Node IDs in order
    edges: List[str]  # Edge IDs in order
    
    # Properties
    total_weight: float = 0.0
    confidence: float = 0.0
    influence_type: InfluenceType = InfluenceType.CAUSAL_POSITIVE
    
    def to_dict(self) -> Dict:
        return {
            "chain_id": self.chain_id,
            "nodes": self.nodes,
            "edges": self.edges,
            "total_weight": self.total_weight,
            "confidence": self.confidence,
            "influence_type": self.influence_type.value
        }


@dataclass
class GraphSnapshot:
    """A snapshot of the graph state at a point in time"""
    snapshot_id: str
    timestamp: datetime
    
    # Node/edge counts
    total_nodes: int
    total_edges: int
    
    # By type
    nodes_by_type: Dict[str, int]
    edges_by_type: Dict[str, int]
    
    # Domain breakdown
    nodes_by_domain: Dict[str, int]
    
    # Key metrics
    graph_density: float = 0.0
    avg_connectivity: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "nodes_by_type": self.nodes_by_type,
            "edges_by_type": self.edges_by_type,
            "nodes_by_domain": self.nodes_by_domain,
            "graph_density": self.graph_density,
            "avg_connectivity": self.avg_connectivity
        }


__all__ = [
    "NodeType",
    "Domain",
    "InfluenceType",
    "GraphNode",
    "GraphEdge",
    "InfluenceChain",
    "GraphSnapshot",
]
