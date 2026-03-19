"""
Memory Scope Manager - Layer 2: Data & Memory Isolation
BB-ARCH-ISO-001: Agent & Engine Isolation Architecture

This module implements the segmented memory architecture ensuring strict
memory access boundaries between agents, domains, and system components.

Directive: BB-ARCH-ISO-001
Layer: 2 - Data & Memory Isolation

Memory Layers:
1. Agent Working Memory - Private temporary reasoning space
2. Domain Memory - Persistent domain knowledge
3. Shared Strategic Memory - Cross-domain collaboration
4. Immutable Audit Memory - System-wide ledger
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import uuid
import threading
import json
import logging

logger = logging.getLogger(__name__)


class MemoryScope(Enum):
    """Memory scope levels as defined in BB-ARCH-ISO-001"""
    AGENT_WORKING = "agent_working"      # Private to single agent
    DOMAIN = "domain"                    # Domain-specific persistent
    SHARED_STRATEGIC = "shared_strategic" # Cross-domain collaboration
    AUDIT = "audit"                      # Immutable system ledger


class MemoryAccessLevel(Enum):
    """Allowed memory access levels"""
    NONE = 0
    READ = 1
    WRITE = 2
    READ_WRITE = 3
    ADMIN = 4  # Includes delete and modify permissions


@dataclass
class MemoryEntry:
    """
    Single entry in any memory layer.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scope: MemoryScope = MemoryScope.AGENT_WORKING
    owner_id: str = ""  # Agent ID or domain name
    key: str = ""
    value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scope": self.scope.value,
            "owner_id": self.owner_id,
            "key": self.key,
            "value": self.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }


