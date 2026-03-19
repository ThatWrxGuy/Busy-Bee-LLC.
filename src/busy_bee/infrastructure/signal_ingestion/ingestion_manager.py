"""
Signal Ingestion Manager

Orchestrates the entire signal ingestion pipeline:
1. Collect signals from connectors
2. Normalize to canonical format
3. Validate signals
4. Store in cache/memory
5. Trigger downstream processing
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import threading
import logging

from .signal_connector_base import (
    SignalConnector, ConnectorConfig, ConnectorStatus, RawSignal
)
from .signal_connector_registry import SignalConnectorRegistry, get_connector_registry
from .signal_normalizer import SignalNormalizer, CanonicalSignal, SignalDomain
from .signal_validator import SignalValidator, ValidationResult
from .signal_cache import SignalCache, get_signal_cache
from .signal_health_monitor import SignalHealthMonitor, get_health_monitor


logger = logging.getLogger(__name__)


class IngestionStatus(Enum):
    """Status of ingestion operation"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class IngestionResult:
    """Result of an ingestion cycle"""
    timestamp: datetime
    status: IngestionStatus
    
    # Counts
    connectors_run: int = 0
    signals_collected: int = 0
    signals_normalized: int = 0
    signals_validated: int = 0
    signals_stored: int = 0
    
    # Errors
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Timing
    duration_ms: float = 0.0
    
    # Sample signals
    sample_signals: List[Dict] = field(default_factory=list)


