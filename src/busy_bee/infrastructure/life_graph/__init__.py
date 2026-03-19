"""
Life Signal Graph

BB-INF-008: Life Signal Graph & Personal Digital Twin Engine

This module provides the infrastructure for modeling the user's life
as an interconnected graph, enabling cross-domain analysis and
leverage discovery.
"""

from .graph_models import (
    NodeType,
    Domain,
    InfluenceType,
    GraphNode,
    GraphEdge,
    InfluenceChain,
    GraphSnapshot,
)

from .life_signal_graph import (
    LifeSignalGraph,
    get_life_graph,
)

from .relationship_engine import (
    RelationshipEngine,
    RELATIONSHIP_PATTERNS,
    get_relationship_engine,
)

from .graph_builder import (
    GraphBuilder,
    BuildResult,
    get_graph_builder,
)

from .graph_query_engine import (
    GraphQueryEngine,
    LeveragePoint,
    RiskCluster,
    get_graph_query_engine,
)


__all__ = [
    # Models
    "NodeType",
    "Domain",
    "InfluenceType",
    "GraphNode",
    "GraphEdge",
    "InfluenceChain",
    "GraphSnapshot",
    
    # Graph
    "LifeSignalGraph",
    "get_life_graph",
    
    # Relationship Engine
    "RelationshipEngine",
    "RELATIONSHIP_PATTERNS",
    "get_relationship_engine",
    
    # Graph Builder
    "GraphBuilder",
    "BuildResult",
    "get_graph_builder",
    
    # Query Engine
    "GraphQueryEngine",
    "LeveragePoint",
    "RiskCluster",
    "get_graph_query_engine",
]
