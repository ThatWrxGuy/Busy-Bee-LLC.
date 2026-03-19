from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from busybee_contracts.tenant_context import TenantContext

from app.ml.common.contracts import PredictionRequest, PredictionResult


class PlanUpgradeRequired(Exception):
    """Raised when action requires plan upgrade."""
    pass


class MLGovernancePolicy:
    """Governance policy that branches by execution mode, plan tier, and billing.
    
    Finance always requires human review.
    SaaS mode enforces stricter policies than personal mode.
    Plan tiers limit capabilities based on subscription.
    """
    
    # Capability matrix
    CAPABILITY_MATRIX = {
        "free": {
            "finance": ["read"],      # Read-only insights
            "health": ["read"],
            "career": ["read"],
        },
        "pro": {
            "finance": ["read", "simulate"],  # Can run simulations
            "health": ["read", "track"],
            "career": ["read", "plan"],
        },
        "enterprise": {
            "finance": ["read", "simulate", "execute"],  # Full execution
            "health": ["read", "track", "execute"],
            "career": ["read", "plan", "execute"],
        },
    }
    
    def __init__(self, min_confidence: float = 0.60) -> None:
        self.min_confidence = min_confidence
    
    def check_capability(
        self,
        domain: str,
        action: str,
        context: "TenantContext | None"
    ) -> bool:
        """Check if context has capability for domain/action.
        
        Raises:
            PlanUpgradeRequired: If action requires upgrade
        """
        plan = context.plan_tier if context else "free"
        domain_lower = domain.lower()
        
        # Get allowed actions for plan
        allowed = self.CAPABILITY_MATRIX.get(plan, {}).get(domain_lower, [])
        
        if action not in allowed:
            if plan == "free":
                raise PlanUpgradeRequired(
                    f"{domain.capitalize()} {action} requires Pro plan or higher"
                )
            return False
        
        return True
    
    def check_billing_access(
        self,
        tenant_id: str | None,
        feature: str
    ) -> bool:
        """Check if tenant has billing access for feature.
        
        Args:
            tenant_id: Tenant ID to check
            feature: Feature name
            
        Returns:
            True if billing allows access
        """
        if not tenant_id:
            # No tenant = free tier
            return False
        
        try:
            from infrastructure.billing.stripe_service import get_billing_manager
            manager = get_billing_manager()
            return manager.check_feature_access(tenant_id, feature)
        except Exception:
            # If billing service unavailable, default to strict
            return False
    
    def apply(
        self,
        request: PredictionRequest,
        result: PredictionResult,
        context: "TenantContext | None" = None
    ) -> PredictionResult:
        """Apply governance policy with context awareness."""
        
        # Finance domain always requires human review
        if "finance" in [d.lower() for d in request.source_domains]:
            result.human_review_required = True
        
        # SaaS mode enforces stricter policies
        if context and context.is_saas:
            # Stricter review for additional domains in SaaS
            saas_strict_domains = {"health", "career", "relationships"}
            source_lower = {d.lower() for d in request.source_domains}
            if source_lower & saas_strict_domains:
                result.human_review_required = True
            
            # Check plan tier - higher tiers may have more autonomy
            if context.plan_tier == "enterprise":
                # Enterprise may have conditional approval
                result.metadata["enterprise_approval"] = "conditional"
            
            # Check billing status for capabilities
            if context.tenant_id:
                billing_ok = self.check_billing_access(
                    context.tenant_id,
                    f"{request.source_domains[0]}:read" if request.source_domains else ""
                )
                if not billing_ok:
                    result.metadata["billing_required"] = True
            
            # Check capabilities
            for domain in request.source_domains:
                try:
                    self.check_capability(domain, "read", context)
                except PlanUpgradeRequired as e:
                    result.metadata["upgrade_required"] = str(e)
        
        # Confidence threshold - downgrade to advisory if too low
        if result.confidence < self.min_confidence:
            result.metadata["advisory_only"] = True
            if not result.human_review_required:
                # Advisory recommendations should still be reviewed
                result.human_review_required = True
        
        return result
    
    def requires_human_review(
        self,
        domain: str,
        context: "TenantContext | None"
    ) -> bool:
        """Check if a domain requires human review."""
        domain_lower = domain.lower()
        
        # Finance always requires review
        if domain_lower == "finance":
            return True
        
        # SaaS strict domains require review
        if context and context.is_saas:
            if domain_lower in {"health", "career", "relationships"}:
                return True
        
        # Default: no mandatory review
        return False
