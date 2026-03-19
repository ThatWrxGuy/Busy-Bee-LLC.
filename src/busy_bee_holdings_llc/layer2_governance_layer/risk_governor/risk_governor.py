"""
Risk Governor - Enforces risk management policies
Part of Layer 2: Governance Layer
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RiskLevel(Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(Enum):
    """Status of a risk assessment"""
    MONITORING = "monitoring"
    MITIGATED = "mitigated"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


@dataclass
class Risk:
    """A tracked risk"""
    id: str
    name: str
    description: str
    domain: str
    risk_level: RiskLevel
    probability: float  # 0.0 - 1.0
    impact: float  # 0.0 - 1.0
    status: RiskStatus
    mitigation_plan: str
    owner: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RiskThreshold:
    """Risk threshold configuration"""
    domain: str
    max_risk_score: float  # Maximum allowed risk score
    escalation_threshold: float  # Threshold for escalation
    requires_approval_above: float  # Risk level requiring approval


class RiskGovernor:
    """
    Risk Governor enforces risk management policies.
    
    Responsibilities:
    - Assess risks
    - Enforce thresholds
    - Monitor risk levels
    - Escalate when necessary
    """
    
    def __init__(self):
        self.risks: List[Risk] = []
        self.thresholds: Dict[str, RiskThreshold] = {}
        self.risk_history: List[Dict[str, Any]] = []
    
    def add_threshold(
        self,
        domain: str,
        max_risk_score: float,
        escalation_threshold: float,
        requires_approval_above: float
    ):
        """Add a risk threshold for a domain"""
        threshold = RiskThreshold(
            domain=domain,
            max_risk_score=max_risk_score,
            escalation_threshold=escalation_threshold,
            requires_approval_above=requires_approval_above
        )
        self.thresholds[domain] = threshold
    
    def assess_risk(
        self,
        name: str,
        description: str,
        domain: str,
        probability: float,
        impact: float,
        mitigation_plan: str,
        owner: Optional[str] = None
    ) -> Risk:
        """Assess and register a new risk"""
        # Calculate risk level
        risk_score = probability * impact
        
        if risk_score < 0.2:
            level = RiskLevel.LOW
        elif risk_score < 0.5:
            level = RiskLevel.MEDIUM
        elif risk_score < 0.8:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL
        
        risk = Risk(
            id=f"risk_{len(self.risks) + 1}_{datetime.now().timestamp()}",
            name=name,
            description=description,
            domain=domain,
            risk_level=level,
            probability=probability,
            impact=impact,
            status=RiskStatus.MONITORING,
            mitigation_plan=mitigation_plan,
            owner=owner
        )
        
        self.risks.append(risk)
        
        # Log to history
        self.risk_history.append({
            "risk_id": risk.id,
            "action": "assessed",
            "risk_score": risk_score,
            "level": level.value,
            "timestamp": datetime.now().isoformat()
        })
        
        return risk
    
    def evaluate_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a strategy's risk"""
        domain = strategy.get("domain", "general")
        risk_factors = strategy.get("risk_factors", {})
        
        # Calculate overall risk score
        risk_score = 0.0
        for factor, value in risk_factors.items():
            risk_score += value
        risk_score = min(1.0, risk_score / len(risk_factors)) if risk_factors else 0.3
        
        # Check against threshold
        threshold = self.thresholds.get(domain)
        
        evaluation = {
            "strategy_id": strategy.get("id"),
            "domain": domain,
            "risk_score": risk_score,
            "approved": True,
            "requires_approval": False,
            "warnings": []
        }
        
        if threshold:
            if risk_score > threshold.max_risk_score:
                evaluation["approved"] = False
                evaluation["warnings"].append(f"Risk score {risk_score} exceeds maximum {threshold.max_risk_score}")
            
            if risk_score > threshold.requires_approval_above:
                evaluation["requires_approval"] = True
            
            if risk_score > threshold.escalation_threshold:
                evaluation["warnings"].append("Risk requires escalation")
        
        return evaluation
    
    def escalate_risk(self, risk_id: str) -> Optional[Risk]:
        """Escalate a risk to critical"""
        risk = next((r for r in self.risks if r.id == risk_id), None)
        
        if not risk:
            return None
        
        risk.status = RiskStatus.ESCALATED
        risk.risk_level = RiskLevel.CRITICAL
        risk.updated_at = datetime.now()
        
        self.risk_history.append({
            "risk_id": risk.id,
            "action": "escalated",
            "timestamp": datetime.now().isoformat()
        })
        
        return risk
    
    def mitigate_risk(self, risk_id: str) -> Optional[Risk]:
        """Mark a risk as mitigated"""
        risk = next((r for r in self.risks if r.id == risk_id), None)
        
        if not risk:
            return None
        
        risk.status = RiskStatus.MITIGATED
        risk.updated_at = datetime.now()
        
        self.risk_history.append({
            "risk_id": risk.id,
            "action": "mitigated",
            "timestamp": datetime.now().isoformat()
        })
        
        return risk
    
    def get_risks_by_domain(self, domain: str) -> List[Risk]:
        """Get all risks for a domain"""
        return [r for r in self.risks if r.domain == domain]
    
    def get_critical_risks(self) -> List[Risk]:
        """Get all critical risks"""
        return [
            r for r in self.risks 
            if r.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk summary"""
        return {
            "total_risks": len(self.risks),
            "by_level": {
                "low": len([r for r in self.risks if r.risk_level == RiskLevel.LOW]),
                "medium": len([r for r in self.risks if r.risk_level == RiskLevel.MEDIUM]),
                "high": len([r for r in self.risks if r.risk_level == RiskLevel.HIGH]),
                "critical": len([r for r in self.risks if r.risk_level == RiskLevel.CRITICAL])
            },
            "by_status": {
                "monitoring": len([r for r in self.risks if r.status == RiskStatus.MONITORING]),
                "mitigated": len([r for r in self.risks if r.status == RiskStatus.MITIGATED]),
                "escalated": len([r for r in self.risks if r.status == RiskStatus.ESCALATED]),
                "resolved": len([r for r in self.risks if r.status == RiskStatus.RESOLVED])
            },
            "critical_risks": [
                {"id": r.id, "name": r.name, "domain": r.domain}
                for r in self.get_critical_risks()
            ]
        }
