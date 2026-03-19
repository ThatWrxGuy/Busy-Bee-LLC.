"""
Life Signal Graph

BB-INF-008: Life Signal Graph & Personal Digital Twin Engine

The core graph data structure for modeling the user's life as an interconnected system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
import threading
import uuid
import logging

from .graph_models import (
    GraphNode, GraphEdge, GraphSnapshot,
    NodeType, Domain, InfluenceType, InfluenceChain
)


logger = logging.getLogger(__name__)


class LifeSignalGraph:
    """
    The Life Signal Graph models the user's life as an interconnected graph.
    
    Features:
    - Node and edge management
    - Influence chain traversal
    - Graph queries
    - Snapshot and history
    - Thread-safe operations
    """
    
    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}
        self._node_index: Dict[str, Set[str]] = {}  # domain -> node_ids
        self._type_index: Dict[str, Set[str]] = {}  # node_type -> node_ids
        
        # Snapshots
        self._snapshots: List[GraphSnapshot] = []
        
        # Lock for thread safety
        self._lock = threading.RLock()
    
    # ============== Node Operations ==============
    
    def add_node(
        self,
        node_type: NodeType,
        name: str,
        domain: Domain,
        value: Any = None,
        confidence: float = 0.5,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Add a node to the graph.
        
        Returns:
            str: The node_id of the added node
        """
        with self._lock:
            node_id = f"node_{uuid.uuid4().hex[:12]}"
            
            node = GraphNode(
                node_id=node_id,
                node_type=node_type,
                name=name,
                domain=domain,
                value=value,
                confidence=confidence,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            self._nodes[node_id] = node
            
            # Update indices
            domain_key = domain.value
            if domain_key not in self._node_index:
                self._node_index[domain_key] = set()
            self._node_index[domain_key].add(node_id)
            
            type_key = node_type.value
            if type_key not in self._type_index:
                self._type_index[type_key] = set()
            self._type_index[type_key].add(node_id)
            
            logger.debug(f"Added node: {name} ({node_id})")
            return node_id
    
    def update_node(
        self,
        node_id: str,
        value: Any = None,
        confidence: float = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update a node's value"""
        with self._lock:
            if node_id not in self._nodes:
                return False
            
            node = self._nodes[node_id]
            
            if value is not None:
                node.value = value
            if confidence is not None:
                node.confidence = confidence
            if metadata:
                node.metadata.update(metadata)
            
            node.last_updated = datetime.now()
            return True
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID"""
        return self._nodes.get(node_id)
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node and its edges"""
        with self._lock:
            if node_id not in self._nodes:
                return False
            
            node = self._nodes[node_id]
            
            # Remove connected edges
            for edge_id in node.incoming_edges + node.outgoing_edges:
                if edge_id in self._edges:
                    edge = self._edges[edge_id]
                    # Remove from other node
                    other_id = edge.source_node_id if edge.target_node_id == node_id else edge.target_node_id
                    if other_id in self._nodes:
                        other_node = self._nodes[other_id]
                        if edge_id in other_node.incoming_edges:
                            other_node.incoming_edges.remove(edge_id)
                        if edge_id in other_node.outgoing_edges:
                            other_node.outgoing_edges.remove(edge_id)
                    del self._edges[edge_id]
            
            # Remove from indices
            domain_key = node.domain.value
            if domain_key in self._node_index:
                self._node_index[domain_key].discard(node_id)
            
            type_key = node.node_type.value
            if type_key in self._type_index:
                self._type_index[type_key].discard(node_id)
            
            del self._nodes[node_id]
            return True
    
    def get_nodes_by_domain(self, domain: Domain) -> List[GraphNode]:
        """Get all nodes in a domain"""
        with self._lock:
            domain_key = domain.value
            if domain_key not in self._node_index:
                return []
            return [self._nodes[nid] for nid in self._node_index[domain_key] if nid in self._nodes]
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        """Get all nodes of a type"""
        with self._lock:
            type_key = node_type.value
            if type_key not in self._type_index:
                return []
            return [self._nodes[nid] for nid in self._type_index[type_key] if nid in self._nodes]
    
    # ============== Edge Operations ==============
    
    def add_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        influence_type: InfluenceType,
        weight: float = 0.5,
        confidence: float = 0.5,
        evidence: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Add an edge between nodes.
        
        Returns:
            str: The edge_id, or None if nodes don't exist
        """
        with self._lock:
            # Verify nodes exist
            if source_node_id not in self._nodes or target_node_id not in self._nodes:
                return None
            
            edge_id = f"edge_{uuid.uuid4().hex[:12]}"
            
            edge = GraphEdge(
                edge_id=edge_id,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                influence_type=influence_type,
                weight=weight,
                confidence=confidence,
                evidence=evidence or [],
                metadata=metadata or {}
            )
            
            self._edges[edge_id] = edge
            
            # Update node edge lists
            self._nodes[source_node_id].outgoing_edges.append(edge_id)
            self._nodes[target_node_id].incoming_edges.append(edge_id)
            
            logger.debug(f"Added edge: {source_node_id} -> {target_node_id}")
            return edge_id
    
    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """Get an edge by ID"""
        return self._edges.get(edge_id)
    
    def remove_edge(self, edge_id: str) -> bool:
        """Remove an edge"""
        with self._lock:
            if edge_id not in self._edges:
                return False
            
            edge = self._edges[edge_id]
            
            # Remove from nodes
            for node_id in [edge.source_node_id, edge.target_node_id]:
                if node_id in self._nodes:
                    node = self._nodes[node_id]
                    if edge_id in node.incoming_edges:
                        node.incoming_edges.remove(edge_id)
                    if edge_id in node.outgoing_edges:
                        node.outgoing_edges.remove(edge_id)
            
            del self._edges[edge_id]
            return True
    
    def get_edges_between(self, node_id_a: str, node_id_b: str) -> List[GraphEdge]:
        """Get all edges between two nodes"""
        return [
            e for e in self._edges.values()
            if (e.source_node_id == node_id_a and e.target_node_id == node_id_b)
            or (e.source_node_id == node_id_b and e.target_node_id == node_id_a)
        ]
    
    # ============== Graph Queries ==============
    
    def get_influence_chain(
        self,
        start_node_id: str,
        depth: int = 3,
        influence_types: List[InfluenceType] = None
    ) -> List[InfluenceChain]:
        """
        Get chains of influence from a starting node.
        
        Args:
            start_node_id: Starting node
            depth: Maximum depth to traverse
            influence_types: Filter by influence types
            
        Returns:
            List of influence chains
        """
        with self._lock:
            chains = []
            
            def traverse(
                current_node_id: str,
                current_depth: int,
                visited: Set[str],
                node_ids: List[str],
                edge_ids: List[str]
            ):
                if current_depth >= depth:
                    return
                
                if current_node_id in visited:
                    return
                
                visited.add(current_node_id)
                node_ids.append(current_node_id)
                
                # Get outgoing edges
                node = self._nodes.get(current_node_id)
                if not node:
                    return
                
                for edge_id in node.outgoing_edges:
                    edge = self._edges.get(edge_id)
                    if not edge:
                        continue
                    
                    if influence_types and edge.influence_type not in influence_types:
                        continue
                    
                    edge_ids.append(edge_id)
                    
                    # Continue traversal
                    traverse(
                        edge.target_node_id,
                        current_depth + 1,
                        visited.copy(),
                        node_ids.copy(),
                        edge_ids.copy()
                    )
                    
                    # Record chain if deep enough
                    if len(node_ids) >= 2:
                        chain = InfluenceChain(
                            chain_id=f"chain_{uuid.uuid4().hex[:8]}",
                            nodes=node_ids.copy(),
                            edges=edge_ids.copy(),
                            total_weight=sum(self._edges[e].weight for e in edge_ids),
                            confidence=sum(self._edges[e].confidence for e in edge_ids) / len(edge_ids) if edge_ids else 0,
                            influence_type=influence_types[0] if influence_types else InfluenceType.CAUSAL_POSITIVE
                        )
                        chains.append(chain)
            
            traverse(start_node_id, 0, set(), [], [])
            return chains
    
    def get_influences_on(self, node_id: str) -> List[Tuple[GraphNode, GraphEdge]]:
        """Get all nodes that influence a given node"""
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                return []
            
            influences = []
            for edge_id in node.incoming_edges:
                edge = self._edges.get(edge_id)
                if edge:
                    source = self._nodes.get(edge.source_node_id)
                    if source:
                        influences.append((source, edge))
            return influences
    
    def get_influences_from(self, node_id: str) -> List[Tuple[GraphNode, GraphEdge]]:
        """Get all nodes that a given node influences"""
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                return []
            
            influences = []
            for edge_id in node.outgoing_edges:
                edge = self._edges.get(edge_id)
                if edge:
                    target = self._nodes.get(edge.target_node_id)
                    if target:
                        influences.append((target, edge))
            return influences
    
    # ============== Graph Analysis ==============
    
    def get_graph_density(self) -> float:
        """Calculate graph density"""
        with self._lock:
            n = len(self._nodes)
            if n < 2:
                return 0.0
            max_edges = n * (n - 1)
            return len(self._edges) / max_edges
    
    def get_node_connectivity(self, node_id: str) -> int:
        """Get the number of connections for a node"""
        node = self._nodes.get(node_id)
        if not node:
            return 0
        return len(node.incoming_edges) + len(node.outgoing_edges)
    
    def get_most_connected_nodes(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most connected nodes"""
        with self._lock:
            connections = [
                (node_id, self.get_node_connectivity(node_id))
                for node_id in self._nodes
            ]
            connections.sort(key=lambda x: x[1], reverse=True)
            return connections[:limit]
    
    def find_clusters(self) -> List[Set[str]]:
        """Find connected components (clusters) in the graph"""
        with self._lock:
            visited = set()
            clusters = []
            
            def dfs(node_id: str, cluster: Set[str]):
                visited.add(node_id)
                cluster.add(node_id)
                
                node = self._nodes.get(node_id)
                if not node:
                    return
                
                for edge_id in node.incoming_edges + node.outgoing_edges:
                    edge = self._edges.get(edge_id)
                    if not edge:
                        continue
                    
                    other_id = edge.source_node_id if edge.target_node_id == node_id else edge.target_node_id
                    if other_id not in visited:
                        dfs(other_id, cluster)
            
            for node_id in self._nodes:
                if node_id not in visited:
                    cluster = set()
                    dfs(node_id, cluster)
                    clusters.append(cluster)
            
            return clusters
    
    # ============== Snapshots ==============
    
    def create_snapshot(self) -> str:
        """Create a snapshot of the current graph state"""
        with self._lock:
            snapshot_id = f"snap_{uuid.uuid4().hex[:8]}"
            
            # Count by type
            nodes_by_type = {}
            for node_type in NodeType:
                count = len(self._type_index.get(node_type.value, set()))
                nodes_by_type[node_type.value] = count
            
            edges_by_type = {}
            for inf_type in InfluenceType:
                count = sum(1 for e in self._edges.values() if e.influence_type == inf_type)
                edges_by_type[inf_type.value] = count
            
            # Count by domain
            nodes_by_domain = {}
            for domain in Domain:
                count = len(self._node_index.get(domain.value, set()))
                nodes_by_domain[domain.value] = count
            
            snapshot = GraphSnapshot(
                snapshot_id=snapshot_id,
                timestamp=datetime.now(),
                total_nodes=len(self._nodes),
                total_edges=len(self._edges),
                nodes_by_type=nodes_by_type,
                edges_by_type=edges_by_type,
                nodes_by_domain=nodes_by_domain,
                graph_density=self.get_graph_density(),
                avg_connectivity=sum(self.get_node_connectivity(n) for n in self._nodes) / len(self._nodes) if self._nodes else 0
            )
            
            self._snapshots.append(snapshot)
            
            # Keep last 50 snapshots
            if len(self._snapshots) > 50:
                self._snapshots = self._snapshots[-50:]
            
            return snapshot_id
    
    def get_snapshots(self, limit: int = 10) -> List[GraphSnapshot]:
        """Get recent snapshots"""
        return self._snapshots[-limit:]
    
    # ============== Graph Info ==============
    
    def get_graph_summary(self) -> Dict:
        """Get summary of the graph"""
        with self._lock:
            return {
                "total_nodes": len(self._nodes),
                "total_edges": len(self._edges),
                "nodes_by_type": {
                    nt.value: len(self._type_index.get(nt.value, set()))
                    for nt in NodeType
                },
                "nodes_by_domain": {
                    d.value: len(self._node_index.get(d.value, set()))
                    for d in Domain
                },
                "edges_by_influence": {
                    it.value: sum(1 for e in self._edges.values() if e.influence_type == it)
                    for it in InfluenceType
                },
                "graph_density": self.get_graph_density(),
                "snapshots": len(self._snapshots)
            }
    
    def get_all_nodes(self) -> List[GraphNode]:
        """Get all nodes"""
        return list(self._nodes.values())
    
    def get_all_edges(self) -> List[GraphEdge]:
        """Get all edges"""
        return list(self._edges.values())
    
    def clear(self) -> None:
        """Clear the graph"""
        with self._lock:
            self._nodes.clear()
            self._edges.clear()
            self._node_index.clear()
            self._type_index.clear()


# Global instance
_global_graph: Optional[LifeSignalGraph] = None


def get_life_graph() -> LifeSignalGraph:
    """Get the global life signal graph"""
    global _global_graph
    if _global_graph is None:
        _global_graph = LifeSignalGraph()
    return _global_graph


__all__ = [
    "LifeSignalGraph",
    "get_life_graph",
]
