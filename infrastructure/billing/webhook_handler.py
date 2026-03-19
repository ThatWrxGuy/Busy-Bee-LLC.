# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Stripe Webhook Handler.

Processes Stripe webhook events to keep subscription state in sync.
"""

from __future__ import annotations

from typing import Any, Callable
from dataclasses import dataclass

from infrastructure.billing.stripe_service import (
    StripeBillingService,
    Subscription,
    SubscriptionStatus,
    WebhookVerificationError,
)


@dataclass
class WebhookResult:
    """Result of webhook processing."""
    success: bool
    message: str
    tenant_id: str | None = None
    data: dict[str, Any] | None = None


class WebhookHandler:
    """Handles Stripe webhook events.
    
    Coordinates between Stripe events and internal tenant state.
    """
    
    def __init__(self, billing_service: StripeBillingService) -> None:
        self.billing = billing_service
        self._handlers: dict[str, Callable] = {}
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register event handlers."""
        self._handlers = {
            "customer.subscription.created": self._on_subscription_created,
            "customer.subscription.updated": self._on_subscription_updated,
            "customer.subscription.deleted": self._on_subscription_deleted,
            "invoice.payment_succeeded": self._on_payment_succeeded,
            "invoice.payment_failed": self._on_payment_failed,
            "customer.subscription.trial_will_end": self._on_trial_will_end,
        }
    
    async def handle_webhook(
        self,
        payload: bytes,
        signature: str
    ) -> WebhookResult:
        """Handle incoming webhook.
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header
            
        Returns:
            WebhookResult
        """
        try:
            event = self.billing.verify_webhook_signature(payload, signature)
        except WebhookVerificationError as e:
            return WebhookResult(
                success=False,
                message=f"Signature verification failed: {e}"
            )
        
        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})
        
        handler = self._handlers.get(event_type)
        
        if handler:
            try:
                return await handler(event_data)
            except Exception as e:
                return WebhookResult(
                    success=False,
                    message=f"Handler error: {e}"
                )
        
        return WebhookResult(
            success=True,
            message=f"No handler for event type: {event_type}"
        )
    
    async def _on_subscription_created(
        self,
        data: dict[str, Any]
    ) -> WebhookResult:
        """Handle new subscription created."""
        tenant_id = data.get("metadata", {}).get("tenant_id")
        
        # Extract subscription details
        subscription = Subscription(
            subscription_id=data.get("id", ""),
            customer_id=data.get("customer", ""),
            tenant_id=tenant_id or "",
            status=SubscriptionStatus(data.get("status", "active")),
            plan=self._extract_plan(data),
            current_period_start=data.get("current_period_start", 0),
            current_period_end=data.get("current_period_end", 0),
            cancel_at_period_end=data.get("cancel_at_period_end", False),
        )
        
        # Sync to billing manager
        from infrastructure.billing.stripe_service import get_billing_manager
        manager = get_billing_manager()
        if tenant_id:
            manager.sync_subscription(tenant_id, subscription)
        
        return WebhookResult(
            success=True,
            message="Subscription created",
            tenant_id=tenant_id,
            data={"subscription_id": subscription.subscription_id}
        )
    
    async def _on_subscription_updated(
        self,
        data: dict[str, Any]
    ) -> WebhookResult:
        """Handle subscription updated."""
        tenant_id = data.get("metadata", {}).get("tenant_id")
        
        subscription = Subscription(
            subscription_id=data.get("id", ""),
            customer_id=data.get("customer", ""),
            tenant_id=tenant_id or "",
            status=SubscriptionStatus(data.get("status", "active")),
            plan=self._extract_plan(data),
            current_period_start=data.get("current_period_start", 0),
            current_period_end=data.get("current_period_end", 0),
            cancel_at_period_end=data.get("cancel_at_period_end", False),
        )
        
        # Sync to billing manager
        from infrastructure.billing.stripe_service import get_billing_manager
        manager = get_billing_manager()
        if tenant_id:
            manager.sync_subscription(tenant_id, subscription)
        
        return WebhookResult(
            success=True,
            message="Subscription updated",
            tenant_id=tenant_id
        )
    
    async def _on_subscription_deleted(
        self,
        data: dict[str, Any]
    ) -> WebhookResult:
        """Handle subscription cancelled/deleted."""
        tenant_id = data.get("metadata", {}).get("tenant_id")
        
        # Remove subscription from manager
        from infrastructure.billing.stripe_service import get_billing_manager
        manager = get_billing_manager()
        if tenant_id:
            manager.sync_subscription(tenant_id, None)  # type: ignore
        
        return WebhookResult(
            success=True,
            message="Subscription deleted",
            tenant_id=tenant_id
        )
    
    async def _on_payment_succeeded(
        self,
        data: dict[str, Any]
    ) -> WebhookResult:
        """Handle successful payment."""
        # Log for analytics, update subscription status if needed
        return WebhookResult(
            success=True,
            message="Payment succeeded"
        )
    
    async def _on_payment_failed(
        self,
        data: dict[str, Any]
    ) -> WebhookResult:
        """Handle failed payment."""
        # Could notify user, downgrade access, etc.
        return WebhookResult(
            success=True,
            message="Payment failed - may need manual intervention"
        )
    
    async def _on_trial_will_end(
        self,
        data: dict[str, Any]
    ) -> WebhookResult:
        """Handle trial ending soon."""
        # Send reminder to user
        tenant_id = data.get("metadata", {}).get("tenant_id")
        
        return WebhookResult(
            success=True,
            message="Trial ending soon - notify user",
            tenant_id=tenant_id
        )
    
    def _extract_plan(self, data: dict[str, Any]) -> str:
        """Extract plan tier from subscription data."""
        items = data.get("items", {}).get("data", [])
        if items:
            price = items[0].get("price", {})
            price_id = price.get("id", "")
            
            plan_map = {
                "price_pro_monthly": "pro",
                "price_pro_yearly": "pro",
                "price_enterprise_monthly": "enterprise",
                "price_enterprise_yearly": "enterprise",
            }
            return plan_map.get(price_id, "free")
        
        return "free"


# FastAPI route handler example
async def stripe_webhook_endpoint(request):
    """FastAPI endpoint for Stripe webhooks."""
    from infrastructure.billing.stripe_service import get_billing_service
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    billing = get_billing_service()
    handler = WebhookHandler(billing)
    
    result = await handler.handle_webhook(body, signature)
    
    if result.success:
        return {"status": "ok"}
    else:
        return {"status": "error", "message": result.message}, 400
