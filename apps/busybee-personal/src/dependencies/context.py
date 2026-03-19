# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Personal App Context Bootstrap.

Injects local TenantContext automatically for personal mode.
"""

from __future__ import annotations

from busybee_contracts.tenant_context import (
    TenantContext,
    create_personal_context,
)


class PersonalContextDependency:
    """FastAPI dependency for Personal mode context.
    
    Automatically injects a local context with full permissions.
    """
    
    @staticmethod
    def get(user_id: str = "owner") -> TenantContext:
        """Get TenantContext for personal mode."""
        return create_personal_context(user_id=user_id)


def get_personal_context() -> TenantContext:
    """Get the personal context (synchronous version)."""
    return create_personal_context()


# Singleton for consistent context across requests
_personal_context: TenantContext | None = None


def get_shared_personal_context() -> TenantContext:
    """Get shared personal context."""
    global _personal_context
    if _personal_context is None:
        _personal_context = create_personal_context()
    return _personal_context
