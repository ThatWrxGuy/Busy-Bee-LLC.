"""
# Strategic Discipline Framework (BB-INT-000)

The Strategic Intelligence Engine operates within the following discipline rules:

## Priority Limits: The 3-3-3 Rule
- Maximum 3 ACTIVE PRIORITIES at once
- Maximum 3 SECONDARY FOCUS items
- Maximum 3 WATCH items

## Decision Priority Formula
```
Priority Score = (Impact × 0.35) + (Urgency × 0.25) + (Leverage × 0.20) + (Alignment × 0.15) + (Confidence × 0.05)
```

## Score Thresholds
| Score | Classification |
|-------|---------------|
| 0-30 | DEFER |
| 31-50 | WATCH |
| 51-70 | SECONDARY |
| 71-100 | PRIORITY |

---

## Strategic Intelligence Engine - BB-INT-001

This module implements the Strategic Intelligence Engine that transforms Busy Bee from a domain-aware reporting system into a true life strategy operating system.

Core Capabilities:
- Strategy Generation
- Scenario Simulation  
- Strategic Debate
- Hidden Leverage Discovery
- Alignment Scoring
- Strategic Path Ranking
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


# ============== ENUMS ==============

class TimeHorizon(Enum):
    """Strategy time horizons (BB-INT-001 Section 5.2)"""
    IMMEDIATE = "immediate"      # 1-14 days
    NEAR_TERM = "near_term"     # 1-12 weeks
    MID_TERM = "mid_term"       # 3-12 months
    LONG_TERM = "long_term"     # 1-5 years


class StrategicPosture(Enum):
    """Current strategic posture"""
    STABILIZE = "stabilize"
    SELECTIVELY_ADVANCE = "selectively_advance"
    AGGRESSIVE_GROWTH = "aggressive_growth"
    CONSOLIDATE = "consolidate"
    TRANSITION = "transition"


class ScenarioCase(Enum):
    """Scenario projection types"""
    BEST_CASE = "best_case"
    BASE_CASE = "base_case"
    WORST_CASE = "worst_case"


class StrategyRejectionReason(Enum):
    """Reasons for rejecting a strategy"""
    RISK_TOO_HIGH = "risk_too_high"
    ALIGNMENT_FAILED = "alignment_failed"
    FEASIBILITY_LOW = "feasibility_low"
    RESOURCE_CONSTRAINT = "resource_constraint"
    GOVERNANCE_VETO = "governance_veto"


# ============== DATA MODELS ==============

@dataclass
class StrategicOption:
    """
    A candidate strategic option (BB-INT-001 Section 5.1)
    
    Represents a plausible strategic path that can be evaluated.
    """
    option_id: str
    title: str
    description: str
    domain: str  # Primary domain
    
    # Actions in this strategy
    actions: List[str] = field(default_factory=list)
    
    # Time horizon
    primary_horizon: TimeHorizon = TimeHorizon.NEAR_TERM
    
    # Cross-domain effects
    cross_domain_impact: Dict[str, str] = field(default_factory=dict)
    
    # Scores (0-1)
    leverage_score: float = 0.0
    risk_score: float = 0.0
    feasibility_score: float = 0.0
    alignment_score: float = 0.0
    compounding_score: float = 0.0
    cross_domain_benefit: float = 0.0
    reversibility_score: float = 0.5
    
    # Overall score
    overall_score: float = 0.0
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall score (BB-INT-001 Section 9)"""
        self.overall_score = (
            self.leverage_score * 0.20 +
            (1 - self.risk_score) * 0.15 +
            self.feasibility_score * 0.15 +
            self.alignment_score * 0.15 +
            self.compounding_score * 0.15 +
            self.cross_domain_benefit * 0.10 +
            self.reversibility_score * 0.10
        )
        return self.overall_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "option_id": self.option_id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain,
            "actions": self.actions,
            "primary_horizon": self.primary_horizon.value,
            "cross_domain_impact": self.cross_domain_impact,
            "scores": {
                "leverage": self.leverage_score,
                "risk": self.risk_score,
                "feasibility": self.feasibility_score,
                "alignment": self.alignment_score,
                "compounding": self.compounding_score,
                "cross_domain_benefit": self.cross_domain_benefit,
                "reversibility": self.reversibility_score,
            },
            "overall_score": self.overall_score
        }


@dataclass
class ScenarioProjection:
    """
    Projected outcome for a strategy across time horizons (BB-INT-001 Section 5.2)
    """
    option_id: str
    time_horizon: TimeHorizon
    
    # Case types
    best_case: Dict[str, Any] = field(default_factory=dict)
    base_case: Dict[str, Any] = field(default_factory=dict)
    worst_case: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics
    expected_gain: float = 0.0
    expected_risk: float = 0.0
    momentum_effect: float = 0.0  # Positive/negative momentum
    opportunity_cost: float = 0.0
    
    # Domain effects
    domain_effects: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Confidence
    confidence: float = 0.7
    
    # Assumptions
    assumptions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "option_id": self.option_id,
            "time_horizon": self.time_horizon.value,
            "best_case": self.best_case,
            "base_case": self.base_case,
            "worst_case": self.worst_case,
            "expected_gain": self.expected_gain,
            "expected_risk": self.expected_risk,
            "momentum_effect": self.momentum_effect,
            "opportunity_cost": self.opportunity_cost,
            "domain_effects": self.domain_effects,
            "confidence": self.confidence,
            "assumptions": self.assumptions
        }


