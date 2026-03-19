"""
Strategic Intelligence Engines - BB-INT-001

Contains:
- Strategy Generation Engine
- Scenario Simulation Engine
- Strategic Debate Engine
- Leverage Discovery Engine
- Alignment Engine
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import random

from .strategy_models import (
    StrategicOption, ScenarioProjection, StrategicDebatePosition,
    StrategicConflict, LeverageOpportunity, AlignmentEvaluation,
    StrategicPath, StrategicIntelligenceOutput, StrategicPosture,
    TimeHorizon, ScenarioCase, StrategyRejectionReason
)
from ..reporting import DomainIntelligenceReport, GovernorAlert


# ============== STRATEGY GENERATION ENGINE ==============

class StrategyGenerationEngine:
    """
    Generates candidate strategies from domain intelligence (BB-INT-001 Section 6.2)
    """
    
    def __init__(self):
        self._counter = 0
    
    def generate_strategies(
        self,
        domain_reports: List[DomainIntelligenceReport],
        risks: List[str],
        opportunities: List[str],
        goals: List[str] = None,
        constraints: List[str] = None
    ) -> List[StrategicOption]:
        """Generate candidate strategic options"""
        
        strategies = []
        goals = goals or []
        constraints = constraints or []
        
        # Generate from domain reports
        for report in domain_reports:
            # Generate based on domain state
            if report.top_opportunities:
                strategies.extend(self._generate_from_opportunities(report))
            
            if report.top_risks:
                strategies.extend(self._generate_from_risks(report))
        
        # Generate cross-domain strategies
        if len(domain_reports) >= 2:
            strategies.extend(self._generate_cross_domain(domain_reports))
        
        # If no strategies, generate defaults
        if not strategies:
            strategies.extend(self._generate_defaults(domain_reports))
        
        return strategies
    
    def _generate_from_opportunities(self, report: DomainIntelligenceReport) -> List[StrategicOption]:
        """Generate strategies from domain opportunities"""
        strategies = []
        
        for i, opp in enumerate(report.top_opportunities[:2]):
            self._counter += 1
            
            strategy = StrategicOption(
                option_id=f"strat_{self._counter}",
                title=f"Capitalize on: {opp}",
                description=f"Focus resources on {opp} in {report.domain}",
                domain=report.domain,
                actions=[f"Pursue {opp}"],
                primary_horizon=TimeHorizon.NEAR_TERM,
                cross_domain_impact={report.domain: "positive"}
            )
            
            # Set baseline scores
            strategy.leverage_score = 0.7
            strategy.risk_score = 0.3
            strategy.feasibility_score = 0.7
            strategy.alignment_score = 0.7
            strategy.compounding_score = 0.6
            strategy.cross_domain_benefit = 0.4
            strategy.calculate_overall_score()
            
            strategies.append(strategy)
        
        return strategies
    
    def _generate_from_risks(self, report: DomainIntelligenceReport) -> List[StrategicOption]:
        """Generate strategies to address risks"""
        strategies = []
        
        for i, risk in enumerate(report.top_risks[:2]):
            self._counter += 1
            
            strategy = StrategicOption(
                option_id=f"strat_{self._counter}",
                title=f"Mitigate: {risk}",
                description=f"Address the risk of {risk} in {report.domain}",
                domain=report.domain,
                actions=[f"Mitigate {risk}"],
                primary_horizon=TimeHorizon.IMMEDIATE,
                cross_domain_impact={report.domain: "risk_reduction"}
            )
            
            strategy.leverage_score = 0.5
            strategy.risk_score = 0.8  # Risk mitigation
            strategy.feasibility_score = 0.6
            strategy.alignment_score = 0.8
            strategy.compounding_score = 0.5
            strategy.cross_domain_benefit = 0.3
            strategy.reversibility_score = 0.7
            strategy.calculate_overall_score()
            
            strategies.append(strategy)
        
        return strategies
    
    def _generate_cross_domain(self, reports: List[DomainIntelligenceReport]) -> List[StrategicOption]:
        """Generate cross-domain strategies"""
        strategies = []
        
        # Find common themes
        all_opps = []
        for r in reports:
            all_opps.extend(r.top_opportunities)
        
        if len(all_opps) >= 2:
            self._counter += 1
            
            strategy = StrategicOption(
                option_id=f"strat_{self._counter}",
                title="Multi-domain optimization",
                description="Coordinate actions across domains for compound benefit",
                domain="cross_domain",
                actions=["Align domain strategies", "Create synergies"],
                primary_horizon=TimeHorizon.MID_TERM,
                cross_domain_impact={r.domain: "positive" for r in reports}
            )
            
            strategy.leverage_score = 0.85
            strategy.risk_score = 0.25
            strategy.feasibility_score = 0.5
            strategy.alignment_score = 0.8
            strategy.compounding_score = 0.9
            strategy.cross_domain_benefit = 0.9
            strategy.calculate_overall_score()
            
            strategies.append(strategy)
        
        return strategies
    
    def _generate_defaults(self, reports: List[DomainIntelligenceReport]) -> List[StrategicOption]:
        """Generate default strategies if nothing else"""
        strategies = []
        
        # Stabilize strategy
        self._counter += 1
        stable = StrategicOption(
            option_id=f"strat_{self._counter}",
            title="Stabilize current position",
            description="Focus on maintaining stability before advancing",
            domain="all",
            actions=["Maintain current course", "Monitor metrics"],
            primary_horizon=TimeHorizon.IMMEDIATE
        )
        stable.leverage_score = 0.4
        stable.risk_score = 0.2
        stable.feasibility_score = 0.9
        stable.alignment_score = 0.8
        stable.calculate_overall_score()
        strategies.append(stable)
        
        return strategies


# ============== SCENARIO SIMULATION ENGINE ==============

class ScenarioSimulationEngine:
    """
    Projects outcomes for strategies across time horizons (BB-INT-001 Section 6.3)
    """
    
    def simulate(
        self,
        strategy: StrategicOption,
        domain_reports: List[DomainIntelligenceReport]
    ) -> List[ScenarioProjection]:
        """Simulate outcomes for a strategy across all time horizons"""
        
        projections = []
        
        for horizon in TimeHorizon:
            projection = self._simulate_horizon(strategy, horizon, domain_reports)
            projections.append(projection)
        
        return projections
    
    def _simulate_horizon(
        self,
        strategy: StrategicOption,
        horizon: TimeHorizon,
        reports: List[DomainIntelligenceReport]
    ) -> ScenarioProjection:
        """Simulate outcome for a specific horizon"""
        
        # Time multiplier
        time_mult = {
            TimeHorizon.IMMEDIATE: 0.1,
            TimeHorizon.NEAR_TERM: 0.3,
            TimeHorizon.MID_TERM: 0.6,
            TimeHorizon.LONG_TERM: 1.0
        }.get(horizon, 0.5)
        
        # Base gains from strategy
        base_gain = strategy.leverage_score * time_mult * 100
        base_risk = strategy.risk_score * (1 - time_mult) * 50
        
        # Create cases
        best_case = {
            "gain": base_gain * 1.5,
            "risk": base_risk * 0.5,
            "momentum": "positive"
        }
        
        base_case = {
            "gain": base_gain,
            "risk": base_risk,
            "momentum": "stable"
        }
        
        worst_case = {
            "gain": base_gain * 0.3,
            "risk": base_risk * 2,
            "momentum": "negative"
        }
        
        # Domain effects
        domain_effects = {}
        for report in reports:
            if strategy.domain == report.domain or strategy.domain == "cross_domain":
                domain_effects[report.domain] = {
                    "expected": base_gain / 100,
                    "risk": base_risk / 100,
                    "momentum": base_case["momentum"]
                }
        
        # Confidence decreases with longer horizons
        confidence = max(0.4, 0.9 - time_mult * 0.4)
        
        projection = ScenarioProjection(
            option_id=strategy.option_id,
            time_horizon=horizon,
            best_case=best_case,
            base_case=base_case,
            worst_case=worst_case,
            expected_gain=base_gain,
            expected_risk=base_risk,
            momentum_effect=0.3 if strategy.compounding_score > 0.5 else 0.0,
            domain_effects=domain_effects,
            confidence=confidence,
            assumptions=["Current trends continue", "No major disruptions"]
        )
        
        return projection


# ============== STRATEGIC DEBATE ENGINE ==============

class StrategicDebateEngine:
    """
    Collects domain positions and resolves tensions (BB-INT-001 Section 6.4)
    """
    
    def __init__(self):
        self._counter = 0
    
    def conduct_debate(
        self,
        strategies: List[StrategicOption],
        domain_reports: List[DomainIntelligenceReport]
    ) -> tuple:
        """Conduct strategic debate and return positions and conflicts"""
        
        positions = []
        conflicts = []
        
        # Get domain positions
        for report in domain_reports:
            position = self._get_domain_position(report, strategies)
            positions.append(position)
        
        # Identify conflicts
        conflicts = self._identify_conflicts(positions)
        
        return positions, conflicts
    
    def _get_domain_position(
        self,
        report: DomainIntelligenceReport,
        strategies: List[StrategicOption]
    ) -> StrategicDebatePosition:
        """Get a domain's debate position"""
        
        # Find relevant strategy
        relevant = [s for s in strategies if s.domain == report.domain]
        
        position = StrategicDebatePosition(
            domain=report.domain,
            chief_officer=report.chief_officer,
            position=f"Focus on {report.top_opportunities[0]}" if report.top_opportunities else "Maintain stability",
            rationale=f"{report.domain.title()} domain shows {report.domain_momentum.value} momentum",
            preferred_actions=report.top_opportunities[:2],
            concerns=report.top_risks[:2]
        )
        
        return position
    
    def _identify_conflicts(self, positions: List[StrategicDebatePosition]) -> List[StrategicConflict]:
        """Identify conflicts between domain positions"""
        
        conflicts = []
        
        # Simple conflict detection
        if len(positions) >= 2:
            # Check for resource conflicts (same priority actions)
            domains_by_action = defaultdict(list)
            for pos in positions:
                for action in pos.preferred_actions:
                    domains_by_action[action].append(pos.domain)
            
            for action, domains in domains_by_action.items():
                if len(domains) > 1:
                    self._counter += 1
                    conflict = StrategicConflict(
                        conflict_id=f"conflict_{self._counter}",
                        domains=domains,
                        description=f"Multiple domains want to focus on: {action}",
                        strategic_tension=f"Resource competition for {action}",
                        resolution_options=[
                            "Prioritize highest-impact domain",
                            "Split resources",
                            "Sequential focus"
                        ]
                    )
                    conflicts.append(conflict)
        
        return conflicts


