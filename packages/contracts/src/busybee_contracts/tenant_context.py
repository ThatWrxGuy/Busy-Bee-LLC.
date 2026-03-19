from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ExecutionMode = Literal["saas", "personal"]


@dataclass(slots=True, frozen=True)
class TenantContext:
    tenant_id: str
    user_id: str
    mode: ExecutionMode
    permissions: tuple[str, ...] = field(default_factory=tuple)
    plan_tier: str = "standard"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_saas(self) -> bool:
        return self.mode == "saas"

    @property
    def is_personal(self) -> bool:
        return self.mode == "personal"
