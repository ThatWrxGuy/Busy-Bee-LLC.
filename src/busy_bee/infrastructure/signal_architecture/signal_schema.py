"""
Signal Architecture - BB-DOM-002: Domain Signal Architecture

This module implements the canonical signal architecture for the PSIP platform.

Signal Classes:
- External: Market data, news, economic indicators
- Behavioral: User actions, spending, activity
- System: Internal metrics, portfolio performance
- Derived: Analyzed/computed insights

Phase 1: Signal Schema, Enums, Validation, Normalization
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


# ============== SIGNAL CLASSES ==============

class SignalClass(Enum):
    """Primary signal classification (BB-DOM-002 Section 4)"""
    EXTERNAL = "external"           # Market data, news, economic indicators
    BEHAVIORAL = "behavioral"     # User actions, spending, activity
    SYSTEM = "system"             # Internal metrics, portfolio performance
    DERIVED = "derived"           # Analyzed/computed insights


class SignalPriority(Enum):
    """Signal importance level (BB-DOM-002 Section 6)"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SignalDomain(Enum):
    """Target domains for signals"""
    FINANCE = "finance"
    HEALTH = "health"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    INTELLIGENCE = "intelligence"
    LIFE_ARCHITECTURE = "life_architecture"
    ALL = "all"  # Cross-domain signals


# ============== SIGNAL DATA MODEL ==============

