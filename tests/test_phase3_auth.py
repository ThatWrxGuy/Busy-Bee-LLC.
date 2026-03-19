# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Tests for BB-ARCH-PROD-004: Identity & Authorization."""

import pytest
import time

# Import from stub (app.ml package)
from app.ml import MLGovernancePolicy, PlanUpgradeRequired

from busybee_contracts.tenant_context import (
    TenantContext,
    create_personal_context,
    create_saas_context,
)
from infrastructure.auth.jwt_service import (
    JWTService,
    JWTPayload,
    JWTExpiredError,
    JWTInvalidSignatureError,
    JWTMissingClaimError,
    create_jwt_token,
    verify_jwt_token,
)


class TestJWTServices:
    """Test JWT service."""
    
    def test_create_and_verify_token(self):
        """Create and verify a valid token."""
        service = JWTService("test-secret")
        
        payload = JWTPayload(
            subject="user-123",
            tenant_id="tenant-456",
            mode="saas",
            plan="pro",
            permissions=["read", "write"]
        )
        
        token = service.create_token(payload)
        verified = service.verify_token(token)
        
        assert verified.subject == "user-123"
        assert verified.tenant_id == "tenant-456"
        assert verified.mode == "saas"
        assert verified.plan == "pro"
        assert "read" in verified.permissions
    
    def test_expired_token_raises(self):
        """Expired token raises JWTExpiredError."""
        service = JWTService("test-secret")
        
        payload = JWTPayload(
            subject="user-123",
            tenant_id="tenant-456",
            mode="saas",
            expires_at=int(time.time()) - 100  # Expired
        )
        
        token = service.create_token(payload)
        
        with pytest.raises(JWTExpiredError):
            service.verify_token(token)
    
    def test_invalid_signature_raises(self):
        """Invalid signature raises JWTInvalidSignatureError."""
        service1 = JWTService("secret-1")
        service2 = JWTService("secret-2")
        
        payload = JWTPayload(subject="user-123")
        token = service1.create_token(payload)
        
        with pytest.raises(JWTInvalidSignatureError):
            service2.verify_token(token)
    
    def test_missing_tenant_for_saas_raises(self):
        """SaaS mode without tenant raises."""
        service = JWTService("test-secret")
        
        payload = JWTPayload(
            subject="user-123",
            mode="saas",
            tenant_id=None  # Missing!
        )
        
        token = service.create_token(payload)
        
        with pytest.raises(JWTMissingClaimError):
            service.verify_token(token)
    
    def test_missing_subject_raises(self):
        """Missing subject raises."""
        service = JWTService("test-secret")
        
        # Create token with empty subject
        payload = JWTPayload(subject="")
        token = service.create_token(payload)
        
        with pytest.raises(JWTMissingClaimError):
            service.verify_token(token)


class TestTenantContextFromJWT:
    """Test TenantContext.from_jwt_payload."""
    
    def test_create_saas_context_from_jwt(self):
        """Create SaaS context from JWT payload."""
        payload = JWTPayload(
            subject="user-123",
            tenant_id="tenant-456",
            mode="saas",
            plan="enterprise",
            permissions=["finance:read", "finance:execute"]
        )
        
        context = TenantContext.from_jwt_payload(payload)
        
        assert context.user_id == "user-123"
        assert context.tenant_id == "tenant-456"
        assert context.is_saas
        assert context.plan_tier == "enterprise"
        assert "finance:read" in context.permissions
        assert context.metadata["source"] == "jwt"
    
    def test_create_personal_context_from_jwt(self):
        """Create personal context from JWT payload."""
        payload = JWTPayload(
            subject="owner",
            mode="personal",
        )
        
        context = TenantContext.from_jwt_payload(payload)
        
        assert context.is_personal
        assert context.user_id == "owner"
        assert "*" in context.permissions
    
    def test_saas_without_tenant_raises(self):
        """SaaS without tenant_id raises."""
        payload = JWTPayload(
            subject="user-123",
            mode="saas",
            tenant_id=None
        )
        
        with pytest.raises(ValueError, match="tenant_id"):
            TenantContext.from_jwt_payload(payload)


