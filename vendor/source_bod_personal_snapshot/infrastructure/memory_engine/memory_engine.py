"""
Memory Engine - Persists and retrieves system knowledge
Infrastructure Layer
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class MemoryEntry:
    """A memory entry"""
    id: str
    memory_type: str  # signal, decision, strategy, outcome, lesson
    content: Dict[str, Any]
    domain: Optional[str]
    importance: float  # 0.0 - 1.0
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0


class MemoryEngine:
    """
    Memory Engine persists and retrieves system knowledge.
    
    Stores:
    - Signals
    - Decisions
    - Strategies
    - Outcomes
    - Lessons learned
    
    Purpose: Continuous improvement of decision quality.
    """
    
    def __init__(self):
        self.memories: List[MemoryEntry] = []
        self.index_by_type: Dict[str, List[str]] = defaultdict(list)
        self.index_by_domain: Dict[str, List[str]] = defaultdict(list)
        self.index_by_tag: Dict[str, List[str]] = defaultdict(list)
    
    def store(
        self,
        memory_type: str,
        content: Dict[str, Any],
        domain: Optional[str] = None,
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> MemoryEntry:
        """Store a memory"""
        entry = MemoryEntry(
            id=f"mem_{len(self.memories) + 1}_{datetime.now().timestamp()}",
            memory_type=memory_type,
            content=content,
            domain=domain,
            importance=importance,
            tags=tags or []
        )
        
        self.memories.append(entry)
        self.index_by_type[memory_type].append(entry.id)
        
        if domain:
            self.index_by_domain[domain].append(entry.id)
        
        for tag in entry.tags:
            self.index_by_tag[tag].append(entry.id)
        
        return entry
    
    def retrieve(
        self,
        memory_type: Optional[str] = None,
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_importance: float = 0.0,
        limit: int = 100
    ) -> List[MemoryEntry]:
        """Retrieve memories with filters"""
        results = self.memories
        
        if memory_type:
            results = [m for m in results if m.memory_type == memory_type]
        
        if domain:
            results = [m for m in results if m.domain == domain]
        
        if tags:
            results = [m for m in results if any(t in m.tags for t in tags)]
        
        results = [m for m in results if m.importance >= min_importance]
        
        # Sort by importance and recency
        results.sort(key=lambda m: (m.importance, m.accessed_at), reverse=True)
        
        return results[:limit]
    
    def get_signal_history(self, domain: Optional[str] = None, limit: int = 50) -> List[MemoryEntry]:
        """Get signal history"""
        return self.retrieve(memory_type="signal", domain=domain, limit=limit)
    
    def get_decisions(self, domain: Optional[str] = None, limit: int = 50) -> List[MemoryEntry]:
        """Get decisions"""
        return self.retrieve(memory_type="decision", domain=domain, limit=limit)
    
    def get_strategies(self, domain: Optional[str] = None, limit: int = 50) -> List[MemoryEntry]:
        """Get strategies"""
        return self.retrieve(memory_type="strategy", domain=domain, limit=limit)
    
    def get_outcomes(self, domain: Optional[str] = None, limit: int = 50) -> List[MemoryEntry]:
        """Get outcomes"""
        return self.retrieve(memory_type="outcome", domain=domain, limit=limit)
    
    def get_lessons(self, domain: Optional[str] = None, limit: int = 50) -> List[MemoryEntry]:
        """Get lessons learned"""
        return self.retrieve(memory_type="lesson", domain=domain, limit=limit)
    
    def access(self, memory_id: str) -> Optional[MemoryEntry]:
        """Access a memory and update access statistics"""
        memory = next((m for m in self.memories if m.id == memory_id), None)
        
        if memory:
            memory.accessed_at = datetime.now()
            memory.access_count += 1
        
        return memory
    
    def get_recent(self, limit: int = 10) -> List[MemoryEntry]:
        """Get recently accessed memories"""
        sorted_memories = sorted(self.memories, key=lambda m: m.accessed_at, reverse=True)
        return sorted_memories[:limit]
    
    def get_important(self, threshold: float = 0.7, limit: int = 10) -> List[MemoryEntry]:
        """Get important memories"""
        important = [m for m in self.memories if m.importance >= threshold]
        important.sort(key=lambda m: m.importance, reverse=True)
        return important[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_memories": len(self.memories),
            "by_type": {
                mtype: len(mids) for mtype, mids in self.index_by_type.items()
            },
            "by_domain": {
                domain: len(mids) for domain, mids in self.index_by_domain.items()
            },
            "total_tags": len(self.index_by_tag),
            "most_accessed": sorted(
                [(m.id, m.access_count) for m in self.memories],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def export(self) -> str:
        """Export all memories as JSON"""
        return json.dumps([
            {
                "id": m.id,
                "memory_type": m.memory_type,
                "content": m.content,
                "domain": m.domain,
                "importance": m.importance,
                "tags": m.tags,
                "created_at": m.created_at.isoformat(),
                "accessed_at": m.accessed_at.isoformat(),
                "access_count": m.access_count
            }
            for m in self.memories
        ], indent=2)