# ============== LEVERAGE DISCOVERY ENGINE ==============

class LeverageDiscoveryEngine:
    """
    Finds high-leverage actions (BB-INT-001 Section 6.5)
    """
    
    def __init__(self):
        self._counter = 0
    
    def discover_leverage(
        self,
        domain_reports: List[DomainIntelligenceReport],
        risks: List[str],
        opportunities: List[str]
    ) -> List[LeverageOpportunity]:
        """Discover high-leverage opportunities"""
        
        opportunities_list = []
        
        # Look for multi-domain impacts
        for opp in opportunities[:5]:
            self._counter += 1
            
            # Estimate affected domains (simplified)
            affected = self._estimate_affected_domains(opp, domain_reports)
            
            leverage = LeverageOpportunity(
                opportunity_id=f"leverage_{self._counter}",
                title=opp,
                description=f"{opp} can benefit multiple areas",
                low_cost=0.3,  # Estimated
                high_benefit=0.7,  # Estimated
                compounding_effects=[f"Improves {d}" for d in affected[:2]],
                affected_domains=affected
            )
            leverage.calculate_leverage()
            
            opportunities_list.append(leverage)
        
        # Special patterns
        opportunities_list.extend(self._detect_special_patterns(domain_reports))
        
        # Sort by leverage
        opportunities_list.sort(key=lambda x: x.leverage_score, reverse=True)
        
        return opportunities_list[:3]  # Top 3
    
    def _estimate_affected_domains(
        self,
        opp: str,
        reports: List[DomainIntelligenceReport]
    ) -> List[str]:
        """Estimate which domains would benefit"""
        
        affected = []
        opp_lower = opp.lower()
        
        # Simple keyword matching
        for report in reports:
            if any(kw in opp_lower for kw in ['sleep', 'health', 'energy', 'wellness']):
                if report.domain == 'health':
                    affected.append(report.domain)
            elif any(kw in opp_lower for kw in ['income', 'career', 'skill', 'job']):
                if report.domain == 'career':
                    affected.append(report.domain)
            elif any(kw in opp_lower for kw in ['financial', 'debt', 'money', 'investment']):
                if report.domain == 'finance':
                    affected.append(report.domain)
        
        # Default to primary domain
        if not affected and reports:
            affected.append(reports[0].domain)
        
        return affected
    
    def _detect_special_patterns(
        self,
        reports: List[DomainIntelligenceReport]
    ) -> List[LeverageOpportunity]:
        """Detect special high-leverage patterns"""
        
        patterns = []
        
        # Check for sleep + workload combination
        health_report = next((r for r in reports if r.domain == 'health'), None)
        career_report = next((r for r in reports if r.domain == 'career'), None)
        
        if health_report and career_report:
            if 'sleep' in str(health_report.key_trends).lower():
                self._counter += 1
                leverage = LeverageOpportunity(
                    opportunity_id=f"leverage_{self._counter}",
                    title="Improve sleep for compound benefits",
                    description="Better sleep improves work quality, mood, and discipline simultaneously",
                    low_cost=0.2,
                    high_benefit=0.9,
                    compounding_effects=["Better work output", "Improved relationships", "Healthier decisions"],
                    affected_domains=["health", "career", "relationships"]
                )
                leverage.calculate_leverage()
                patterns.append(leverage)
        
        return patterns


