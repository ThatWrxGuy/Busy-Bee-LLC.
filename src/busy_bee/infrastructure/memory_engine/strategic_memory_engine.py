"""
BB-MEM-001: Strategic Memory Engine

This module establishes long-term experiential intelligence within Busy Bee.

Memory Layers:
- Decision Memory: Records past strategic choices
- Outcome Memory: Tracks strategy results  
- Pattern Memory: Detects recurring signals
- Risk Memory: Stores known failure patterns
- Opportunity Memory: Stores successful leverage points

Extends: BB-INT-001, BB-INT-002A
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

# ============== ENUMS ==============

class MemoryType(Enum):
    """Types of strategic memory"""
    DECISION = "decision"
    OUTCOME = "outcome"
    PATTERN = "pattern"
    RISK = "risk"
    OPPORTUNITY = "opportunity"


class PatternType(Enum):
    """Types of detected patterns"""
    SIGNAL_RECURRENCE = "signal_recurrence"
    CROSS_DOMAIN = "cross_domain"
    TEMPORAL = "temporal"
    BEHAVIORAL = "behavioral"


class OutcomeType(Enum):
    """Strategy outcome types"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    NEUTRAL = "neutral"


# ============== DATA MODELS ==============

@dataclass
class DecisionRecord:
    """Record of a strategic decision"""
    decision_id: str
    timestamp: datetime
    
    # Decision details
    strategy_selected: str
    candidate_strategies: List[str]
    strategic_posture: str
    
    # Context
    domain_context: Dict[str, Any]
    confidence_score: float
    
    # Execution
    execution_status: str = "pending"
    notes: str = ""


@dataclass
class StrategyOutcome:
    """Outcome of a strategy execution"""
    outcome_id: str
    decision_id: str
    timestamp: datetime
    
    # Outcome details
    observed_outcome: str
    expected_outcome: str
    variance: float  # Difference between expected and actual
    success_score: float  # 0-1
    
    # Timing
    duration_days: int = 0
    completed: bool = False
    
    # Analysis
    success_factors: List[str] = field(default_factory=list)
    failure_factors: List[str] = field(default_factory=list)


@dataclass
class PatternRecord:
    """A detected pattern in signals or behavior"""
    pattern_id: str
    pattern_type: PatternType
    
    # Pattern details
    name: str
    description: str
    
    # Detection
    first_seen: datetime
    last_seen: datetime
    frequency: int  # How many times observed
    
    # Confidence
    confidence: float  # 0-1
    
    # Related
    signal_types: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)


@dataclass
class RiskEvent:
    """A known risk or failure pattern"""
    risk_id: str
    timestamp: datetime
    
    # Risk details
    risk_type: str
    description: str
    
    # Trigger
    trigger_signals: List[str] = field(default_factory=list)
    
    # Impact
    impact_score: float = 0.0  # 0-1
    affected_domains: List[str] = field(default_factory=list)
    
    # Resolution
    resolution: str = ""
    recurrence_count: int = 1


@dataclass
class OpportunityEvent:
    """A successful leverage opportunity"""
    opportunity_id: str
    timestamp: datetime
    
    # Opportunity details
    title: str
    description: str
    
    # Trigger
    trigger_signals: List[str] = field(default_factory=list)
    
    # Impact
    leverage_score: float  # 0-1
    impact_score: float = 0.0  # 0-1
    
    # Outcome
    outcome: str = ""
    success: bool = False


@dataclass
class MemoryQuery:
    """Query for retrieving memories"""
    memory_type: MemoryType
    domain: Optional[str] = None
    time_range: Optional[timedelta] = None
    min_confidence: float = 0.0
    limit: int = 10


# ============== DECISION MEMORY ENGINE ==============

