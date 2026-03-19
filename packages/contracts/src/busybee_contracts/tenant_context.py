from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, FrozenSet

ExecutionMode = Literal["saas", "personal"]


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Canonical tenant context for all Busy Bee operations.
    
    This context MUST be present for all SaaS operations.
    Personal mode uses a simplified local context.
    """
    
    tenant_id: str | None = None
    user_id: str | None = None
    mode: ExecutionMode = "personal"
    permissions: FrozenSet[str] = field(default_factory=frozenset)
    plan_tier: str = "free"
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
    
    def has_permission(self, permission: str) -> bool:
        """Check if context has a specific permission."""
        if "*" in self.permissions:
            return True
        return permission in self.permissions
    
    def to_lineage(self) -> dict[str, Any]:
        """Convert to lineage dict for audit."""
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "mode": self.mode,
            "plan_tier": self.plan_tier,
        }


def create_personal_context(user_id: str = "owner") -> TenantContext:
    """Create a personal mode context with full permissions."""
    return TenantContext(
        tenant_id="personal-local",
        user_id=user_id,
        mode="personal",
        permissions=frozenset({"*"}),
        plan_tier="owner",
        metadata={"source": "bootstrap"}
    )


def create_saas_context(
    tenant_id: str,
    user_id: str,
    permissions: list[str] | None = None,
    plan_tier: str = "free"
) -> TenantContext:
    """Create a SaaS mode context with scoped permissions."""
    return TenantContext(
        tenant_id=tenant_id,
        user_id=user_id,
        mode="saas",
        permissions=frozenset(permissions) if permissions else frozenset(),
        plan_tier=plan_tier,
    )