class MemoryLayer(ABC):
    """
    Abstract base class for memory layers.
    Each layer implements specific access patterns and constraints.
    """
    
    def __init__(self, scope: MemoryScope):
        self.scope = scope
        self._storage: Dict[str, MemoryEntry] = {}
        self._lock = threading.RLock()
        
    @abstractmethod
    def can_read(self, requester_id: str, key: str) -> bool:
        """Check if a requester can read a key"""
        pass
    
    @abstractmethod
    def can_write(self, requester_id: str, key: str) -> bool:
        """Check if a requester can write a key"""
        pass
    
    def get(self, key: str, requester_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry if access is allowed"""
        with self._lock:
            if self.can_read(requester_id, key):
                entry = self._storage.get(key)
                if entry:
                    return entry
            return None
            
    def set(self, key: str, value: Any, owner_id: str, metadata: Optional[Dict] = None) -> MemoryEntry:
        """Set a memory entry if access is allowed"""
        with self._lock:
            if not self.can_write(owner_id, key):
                raise PermissionError(f"Write denied for {key} in {self.scope.value}")
            
            existing = self._storage.get(key)
            now = datetime.now()
            
            if existing:
                entry = MemoryEntry(
                    id=existing.id,
                    scope=self.scope,
                    owner_id=owner_id,
                    key=key,
                    value=value,
                    metadata=metadata or {},
                    created_at=existing.created_at,
                    updated_at=now,
                    version=existing.version + 1
                )
            else:
                entry = MemoryEntry(
                    scope=self.scope,
                    owner_id=owner_id,
                    key=key,
                    value=value,
                    metadata=metadata or {}
                )
                
            self._storage[key] = entry
            return entry
            
    def delete(self, key: str, requester_id: str) -> bool:
        """Delete a memory entry if access is allowed"""
        with self._lock:
            if not self.can_write(requester_id, key):
                raise PermissionError(f"Delete denied for {key} in {self.scope.value}")
            
            if key in self._storage:
                del self._storage[key]
                return True
            return False
            
    def list_keys(self, requester_id: str) -> List[str]:
        """List all accessible keys for a requester"""
        with self._lock:
            return [
                key for key in self._storage.keys()
                if self.can_read(requester_id, key)
            ]
    
    def get_all(self, requester_id: str) -> List[MemoryEntry]:
        """Get all accessible entries for a requester"""
        with self._lock:
            return [
                entry for key, entry in self._storage.items()
                if self.can_read(requester_id, key)
            ]


class AgentWorkingMemory(MemoryLayer):
    """
    Layer 1: Agent Working Memory
    
    Private temporary reasoning space for each agent.
    Accessible only by the owning agent.
    
    Used for:
    - Intermediate reasoning
    - Temporary simulations
    - Scratch analysis
    """
    
    def __init__(self):
        super().__init__(MemoryScope.AGENT_WORKING)
        self._agent_storage: Dict[str, Dict[str, MemoryEntry]] = defaultdict(dict)
        
    def can_read(self, requester_id: str, key: str) -> bool:
        """Only the owning agent can read its working memory"""
        # Format: {agent_id}:{key}
        agent_id = key.split(":")[0] if ":" in key else ""
        return agent_id == requester_id
    
    def can_write(self, requester_id: str, key: str) -> bool:
        """Only the owning agent can write to its working memory"""
        agent_id = key.split(":")[0] if ":" in key else ""
        return agent_id == requester_id
    
    def get(self, key: str, agent_id: str) -> Optional[MemoryEntry]:
        """Get entry using composite key"""
        full_key = f"{agent_id}:{key}"
        return super().get(full_key, agent_id)
    
    def set(self, key: str, value: Any, agent_id: str, metadata: Optional[Dict] = None) -> MemoryEntry:
        """Set entry using composite key"""
        full_key = f"{agent_id}:{key}"
        return super().set(full_key, value, agent_id, metadata)
    
    def delete(self, key: str, agent_id: str) -> bool:
        """Delete entry using composite key"""
        full_key = f"{agent_id}:{key}"
        return super().delete(full_key, agent_id)
    
    def list_keys(self, agent_id: str) -> List[str]:
        """List all keys for an agent"""
        with self._lock:
            prefix = f"{agent_id}:"
            return [
                key[len(prefix):] for key in self._storage.keys()
                if key.startswith(prefix)
            ]
    
    def clear_agent(self, agent_id: str) -> int:
        """Clear all working memory for an agent"""
        with self._lock:
            prefix = f"{agent_id}:"
            keys_to_delete = [k for k in self._storage.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._storage[key]
            return len(keys_to_delete)


class DomainMemory(MemoryLayer):
    """
    Layer 2: Domain Memory
    
    Persistent domain knowledge.
    Each domain has its own isolated memory space.
    
    Example domains: finance, health, career, relationships, intelligence, life_architecture
    """
    
    def __init__(self):
        super().__init__(MemoryScope.DOMAIN)
        self._domain_storage: Dict[str, Dict[str, MemoryEntry]] = defaultdict(dict)
        
    def can_read(self, requester_id: str, key: str) -> bool:
        """Domain memory is readable by any agent in that domain"""
        domain = key.split(":")[0] if ":" in key else ""
        return domain == requester_id or requester_id.startswith(domain)
    
    def can_write(self, requester_id: str, key: str) -> bool:
        """Only agents in the domain can write to domain memory"""
        domain = key.split(":")[0] if ":" in key else ""
        return domain == requester_id or requester_id.startswith(domain)
    
    def get(self, key: str, domain: str, requester_id: str) -> Optional[MemoryEntry]:
        """Get entry for a domain"""
        full_key = f"{domain}:{key}"
        return super().get(full_key, requester_id)
    
    def set(self, key: str, value: Any, domain: str, requester_id: str, metadata: Optional[Dict] = None) -> MemoryEntry:
        """Set entry for a domain"""
        full_key = f"{domain}:{key}"
        return super().set(full_key, value, requester_id, metadata)
    
    def list_domains(self) -> List[str]:
        """List all domains with stored memory"""
        with self._lock:
            domains = set()
            for key in self._storage.keys():
                domain = key.split(":")[0]
                domains.add(domain)
            return list(domains)


class SharedStrategicMemory(MemoryLayer):
    """
    Layer 3: Shared Strategic Memory
    
    Accessible by all agents for cross-domain collaboration.
    Contains:
    - Global signals
    - Strategic priorities
    - Life graph insights
    - Cross-domain correlations
    """
    
    def __init__(self):
        super().__init__(MemoryScope.SHARED_STRATEGIC)
        
    def can_read(self, requester_id: str, key: str) -> bool:
        """All agents can read shared strategic memory"""
        return True
    
    def can_write(self, requester_id: str, key: str) -> bool:
        """Write access requires domain prefix"""
        # Allow writes from registered agents with domain prefix
        return ":" in key or requester_id.startswith(("finance_", "health_", "career_", 
                                                        "relationships_", "intelligence_", "life_"))
    
    def list_by_category(self, category: str) -> List[MemoryEntry]:
        """List entries by category"""
        with self._lock:
            return [
                entry for key, entry in self._storage.items()
                if key.startswith(f"{category}:")
            ]


class AuditMemory(MemoryLayer):
    """
    Layer 4: Immutable Audit Memory
    
    System-wide ledger that cannot be modified once written.
    Stores:
    - Recommendations
    - Decisions
    - Approvals
    - Actions
    - Errors
    - System state
    
    Implements append-only semantics.
    """
    
    def __init__(self):
        super().__init__(MemoryScope.AUDIT)
        self._append_only_lock = threading.RLock()
        
    def can_read(self, requester_id: str, key: str) -> bool:
        """All system components can read audit memory"""
        return True
    
    def can_write(self, requester_id: str, key: str) -> bool:
        """Only system components can write to audit memory"""
        return requester_id in ("system", "audit", "execution_gate", "executive_council")
    
    def append(
        self,
        entry_type: str,
        data: Dict[str, Any],
        actor_id: str,
        metadata: Optional[Dict] = None
    ) -> MemoryEntry:
        """
        Append a new entry to audit memory.
        
        This is the ONLY way to add entries to audit memory.
        Once written, entries cannot be modified or deleted.
        """
        with self._append_only_lock:
            entry = MemoryEntry(
                scope=MemoryScope.AUDIT,
                owner_id=actor_id,
                key=f"{entry_type}:{uuid.uuid4()}",
                value=data,
                metadata={
                    "entry_type": entry_type,
                    "actor": actor_id,
                    **(metadata or {})
                }
            )
            self._storage[entry.id] = entry
            return entry
    
    def query(
        self,
        entry_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[MemoryEntry]:
        """Query audit memory with filters"""
        with self._lock:
            results = []
            for entry in self._storage.values():
                # Filter by entry type
                if entry_type and entry.metadata.get("entry_type") != entry_type:
                    continue
                    
                # Filter by actor
                if actor_id and entry.metadata.get("actor") != actor_id:
                    continue
                    
                # Filter by time range
                if start_time and entry.created_at < start_time:
                    continue
                if end_time and entry.created_at > end_time:
                    continue
                    
                results.append(entry)
                
            # Sort by timestamp (newest first)
            results.sort(key=lambda e: e.created_at, reverse=True)
            return results[:limit]
    
    def delete(self, key: str, requester_id: str) -> bool:
        """Audit memory is immutable - delete is disabled"""
        raise PermissionError("Audit memory is immutable - deletions not allowed")


class MemoryScopeManager:
    """
    Central manager for all memory layers.
    
    Provides unified interface for memory access while enforcing
    the four-layer isolation architecture.
    
    This is the main entry point for memory operations.
    """
    
    def __init__(self):
        self.agent_working = AgentWorkingMemory()
        self.domain = DomainMemory()
        self.shared = SharedStrategicMemory()
        self.audit = AuditMemory()
        self._lock = threading.RLock()
        
    def read(
        self,
        scope: MemoryScope,
        key: str,
        requester_id: str,
        domain: Optional[str] = None
    ) -> Optional[Any]:
        """Read a value from the appropriate memory layer"""
        with self._lock:
            layer = self._get_layer(scope)
            
            if scope == MemoryScope.DOMAIN and domain:
                entry = layer.get(key, domain, requester_id)
            elif scope == MemoryScope.AGENT_WORKING:
                entry = layer.get(key, requester_id)
            else:
                entry = layer.get(key, requester_id)
                
            return entry.value if entry else None
            
    def write(
        self,
        scope: MemoryScope,
        key: str,
        value: Any,
        requester_id: str,
        domain: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> MemoryEntry:
        """Write a value to the appropriate memory layer"""
        with self._lock:
            layer = self._get_layer(scope)
            
            if scope == MemoryScope.DOMAIN and domain:
                entry = layer.set(key, value, domain, requester_id, metadata)
            elif scope == MemoryScope.AGENT_WORKING:
                entry = layer.set(key, value, requester_id, metadata)
            else:
                entry = layer.set(key, value, requester_id, metadata)
                
            return entry
    
    def audit_log(
        self,
        entry_type: str,
        data: Dict[str, Any],
        actor_id: str,
        metadata: Optional[Dict] = None
    ) -> MemoryEntry:
        """Append to audit memory"""
        return self.audit.append(entry_type, data, actor_id, metadata)
    
    def _get_layer(self, scope: MemoryScope) -> MemoryLayer:
        """Get the appropriate memory layer"""
        layers = {
            MemoryScope.AGENT_WORKING: self.agent_working,
            MemoryScope.DOMAIN: self.domain,
            MemoryScope.SHARED_STRATEGIC: self.shared,
            MemoryScope.AUDIT: self.audit
        }
        return layers.get(scope)
    
    def get_memory_summary(self, requester_id: str) -> Dict[str, Any]:
        """Get a summary of accessible memory for a requester"""
        with self._lock:
            return {
                "agent_working_keys": self.agent_working.list_keys(requester_id),
                "domain_available": self.domain.list_domains(),
                "shared_strategic_keys": self.shared.list_keys(requester_id),
                "audit_recent": len(self.audit._storage)
            }
    
    def clear_agent_memory(self, agent_id: str) -> int:
        """Clear all memory for an agent"""
        return self.agent_working.clear_agent(agent_id)


# Global memory manager instance
_global_memory_manager: Optional[MemoryScopeManager] = None


def get_memory_manager() -> MemoryScopeManager:
    """Get the global memory scope manager"""
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryScopeManager()
    return _global_memory_manager


def reset_memory_manager() -> None:
    """Reset the global memory manager (for testing)"""
    global _global_memory_manager
    _global_memory_manager = None
