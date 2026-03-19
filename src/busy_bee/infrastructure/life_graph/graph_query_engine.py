"""
Graph Query Engine

BB-INF-008: Life Signal Graph & Personal Digital Twin Engine

Provides query capabilities for the life signal graph.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
import logging

from .graph_models import GraphNode, GraphEdge, NodeType, Domain, InfluenceType
from .life_signal_graph import LifeSignalGraph, get_life_graph


logger = logging.getLogger(__name__)


@dataclass
class LeveragePoint:
    """A high-leverage node in the graph"""
    node_id: str
    name: str
    domain: Domain
    reach: int  # How many nodes it influences
    leverage_score: float
    
    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "domain": self.domain.value,
            "reach": self.reach,
            "leverage_score": self.leverage_score
        }


@dataclass
class RiskCluster:
    """A cluster of related risks"""
    cluster_id: str
    risk_nodes: List[str]
    connected_nodes: List[str]
    severity: float
    
    def to_dict(self) -> Dict:
        return {
            "cluster_id": self.cluster_id,
            "risk_nodes": self.risk_nodes,
            "connected_nodes": self.connected_nodes,
            "severity": self.severity
        }


class GraphQueryEngine:
    """
    Provides query capabilities for the life signal graph.
    
    Capabilities:
    - Influence chain queries
    - High-leverage node discovery
    - Risk cluster identification
    - Domain-specific queries
    """
    
    def __init__(self, graph: LifeSignalGraph = None):
        self.graph = graph or get_life_graph()
    
    def get_influence_chain(
        self,
        node_name: str,
        depth: int = 3,
        domain: Domain = None
    ) -> List[Dict]:
        """
        Get influence chain from a node.
        
        Args:
            node_name: Name of the node (partial match)
            depth: Maximum depth
            domain: Filter by domain
            
        Returns:
            List of influence chains
        """
        # Find the node
        target_node = None
        for node in self.graph.get_all_nodes():
            if node_name.lower() in node.name.lower():
                if domain is None or node.domain == domain:
                    target_node = node
                    break
        
        if not target_node:
            return []
        
        chains = self.graph.get_influence_chain(
            start_node_id=target_node.node_id,
            depth=depth
        )
        
        return [chain.to_dict() for chain in chains]
    
    def get_high_leverage_nodes(
        self,
        limit: int = 10,
        domain: Domain = None
    ) -> List[LeveragePoint]:
        """
        Find high-leverage nodes.
        
        A node has high leverage if it influences many other nodes.
        
        Returns:
            List of leverage points sorted by score
        """
        leverage_points = []
        
        nodes = self.graph.get_all_nodes()
        if domain:
            nodes = [n for n in nodes if n.domain == domain]
        
        for node in nodes:
            # Calculate reach (number of influenced nodes)
            influences = self.graph.get_influences_from(node.node_id)
            
            # Get downstream reach
            downstream = set()
            def traverse(node_id: str, depth: int, max_depth: int):
                if depth >= max_depth:
                    return
                for _, edge in self.graph.get_influences_from(node_id):
                    downstream.add(edge.target_node_id)
                    traverse(edge.target_node_id, depth + 1, max_depth)
            
            traverse(node.node_id, 0, 3)
            
            reach = len(downstream)
            
            # Calculate leverage score
            # Score = reach * average edge weight * node confidence
            avg_weight = 0.5
            if influences:
                avg_weight = sum(e.weight for _, e in influences) / len(influences)
            
            leverage_score = reach * avg_weight * node.confidence
            
            if reach > 0:
                leverage_points.append(LeveragePoint(
                    node_id=node.node_id,
                    name=node.name,
                    domain=node.domain,
                    reach=reach,
                    leverage_score=leverage_score
                ))
        
        # Sort by leverage score
        leverage_points.sort(key=lambda x: x.leverage_score, reverse=True)
        
        return leverage_points[:limit]
    
    def get_risk_clusters(self) -> List[RiskCluster]:
        """
        Find clusters of related risks.
        
        Returns:
            List of risk clusters
        """
        # Get all risk nodes
        risk_nodes = self.graph.get_nodes_by_type(NodeType.RISK)
        
        if not risk_nodes:
            return []
        
        # Find clusters using graph's cluster detection
        clusters = self.graph.find_clusters()
        
        risk_clusters = []
        
        for cluster in clusters:
            cluster_risks = [n for n in cluster if n in [r.node_id for r in risk_nodes]]
            
            if cluster_risks:
                # Calculate severity
                severity = sum(
                    r.value for r in risk_nodes
                    if r.node_id in cluster_risks
                ) / len(cluster_risks)
                
                risk_clusters.append(RiskCluster(
                    cluster_id=f"risk_cluster_{len(risk_clusters)}",
                    risk_nodes=cluster_risks,
                    connected_nodes=list(cluster - set(cluster_risks)),
                    severity=severity
                ))
        
        # Sort by severity
        risk_clusters.sort(key=lambda x: x.severity, reverse=True)
        
        return risk_clusters
    
    def get_domain_health(self, domain: Domain) -> Dict:
        """
        Get health metrics for a domain.
        
        Returns:
            Domain health summary
        """
        nodes = self.graph.get_nodes_by_domain(domain)
        
        if not nodes:
            return {
                "domain": domain.value,
                "status": "no_data",
                "node_count": 0
            }
        
        # Calculate metrics
        signals = [n for n in nodes if n.node_type == NodeType.SIGNAL]
        states = [n for n in nodes if n.node_type == NodeType.STATE]
        risks = [n for n in nodes if n.node_type == NodeType.RISK]
        opportunities = [n for n in nodes if n.node_type == NodeType.OPPORTUNITY]
        
        # Calculate average confidence
        avg_confidence = sum(n.confidence for n in nodes) / len(nodes)
        
        # Determine status
        if risks:
            avg_risk = sum(r.value for r in risks if isinstance(r.value, (int, float))) / len(risks)
            if avg_risk > 0.7:
                status = "critical"
            elif avg_risk > 0.4:
                status = "warning"
            else:
                status = "stable"
        else:
            status = "stable"
        
        return {
            "domain": domain.value,
            "status": status,
            "node_count": len(nodes),
            "signals": len(signals),
            "states": len(states),
            "risks": len(risks),
            "opportunities": len(opportunities),
            "avg_confidence": avg_confidence,
            "graph_density": len(nodes) / max(1, self.graph.get_graph_density() * 100)
        }
    
    def find_path_between(
        self,
        source_name: str,
        target_name: str
    ) -> Optional[List[str]]:
        """
        Find a path between two nodes.
        
        Returns:
            List of node IDs in path, or None if no path
        """
        # Find source and target
        source = None
        target = None
        
        for node in self.graph.get_all_nodes():
            if source_name.lower() in node.name.lower():
                source = node
            if target_name.lower() in node.name.lower():
                target = node
            
            if source and target:
                break
        
        if not source or not target:
            return None
        
        # BFS to find path
        from collections import deque
        
        queue = deque([(source.node_id, [source.node_id])])
        visited = {source.node_id}
        
        while queue:
            current, path = queue.popleft()
            
            if current == target.node_id:
                return path
            
            for neighbor, _ in self.graph.get_influences_from(current):
                if neighbor.node_id not in visited:
                    visited.add(neighbor.node_id)
                    queue.append((neighbor.node_id, path + [neighbor.node_id]))
        
        return None
    
    def get_cross_domain_influence(self) -> Dict:
        """
        Get influence between domains.
        
        Returns:
            Matrix of cross-domain influence
        """
        influence_matrix = {}
        
        for src_domain in Domain:
            influence_matrix[src_domain.value] = {}
            
            src_nodes = self.graph.get_nodes_by_domain(src_domain)
            if not src_nodes:
                continue
            
            for tgt_domain in Domain:
                if src_domain == tgt_domain:
                    continue
                
                tgt_nodes = self.graph.get_nodes_by_domain(tgt_domain)
                if not tgt_nodes:
                    continue
                
                # Count edges between domains
                cross_edges = 0
                total_weight = 0.0
                
                for src_node in src_nodes:
                    for _, edge in self.graph.get_influences_from(src_node.node_id):
                        if edge.target_node_id in [n.node_id for n in tgt_nodes]:
                            cross_edges += 1
                            total_weight += edge.weight
                
                if cross_edges > 0:
                    influence_matrix[src_domain.value][tgt_domain.value] = {
                        "edge_count": cross_edges,
                        "avg_weight": total_weight / cross_edges
                    }
        
        return influence_matrix
    
    def get_life_system_summary(self) -> Dict:
        """
        Get a comprehensive summary of the life system.
        
        Returns:
            Full life system summary
        """
        return {
            "graph": self.graph.get_graph_summary(),
            "domain_health": {
                domain.value: self.get_domain_health(domain)
                for domain in Domain
            },
            "leverage_points": [
                lp.to_dict() for lp in self.get_high_leverage_nodes(5)
            ],
            "risk_clusters": [
                rc.to_dict() for rc in self.get_risk_clusters()
            ],
            "cross_domain": self.get_cross_domain_influence()
        }


# Global instance
_query_engine: Optional[GraphQueryEngine] = None


def get_graph_query_engine() -> GraphQueryEngine:
    """Get the global graph query engine"""
    global _query_engine
    if _query_engine is None:
        _query_engine = GraphQueryEngine()
    return _query_engine


__all__ = [
    "GraphQueryEngine",
    "LeveragePoint",
    "RiskCluster",
    "get_graph_query_engine",
]