class DecisionMemoryEngine:
    """Stores and retrieves strategic decisions"""
    
    def __init__(self):
        self._decisions: Dict[str, DecisionRecord] = {}
        self._counter = 0
    
    def store_decision(self, decision: DecisionRecord) -> str:
        """Store a decision record"""
        self._decisions[decision.decision_id] = decision
        return decision.decision_id
    
    def get_decision(self, decision_id: str) -> Optional[DecisionRecord]:
        """Retrieve a specific decision"""
        return self._decisions.get(decision_id)
    
    def get_recent_decisions(self, days: int = 30, domain: str = None) -> List[DecisionRecord]:
        """Get recent decisions"""
        cutoff = datetime.now() - timedelta(days=days)
        results = []
        
        for d in self._decisions.values():
            if d.timestamp < cutoff:
                continue
            if domain and d.domain_context.get('domain') != domain:
                continue
            results.append(d)
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)
    
    def create_decision(
        self,
        strategy_selected: str,
        candidates: List[str],
        posture: str,
        domain_context: Dict,
        confidence: float
    ) -> DecisionRecord:
        """Create and store a new decision"""
        self._counter += 1
        
        decision = DecisionRecord(
            decision_id=f"dec_{self._counter}",
            timestamp=datetime.now(),
            strategy_selected=strategy_selected,
            candidate_strategies=candidates,
            strategic_posture=posture,
            domain_context=domain_context,
            confidence_score=confidence
        )
        
        self.store_decision(decision)
        return decision


# ============== OUTCOME MEMORY ENGINE ==============

class OutcomeMemoryEngine:
    """Tracks strategy execution outcomes"""
    
    def __init__(self):
        self._outcomes: Dict[str, StrategyOutcome] = {}
        self._counter = 0
    
    def store_outcome(self, outcome: StrategyOutcome) -> str:
        """Store an outcome record"""
        self._outcomes[outcome.outcome_id] = outcome
        return outcome.outcome_id
    
    def get_outcome(self, outcome_id: str) -> Optional[StrategyOutcome]:
        """Retrieve a specific outcome"""
        return self._outcomes.get(outcome_id)
    
    def get_outcomes_for_decision(self, decision_id: str) -> List[StrategyOutcome]:
        """Get all outcomes for a decision"""
        return [o for o in self._outcomes.values() if o.decision_id == decision_id]
    
    def get_recent_outcomes(self, days: int = 90) -> List[StrategyOutcome]:
        """Get recent outcomes"""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            o for o in self._outcomes.values()
            if o.timestamp >= cutoff
        ]
    
    def calculate_success_rate(self, domain: str = None) -> float:
        """Calculate overall success rate"""
        outcomes = self.get_recent_outcomes()
        
        if domain:
            outcomes = [o for o in outcomes if o.observed_outcome.get('domain') == domain]
        
        if not outcomes:
            return 0.5  # Default neutral
        
        total = sum(o.success_score for o in outcomes) / len(outcomes)
        return total
    
    def create_outcome(
        self,
        decision_id: str,
        expected: str,
        observed: str,
        variance: float,
        success: float
    ) -> StrategyOutcome:
        """Create and store a new outcome"""
        self._counter += 1
        
        outcome = StrategyOutcome(
            outcome_id=f"out_{self._counter}",
            decision_id=decision_id,
            timestamp=datetime.now(),
            expected_outcome=expected,
            observed_outcome=observed,
            variance=variance,
            success_score=success,
            completed=True
        )
        
        self.store_outcome(outcome)
        return outcome


# ============== PATTERN MEMORY ENGINE ==============

class PatternMemoryEngine:
    """Detects and stores recurring patterns"""
    
    def __init__(self):
        self._patterns: Dict[str, PatternRecord] = {}
        self._counter = 0
    
    def detect_pattern(
        self,
        pattern_type: PatternType,
        name: str,
        signals: List[str],
        domains: List[str],
        confidence: float
    ) -> PatternRecord:
        """Detect and store a new pattern"""
        
        # Check if pattern already exists
        existing = self._find_matching_pattern(signals, domains)
        
        if existing:
            # Update existing pattern
            existing.frequency += 1
            existing.last_seen = datetime.now()
            return existing
        
        # Create new pattern
        self._counter += 1
        
        pattern = PatternRecord(
            pattern_id=f"pat_{self._counter}",
            pattern_type=pattern_type,
            name=name,
            description=f"Pattern: {name}",
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            frequency=1,
            confidence=confidence,
            signal_types=signals,
            domains=domains
        )
        
        self._patterns[pattern.pattern_id] = pattern
        return pattern
    
    def _find_matching_pattern(self, signals: List[str], domains: List[str]) -> Optional[PatternRecord]:
        """Find existing matching pattern"""
        for p in self._patterns.values():
            # Check signal overlap
            signal_match = len(set(p.signal_types) & set(signals)) > 0
            domain_match = len(set(p.domains) & set(domains)) > 0
            
            if signal_match and domain_match:
                return p
        
        return None
    
    def get_patterns(self, pattern_type: PatternType = None, min_confidence: float = 0.0) -> List[PatternRecord]:
        """Get patterns matching criteria"""
        results = []
        
        for p in self._patterns.values():
            if pattern_type and p.pattern_type != pattern_type:
                continue
            if p.confidence < min_confidence:
                continue
            results.append(p)
        
        return sorted(results, key=lambda x: x.confidence, reverse=True)
    
    def get_recurring_signals(self, domain: str = None) -> List[str]:
        """Get signals that recur frequently"""
        signal_counts = defaultdict(int)
        
        for p in self._patterns.values():
            if domain and domain not in p.domains:
                continue
            
            for signal in p.signal_types:
                signal_counts[signal] += p.frequency
        
        # Return top recurring signals
        sorted_signals = sorted(signal_counts.items(), key=lambda x: x[1], reverse=True)
        return [s[0] for s in sorted_signals[:10]]


