# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Tests for BB-BIZ-001: Billing & Subscription Enforcement."""

import pytest

from infrastructure.billing.stripe_service import (
    StripeBillingService,
    BillingManager,
    Subscription,
    SubscriptionStatus,
    PlanUpgradeRequiredError,
)


class TestStripeBillingService:
    """Test Stripe billing service."""
    
    def test_create_customer(self):
        """Create a customer."""
        service = StripeBillingService()
        
        customer = service.create_customer(
            tenant_id="tenant-123",
            email="test@example.com",
            name="Test User"
        )
        
        assert customer.tenant_id == "tenant-123"
        assert customer.email == "test@example.com"
        assert customer.name == "Test User"
        assert customer.customer_id.startswith("cus_")
    
    def test_create_subscription(self):
        """Create a subscription."""
        service = StripeBillingService()
        
        subscription = service.create_subscription(
            customer_id="cus_123",
            tenant_id="tenant-123",
            price_id="price_pro_monthly"
        )
        
        assert subscription.tenant_id == "tenant-123"
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.plan == "pro"
    
    def test_subscription_status(self):
        """Test subscription status checks."""
        active_sub = Subscription(
            subscription_id="sub_1",
            customer_id="cus_1",
            tenant_id="t1",
            status=SubscriptionStatus.ACTIVE,
            plan="pro",
            current_period_start=0,
            current_period_end=9999999999
        )
        
        assert active_sub.is_active
        assert active_sub.is_valid
        
        trialing_sub = Subscription(
            subscription_id="sub_2",
            customer_id="cus_2",
            tenant_id="t2",
            status=SubscriptionStatus.TRIALING,
            plan="pro",
            current_period_start=0,
            current_period_end=9999999999
        )
        
        assert trialing_sub.is_trialing
        assert trialing_sub.is_valid
        
        canceled_sub = Subscription(
            subscription_id="sub_3",
            customer_id="cus_3",
            tenant_id="t3",
            status=SubscriptionStatus.CANCELED,
            plan="pro",
            current_period_start=0,
            current_period_end=9999999999
        )
        
        assert not canceled_sub.is_active
        assert not canceled_sub.is_valid


class TestBillingManager:
    """Test billing manager feature access."""
    
    def test_free_tier_read_only(self):
        """Free tier has read-only access."""
        manager = BillingManager(StripeBillingService())
        
        # No subscription = free tier
        assert manager.check_feature_access("tenant-1", "finance:read")
        assert manager.check_feature_access("tenant-1", "health:read")
        
        # No execute
        assert not manager.check_feature_access("tenant-1", "finance:execute")
        assert not manager.check_feature_access("tenant-1", "health:execute")
    
    def test_pro_tier_simulate(self):
        """Pro tier can simulate."""
        service = StripeBillingService()
        manager = BillingManager(service)
        
        # Add pro subscription
        sub = Subscription(
            subscription_id="sub_1",
            customer_id="cus_1",
            tenant_id="tenant-pro",
            status=SubscriptionStatus.ACTIVE,
            plan="pro",
            current_period_start=0,
            current_period_end=9999999999
        )
        manager.sync_subscription("tenant-pro", sub)
        
        # Pro can read and simulate
        assert manager.check_feature_access("tenant-pro", "finance:read")
        assert manager.check_feature_access("tenant-pro", "finance:simulate")
        
        # But not execute
        assert not manager.check_feature_access("tenant-pro", "finance:execute")
    
    def test_enterprise_full_access(self):
        """Enterprise has full access."""
        service = StripeBillingService()
        manager = BillingManager(service)
        
        # Add enterprise subscription
        sub = Subscription(
            subscription_id="sub_2",
            customer_id="cus_2",
            tenant_id="tenant-ent",
            status=SubscriptionStatus.ACTIVE,
            plan="enterprise",
            current_period_start=0,
            current_period_end=9999999999
        )
        manager.sync_subscription("tenant-ent", sub)
        
        # Enterprise can do everything
        assert manager.check_feature_access("tenant-ent", "finance:read")
        assert manager.check_feature_access("tenant-ent", "finance:simulate")
        assert manager.check_feature_access("tenant-ent", "finance:execute")
        assert manager.check_feature_access("tenant-ent", "health:execute")
        assert manager.check_feature_access("tenant-ent", "career:execute")
    
    def test_require_feature_raises(self):
        """require_feature raises when not allowed."""
        manager = BillingManager(StripeBillingService())
        
        with pytest.raises(PlanUpgradeRequiredError):
            manager.require_feature("tenant-1", "finance:execute")
    
    def test_canceled_subscription_no_access(self):
        """Canceled subscription loses access."""
        service = StripeBillingService()
        manager = BillingManager(service)
        
        # Add canceled subscription
        sub = Subscription(
            subscription_id="sub_1",
            customer_id="cus_1",
            tenant_id="tenant-canceled",
            status=SubscriptionStatus.CANCELED,
            plan="pro",
            current_period_start=0,
            current_period_end=9999999999,
            cancel_at_period_end=True
        )
        manager.sync_subscription("tenant-canceled", sub)
        
        # No longer valid
        assert not sub.is_valid
        
        # Should fall back to free tier
        assert not manager.check_feature_access("tenant-canceled", "finance:simulate")


class TestWebhookProcessing:
    """Test webhook event processing."""
    
    def test_webhook_signature_verification(self):
        """Verify webhook signature."""
        import hmac
        import hashlib
        
        service = StripeBillingService(webhook_secret="test-secret")
        
        payload = b'{"type":"test.event","data":{"object":{"id":"evt_123"}}}'
        signature = hmac.new(
            b"test-secret",
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Should not raise
        result = service.verify_webhook_signature(payload, signature)
        assert result["type"] == "test.event"
    
    def test_webhook_signature_invalid(self):
        """Invalid signature raises."""
        from infrastructure.billing.stripe_service import WebhookVerificationError
        
        service = StripeBillingService(webhook_secret="test-secret")
        
        with pytest.raises(WebhookVerificationError):
            service.verify_webhook_signature(b'{}', "invalid-signature")
    
    def test_process_webhook_events(self):
        """Process various webhook events."""
        service = StripeBillingService()
        
        # Customer subscription created
        result = service.process_webhook_event(
            "customer.subscription.created",
            {"id": "sub_123", "metadata": {"tenant_id": "t1"}}
        )
        assert result["status"] == "created"
        
        # Invoice payment succeeded
        result = service.process_webhook_event(
            "invoice.payment_succeeded",
            {"id": "in_123"}
        )
        assert result["status"] == "paid"
        
        # Unknown event
        result = service.process_webhook_event(
            "unknown.event",
            {}
        )
        assert result["status"] == "ignored"


class TestPlanPricing:
    """Test plan pricing IDs."""
    
    def test_price_ids_exist(self):
        """All plan price IDs are defined."""
        service = StripeBillingService()
        
        assert service.PRICE_IDS["free"] is None
        assert service.PRICE_IDS["pro_monthly"] == "price_pro_monthly"
        assert service.PRICE_IDS["enterprise_yearly"] == "price_enterprise_yearly"
    
    def test_plan_tier_mapping(self):
        """Price IDs map to correct tiers."""
        service = StripeBillingService()
        
        assert service.PLAN_TIERS["price_pro_monthly"] == "pro"
        assert service.PLAN_TIERS["price_pro_yearly"] == "pro"
        assert service.PLAN_TIERS["price_enterprise_monthly"] == "enterprise"
        assert service.PLAN_TIERS["price_enterprise_yearly"] == "enterprise"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
