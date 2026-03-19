# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Connector Credential Resolver.

Enforces tenant-scoped connector access.
"""

from __future__ import annotations

from typing import Any, Protocol, TypeVar
from busybee_contracts.tenant_context import TenantContext


class ConnectorClient(Protocol):
    """Protocol for connector clients."""
    
    def get_accounts(self) -> list[dict[str, Any]]:
        """Get accounts for the scoped context."""
        ...


class ConnectorCredentialError(ValueError):
    """Raised when credential resolution fails."""
    pass


class ConnectorScopeError(ConnectorCredentialError):
    """Raised when tenant scope is missing."""
    pass


class ConnectorCredentialResolver:
    """Resolves credentials for tenant-scoped connector access.
    
    This is critical for SaaS multi-tenant isolation.
    Each tenant gets their own credentials, never shared.
    """
    
    def __init__(self) -> None:
        # In production, this would load from secure vault
        self._credential_store: dict[str, dict[str, str]] = {}
    
    def resolve(
        self,
        provider: str,
        context: TenantContext,
        required_permission: str = "read"
    ) -> dict[str, str]:
        """Resolve credentials for a connector provider.
        
        Args:
            provider: Provider name (e.g., "plaid", "yahoo", "google")
            context: TenantContext for scoping
            required_permission: Required permission level
            
        Returns:
            Dict of credentials for the provider
            
        Raises:
            ConnectorScopeError: If tenant scope missing
            ConnectorCredentialError: If credentials not found
        """
        # Enforce tenant scope for SaaS
        if context.is_saas:
            context.require_scope()
        
        # Build credential key
        cred_key = self._build_cred_key(provider, context)
        
        # Look up credentials
        if cred_key not in self._credential_store:
            # In production, would fetch from vault/secrets manager
            raise ConnectorCredentialError(
                f"No credentials found for provider={provider}, tenant={context.tenant_id}"
            )
        
        creds = self._credential_store[cred_key]
        
        # Check permission
        if not context.has_permission(required_permission):
            raise ConnectorCredentialError(
                f"Missing required permission: {required_permission}"
            )
        
        return creds
    
    def register_credentials(
        self,
        provider: str,
        context: TenantContext,
        credentials: dict[str, str]
    ) -> None:
        """Register credentials for a provider and tenant.
        
        In production, this would go to a secure vault.
        """
        cred_key = self._build_cred_key(provider, context)
        self._credential_store[cred_key] = credentials
    
    def _build_cred_key(self, provider: str, context: TenantContext) -> str:
        """Build credential lookup key."""
        if context.is_personal:
            return f"personal:{provider}"
        return f"saas:{context.tenant_id}:{provider}"


class ConnectorFactory:
    """Factory for creating tenant-scoped connector clients."""
    
    def __init__(self, resolver: ConnectorCredentialResolver) -> None:
        self.resolver = resolver
    
    def for_context(self, context: TenantContext) -> "_TenantScopedConnectors":
        """Create tenant-scoped connector wrapper."""
        return _TenantScopedConnectors(context, self.resolver)


class _TenantScopedConnectors:
    """Tenant-scoped connector access."""
    
    def __init__(self, context: TenantContext, resolver: ConnectorCredentialResolver):
        self._context = context
        self._resolver = resolver
    
    @property
    def plaid(self) -> dict[str, str]:
        """Get Plaid credentials."""
        return self._resolver.resolve("plaid", self._context, "read")
    
    @property
    def yahoo(self) -> dict[str, str]:
        """Get Yahoo Finance credentials."""
        return self._resolver.resolve("yahoo", self._context, "read")
    
    @property
    def google(self) -> dict[str, str]:
        """Get Google credentials."""
        return self._resolver.resolve("google", self._context, "read")
    
    def get_credential(self, provider: str) -> dict[str, str]:
        """Get credentials for any provider."""
        return self._resolver.resolve(provider, self._context, "read")


# Singleton instance
_default_resolver = ConnectorCredentialResolver()


def get_connector_factory() -> ConnectorFactory:
    """Get the default connector factory."""
    return ConnectorFactory(_default_resolver)
