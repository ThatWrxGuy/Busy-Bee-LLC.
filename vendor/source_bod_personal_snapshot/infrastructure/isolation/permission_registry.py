"""
Permission Registry - Layer 3: Tool & Permission Isolation
BB-ARCH-ISO-001: Agent & Engine Isolation Architecture

This module implements the permission registry that controls which tools
each agent is allowed to access.

Directive: BB-ARCH-ISO-001
Layer: 3 - Tool & Permission Isolation

Tool Categories:
L1: Read-only data tools
L2: Analysis tools
L3: Simulation tools
L4: Recommendation tools
L5: External action tools (requires Governor approval)
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import logging

logger = logging.getLogger(__name__)


class ToolRiskLevel(Enum):
    """Tool risk levels as defined in BB-ARCH-ISO-001"""
    L1_READ_ONLY = 1      # Read-only data tools
    L2_ANALYSIS = 2       # Analysis tools
    L3_SIMULATION = 3    # Simulation tools
    L4_RECOMMENDATION = 4 # Recommendation tools
    L5_EXTERNAL = 5       # External action tools (requires approval)


class PermissionStatus(Enum):
    """Permission grant status"""
    GRANTED = "granted"
    DENIED = "denied"
    PENDING_APPROVAL = "pending_approval"
    REVOKED = "revoked"


@dataclass
class ToolDefinition:
    """Definition of a tool with its properties"""
    tool_id: str
    name: str
    description: str
    risk_level: ToolRiskLevel
    category: str
    domains: List[str]  # Allowed domains
    requires_approval: bool = False
    approval_role: str = "governor"  # Who can approve
    metadata: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class PermissionGrant:
    """A permission grant for an agent/tool combination"""
    grant_id: str
    agent_id: str
    tool_id: str
    status: PermissionStatus
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Check if grant is still valid"""
        if self.status != PermissionStatus.GRANTED:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True


