# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Tests for BB-ARCH-PROD-003: Tenant Context Propagation."""

import pytest
from busybee_contracts.tenant_context import (
    TenantContext,
    create_personal_context,
    create_saas_context,
)


class TestTenantContext:
    """Test TenantContext contract."""
    
    def test_personal_context_has_full_permissions(self):
        """Personal mode has wildcard permissions."""
        ctx = create_personal_context()
        
        assert ctx.is_personal
        assert ctx.mode == "personal"
        assert ctx.tenant_id == "personal-local"
        assert ctx.user_id == "owner"
        assert "*" in ctx.permissions
        assert ctx.plan_tier == "owner"
    
    def test_saas_context_requires_scope(self):
        """SaaS context must have tenant and user."""
        ctx = create_saas_context(
            tenant_id="tenant-123",
            user_id="user-456",
            permissions=["read", "write"],
            plan_tier="pro"
        )
        
        assert ctx.is_saas
        assert ctx.mode == "saas"
        assert ctx.tenant_id == "tenant-123"
        assert ctx.user_id == "user-456"
        assert "read" in ctx.permissions
        assert ctx.plan_tier == "pro"
    
    def test_saas_require_tenant_raises(self):
        """SaaS without tenant_id raises."""
        ctx = TenantContext(
            tenant_id=None,
            user_id="user",
            mode="saas"
        )
        
        with pytest.raises(ValueError, match="tenant_id"):
            ctx.require_tenant()
    
    def test_saas_require_user_raises(self):
        """SaaS without user_id raises."""
        ctx = TenantContext(
            tenant_id="tenant",
            user_id=None,
            mode="saas"
        )
        
        with pytest.raises(ValueError, match="user_id"):
            ctx.require_user()
    
    def test_personal_no_tenant_required(self):
        """Personal mode doesn't require tenant."""
        ctx = create_personal_context()
        
        # Should not raise
        ctx.require_tenant()
        ctx.require_user()
    
    def test_has_permission(self):
        """Permission checking works."""
        ctx = TenantContext(
            tenant_id="t",
            user_id="u",
            mode="saas",
            permissions=frozenset({"read", "write"})
        )
        
        assert ctx.has_permission("read")
        assert ctx.has_permission("write")
        assert not ctx.has_permission("delete")
    
    def test_wildcard_permission(self):
        """Wildcard grants all permissions."""
        ctx = create_personal_context()
        
        assert ctx.has_permission("anything")
        assert ctx.has_permission("delete")
    
    def test_to_lineage(self):
        """Lineage export works."""
        ctx = create_saas_context(
            tenant_id="t1",
            user_id="u1",
            plan_tier="enterprise"
        )
        
        lineage = ctx.to_lineage()
        
        assert lineage["tenant_id"] == "t1"
        assert lineage["user_id"] == "u1"
        assert lineage["mode"] == "saas"
        assert lineage["plan_tier"] == "enterprise"


class TestConnectorScope:
    """Test connector scope enforcement."""
    
    def test_personal_connector_allowed(self):
        """Personal mode can access connectors."""
        ctx = create_personal_context()
        
        # No exception should be raised
        ctx.require_scope()  # Should pass for personal
    
    def test_saas_missing_tenant_blocked(self):
        """SaaS without tenant is blocked."""
        ctx = TenantContext(
            tenant_id=None,
            user_id="user",
            mode="saas"
        )
        
        with pytest.raises(ValueError):
            ctx.require_scope()


class TestGovernancePolicy:
    """Test governance policy branching."""
    
    def test_finance_requires_review_always(self):
        """Finance always requires human review."""
        from app.ml.governance.policy import MLGovernancePolicy
        
        policy = MLGovernancePolicy()
        
        personal_ctx = create_personal_context()
        saas_ctx = create_saas_context("t", "u")
        
        # Both should require review for finance
        assert policy.requires_human_review("finance", personal_ctx)
        assert policy.requires_human_review("finance", saas_ctx)
    
    def test_saas_stricter_than_personal(self):
        """SaaS has stricter policies."""
        from app.ml.governance.policy import MLGovernancePolicy
        
        policy = MLGovernancePolicy()
        
        personal_ctx = create_personal_context()
        saas_ctx = create_saas_context("t", "u")
        
        # Career requires review in SaaS, not in personal
        assert not policy.requires_human_review("career", personal_ctx)
        assert policy.requires_human_review("career", saas_ctx)


class TestInferenceGateway:
    """Test inference gateway with context."""
    
    def test_gateway_accepts_context(self):
        """Gateway works with TenantContext."""
        from app.ml.models.sklearn_models import BaselineStrategyScoreModel
        from app.ml.common.contracts import PredictionRequest
        from app.ml.registry.model_registry import ModelRegistry
        from app.ml.governance.policy import MLGovernancePolicy
        from app.ml.inference.gateway import InferenceGateway
        
        # Setup
        registry = ModelRegistry()
        registry.register(BaselineStrategyScoreModel())
        policy = MLGovernancePolicy()
        gateway = InferenceGateway(registry, policy)
        
        # Request
        request = PredictionRequest(
            task_name="strategy_score",
            entity_id="user-001",
            features={"risk_score": 0.3, "readiness_score": 0.8, "stability_score": 0.7},
            source_domains=["finance"],
        )
        
        # Execute with personal context
        personal_ctx = create_personal_context()
        result = gateway.predict(request, context=personal_ctx)
        
        assert result is not None
        assert result.model_name == "baseline_strategy_score"
        assert "lineage" in result.metadata
        assert result.metadata["mode"] == "personal"
    
    def test_saas_without_context_raises(self):
        """SaaS without context raises."""
        from app.ml.models.sklearn_models import BaselineStrategyScoreModel
        from app.ml.common.contracts import PredictionRequest
        from app.ml.registry.model_registry import ModelRegistry
        from app.ml.governance.policy import MLGovernancePolicy
        from app.ml.inference.gateway import InferenceGateway
        
        registry = ModelRegistry()
        registry.register(BaselineStrategyScoreModel())
        policy = MLGovernancePolicy()
        gateway = InferenceGateway(registry, policy)
        
        request = PredictionRequest(
            task_name="strategy_score",
            entity_id="user-001",
            features={"risk_score": 0.3, "readiness_score": 0.8, "stability_score": 0.7},
            source_domains=["finance"],
        )
        
        # SaaS context without scope
        saas_ctx = TenantContext(tenant_id=None, user_id=None, mode="saas")
        
        with pytest.raises(ValueError):
            gateway.predict(request, context=saas_ctx)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
