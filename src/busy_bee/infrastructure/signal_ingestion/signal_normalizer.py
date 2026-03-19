"""
Signal Normalizer

Converts raw signals from various connectors into the Canonical Signal Format.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid


class SignalDomain(Enum):
    """Domains for signals"""
    FINANCE = "finance"
    HEALTH = "health"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    INTELLIGENCE = "intelligence"
    LIFE_ARCHITECTURE = "life_architecture"
    GENERAL = "general"


class SignalUnit(Enum):
    """Units for signal values"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    PERCENT = "percent"
    COUNT = "count"
    HOURS = "hours"
    DAYS = "days"
    RATING = "rating"
    BOOLEAN = "boolean"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class CanonicalSignal:
    """
    Canonical Signal Model
    
    All signals must be converted to this format.
    """
    signal_id: str
    domain: SignalDomain
    source: str
    timestamp: datetime
    
    # Core metrics
    metric_name: str
    metric_value: Any
    unit: SignalUnit
    
    # Quality
    confidence: float  # 0.0 - 1.0
    
    # Organization
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Lineage
    original_connector_id: str = ""
    original_raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "signal_id": self.signal_id,
            "domain": self.domain.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "unit": self.unit.value,
            "confidence": self.confidence,
            "tags": self.tags,
            "metadata": self.metadata,
            "original_connector_id": self.original_connector_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CanonicalSignal':
        """Create from dictionary"""
        return cls(
            signal_id=data["signal_id"],
            domain=SignalDomain(data.get("domain", "general")),
            source=data["source"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metric_name=data["metric_name"],
            metric_value=data["metric_value"],
            unit=SignalUnit(data.get("unit", "unknown")),
            confidence=data["confidence"],
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            original_connector_id=data.get("original_connector_id", "")
        )


class SignalNormalizer:
    """
    Normalizes raw signals to canonical format.
    
    Handles:
    - Domain mapping
    - Unit conversion
    - Value validation
    - Tag enrichment
    """
    
    # Domain mapping from common sources
    DOMAIN_MAP = {
        "bank": SignalDomain.FINANCE,
        "brokerage": SignalDomain.FINANCE,
        "crypto": SignalDomain.FINANCE,
        "plaid": SignalDomain.FINANCE,
        "calendar": SignalDomain.LIFE_ARCHITECTURE,
        "google_calendar": SignalDomain.LIFE_ARCHITECTURE,
        "apple_calendar": SignalDomain.LIFE_ARCHITECTURE,
        "apple_health": SignalDomain.HEALTH,
        "fitbit": SignalDomain.HEALTH,
        "whoop": SignalDomain.HEALTH,
        "garmin": SignalDomain.HEALTH,
        "notion": SignalDomain.INTELLIGENCE,
        "todoist": SignalDomain.INTELLIGENCE,
        "asana": SignalDomain.INTELLIGENCE,
        "linkedin": SignalDomain.CAREER,
        "indeed": SignalDomain.CAREER,
    }
    
    # Unit mapping
    UNIT_MAP = {
        "$": SignalUnit.USD,
        "USD": SignalUnit.USD,
        "EUR": SignalUnit.EUR,
        "GBP": SignalUnit.GBP,
        "%": SignalUnit.PERCENT,
        "percent": SignalUnit.PERCENT,
        "hours": SignalUnit.HOURS,
        "hrs": SignalUnit.HOURS,
        "days": SignalUnit.DAYS,
    }
    
    def __init__(self):
        self.normalization_rules: Dict[str, Dict] = {}
    
    def normalize(
        self,
        raw_data: Dict[str, Any],
        connector_id: str,
        source: str
    ) -> CanonicalSignal:
        """
        Normalize raw signal data to canonical format.
        
        Args:
            raw_data: Raw data from connector
            connector_id: ID of the source connector
            source: Source identifier
            
        Returns:
            CanonicalSignal in standard format
        """
        # Extract or generate signal ID
        signal_id = raw_data.get("signal_id") or f"sig_{uuid.uuid4().hex[:12]}"
        
        # Determine domain
        domain = self._determine_domain(source, raw_data)
        
        # Extract timestamp
        timestamp = self._extract_timestamp(raw_data)
        
        # Extract metric name
        metric_name = self._extract_metric_name(raw_data)
        
        # Extract and convert value
        metric_value = self._extract_value(raw_data)
        
        # Determine unit
        unit = self._determine_unit(raw_data, metric_name)
        
        # Calculate confidence
        confidence = self._calculate_confidence(raw_data)
        
        # Extract tags
        tags = self._extract_tags(raw_data, domain)
        
        # Build metadata
        metadata = self._build_metadata(raw_data, source)
        
        return CanonicalSignal(
            signal_id=signal_id,
            domain=domain,
            source=source,
            timestamp=timestamp,
            metric_name=metric_name,
            metric_value=metric_value,
            unit=unit,
            confidence=confidence,
            tags=tags,
            metadata=metadata,
            original_connector_id=connector_id,
            original_raw_data=raw_data
        )
    
    def _determine_domain(self, source: str, raw_data: Dict) -> SignalDomain:
        """Determine signal domain from source and data"""
        source_lower = source.lower()
        
        # Check source mapping
        for key, domain in self.DOMAIN_MAP.items():
            if key in source_lower:
                return domain
        
        # Check data for domain hint
        if "domain" in raw_data:
            try:
                return SignalDomain(raw_data["domain"])
            except ValueError:
                pass
        
        # Default to general
        return SignalDomain.GENERAL
    
    def _extract_timestamp(self, raw_data: Dict) -> datetime:
        """Extract timestamp from raw data"""
        # Try various timestamp fields
        for field in ["timestamp", "date", "time", "datetime", "created_at", "updated_at"]:
            if field in raw_data:
                value = raw_data[field]
                if isinstance(value, datetime):
                    return value
                if isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value.replace("Z", "+00:00"))
                    except ValueError:
                        pass
        
        # Default to now
        return datetime.now()
    
    def _extract_metric_name(self, raw_data: Dict) -> str:
        """Extract metric name from raw data"""
        # Try various name fields
        for field in ["metric_name", "metric", "name", "label", "title"]:
            if field in raw_data:
                return str(raw_data[field])
        
        # Try to infer from data keys
        numeric_keys = [k for k in raw_data.keys() 
                       if isinstance(raw_data.get(k), (int, float))]
        if numeric_keys:
            return numeric_keys[0]
        
        return "unknown_metric"
    
    def _extract_value(self, raw_data: Dict) -> Any:
        """Extract metric value from raw data"""
        # Try various value fields
        for field in ["metric_value", "value", "amount", "balance", "count", "score"]:
            if field in raw_data:
                return raw_data[field]
        
        # Return first numeric value found
        for key, value in raw_data.items():
            if isinstance(value, (int, float, str)):
                return value
        
        return None
    
    def _determine_unit(self, raw_data: Dict, metric_name: str) -> SignalUnit:
        """Determine unit from raw data and metric name"""
        # Check explicit unit field
        if "unit" in raw_data:
            unit_str = str(raw_data["unit"]).upper()
            if unit_str in [u.value for u in SignalUnit]:
                return SignalUnit(unit_str)
        
        # Check unit mapping
        if "unit" in raw_data:
            return self.UNIT_MAP.get(raw_data["unit"].lower(), SignalUnit.UNKNOWN)
        
        # Infer from metric name
        metric_lower = metric_name.lower()
        if "balance" in metric_lower or "amount" in metric_lower or "price" in metric_lower:
            return SignalUnit.USD
        if "percentage" in metric_lower or "rate" in metric_lower:
            return SignalUnit.PERCENT
        if "hours" in metric_lower or "sleep" in metric_lower:
            return SignalUnit.HOURS
        if "count" in metric_lower or "number" in metric_lower:
            return SignalUnit.COUNT
        
        return SignalUnit.UNKNOWN
    
    def _calculate_confidence(self, raw_data: Dict) -> float:
        """Calculate confidence score for the signal"""
        # Use explicit confidence if present
        if "confidence" in raw_data:
            return float(raw_data["confidence"])
        
        # Use data quality indicators
        confidence = 0.5  # Base confidence
        
        # Has timestamp
        if any(f in raw_data for f in ["timestamp", "date", "time"]):
            confidence += 0.1
        
        # Has multiple fields
        if len(raw_data) > 3:
            confidence += 0.1
        
        # Source is known
        if raw_data.get("source"):
            confidence += 0.1
        
        # Has value
        if raw_data.get("value") is not None:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _extract_tags(self, raw_data: Dict, domain: SignalDomain) -> List[str]:
        """Extract and enrich tags"""
        tags = []
        
        # Add domain tag
        tags.append(domain.value)
        
        # Add explicit tags
        if "tags" in raw_data:
            tags.extend(raw_data["tags"])
        
        # Add category from source
        if "category" in raw_data:
            tags.append(raw_data["category"])
        
        return list(set(tags))
    
    def _build_metadata(self, raw_data: Dict, source: str) -> Dict[str, Any]:
        """Build metadata from raw data"""
        metadata = {
            "source": source,
            "raw_keys": list(raw_data.keys())
        }
        
        # Add relevant fields to metadata
        for field in ["category", "type", "status", "account_id", "user_id"]:
            if field in raw_data:
                metadata[field] = raw_data[field]
        
        return metadata
    
    def add_normalization_rule(
        self,
        metric_pattern: str,
        domain: SignalDomain,
        unit: SignalUnit,
        tags: List[str] = None
    ) -> None:
        """Add a normalization rule for a metric pattern"""
        self.normalization_rules[metric_pattern] = {
            "domain": domain,
            "unit": unit,
            "tags": tags or []
        }


__all__ = [
    "SignalNormalizer",
    "CanonicalSignal",
    "SignalDomain",
    "SignalUnit",
]