class PermissionRegistry:
    """
    Central registry for managing agent-tool permissions.
    
    Implements the principle of least privilege - agents only get
    the minimum permissions needed for their role.
    
    Key features:
    - Domain-based tool access
    - Risk level enforcement
    - Governor approval workflow for high-risk tools
    - Audit logging of all permission changes
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._grants: Dict[str, List[PermissionGrant]] = {}  # agent_id -> grants
        self._domain_permissions: Dict[str, Set[str]] = {}   # domain -> tool_ids
        self._lock = threading.RLock()
        
        # Initialize default tools
        self._register_default_tools()
        
    def _register_default_tools(self) -> None:
        """Register default system tools"""
        default_tools = [
            # L1: Read-only data tools
            ToolDefinition(
                tool_id="read_market_data",
                name="Read Market Data",
                description="Read financial market data",
                risk_level=ToolRiskLevel.L1_READ_ONLY,
                category="data",
                domains=["finance"]
            ),
            ToolDefinition(
                tool_id="read_health_data",
                name="Read Health Data",
                description="Read health metrics and data",
                risk_level=ToolRiskLevel.L1_READ_ONLY,
                category="data",
                domains=["health"]
            ),
            ToolDefinition(
                tool_id="read_career_data",
                name="Read Career Data",
                description="Read career-related data",
                risk_level=ToolRiskLevel.L1_READ_ONLY,
                category="data",
                domains=["career"]
            ),
            
            # L2: Analysis tools
            ToolDefinition(
                tool_id="analyze_portfolio",
                name="Analyze Portfolio",
                description="Analyze investment portfolio performance",
                risk_level=ToolRiskLevel.L2_ANALYSIS,
                category="analysis",
                domains=["finance"]
            ),
            ToolDefinition(
                tool_id="analyze_health_trends",
                name="Analyze Health Trends",
                description="Analyze health data trends",
                risk_level=ToolRiskLevel.L2_ANALYSIS,
                category="analysis",
                domains=["health"]
            ),
            
            # L3: Simulation tools
            ToolDefinition(
                tool_id="simulate_investment",
                name="Simulate Investment",
                description="Simulate investment scenarios",
                risk_level=ToolRiskLevel.L3_SIMULATION,
                category="simulation",
                domains=["finance"]
            ),
            ToolDefinition(
                tool_id="simulate_lifestyle",
                name="Simulate Lifestyle",
                description="Simulate lifestyle changes",
                risk_level=ToolRiskLevel.L3_SIMULATION,
                category="simulation",
                domains=["life_architecture"]
            ),
            
            # L4: Recommendation tools
            ToolDefinition(
                tool_id="generate_recommendation",
                name="Generate Recommendation",
                description="Generate actionable recommendations",
                risk_level=ToolRiskLevel.L4_RECOMMENDATION,
                category="recommendation",
                domains=["finance", "health", "career", "relationships", "intelligence", "life_architecture"]
            ),
            
            # L5: External action tools (require approval)
            ToolDefinition(
                tool_id="execute_trade",
                name="Execute Trade",
                description="Execute financial trades",
                risk_level=ToolRiskLevel.L5_EXTERNAL,
                category="action",
                domains=["finance"],
                requires_approval=True,
                approval_role="governor"
            ),
            ToolDefinition(
                tool_id="transfer_funds",
                name="Transfer Funds",
                description="Transfer funds between accounts",
                risk_level=ToolRiskLevel.L5_EXTERNAL,
                category="action",
                domains=["finance"],
                requires_approval=True,
                approval_role="governor"
            ),
            ToolDefinition(
                tool_id="send_communication",
                name="Send Communication",
                description="Send external communications",
                risk_level=ToolRiskLevel.L5_EXTERNAL,
                category="action",
                domains=["relationships", "career"],
                requires_approval=True,
                approval_role="governor"
            ),
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
            
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a new tool"""
        with self._lock:
            self._tools[tool.tool_id] = tool
            
            # Add to domain permissions
            for domain in tool.domains:
                if domain not in self._domain_permissions:
                    self._domain_permissions[domain] = set()
                self._domain_permissions[domain].add(tool.tool_id)
                
            logger.info(f"Registered tool: {tool.tool_id} (risk level: {tool.risk_level.name})")
            
    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool definition"""
        return self._tools.get(tool_id)
    
    def list_tools(self, domain: Optional[str] = None, risk_level: Optional[ToolRiskLevel] = None) -> List[ToolDefinition]:
        """List tools with optional filters"""
        with self._lock:
            tools = list(self._tools.values())
            
            if domain:
                tools = [t for t in tools if domain in t.domains]
            if risk_level:
                tools = [t for t in tools if t.risk_level == risk_level]
                
            return tools
    
    def grant_permission(
        self,
        agent_id: str,
        tool_id: str,
        granted_by: str,
        expires_at: Optional[datetime] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> PermissionGrant:
        """Grant permission to an agent for a tool"""
        with self._lock:
            tool = self._tools.get(tool_id)
            if not tool:
                raise ValueError(f"Tool not found: {tool_id}")
                
            grant = PermissionGrant(
                grant_id=f"grant_{agent_id}_{tool_id}_{datetime.now().timestamp()}",
                agent_id=agent_id,
                tool_id=tool_id,
                status=PermissionStatus.GRANTED,
                granted_by=granted_by,
                granted_at=datetime.now(),
                expires_at=expires_at,
                conditions=conditions or {}
            )
            
            if agent_id not in self._grants:
                self._grants[agent_id] = []
            self._grants[agent_id].append(grant)
            
            logger.info(f"Granted {tool_id} to {agent_id} by {granted_by}")
            return grant
    
    def revoke_permission(self, agent_id: str, tool_id: str, revoked_by: str) -> bool:
        """Revoke permission from an agent"""
        with self._lock:
            grants = self._grants.get(agent_id, [])
            for grant in grants:
                if grant.tool_id == tool_id and grant.is_valid():
                    grant.status = PermissionStatus.REVOKED
                    logger.info(f"Revoked {tool_id} from {agent_id} by {revoked_by}")
                    return True
            return False
    
    def check_permission(self, agent_id: str, tool_id: str) -> PermissionStatus:
        """Check if an agent has permission for a tool"""
        with self._lock:
            grants = self._grants.get(agent_id, [])
            for grant in grants:
                if grant.tool_id == tool_id and grant.is_valid():
                    return grant.status
            return PermissionStatus.DENIED
    
    def check_domain_permission(self, agent_id: str, tool_id: str, agent_domain: str) -> bool:
        """
        Check if an agent from a domain has permission for a tool.
        Considers domain-level permissions.
        """
        tool = self._tools.get(tool_id)
        if not tool:
            return False
            
        # Check if tool is available in agent's domain
        if agent_domain not in tool.domains:
            return False
            
        # Check individual grant
        status = self.check_permission(agent_id, tool_id)
        return status == PermissionStatus.GRANTED
    
    def get_agent_permissions(self, agent_id: str) -> List[PermissionGrant]:
        """Get all permissions for an agent"""
        with self._lock:
            return [
                g for g in self._grants.get(agent_id, [])
                if g.is_valid()
            ]
    
    def get_tools_by_risk_level(self, risk_level: ToolRiskLevel) -> List[ToolDefinition]:
        """Get all tools at a specific risk level"""
        with self._lock:
            return [
                t for t in self._tools.values()
                if t.risk_level == risk_level
            ]
    
    def requires_approval(self, tool_id: str) -> bool:
        """Check if a tool requires governor approval"""
        tool = self._tools.get(tool_id)
        return tool.requires_approval if tool else False


# Global permission registry instance
_global_permission_registry: Optional[PermissionRegistry] = None


def get_permission_registry() -> PermissionRegistry:
    """Get the global permission registry"""
    global _global_permission_registry
    if _global_permission_registry is None:
        _global_permission_registry = PermissionRegistry()
    return _global_permission_registry


def reset_permission_registry() -> None:
    """Reset the global permission registry (for testing)"""
    global _global_permission_registry
    _global_permission_registry = None
