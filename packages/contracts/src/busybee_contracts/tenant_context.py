# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Extended Tenant Context with roles and workspace support.

This module extends the base TenantContext with roles, permissions,
and workspace isolation for BB-SAAS-001 Multi-Tenant SaaS Foundation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, FrozenSet

if TYPE_CHECKING:
    from infrastructure.auth.jwt_service import JWTPayload

ExecutionMode = Literal["saas", "personal"]

PlanTier = Literal["free", "pro", "enterprise"]

# Role definitions
class Roles:
    """Standard roles for Busy Bee SaaS."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
    APPROVER = "approver"


# Permission definitions
class Permissions:
    """Standard permissions for Busy Bee SaaS."""
    # Tenant management
    TENANT_READ = "tenant:read"
    TENANT_WRITE = "tenant:write"
    TENANT_ADMIN = "tenant:admin"
    
    # Agent execution
    AGENT_EXECUTE = "agent:execute"
    AGENT_CREATE = "agent:create"
    AGENT_MANAGE = "agent:manage"
    
    # Connector management
    CONNECTOR_READ = "connector:read"
    CONNECTOR_WRITE = "connector:write"
    CONNECTOR_MANAGE = "connector:manage"
    
    # Financial actions
    FINANCE_READ = "finance:read"
    FINANCE_WRITE = "finance:write"
    FINANCE_APPROVE = "finance:approve"
    
    # Health data
    HEALTH_READ = "health:read"
    HEALTH_WRITE = "health:write"
    
    # Career data
    CAREER_READ = "career:read"
    CAREER_WRITE = "career:write"
    
    # Governance
    GOVERNANCE_READ = "governance:read"
    GOVERNANCE_WRITE = "governance:write"
    APPROVALS_MANAGE = "approvals:manage"
    
    # Billing
    BILLING_READ = "billing:read"
    BILLING_MANAGE = "billing:manage"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[str, FrozenSet[str]] = {
    Roles.OWNER: frozenset({"*"}),
    Roles.ADMIN: frozenset({
        Permissions.TENANT_READ, Permissions.TENANT_WRITE,
        Permissions.AGENT_EXECUTE, Permissions.AGENT_CREATE, Permissions.AGENT_MANAGE,
        Permissions.CONNECTOR_READ, Permissions.CONNECTOR_WRITE, Permissions.CONNECTOR_MANAGE,
        Permissions.FINANCE_READ, Permissions.FINANCE_WRITE,
        Permissions.HEALTH_READ, Permissions.HEALTH_WRITE,
        Permissions.CAREER_READ, Permissions.CAREER_WRITE,
        Permissions.GOVERNANCE_READ, Permissions.GOVERNANCE_WRITE,
        Permissions.APPROVALS_MANAGE,
    }),
    Roles.MEMBER: frozenset({
        Permissions.TENANT_READ,
        Permissions.AGENT_EXECUTE, Permissions.AGENT_CREATE,
        Permissions.CONNECTOR_READ, Permissions.CONNECTOR_WRITE,
        Permissions.FINANCE_READ,
        Permissions.HEALTH_READ, Permissions.HEALTH_WRITE,
        Permissions.CAREER_READ, Permissions.CAREER_WRITE,
    }),
    Roles.VIEWER: frozenset({
        Permissions.TENANT_READ,
        Permissions.AGENT_EXECUTE,
        Permissions.CONNECTOR_READ,
        Permissions.FINANCE_READ,
        Permissions.HEALTH_READ,
        Permissions.CAREER_READ,
    }),
    Roles.APPROVER: frozenset({
        Permissions.TENANT_READ,
        Permissions.FINANCE_READ, Permissions.FINANCE_APPROVE,
        Permissions.GOVERNANCE_READ, Permissions.APPROVALS_MANAGE,
    }),
}


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Canonical tenant context for all Busy Bee operations.

    This context MUST be derived from JWT in SaaS mode.
    Personal mode uses a simplified local context.
    
    Extended with roles, workspace_id, and permission helpers.
    """

    tenant_id: str | None = None
    user_id: str | None = None
    workspace_id: str | None = None
    roles: FrozenSet[str] = field(default_factory=frozenset)
    permissions: FrozenSet[str] = field(default_factory=frozenset)
    mode: ExecutionMode = "personal"
    plan_tier: PlanTier = "free"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_saas(self) -> bool:
        """Check if running in SaaS mode."""
        return self.mode == "saas"

    @property
    def is_personal(self) -> bool:
        """Check if running in personal mode."""
        return self.mode == "personal"

    @property
    def has_tenant_scope(self) -> bool:
        """Check if tenant scope is available."""
        return bool(self.tenant_id)

    @property
    def has_user_scope(self) -> bool:
        """Check if user scope is available."""
        return bool(self.user_id)

    @property
    def has_workspace_scope(self) -> bool:
        """Check if workspace scope is available."""
        return bool(self.workspace_id)

    @property
    def is_owner(self) -> bool:
        """Check if user has owner role."""
        return Roles.OWNER in self.roles

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return Roles.ADMIN in self.roles

    def require_tenant(self) -> None:
        """Require valid tenant_id for SaaS operations."""
        if self.is_saas and not self.tenant_id:
            raise ValueError("SaaS execution requires tenant_id")

    def require_user(self) -> None:
        """Require valid user_id for SaaS operations."""
        if self.is_saas and not self.user_id:
            raise ValueError("SaaS execution requires user_id")

    def require_scope(self) -> None:
        """Require both tenant and user scope."""
        self.require_tenant()
        self.require_user()

    def require_workspace(self) -> None:
        """Require workspace_id for workspace operations."""
        if self.is_saas and not self.workspace_id:
            raise ValueError("Workspace operations require workspace_id")

    def has_permission(self, permission: str) -> bool:
        """Check if context has a specific permission.
        
        Checks both explicit permissions and role-based permissions.
        """
        # Wildcard grants all
        if "*" in self.permissions:
            return True
        # Check explicit permission
        if permission in self.permissions:
            return True
        # Check role-based permissions
        for role in self.roles:
            role_perms = ROLE_PERMISSIONS.get(role, frozenset())
            if "*" in role_perms:
                return True
            if permission in role_perms:
                return True
        return False

    def require_permission(self, permission: str) -> None:
        """Require a specific permission."""
        if not self.has_permission(permission):
            raise PermissionError(f"Missing required permission: {permission}")

    def get_data_path(self, resource: str = "") -> str:
        """Get the data path for this tenant.
        
        All data storage must be scoped under this path.
        
        Args:
            resource: Optional resource path to append
            
        Returns:
            Path string: /tenants/{tenant_id}/{workspace_id}/{resource}
        """
        if not self.tenant_id:
            raise ValueError("Cannot get data path without tenant_id")
        
        base = f"/tenants/{self.tenant_id}"
        if self.workspace_id:
            base = f"{base}/workspaces/{self.workspace_id}"
        
        if resource:
            base = f"{base}/{resource}"
        
        return base

    def to_lineage(self) -> dict[str, Any]:
        """Convert to lineage dict for audit."""
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "roles": list(self.roles),
            "mode": self.mode,
            "plan_tier": self.plan_tier,
        }

    @classmethod
    def from_jwt_payload(cls, payload: "JWTPayload") -> "TenantContext":
        """Create TenantContext from JWT payload.

        This is the ONLY allowed way to create SaaS contexts.

        Args:
            payload: Verified JWT payload

        Returns:
            TenantContext derived from JWT

        Raises:
            ValueError: If payload is invalid for SaaS mode
        """
        mode = payload.mode

        if mode == "saas":
            # SaaS requires tenant_id from JWT
            if not payload.tenant_id:
                raise ValueError("SaaS mode requires tenant_id in JWT")

            # Extract roles from payload or default to member
            roles = frozenset(payload.roles) if hasattr(payload, 'roles') else frozenset({Roles.MEMBER})
            
            # Compute permissions from roles
            permissions = cls._compute_permissions(roles, payload.permissions)

            return cls(
                tenant_id=payload.tenant_id,
                user_id=payload.subject,
                workspace_id=payload.workspace_id if hasattr(payload, 'workspace_id') else None,
                roles=roles,
                permissions=permissions,
                mode=mode,
                plan_tier=payload.plan,
                metadata={"source": "jwt", "iat": payload.issued_at}
            )
        else:
            # Personal mode - create local context
            return create_personal_context(user_id=payload.subject)

    @staticmethod
    def _compute_permissions(
        roles: FrozenSet[str],
        explicit_permissions: list[str] | None = None
    ) -> FrozenSet[str]:
        """Compute permissions from roles and explicit grants."""
        perms = set()
        
        # Add role-based permissions
        for role in roles:
            role_perms = ROLE_PERMISSIONS.get(role, frozenset())
            perms.update(role_perms)
        
        # Add explicit permissions
        if explicit_permissions:
            perms.update(explicit_permissions)
        
        return frozenset(perms)


def create_personal_context(user_id: str = "owner") -> TenantContext:
    """Create a personal mode context with full permissions.

    WARNING: This should ONLY be used for local development/testing.
    Production personal mode should still use JWT.
    """
    return TenantContext(
        tenant_id="personal-local",
        user_id=user_id,
        workspace_id="default",
        roles=frozenset({Roles.OWNER}),
        permissions=frozenset({"*"}),
        mode="personal",
        plan_tier="owner",
        metadata={"source": "bootstrap"}
    )


def create_saas_context(
    tenant_id: str,
    user_id: str,
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
    workspace_id: str | None = None,
    plan_tier: str = "free"
) -> TenantContext:
    """Create a SaaS mode context with scoped permissions.

    WARNING: This should ONLY be used internally after JWT verification.
    Use from_jwt_payload() for normal creation.
    """
    roles = roles or [Roles.MEMBER]
    computed_permissions = TenantContext._compute_permissions(
        frozenset(roles),
        permissions
    )
    
    return TenantContext(
        tenant_id=tenant_id,
        user_id=user_id,
        workspace_id=workspace_id,
        roles=frozenset(roles),
        permissions=computed_permissions,
        mode="saas",
        plan_tier=plan_tier,
    )
