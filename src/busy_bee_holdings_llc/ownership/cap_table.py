from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class CapTable:
    trust_percent: float
    founder_percent: float
    investor_pool_percent: float

    @property
    def total_percent(self) -> float:
        return round(self.trust_percent + self.founder_percent + self.investor_pool_percent, 4)

    def validate(self) -> None:
        if self.total_percent != 100.0:
            raise ValueError(f"Ownership must total 100%, got {self.total_percent}%")
        if self.trust_percent != 51.0:
            raise ValueError("Trust percentage must remain 51.0% in this package")
        if self.investor_pool_percent > 20.0:
            raise ValueError("Investor pool may not exceed 20.0% in this package")

def default_cap_table() -> CapTable:
    table = CapTable(trust_percent=51.0, founder_percent=29.0, investor_pool_percent=20.0)
    table.validate()
    return table
