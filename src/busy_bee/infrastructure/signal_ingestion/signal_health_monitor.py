"""
Signal Health Monitor

Monitors the health and performance of signal ingestion components.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum
import threading
import time


class HealthStatus(Enum):
    """Health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ConnectorHealth:
    """Health information for a connector"""
    connector_id: str
    connector_type: str
    status: HealthStatus
    last_check: datetime
    latency_ms: float
    uptime_seconds: float
    total_collections: int = 0
    failed_collections: int = 0
    error_message: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.total_collections
        if total == 0:
            return 0.0
        return (total - self.failed_collections) / total


@dataclass
class IngestionHealth:
    """Overall ingestion system health"""
    status: HealthStatus
    timestamp: datetime
    
    # Counts
    active_connectors: int = 0
    total_signals_ingested: int = 0
    signals_last_hour: int = 0
    
    # Performance
    avg_latency_ms: float = 0.0
    total_errors: int = 0
    
    # Component health
    normalizer_status: HealthStatus = HealthStatus.UNKNOWN
    validator_status: HealthStatus = HealthStatus.UNKNOWN
    cache_status: HealthStatus = HealthStatus.UNKNOWN


class SignalHealthMonitor:
    """
    Monitors health of signal ingestion system.
    
    Tracks:
    - Connector uptime and latency
    - Signal freshness
    - Ingestion errors
    - System performance
    """
    
    def __init__(self):
        self._connector_health: Dict[str, ConnectorHealth] = {}
        self._signals_per_hour: List[int] = []
        self._total_signals: int = 0
        self._total_errors: int = 0
        self._latencies: List[float] = []
        self._lock = threading.RLock()
        self._last_hour_check = datetime.now()
    
    def record_collection(
        self,
        connector_id: str,
        connector_type: str,
        success: bool,
        latency_ms: float,
        signal_count: int = 0,
        error: Optional[str] = None
    ) -> None:
        """Record a collection event"""
        with self._lock:
            now = datetime.now()
            
            # Get or create connector health
            if connector_id not in self._connector_health:
                self._connector_health[connector_id] = ConnectorHealth(
                    connector_id=connector_id,
                    connector_type=connector_type,
                    status=HealthStatus.UNKNOWN,
                    last_check=now,
                    latency_ms=latency_ms,
                    uptime_seconds=0.0
                )
            
            health = self._connector_health[connector_id]
            health.last_check = now
            health.latency_ms = latency_ms
            health.total_collections += 1
            
            if success:
                health.uptime_seconds += (latency_ms / 1000)
            else:
                health.failed_collections += 1
                health.error_message = error
            
            # Update status
            if health.failed_collections > health.total_collections * 0.5:
                health.status = HealthStatus.UNHEALTHY
            elif health.failed_collections > 0:
                health.status = HealthStatus.DEGRADED
            else:
                health.status = HealthStatus.HEALTHY
            
            # Record signal count
            if signal_count > 0:
                self._total_signals += signal_count
                self._record_signal_count(signal_count)
            
            # Record latency
            self._latencies.append(latency_ms)
            if len(self._latencies) > 100:
                self._latencies = self._latencies[-100:]
            
            # Record error
            if not success:
                self._total_errors += 1
    
    def _record_signal_count(self, count: int) -> None:
        """Record signal count for hourly tracking"""
        now = datetime.now()
        
        # Reset hourly tracking if needed
        if now - self._last_hour_check > timedelta(hours=1):
            self._signals_per_hour = []
            self._last_hour_check = now
        
        self._signals_per_hour.append(count)
    
    def get_connector_health(self, connector_id: str) -> Optional[ConnectorHealth]:
        """Get health for a specific connector"""
        return self._connector_health.get(connector_id)
    
    def get_all_connector_health(self) -> List[ConnectorHealth]:
        """Get health for all connectors"""
        return list(self._connector_health.values())
    
    def get_ingestion_health(self) -> IngestionHealth:
        """Get overall ingestion system health"""
        with self._lock:
            now = datetime.now()
            
            # Determine overall status
            connector_statuses = [c.status for c in self._connector_health.values()]
            
            if not connector_statuses:
                overall_status = HealthStatus.UNKNOWN
            elif HealthStatus.UNHEALTHY in connector_statuses:
                overall_status = HealthStatus.UNHEALTHY
            elif HealthStatus.DEGRADED in connector_statuses:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY
            
            # Calculate average latency
            avg_latency = sum(self._latencies) / len(self._latencies) if self._latencies else 0.0
            
            # Count active connectors
            active = sum(
                1 for c in self._connector_health.values()
                if c.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            )
            
            return IngestionHealth(
                status=overall_status,
                timestamp=now,
                active_connectors=active,
                total_signals_ingested=self._total_signals,
                signals_last_hour=sum(self._signals_per_hour),
                avg_latency_ms=avg_latency,
                total_errors=self._total_errors,
                normalizer_status=HealthStatus.HEALTHY,  # Would integrate with actual component
                validator_status=HealthStatus.HEALTHY,
                cache_status=HealthStatus.HEALTHY
            )
    
    def get_health_summary(self) -> Dict:
        """Get health summary as dictionary"""
        ingestion = self.get_ingestion_health()
        
        return {
            "status": ingestion.status.value,
            "timestamp": ingestion.timestamp.isoformat(),
            "connectors": {
                "active": ingestion.active_connectors,
                "total": len(self._connector_health)
            },
            "signals": {
                "total_ingested": ingestion.total_signals_ingested,
                "last_hour": ingestion.signals_last_hour
            },
            "performance": {
                "avg_latency_ms": ingestion.avg_latency_ms,
                "total_errors": ingestion.total_errors
            },
            "components": {
                "normalizer": ingestion.normalizer_status.value,
                "validator": ingestion.validator_status.value,
                "cache": ingestion.cache_status.value
            }
        }
    
    def get_connector_details(self) -> List[Dict]:
        """Get detailed health for all connectors"""
        return [
            {
                "connector_id": c.connector_id,
                "connector_type": c.connector_type,
                "status": c.status.value,
                "last_check": c.last_check.isoformat(),
                "latency_ms": c.latency_ms,
                "uptime_seconds": c.uptime_seconds,
                "total_collections": c.total_collections,
                "failed_collections": c.failed_collections,
                "success_rate": c.success_rate,
                "error_message": c.error_message
            }
            for c in self._connector_health.values()
        ]
    
    def check_signal_freshness(self, max_age_minutes: int = 60) -> Dict:
        """Check if signals are fresh"""
        # This would integrate with actual signal storage
        return {
            "is_fresh": True,
            "last_signal_time": datetime.now().isoformat(),
            "max_age_minutes": max_age_minutes
        }


# Global health monitor
_global_monitor: Optional[SignalHealthMonitor] = None


def get_health_monitor() -> SignalHealthMonitor:
    """Get the global health monitor"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = SignalHealthMonitor()
    return _global_monitor


__all__ = [
    "SignalHealthMonitor",
    "ConnectorHealth",
    "IngestionHealth",
    "HealthStatus",
    "get_health_monitor",
]
