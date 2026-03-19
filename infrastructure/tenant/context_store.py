# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Tenant Context Store.

In-memory store for tenant context data.
In production, would connect to database.
"""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TenantRecord:
    """Tenant record in the store."""
    tenant_id: str
    plan_tier: str
    created_at: datetime
    metadata: dict[str, Any]


class TenantContextStore:
    """Store for tenant context data.
    
    In production, this would be backed by a database.
    """
    
    def __init__(self) -> None:
        self._tenants: dict[str, TenantRecord] = {}
    
    def create_tenant(
        self,
        tenant_id: str,
        plan_tier: str = "free",
        metadata: dict[str, Any] | None = None
    ) -> TenantRecord:
        """Create a new tenant."""
        record = TenantRecord(
            tenant_id=tenant_id,
            plan_tier=plan_tier,
            created_at=datetime.utcnow(),
            metadata=metadata or {},
        )
        self._tenants[tenant_id] = record
        return record
    
    def get_tenant(self, tenant_id: str) -> TenantRecord | None:
        """Get tenant by ID."""
        return self._tenants.get(tenant_id)
    
    def update_plan(self, tenant_id: str, plan_tier: str) -> bool:
        """Update tenant plan tier."""
        if tenant_id in self._tenants:
            self._tenants[tenant_id].plan_tier = plan_tier
            return True
        return False
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant."""
        if tenant_id in self._tenants:
            del self._tenants[tenant_id]
            return True
        return False
    
    def list_tenants(self) -> list[TenantRecord]:
        """List all tenants."""
        return list(self._tenants.values())


# Singleton instance
_tenant_store = TenantContextStore()


def get_tenant_store() -> TenantContextStore:
    """Get the default tenant store."""
    return _tenant_store
