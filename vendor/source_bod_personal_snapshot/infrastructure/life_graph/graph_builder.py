"""
Graph Builder

BB-INF-008: Life Signal Graph & Personal Digital Twin Engine

Converts signals and data into graph nodes and edges.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from .graph_models import GraphNode, GraphEdge, NodeType, Domain, InfluenceType
from .life_signal_graph import LifeSignalGraph, get_life_graph
from .relationship_engine import RelationshipEngine, get_relationship_engine


logger = logging.getLogger(__name__)


@dataclass
class BuildResult:
    """Result of a graph build operation"""
    nodes_created: int
    edges_created: int
    nodes_updated: int
    errors: List[str]


class GraphBuilder:
    """
    Builds the life signal graph from various data sources.
    
    Pipeline:
    1. Convert signals to nodes
    2. Create state nodes
    3. Discover relationships
    4. Create edges
    5. Update existing nodes
    """
    
    def __init__(
        self,
        graph: LifeSignalGraph = None,
        relationship_engine: RelationshipEngine = None
    ):
        self.graph = graph or get_life_graph()
        self.relationship_engine = relationship_engine or get_relationship_engine()
        
        # Track node mappings
        self._signal_node_map: Dict[str, str] = {}  # signal_id -> node_id
    
    def build_from_signals(
        self,
        signals: List[Dict],
        domain: Domain = None
    ) -> BuildResult:
        """
        Build graph nodes from signals.
        
        Args:
            signals: List of signal dictionaries
            domain: Domain to assign (or infer from signal)
            
        Returns:
            BuildResult with statistics
        """
        result = BuildResult(
            nodes_created=0,
            edges_created=0,
            nodes_updated=0,
            errors=[]
        )
        
        for signal in signals:
            try:
                # Determine domain
                sig_domain = domain
                if not sig_domain:
                    domain_str = signal.get("domain", "general")
                    try:
                        sig_domain = Domain(domain_str)
                    except ValueError:
                        sig_domain = Domain.GENERAL
                
                # Determine node type
                node_type = NodeType.SIGNAL
                
                # Create node
                node_id = self.graph.add_node(
                    node_type=node_type,
                    name=signal.get("metric_name", "unknown"),
                    domain=sig_domain,
                    value=signal.get("metric_value"),
                    confidence=signal.get("confidence", 0.5),
                    tags=signal.get("tags", []),
                    metadata={
                        "source": signal.get("source"),
                        "timestamp": signal.get("timestamp")
                    }
                )
                
                result.nodes_created += 1
                self._signal_node_map[signal.get("signal_id", "")] = node_id
                
            except Exception as e:
                logger.error(f"Error building node from signal: {e}")
                result.errors.append(str(e))
        
        return result
    
    def create_state_node(
        self,
        name: str,
        domain: Domain,
        value: Any,
        confidence: float = 0.5,
        source_nodes: List[str] = None
    ) -> Optional[str]:
        """
        Create a derived state node.
        
        Args:
            name: State name
            domain: Domain
            value: Computed state value
            confidence: Confidence in state
            source_nodes: Source nodes that contributed to this state
            
        Returns:
            node_id or None
        """
        node_id = self.graph.add_node(
            node_type=NodeType.STATE,
            name=name,
            domain=domain,
            value=value,
            confidence=confidence,
            metadata={"derived_from": source_nodes or []}
        )
        
        # Create edges from source nodes
        if source_nodes:
            for src_id in source_nodes:
                self.graph.add_edge(
                    source_node_id=src_id,
                    target_node_id=node_id,
                    influence_type=InfluenceType.CAUSAL_POSITIVE,
                    weight=0.5,
                    confidence=confidence
                )
        
        return node_id
    
    def create_risk_node(
        self,
        name: str,
        domain: Domain,
        severity: float,
        description: str = "",
        source_nodes: List[str] = None
    ) -> Optional[str]:
        """Create a risk node"""
        node_id = self.graph.add_node(
            node_type=NodeType.RISK,
            name=name,
            domain=domain,
            value=severity,
            confidence=0.7,
            tags=["risk", description],
            metadata={
                "description": description,
                "derived_from": source_nodes or []
            }
        )
        
        if source_nodes:
            for src_id in source_nodes:
                self.graph.add_edge(
                    source_node_id=src_id,
                    target_node_id=node_id,
                    influence_type=InfluenceType.CAUSAL_POSITIVE,
                    weight=severity,
                    confidence=0.6
                )
        
        return node_id
    
    def create_opportunity_node(
        self,
        name: str,
        domain: Domain,
        potential: float,
        description: str = "",
        source_nodes: List[str] = None
    ) -> Optional[str]:
        """Create an opportunity node"""
        node_id = self.graph.add_node(
            node_type=NodeType.OPPORTUNITY,
            name=name,
            domain=domain,
            value=potential,
            confidence=0.6,
            tags=["opportunity", description],
            metadata={
                "description": description,
                "derived_from": source_nodes or []
            }
        )
        
        if source_nodes:
            for src_id in source_nodes:
                self.graph.add_edge(
                    source_node_id=src_id,
                    target_node_id=node_id,
                    influence_type=InfluenceType.ENABLES,
                    weight=potential,
                    confidence=0.5
                )
        
        return node_id
    
    def create_strategy_node(
        self,
        name: str,
        domain: Domain,
        expected_impact: float,
        risk_level: float,
        target_nodes: List[str] = None
    ) -> Optional[str]:
        """Create a strategy node"""
        node_id = self.graph.add_node(
            node_type=NodeType.STRATEGY,
            name=name,
            domain=domain,
            value=expected_impact,
            confidence=1.0 - risk_level,
            tags=["strategy"],
            metadata={
                "expected_impact": expected_impact,
                "risk_level": risk_level,
                "target_nodes": target_nodes or []
            }
        )
        
        # Strategy influences target nodes
        if target_nodes:
            for tgt_id in target_nodes:
                self.graph.add_edge(
                    source_node_id=node_id,
                    target_node_id=tgt_id,
                    influence_type=InfluenceType.CAUSAL_POSITIVE,
                    weight=expected_impact,
                    confidence=0.7
                )
        
        return node_id
    
    def build_derived_states(self) -> int:
        """
        Build common derived state nodes from existing signal nodes.
        
        Returns:
            Number of state nodes created
        """
        states_created = 0
        
        # Financial derived states
        finance_nodes = self.graph.get_nodes_by_domain(Domain.FINANCE)
        finance_signal_values = {}
        for node in finance_nodes:
            if node.node_type == NodeType.SIGNAL:
                finance_signal_values[node.name] = node.value
        
        # Check for financial stress indicators
        if finance_signal_values:
            # Check for debt
            debt = finance_signal_values.get("debt", 0)
            income = finance_signal_values.get("income", 0)
            
            if debt and income:
                debt_to_income = debt / income if income > 0 else 0
                if debt_to_income > 0.3:
                    self.create_state_node(
                        name="financial_stress",
                        domain=Domain.FINANCE,
                        value=debt_to_income,
                        confidence=0.7,
                        source_nodes=[n.node_id for n in finance_nodes]
                    )
                    states_created += 1
        
        # Health derived states
        health_nodes = self.graph.get_nodes_by_domain(Domain.HEALTH)
        health_signal_values = {}
        for node in health_nodes:
            if node.node_type == NodeType.SIGNAL:
                health_signal_values[node.name] = node.value
        
        # Check for sleep deficit
        sleep = health_signal_values.get("sleep_hours", 8)
        if sleep and sleep < 7:
            deficit = 7 - sleep
            self.create_state_node(
                name="sleep_deficit",
                domain=Domain.HEALTH,
                value=deficit,
                confidence=0.8,
                source_nodes=[n.node_id for n in health_nodes]
            )
            states_created += 1
        
        # Career derived states
        career_nodes = self.graph.get_nodes_by_domain(Domain.CAREER)
        
        return states_created
    
    def build_all_relationships(self) -> int:
        """
        Build all relationships based on patterns and existing nodes.
        
        Returns:
            Number of edges created
        """
        return len(self.relationship_engine.build_cross_domain_relationships())
    
    def full_build(
        self,
        signals: List[Dict] = None,
        build_states: bool = True,
        build_relationships: bool = True
    ) -> BuildResult:
        """
        Perform a full graph build.
        
        Args:
            signals: Signals to add
            build_states: Whether to create derived states
            build_relationships: Whether to create relationships
            
        Returns:
            BuildResult with all statistics
        """
        result = BuildResult(0, 0, 0, [])
        
        # Build from signals
        if signals:
            signal_result = self.build_from_signals(signals)
            result.nodes_created += signal_result.nodes_created
            result.errors.extend(signal_result.errors)
        
        # Build derived states
        if build_states:
            states_count = self.build_derived_states()
            result.nodes_created += states_count
        
        # Build relationships
        if build_relationships:
            edges_count = self.build_all_relationships()
            result.edges_created += edges_count
        
        # Create snapshot
        self.graph.create_snapshot()
        
        return result


# Global instance
_graph_builder: Optional[GraphBuilder] = None


def get_graph_builder() -> GraphBuilder:
    """Get the global graph builder"""
    global _graph_builder
    if _graph_builder is None:
        _graph_builder = GraphBuilder()
    return _graph_builder


__all__ = [
    "GraphBuilder",
    "BuildResult",
    "get_graph_builder",
]
