"""
Signal Validator

Validates signals for quality, completeness, and correctness.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class ValidationSeverity(Enum):
    """Severity of validation issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue"""
    field: str
    message: str
    severity: ValidationSeverity
    value: Any = None


@dataclass
class ValidationResult:
    """Result of signal validation"""
    is_valid: bool
    signal_id: str
    issues: List[ValidationIssue]
    validated_at: datetime
    
    def add_issue(
        self,
        field: str,
        message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ) -> None:
        """Add a validation issue"""
        self.issues.append(ValidationIssue(
            field=field,
            message=message,
            severity=severity,
            value=None
        ))
        if severity == ValidationSeverity.ERROR:
            self.is_valid = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "signal_id": self.signal_id,
            "issues": [
                {
                    "field": i.field,
                    "message": i.message,
                    "severity": i.severity.value
                }
                for i in self.issues
            ],
            "validated_at": self.validated_at.isoformat()
        }


class SignalValidator:
    """
    Validates signals for quality and correctness.
    
    Checks:
    - Required fields present
    - Data type correctness
    - Value ranges
    - Temporal validity
    - Schema compliance
    """
    
    # Required fields for canonical signals
    REQUIRED_FIELDS = [
        "signal_id",
        "domain",
        "source",
        "timestamp",
        "metric_name",
        "metric_value"
    ]
    
    # Valid domains
    VALID_DOMAINS = [
        "finance", "health", "career", "relationships",
        "intelligence", "life_architecture", "general"
    ]
    
    # Valid units
    VALID_UNITS = [
        "USD", "EUR", "GBP", "percent", "count",
        "hours", "days", "rating", "boolean", "text", "unknown"
    ]
    
    # Value ranges by unit type
    VALUE_RANGES = {
        "USD": (0, 1000000000),
        "EUR": (0, 1000000000),
        "GBP": (0, 1000000000),
        "percent": (0, 100),
        "count": (0, 1000000),
        "hours": (0, 24),
        "days": (0, 365),
        "rating": (1, 5),
    }
    
    def __init__(
        self,
        max_age_hours: int = 24,
        min_confidence: float = 0.3,
        strict_mode: bool = False
    ):
        self.max_age_hours = max_age_hours
        self.min_confidence = min_confidence
        self.strict_mode = strict_mode
    
    def validate(self, signal: Dict) -> ValidationResult:
        """
        Validate a signal.
        
        Args:
            signal: Signal dictionary to validate
            
        Returns:
            ValidationResult with validation status and issues
        """
        signal_id = signal.get("signal_id", "unknown")
        result = ValidationResult(
            is_valid=True,
            signal_id=signal_id,
            issues=[],
            validated_at=datetime.now()
        )
        
        # Check required fields
        self._validate_required_fields(signal, result)
        
        # Validate data types
        self._validate_data_types(signal, result)
        
        # Validate value ranges
        self._validate_value_ranges(signal, result)
        
        # Validate temporal data
        self._validate_temporal(signal, result)
        
        # Validate confidence
        self._validate_confidence(signal, result)
        
        # Validate domain and unit
        self._validate_domain_unit(signal, result)
        
        return result
    
    def _validate_required_fields(
        self,
        signal: Dict,
        result: ValidationResult
    ) -> None:
        """Validate required fields are present"""
        for field in self.REQUIRED_FIELDS:
            if field not in signal or signal[field] is None:
                result.add_issue(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    severity=ValidationSeverity.ERROR
                )
    
    def _validate_data_types(
        self,
        signal: Dict,
        result: ValidationResult
    ) -> None:
        """Validate data types of fields"""
        # signal_id should be string
        if "signal_id" in signal and not isinstance(signal["signal_id"], str):
            result.add_issue(
                field="signal_id",
                message="signal_id must be a string",
                severity=ValidationSeverity.ERROR
            )
        
        # timestamp should be datetime or ISO string
        if "timestamp" in signal:
            ts = signal["timestamp"]
            if isinstance(ts, str):
                try:
                    datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    result.add_issue(
                        field="timestamp",
                        message="timestamp is not a valid ISO format",
                        severity=ValidationSeverity.ERROR
                    )
            elif not isinstance(ts, datetime):
                result.add_issue(
                    field="timestamp",
                    message="timestamp must be datetime or ISO string",
                    severity=ValidationSeverity.ERROR
                )
        
        # confidence should be float between 0 and 1
        if "confidence" in signal:
            conf = signal["confidence"]
            if not isinstance(conf, (int, float)):
                result.add_issue(
                    field="confidence",
                    message="confidence must be numeric",
                    severity=ValidationSeverity.ERROR
                )
            elif not 0 <= conf <= 1:
                result.add_issue(
                    field="confidence",
                    message="confidence must be between 0 and 1",
                    severity=ValidationSeverity.ERROR
                )
        
        # tags should be a list
        if "tags" in signal and not isinstance(signal["tags"], list):
            result.add_issue(
                field="tags",
                message="tags must be a list",
                severity=ValidationSeverity.ERROR
            )
    
    def _validate_value_ranges(
        self,
        signal: Dict,
        result: ValidationResult
    ) -> None:
        """Validate value is within acceptable range"""
        unit = signal.get("unit", "").lower()
        value = signal.get("metric_value")
        
        if unit not in self.VALUE_RANGES:
            return
        
        if value is None:
            result.add_issue(
                field="metric_value",
                message="metric_value is None",
                severity=ValidationSeverity.WARNING
            )
            return
        
        if not isinstance(value, (int, float)):
            return  # Can't check range for non-numeric
        
        min_val, max_val = self.VALUE_RANGES[unit]
        
        if not min_val <= value <= max_val:
            result.add_issue(
                field="metric_value",
                message=f"value {value} outside range [{min_val}, {max_val}] for unit {unit}",
                severity=ValidationSeverity.WARNING
            )
    
    def _validate_temporal(
        self,
        signal: Dict,
        result: ValidationResult
    ) -> None:
        """Validate temporal aspects of the signal"""
        ts = signal.get("timestamp")
        if not ts:
            return
        
        # Parse timestamp
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                return
        
        # Check if not too old
        now = datetime.now()
        age = now - ts
        
        if age > timedelta(hours=self.max_age_hours):
            result.add_issue(
                field="timestamp",
                message=f"signal is {age.total_seconds()/3600:.1f} hours old (max: {self.max_age_hours})",
                severity=ValidationSeverity.WARNING
            )
        
        # Check if not in the future
        if ts > now + timedelta(minutes=5):
            result.add_issue(
                field="timestamp",
                message="timestamp is in the future",
                severity=ValidationSeverity.WARNING
            )
    
    def _validate_confidence(
        self,
        signal: Dict,
        result: ValidationResult
    ) -> None:
        """Validate confidence level"""
        confidence = signal.get("confidence", 0.5)
        
        if confidence < self.min_confidence:
            severity = ValidationSeverity.ERROR if self.strict_mode else ValidationSeverity.WARNING
            result.add_issue(
                field="confidence",
                message=f"confidence {confidence} below minimum {self.min_confidence}",
                severity=severity
            )
    
    def _validate_domain_unit(
        self,
        signal: Dict,
        result: ValidationResult
    ) -> None:
        """Validate domain and unit values"""
        domain = signal.get("domain", "").lower()
        unit = signal.get("unit", "").lower()
        
        # Validate domain
        if domain and domain not in self.VALID_DOMAINS:
            result.add_issue(
                field="domain",
                message=f"unknown domain '{domain}'",
                severity=ValidationSeverity.WARNING
            )
        
        # Validate unit
        if unit and unit not in self.VALUE_RANGES:
            # Only warn if it's not a known non-numeric unit
            if unit not in ["boolean", "text", "rating", "unknown"]:
                result.add_issue(
                    field="unit",
                    message=f"unknown unit '{unit}'",
                    severity=ValidationSeverity.INFO
                )
    
    def validate_batch(self, signals: List[Dict]) -> List[ValidationResult]:
        """Validate a batch of signals"""
        return [self.validate(s) for s in signals]
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict:
        """Get summary of validation results"""
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        
        issues_by_severity = {
            "errors": 0,
            "warnings": 0,
            "infos": 0
        }
        
        for result in results:
            for issue in result.issues:
                if issue.severity == ValidationSeverity.ERROR:
                    issues_by_severity["errors"] += 1
                elif issue.severity == ValidationSeverity.WARNING:
                    issues_by_severity["warnings"] += 1
                else:
                    issues_by_severity["infos"] += 1
        
        return {
            "total_signals": total,
            "valid_signals": valid,
            "invalid_signals": total - valid,
            "validation_rate": valid / total if total > 0 else 0,
            "issues": issues_by_severity
        }


__all__ = [
    "SignalValidator",
    "ValidationIssue",
    "ValidationResult",
    "ValidationSeverity",
]
