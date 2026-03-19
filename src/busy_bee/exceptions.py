class BusyBeeError(Exception):
    """Base exception for Busy Bee."""


class ApprovalRequiredError(BusyBeeError):
    """Raised when a real-world action requires human approval."""


class ArtifactNotFoundError(BusyBeeError):
    """Raised when model or registry artifacts are missing."""