class SignalIngestionManager:
    """
    Main orchestration class for signal ingestion.
    
    Pipeline:
    1. Collect from connectors
    2. Normalize
    3. Validate
    4. Store
    5. Notify downstream
    """
    
    def __init__(
        self,
        registry: Optional[SignalConnectorRegistry] = None,
        cache: Optional[SignalCache] = None,
        health_monitor: Optional[SignalHealthMonitor] = None
    ):
        self.registry = registry or get_connector_registry()
        self.cache = cache or get_signal_cache()
        self.health_monitor = health_monitor or get_health_monitor()
        
        self.normalizer = SignalNormalizer()
        self.validator = SignalValidator()
        
        self.status = IngestionStatus.IDLE
        self._runners: Dict[str, threading.Thread] = {}
        self._running = False
        
        # Callbacks for downstream processing
        self._on_signals_ingested: List[Callable[[List[CanonicalSignal]], None]] = []
        self._on_validation_failure: List[Callable[[ValidationResult], None]] = []
    
    def register_connector(self, config: ConnectorConfig) -> bool:
        """Register and create a connector"""
        try:
            connector = self.registry.create_connector(
                connector_type=config.connector_id.split("_")[0],
                config=config
            )
            if connector:
                logger.info(f"Registered connector: {config.connector_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to register connector: {e}")
            return False
    
    def connect_all(self) -> Dict[str, bool]:
        """Connect all registered connectors"""
        results = {}
        for connector in self.registry.get_all_connectors():
            try:
                success = connector.connect()
                results[connector.config.connector_id] = success
                if success:
                    logger.info(f"Connected: {connector.config.connector_id}")
            except Exception as e:
                logger.error(f"Failed to connect {connector.config.connector_id}: {e}")
                results[connector.config.connector_id] = False
        return results
    
    def disconnect_all(self) -> None:
        """Disconnect all connectors"""
        for connector in self.registry.get_all_connectors():
            try:
                connector.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting {connector.config.connector_id}: {e}")
    
    def run_ingestion_cycle(self) -> IngestionResult:
        """
        Run a single ingestion cycle.
        
        Returns:
            IngestionResult with statistics and any errors
        """
        start_time = datetime.now()
        result = IngestionResult(
            timestamp=start_time,
            status=IngestionStatus.RUNNING
        )
        
        try:
            # Phase 1: Collect from all connectors
            all_raw_signals: List[RawSignal] = []
            connectors_run = 0
            
            for connector in self.registry.get_all_connectors():
                if not connector.config.enabled:
                    continue
                
                if connector.status != ConnectorStatus.CONNECTED:
                    continue
                
                connectors_run += 1
                
                try:
                    raw_signals = connector.collect()
                    all_raw_signals.extend(raw_signals)
                    result.signals_collected += len(raw_signals)
                    
                    # Record health
                    self.health_monitor.record_collection(
                        connector_id=connector.config.connector_id,
                        connector_type=connector.connector_type,
                        success=True,
                        latency_ms=0,
                        signal_count=len(raw_signals)
                    )
                    
                except Exception as e:
                    logger.error(f"Collection error from {connector.config.connector_id}: {e}")
                    result.errors.append(f"{connector.config.connector_id}: {str(e)}")
                    
                    self.health_monitor.record_collection(
                        connector_id=connector.config.connector_id,
                        connector_type=connector.connector_type,
                        success=False,
                        latency_ms=0,
                        error=str(e)
                    )
            
            result.connectors_run = connectors_run
            
            # Phase 2: Normalize signals
            canonical_signals: List[CanonicalSignal] = []
            
            for raw in all_raw_signals:
                try:
                    normalized_data = connector.normalize(raw)
                    canonical = self.normalizer.normalize(
                        raw_data={
                            **raw.data,
                            "signal_id": raw.connector_id + "_" + str(hash(str(raw.data)))
                        },
                        connector_id=raw.connector_id,
                        source=raw.source
                    )
                    canonical_signals.append(canonical)
                    result.signals_normalized += 1
                    
                except Exception as e:
                    logger.warning(f"Normalization error: {e}")
                    result.warnings.append(f"Normalization: {str(e)}")
            
            # Phase 3: Validate signals
            validated_signals: List[CanonicalSignal] = []
            
            for signal in canonical_signals:
                validation = self.validator.validate(signal.to_dict())
                
                if validation.is_valid:
                    validated_signals.append(signal)
                    result.signals_validated += 1
                else:
                    result.warnings.append(
                        f"Validation failed for {signal.signal_id}: "
                        f"{[i.message for i in validation.issues]}"
                    )
            
            # Phase 4: Store signals
            for signal in validated_signals:
                try:
                    cache_key = f"signal:{signal.signal_id}"
                    self.cache.set(cache_key, signal.to_dict())
                    result.signals_stored += 1
                except Exception as e:
                    logger.warning(f"Cache error: {e}")
                    result.warnings.append(f"Cache: {str(e)}")
            
            # Phase 5: Trigger downstream
            if validated_signals and self._on_signals_ingested:
                for callback in self._on_signals_ingested:
                    try:
                        callback(validated_signals)
                    except Exception as e:
                        logger.error(f"Downstream callback error: {e}")
                        result.errors.append(f"Callback: {str(e)}")
            
            # Store sample signals for result
            result.sample_signals = [
                s.to_dict() for s in validated_signals[:5]
            ]
            
            result.status = IngestionStatus.IDLE
            
        except Exception as e:
            result.status = IngestionStatus.ERROR
            result.errors.append(f"Fatal: {str(e)}")
            logger.error(f"Ingestion cycle error: {e}")
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds() * 1000
        result.duration_ms = duration
        
        return result
    
    def get_signals_by_domain(
        self,
        domain: SignalDomain,
        limit: int = 100
    ) -> List[CanonicalSignal]:
        """Get cached signals filtered by domain"""
        signals = []
        
        for key in self.cache.keys():
            if key.startswith("signal:"):
                data = self.cache.get(key)
                if data and data.get("domain") == domain.value:
                    signals.append(CanonicalSignal.from_dict(data))
                    if len(signals) >= limit:
                        break
        
        return signals
    
    def get_all_signals(self, limit: int = 1000) -> List[CanonicalSignal]:
        """Get all cached signals"""
        signals = []
        
        for key in self.cache.keys():
            if key.startswith("signal:"):
                data = self.cache.get(key)
                if data:
                    signals.append(CanonicalSignal.from_dict(data))
                    if len(signals) >= limit:
                        break
        
        return signals
    
    def get_manager_status(self) -> Dict:
        """Get status of the ingestion manager"""
        return {
            "status": self.status.value,
            "connectors": self.registry.get_registry_summary(),
            "cache": self.cache.get_stats(),
            "health": self.health_monitor.get_health_summary()
        }
    
    def on_signals_ingested(self, callback: Callable[[List[CanonicalSignal]], None]) -> None:
        """Register callback for when signals are ingested"""
        self._on_signals_ingested.append(callback)
    
    def on_validation_failure(self, callback: Callable[[ValidationResult], None]) -> None:
        """Register callback for validation failures"""
        self._on_validation_failure.append(callback)
    
    def start_continuous_ingestion(
        self,
        interval_seconds: int = 300,
        run_immediately: bool = True
    ) -> None:
        """Start continuous ingestion in background thread"""
        if self._running:
            return
        
        self._running = True
        
        def run_loop():
            if run_immediately:
                self.run_ingestion_cycle()
            
            while self._running:
                import time
                time.sleep(interval_seconds)
                if self._running:
                    self.run_ingestion_cycle()
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        self._runners["continuous"] = thread
        logger.info(f"Started continuous ingestion (interval: {interval_seconds}s)")
    
    def stop_continuous_ingestion(self) -> None:
        """Stop continuous ingestion"""
        self._running = False
        if "continuous" in self._runners:
            del self._runners["continuous"]
        logger.info("Stopped continuous ingestion")


# Global ingestion manager
_global_manager: Optional[SignalIngestionManager] = None


def get_ingestion_manager() -> SignalIngestionManager:
    """Get the global ingestion manager"""
    global _global_manager
    if _global_manager is None:
        _global_manager = SignalIngestionManager()
    return _global_manager


__all__ = [
    "SignalIngestionManager",
    "IngestionResult",
    "IngestionStatus",
    "get_ingestion_manager",
]
