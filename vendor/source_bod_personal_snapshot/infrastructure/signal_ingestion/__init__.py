"""
Signal Ingestion Layer

BB-INF-007: Real Signal Ingestion & Continuous Intelligence Cycle

This module provides the infrastructure for ingesting real-world signals
from various data sources and normalizing them for processing by the
Busy Bee intelligence system.

Components:
- signal_connector_base: Base interface for all connectors
- signal_connector_registry: Manages connector lifecycle
- signal_normalizer: Converts raw signals to canonical format
- signal_validator: Validates signal quality
- signal_cache: In-memory cache for signals
- signal_health_monitor: Monitors system health
- ingestion_manager: Orchestrates the ingestion pipeline
"""

from .signal_connector_base import (
    SignalConnector,
    MockConnector,
    ConnectorCategory,
    ConnectorStatus,
    ConnectorConfig,
    RawSignal,
)

from .signal_connector_registry import (
    SignalConnectorRegistry,
    get_connector_registry,
    register_connector,
)

from .signal_normalizer import (
    SignalNormalizer,
    CanonicalSignal,
    SignalDomain,
    SignalUnit,
)

from .signal_validator import (
    SignalValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)

from .signal_cache import (
    SignalCache,
    CacheEntry,
    get_signal_cache,
)

from .signal_health_monitor import (
    SignalHealthMonitor,
    ConnectorHealth,
    IngestionHealth,
    HealthStatus,
    get_health_monitor,
)

from .ingestion_manager import (
    SignalIngestionManager,
    IngestionResult,
    IngestionStatus,
    get_ingestion_manager,
)


__all__ = [
    # Connector base
    "SignalConnector",
    "MockConnector",
    "ConnectorCategory",
    "ConnectorStatus",
    "ConnectorConfig",
    "RawSignal",
    
    # Registry
    "SignalConnectorRegistry",
    "get_connector_registry",
    "register_connector",
    
    # Normalizer
    "SignalNormalizer",
    "CanonicalSignal",
    "SignalDomain",
    "SignalUnit",
    
    # Validator
    "SignalValidator",
    "ValidationIssue",
    "ValidationResult",
    "ValidationSeverity",
    
    # Cache
    "SignalCache",
    "CacheEntry",
    "get_signal_cache",
    
    # Health Monitor
    "SignalHealthMonitor",
    "ConnectorHealth",
    "IngestionHealth",
    "HealthStatus",
    "get_health_monitor",
    
    # Manager
    "SignalIngestionManager",
    "IngestionResult",
    "IngestionStatus",
    "get_ingestion_manager",
]
