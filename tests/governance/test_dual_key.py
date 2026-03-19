from busy_bee_holdings_llc.api.schemas import DecisionRequest
from busy_bee_holdings_llc.governance.engine import GovernanceEngine
from busy_bee_holdings_llc.governance.policy import load_default_policy
from busy_bee_holdings_llc.ownership.cap_table import default_cap_table

def test_reserved_action_requires_dual_key_and_board() -> None:
    engine = GovernanceEngine(policy=load_default_policy(), cap_table=default_cap_table())
    result = engine.evaluate(DecisionRequest(
        action_type="issue_equity",
        title="Raise seed capital",
        description="Create investor units",
        executive_brief_present=True,
        founder_approved=True,
        trust_approved=False,
        board_supermajority=True,
    ))
    assert result.approved is False
    assert result.reason == "trust_approval_required"
