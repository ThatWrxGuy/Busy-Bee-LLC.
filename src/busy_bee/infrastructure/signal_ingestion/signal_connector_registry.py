"""
Signal Connector Registry

Manages registration, lifecycle, and orchestration of all signal connectors.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Type
import threading

from .signal_connector_base import (
    SignalConnector, ConnectorConfig, ConnectorStatus, ConnectorCategory, RawSignal
)


@dataclass
class ConnectorRegistration:
    """Registration metadata for a connector"""
    connector_type: str
    connector_class: Type[SignalConnector]
    category: ConnectorCategory
    description: str
    required_credentials: List[str] = field(default_factory=list)


class SignalConnectorRegistry:
    """
    Registry for managing signal connectors.
    
    Handles:
    - Connector registration
    - Connector instantiation
    - Lifecycle management
    - Credential storage
    """
    
    def __init__(self):
        self._registrations: Dict[str, ConnectorRegistration] = {}
        self._instances: Dict[str, SignalConnector] = {}
        self._lock = threading.Lock()
    
    def register(
        self,
        connector_type: str,
        connector_class: Type[SignalConnector],
        category: ConnectorCategory,
        description: str = "",
        required_credentials: List[str] = None
    ) -> None:
        """Register a connector type"""
        with self._lock:
            self._registrations[connector_type] = ConnectorRegistration(
                connector_type=connector_type,
                connector_class=connector_class,
                category=category,
                description=description,
                required_credentials=required_credentials or []
            )
    
    def create_connector(
        self,
        connector_type: str,
        config: ConnectorConfig
    ) -> Optional[SignalConnector]:
        """Create a connector instance"""
        with self._lock:
            if connector_type not in self._registrations:
                return None
            
            registration = self._registrations[connector_type]
            connector = registration.connector_class(config)
            
            self._instances[config.connector_id] = connector
            return connector
    
    def get_connector(self, connector_id: str) -> Optional[SignalConnector]:
        """Get connector instance by ID"""
        return self._instances.get(connector_id)
    
    def remove_connector(self, connector_id: str) -> bool:
        """Remove and cleanup a connector"""
        with self._lock:
            if connector_id in self._instances:
                connector = self._instances[connector_id]
                try:
                    connector.disconnect()
                except Exception:
                    pass
                del self._instances[connector_id]
                return True
            return False
    
    def get_all_connectors(self) -> List[SignalConnector]:
        """Get all registered connector instances"""
        return list(self._instances.values())
    
    def get_connectors_by_category(self, category: ConnectorCategory) -> List[SignalConnector]:
        """Get all connectors in a category"""
        return [
            c for c in self._instances.values()
            if c.config.category == category
        ]
    
    def get_connectors_by_status(self, status: ConnectorStatus) -> List[SignalConnector]:
        """Get all connectors with a specific status"""
        return [c for c in self._instances.values() if c.status == status]
    
    def get_registry_summary(self) -> Dict:
        """Get summary of all registered connectors"""
        return {
            "registered_types": list(self._registrations.keys()),
            "active_instances": len(self._instances),
            "by_category": {
                category.value: len(self.get_connectors_by_category(category))
                for category in ConnectorCategory
            },
            "by_status": {
                status.value: len(self.get_connectors_by_status(status))
                for status in ConnectorStatus
            }
        }
    
    def list_registered_types(self) -> List[Dict]:
        """List all registered connector types"""
        return [
            {
                "type": reg.connector_type,
                "category": reg.category.value,
                "description": reg.description,
                "required_credentials": reg.required_credentials
            }
            for reg in self._registrations.values()
        ]


# Global registry instance
_global_registry: Optional[SignalConnectorRegistry] = None


def get_connector_registry() -> SignalConnectorRegistry:
    """Get the global connector registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = SignalConnectorRegistry()
    return _global_registry


def register_connector(
    connector_type: str,
    category: ConnectorCategory,
    description: str = "",
    required_credentials: List[str] = None
):
    """Decorator to register a connector"""
    def decorator(cls: Type[SignalConnector]):
        registry = get_connector_registry()
        registry.register(
            connector_type=connector_type,
            connector_class=cls,
            category=category,
            description=description,
            required_credentials=required_credentials
        )
        return cls
    return decorator


__all__ = [
    "SignalConnectorRegistry",
    "ConnectorRegistration",
    "get_connector_registry",
    "register_connector",
]