# ============== RISK MEMORY ENGINE ==============

class RiskMemoryEngine:
    """Stores known failure patterns and risks"""
    
    def __init__(self):
        self._risks: Dict[str, RiskEvent] = {}
        self._counter = 0
    
    def store_risk(self, risk: RiskEvent) -> str:
        """Store a risk event"""
        self._risks[risk.risk_id] = risk
        return risk.risk_id
    
    def get_risks(self, domain: str = None) -> List[RiskEvent]:
        """Get risks, optionally filtered by domain"""
        results = []
        
        for r in self._risks.values():
            if domain and domain not in r.affected_domains:
                continue
            results.append(r)
        
        return sorted(results, key=lambda x: x.impact_score, reverse=True)
    
    def check_risk_recognition(self, signals: List[str]) -> List[RiskEvent]:
        """Check if current signals match known risks"""
        matched = []
        
        for r in self._risks.values():
            # Check signal overlap
            if set(r.trigger_signals) & set(signals):
                matched.append(r)
        
        return matched
    
    def create_risk(
        self,
        risk_type: str,
        description: str,
        triggers: List[str],
        impact: float,
        domains: List[str]
    ) -> RiskEvent:
        """Create and store a new risk"""
        
        # Check if risk already exists
        for r in self._risks.values():
            if set(r.trigger_signals) == set(triggers):
                r.recurrence_count += 1
                return r
        
        self._counter += 1
        
        risk = RiskEvent(
            risk_id=f"risk_{self._counter}",
            timestamp=datetime.now(),
            risk_type=risk_type,
            description=description,
            trigger_signals=triggers,
            impact_score=impact,
            affected_domains=domains
        )
        
        self.store_risk(risk)
        return risk


# ============== OPPORTUNITY MEMORY ENGINE ==============

class OpportunityMemoryEngine:
    """Stores successful leverage opportunities"""
    
    def __init__(self):
        self._opportunities: Dict[str, OpportunityEvent] = {}
        self._counter = 0
    
    def store_opportunity(self, opp: OpportunityEvent) -> str:
        """Store an opportunity"""
        self._opportunities[opp.opportunity_id] = opp
        return opp.opportunity_id
    
    def get_opportunities(self, min_leverage: float = 0.0) -> List[OpportunityEvent]:
        """Get opportunities above leverage threshold"""
        return [
            o for o in self._opportunities.values()
            if o.leverage_score >= min_leverage
        ]
    
    def get_successful_opportunities(self, domain: str = None) -> List[OpportunityEvent]:
        """Get opportunities that succeeded"""
        results = []
        
        for o in self._opportunities.values():
            if not o.success:
                continue
            if domain and domain not in o.trigger_signals:
                continue
            results.append(o)
        
        return sorted(results, key=lambda x: x.leverage_score, reverse=True)
    
    def create_opportunity(
        self,
        title: str,
        triggers: List[str],
        leverage: float,
        impact: float
    ) -> OpportunityEvent:
        """Create and store a new opportunity"""
        self._counter += 1
        
        opp = OpportunityEvent(
            opportunity_id=f"opp_{self._counter}",
            timestamp=datetime.now(),
            title=title,
            description=title,
            trigger_signals=triggers,
            leverage_score=leverage,
            impact_score=impact
        )
        
        self.store_opportunity(opp)
        return opp


