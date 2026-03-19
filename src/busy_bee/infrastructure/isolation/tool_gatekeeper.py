"""
Tool Gatekeeper - Layer 3: Tool & Permission Isolation (Enforcement)
BB-ARCH-ISO-001: Agent & Engine Isolation Architecture

This module implements the gatekeeper that enforces tool access policies
and blocks unauthorized tool invocations.

Directive: BB-ARCH-ISO-001
Layer: 3 - Tool & Permission Isolation

The gatekeeper validates:
- Agent identity
- Tool permissions
- Domain restrictions
- Risk level requirements
- Approval status for high-risk tools
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import logging

logger = logging.getLogger(__name__)

from .permission_registry import (
    PermissionRegistry, 
    ToolDefinition, 
    ToolRiskLevel,
    PermissionStatus,
    get_permission_registry
)


class GatekeeperDecision(Enum):
    """Possible gatekeeper decisions"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class GatekeeperRequest:
    """Request to access a tool"""
    request_id: str
    agent_id: str
    agent_domain: str
    tool_id: str
    parameters: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "agent_domain": self.agent_domain,
            "tool_id": self.tool_id,
            "parameters": self.parameters,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class GatekeeperResponse:
    """Response from gatekeeper"""
    decision: GatekeeperDecision
    tool_id: str
    agent_id: str
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    approval_request_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "tool_id": self.tool_id,
            "agent_id": self.agent_id,
            "reason": self.reason,
            "metadata": self.metadata,
            "approval_request_id": self.approval_request_id
        }


class ApprovalRequest:
    """Request for approval of a high-risk tool"""
    def __init__(
        self,
        request: GatekeeperRequest,
        tool: ToolDefinition,
        required_approver: str
    ):
        self.request_id = request.request_id
        self.request = request
        self.tool = tool
        self.required_approver = required_approver
        self.status = "pending"
        self.requested_at = datetime.now()
        self.approved_by: Optional[str] = None
        self.denied_by: Optional[str] = None
        self.approved_at: Optional[datetime] = None
        self.denied_at: Optional[datetime] = None
        self.denial_reason: Optional[str] = None


