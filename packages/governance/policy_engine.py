# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Policy Engine for governance and approval enforcement.

Implements policy evaluation and human approval workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable
import uuid

from busybee_contracts.tenant_context import TenantContext, Permissions


class RiskLevel(str, Enum):
    """Risk levels for actions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionStatus(str, Enum):
    """Status of an action."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    CANCELLED = "cancelled"


@dataclass
class PolicyRule:
    """A policy rule definition."""
    name: str
    description: str
    risk_level: RiskLevel
    domain: str
    requires_human_approval: bool
    condition: Callable[[TenantContext, dict[str, Any]], bool] | None = None
    action: Callable[[TenantContext, dict[str, Any]], Any] | None = None


@dataclass
class ApprovalRequest:
    """An approval request for a high-risk action."""
    request_id: str
    tenant_id: str
    user_id: str
    action_id: str
    domain: str
    risk_level: RiskLevel
    description: str
    details: dict[str, Any]
    status: ActionStatus
    requested_at: datetime
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    resolution_reason: str | None = None

    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


class PolicyViolationError(Exception):
    """Raised when a policy is violated."""
    def __init__(self, message: str, rule: PolicyRule | None = None):
        super().__init__(message)
        self.rule = rule


class ApprovalRequiredError(PolicyViolationError):
    """Raised when an action requires human approval."""
    def __init__(self, message: str, request: ApprovalRequest):
        super().__init__(message)
        self.request = request


class PolicyEngine:
    """Engine for evaluating policies and managing approvals.
    
    Enforces governance rules including human approval for financial actions.
    """

    def __init__(self) -> None:
        self._rules: dict[str, PolicyRule] = {}
        self._approval_store: dict[str, ApprovalRequest] = {}
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Set up default governance rules."""
        
        # Financial transaction rules
        self.register_rule(PolicyRule(
            name="financial_transaction_approval",
            description="All financial transactions over $100 require human approval",
            risk_level=RiskLevel.HIGH,
            domain="finance",
            requires_human_approval=True,
            condition=lambda ctx, details: details.get("amount", 0) > 100
        ))
        
        self.register_rule(PolicyRule(
            name="investment_approval",
            description="All investment actions require human approval",
            risk_level=RiskLevel.CRITICAL,
            domain="finance",
            requires_human_approval=True,
        ))
        
        self.register_rule(PolicyRule(
            name="data_export_approval",
            description="Large data exports require approval",
            risk_level=RiskLevel.MEDIUM,
            domain="general",
            requires_human_approval=True,
            condition=lambda ctx, details: details.get("record_count", 0) > 1000
        ))

    def register_rule(self, rule: PolicyRule) -> None:
        """Register a policy rule."""
        self._rules[rule.name] = rule

    def get_rule(self, name: str) -> PolicyRule | None:
        """Get a policy rule by name."""
        return self._rules.get(name)

    def list_rules(self, domain: str | None = None) -> list[PolicyRule]:
        """List all rules, optionally filtered by domain."""
        rules = list(self._rules.values())
        if domain:
            rules = [r for r in rules if r.domain == domain]
        return rules

    def evaluate(
        self,
        context: TenantContext,
        action_id: str,
        details: dict[str, Any]
    ) -> tuple[RiskLevel, bool]:
        """Evaluate an action against policies.
        
        Args:
            context: Tenant context
            action_id: Action identifier
            details: Action details
            
        Returns:
            Tuple of (risk_level, requires_approval)
        """
        max_risk = RiskLevel.LOW
        requires_approval = False

        for rule in self._rules.values():
            # Check domain match
            if rule.domain not in action_id and rule.domain not in details.get("domain", ""):
                continue
                
            # Check condition
            if rule.condition and not rule.condition(context, details):
                continue

            # Update risk level
            if rule.risk_level.value > max_risk.value:
                max_risk = rule.risk_level
            
            if rule.requires_human_approval:
                requires_approval = True

        return max_risk, requires_approval

    def check_and_approve(
        self,
        context: TenantContext,
        action_id: str,
        details: dict[str, Any]
    ) -> ApprovalRequest | None:
        """Check policy and create approval request if needed.
        
        Returns:
            ApprovalRequest if approval needed, None if approved
        """
        risk_level, requires_approval = self.evaluate(context, action_id, details)
        
        if requires_approval:
            request = ApprovalRequest(
                request_id=str(uuid.uuid4()),
                tenant_id=context.tenant_id or "",
                user_id=context.user_id or "",
                action_id=action_id,
                domain=details.get("domain", "general"),
                risk_level=risk_level,
                description=details.get("description", action_id),
                details=details,
                status=ActionStatus.PENDING,
                requested_at=datetime.utcnow()
            )
            self._approval_store[request.request_id] = request
            return request
        
        return None

    def create_approval_request(
        self,
        context: TenantContext,
        action_id: str,
        domain: str,
        description: str,
        details: dict[str, Any],
        risk_level: RiskLevel = RiskLevel.MEDIUM
    ) -> ApprovalRequest:
        """Manually create an approval request."""
        request = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            tenant_id=context.tenant_id or "",
            user_id=context.user_id or "",
            action_id=action_id,
            domain=domain,
            risk_level=risk_level,
            description=description,
            details=details,
            status=ActionStatus.PENDING,
            requested_at=datetime.utcnow()
        )
        self._approval_store[request.request_id] = request
        return request

    def get_approval_request(
        self,
        request_id: str
    ) -> ApprovalRequest | None:
        """Get an approval request by ID."""
        return self._approval_store.get(request_id)

    def get_pending_approvals(
        self,
        tenant_id: str | None = None,
        user_id: str | None = None
    ) -> list[ApprovalRequest]:
        """Get pending approval requests, optionally filtered."""
        requests = [
            r for r in self._approval_store.values()
            if r.status == ActionStatus.PENDING
        ]
        
        if tenant_id:
            requests = [r for r in requests if r.tenant_id == tenant_id]
        
        if user_id:
            requests = [r for r in requests if r.user_id == user_id]
        
        return sorted(requests, key=lambda r: r.requested_at, reverse=True)

    def approve_request(
        self,
        request_id: str,
        resolver_id: str,
        reason: str | None = None
    ) -> ApprovalRequest | None:
        """Approve an approval request."""
        request = self._approval_store.get(request_id)
        if request and request.status == ActionStatus.PENDING:
            request.status = ActionStatus.APPROVED
            request.resolved_at = datetime.utcnow()
            request.resolved_by = resolver_id
            request.resolution_reason = reason
            return request
        return None

    def reject_request(
        self,
        request_id: str,
        resolver_id: str,
        reason: str
    ) -> ApprovalRequest | None:
        """Reject an approval request."""
        request = self._approval_store.get(request_id)
        if request and request.status == ActionStatus.PENDING:
            request.status = ActionStatus.REJECTED
            request.resolved_at = datetime.utcnow()
            request.resolved_by = resolver_id
            request.resolution_reason = reason
            return request
        return None

    def can_user_approve(self, context: TenantContext) -> bool:
        """Check if user can approve requests."""
        return context.has_permission(Permissions.FINANCE_APPROVE) or \
               context.has_permission(Permissions.APPROVALS_MANAGE) or \
               context.is_admin or context.is_owner


# Singleton instance
_policy_engine: PolicyEngine | None = None


def get_policy_engine() -> PolicyEngine:
    """Get the default policy engine."""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine
