"""
Life Architecture Domain Specialist Agents
Part of BB-DOM-001: Domain Intelligence Expansion Framework

Agents:
1. Life Alignment Advisor (Strategist) - Life purpose alignment
2. Lifestyle Architect (Strategist) - Lifestyle design
3. Time Allocation Strategist (Strategist) - Time management
4. Adventure Planner (Strategist) - Life experiences
5. Environment Designer (Strategist) - Living space optimization
6. Momentum Coordinator (Strategist) - Progress tracking
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from layer3_domain_intelligence.base_specialist_agent import (
    SpecialistAgent, ObserverAgent, StrategistAgent, GovernorAgent,
    AgentSignal, AgentInsight, AgentRole
)


# ============== LIFE ARCHITECTURE AGENTS ==============

class LifeAlignmentAdvisorAgent(StrategistAgent):
    """
    Life Alignment Advisor - Life purpose alignment
    
    Role: Strategist
    Responsibilities: Align life with values and purpose
    """
    
    def __init__(self):
        super().__init__("life_alignment_advisor", "Life Alignment Advisor", "life_architecture")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "values_check":
            return self._assess_alignment(signal)
        elif signal_type == "purpose_clarify":
            return self._clarify_purpose(signal)
        elif signal_type == "life_area_review":
            return self._review_area(signal)
        
        return None
    
    def _assess_alignment(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        alignment_score = data.get("alignment_score", 0.7)
        
        if alignment_score > 0.8:
            return self.create_insight(
                insight_type="alignment_great",
                title="Life Alignment: Excellent",
                description=f"Alignment score: {alignment_score:.0%} - Living purposefully",
                confidence=0.85,
                priority="low",
                data={"alignment": alignment_score}
            )
        elif alignment_score > 0.6:
            return self.create_insight(
                insight_type="alignment_good",
                title="Life Alignment: Good",
                description=f"Alignment score: {alignment_score:.0%} - Mostly on track",
                confidence=0.8,
                priority="medium",
                data={"alignment": alignment_score}
            )
        
        return self.create_insight(
            insight_type="alignment_poor",
            title="Life Alignment: Needs Work",
            description=f"Alignment score: {alignment_score:.0%} - Review priorities",
            confidence=0.85,
            priority="high",
            data={"alignment": alignment_score}
        )
    
    def _clarify_purpose(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        area = data.get("life_area", "career")
        
        questions = [
            "What brings you joy in this area?",
            "What would you do if money wasn't a concern?",
            "What legacy do you want to leave?"
        ]
        
        return self.create_insight(
            insight_type="purpose_clarity",
            title=f"Purpose: {area.title()}",
            description="Questions: " + " | ".join(questions[:2]),
            confidence=0.75,
            priority="high",
            data={"area": area, "questions": questions}
        )
    
    def _review_area(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        life_area = data.get("life_area", "")
        satisfaction = data.get("satisfaction", 0.5)
        
        return self.create_insight(
            insight_type="area_review",
            title=f"Review: {life_area.title()}",
            description=f"Satisfaction: {satisfaction:.0%}",
            confidence=0.8,
            priority="medium",
            data={"area": life_area, "satisfaction": satisfaction}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["alignment_assessment", "purpose_clarification", "area_review"],
            "signal_types": ["values_check", "purpose_clarify", "life_area_review"]
        }


class LifestyleArchitectAgent(StrategistAgent):
    """
    Lifestyle Architect - Lifestyle design
    
    Role: Strategist
    Responsibilities: Design optimal lifestyle patterns
    """
    
    def __init__(self):
        super().__init__("lifestyle_architect", "Lifestyle Architect", "life_architecture")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "lifestyle_design":
            return self._design_lifestyle(signal)
        elif signal_type == "routine_review":
            return self._review_routine(signal)
        elif signal_type == "lifestyle_change":
            return self._plan_change(signal)
        
        return None
    
    def _design_lifestyle(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        goals = data.get("goals", [])
        
        return self.create_insight(
            insight_type="lifestyle_design",
            title="Lifestyle Design",
            description=f"Designing around goals: {', '.join(goals[:2])}",
            confidence=0.8,
            priority="high",
            data={"goals": goals}
        )
    
    def _review_routine(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        routine_type = data.get("routine_type", "daily")
        effectiveness = data.get("effectiveness", 0.7)
        
        if effectiveness < 0.6:
            return self.create_insight(
                insight_type="routine_improve",
                title=f"Routine Review: {routine_type.title()}",
                description="Effectiveness low - redesign recommended",
                confidence=0.8,
                priority="high",
                data={"type": routine_type, "effectiveness": effectiveness}
            )
        
        return self.create_insight(
            insight_type="routine_good",
            title=f"Routine: {routine_type.title()}",
            description=f"Effectiveness: {effectiveness:.0%} - Working well",
            confidence=0.8,
            priority="low",
            data={"type": routine_type, "effectiveness": effectiveness}
        )
    
    def _plan_change(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        change = data.get("change", "")
        
        return self.create_insight(
            insight_type="change_plan",
            title=f"Lifestyle Change: {change}",
            description="Phase in gradually - 2-week adaptation period",
            confidence=0.75,
            priority="medium",
            data={"change": change}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["lifestyle_design", "routine_review", "change_planning"],
            "signal_types": ["lifestyle_design", "routine_review", "lifestyle_change"]
        }


class TimeAllocationStrategistAgent(StrategistAgent):
    """
    Time Allocation Strategist - Time management
    
    Role: Strategist
    Responsibilities: Optimize time allocation across life areas
    """
    
    def __init__(self):
        super().__init__("time_allocation_strategist", "Time Allocation Strategist", "life_architecture")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "time_audit":
            return self._audit_time(signal)
        elif signal_type == "time_redistribute":
            return self._redistribute(signal)
        elif signal_type == "schedule_optimize":
            return self._optimize_schedule(signal)
        
        return None
    
    def _audit_time(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        allocation = data.get("current_allocation", {})
        
        insights = []
        for area, hours in allocation.items():
            if hours > 50:
                insights.append(f"{area}: overloaded")
            elif hours < 5:
                insights.append(f"{area}: neglected")
        
        if insights:
            return self.create_insight(
                insight_type="time_audit",
                title="Time Audit Results",
                description="Issues: " + ", ".join(insights),
                confidence=0.85,
                priority="high",
                data={"allocation": allocation}
            )
        
        return self.create_insight(
            insight_type="time_ok",
            title="Time Allocation: Balanced",
            description="All life areas receiving adequate time",
            confidence=0.85,
            priority="low",
            data={}
        )
    
    def _redistribute(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        from_area = data.get("reduce_from", "")
        to_area = data.get("increase_to", "")
        hours = data.get("hours", 2)
        
        return self.create_insight(
            insight_type="time_redistribute",
            title="Time Redistribution",
            description=f"Move {hours}h from {from_area} to {to_area}",
            confidence=0.8,
            priority="medium",
            data={"from": from_area, "to": to_area, "hours": hours}
        )
    
    def _optimize_schedule(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        
        tips = [
            "Batch similar tasks",
            "Time-block deep work",
            "Protect morning hours for priorities",
            "Leave buffer time between commitments"
        ]
        
        return self.create_insight(
            insight_type="schedule_tips",
            title="Schedule Optimization",
            description="Tips: " + tips[0] + " | " + tips[1],
            confidence=0.75,
            priority="medium",
            data={"tips": tips}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["time_auditing", "allocation_optimization", "schedule_design"],
            "signal_types": ["time_audit", "time_redistribute", "schedule_optimize"]
        }


class AdventurePlannerAgent(StrategistAgent):
    """
    Adventure Planner - Life experiences
    
    Role: Strategist
    Responsibilities: Plan experiences, create memories, design adventures
    """
    
    def __init__(self):
        super().__init__("adventure_planner", "Adventure Planner", "life_architecture")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "adventure_idea":
            return self._plan_adventure(signal)
        elif signal_type == "experience_goal":
            return self._set_experience_goals(signal)
        elif signal_type == "memory_making":
            return self._suggest_activities(signal)
        
        return None
    
    def _plan_adventure(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        adventure_type = data.get("type", "new")
        budget = data.get("budget", "moderate")
        
        adventures = {
            "local": ["Try new restaurant", "Day trip nearby", "Explore hidden gem"],
            "regional": ["Weekend road trip", "National park visit", "City escape"],
            "international": ["New country", "Culture immersion", "Adventure travel"]
        }
        
        options = adventures.get(budget, adventures["local"])
        
        return self.create_insight(
            insight_type="adventure_plan",
            title=f"Adventure: {adventure_type.title()}",
            description=f"Options: {options[0]}",
            confidence=0.75,
            priority="medium",
            data={"type": adventure_type, "options": options}
        )
    
    def _set_experience_goals(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        year = data.get("year", 2024)
        
        return self.create_insight(
            insight_type="experience_goals",
            title=f"Experience Goals: {year}",
            description="Plan: 1 big adventure + 12 monthly experiences",
            confidence=0.8,
            priority="medium",
            data={"year": year}
        )
    
    def _suggest_activities(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        season = data.get("season", "spring")
        
        activities = {
            "spring": "Outdoor markets, hiking, gardening",
            "summer": "Beach, concerts, BBQs",
            "fall": "Apple picking, driving tours, festivals",
            "winter": "Cozy gatherings, winter sports, reflection"
        }
        
        return self.create_insight(
            insight_type="seasonal_activities",
            title=f"Seasonal Activities: {season.title()}",
            description=activities.get(season, "Plan meaningful activities"),
            confidence=0.75,
            priority="low",
            data={"season": season, "activities": activities.get(season)}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["adventure_planning", "experience_design", "memory_creation"],
            "signal_types": ["adventure_idea", "experience_goal", "memory_making"]
        }


class EnvironmentDesignerAgent(StrategistAgent):
    """
    Environment Designer - Living space optimization
    
    Role: Strategist
    Responsibilities: Design optimal environments for productivity and wellbeing
    """
    
    def __init__(self):
        super().__init__("environment_designer", "Environment Designer", "life_architecture")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "space_design":
            return self._design_space(signal)
        elif signal_type == "environment_assess":
            return self._assess_environment(signal)
        elif signal_type == "organization":
            return self._suggest_organization(signal)
        
        return None
    
    def _design_space(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        space_type = data.get("space_type", "home_office")
        goal = data.get("goal", "productivity")
        
        elements = {
            "productivity": ["Ergonomic desk", "Good lighting", "Minimal distractions"],
            "relaxation": ["Comfortable seating", "Soft lighting", "Natural elements"],
            "creativity": ["Inspiring art", "Flexible seating", "Open space"]
        }
        
        return self.create_insight(
            insight_type="space_design",
            title=f"Design: {space_type.replace('_', ' ').title()}",
            description=f"For {goal}: {', '.join(elements.get(goal, elements['productivity'])[:2])}",
            confidence=0.75,
            priority="medium",
            data={"space": space_type, "goal": goal}
        )
    
    def _assess_environment(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        workspace_score = data.get("workspace_score", 0.7)
        
        if workspace_score < 0.6:
            return self.create_insight(
                insight_type="environment_improve",
                title="Environment Needs Work",
                description="Workspace optimization recommended",
                confidence=0.8,
                priority="high",
                data={"score": workspace_score}
            )
        
        return self.create_insight(
            insight_type="environment_good",
            title="Environment: Good",
            description="Space supports your goals well",
            confidence=0.8,
            priority="low",
            data={"score": workspace_score}
        )
    
    def _suggest_organization(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        area = data.get("area", "workspace")
        
        tips = [
            "One in, one out rule",
            "Designate a home for everything",
            "Weekly 15-minute reset",
            "Vertical storage for small items"
        ]
        
        return self.create_insight(
            insight_type="organization_tips",
            title=f"Organization: {area.title()}",
            description="Tip: " + tips[0],
            confidence=0.75,
            priority="medium",
            data={"area": area, "tips": tips}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["space_design", "environment_assessment", "organization_systems"],
            "signal_types": ["space_design", "environment_assess", "organization"]
        }


class MomentumCoordinatorAgent(StrategistAgent):
    """
    Momentum Coordinator - Progress tracking
    
    Role: Strategist
    Responsibilities: Track momentum, maintain progress, adjust course
    """
    
    def __init__(self):
        super().__init__("momentum_coordinator", "Momentum Coordinator", "life_architecture")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "momentum_check":
            return self._assess_momentum(signal)
        elif signal_type == "progress_stalled":
            return self._restart_momentum(signal)
        elif signal_type == "milestone":
            return self._celebrate_milestone(signal)
        
        return None
    
    def _assess_momentum(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        streak = data.get("streak_days", 0)
        velocity = data.get("velocity", 0.5)
        
        if streak > 7 and velocity > 0.7:
            return self.create_insight(
                insight_type="momentum_strong",
                title="Momentum: Strong",
                description=f"Streak: {streak} days, Velocity: {velocity:.0%}",
                confidence=0.9,
                priority="low",
                data={"streak": streak, "velocity": velocity}
            )
        elif streak > 0:
            return self.create_insight(
                insight_type="momentum_building",
                title="Momentum: Building",
                description=f"Streak: {streak} days - Keep going!",
                confidence=0.85,
                priority="low",
                data={"streak": streak, "velocity": velocity}
            )
        
        return self.create_insight(
            insight_type="momentum_low",
            title="Momentum: Starting",
            description="Begin small - build consistency",
            confidence=0.8,
            priority="medium",
            data={"streak": streak, "velocity": velocity}
        )
    
    def _restart_momentum(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        stalled_weeks = data.get("weeks_stalled", 1)
        
        strategies = [
            "Reduce scope - start smaller",
            "Remove friction - simplify starting",
            "Add accountability - share goal",
            "Reward small wins"
        ]
        
        return self.create_insight(
            insight_type="restart_momentum",
            title=f"Momentum Stalled ({stalled_weeks} weeks)",
            description="Strategy: " + strategies[0],
            confidence=0.8,
            priority="high",
            data={"weeks": stalled_weeks, "strategies": strategies}
        )
    
    def _celebrate_milestone(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        milestone = data.get("milestone", "")
        
        return self.create_insight(
            insight_type="milestone_reached",
            title=f"Milestone: {milestone}",
            description="Acknowledge achievement! Document the success.",
            confidence=0.95,
            priority="low",
            data={"milestone": milestone}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["momentum_tracking", "progress_assessment", "restart_planning"],
            "signal_types": ["momentum_check", "progress_stalled", "milestone"]
        }


# ============== LIFE ARCHITECTURE GOVERNOR (ADDED) ==============

class LifeBalanceGovernorAgent(GovernorAgent):
    """
    Life Balance Governor - Life balance enforcement
    
    Role: Governor
    Responsibilities: Monitor life balance, enforce limits, prevent burnout
    """
    
    def __init__(self):
        super().__init__("life_balance_governor", "Life Balance Governor", "life_architecture")
        self.balance_thresholds = {
            "work_life": 0.3,  # Max work percentage
            "social": 0.1,     # Min social percentage
            "self_care": 0.05  # Min self-care percentage
        }
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "balance_check":
            return self._assess_balance(signal)
        elif signal_type == "burnout_warning":
            return self._evaluate_burnout_risk(signal)
        elif signal_type == "overwork_detected":
            return self._address_overwork(signal)
        
        return None
    
    def _assess_balance(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        allocation = data.get("allocation", {})
        
        issues = []
        
        work_pct = allocation.get("work", 0)
        if work_pct > self.balance_thresholds["work_life"]:
            issues.append(f"Work overload: {work_pct:.0%} (max: {self.balance_thresholds['work_life']:.0%})")
        
        social_pct = allocation.get("social", 0)
        if social_pct < self.balance_thresholds["social"]:
            issues.append(f"Low social: {social_pct:.0%} (min: {self.balance_thresholds['social']:.0%})")
        
        self_pct = allocation.get("self_care", 0)
        if self_pct < self.balance_thresholds["self_care"]:
            issues.append(f"Low self-care: {self_pct:.0%} (min: {self.balance_thresholds['self_care']:.0%})")
        
        if issues:
            return self.create_insight(
                insight_type="balance_issues",
                title="Life Balance Issues Detected",
                description=" | ".join(issues),
                confidence=0.85,
                priority="high",
                data={"issues": issues}
            )
        
        return self.create_insight(
            insight_type="balance_good",
            title="Life Balance: Healthy",
            description="All life areas receiving adequate attention",
            confidence=0.85,
            priority="low",
            data={}
        )
    
    def _evaluate_burnout_risk(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        risk_score = data.get("risk_score", 0)
        
        if risk_score > 0.7:
            return self.create_insight(
                insight_type="burnout_risk",
                title="Burnout Risk: HIGH",
                description="Immediate action required - reduce load",
                confidence=0.9,
                priority="critical",
                data={"risk_score": risk_score}
            )
        elif risk_score > 0.5:
            return self.create_insight(
                insight_type="burnout_warning",
                title="Burnout Risk: Elevated",
                description="Increase recovery time, reduce stress",
                confidence=0.8,
                priority="high",
                data={"risk_score": risk_score}
            )
        
        return self.create_insight(
            insight_type="burnout_safe",
            title="Burnout Risk: Low",
            description="Balance appears sustainable",
            confidence=0.85,
            priority="low",
            data={"risk_score": risk_score}
        )
    
    def _address_overwork(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        consecutive_days = data.get("consecutive_days", 0)
        
        if consecutive_days > 10:
            return self.create_insight(
                insight_type="overwork_critical",
                title=f"Overwork: {consecutive_days} consecutive days",
                description="MANDATORY: Take at least 1 full day off",
                confidence=0.95,
                priority="critical",
                data={"days": consecutive_days}
            )
        
        return self.create_insight(
            insight_type="overwork_warning",
            title=f"Overwork: {consecutive_days} days",
            description="Consider taking a break soon",
            confidence=0.8,
            priority="medium",
            data={"days": consecutive_days}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "governor",
            "capabilities": ["balance_assessment", "burnout_prevention", "workload_enforcement"],
            "signal_types": ["balance_check", "burnout_warning", "overwork_detected"],
            "thresholds": self.balance_thresholds
        }
