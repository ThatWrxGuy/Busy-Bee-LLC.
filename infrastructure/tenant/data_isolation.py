# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Tenant Data Isolation Patterns.

This module provides patterns for ensuring tenant data isolation at the database level.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar, Protocol
from dataclasses import dataclass


T = TypeVar("T")


class TenantScopeError(Exception):
    """Raised when tenant scope is missing for data access."""
    pass


@dataclass
class TenantFilter:
    """Tenant filter for database queries."""
    tenant_id: str
    user_id: str | None = None


class TenantScopedRepository(Generic[T]):
    """Base class for tenant-scoped data access.
    
    All data access must be filtered by tenant_id.
    """
    
    def __init__(self, tenant_filter: TenantFilter) -> None:
        self._tenant_filter = tenant_filter
    
    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self._tenant_filter.tenant_id
    
    @property
    def user_id(self) -> str | None:
        """Get user ID."""
        return self._tenant_filter.user_id
    
    def _filter_by_tenant(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter data by tenant ID.
        
        In production, this would be handled by the database (RLS).
        This is a Python-side enforcement as backup.
        """
        return [
            item for item in data
            if item.get("tenant_id") == self.tenant_id
        ]
    
    def _require_tenant(self) -> None:
        """Require valid tenant scope."""
        if not self.tenant_id:
            raise TenantScopeError("Tenant ID required for data access")


class TenantDataStore:
    """In-memory tenant data store with isolation.
    
    In production, replace with database with Row-Level Security (RLS).
    """
    
    def __init__(self) -> None:
        # Data is keyed by tenant_id
        self._data: dict[str, dict[str, list[dict]]] = {}
    
    def create(
        self,
        tenant_id: str,
        collection: str,
        document: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a document for a tenant.
        
        Args:
            tenant_id: Tenant ID
            collection: Collection name
            document: Document to create
            
        Returns:
            Created document
        """
        if tenant_id not in self._data:
            self._data[tenant_id] = {}
        
        if collection not in self._data[tenant_id]:
            self._data[tenant_id][collection] = []
        
        # Add tenant_id to document
        doc = {"tenant_id": tenant_id, **document}
        self._data[tenant_id][collection].append(doc)
        
        return doc
    
    def find(
        self,
        tenant_id: str,
        collection: str,
        query: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Find documents for a tenant.
        
        Args:
            tenant_id: Tenant ID
            collection: Collection name
            query: Optional query filter
            
        Returns:
            List of matching documents
        """
        if tenant_id not in self._data:
            return []
        
        if collection not in self._data[tenant_id]:
            return []
        
        results = self._data[tenant_id][collection]
        
        if query:
            # Apply query filters
            results = [
                doc for doc in results
                if all(doc.get(k) == v for k, v in query.items())
            ]
        
        return results
    
    def find_one(
        self,
        tenant_id: str,
        collection: str,
        query: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Find a single document for a tenant."""
        results = self.find(tenant_id, collection, query)
        return results[0] if results else None
    
    def update(
        self,
        tenant_id: str,
        collection: str,
        query: dict[str, Any],
        update: dict[str, Any]
    ) -> int:
        """Update documents for a tenant.
        
        Returns:
            Number of documents updated
        """
        if tenant_id not in self._data:
            return 0
        
        if collection not in self._data[tenant_id]:
            return 0
        
        count = 0
        for doc in self._data[tenant_id][collection]:
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update)
                count += 1
        
        return count
    
    def delete(
        self,
        tenant_id: str,
        collection: str,
        query: dict[str, Any]
    ) -> int:
        """Delete documents for a tenant.
        
        Returns:
            Number of documents deleted
        """
        if tenant_id not in self._data:
            return 0
        
        if collection not in self._data[tenant_id]:
            return 0
        
        original_len = len(self._data[tenant_id][collection])
        self._data[tenant_id][collection] = [
            doc for doc in self._data[tenant_id][collection]
            if not all(doc.get(k) == v for k, v in query.items())
        ]
        
        return original_len - len(self._data[tenant_id][collection])
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete all data for a tenant."""
        if tenant_id in self._data:
            del self._data[tenant_id]
            return True
        return False


# Singleton instance
_tenant_store = TenantDataStore()


def get_tenant_data_store() -> TenantDataStore:
    """Get the default tenant data store."""
    return _tenant_store
