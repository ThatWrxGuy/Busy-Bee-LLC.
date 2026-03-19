"""
Signal Connector Base Interface

All signal connectors must implement this interface to integrate with the 
Signal Ingestion Layer.

Connector Categories:
- Financial: Bank APIs, brokerage accounts, crypto wallets
- Calendar: Google Calendar, Apple Calendar  
- Health: Apple Health, Fitbit, Whoop
- Market: Stock prices, macro indicators
- Productivity: Notion, task managers
- Communication: Email, messaging metrics
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class ConnectorCategory(Enum):
    """Categories of signal connectors"""
    FINANCIAL = "financial"
    CALENDAR = "calendar"
    HEALTH = "health"
    MARKET = "market"
    PRODUCTIVITY = "productivity"
    COMMUNICATION = "communication"
    CUSTOM = "custom"


class ConnectorStatus(Enum):
    """Status of a connector"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class ConnectorConfig:
    """Configuration for a connector"""
    connector_id: str
    name: str
    category: ConnectorCategory
    enabled: bool = True
    poll_interval: int = 300  # seconds
    rate_limit: int = 100  # requests per hour
    credentials: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RawSignal:
    """Raw signal data from a connector before normalization"""
    connector_id: str
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    raw_format: str  # e.g., "json", "xml", "csv"
    metadata: Dict[str, Any] = field(default_factory=dict)


class SignalConnector(ABC):
    """
    Base class for all signal connectors.
    
    All connectors must implement:
    - connect(): Establish connection to the data source
    - collect(): Fetch raw data from the source
    - normalize(): Convert raw data to canonical format
    - health_check(): Verify connector is functioning
    """
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.status = ConnectorStatus.DISCONNECTED
        self.last_collected: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self._connection = None
    
    @property
    @abstractmethod
    def connector_type(self) -> str:
        """Unique identifier for this connector type"""
        pass
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the data source.
        
        Returns:
            bool: True if connection successful
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the data source"""
        pass
    
    @abstractmethod
    def collect(self) -> List[RawSignal]:
        """
        Collect raw signals from the data source.
        
        Returns:
            List[RawSignal]: List of raw signals collected
        """
        pass
    
    @abstractmethod
    def normalize(self, raw_signal: RawSignal) -> Dict[str, Any]:
        """
        Normalize a raw signal to canonical format.
        
        Returns:
            Dict with keys: domain, metric_name, metric_value, unit, confidence, tags, metadata
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the connector.
        
        Returns:
            Dict with keys: status, latency_ms, last_success, error_message
        """
        pass
    
    def validate_credentials(self) -> bool:
        """Validate that required credentials are present"""
        required = self.get_required_credentials()
        return all(key in self.config.credentials for key in required)
    
    def get_required_credentials(self) -> List[str]:
        """List of required credential keys for this connector"""
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get current connector status"""
        return {
            "connector_id": self.config.connector_id,
            "connector_type": self.connector_type,
            "status": self.status.value,
            "last_collected": self.last_collected.isoformat() if self.last_collected else None,
            "last_error": self.last_error,
            "enabled": self.config.enabled
        }
    
    def _generate_signal_id(self) -> str:
        """Generate unique signal ID"""
        return f"sig_{uuid.uuid4().hex[:12]}"


# ============== BASE CONNECTOR IMPLEMENTATIONS ==============

class MockConnector(SignalConnector):
    """Mock connector for testing and development"""
    
    @property
    def connector_type(self) -> str:
        return "mock"
    
    def connect(self) -> bool:
        self.status = ConnectorStatus.CONNECTED
        return True
    
    def disconnect(self) -> None:
        self.status = ConnectorStatus.DISCONNECTED
    
    def collect(self) -> List[RawSignal]:
        self.last_collected = datetime.now()
        # Return mock data for testing
        return [
            RawSignal(
                connector_id=self.config.connector_id,
                source="mock_source",
                timestamp=datetime.now(),
                data={"value": 100, "label": "test"},
                raw_format="json"
            )
        ]
    
    def normalize(self, raw_signal: RawSignal) -> Dict[str, Any]:
        return {
            "domain": "general",
            "metric_name": "test_metric",
            "metric_value": raw_signal.data.get("value", 0),
            "unit": "count",
            "confidence": 0.5,
            "tags": ["test"],
            "metadata": {}
        }
    
    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "latency_ms": 0,
            "last_success": datetime.now().isoformat(),
            "error_message": None
        }


__all__ = [
    "SignalConnector",
    "MockConnector",
    "ConnectorCategory",
    "ConnectorStatus", 
    "ConnectorConfig",
    "RawSignal",
]
