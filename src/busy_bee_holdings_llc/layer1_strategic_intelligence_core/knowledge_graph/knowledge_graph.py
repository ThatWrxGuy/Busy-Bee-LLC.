"""
Knowledge Graph - Stores and manages strategic knowledge
Part of Layer 1: Strategic Intelligence Core
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class Node:
    """A node in the knowledge graph"""
    id: str
    node_type: str  # entity, concept, person, organization, domain, strategy
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Relationship:
    """A relationship between nodes"""
    id: str
    source_id: str
    target_id: str
    relationship_type: str  # knows, relates_to, depends_on, supports, conflicts
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class KnowledgeGraph:
    """
    Knowledge Graph stores and manages strategic knowledge.
    
    Responsibilities:
    - Store entities and concepts
    - Manage relationships
    - Support querying and inference
    """
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.relationships: List[Relationship] = []
        self.index_by_type: Dict[str, Set[str]] = defaultdict(set)
    
    def add_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Node:
        """Add a node to the knowledge graph"""
        node = Node(
            id=node_id,
            node_type=node_type,
            label=label,
            properties=properties or {}
        )
        self.nodes[node_id] = node
        self.index_by_type[node_type].add(node_id)
        return node
    
    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Optional[Relationship]:
        """Add a relationship between two nodes"""
        # Verify nodes exist
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        relationship = Relationship(
            id=f"rel_{len(self.relationships) + 1}",
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            properties=properties or {}
        )
        self.relationships.append(relationship)
        return relationship
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_nodes_by_type(self, node_type: str) -> List[Node]:
        """Get all nodes of a specific type"""
        node_ids = self.index_by_type.get(node_type, set())
        return [self.nodes[nid] for nid in node_ids]
    
    def get_relationships(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for a node"""
        result = []
        for rel in self.relationships:
            if rel.source_id == node_id or rel.target_id == node_id:
                result.append({
                    "relationship": rel,
                    "direction": "outgoing" if rel.source_id == node_id else "incoming",
                    "other_node": self.nodes.get(
                        rel.target_id if rel.source_id == node_id else rel.source_id
                    )
                })
        return result
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 3) -> Optional[List[str]]:
        """Find a path between two nodes (simplified BFS)"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return None
        
        visited = {start_id}
        queue = [[start_id]]
        
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            if current == end_id:
                return path
            
            if len(path) > max_depth:
                continue
            
            for rel in self.relationships:
                next_node = None
                if rel.source_id == current and rel.target_id not in visited:
                    next_node = rel.target_id
                elif rel.target_id == current and rel.source_id not in visited:
                    next_node = rel.source_id
                
                if next_node:
                    visited.add(next_node)
                    queue.append(path + [next_node])
        
        return None
    
    def query(self, filters: Dict[str, Any]) -> List[Node]:
        """Query nodes with filters"""
        results = list(self.nodes.values())
        
        if "node_type" in filters:
            results = [n for n in results if n.node_type == filters["node_type"]]
        
        if "label_contains" in filters:
            results = [
                n for n in results 
                if filters["label_contains"].lower() in n.label.lower()
            ]
        
        if "domain" in filters:
            results = [n for n in results if n.properties.get("domain") == filters["domain"]]
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        return {
            "total_nodes": len(self.nodes),
            "total_relationships": len(self.relationships),
            "node_types": {
                ntype: len(nids) for ntype, nids in self.index_by_type.items()
            },
            "relationship_types": self._count_relationship_types()
        }
    
    def _count_relationship_types(self) -> Dict[str, int]:
        """Count relationships by type"""
        counts = defaultdict(int)
        for rel in self.relationships:
            counts[rel.relationship_type] += 1
        return dict(counts)
