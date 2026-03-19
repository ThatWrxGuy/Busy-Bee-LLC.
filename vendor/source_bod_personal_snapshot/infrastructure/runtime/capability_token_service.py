"""
Capability Token Service - BB-ARCH-ISO-002
Agent Sandbox & Container Runtime Architecture

This module implements the capability token service that issues
temporary capability tokens to agent containers.

Directive: BB-ARCH-ISO-002
Section: 10 - Agent Security Model
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import threading
import hashlib
import logging

logger = logging.getLogger(__name__)


class CapabilityScope(Enum):
    """Scopes for capabilities"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class Capability:
    """A single capability"""
    name: str
    description: str
    scope: CapabilityScope
    resource: str  # What resource this applies to
    permissions: List[str] = field(default_factory=list)
    requires_approval: bool = False  # Whether this capability requires approval


@dataclass
class CapabilityToken:
    """A temporary token granting capabilities to an agent"""
    token_id: str
    agent_id: str
    capabilities: List[str]  # List of capability names
    issued_at: datetime
    expires_at: datetime
    is_active: bool = True
    
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        if not self.is_active:
            return False
        if datetime.now() > self.expires_at:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active
        }


class CapabilityRegistry:
    """
    Registry of available capabilities.
    
    Defines what capabilities exist in the system.
    """
    
    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        self._lock = threading.RLock()
        
        # Register default capabilities
        self._register_default_capabilities()
        
    def _register_default_capabilities(self) -> None:
        """Register default system capabilities"""
        
        # Finance domain capabilities
        self.register_capability(Capability(
            name="read_financial_data",
            description="Read financial data and market information",
            scope=CapabilityScope.READ,
            resource="finance",
            permissions=["read_market_data", "read_portfolio"]
        ))
        
        self.register_capability(Capability(
            name="read_financial_memory",
            description="Read from financial memory",
            scope=CapabilityScope.READ,
            resource="finance_memory",
            permissions=["read"]
        ))
        
        self.register_capability(Capability(
            name="write_financial_memory",
            description="Write to financial memory",
            scope=CapabilityScope.WRITE,
            resource="finance_memory",
            permissions=["write"]
        ))
        
        self.register_capability(Capability(
            name="publish_strategy",
            description="Publish strategies to the fabric",
            scope=CapabilityScope.EXECUTE,
            resource="strategy_registry",
            permissions=["register"]
        ))
        
        self.register_capability(Capability(
            name="read_market_signals",
            description="Read market signals",
            scope=CapabilityScope.READ,
            resource="signals",
            permissions=["read:market"]
        ))
        
        # Health domain capabilities
        self.register_capability(Capability(
            name="read_health_data",
            description="Read health data and metrics",
            scope=CapabilityScope.READ,
            resource="health",
            permissions=["read_vitals", "read_sleep", "read_activity"]
        ))
        
        self.register_capability(Capability(
            name="read_health_memory",
            description="Read from health memory",
            scope=CapabilityScope.READ,
            resource="health_memory",
            permissions=["read"]
        ))
        
        self.register_capability(Capability(
            name="publish_wellness_recommendations",
            description="Publish wellness recommendations",
            scope=CapabilityScope.EXECUTE,
            resource="recommendations",
            permissions=["create"]
        ))
        
        # Career domain capabilities
        self.register_capability(Capability(
            name="read_career_data",
            description="Read career data",
            scope=CapabilityScope.READ,
            resource="career",
            permissions=["read_skills", "read_opportunities"]
        ))
        
        self.register_capability(Capability(
            name="publish_career_insights",
            description="Publish career insights",
            scope=CapabilityScope.EXECUTE,
            resource="insights",
            permissions=["create"]
        ))
        
        # Relationship domain capabilities
        self.register_capability(Capability(
            name="read_relationship_data",
            description="Read relationship data",
            scope=CapabilityScope.READ,
            resource="relationships",
            permissions=["read_contacts", "read_interactions"]
        ))
        
        # General capabilities
        self.register_capability(Capability(
            name="read_shared_memory",
            description="Read from shared strategic memory",
            scope=CapabilityScope.READ,
            resource="shared_memory",
            permissions=["read"]
        ))
        
        self.register_capability(Capability(
            name="write_shared_memory",
            description="Write to shared strategic memory",
            scope=CapabilityScope.WRITE,
            resource="shared_memory",
            permissions=["write"]
        ))
        
        self.register_capability(Capability(
            name="read_audit_memory",
            description="Read audit memory",
            scope=CapabilityScope.READ,
            resource="audit_memory",
            permissions=["read"]
        ))
        
        # High-risk capabilities (require approval)
        self.register_capability(Capability(
            name="execute_trade",
            description="Execute financial trades",
            scope=CapabilityScope.EXECUTE,
            resource="trading",
            permissions=["execute"],
            requires_approval=True
        ))
        
        self.register_capability(Capability(
            name="transfer_funds",
            description="Transfer funds between accounts",
            scope=CapabilityScope.EXECUTE,
            resource="banking",
            permissions=["transfer"],
            requires_approval=True
        ))
        
    def register_capability(self, capability: Capability) -> None:
        """Register a new capability"""
        with self._lock:
            self._capabilities[capability.name] = capability
            logger.info(f"Registered capability: {capability.name}")
            
    def get_capability(self, name: str) -> Optional[Capability]:
        """Get a capability by name"""
        return self._capabilities.get(name)
    
    def get_all_capabilities(self) -> List[Capability]:
        """Get all registered capabilities"""
        return list(self._capabilities.values())
    
    def get_capabilities_for_domain(self, domain: str) -> List[Capability]:
        """Get capabilities available for a domain"""
        return [
            cap for cap in self._capabilities.values()
            if domain in cap.resource or domain in cap.name
        ]
    
    def requires_approval(self, capability_name: str) -> bool:
        """Check if a capability requires approval"""
        cap = self._capabilities.get(capability_name)
        return getattr(cap, 'requires_approval', False)


