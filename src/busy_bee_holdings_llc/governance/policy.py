from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class GovernancePolicy:
    reserved_actions: set[str] = field(default_factory=lambda: {
        "sell_company",
        "issue_equity",
        "transfer_ip",
        "exclusive_ip_license",
        "take_debt",
        "change_governance",
        "remove_founder",
        "admit_investor",
    })
    supermajority_actions: set[str] = field(default_factory=lambda: {
        "sell_company",
        "issue_equity",
        "take_debt",
        "change_governance",
        "remove_founder",
        "admit_investor",
    })
    financial_execution_requires_human_approval: bool = True

def load_default_policy() -> GovernancePolicy:
    return GovernancePolicy()
