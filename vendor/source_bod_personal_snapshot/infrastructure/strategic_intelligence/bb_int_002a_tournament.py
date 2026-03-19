"""
BB-INT-002A: Advanced Strategy Tournament & Stress Testing Doctrine

This module extends the Strategy Tournament Engine with:
- Multi-stage tournament evaluation
- Scenario stress testing
- Round-robin competition
- Fragility and regret analysis
- Financial strategy variation tournaments
- Championship selection

Extends: BB-INT-001, BB-INT-002
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random

# ============== ENUMS ==============

class TournamentStage(Enum):
    """Tournament stages"""
    GENERATION = "generation"
    QUALIFICATION = "qualification"
    STRESS_TEST = "stress_test"
    ROUND_ROBIN = "round_robin"
    PORTFOLIO_FIT = "portfolio_fit"
    CHAMPIONSHIP = "championship"
    COMPLETE = "complete"


class StrategyArchetype(Enum):
    """Strategy classification archetypes"""
    STABILIZE = "stabilize"
    OPTIMIZE = "optimize"
    EXPAND = "expand"
    DEFEND = "defend"
    TRANSITION = "transition"


class StressScenario(Enum):
    """Stress testing scenarios"""
    BASELINE = "baseline"
    ADVERSE = "adverse"
    FAVORABLE = "favorable"
    VOLATILITY = "volatility"
    LOW_RESOURCE = "low_resource"


@dataclass
class EvaluationDimension:
    """Scoring dimension"""
    name: str
    score: float
    weight: float
    
    def weighted_score(self) -> float:
        return self.score * self.weight


@dataclass
class StressResult:
    """Result of stress testing"""
    scenario: StressScenario
    baseline_score: float
    stressed_score: float
    resilience: float  # How well it held up
    fragility: float   # How easily it broke
    assumptions_affected: List[str] = field(default_factory=list)


@dataclass
class TournamentCandidate:
    """A strategy in the tournament"""
    strategy_id: str
    title: str
    archetype: StrategyArchetype
    
    # Evaluation scores
    impact_score: float = 0.0
    risk_score: float = 0.0
    leverage_score: float = 0.0
    alignment_score: float = 0.0
    feasibility_score: float = 0.0
    robustness_score: float = 0.0
    optionality_score: float = 0.0
    execution_burden_score: float = 0.0
    
    # Analysis
    stress_results: List[StressResult] = field(default_factory=list)
    fragility_analysis: Dict[str, float] = field(default_factory=dict)
    regret_analysis: Dict[str, float] = field(default_factory=dict)
    
    # Tournament
    round_robin_wins: int = 0
    round_robin_losses: int = 0
    tournament_score: float = 0.0
    eliminated: bool = False
    elimination_reason: str = ""
    
    def total_score(self) -> float:
        weights = {
            'impact': 0.25,
            'risk': 0.20,
            'leverage': 0.15,
            'alignment': 0.10,
            'feasibility': 0.10,
            'robustness': 0.10,
            'optionality': 0.05,
            'execution': 0.05
        }
        return (
            self.impact_score * weights['impact'] +
            (1 - self.risk_score) * weights['risk'] +
            self.leverage_score * weights['leverage'] +
            self.alignment_score * weights['alignment'] +
            self.feasibility_score * weights['feasibility'] +
            self.robustness_score * weights['robustness'] +
            self.optionality_score * weights['optionality'] +
            (1 - self.execution_burden_score) * weights['execution']
        )


@dataclass
class FinancialVariation:
    """A financial strategy variation"""
    variation_id: str
    title: str
    description: str
    
    # Variation specific
    allocation_strategy: str = ""
    risk_level: str = "moderate"
    expected_return: float = 0.0
    volatility: float = 0.0
    diversification_score: float = 0.5
    
    # Mini-tournament results
    mini_tournament_score: float = 0.0
    is_champion: bool = False


@dataclass
class TournamentResult:
    """Final tournament result"""
    tournament_id: str
    timestamp: datetime
    
    # Winners
    primary_strategy: TournamentCandidate = None
    runner_up_strategy: TournamentCandidate = None
    challenger_strategy: TournamentCandidate = None
    
    # Financial variations (if applicable)
    financial_variations: List[FinancialVariation] = field(default_factory=list)
    financial_champion: FinancialVariation = None
    
    # Analysis
    eliminated_candidates: List[TournamentCandidate] = field(default_factory=list)
    key_tradeoffs: List[str] = field(default_factory=list)
    fragility_summary: Dict[str, Any] = field(default_factory=dict)
    regret_summary: Dict[str, Any] = field(default_factory=list)
    
    # Metadata
    total_candidates: int = 0
    rounds_conducted: int = 0
    confidence_score: float = 0.0
    assumptions: List[str] = field(default_factory=list)
    trigger_conditions: List[str] = field(default_factory=list)


# ============== QUALIFICATION GATE ==============

class QualificationGate:
    """Stage 1: Validate strategies before tournament"""
    
    def __init__(self):
        self.min_confidence = 0.4
        self.min_leverage = 0.3
        self.min_feasibility = 0.4
    
    def validate(self, candidate: TournamentCandidate) -> tuple:
        """
        Returns: (passed: bool, reason: str)
        """
        # Check confidence
        if candidate.robustness_score < self.min_confidence:
            return False, "Confidence below threshold"
        
        # Check leverage
        if candidate.leverage_score < self.min_leverage:
            return False, "Leverage below threshold"
        
        # Check feasibility
        if candidate.feasibility_score < self.min_feasibility:
            return False, "Feasibility below threshold"
        
        # Check too risky
        if candidate.risk_score > 0.85:
            return False, "Risk too high"
        
        return True, "Passed"


# ============== STRESS TESTING ENGINE ==============

class StressTestingEngine:
    """Stage 2: Test strategies under multiple scenarios"""
    
    def stress_test(self, candidate: TournamentCandidate) -> List[StressResult]:
        """Run stress tests on a candidate"""
        results = []
        
        scenarios = [
            StressScenario.BASELINE,
            StressScenario.ADVERSE,
            StressScenario.FAVORABLE,
            StressScenario.VOLATILITY,
            StressScenario.LOW_RESOURCE
        ]
        
        base_score = candidate.total_score()
        
        for scenario in scenarios:
            result = self._run_scenario(candidate, scenario, base_score)
            results.append(result)
        
        return results
    
    def _run_scenario(self, candidate: TournamentCandidate, scenario: StressScenario, base: float) -> StressResult:
        """Run a single stress scenario"""
        
        # Scenario multipliers
        multipliers = {
            StressScenario.BASELINE: 1.0,
            StressScenario.ADVERSE: 0.7,
            StressScenario.FAVORABLE: 1.2,
            StressScenario.VOLATILITY: 0.85,
            StressScenario.LOW_RESOURCE: 0.6
        }
        
        mult = multipliers.get(scenario, 1.0)
        stressed = base * mult
        
        # Calculate resilience (how well it held up)
        resilience = stressed / base if base > 0 else 0
        
        # Calculate fragility (inverse of resilience, capped)
        fragility = max(0, 1 - resilience)
        
        # Identify affected assumptions
        assumptions = []
        if scenario == StressScenario.ADVERSE:
            assumptions.append("Conditions remain stable")
        elif scenario == StressScenario.VOLATILITY:
            assumptions.append("No major disruptions")
        elif scenario == StressScenario.LOW_RESOURCE:
            assumptions.append("Sufficient resources available")
        
        return StressResult(
            scenario=scenario,
            baseline_score=base,
            stressed_score=stressed,
            resilience=resilience,
            fragility=fragility,
            assumptions_affected=assumptions
        )


# ============== ROUND ROBIN TOURNAMENT ==============

class RoundRobinEngine:
    """Stage 3: Strategies compete in round-robin"""
    
    def run_round_robin(self, candidates: List[TournamentCandidate]) -> List[TournamentCandidate]:
        """Run round-robin tournament"""
        
        # Each candidate vs every other candidate
        for i, c1 in enumerate(candidates):
            for j, c2 in enumerate(candidates):
                if i >= j:
                    continue
                
                winner = self._compare(c1, c2)
                
                if winner == c1:
                    c1.round_robin_wins += 1
                    c2.round_robin_losses += 1
                else:
                    c2.round_robin_wins += 1
                    c1.round_robin_losses += 1
        
        # Calculate tournament score
        for c in candidates:
            c.tournament_score = (
                c.total_score() * 0.6 +
                (c.round_robin_wins / max(1, c.round_robin_wins + c.round_robin_losses)) * 0.4
            ) if (c.round_robin_wins + c.round_robin_losses) > 0 else c.total_score()
        
        # Sort by tournament score
        candidates.sort(key=lambda x: x.tournament_score, reverse=True)
        
        return candidates
    
    def _compare(self, c1: TournamentCandidate, c2: TournamentCandidate) -> TournamentCandidate:
        """Compare two candidates"""
        # Primary: total score
        if abs(c1.total_score() - c2.total_score()) > 0.05:
            return c1 if c1.total_score() > c2.total_score() else c2
        
        # Tie-breaker: robustness
        if abs(c1.robustness_score - c2.robustness_score) > 0.1:
            return c1 if c1.robustness_score > c2.robustness_score else c2
        
        # Tie-breaker: lower risk
        return c1 if c1.risk_score < c2.risk_score else c2


# ============== PORTFOLIO FIT EVALUATOR ==============

class PortfolioFitEvaluator:
    """Stage 4: Evaluate strategy fit within life system"""
    
    def evaluate_fit(self, candidate: TournamentCandidate, active_priorities: List[str]) -> float:
        """Evaluate how well strategy fits with existing priorities"""
        
        # Check conflicts
        conflict_penalty = 0.0
        
        # Simulated conflict detection
        if candidate.archetype == StrategyArchetype.EXPAND and len(active_priorities) >= 3:
            conflict_penalty = 0.15
        
        # Execution capacity check
        if candidate.execution_burden_score > 0.7:
            conflict_penalty += 0.1
        
        # Base fit score minus penalties
        fit_score = 0.8 - conflict_penalty
        
        return max(0.0, fit_score)


# ============== FINANCIAL VARIATION ENGINE ==============

class FinancialVariationEngine:
    """Stage 9: Generate and evaluate financial strategy variations"""
    
    def generate_variations(self, primary_strategy: str) -> List[FinancialVariation]:
        """Generate 3 variations of a financial strategy"""
        
        variations = []
        
        # Variation A: Conservative
        variations.append(FinancialVariation(
            variation_id="var_a",
            title=f"Conservative: {primary_strategy}",
            description="Lower exposure, reduced risk approach",
            allocation_strategy="conservative",
            risk_level="low",
            expected_return=0.05,
            volatility=0.08,
            diversification_score=0.9
        ))
        
        # Variation B: Balanced
        variations.append(FinancialVariation(
            variation_id="var_b",
            title=f"Balanced: {primary_strategy}",
            description="Moderate exposure with diversification",
            allocation_strategy="balanced",
            risk_level="moderate",
            expected_return=0.10,
            volatility=0.15,
            diversification_score=0.7
        ))
        
        # Variation C: Aggressive
        variations.append(FinancialVariation(
            variation_id="var_c",
            title=f"Aggressive: {primary_strategy}",
            description="Higher exposure targeting maximum upside",
            allocation_strategy="aggressive",
            risk_level="high",
            expected_return=0.18,
            volatility=0.28,
            diversification_score=0.4
        ))
        
        return variations
    
    def run_mini_tournament(self, variations: List[FinancialVariation]) -> FinancialVariation:
        """Run mini-tournament on variations"""
        
        # Score each variation
        for var in variations:
            # Financial scoring formula
            score = (
                var.expected_return * 0.35 +
                (1 - var.volatility) * 0.25 +
                var.diversification_score * 0.20 +
                (1.0 if var.risk_level == "moderate" else 0.7) * 0.20
            )
            var.mini_tournament_score = score
        
        # Sort and mark champion
        variations.sort(key=lambda x: x.mini_tournament_score, reverse=True)
        
        for i, var in enumerate(variations):
            var.is_champion = (i == 0)
        
        return variations[0]


# ============== MAIN TOURNAMENT ENGINE ==============

class AdvancedTournamentEngine:
    """
    BB-INT-002A: Advanced Strategy Tournament & Stress Testing
    
    Multi-stage tournament with:
    - Qualification Gate
    - Scenario Stress Testing
    - Round Robin Competition
    - Portfolio Fit Evaluation
    - Championship Round
    - Financial Variation Tournament
    """
    
    def __init__(self):
        self.gate = QualificationGate()
        self.stress_test = StressTestingEngine()
        self.round_robin = RoundRobinEngine()
        self.portfolio_fit = PortfolioFitEvaluator()
        self.financial_variations = FinancialVariationEngine()
        self._counter = 0
    
    def run_tournament(
        self,
        strategies: List[Dict],
        active_priorities: List[str] = None,
        is_financial: bool = False
    ) -> TournamentResult:
        """
        Run full advanced tournament on strategies
        """
        
        self._counter += 1
        active_priorities = active_priorities or []
        
        # Convert to candidates
        candidates = self._create_candidates(strategies)
        
        # Stage 1: Qualification Gate
        qualified = []
        eliminated = []
        for c in candidates:
            passed, reason = self.gate.validate(c)
            if passed:
                qualified.append(c)
            else:
                c.eliminated = True
                c.elimination_reason = reason
                eliminated.append(c)
        
        candidates = qualified
        
        # Stage 2: Stress Testing
        for c in candidates:
            c.stress_results = self.stress_test.stress_test(c)
            # Calculate fragility
            avg_fragility = sum(r.fragility for r in c.stress_results) / len(c.stress_results)
            c.fragility_analysis = {
                'average_fragility': avg_fragility,
                'most_stressed': min(c.stress_results, key=lambda x: x.resilience).scenario.value
            }
        
        # Stage 3: Round Robin
        if len(candidates) > 1:
            candidates = self.round_robin.run_round_robin(candidates)
        
        # Stage 4: Portfolio Fit
        for c in candidates:
            fit_score = self.portfolio_fit.evaluate_fit(c, active_priorities)
            c.tournament_score *= fit_score
        
        # Re-sort after fit evaluation
        candidates.sort(key=lambda x: x.tournament_score, reverse=True)
        
        # Stage 5: Championship - select top 3
        primary = candidates[0] if len(candidates) > 0 else None
        runner_up = candidates[1] if len(candidates) > 1 else None
        challenger = candidates[2] if len(candidates) > 2 else None
        
        # Financial variations if applicable
        financial_champion = None
        financial_vars = []
        
        if is_financial and primary:
            financial_vars = self.financial_variations.generate_variations(primary.title)
            financial_champion = self.financial_variations.run_mini_tournament(financial_vars)
        
        # Build result
        result = TournamentResult(
            tournament_id=f"tournament_{self._counter}",
            timestamp=datetime.now(),
            primary_strategy=primary,
            runner_up_strategy=runner_up,
            challenger_strategy=challenger,
            financial_variations=financial_vars,
            financial_champion=financial_champion,
            eliminated_candidates=eliminated,
            total_candidates=len(strategies),
            rounds_conducted=4,
            confidence_score=0.75,
            assumptions=["Strategies represent true options", "Scenarios are reasonable"],
            trigger_conditions=["Major life change", "Domain crisis", "Opportunity significant shift"]
        )
        
        # Add tradeoffs
        result.key_tradeoffs = self._extract_tradeoffs(candidates)
        
        return result
    
    def _create_candidates(self, strategies: List[Dict]) -> List[TournamentCandidate]:
        """Convert strategy dicts to tournament candidates"""
        
        candidates = []
        
        archetype_map = {
            'stabilize': StrategyArchetype.STABILIZE,
            'optimize': StrategyArchetype.OPTIMIZE,
            'expand': StrategyArchetype.EXPAND,
            'defend': StrategyArchetype.DEFEND,
            'transition': StrategyArchetype.TRANSITION
        }
        
        for i, s in enumerate(strategies):
            archetype = archetype_map.get(
                s.get('domain', 'optimize').lower(),
                StrategyArchetype.OPTIMIZE
            )
            
            # Infer archetype from title
            title_lower = s.get('title', '').lower()
            if 'stabilize' in title_lower or 'reduce' in title_lower:
                archetype = StrategyArchetype.STABILIZE
            elif 'expand' in title_lower or 'increase' in title_lower:
                archetype = StrategyArchetype.EXPAND
            elif 'mitigate' in title_lower or 'protect' in title_lower:
                archetype = StrategyArchetype.DEFEND
            
            c = TournamentCandidate(
                strategy_id=f"candidate_{i}",
                title=s.get('title', f'Strategy {i}'),
                archetype=archetype,
                impact_score=s.get('impact', 70.0),
                risk_score=s.get('risk', 0.3),
                leverage_score=s.get('leverage', 60.0),
                alignment_score=s.get('alignment', 70.0),
                feasibility_score=s.get('feasibility', 0.7),
                robustness_score=s.get('confidence', 0.7),
                optionality_score=s.get('optionality', 0.5),
                execution_burden_score=s.get('burden', 0.4)
            )
            
            candidates.append(c)
        
        return candidates
    
    def _extract_tradeoffs(self, candidates: List[TournamentCandidate]) -> List[str]:
        """Extract key tradeoffs from tournament"""
        
        tradeoffs = []
        
        if len(candidates) >= 2:
            c1 = candidates[0]
            c2 = candidates[1]
            
            # Compare dimensions
            if c1.impact_score > c2.impact_score + 10:
                tradeoffs.append(f"{c1.title} has higher impact but may have higher risk")
            
            if c1.robustness_score < c2.robustness_score:
                tradeoffs.append(f"{c2.title} is more robust across scenarios")
            
            if c1.execution_burden_score > c2.execution_burden_score + 0.2:
                tradeoffs.append(f"{c1.title} requires more execution effort")
        
        return tradeoffs
    
    def format_tournament_report(self, result: TournamentResult) -> str:
        """Format tournament as readable report"""
        
        lines = [
            "=" * 60,
            "STRATEGY TOURNAMENT REPORT",
            f"Date: {result.timestamp.strftime('%Y-%m-%d')}",
            "=" * 60,
            "",
            "CHAMPIONSHIP RESULTS",
            "-" * 40,
            f"PRIMARY: {result.primary_strategy.title if result.primary_strategy else 'None'}",
            f"  Score: {result.primary_strategy.tournament_score:.2f}" if result.primary_strategy else "",
            "",
            f"RUNNER-UP: {result.runner_up_strategy.title if result.runner_up_strategy else 'None'}",
            f"CHALLENGER: {result.challenger_strategy.title if result.challenger_strategy else 'None'}",
            "",
            "KEY TRADEOFFS",
            "-" * 40
        ]
        
        for t in result.key_tradeoffs:
            lines.append(f"• {t}")
        
        if result.financial_champion:
            lines.extend([
                "",
                "FINANCIAL VARIATION CHAMPION",
                "-" * 40,
                f"{result.financial_champion.title}",
                f"Strategy: {result.financial_champion.allocation_strategy}"
            ])
        
        lines.extend([
            "",
            f"Confidence: {result.confidence_score:.0%}",
            "",
            "=" * 60
        ])
        
        return "\n".join(lines)


__all__ = [
    "TournamentStage",
    "StrategyArchetype",
    "StressScenario",
    "EvaluationDimension",
    "StressResult",
    "TournamentCandidate",
    "FinancialVariation",
    "TournamentResult",
    "QualificationGate",
    "StressTestingEngine",
    "RoundRobinEngine",
    "PortfolioFitEvaluator",
    "FinancialVariationEngine",
    "AdvancedTournamentEngine",
]
