from __future__ import annotations

from busy_bee_holdings_llc.api.schemas import DecisionRequest, DecisionResponse
from busy_bee_holdings_llc.governance.policy import GovernancePolicy
from busy_bee_holdings_llc.ownership.cap_table import CapTable

class GovernanceEngine:
    def __init__(self, policy: GovernancePolicy, cap_table: CapTable) -> None:
        self.policy = policy
        self.cap_table = cap_table

    def evaluate(self, request: DecisionRequest) -> DecisionResponse:
        if not request.executive_brief_present:
            return DecisionResponse(approved=False, reason="executive_brief_required")

        if request.action_type in self.policy.reserved_actions:
            if not request.founder_approved:
                return DecisionResponse(approved=False, reason="founder_approval_required")
            if not request.trust_approved:
                return DecisionResponse(approved=False, reason="trust_approval_required")

        if request.action_type in self.policy.supermajority_actions and not request.board_supermajority:
            return DecisionResponse(approved=False, reason="board_supermajority_required")

        if request.action_type == "admit_investor":
            projected = float(request.metadata.get("projected_investor_pool_post_close", self.cap_table.investor_pool_percent))
            if projected > 20.0:
                return DecisionResponse(approved=False, reason="investor_pool_cap_exceeded")

        if request.action_type == "transfer_ip":
            destination = request.metadata.get("destination_entity", "")
            if destination != "Busy Bee Holdings LLC":
                return DecisionResponse(approved=False, reason="ip_must_remain_in_holdco")

        return DecisionResponse(approved=True, reason="approved")
