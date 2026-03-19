"""
Infrastructure - Signal Architecture

BB-DOM-002: Domain Signal Architecture

Contains:
- Signal Schema: Canonical signal data model, validation, normalization
- Global Signal Bus: Central routing layer
- Derived Signal Engine: Signal transformation and synthesis
"""

from .signal_schema import (
    SignalClass,
    SignalPriority,
    SignalDomain,
    Signal,
    ValidationResult,
    SignalValidator,
    SignalNormalizer,
    SignalFactory,
    SignalTypeRegistry
)

from .global_signal_bus import (
    GlobalSignalBus,
    SignalRoute,
    SignalSubscription,
    SignalEscalator,
    RoutingType
)

from .derived_signal_engine import (
    DerivedSignalEngine,
    DerivedSignalRule
)


__all__ = [
    # Enums
    "SignalClass",
    "SignalPriority",
    "SignalDomain",
    "RoutingType",
    
    # Core
    "Signal",
    "ValidationResult",
    "SignalValidator",
    "SignalNormalizer",
    "SignalFactory",
    "SignalTypeRegistry",
    
    # Bus
    "GlobalSignalBus",
    "SignalRoute",
    "SignalSubscription",
    "SignalEscalator",
    
    # Derived
    "DerivedSignalEngine",
    "DerivedSignalRule",
]