class ToolGatekeeper:
    """
    Gatekeeper that enforces tool access policies.
    
    This is the enforcement point for Layer 3 - Tool & Permission Isolation.
    All tool invocations must pass through the gatekeeper.
    
    Features:
    - Permission validation
    - Domain restriction enforcement
    - Risk level checking
    - Approval workflow for L5 tools
    - Comprehensive audit logging
    """
    
    def __init__(self, permission_registry: Optional[PermissionRegistry] = None):
        self._registry = permission_registry or get_permission_registry()
        self._approval_requests: Dict[str, ApprovalRequest] = {}
        self._lock = threading.RLock()
        
        # Callbacks for logging
        self._log_callback: Optional[Callable[[GatekeeperResponse], None]] = None
        
    def set_log_callback(self, callback: Callable[[GatekeeperResponse], None]) -> None:
        """Set callback for logging gatekeeper decisions"""
        self._log_callback = callback
    
    def check_access(self, request: GatekeeperRequest) -> GatekeeperResponse:
        """
        Check if an agent can access a tool.
        
        This is the main entry point for tool access validation.
        Returns a GatekeeperResponse with the decision.
        """
        with self._lock:
            tool = self._registry.get_tool(request.tool_id)
            
            # Tool not found
            if not tool:
                response = GatekeeperResponse(
                    decision=GatekeeperDecision.DENY,
                    tool_id=request.tool_id,
                    agent_id=request.agent_id,
                    reason=f"Tool not found: {request.tool_id}"
                )
                self._log_decision(response)
                return response
            
            # Check domain restriction
            if request.agent_domain not in tool.domains:
                response = GatekeeperResponse(
                    decision=GatekeeperDecision.DENY,
                    tool_id=request.tool_id,
                    agent_id=request.agent_id,
                    reason=f"Tool {request.tool_id} not available in domain {request.agent_domain}",
                    metadata={"domain": request.agent_domain, "allowed_domains": tool.domains}
                )
                self._log_decision(response)
                return response
            
            # Check permission status
            permission_status = self._registry.check_permission(request.agent_id, request.tool_id)
            
            if permission_status == PermissionStatus.DENIED:
                # Check if domain-level permission exists
                if self._registry.check_domain_permission(request.agent_id, request.tool_id, request.agent_domain):
                    # Domain has permission, but agent doesn't have explicit grant
                    # Grant permission automatically for domain-level tools
                    self._registry.grant_permission(
                        agent_id=request.agent_id,
                        tool_id=request.tool_id,
                        granted_by="system_domain_grant"
                    )
                    permission_status = PermissionStatus.GRANTED
            
            if permission_status == PermissionStatus.DENIED:
                response = GatekeeperResponse(
                    decision=GatekeeperDecision.DENY,
                    tool_id=request.tool_id,
                    agent_id=request.agent_id,
                    reason=f"Permission denied for tool {request.tool_id}",
                    metadata={"risk_level": tool.risk_level.name}
                )
                self._log_decision(response)
                return response
            
            # Check if approval is required for high-risk tools
            if tool.requires_approval:
                # Check if there's a pending approval
                pending_approval = self._get_pending_approval(request)
                
                if pending_approval and pending_approval.status == "approved":
                    # Already approved
                    response = GatekeeperResponse(
                        decision=GatekeeperDecision.ALLOW,
                        tool_id=request.tool_id,
                        agent_id=request.agent_id,
                        reason="Tool access granted with prior approval",
                        metadata={"approval_id": pending_approval.request_id}
                    )
                    self._log_decision(response)
                    return response
                else:
                    # Require approval
                    approval_req = self._create_approval_request(request, tool)
                    response = GatekeeperResponse(
                        decision=GatekeeperDecision.REQUIRE_APPROVAL,
                        tool_id=request.tool_id,
                        agent_id=request.agent_id,
                        reason=f"Tool {request.tool_id} requires {tool.approval_role} approval",
                        metadata={
                            "risk_level": tool.risk_level.name,
                            "required_approver": tool.approval_role
                        },
                        approval_request_id=approval_req.request_id
                    )
                    self._log_decision(response)
                    return response
            
            # Allow access
            response = GatekeeperResponse(
                decision=GatekeeperDecision.ALLOW,
                tool_id=request.tool_id,
                agent_id=request.agent_id,
                reason=f"Tool access granted for {request.tool_id}",
                metadata={"risk_level": tool.risk_level.name}
            )
            self._log_decision(response)
            return response
    
    def _get_pending_approval(self, request: GatekeeperRequest) -> Optional[ApprovalRequest]:
        """Check if there's a pending approval for this request"""
        for approval in self._approval_requests.values():
            if (approval.request.agent_id == request.agent_id and
                approval.request.tool_id == request.tool_id and
                approval.status == "approved"):
                return approval
        return None
    
    def _create_approval_request(self, request: GatekeeperRequest, tool: ToolDefinition) -> ApprovalRequest:
        """Create a new approval request"""
        approval = ApprovalRequest(
            request=request,
            tool=tool,
            required_approver=tool.approval_role
        )
        self._approval_requests[approval.request_id] = approval
        return approval
    
    def approve_request(self, approval_request_id: str, approved_by: str) -> bool:
        """Approve a pending approval request"""
        with self._lock:
            approval = self._approval_requests.get(approval_request_id)
            if not approval:
                logger.warning(f"Approval request not found: {approval_request_id}")
                return False
                
            approval.status = "approved"
            approval.approved_by = approved_by
            approval.approved_at = datetime.now()
            
            logger.info(f"Approved {approval.tool.tool_id} for {approval.request.agent_id} by {approved_by}")
            return True
    
    def deny_request(self, approval_request_id: str, denied_by: str, reason: str) -> bool:
        """Deny a pending approval request"""
        with self._lock:
            approval = self._approval_requests.get(approval_request_id)
            if not approval:
                logger.warning(f"Approval request not found: {approval_request_id}")
                return False
                
            approval.status = "denied"
            approval.denied_by = denied_by
            approval.denied_at = datetime.now()
            approval.denial_reason = reason
            
            logger.info(f"Denied {approval.tool.tool_id} for {approval.request.agent_id} by {denied_by}: {reason}")
            return True
    
    def get_pending_approvals(self, approver_role: Optional[str] = None) -> List[ApprovalRequest]:
        """Get pending approval requests"""
        with self._lock:
            approvals = [
                a for a in self._approval_requests.values()
                if a.status == "pending"
            ]
            if approver_role:
                approvals = [
                    a for a in approvals
                    if a.required_approver == approver_role
                ]
            return approvals
    
    def _log_decision(self, response: GatekeeperResponse) -> None:
        """Log gatekeeper decision"""
        if self._log_callback:
            self._log_callback(response)
        else:
            logger.info(f"Gatekeeper: {response.decision.value} - {response.agent_id} -> {response.tool_id}: {response.reason}")
    
    def get_tool_risk_level(self, tool_id: str) -> Optional[ToolRiskLevel]:
        """Get the risk level of a tool"""
        tool = self._registry.get_tool(tool_id)
        return tool.risk_level if tool else None
    
    def is_tool_allowed(self, agent_id: str, tool_id: str, agent_domain: str) -> bool:
        """Quick check if tool is allowed (returns boolean)"""
        request = GatekeeperRequest(
            request_id=f"quick_check_{agent_id}_{tool_id}",
            agent_id=agent_id,
            agent_domain=agent_domain,
            tool_id=tool_id,
            parameters={}
        )
        response = self.check_access(request)
        return response.decision == GatekeeperDecision.ALLOW


# Global gatekeeper instance
_global_gatekeeper: Optional[ToolGatekeeper] = None


def get_tool_gatekeeper() -> ToolGatekeeper:
    """Get the global tool gatekeeper"""
    global _global_gatekeeper
    if _global_gatekeeper is None:
        _global_gatekeeper = ToolGatekeeper()
    return _global_gatekeeper


def reset_tool_gatekeeper() -> None:
    """Reset the global tool gatekeeper (for testing)"""
    global _global_gatekeeper
    _global_gatekeeper = None
