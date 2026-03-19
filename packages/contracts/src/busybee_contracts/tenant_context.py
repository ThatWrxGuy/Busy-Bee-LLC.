from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, FrozenSet

if TYPE_CHECKING:
    from infrastructure.auth.jwt_service import JWTPayload

ExecutionMode = Literal["saas", "personal"]

PlanTier = Literal["free", "pro", "enterprise"]


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Canonical tenant context for all Busy Bee operations.
    
    This context MUST be derived from JWT in SaaS mode.
    Personal mode uses a simplified local context.
    """
    
    tenant_id: str | None = None
    user_id: str | None = None
    mode: ExecutionMode = "personal"
    permissions: FrozenSet[str] = field(default_factory=frozenset)
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
            
            return cls(
                tenant_id=payload.tenant_id,
                user_id=payload.subject,
                mode=mode,
                permissions=frozenset(payload.permissions),
                plan_tier=payload.plan,
                metadata={"source": "jwt", "iat": payload.issued_at}
            )
        else:
            # Personal mode - create local context
            return create_personal_context(user_id=payload.subject)


def create_personal_context(user_id: str = "owner") -> TenantContext:
    """Create a personal mode context with full permissions.
    
    WARNING: This should ONLY be used for local development/testing.
    Production personal mode should still use JWT.
    """
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
    """Create a SaaS mode context with scoped permissions.
    
    WARNING: This should ONLY be used internally after JWT verification.
    Use from_jwt_payload() for normal creation.
    """
    return TenantContext(
        tenant_id=tenant_id,
        user_id=user_id,
        mode="saas",
        permissions=frozenset(permissions) if permissions else frozenset(),
        plan_tier=plan_tier,
    )
