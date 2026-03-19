from dataclasses import dataclass


@dataclass(frozen=True)
class DomainSignal:
    domain: str
    name: str
    value: float
    source: str


@dataclass(frozen=True)
class Recommendation:
    id: str
    domain: str
    title: str
    rationale: str
    requires_human_approval: bool
