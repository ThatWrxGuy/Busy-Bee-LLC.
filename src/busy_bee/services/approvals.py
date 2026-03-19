from __future__ import annotations

from busy_bee.exceptions import ApprovalRequiredError


class ApprovalService:
    def __init__(self, require_human_approval_for_financial_execution: bool = True) -> None:
        self.require_human_approval_for_financial_execution = require_human_approval_for_financial_execution

    def assert_execution_allowed(self, domain: str, approved: bool = False) -> None:
        if domain == "finance" and self.require_human_approval_for_financial_execution and not approved:
            raise ApprovalRequiredError(
                "Financial execution blocked until explicit human approval is recorded."
            )