# ============== ALIGNMENT ENGINE ==============

class AlignmentEngine:
    """
    Scores strategy alignment (BB-INT-001 Section 6.6)
    """
    
    def evaluate(
        self,
        strategy: StrategicOption,
        goals: List[str] = None,
        constraints: List[str] = None,
        governor_alerts: List[GovernorAlert] = None
    ) -> AlignmentEvaluation:
        """Evaluate strategy alignment"""
        
        goals = goals or []
        constraints = constraints or []
        governor_alerts = governor_alerts or []
        
        evaluation = AlignmentEvaluation(
            option_id=strategy.option_id
        )
        
        # Goal alignment (simplified)
        evaluation.goal_alignment = strategy.alignment_score
        
        # Constraint alignment
        if constraints:
            # Simple heuristic
            evaluation.constraint_alignment = 0.7 if len(constraints) < 3 else 0.5
        else:
            evaluation.constraint_alignment = 0.8
        
        # Life architecture alignment
        evaluation.life_architecture_alignment = strategy.compounding_score
        
        # Domain balance
        evaluation.domain_balance_alignment = strategy.cross_domain_benefit
        
        # Governor checks
        relevant_alerts = [a for a in governor_alerts if a.domain == strategy.domain]
        if relevant_alerts:
            evaluation.passes_governor_checks = not any(
                a.severity.value in ['high', 'critical'] for a in relevant_alerts
            )
            evaluation.governor_concerns = [
                a.risk_assessment for a in relevant_alerts
            ]
        else:
            evaluation.passes_governor_checks = True
        
        # Within policy (always true for now)
        evaluation.within_policy = True
        
        # Calculate overall
        evaluation.calculate_overall()
        
        return evaluation


