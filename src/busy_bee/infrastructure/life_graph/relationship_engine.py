"""
Relationship Engine

BB-INF-008: Life Signal Graph & Personal Digital Twin Engine

Discovers and manages relationships between signals in the life graph.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
import logging

from .graph_models import GraphNode, GraphEdge, NodeType, Domain, InfluenceType
from .life_signal_graph import LifeSignalGraph, get_life_graph


logger = logging.getLogger(__name__)


# Pre-defined relationship patterns
RELATIONSHIP_PATTERNS = {
    # Finance -> Health
    ("finance", "health"): [
        ("financial_stress", "sleep_quality", InfluenceType.CAUSAL_NEGATIVE, 0.6),
        ("financial_stress", "stress_level", InfluenceType.CAUSAL_POSITIVE, 0.7),
        ("income", "health_investment", InfluenceType.CAUSAL_POSITIVE, 0.5),
    ],
    
    # Finance -> Career
    ("finance", "career"): [
        ("income", "career_freedom", InfluenceType.CAUSAL_POSITIVE, 0.6),
        ("debt", "career_risk_tolerance", InfluenceType.CAUSAL_NEGATIVE, 0.5),
        ("savings_rate", "career_optionality", InfluenceType.CAUSAL_POSITIVE, 0.7),
    ],
    
    # Finance -> Life Architecture
    ("finance", "life_architecture"): [
        ("financial_freedom", "lifestyle_options", InfluenceType.CAUSAL_POSITIVE, 0.8),
        ("income", "living_situation", InfluenceType.CAUSAL_POSITIVE, 0.5),
        ("debt", "time_flexibility", InfluenceType.CAUSAL_NEGATIVE, 0.6),
    ],
    
    # Health -> Career
    ("health", "career"): [
        ("sleep_quality", "work_performance", InfluenceType.CAUSAL_POSITIVE, 0.7),
        ("energy_level", "productivity", InfluenceType.CAUSAL_POSITIVE, 0.8),
        ("stress_level", "career_satisfaction", InfluenceType.CAUSAL_NEGATIVE, 0.6),
        ("burnout_risk", "job_change_consideration", InfluenceType.CAUSAL_POSITIVE, 0.5),
    ],
    
    # Health -> Relationships
    ("health", "relationships"): [
        ("sleep_quality", "relationship_quality", InfluenceType.CAUSAL_POSITIVE, 0.5),
        ("energy_level", "social_energy", InfluenceType.CAUSAL_POSITIVE, 0.7),
        ("stress_level", "conflict_frequency", InfluenceType.CAUSAL_POSITIVE, 0.6),
    ],
    
    # Career -> Relationships
    ("career", "relationships"): [
        ("work_hours", "relationship_time", InfluenceType.CAUSAL_NEGATIVE, 0.7),
        ("career_stress", "relationship_stress", InfluenceType.CAUSAL_POSITIVE, 0.6),
        ("income", "relationship_resources", InfluenceType.CAUSAL_POSITIVE, 0.4),
    ],
    
    # Career -> Life Architecture
    ("career", "life_architecture"): [
        ("work_hours", "lifestyle_flexibility", InfluenceType.CAUSAL_NEGATIVE, 0.6),
        ("career_growth", "life_satisfaction", InfluenceType.CAUSAL_POSITIVE, 0.7),
        ("job_security", "life_planning_confidence", InfluenceType.CAUSAL_POSITIVE, 0.8),
    ],
    
    # Life Architecture -> Health
    ("life_architecture", "health"): [
        ("lifestyle_quality", "health_prioritization", InfluenceType.CAUSAL_POSITIVE, 0.5),
        ("schedule_control", "sleep_consistency", InfluenceType.CAUSAL_POSITIVE, 0.6),
        ("time_pressure", "exercise_time", InfluenceType.CAUSAL_NEGATIVE, 0.5),
    ],
}


class RelationshipEngine:
    """
    Discovers and manages relationships between signals in the life graph.
    
    Responsibilities:
    - Discover relationships from patterns
    - Infer relationships from data
    - Weight relationships based on evidence
    - Manage relationship lifecycle
    """
    
    def __init__(self, graph: LifeSignalGraph = None):
        self.graph = graph or get_life_graph()
        
        # Discovered relationships
        self._relationship_templates: Dict[str, List] = {}
        
        # Initialize patterns
        self._load_default_patterns()
    
    def _load_default_patterns(self) -> None:
        """Load default relationship patterns"""
        # Patterns are already loaded in RELATIONSHIP_PATTERNS
        pass
    
    def discover_relationships(
        self,
        source_node: GraphNode,
        target_node: GraphNode
    ) -> Optional[Tuple[InfluenceType, float]]:
        """
        Discover if there's a relationship between two nodes.
        
        Returns:
            Tuple of (influence_type, weight), or None if no relationship
        """
        # Check predefined patterns
        domain_key = (source_node.domain.value, target_node.domain.value)
        
        if domain_key in RELATIONSHIP_PATTERNS:
            patterns = RELATIONSHIP_PATTERNS[domain_key]
            
            for source_name, target_name, influence_type, weight in patterns:
                if source_name in source_node.name.lower() and target_name in target_node.name.lower():
                    return (influence_type, weight)
        
        # Check node type relationships
        if source_node.node_type == NodeType.SIGNAL and target_node.node_type == NodeType.STATE:
            # Signal influences state
            return (InfluenceType.CAUSAL_POSITIVE, 0.5)
        
        if source_node.node_type == NodeType.RISK and target_node.node_type == NodeType.STATE:
            # Risk affects state negatively
            return (InfluenceType.CAUSAL_NEGATIVE, 0.6)
        
        if source_node.node_type == NodeType.OPPORTUNITY and target_node.node_type == NodeType.STATE:
            # Opportunity enables positive state
            return (InfluenceType.ENABLES, 0.5)
        
        # Default: check if domains are the same
        if source_node.domain == target_node.domain:
            # Same domain might have correlation
            return (InfluenceType.CORRELATION, 0.3)
        
        return None
    
    def infer_edge_weight(
        self,
        source_node: GraphNode,
        target_node: GraphNode,
        historical_values: List[Tuple[Any, Any]] = None
    ) -> float:
        """
        Infer edge weight from data.
        
        Args:
            source_node: Source node
            target_node: Target node
            historical_values: List of (source_value, target_value) pairs
            
        Returns:
            Inferred weight (0-1)
        """
        if not historical_values or len(historical_values) < 3:
            # Not enough data, use default discovery
            discovered = self.discover_relationships(source_node, target_node)
            if discovered:
                return discovered[1]
            return 0.3
        
        # Calculate correlation
        try:
            values_a = [v[0] for v in historical_values if v[0] is not None and v[1] is not None]
            values_b = [v[1] for v in historical_values if v[0] is not None and v[1] is not None]
            
            if len(values_a) < 3:
                return 0.3
            
            # Simple correlation calculation
            mean_a = sum(values_a) / len(values_a)
            mean_b = sum(values_b) / len(values_b)
            
            covariance = sum((a - mean_a) * (b - mean_b) for a, b in zip(values_a, values_b))
            std_a = (sum((a - mean_a) ** 2 for a in values_a) ** 0.5)
            std_b = (sum((b - mean_b) ** 2 for b in values_b) ** 0.5)
            
            if std_a == 0 or std_b == 0:
                correlation = 0
            else:
                correlation = covariance / (std_a * std_b)
            
            # Convert correlation to weight
            return min(abs(correlation), 1.0)
            
        except Exception as e:
            logger.warning(f"Error inferring weight: {e}")
            return 0.3
    
    def build_cross_domain_relationships(self) -> List[str]:
        """
        Build relationships between domains based on known patterns.
        
        Returns:
            List of edge IDs created
        """
        edge_ids = []
        
        # Get all nodes by domain
        nodes_by_domain = {}
        for domain in Domain:
            nodes = self.graph.get_nodes_by_domain(domain)
            if nodes:
                nodes_by_domain[domain] = nodes
        
        # Apply patterns
        for (src_domain, tgt_domain), patterns in RELATIONSHIP_PATTERNS.items():
            if src_domain not in nodes_by_domain or tgt_domain not in nodes_by_domain:
                continue
            
            src_nodes = nodes_by_domain[Domain(src_domain)]
            tgt_nodes = nodes_by_domain[Domain(tgt_domain)]
            
            for src_node in src_nodes:
                for tgt_node in tgt_nodes:
                    # Check if relationship matches pattern
                    for src_name, tgt_name, influence_type, weight in patterns:
                        if src_name in src_node.name.lower() and tgt_name in tgt_node.name.lower():
                            # Check if edge already exists
                            existing = self.graph.get_edges_between(src_node.node_id, tgt_node.node_id)
                            if not existing:
                                edge_id = self.graph.add_edge(
                                    source_node_id=src_node.node_id,
                                    target_node_id=tgt_node.node_id,
                                    influence_type=influence_type,
                                    weight=weight,
                                    confidence=0.6,
                                    evidence=[f"pattern: {src_name} -> {tgt_name}"]
                                )
                                if edge_id:
                                    edge_ids.append(edge_id)
        
        logger.info(f"Built {len(edge_ids)} cross-domain relationships")
        return edge_ids
    
    def find_risk_propagation_paths(self, risk_node_id: str) -> List[str]:
        """
        Find how a risk propagates through the graph.
        
        Returns:
            List of node IDs that the risk affects
        """
        chains = self.graph.get_influence_chain(
            start_node_id=risk_node_id,
            depth=5,
            influence_types=[InfluenceType.CAUSAL_POSITIVE, InfluenceType.CAUSAL_NEGATIVE]
        )
        
        affected_nodes = set()
        for chain in chains:
            for node_id in chain.nodes:
                if node_id != risk_node_id:
                    affected_nodes.add(node_id)
        
        return list(affected_nodes)
    
    def find_opportunity_leverage(self, opportunity_node_id: str) -> List[Tuple[str, float]]:
        """
        Find the leverage points an opportunity can affect.
        
        Returns:
            List of (node_id, influence_weight) tuples
        """
        chains = self.graph.get_influence_chain(
            start_node_id=opportunity_node_id,
            depth=4,
            influence_types=[InfluenceType.CAUSAL_POSITIVE, InfluenceType.ENABLES]
        )
        
        leverage = []
        for chain in chains:
            for node_id, weight in zip(chain.nodes[1:], chain.edges):
                edge = self.graph.get_edge(weight)
                if edge:
                    leverage.append((node_id, edge.weight * chain.total_weight))
        
        return leverage
    
    def get_relationship_summary(self) -> Dict:
        """Get summary of relationships in the graph"""
        all_edges = self.graph.get_all_edges()
        
        by_type = {}
        for edge in all_edges:
            it = edge.influence_type.value
            by_type[it] = by_type.get(it, 0) + 1
        
        return {
            "total_relationships": len(all_edges),
            "by_influence_type": by_type,
            "graph_summary": self.graph.get_graph_summary()
        }


# Global instance
_relationship_engine: Optional[RelationshipEngine] = None


def get_relationship_engine() -> RelationshipEngine:
    """Get the global relationship engine"""
    global _relationship_engine
    if _relationship_engine is None:
        _relationship_engine = RelationshipEngine()
    return _relationship_engine


__all__ = [
    "RelationshipEngine",
    "RELATIONSHIP_PATTERNS",
    "get_relationship_engine",
]