@dataclass
class StrategicDebatePosition:
    """
    A domain's position in strategic debate (BB-INT-001 Section 5.3)
    """
    domain: str
    chief_officer: str
    
    position: str  # What this domain supports
    rationale: str
    
    concerns: List[str] = field(default_factory=list)
    preferred_actions: List[str] = field(default_factory=list)
    
    # Agreement levels with other domains
    agreements: Dict[str, float] = field(default_factory=dict)  # domain -> agreement (0-1)
    conflicts: Dict[str, str] = field(default_factory=dict)  # domain -> conflict reason
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "chief_officer": self.chief_officer,
            "position": self.position,
            "rationale": self.rationale,
            "concerns": self.concerns,
            "preferred_actions": self.preferred_actions,
            "agreements": self.agreements,
            "conflicts": self.conflicts
        }


@dataclass
class StrategicConflict:
    """
    Identified conflict between domains (BB-INT-001 Section 5.3)
    """
    conflict_id: str
    domains: List[str]
    
    description: str
    strategic_tension: str  # The core tension
    
    resolution_options: List[str] = field(default_factory=list)
    recommended_resolution: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "domains": self.domains,
            "description": self.description,
            "strategic_tension": self.strategic_tension,
            "resolution_options": self.resolution_options,
            "recommended_resolution": self.recommended_resolution
        }


@dataclass
class LeverageOpportunity:
    """
    High-leverage action that produces outsized benefit (BB-INT-001 Section 5.4)
    """
    opportunity_id: str
    title: str
    description: str
    
    # Why it's high leverage
    low_cost: float  # Resource cost (0-1)
    high_benefit: float  # Expected benefit (0-1)
    compounding_effects: List[str] = field(default_factory=list)
    bottleneck_removal: str = ""
    
    # Domains affected
    affected_domains: List[str] = field(default_factory=list)
    
    # Impact scores
    leverage_score: float = 0.0
    confidence: float = 0.7
    
    def calculate_leverage(self) -> float:
        """Calculate leverage as benefit/cost ratio"""
        if self.low_cost > 0:
            self.leverage_score = self.high_benefit / (self.low_cost + 0.1)
        else:
            self.leverage_score = self.high_benefit * 2  # Free action
        return min(1.0, self.leverage_score)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "title": self.title,
            "description": self.description,
            "low_cost": self.low_cost,
            "high_benefit": self.high_benefit,
            "compounding_effects": self.compounding_effects,
            "bottleneck_removal": self.bottleneck_removal,
            "affected_domains": self.affected_domains,
            "leverage_score": self.leverage_score,
            "confidence": self.confidence
        }


@dataclass
class AlignmentEvaluation:
    """
    Evaluation of strategy alignment (BB-INT-001 Section 5.5)
    """
    option_id: str
    
    # Alignment scores
    goal_alignment: float = 0.5  # With user goals
    constraint_alignment: float = 0.5  # With constraints
    life_architecture_alignment: float = 0.5  # With long-term life design
    domain_balance_alignment: float = 0.5  # Maintains domain balance
    
    # Governance
    passes_governor_checks: bool = True
    governor_concerns: List[str] = field(default_factory=list)
    
    # Policy boundaries
    within_policy: bool = True
    policy_notes: List[str] = field(default_factory=list)
    
    # Overall
    alignment_score: float = 0.5
    approved: bool = True
    rejection_reason: StrategyRejectionReason = None
    
    def calculate_overall(self) -> float:
        """Calculate overall alignment"""
        self.alignment_score = (
            self.goal_alignment * 0.25 +
            self.constraint_alignment * 0.20 +
            self.life_architecture_alignment * 0.20 +
            self.domain_balance_alignment * 0.15 +
            (1.0 if self.passes_governor_checks else 0.0) * 0.10 +
            (1.0 if self.within_policy else 0.0) * 0.10
        )
        
        self.approved = (
            self.alignment_score >= 0.4 and
            self.passes_governor_checks and
            self.within_policy
        )
        
        return self.alignment_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "option_id": self.option_id,
            "goal_alignment": self.goal_alignment,
            "constraint_alignment": self.constraint_alignment,
            "life_architecture_alignment": self.life_architecture_alignment,
            "domain_balance_alignment": self.domain_balance_alignment,
            "passes_governor_checks": self.passes_governor_checks,
            "governor_concerns": self.governor_concerns,
            "within_policy": self.within_policy,
            "alignment_score": self.alignment_score,
            "approved": self.approved,
            "rejection_reason": self.rejection_reason.value if self.rejection_reason else None
        }


