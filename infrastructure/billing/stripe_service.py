# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Stripe Billing Service for subscription management.

This service integrates with Stripe for payment processing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import hashlib
import hmac
import json
import time


class BillingError(Exception):
    """Base billing exception."""
    pass


class SubscriptionInactiveError(BillingError):
    """Raised when subscription is not active."""
    pass


class PlanUpgradeRequiredError(BillingError):
    """Raised when action requires upgrade."""
    pass


class WebhookVerificationError(BillingError):
    """Raised when webhook signature is invalid."""
    pass


class SubscriptionStatus(str, Enum):
    """Stripe subscription status."""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


@dataclass
class Subscription:
    """Subscription details from Stripe."""
    subscription_id: str
    customer_id: str
    tenant_id: str
    status: SubscriptionStatus
    plan: str
    current_period_start: int
    current_period_end: int
    cancel_at_period_end: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING)
    
    @property
    def is_trialing(self) -> bool:
        """Check if in trial period."""
        return self.status == SubscriptionStatus.TRIALING
    
    @property
    def is_valid(self) -> bool:
        """Check if subscription is valid (active or trial)."""
        return self.is_active and not self.cancel_at_period_end


@dataclass
class Customer:
    """Stripe customer details."""
    customer_id: str
    tenant_id: str
    email: str
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class StripeBillingService:
    """Service for Stripe subscription management.
    
    In production, this would use the Stripe Python SDK.
    This is a demonstration implementation.
    """
    
    # Plan pricing IDs (Stripe Price IDs)
    PRICE_IDS = {
        "free": None,  # No Stripe subscription
        "pro_monthly": "price_pro_monthly",
        "pro_yearly": "price_pro_yearly",
        "enterprise_monthly": "price_enterprise_monthly",
        "enterprise_yearly": "price_enterprise_yearly",
    }
    
    # Plan tier mapping
    PLAN_TIERS = {
        "price_pro_monthly": "pro",
        "price_pro_yearly": "pro",
        "price_enterprise_monthly": "enterprise",
        "price_enterprise_yearly": "enterprise",
    }
    
    def __init__(
        self,
        secret_key: str | None = None,
        webhook_secret: str | None = None
    ) -> None:
        self.secret_key = secret_key or "sk_test_xxx"
        self.webhook_secret = webhook_secret or "whsec_xxx"
        # In production: stripe.api_key = secret_key
    
    def create_customer(
        self,
        tenant_id: str,
        email: str,
        name: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> Customer:
        """Create a Stripe customer for a tenant.
        
        Args:
            tenant_id: Tenant ID
            email: Customer email
            name: Optional customer name
            metadata: Optional metadata
            
        Returns:
            Customer object
        """
        # In production: stripe.Customer.create(email=email, name=name, ...)
        customer_id = f"cus_{self._generate_id()}"
        
        return Customer(
            customer_id=customer_id,
            tenant_id=tenant_id,
            email=email,
            name=name,
            metadata=metadata or {}
        )
    
    def create_subscription(
        self,
        customer_id: str,
        tenant_id: str,
        price_id: str
    ) -> Subscription:
        """Create a subscription for a customer.
        
        Args:
            customer_id: Stripe customer ID
            tenant_id: Tenant ID
            price_id: Stripe price ID
            
        Returns:
            Subscription object
        """
        # In production: stripe.Subscription.create(customer=customer_id, items=[...])
        subscription_id = f"sub_{self._generate_id()}"
        now = int(time.time())
        
        return Subscription(
            subscription_id=subscription_id,
            customer_id=customer_id,
            tenant_id=tenant_id,
            status=SubscriptionStatus.ACTIVE,
            plan=self.PLAN_TIERS.get(price_id, "free"),
            current_period_start=now,
            current_period_end=now + 30 * 24 * 3600,  # 30 days
        )
    
    def get_subscription(
        self,
        subscription_id: str
    ) -> Subscription | None:
        """Get subscription details.
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Subscription or None if not found
        """
        # In production: stripe.Subscription.retrieve(subscription_id)
        # This is a mock implementation
        return None
    
    def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Subscription:
        """Cancel a subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            immediately: Cancel immediately or at period end
            
        Returns:
            Updated subscription
        """
        # In production: stripe.Subscription.modify(subscription_id, cancel_at_period_end=...)
        raise NotImplementedError("Use Stripe SDK in production")
    
    def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str
    ) -> Subscription:
        """Update subscription to new price.
        
        Args:
            subscription_id: Stripe subscription ID
            new_price_id: New Stripe price ID
            
        Returns:
            Updated subscription
        """
        # In production: stripe.Subscription.modify with proration behavior
        raise NotImplementedError("Use Stripe SDK in production")
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> dict[str, Any]:
        """Verify webhook signature from Stripe.
        
        Args:
            payload: Raw webhook payload
            signature: Stripe-Signature header value
            
        Returns:
            Webhook event data
            
        Raises:
            WebhookVerificationError: If signature is invalid
        """
        # In production: stripe.Webhook.construct_event(payload, signature, webhook_secret)
        
        # Simple HMAC verification (demo)
        expected_sig = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            raise WebhookVerificationError("Invalid webhook signature")
        
        return json.loads(payload)
    
    def process_webhook_event(
        self,
        event_type: str,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a webhook event from Stripe.
        
        Args:
            event_type: Stripe event type
            data: Event data
            
        Returns:
            Processed result
        """
        handlers = {
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(data)
        
        return {"status": "ignored", "event": event_type}
    
    def _handle_subscription_created(
        self,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle new subscription."""
        # In production: Update tenant store with subscription
        return {"status": "created", "tenant_id": data.get("metadata", {}).get("tenant_id")}
    
    def _handle_subscription_updated(
        self,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle subscription update."""
        return {"status": "updated", "tenant_id": data.get("metadata", {}).get("tenant_id")}
    
    def _handle_subscription_deleted(
        self,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle subscription cancellation."""
        return {"status": "deleted", "tenant_id": data.get("metadata", {}).get("tenant_id")}
    
    def _handle_payment_succeeded(
        self,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle successful payment."""
        return {"status": "paid", "invoice_id": data.get("id")}
    
    def _handle_payment_failed(
        self,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle failed payment."""
        return {"status": "failed", "invoice_id": data.get("id")}
    
    def _generate_id(self) -> str:
        """Generate a random ID."""
        import secrets
        return secrets.token_hex(12)


class BillingManager:
    """High-level billing operations.
    
    Coordinates between subscription state and feature access.
    """
    
    def __init__(self, stripe_service: StripeBillingService) -> None:
        self.stripe = stripe_service
        self._subscriptions: dict[str, Subscription] = {}
    
    def check_feature_access(
        self,
        tenant_id: str,
        feature: str
    ) -> bool:
        """Check if tenant has access to a feature.
        
        Args:
            tenant_id: Tenant ID
            feature: Feature name (e.g., "finance:execute")
            
        Returns:
            True if access allowed
        """
        subscription = self._subscriptions.get(tenant_id)
        
        if not subscription or not subscription.is_valid:
            # Free tier - check feature map
            return self._free_tier_features.get(feature, False)
        
        # Check based on plan
        plan = subscription.plan
        return self._plan_features.get(plan, {}).get(feature, False)
    
    def require_feature(
        self,
        tenant_id: str,
        feature: str
    ) -> None:
        """Require feature access or raise.
        
        Args:
            tenant_id: Tenant ID
            feature: Feature name
            
        Raises:
            PlanUpgradeRequiredError: If feature not available
        """
        if not self.check_feature_access(tenant_id, feature):
            raise PlanUpgradeRequiredError(
                f"Feature '{feature}' requires a subscription upgrade"
            )
    
    def sync_subscription(
        self,
        tenant_id: str,
        subscription: Subscription
    ) -> None:
        """Sync subscription state."""
        self._subscriptions[tenant_id] = subscription
    
    def get_subscription(self, tenant_id: str) -> Subscription | None:
        """Get subscription for tenant."""
        return self._subscriptions.get(tenant_id)
    
    # Feature maps
    _free_tier_features = {
        "finance:read": True,
        "health:read": True,
        "career:read": True,
        "finance:simulate": False,
        "health:track": False,
        "career:plan": False,
        "finance:execute": False,
        "health:execute": False,
        "career:execute": False,
    }
    
    _plan_features = {
        "pro": {
            "finance:read": True,
            "finance:simulate": True,
            "health:read": True,
            "health:track": True,
            "career:read": True,
            "career:plan": True,
            "finance:execute": False,
            "health:execute": False,
            "career:execute": False,
        },
        "enterprise": {
            "finance:read": True,
            "finance:simulate": True,
            "finance:execute": True,
            "health:read": True,
            "health:track": True,
            "health:execute": True,
            "career:read": True,
            "career:plan": True,
            "career:execute": True,
        },
    }


# Default instance
_billing_service: StripeBillingService | None = None
_billing_manager: BillingManager | None = None


def get_billing_service() -> StripeBillingService:
    """Get the default billing service."""
    global _billing_service
    if _billing_service is None:
        _billing_service = StripeBillingService()
    return _billing_service


def get_billing_manager() -> BillingManager:
    """Get the default billing manager."""
    global _billing_manager
    if _billing_manager is None:
        _billing_manager = BillingManager(get_billing_service())
    return _billing_manager