class CapabilityTokenService:
    """
    Service for issuing and managing capability tokens.
    
    Each agent container receives a temporary capability token
    that defines what the agent can access.
    
    Section 10: Agent Security Model
    """
    
    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self._registry = registry or CapabilityRegistry()
        self._tokens: Dict[str, CapabilityToken] = {}
        self._agent_tokens: Dict[str, List[str]] = {}  # agent_id -> token_ids
        self._lock = threading.RLock()
        
        # Token configuration
        self._default_ttl_minutes = 60
        self._max_token_age_hours = 24
        
    def issue_token(
        self,
        agent_id: str,
        capability_names: List[str],
        ttl_minutes: Optional[int] = None
    ) -> CapabilityToken:
        """
        Issue a capability token to an agent.
        
        This is called when an agent container starts.
        """
        with self._lock:
            # Validate capabilities
            valid_capabilities = []
            for name in capability_names:
                cap = self._registry.get_capability(name)
                if cap:
                    valid_capabilities.append(name)
                else:
                    logger.warning(f"Unknown capability: {name}")
                    
            # Create token
            ttl = ttl_minutes or self._default_ttl_minutes
            now = datetime.now()
            
            token = CapabilityToken(
                token_id=self._generate_token_id(agent_id),
                agent_id=agent_id,
                capabilities=valid_capabilities,
                issued_at=now,
                expires_at=now + timedelta(minutes=ttl)
            )
            
            self._tokens[token.token_id] = token
            
            # Track agent's tokens
            if agent_id not in self._agent_tokens:
                self._agent_tokens[agent_id] = []
            self._agent_tokens[agent_id].append(token.token_id)
            
            logger.info(f"Issued token {token.token_id} to agent {agent_id} with capabilities: {valid_capabilities}")
            
            return token
            
    def verify_token(self, token_id: str, required_capability: str) -> bool:
        """
        Verify a token has a specific capability.
        
        This is called when an agent attempts to access a resource.
        """
        with self._lock:
            token = self._tokens.get(token_id)
            if not token or not token.is_valid():
                return False
                
            return required_capability in token.capabilities
            
    def revoke_token(self, token_id: str) -> bool:
        """Revoke a capability token"""
        with self._lock:
            token = self._tokens.get(token_id)
            if not token:
                return False
                
            token.is_active = False
            
            # Remove from agent's tokens
            agent_id = token.agent_id
            if agent_id in self._agent_tokens:
                self._agent_tokens[agent_id] = [
                    t for t in self._agent_tokens[agent_id]
                    if t != token_id
                ]
                
            logger.info(f"Revoked token {token_id}")
            return True
            
    def revoke_all_agent_tokens(self, agent_id: str) -> int:
        """Revoke all tokens for an agent"""
        with self._lock:
            token_ids = self._agent_tokens.get(agent_id, [])
            count = 0
            
            for token_id in token_ids:
                if self.revoke_token(token_id):
                    count += 1
                    
            return count
            
    def refresh_token(self, token_id: str, ttl_minutes: Optional[int] = None) -> bool:
        """Refresh a token's expiration time"""
        with self._lock:
            token = self._tokens.get(token_id)
            if not token:
                return False
                
            ttl = ttl_minutes or self._default_ttl_minutes
            token.expires_at = datetime.now() + timedelta(minutes=ttl)
            
            logger.info(f"Refreshed token {token_id}")
            return True
            
    def get_token(self, token_id: str) -> Optional[CapabilityToken]:
        """Get token by ID"""
        return self._tokens.get(token_id)
    
    def get_agent_tokens(self, agent_id: str) -> List[CapabilityToken]:
        """Get all valid tokens for an agent"""
        with self._lock:
            token_ids = self._agent_tokens.get(agent_id, [])
            return [
                self._tokens[tid] 
                for tid in token_ids 
                if tid in self._tokens and self._tokens[tid].is_valid()
            ]
            
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens"""
        with self._lock:
            now = datetime.now()
            expired = [
                tid for tid, token in self._tokens.items()
                if not token.is_valid()
            ]
            
            for tid in expired:
                token = self._tokens[tid]
                agent_id = token.agent_id
                
                # Remove from agent's tokens
                if agent_id in self._agent_tokens:
                    self._agent_tokens[agent_id] = [
                        t for t in self._agent_tokens[agent_id]
                        if t != tid
                    ]
                    
                del self._tokens[tid]
                
            if expired:
                logger.info(f"Cleaned up {len(expired)} expired tokens")
                
            return len(expired)
            
    def get_capabilities_for_agent(self, agent_id: str) -> List[Capability]:
        """Get all capabilities available to an agent"""
        tokens = self.get_agent_tokens(agent_id)
        capabilities = []
        
        for token in tokens:
            for cap_name in token.capabilities:
                cap = self._registry.get_capability(cap_name)
                if cap:
                    capabilities.append(cap)
                    
        return capabilities
        
    def _generate_token_id(self, agent_id: str) -> str:
        """Generate a unique token ID"""
        raw = f"{agent_id}:{uuid.uuid4()}:{datetime.now().isoformat()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]


# Global service instance
_global_capability_service: Optional[CapabilityTokenService] = None


def get_capability_token_service() -> CapabilityTokenService:
    """Get the global capability token service"""
    global _global_capability_service
    if _global_capability_service is None:
        _global_capability_service = CapabilityTokenService()
    return _global_capability_service


def reset_capability_token_service() -> None:
    """Reset the global service (for testing)"""
    global _global_capability_service
    _global_capability_service = None
