"""
PSIP Configuration Models

Immutable, typed configuration contracts for PSIP domain and governance setup.

This module provides frozen dataclasses that replace raw dictionary configuration
with a type-safe, validated contract layer.
"""

from dataclasses import dataclass, field
from typing import Any, Iterable, Tuple


def _normalize_tuple(values: Iterable[str] | None) -> Tuple[str, ...]:
    """Normalize an iterable of strings to an immutable tuple."""
    if not values:
        return ()
    return tuple(v.strip() for v in values if v and v.strip())


@dataclass(frozen=True)
class GovernanceConfig:
    """
    Governance configuration for a domain.
    
    Immutable after creation.
    """
    council_members: Tuple[str, ...] = field(default_factory=tuple)
    risk_threshold_high: float = 0.7
    risk_threshold_medium: float = 0.5
    risk_threshold_low: float = 0.6
    priority_weight: float = 1.0
    
    def __post_init__(self) -> None:
        """Validate and normalize governance config."""
        # Normalize council members to tuple
        object.__setattr__(
            self,
            "council_members",
            _normalize_tuple(self.council_members),
        )
        
        # Validate risk thresholds
        for name, value in [
            ("risk_threshold_high", self.risk_threshold_high),
            ("risk_threshold_medium", self.risk_threshold_medium),
            ("risk_threshold_low", self.risk_threshold_low),
        ]:
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"GovernanceConfig.{name} must be between 0.0 and 1.0, got {value}"
                )
        
        # Validate priority weight
        if self.priority_weight < 0:
            raise ValueError(
                f"GovernanceConfig.priority_weight must be non-negative, got {self.priority_weight}"
            )
    
    @property
    def risk_thresholds(self) -> Tuple[float, float, float]:
        """Return thresholds as a tuple for backward compatibility."""
        return (self.risk_threshold_high, self.risk_threshold_medium, self.risk_threshold_low)


@dataclass(frozen=True)
class RoleConfig:
    """
    Role configuration for a domain.
    
    Immutable after creation.
    """
    observer_enabled: bool = True
    strategist_enabled: bool = True
    governor_enabled: bool = True


@dataclass(frozen=True)
class DomainConfig:
    """
    Complete configuration for a PSIP domain.
    
    Immutable after creation. This is the canonical configuration object
    that should be used instead of raw dictionaries.
    """
    name: str
    enabled: bool = True
    roles: RoleConfig = field(default_factory=RoleConfig)
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    description: str | None = None
    chief_class: Any = field(default=None, repr=False)  # Store class reference, not instance
    
    def __post_init__(self) -> None:
        """Validate domain config."""
        if not self.name or not self.name.strip():
            raise ValueError("DomainConfig.name must not be empty")
        
        # Validate governance
        if self.governance is None:
            raise ValueError("DomainConfig.governance must not be None")
        
        # Validate roles
        if self.roles is None:
            raise ValueError("DomainConfig.roles must not be None")
    
    @property
    def member_id(self) -> str:
        """Get the council member ID (derived from name)."""
        return self.name[:3].lower()
    
    @property
    def short_name(self) -> str:
        """Get the short name for the chief officer."""
        name_map = {
            "finance": "CFO",
            "health": "CHO",
            "career": "CCO",
            "relationships": "CRO",
            "intelligence": "CIO",
            "life_architecture": "CLA",
        }
        return name_map.get(self.name, self.name[:3].upper())
    
    @property
    def title(self) -> str:
        """Get the title for the chief officer."""
        title_map = {
            "finance": "Chief Financial Officer",
            "health": "Chief Health Officer",
            "career": "Chief Career Officer",
            "relationships": "Chief Relationship Officer",
            "intelligence": "Chief Intelligence Officer",
            "life_architecture": "Chief Life Architect",
        }
        return title_map.get(self.name, f"Chief {self.name.title()} Officer")


def validate_domain_config(config: DomainConfig) -> None:
    """
    Validate a domain configuration.
    
    Raises ValueError if configuration is invalid.
    """
    if not config.name.strip():
        raise ValueError("DomainConfig.name must not be empty")
    
    if not config.enabled and config.governance.risk_threshold_high > 0:
        # Disabled domains shouldn't have active risk thresholds
        pass  # This is allowed for graceful degradation
    
    # Governance is validated in its own __post_init__


def validate_domain_config_collection(configs: dict[str, DomainConfig]) -> None:
    """
    Validate a collection of domain configurations.
    
    Raises ValueError if any configuration is invalid or has conflicts.
    """
    if not configs:
        raise ValueError("At least one domain configuration is required")
    
    for name, config in configs.items():
        if config.name != name:
            raise ValueError(
                f"Config key '{name}' does not match DomainConfig.name '{config.name}'"
            )
        validate_domain_config(config)
