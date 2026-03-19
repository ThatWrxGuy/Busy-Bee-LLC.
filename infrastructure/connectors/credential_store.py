# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Credential Vault for encrypted per-tenant connector storage.

This module provides secure credential storage with encryption,
ensuring each tenant's credentials are isolated and protected.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

from busybee_contracts.tenant_context import TenantContext


# Key derivation for tenant-specific encryption
def _derive_key(tenant_id: str, salt: bytes) -> bytes:
    """Derive encryption key from tenant ID."""
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(tenant_id.encode()))


@dataclass
class StoredCredential:
    """A stored credential with metadata."""
    connector_name: str
    encrypted_data: bytes
    created_at: datetime
    expires_at: datetime | None = None
    last_synced: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class CredentialVaultError(Exception):
    """Base exception for credential vault errors."""
    pass


class CredentialNotFoundError(CredentialVaultError):
    """Raised when credential is not found."""
    pass


class CredentialExpiredError(CredentialVaultError):
    """Raised when credential has expired."""
    pass


class CredentialVault:
    """Secure vault for storing connector credentials per tenant.
    
    Each tenant gets their own encryption key derived from their tenant_id.
    This ensures tenant isolation at the storage level.
    """

    def __init__(self, master_key: str | None = None) -> None:
        """Initialize the vault.
        
        Args:
            master_key: Optional master key for key derivation.
                       In production, load from secure vault (Vault, AWS Secrets, etc.)
        """
        self._master_key = master_key or os.environ.get(
            "CREDENTIAL_VAULT_KEY",
            secrets.token_urlsafe(32)
        )
        self._salt = os.environ.get(
            "CREDENTIAL_VAULT_SALT",
            secrets.token_bytes(16)
        ).encode()
        
        # In-memory store (in production, use encrypted database)
        # tenant_id -> connector_name -> StoredCredential
        self._store: dict[str, dict[str, StoredCredential]] = {}

    def _get_fernet(self, tenant_id: str) -> Fernet:
        """Get Fernet instance for tenant-specific encryption."""
        key = _derive_key(tenant_id, self._salt)
        return Fernet(key)

    def store(
        self,
        context: TenantContext,
        connector_name: str,
        credentials: dict[str, str],
        expires_at: datetime | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """Store credentials for a connector.
        
        Args:
            context: Tenant context for isolation
            connector_name: Name of the connector
            credentials: Credential key-value pairs to store
            expires_at: Optional expiration datetime
            metadata: Optional metadata about the credential
        """
        if not context.tenant_id:
            raise CredentialVaultError("Cannot store credentials without tenant_id")

        # Serialize and encrypt
        data = json.dumps(credentials).encode()
        fernet = self._get_fernet(context.tenant_id)
        encrypted = fernet.encrypt(data)

        stored = StoredCredential(
            connector_name=connector_name,
            encrypted_data=encrypted,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_synced=datetime.utcnow(),
            metadata=metadata or {}
        )

        # Store per tenant
        if context.tenant_id not in self._store:
            self._store[context.tenant_id] = {}
        
        self._store[context.tenant_id][connector_name] = stored

    def retrieve(
        self,
        context: TenantContext,
        connector_name: str
    ) -> dict[str, str]:
        """Retrieve credentials for a connector.
        
        Args:
            context: Tenant context for isolation
            connector_name: Name of the connector
            
        Returns:
            Decrypted credential key-value pairs
            
        Raises:
            CredentialNotFoundError: If credentials not found
            CredentialExpiredError: If credentials have expired
        """
        if not context.tenant_id:
            raise CredentialVaultError("Cannot retrieve credentials without tenant_id")

        tenant_store = self._store.get(context.tenant_id, {})
        stored = tenant_store.get(connector_name)
        
        if stored is None:
            raise CredentialNotFoundError(
                f"No credentials found for connector={connector_name}"
            )

        # Check expiration
        if stored.expires_at and stored.expires_at < datetime.utcnow():
            raise CredentialExpiredError(
                f"Credentials for {connector_name} have expired"
            )

        # Decrypt
        fernet = self._get_fernet(context.tenant_id)
        decrypted = fernet.decrypt(stored.encrypted_data)
        return json.loads(decrypted)

    def delete(
        self,
        context: TenantContext,
        connector_name: str
    ) -> bool:
        """Delete credentials for a connector.
        
        Args:
            context: Tenant context for isolation
            connector_name: Name of the connector
            
        Returns:
            True if deleted, False if not found
        """
        if not context.tenant_id:
            return False

        tenant_store = self._store.get(context.tenant_id, {})
        if connector_name in tenant_store:
            del tenant_store[connector_name]
            return True
        return False

    def list_connectors(
        self,
        context: TenantContext
    ) -> list[str]:
        """List all connected connectors for a tenant.
        
        Args:
            context: Tenant context
            
        Returns:
            List of connector names
        """
        if not context.tenant_id:
            return []

        tenant_store = self._store.get(context.tenant_id, {})
        return list(tenant_store.keys())

    def get_status(
        self,
        context: TenantContext,
        connector_name: str
    ) -> dict[str, Any]:
        """Get status of a connector's credentials.
        
        Args:
            context: Tenant context
            connector_name: Name of the connector
            
        Returns:
            Status dict with expiry, last_sync, etc.
        """
        if not context.tenant_id:
            return {"status": "disconnected"}

        tenant_store = self._store.get(context.tenant_id, {})
        stored = tenant_store.get(connector_name)
        
        if stored is None:
            return {"status": "disconnected"}

        # Determine status
        status = "active"
        if stored.expires_at and stored.expires_at < datetime.utcnow():
            status = "expired"
        elif stored.expires_at and stored.expires_at < datetime.utcnow() + timedelta(days=7):
            status = "expiring_soon"

        return {
            "status": status,
            "connected": True,
            "created_at": stored.created_at.isoformat(),
            "expires_at": stored.expires_at.isoformat() if stored.expires_at else None,
            "last_synced": stored.last_synced.isoformat() if stored.last_synced else None,
            "metadata": stored.metadata
        }

    def update_sync_time(
        self,
        context: TenantContext,
        connector_name: str
    ) -> None:
        """Update the last synced time for a connector.
        
        Args:
            context: Tenant context
            connector_name: Name of the connector
        """
        if not context.tenant_id:
            return

        tenant_store = self._store.get(context.tenant_id, {})
        stored = tenant_store.get(connector_name)
        
        if stored:
            stored.last_synced = datetime.utcnow()


# Singleton instance
_vault: CredentialVault | None = None


def get_credential_vault() -> CredentialVault:
    """Get the default credential vault."""
    global _vault
    if _vault is None:
        _vault = CredentialVault()
    return _vault
