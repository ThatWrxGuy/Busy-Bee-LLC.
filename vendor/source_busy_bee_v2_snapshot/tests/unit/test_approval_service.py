import pytest

from busy_bee.exceptions import ApprovalRequiredError
from busy_bee.services.approvals import ApprovalService


def test_finance_requires_approval() -> None:
    service = ApprovalService(True)
    with pytest.raises(ApprovalRequiredError):
        service.assert_execution_allowed("finance", approved=False)


def test_non_finance_does_not_require_approval() -> None:
    service = ApprovalService(True)
    service.assert_execution_allowed("health", approved=False)
