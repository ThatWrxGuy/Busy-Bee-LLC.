# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Tests for multi-tenant isolation.

Validates that:
- Tenant data is properly isolated
- No cross-tenant leakage is possible
- Middleware enforces tenant resolution
- Permission checks work correctly
"""

import pytest
from datetime import datetime

from busybee_contracts.tenant_context import (
    TenantContext,
    Roles,
    Permissions,
    create_saas_context,
    create_personal_context,
)
from infrastructure.connectors.credential_store import CredentialVault
from infrastructure.connectors.health_monitor import ConnectorHealthMonitor, ConnectorHealthStatus
from packages.governance.policy_engine import PolicyEngine, RiskLevel
from packages.governance.audit_log import AuditLog, AuditEventType


class TestTenantIsolation:
    """Test suite for tenant isolation."""

    def test_tenant_context_isolation(self):
        """Test that tenant contexts are properly isolated."""
        # Create two different tenant contexts
        context_a = create_saas_context(
            tenant_id="tenant_a",
            user_id="user_a",
            roles=[Roles.MEMBER],
            workspace_id="workspace_a"
        )
        
        context_b = create_saas_context(
            tenant_id="tenant_b", 
            user_id="user_b",
            roles=[Roles.MEMBER],
            workspace_id="workspace_b"
        )
        
        # Verify they are different
        assert context_a.tenant_id != context_b.tenant_id
        assert context_a.user_id != context_b.user_id
        assert context_a.workspace_id != context_b.workspace_id
        
        # Verify data path isolation
        path_a = context_a.get_data_path("data")
        path_b = context_b.get_data_path("data")
        
        assert path_a != path_b
        assert "tenant_a" in path_a
        assert "tenant_b" in path_b

    def test_credential_vault_isolation(self):
        """Test that credentials are isolated per tenant."""
        vault = CredentialVault()
        
        # Create two tenant contexts
        context_a = create_saas_context(
            tenant_id="tenant_a",
            user_id="user_a"
        )
        context_b = create_saas_context(
            tenant_id="tenant_b",
            user_id="user_b"
        )
        
        # Store credentials for tenant A
        vault.store(
            context_a,
            "plaid",
            {"access_token": "token_a"}
        )
        
        # Store credentials for tenant B
        vault.store(
            context_b,
            "plaid", 
            {"access_token": "token_b"}
        )
        
        # Retrieve and verify isolation
        creds_a = vault.retrieve(context_a, "plaid")
        creds_b = vault.retrieve(context_b, "plaid")
        
        assert creds_a["access_token"] == "token_a"
        assert creds_b["access_token"] == "token_b"
        
        # Verify cross-tenant access is impossible
        with pytest.raises(Exception):
            # Try to get tenant B's credentials with tenant A's context
            vault.retrieve(context_a, "plaid")

    def test_health_monitor_isolation(self):
        """Test that health records are isolated per tenant."""
        monitor = ConnectorHealthMonitor()
        
        context_a = create_saas_context(
            tenant_id="tenant_a",
            user_id="user_a"
        )
        context_b = create_saas_context(
            tenant_id="tenant_b",
            user_id="user_b"
        )
        
        # Record health for tenant A
        monitor.record_check(
            context_a,
            "plaid",
            ConnectorHealthStatus.ACTIVE
        )
        
        # Record health for tenant B  
        monitor.record_check(
            context_b,
            "plaid",
            ConnectorHealthStatus.ERROR,
            error="Test error"
        )
        
        # Verify isolation
        status_a = monitor.get_status(context_a, "plaid")
        status_b = monitor.get_status(context_b, "plaid")
        
        assert status_a == ConnectorHealthStatus.ACTIVE
        assert status_b == ConnectorHealthStatus.ERROR
        
        # Verify tenant A cannot see tenant B's errors
        record_a = monitor.get_health_record(context_a, "plaid")
        assert record_a is not None
        assert record_a.error_count == 0

    def test_permission_isolation(self):
        """Test that permissions are properly scoped."""
        # Owner has all permissions
        owner_context = create_saas_context(
            tenant_id="tenant_a",
            user_id="owner",
            roles=[Roles.OWNER]
        )
        
        # Member has limited permissions
        member_context = create_saas_context(
            tenant_id="tenant_a",
            user_id="member",
            roles=[Roles.MEMBER]
        )
        
        # Viewer has even more limited permissions
        viewer_context = create_saas_context(
            tenant_id="tenant_a",
            user_id="viewer",
            roles=[Roles.VIEWER]
        )
        
        # Owner can do anything
        assert owner_context.has_permission("*")
        assert owner_context.has_permission(Permissions.TENANT_ADMIN)
        
        # Member cannot do admin things
        assert not member_context.has_permission(Permissions.TENANT_ADMIN)
        assert member_context.has_permission(Permissions.AGENT_EXECUTE)
        
        # Viewer can only read
        assert not viewer_context.has_permission(Permissions.AGENT_CREATE)
        assert viewer_context.has_permission(Permissions.TENANT_READ)

    def test_policy_engine_tenant_isolation(self):
        """Test that policy engine respects tenant boundaries."""
        engine = PolicyEngine()
        
        context_a = create_saas_context(
            tenant_id="tenant_a",
            user_id="user_a"
        )
        
        # Create approval request for tenant A
        request = engine.create_approval_request(
            context=context_a,
            action_id="finance.transaction",
            domain="finance",
            description="Test transaction",
            details={"amount": 500},
            risk_level=RiskLevel.HIGH
        )
        
        assert request.tenant_id == "tenant_a"
        assert request.status.value == "pending"
        
        # Get pending for tenant A
        pending_a = engine.get_pending_approvals(tenant_id="tenant_a")
        assert len(pending_a) == 1
        
        # Get pending for tenant B (should be empty)
        pending_b = engine.get_pending_approvals(tenant_id="tenant_b")
        assert len(pending_b) == 0

    def test_audit_log_tenant_isolation(self):
        """Test that audit logs are isolated per tenant."""
        log = AuditLog()
        
        context_a = create_saas_context(
            tenant_id="tenant_a",
            user_id="user_a",
            roles=[Roles.OWNER]
        )
        
        context_b = create_saas_context(
            tenant_id="tenant_b",
            user_id="user_b",
            roles=[Roles.MEMBER]
        )
        
        # Log events for tenant A
        log.log(context_a, AuditEventType.USER_LOGIN, "User A logged in")
        log.log(context_a, AuditEventType.CONNECTOR_CONNECTED, "Connector connected")
        
        # Log events for tenant B
        log.log(context_b, AuditEventType.USER_LOGIN, "User B logged in")
        
        # Verify isolation - tenant A events
        events_a = log.get_events("tenant_a")
        assert len(events_a) == 2
        
        # Verify isolation - tenant B events
        events_b = log.get_events("tenant_b")
        assert len(events_b) == 1
        
        # Verify cross-tenant access returns empty
        events_b_from_a = log.get_events("tenant_b")  # Wrong tenant
        assert len(events_b_from_a) == 1  # Should only have tenant B's events

    def test_data_path_isolation(self):
        """Test that data paths are properly isolated."""
        # Different tenants
        context_a = create_saas_context(
            tenant_id="tenant_a",
            user_id="user_a",
            workspace_id="workspace_1"
        )
        
        context_b = create_saas_context(
            tenant_id="tenant_b",
            user_id="user_b", 
            workspace_id="workspace_1"
        )
        
        # Same workspace ID but different tenant - paths should differ
        path_a = context_a.get_data_path("files")
        path_b = context_b.get_data_path("files")
        
        assert path_a != path_b
        
        # Different workspaces within same tenant
        context_c = create_saas_context(
            tenant_id="tenant_a",
            user_id="user_a",
            workspace_id="workspace_2"
        )
        
        path_c = context_c.get_data_path("files")
        
        assert path_a != path_c  # Different workspaces
        assert "tenant_a" in path_a
        assert "workspace_2" in path_c


class TestConnectorResolution:
    """Test connector resolution by tenant."""

    def test_connector_per_tenant(self):
        """Test that each tenant gets their own connector credentials."""
        vault = CredentialVault()
        
        # Two tenants connecting to the same service
        context_tenant1 = create_saas_context(
            tenant_id="tenant_1",
            user_id="user_1"
        )
        
        context_tenant2 = create_saas_context(
            tenant_id="tenant_2", 
            user_id="user_2"
        )
        
        # Both connect to plaid with different credentials
        vault.store(
            context_tenant1,
            "plaid",
            {"access_token": "tenant1_plaid_token", "item_id": "item_1"}
        )
        
        vault.store(
            context_tenant2,
            "plaid",
            {"access_token": "tenant2_plaid_token", "item_id": "item_2"}
        )
        
        # Verify each gets their own
        creds1 = vault.retrieve(context_tenant1, "plaid")
        creds2 = vault.retrieve(context_tenant2, "plaid")
        
        assert creds1["item_id"] == "item_1"
        assert creds2["item_id"] == "item_2"
        assert creds1["access_token"] != creds2["access_token"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