@dataclass
class StrategicPath:
    """
    A complete strategic path with all evaluations (BB-INT-001 Section 6)
    """
    path_id: str
    name: str
    
    # The strategy
    strategy: StrategicOption
    
    # Projections across horizons
    projections: List[ScenarioProjection] = field(default_factory=list)
    
    # Alignment
    alignment: AlignmentEvaluation = None
    
    # Sequence of actions
    action_sequence: List[Dict[str, Any]] = field(default_factory=list)
    
    # Rankings
    rank: int = 0
    final_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path_id": self.path_id,
            "name": self.name,
            "strategy": self.strategy.to_dict(),
            "projections": [p.to_dict() for p in self.projections],
            "alignment": self.alignment.to_dict() if self.alignment else None,
            "action_sequence": self.action_sequence,
            "rank": self.rank,
            "final_score": self.final_score
        }


@dataclass
class StrategicIntelligenceOutput:
    """
    Final output from the Strategic Intelligence Engine (BB-INT-001 Section 8)
    """
    output_id: str
    timestamp: datetime
    
    # Current posture
    current_posture: StrategicPosture
    posture_rationale: str
    
    # Top tensions
    top_strategic_tensions: List[str] = field(default_factory=list)
    
    # Candidate options
    candidate_options: List[StrategicOption] = field(default_factory=list)
    
    # Projections
    projections_by_horizon: Dict[TimeHorizon, List[ScenarioProjection]] = field(default_factory=dict)
    
    # Leverage
    highest_leverage_opportunities: List[LeverageOpportunity] = field(default_factory=list)
    
    # Debates
    debate_positions: List[StrategicDebatePosition] = field(default_factory=list)
    conflicts: List[StrategicConflict] = field(default_factory=list)
    
    # Final recommendation
    recommended_path: StrategicPath = None
    rejected_paths: List[Dict[str, Any]] = field(default_factory=list)
    
    # Next actions
    recommended_next_actions: List[str] = field(default_factory=list)
    
    # Metadata
    confidence: float = 0.7
    key_assumptions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_id": self.output_id,
            "timestamp": self.timestamp.isoformat(),
            "current_posture": self.current_posture.value,
            "posture_rationale": self.posture_rationale,
            "top_strategic_tensions": self.top_strategic_tensions,
            "candidate_options": [o.to_dict() for o in self.candidate_options],
            "projections": {k.value: [p.to_dict() for p in v] for k, v in self.projections_by_horizon.items()},
            "leverage_opportunities": [l.to_dict() for l in self.highest_leverage_opportunities],
            "debate_positions": [d.to_dict() for d in self.debate_positions],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "recommended_path": self.recommended_path.to_dict() if self.recommended_path else None,
            "rejected_paths": self.rejected_paths,
            "recommended_next_actions": self.recommended_next_actions,
            "confidence": self.confidence,
            "key_assumptions": self.key_assumptions
        }
    
    def format_assessment(self) -> str:
        """Format as readable strategic assessment (BB-INT-001 Section 10)"""
        lines = [
            "=" * 60,
            "STRATEGIC INTELLIGENCE ASSESSMENT",
            f"Date: {self.timestamp.strftime('%Y-%m-%d')}",
            "=" * 60,
            "",
            f"Strategic Posture: {self.current_posture.value.upper()}",
            f"Posture: {self.posture_rationale}",
            "",
            "Top Strategic Tensions:",
            "-" * 40
        ]
        
        for tension in self.top_strategic_tensions:
            lines.append(f"• {tension}")
        
        lines.extend([
            "",
            "Highest Leverage Opportunity:",
            "-" * 40
        ])
        
        if self.highest_leverage_opportunities:
            top = self.highest_leverage_opportunities[0]
            lines.append(f"• {top.title}")
            lines.append(f"  {top.description}")
        
        lines.extend([
            "",
            "Best Strategic Path:",
            "-" * 40
        ])
        
        if self.recommended_path:
            lines.append(f"• {self.recommended_path.name}")
            for action in self.recommended_path.action_sequence[:3]:
                lines.append(f"  {action.get('step', '?')}. {action.get('action', '?')}")
        
        lines.extend([
            "",
            "Rejected Alternatives:",
            "-" * 40
        ])
        
        for rej in self.rejected_paths[:2]:
            lines.append(f"• {rej.get('title', '?')}: {rej.get('reason', '?')}")
        
        lines.extend([
            "",
            f"Confidence: {self.confidence:.0%}",
            "",
            "Key Assumptions:",
            "-" * 40
        ])
        
        for assumption in self.key_assumptions[:3]:
            lines.append(f"• {assumption}")
        
        return "\n".join(lines)


__all__ = [
    # Enums
    "TimeHorizon",
    "StrategicPosture", 
    "ScenarioCase",
    "StrategyRejectionReason",
    
    # Models
    "StrategicOption",
    "ScenarioProjection",
    "StrategicDebatePosition",
    "StrategicConflict",
    "LeverageOpportunity",
    "AlignmentEvaluation",
    "StrategicPath",
    "StrategicIntelligenceOutput",
]
