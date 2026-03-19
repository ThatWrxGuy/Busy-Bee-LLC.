"""
Signal Refresh Engine

Refreshes signals from all connected sources.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import logging

from ..signal_ingestion import (
    SignalIngestionManager, get_ingestion_manager,
    SignalDomain, CanonicalSignal
)


logger = logging.getLogger(__name__)


@dataclass
class RefreshResult:
    """Result of a signal refresh"""
    timestamp: datetime
    success: bool
    
    signals_refreshed: int = 0
    signals_by_domain: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0


class SignalRefreshEngine:
    """
    Engine for refreshing signals from connectors.
    
    Handles:
    - Periodic signal collection
    - Signal deduplication
    - Change detection
    - Staleness tracking
    """
    
    def __init__(self, ingestion_manager: Optional[SignalIngestionManager] = None):
        self.ingestion = ingestion_manager or get_ingestion_manager()
        
        # Track last known values for change detection
        self._last_values: Dict[str, Any] = {}
        self._last_refresh: Optional[datetime] = None
    
    def refresh_all(self) -> RefreshResult:
        """Refresh signals from all connectors"""
        start_time = datetime.now()
        result = RefreshResult(
            timestamp=start_time,
            success=False
        )
        
        try:
            # Run ingestion cycle
            ingestion_result = self.ingestion.run_ingestion_cycle()
            
            result.signals_refreshed = ingestion_result.signals_normalized
            result.errors = ingestion_result.errors
            
            # Count by domain
            all_signals = self.ingestion.get_all_signals()
            for signal in all_signals:
                domain = signal.domain.value
                result.signals_by_domain[domain] = result.signals_by_domain.get(domain, 0) + 1
            
            result.success = len(result.errors) == 0
            self._last_refresh = datetime.now()
            
        except Exception as e:
            logger.error(f"Signal refresh failed: {e}")
            result.errors.append(str(e))
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def refresh_domain(self, domain: SignalDomain) -> RefreshResult:
        """Refresh signals for a specific domain"""
        start_time = datetime.now()
        result = RefreshResult(
            timestamp=start_time,
            success=False
        )
        
        # Run full refresh (could optimize to domain-specific)
        refresh_result = self.refresh_all()
        
        # Filter by domain
        domain_signals = self.ingestion.get_signals_by_domain(domain)
        
        result.signals_refreshed = len(domain_signals)
        result.signals_by_domain = {domain.value: len(domain_signals)}
        result.success = True
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def get_changes(self, domain: Optional[SignalDomain] = None) -> List[Dict]:
        """Detect changes since last refresh"""
        changes = []
        
        all_signals = self.ingestion.get_all_signals()
        
        for signal in all_signals:
            if domain and signal.domain != domain:
                continue
            
            key = f"{signal.domain.value}:{signal.metric_name}"
            current_value = signal.metric_value
            
            if key in self._last_values:
                last_value = self._last_values[key]
                if current_value != last_value:
                    changes.append({
                        "metric_name": signal.metric_name,
                        "domain": signal.domain.value,
                        "previous_value": last_value,
                        "current_value": current_value,
                        "timestamp": signal.timestamp.isoformat()
                    })
            
            self._last_values[key] = current_value
        
        return changes
    
    def get_stale_signals(self, max_age_minutes: int = 60) -> List[CanonicalSignal]:
        """Get signals that haven't been updated"""
        threshold = datetime.now() - timedelta(minutes=max_age_minutes)
        stale = []
        
        all_signals = self.ingestion.get_all_signals()
        
        for signal in all_signals:
            if signal.timestamp < threshold:
                stale.append(signal)
        
        return stale
    
    def get_refresh_status(self) -> Dict:
        """Get status of signal refresh"""
        return {
            "last_refresh": self._last_refresh.isoformat() if self._last_refresh else None,
            "tracked_metrics": len(self._last_values),
            "ingestion_status": self.ingestion.get_manager_status()
        }


# Global instance
_refresh_engine: Optional[SignalRefreshEngine] = None


def get_signal_refresh_engine() -> SignalRefreshEngine:
    """Get the global signal refresh engine"""
    global _refresh_engine
    if _refresh_engine is None:
        _refresh_engine = SignalRefreshEngine()
    return _refresh_engine


__all__ = [
    "SignalRefreshEngine",
    "RefreshResult",
    "get_signal_refresh_engine",
]