class TestPlanEnforcement:
    """Test plan tier capability enforcement."""
    
    def test_free_plan_blocked_from_execute(self):
        """Free plan blocked from finance execute."""
        policy = MLGovernancePolicy()
        
        context = create_saas_context(
            tenant_id="t1",
            user_id="u1",
            plan_tier="free"
        )
        
        with pytest.raises(PlanUpgradeRequired):
            policy.check_capability("finance", "execute", context)
    
    def test_pro_plan_allowed_simulate(self):
        """Pro plan allowed to simulate finance."""
        policy = MLGovernancePolicy()
        
        context = create_saas_context(
            tenant_id="t1",
            user_id="u1",
            plan_tier="pro"
        )
        
        # Should not raise
        assert policy.check_capability("finance", "simulate", context)
    
    def test_enterprise_allowed_execute(self):
        """Enterprise plan allowed full execution."""
        policy = MLGovernancePolicy()
        
        context = create_saas_context(
            tenant_id="t1",
            user_id="u1",
            plan_tier="enterprise"
        )
        
        # Should not raise
        assert policy.check_capability("finance", "execute", context)


class TestDataIsolation:
    """Test tenant data isolation."""
    
    def test_tenant_cannot_access_other_data(self):
        """Tenant cannot see another tenant's data."""
        from infrastructure.tenant.data_isolation import TenantDataStore
        
        store = TenantDataStore()
        
        # Tenant A creates data
        store.create("tenant-a", "transactions", {"id": "tx1", "amount": 100})
        
        # Tenant B creates data
        store.create("tenant-b", "transactions", {"id": "tx2", "amount": 200})
        
        # Tenant A can only see their data
        results = store.find("tenant-a", "transactions")
        assert len(results) == 1
        assert results[0]["id"] == "tx1"
        
        # Tenant B can only see their data
        results = store.find("tenant-b", "transactions")
        assert len(results) == 1
        assert results[0]["id"] == "tx2"
    
    def test_delete_tenant_removes_all_data(self):
        """Deleting tenant removes all their data."""
        from infrastructure.tenant.data_isolation import TenantDataStore
        
        store = TenantDataStore()
        
        store.create("tenant-a", "transactions", {"id": "tx1"})
        store.create("tenant-a", "accounts", {"id": "acc1"})
        
        # Delete tenant
        store.delete_tenant("tenant-a")
        
        # Verify all data gone
        assert store.find("tenant-a", "transactions") == []
        assert store.find("tenant-a", "accounts") == []


class TestMiddlewareEnforcement:
    """Test middleware enforcement logic."""
    
    def test_missing_auth_header_rejected(self):
        """Missing Authorization header is rejected."""
        # This would require actual HTTP testing
        # Here we test the JWT validation logic
        
        service = JWTService("secret")
        
        # No token
        with pytest.raises(Exception):  # Would be JSONResponse in middleware
            service.verify_token("")
    
    def test_malformed_token_rejected(self):
        """Malformed token is rejected."""
        service = JWTService("secret")
        
        with pytest.raises(Exception):
            service.verify_token("not.a.valid.token")


class TestCapabilityMatrix:
    """Test capability matrix."""
    
    def test_free_read_only(self):
        """Free plan has read-only access."""
        policy = MLGovernancePolicy()
        
        context = create_saas_context("t1", "u1", plan_tier="free")
        
        # Read should work
        assert policy.check_capability("finance", "read", context)
        
        # Simulate should fail
        with pytest.raises(PlanUpgradeRequired):
            policy.check_capability("finance", "simulate", context)
    
    def test_enterprise_full_access(self):
        """Enterprise has full access."""
        policy = MLGovernancePolicy()
        
        context = create_saas_context("t1", "u1", plan_tier="enterprise")
        
        # All actions should work
        assert policy.check_capability("finance", "read", context)
        assert policy.check_capability("finance", "simulate", context)
        assert policy.check_capability("finance", "execute", context)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
