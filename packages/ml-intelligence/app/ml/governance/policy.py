from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from busybee_contracts.tenant_context import TenantContext

from app.ml.common.contracts import PredictionRequest, PredictionResult


class MLGovernancePolicy:
    """Governance policy that branches by execution mode.
    
    Finance always requires human review.
    SaaS mode enforces stricter policies than personal mode.
    """
    
    def __init__(self, min_confidence: float = 0.60) -> None:
        self.min_confidence = min_confidence
    
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