# ============== MAIN STRATEGIC MEMORY SERVICE ==============

class StrategicMemoryService:
    """
    BB-MEM-001: Strategic Memory Engine
    
    Coordinates all memory layers and provides unified interface.
    """
    
    def __init__(self):
        # Initialize all memory engines
        self.decisions = DecisionMemoryEngine()
        self.outcomes = OutcomeMemoryEngine()
        self.patterns = PatternMemoryEngine()
        self.risks = RiskMemoryEngine()
        self.opportunities = OpportunityMemoryEngine()
    
    # --- Decision Operations ---
    
    def record_decision(
        self,
        strategy: str,
        candidates: List[str],
        posture: str,
        context: Dict,
        confidence: float
    ) -> DecisionRecord:
        """Record a strategic decision"""
        return self.decisions.create_decision(
            strategy_selected=strategy,
            candidates=candidates,
            posture=posture,
            domain_context=context,
            confidence=confidence
        )
    
    def get_decision_history(self, days: int = 30) -> List[DecisionRecord]:
        """Get recent decision history"""
        return self.decisions.get_recent_decisions(days)
    
    # --- Outcome Operations ---
    
    def record_outcome(
        self,
        decision_id: str,
        expected: str,
        observed: str,
        success_score: float
    ) -> StrategyOutcome:
        """Record a strategy outcome"""
        variance = abs(success_score - 0.5) * 2  # 0-1 scale
        
        return self.outcomes.create_outcome(
            decision_id=decision_id,
            expected=expected,
            observed=observed,
            variance=variance,
            success=success_score
        )
    
    def get_success_rate(self, domain: str = None) -> float:
        """Calculate strategy success rate"""
        return self.outcomes.calculate_success_rate(domain)
    
    # --- Pattern Operations ---
    
    def detect_and_store_pattern(
        self,
        pattern_type: PatternType,
        name: str,
        signals: List[str],
        domains: List[str],
        confidence: float
    ) -> PatternRecord:
        """Detect and store a pattern"""
        return self.patterns.detect_pattern(pattern_type, name, signals, domains, confidence)
    
    def get_patterns(self, pattern_type: PatternType = None) -> List[PatternRecord]:
        """Get detected patterns"""
        return self.patterns.get_patterns(pattern_type)
    
    # --- Risk Operations ---
    
    def check_active_risks(self, signals: List[str]) -> List[RiskEvent]:
        """Check for recognized risks in current signals"""
        return self.risks.check_risk_recognition(signals)
    
    def get_known_risks(self, domain: str = None) -> List[RiskEvent]:
        """Get known risks"""
        return self.risks.get_risks(domain)
    
    # --- Opportunity Operations ---
    
    def get_high_leverage_opportunities(self, min_leverage: float = 0.7) -> List[OpportunityEvent]:
        """Get historically successful opportunities"""
        return self.opportunities.get_successful_opportunities()
    
    # --- Memory Analysis ---
    
    def analyze_strategic_memory(self) -> Dict[str, Any]:
        """Generate memory analysis report"""
        
        # Decision stats
        recent_decisions = self.decisions.get_recent_decisions(30)
        
        # Outcome stats
        success_rate = self.outcomes.calculate_success_rate()
        recent_outcomes = self.outcomes.get_recent_outcomes(90)
        
        # Pattern stats
        patterns = self.patterns.get_patterns()
        
        # Risk stats
        risks = self.risks.get_risks()
        
        # Opportunity stats
        opportunities = self.opportunities.get_successful_opportunities()
        
        return {
            "decision_count_30d": len(recent_decisions),
            "success_rate": success_rate,
            "outcomes_90d": len(recent_outcomes),
            "patterns_detected": len(patterns),
            "known_risks": len(risks),
            "successful_opportunities": len(opportunities),
            "timestamp": datetime.now().isoformat()
        }


__all__ = [
    "MemoryType",
    "PatternType", 
    "OutcomeType",
    "DecisionRecord",
    "StrategyOutcome",
    "PatternRecord",
    "RiskEvent",
    "OpportunityEvent",
    "MemoryQuery",
    "DecisionMemoryEngine",
    "OutcomeMemoryEngine",
    "PatternMemoryEngine",
    "RiskMemoryEngine",
    "OpportunityMemoryEngine",
    "StrategicMemoryService",
]
