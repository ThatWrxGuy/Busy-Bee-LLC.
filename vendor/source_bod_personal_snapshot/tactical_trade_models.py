"""
Tactical Trade Intelligence Models

Normalized models for tactical finance trade intelligence including
SPY 0DTE and other strategy engines.

These models provide a stable interface between tactical engines
and the PSIP executive brief pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class TacticalTradeInsight:
    """
    Normalized tactical trade intelligence model.
    
    This is the stable shape passed into PSIP/reporting from
    tactical trade engines like SPY 0DTE.
    """
    strategy_id: str
    strategy_name: str
    generated_at: datetime
    instrument: str
    market_bias: str  # bullish, bearish, neutral
    recommendation: str  # enter, watch, avoid, reduce_risk, hold
    confidence: float  # 0.0 - 1.0
    risk_level: str  # low, medium, high, extreme
    setup_quality: str  # weak, moderate, strong, elite
    thesis: str
    entry_criteria: List[str] = field(default_factory=list)
    invalidation_criteria: List[str] = field(default_factory=list)
    targets: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization"""
        return {
            "strategy_id": self.strategy_id,
            "strategy_name": self.strategy_name,
            "generated_at": self.generated_at.isoformat() if isinstance(self.generated_at, datetime) else self.generated_at,
            "instrument": self.instrument,
            "market_bias": self.market_bias,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "setup_quality": self.setup_quality,
            "thesis": self.thesis,
            "entry_criteria": self.entry_criteria,
            "invalidation_criteria": self.invalidation_criteria,
            "targets": self.targets,
            "warnings": self.warnings,
            "metadata": self.metadata
        }
    
    def is_actionable(self, confidence_threshold: float = 0.6) -> bool:
        """Check if this insight represents an actionable trade"""
        return (
            self.recommendation in ("enter", "watch") and 
            self.confidence >= confidence_threshold and
            self.setup_quality in ("moderate", "strong", "elite")
        )
    
    def has_elevated_risk(self) -> bool:
        """Check if this insight has elevated risk"""
        return self.risk_level in ("high", "extreme") or len(self.warnings) > 0


@dataclass
class TradeOpportunity:
    """Mapped trade opportunity for executive brief"""
    domain: str = "finance"
    title: str = ""
    description: str = ""
    strength: str = ""
    confidence: float = 0.0
    market_bias: str = ""
    instrument: str = ""
    source: str = "spy0dte_engine"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "title": self.title,
            "description": self.description,
            "strength": self.strength,
            "confidence": self.confidence,
            "market_bias": self.market_bias,
            "instrument": self.instrument,
            "source": self.source
        }


@dataclass
class TradeRisk:
    """Mapped trade risk for executive brief"""
    domain: str = "finance"
    title: str = ""
    description: str = ""
    severity: str = ""
    source: str = "spy0dte_engine"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "source": self.source
        }


@dataclass
class TradeAction:
    """Mapped trade action for executive brief"""
    domain: str = "finance"
    action: str = ""
    priority: str = "medium"
    action_type: str = "tactical_trade"
    confidence: float = 0.0
    strategy_name: str = ""
    entry_criteria: List[str] = field(default_factory=list)
    risk_level: str = ""
    source: str = "spy0dte_engine"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "action": self.action,
            "priority": self.priority,
            "action_type": self.action_type,
            "confidence": self.confidence,
            "strategy_name": self.strategy_name,
            "entry_criteria": self.entry_criteria,
            "risk_level": self.risk_level,
            "source": self.source
        }


# Recommendation to priority mapping
RECOMMENDATION_PRIORITY_MAP = {
    "enter": "high",
    "watch": "medium",
    "hold": "low",
    "reduce_risk": "high",
    "avoid": "low"
}

# Setup quality to strength mapping
QUALITY_STRENGTH_MAP = {
    "weak": "low",
    "moderate": "medium",
    "strong": "high",
    "elite": "high"
}

# Risk level to severity mapping
RISK_SEVERITY_MAP = {
    "low": "low",
    "medium": "medium",
    "high": "high",
    "extreme": "critical"
}