# ============== STRATEGIC INTELLIGENCE ENGINE ==============

class StrategicIntelligenceEngine:
    """
    Top-level orchestrator (BB-INT-001 Section 6.7)
    
    Coordinates all components to produce strategic intelligence output.
    """
    
    def __init__(self):
        self.strategy_gen = StrategyGenerationEngine()
        self.simulation = ScenarioSimulationEngine()
        self.debate = StrategicDebateEngine()
        self.leverage = LeverageDiscoveryEngine()
        self.alignment = AlignmentEngine()
        
        self._counter = 0
    
    def process(
        self,
        domain_reports: List[DomainIntelligenceReport],
        governor_alerts: List[GovernorAlert] = None,
        user_goals: List[str] = None,
        constraints: List[str] = None
    ) -> StrategicIntelligenceOutput:
        """
        Main entry point: Generate strategic intelligence from domain reports.
        """
        
        self._counter += 1
        governor_alerts = governor_alerts or []
        
        # Extract risks and opportunities
        risks = []
        opportunities = []
        for report in domain_reports:
            risks.extend(report.top_risks)
            opportunities.extend(report.top_opportunities)
        
        # 1. Generate strategies
        strategies = self.strategy_gen.generate_strategies(
            domain_reports, risks, opportunities, user_goals, constraints
        )
        
        # 2. Simulate scenarios
        for strategy in strategies:
            projections = self.simulation.simulate(strategy, domain_reports)
        
        # 3. Conduct debate
        positions, conflicts = self.debate.conduct_debate(strategies, domain_reports)
        
        # 4. Discover leverage
        leverage_opps = self.leverage.discover_leverage(
            domain_reports, risks, opportunities
        )
        
        # 5. Evaluate alignment
        aligned_strategies = []
        for strategy in strategies:
            eval_result = self.alignment.evaluate(
                strategy, user_goals, constraints, governor_alerts
            )
            path = StrategicPath(
                path_id=f"path_{len(aligned_strategies) + 1}",
                name=strategy.title,
                strategy=strategy,
                projections=projections,
                alignment=eval_result
            )
            aligned_strategies.append(path)
        
        # Sort by final score
        for i, path in enumerate(aligned_strategies):
            path.rank = i + 1
            path.final_score = path.strategy.overall_score * (path.alignment.alignment_score if path.alignment else 0.5)
        
        aligned_strategies.sort(key=lambda x: x.final_score, reverse=True)
        
        # Build output
        output = StrategicIntelligenceOutput(
            output_id=f"strategic_output_{self._counter}",
            timestamp=datetime.now(),
            current_posture=self._determine_posture(domain_reports),
            posture_rationale=self._get_posture_rationale(domain_reports),
            top_strategic_tensions=self._extract_tensions(conflicts),
            candidate_options=strategies,
            highest_leverage_opportunities=leverage_opps,
            debate_positions=positions,
            conflicts=conflicts
        )
        
        # Set recommended path
        if aligned_strategies:
            output.recommended_path = aligned_strategies[0]
            output.recommended_path.action_sequence = [
                {"step": i+1, "action": a} 
                for i, a in enumerate(output.recommended_path.strategy.actions[:3])
            ]
            
            # Rejected paths
            for path in aligned_strategies[1:]:
                output.rejected_paths.append({
                    "title": path.strategy.title,
                    "reason": "Lower overall score" if path.alignment else "Alignment failed",
                    "score": path.final_score
                })
        
        # Set next actions
        if output.recommended_path:
            output.recommended_next_actions = output.recommended_path.strategy.actions[:3]
        
        # Confidence
        output.confidence = sum(r.confidence for r in domain_reports) / len(domain_reports) if domain_reports else 0.7
        output.key_assumptions = ["Current trends continue", "No major external disruptions"]
        
        return output
    
    def _determine_posture(self, reports: List[DomainIntelligenceReport]) -> StrategicPosture:
        """Determine current strategic posture"""
        
        if not reports:
            return StrategicPosture.STABILIZE
        
        # Check momentum
        declining = sum(1 for r in reports if r.domain_momentum.value == 'declining')
        
        if declining >= len(reports) / 2:
            return StrategicPosture.CONSOLIDATE
        elif declining == 0:
            accelerating = sum(1 for r in reports if r.domain_momentum.value == 'accelerating')
            if accelerating >= len(reports) / 2:
                return StrategicPosture.AGGRESSIVE_GROWTH
        
        return StrategicPosture.SELECTIVELY_ADVANCE
    
    def _get_posture_rationale(self, reports: List[DomainIntelligenceReport]) -> str:
        """Get rationale for posture"""
        
        if not reports:
            return "Insufficient data for posture determination"
        
        states = [r.domain_state for r in reports[:3]]
        return f"Domain states: {', '.join(states)}"
    
    def _extract_tensions(self, conflicts: List[StrategicConflict]) -> List[str]:
        """Extract strategic tensions from conflicts"""
        
        return [c.strategic_tension for c in conflicts[:3]]


__all__ = [
    "StrategyGenerationEngine",
    "ScenarioSimulationEngine", 
    "StrategicDebateEngine",
    "LeverageDiscoveryEngine",
    "AlignmentEngine",
    "StrategicIntelligenceEngine",
]