@dataclass
class Signal:
    """
    Canonical Signal Data Model (BB-DOM-002 Section 5)
    
    Required Fields:
    - signal_id, signal_type, signal_class, domain_targets, source, timestamp,
      value, unit, confidence, priority, freshness_ttl, tags
    """
    # Required fields
    signal_id: str
    signal_type: str
    signal_class: SignalClass
    domain_targets: List[SignalDomain]
    source: str
    timestamp: datetime
    value: Any
    unit: str
    confidence: float  # 0.0 - 1.0
    priority: SignalPriority
    freshness_ttl: int  # seconds
    tags: List[str] = field(default_factory=list)
    
    # Optional fields
    normalized_value: Optional[float] = None
    baseline_value: Optional[float] = None
    delta: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    metadata: Dict[str, Any] = field(default_factory=dict)
    derived_from: Optional[List[str]] = None  # Signal IDs this was derived from
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.timestamp + timedelta(seconds=self.freshness_ttl)
    
    def is_expired(self) -> bool:
        """Check if signal has expired (BB-DOM-002 Section 13)"""
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Basic validity check"""
        if not 0.0 <= self.confidence <= 1.0:
            return False
        if not self.domain_targets:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "signal_class": self.signal_class.value,
            "domain_targets": [d.value for d in self.domain_targets],
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "unit": self.unit,
            "confidence": self.confidence,
            "priority": self.priority.value,
            "freshness_ttl": self.freshness_ttl,
            "tags": self.tags,
            "normalized_value": self.normalized_value,
            "baseline_value": self.baseline_value,
            "delta": self.delta,
            "trend": self.trend,
            "metadata": self.metadata,
            "derived_from": self.derived_from,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }


# ============== SIGNAL TYPE REGISTRY ==============

class SignalTypeRegistry:
    """
    Registry of valid signal types per domain (BB-DOM-002 Section 11)
    """
    
    # Finance signals
    FINANCE_EXTERNAL = [
        "asset_price", "volatility_index", "interest_rate", "inflation_rate",
        "macro_release", "options_flow", "market_regime", "sector_performance"
    ]
    FINANCE_BEHAVIORAL = [
        "spending", "saving_rate", "debt_payment", "investing_behavior",
        "trade_frequency", "expense_category", "income_change"
    ]
    FINANCE_SYSTEM = [
        "portfolio_allocation", "risk_exposure", "liquidity_level",
        "debt_ratio", "capital_posture", "return_rate"
    ]
    FINANCE_DERIVED = [
        "financial_stress_score", "market_regime_score", "concentration_risk",
        "trade_expectancy", "opportunity_ranking", "portfolio_health"
    ]
    
    # Health signals
    HEALTH_EXTERNAL = ["weather", "seasonal_illness", "environmental_conditions"]
    HEALTH_BEHAVIORAL = [
        "sleep_duration", "sleep_consistency", "steps", "exercise_session",
        "nutrition_quality", "hydration", "stress_log", "heart_rate"
    ]
    HEALTH_SYSTEM = [
        "recovery_score", "fatigue_score", "workout_adherence", "routine_compliance"
    ]
    HEALTH_DERIVED = [
        "burnout_probability", "health_momentum", "recovery_deficit",
        "habit_stability", "wellness_score"
    ]
    
    # Career signals
    CAREER_EXTERNAL = [
        "job_market_trend", "wage_trend", "industry_condition", "skill_demand"
    ]
    CAREER_BEHAVIORAL = [
        "hours_worked", "deep_work_session", "learning_activity",
        "networking_activity", "project_completion"
    ]
    CAREER_SYSTEM = [
        "performance_trend", "skill_gap_index", "income_growth_rate", "opportunity_pipeline"
    ]
    CAREER_DERIVED = [
        "career_leverage_score", "stagnation_risk", "promotion_readiness",
        "opportunity_fit", "career_health"
    ]
    
    # Relationships signals
    RELATIONSHIPS_EXTERNAL = ["schedule_conflict", "family_event", "travel_period"]
    RELATIONSHIPS_BEHAVIORAL = [
        "partner_time", "communication_frequency", "conflict_event",
        "family_contact", "social_interaction"
    ]
    RELATIONSHIPS_SYSTEM = [
        "relationship_maintenance", "communication_consistency", "trust_stability"
    ]
    RELATIONSHIPS_DERIVED = [
        "relationship_strain_index", "connection_score", "conflict_risk",
        "support_network_health"
    ]
    
    # Intelligence signals
    INTELLIGENCE_EXTERNAL = ["research_input", "article", "book", "expert_content", "topic_interest"]
    INTELLIGENCE_BEHAVIORAL = [
        "study_session", "note_capture", "reading_completion",
        "idea_generation", "decision_review"
    ]
    INTELLIGENCE_SYSTEM = [
        "knowledge_graph_density", "research_coverage", "learning_cadence", "decision_quality"
    ]
    INTELLIGENCE_DERIVED = [
        "insight_generation_rate", "cognitive_overload", "bias_probability", "clarity_score"
    ]
    
    # Life Architecture signals
    LIFE_EXTERNAL = ["travel_opportunity", "seasonal_timing", "environmental_constraint", "life_event"]
    LIFE_BEHAVIORAL = [
        "calendar_density", "leisure_allocation", "home_maintenance",
        "routine_consistency", "time_fragmentation"
    ]
    LIFE_SYSTEM = [
        "balance_score", "schedule_pressure", "value_alignment", "momentum_index"
    ]
    LIFE_DERIVED = [
        "life_friction_score", "life_balance_risk", "misalignment_score", "restoration_need"
    ]
    
    @classmethod
    def get_valid_types(cls, domain: SignalDomain, signal_class: SignalClass) -> List[str]:
        """Get valid signal types for a domain and class"""
        domain_map = {
            SignalDomain.FINANCE: {
                SignalClass.EXTERNAL: cls.FINANCE_EXTERNAL,
                SignalClass.BEHAVIORAL: cls.FINANCE_BEHAVIORAL,
                SignalClass.SYSTEM: cls.FINANCE_SYSTEM,
                SignalClass.DERIVED: cls.FINANCE_DERIVED,
            },
            SignalDomain.HEALTH: {
                SignalClass.EXTERNAL: cls.HEALTH_EXTERNAL,
                SignalClass.BEHAVIORAL: cls.HEALTH_BEHAVIORAL,
                SignalClass.SYSTEM: cls.HEALTH_SYSTEM,
                SignalClass.DERIVED: cls.HEALTH_DERIVED,
            },
            SignalDomain.CAREER: {
                SignalClass.EXTERNAL: cls.CAREER_EXTERNAL,
                SignalClass.BEHAVIORAL: cls.CAREER_BEHAVIORAL,
                SignalClass.SYSTEM: cls.CAREER_SYSTEM,
                SignalClass.DERIVED: cls.CAREER_DERIVED,
            },
            SignalDomain.RELATIONSHIPS: {
                SignalClass.EXTERNAL: cls.RELATIONSHIPS_EXTERNAL,
                SignalClass.BEHAVIORAL: cls.RELATIONSHIPS_BEHAVIORAL,
                SignalClass.SYSTEM: cls.RELATIONSHIPS_SYSTEM,
                SignalClass.DERIVED: cls.RELATIONSHIPS_DERIVED,
            },
            SignalDomain.INTELLIGENCE: {
                SignalClass.EXTERNAL: cls.INTELLIGENCE_EXTERNAL,
                SignalClass.BEHAVIORAL: cls.INTELLIGENCE_BEHAVIORAL,
                SignalClass.SYSTEM: cls.INTELLIGENCE_SYSTEM,
                SignalClass.DERIVED: cls.INTELLIGENCE_DERIVED,
            },
            SignalDomain.LIFE_ARCHITECTURE: {
                SignalClass.EXTERNAL: cls.LIFE_EXTERNAL,
                SignalClass.BEHAVIORAL: cls.LIFE_BEHAVIORAL,
                SignalClass.SYSTEM: cls.LIFE_SYSTEM,
                SignalClass.DERIVED: cls.LIFE_DERIVED,
            },
        }
        return domain_map.get(domain, {}).get(signal_class, [])


# ============== SIGNAL VALIDATION ==============

class ValidationResult:
    """Result of signal validation"""
    def __init__(self, valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    @property
    def is_valid(self) -> bool:
        return self.valid


class SignalValidator:
    """
    Signal Validation Service (BB-DOM-002 Section 8)
    
    Validation checks:
    - schema validity
    - allowed signal class
    - supported domain targets
    - timestamp validity
    - non-null required fields
    - acceptable confidence bounds
    - valid priority value
    - source trust policy
    """
    
    def __init__(self):
        self.trusted_sources = {
            "brokerage_api", "wearable", "calendar", "manual_input",
            "analytics_engine", "market_api", "news_api", "bank_api",
            "fitness_app", "linkedin", "system"
        }
    
    def validate(self, signal: Signal) -> ValidationResult:
        """Validate a signal against all rules"""
        errors = []
        warnings = []
        
        # 1. Schema validity - check required fields
        if not signal.signal_id:
            errors.append("signal_id is required")
        if not signal.signal_type:
            errors.append("signal_type is required")
        if not signal.source:
            errors.append("source is required")
        
        # 2. Check signal class is valid
        if not isinstance(signal.signal_class, SignalClass):
            errors.append(f"Invalid signal_class: {signal.signal_class}")
        
        # 3. Check domain targets
        if not signal.domain_targets:
            errors.append("At least one domain_target is required")
        
        # 4. Timestamp validity
        if not signal.timestamp:
            errors.append("timestamp is required")
        elif signal.timestamp > datetime.now() + timedelta(hours=1):
            warnings.append("timestamp is in the future")
        
        # 5. Confidence bounds
        if not 0.0 <= signal.confidence <= 1.0:
            errors.append(f"confidence must be 0.0-1.0, got {signal.confidence}")
        
        # 6. Priority validity
        if not isinstance(signal.priority, SignalPriority):
            errors.append(f"Invalid priority: {signal.priority}")
        
        # 7. Source trust policy
        if signal.source not in self.trusted_sources:
            warnings.append(f"Unknown source: {signal.source}")
        
        # 8. Freshness TTL
        if signal.freshness_ttl <= 0:
            errors.append("freshness_ttl must be positive")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


# ============== SIGNAL NORMALIZATION ==============

class SignalNormalizer:
    """
    Signal Normalization Service (BB-DOM-002 Section 7)
    
    Responsibilities:
    - standardize units
    - align timestamps
    - validate value ranges
    - handle missing data
    - compute baseline comparisons
    - convert freeform inputs to structured format
    """
    
    # Unit conversion maps
    UNIT_CONVERSIONS = {
        # Time
        ("minutes", "hours"): lambda x: x / 60,
        ("seconds", "hours"): lambda x: x / 3600,
        ("minutes", "days"): lambda x: x / 1440,
        # Currency
        ("dollars", "USD"): lambda x: x,  # Already normalized
        ("$", "USD"): lambda x: x,
        # Percentage
        ("percent", "percentage"): lambda x: x,
        ("%", "percentage"): lambda x: x,
    }
    
    # Value ranges for validation
    VALUE_RANGES = {
        "sleep_duration": (0, 24),
        "heart_rate": (30, 220),
        "steps": (0, 100000),
        "confidence": (0.0, 1.0),
        "spending": (0, 1000000),
        "hours_worked": (0, 168),
    }
    
    def normalize(self, signal: Signal) -> Signal:
        """Normalize a signal"""
        # 1. Standardize units
        signal = self._normalize_units(signal)
        
        # 2. Validate and clamp value ranges
        signal = self._normalize_value_range(signal)
        
        # 3. Compute normalized value (0-1 scale where applicable)
        signal = self._compute_normalized_value(signal)
        
        # 4. Compute delta from baseline
        signal = self._compute_delta(signal)
        
        # 5. Determine trend
        signal = self._compute_trend(signal)
        
        return signal
    
    def _normalize_units(self, signal: Signal) -> Signal:
        """Standardize units"""
        # For now, just ensure unit is set
        if not signal.unit and signal.value is not None:
            signal.unit = self._infer_unit(signal.signal_type)
        return signal
    
    def _infer_unit(self, signal_type: str) -> str:
        """Infer unit from signal type"""
        if "duration" in signal_type or "time" in signal_type:
            return "hours"
        elif "rate" in signal_type or "score" in signal_type or "confidence" in signal_type:
            return "percentage"
        elif "spending" in signal_type or "price" in signal_type or "income" in signal_type:
            return "USD"
        elif "count" in signal_type or "frequency" in signal_type:
            return "count"
        return "score"
    
    def _normalize_value_range(self, signal: Signal) -> Signal:
        """Validate and clamp value to acceptable range"""
        range_key = signal.signal_type
        if range_key in self.VALUE_RANGES:
            min_val, max_val = self.VALUE_RANGES[range_key]
            if isinstance(signal.value, (int, float)):
                signal.value = max(min_val, min(signal.value, max_val))
        return signal
    
    def _compute_normalized_value(self, signal: Signal) -> Signal:
        """Compute normalized 0-1 value where applicable"""
        range_key = signal.signal_type
        if range_key in self.VALUE_RANGES and isinstance(signal.value, (int, float)):
            min_val, max_val = self.VALUE_RANGES[range_key]
            if max_val > min_val:
                signal.normalized_value = (signal.value - min_val) / (max_val - min_val)
        return signal
    
    def _compute_delta(self, signal: Signal) -> Signal:
        """Compute change from baseline"""
        if signal.baseline_value is not None and isinstance(signal.value, (int, float)):
            signal.delta = signal.value - signal.baseline_value
        return signal
    
    def _compute_trend(self, signal: Signal) -> Signal:
        """Determine trend direction"""
        if signal.delta is not None:
            if signal.delta > 0.1:
                signal.trend = "up"
            elif signal.delta < -0.1:
                signal.trend = "down"
            else:
                signal.trend = "stable"
        return signal


# ============== SIGNAL FACTORY ==============

class SignalFactory:
    """
    Factory for creating standardized signals
    """
    
    def __init__(self):
        self.validator = SignalValidator()
        self.normalizer = SignalNormalizer()
        self._signal_counter = 0
    
    def create_signal(
        self,
        signal_type: str,
        signal_class: SignalClass,
        domain_targets: List[SignalDomain],
        source: str,
        value: Any,
        unit: str,
        confidence: float = 0.5,
        priority: SignalPriority = SignalPriority.MEDIUM,
        freshness_ttl: int = 3600,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Signal:
        """Create and validate a new signal"""
        self._signal_counter += 1
        
        signal = Signal(
            signal_id=f"sig_{self._signal_counter}_{datetime.now().timestamp()}",
            signal_type=signal_type,
            signal_class=signal_class,
            domain_targets=domain_targets,
            source=source,
            timestamp=datetime.now(),
            value=value,
            unit=unit,
            confidence=confidence,
            priority=priority,
            freshness_ttl=freshness_ttl,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Validate
        validation = self.validator.validate(signal)
        if not validation.valid:
            raise ValueError(f"Invalid signal: {validation.errors}")
        
        # Normalize
        signal = self.normalizer.normalize(signal)
        
        return signal
    
    def create_derived_signal(
        self,
        signal_type: str,
        source_signals: List[Signal],
        computed_value: Any,
        unit: str,
        confidence: float = 0.5,
        priority: SignalPriority = SignalPriority.MEDIUM,
        tags: List[str] = None
    ) -> Signal:
        """Create a derived signal from existing signals"""
        # Determine target domains from source signals
        target_domains = set()
        for sig in source_signals:
            target_domains.update(sig.domain_targets)
        
        self._signal_counter += 1
        
        signal = Signal(
            signal_id=f"derived_{self._signal_counter}_{datetime.now().timestamp()}",
            signal_type=signal_type,
            signal_class=SignalClass.DERIVED,
            domain_targets=list(target_domains),
            source="derived_signal_engine",
            timestamp=datetime.now(),
            value=computed_value,
            unit=unit,
            confidence=confidence,
            priority=priority,
            freshness_ttl=3600,
            tags=tags or ["derived"],
            derived_from=[s.signal_id for s in source_signals]
        )
        
        return self.normalizer.normalize(signal)


__all__ = [
    # Enums
    "SignalClass",
    "SignalPriority", 
    "SignalDomain",
    
    # Core
    "Signal",
    "ValidationResult",
    "SignalValidator",
    "SignalNormalizer",
    "SignalFactory",
    "SignalTypeRegistry",
]
