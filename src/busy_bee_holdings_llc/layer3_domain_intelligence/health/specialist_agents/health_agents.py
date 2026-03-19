"""
Health Domain Specialist Agents
Part of BB-DOM-001: Domain Intelligence Expansion Framework

Agents:
1. Sleep Recovery Advisor (Strategist) - Sleep optimization
2. Nutrition Strategist (Strategist) - Dietary planning
3. Fitness Programmer (Strategist) - Exercise programming
4. Stress Resilience Analyst (Governor) - Stress management
5. Habit Formation Coach (Strategist) - Behavior change
6. Preventive Health Monitor (Observer) - Health monitoring
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from layer3_domain_intelligence.base_specialist_agent import (
    SpecialistAgent, ObserverAgent, StrategistAgent, GovernorAgent,
    AgentSignal, AgentInsight, AgentRole
)


# ============== HEALTH AGENTS ==============

class SleepRecoveryAdvisorAgent(StrategistAgent):
    """
    Sleep Recovery Advisor - Sleep optimization
    
    Role: Strategist
    Responsibilities: Optimize sleep quality, recovery strategies
    """
    
    def __init__(self):
        super().__init__("sleep_recovery_advisor", "Sleep Recovery Advisor", "health")
        self.optimal_hours = (7, 9)
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "sleep_data":
            return self._analyze_sleep(signal)
        elif signal_type == "sleep_debt":
            return self._calculate_recovery(signal)
        elif signal_type == "sleep_schedule":
            return self._optimize_schedule(signal)
        
        return None
    
    def _analyze_sleep(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        hours = data.get("hours", 7)
        quality = data.get("quality", 0.7)
        
        assessment = "optimal"
        if hours < self.optimal_hours[0] or quality < 0.7:
            assessment = "needs_improvement"
        if hours < 5:
            assessment = "critical"
        
        return self.create_insight(
            insight_type="sleep_analysis",
            title=f"Sleep: {hours}h, Quality: {quality:.0%}",
            description=f"Sleep status: {assessment}",
            confidence=0.85,
            priority="high" if assessment == "critical" else "medium",
            data={"hours": hours, "quality": quality}
        )
    
    def _calculate_recovery(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        debt_hours = data.get("debt_hours", 0)
        
        recovery_plan = []
        if debt_hours > 10:
            recovery_plan.append("Add 1-2 extra sleep hours/night for 1 week")
            recovery_plan.append("Consider naps (20-30min)")
        elif debt_hours > 5:
            recovery_plan.append("Add 30-60 min extra sleep nightly")
        
        return self.create_insight(
            insight_type="recovery_plan",
            title=f"Sleep Debt: {debt_hours}h",
            description="Recovery plan: " + "; ".join(recovery_plan) if recovery_plan else "No significant debt",
            confidence=0.8,
            priority="high" if debt_hours > 10 else "medium",
            data={"debt_hours": debt_hours, "plan": recovery_plan}
        )
    
    def _optimize_schedule(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        current_bedtime = data.get("current_bedtime", "11:00")
        current_wake = data.get("current_wake", "7:00")
        
        suggestions = [
            "Maintain consistent sleep/wake times",
            "Avoid screens 1h before bed",
            "Keep bedroom cool (65-68°F)"
        ]
        
        return self.create_insight(
            insight_type="schedule_optimization",
            title="Sleep Schedule Optimization",
            description="Current: " + current_bedtime + " - " + current_wake + ". " + " | ".join(suggestions),
            confidence=0.75,
            priority="medium",
            data={"bedtime": current_bedtime, "wake": current_wake}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["sleep_analysis", "recovery_planning", "schedule_optimization"],
            "signal_types": ["sleep_data", "sleep_debt", "sleep_schedule"]
        }


class NutritionStrategistAgent(StrategistAgent):
    """
    Nutrition Strategist - Dietary planning
    
    Role: Strategist
    Responsibilities: Analyze nutrition, create meal strategies
    """
    
    def __init__(self):
        super().__init__("nutrition_strategist", "Nutrition Strategist", "health")
        self.macros_ratio = {"protein": 0.30, "carbs": 0.40, "fats": 0.30}
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "meal_log":
            return self._analyze_meals(signal)
        elif signal_type == "macro_analysis":
            return self._analyze_macros(signal)
        elif signal_type == "nutrition_goal":
            return self._plan_nutrition(signal)
        
        return None
    
    def _analyze_meals(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        calories = data.get("calories", 2000)
        meals = data.get("meals_count", 3)
        
        assessment = "balanced"
        if calories > 2500:
            assessment = "calorie_excess"
        elif calories < 1500:
            assessment = "calorie_deficit"
        
        return self.create_insight(
            insight_type="meal_analysis",
            title=f"Daily Nutrition: {calories} cal, {meals} meals",
            description=f"Assessment: {assessment}",
            confidence=0.8,
            priority="medium",
            data={"calories": calories, "meals": meals}
        )
    
    def _analyze_macros(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        protein = data.get("protein_pct", 0)
        carbs = data.get("carbs_pct", 0)
        fats = data.get("fats_pct", 0)
        
        adjustments = []
        if abs(protein - self.macros_ratio["protein"]) > 0.1:
            adjustments.append(f"protein: {protein:.0%} -> {self.macros_ratio['protein']:.0%}")
        if abs(carbs - self.macros_ratio["carbs"]) > 0.15:
            adjustments.append(f"carbs: {carbs:.0%} -> {self.macros_ratio['carbs']:.0%}")
        
        if adjustments:
            return self.create_insight(
                insight_type="macro_recommendation",
                title="Macro Adjustments Needed",
                description="Adjust: " + ", ".join(adjustments),
                confidence=0.75,
                priority="medium",
                data={"protein": protein, "carbs": carbs, "fats": fats}
            )
        
        return self.create_insight(
            insight_type="macro_ok",
            title="Macros Well-Balanced",
            description="All macronutrients within target ranges",
            confidence=0.75,
            priority="low",
            data={}
        )
    
    def _plan_nutrition(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        goal = data.get("goal", "maintain")  # lose_weight, gain_muscle, maintain
        
        plans = {
            "lose_weight": "Calorie deficit 300-500, high protein, moderate carbs",
            "gain_muscle": "Calorie surplus 200-300, high protein, moderate carbs",
            "maintain": "Balanced maintenance calories"
        }
        
        return self.create_insight(
            insight_type="nutrition_plan",
            title=f"Nutrition Plan: {goal.replace('_', ' ').title()}",
            description=plans.get(goal, "Maintain balanced diet"),
            confidence=0.8,
            priority="high",
            data={"goal": goal, "plan": plans.get(goal)}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["meal_analysis", "macro_planning", "nutrition_goals"],
            "signal_types": ["meal_log", "macro_analysis", "nutrition_goal"]
        }


class FitnessProgrammerAgent(StrategistAgent):
    """
    Fitness Programmer - Exercise programming
    
    Role: Strategist
    Responsibilities: Design workout programs, track progress
    """
    
    def __init__(self):
        super().__init__("fitness_programmer", "Fitness Programmer", "health")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "workout_data":
            return self._analyze_workout(signal)
        elif signal_type == "fitness_goal":
            return self._create_program(signal)
        elif signal_type == "progress_stalled":
            return self._adjust_program(signal)
        
        return None
    
    def _analyze_workout(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        workout_type = data.get("type", "unknown")
        duration = data.get("duration_minutes", 0)
        intensity = data.get("intensity", 0.5)
        
        assessment = "good"
        if duration < 30:
            assessment = "too_short"
        elif duration > 90:
            assessment = "too_long"
        
        return self.create_insight(
            insight_type="workout_analysis",
            title=f"{workout_type}: {duration}min @ {intensity:.0%} intensity",
            description=f"Assessment: {assessment}",
            confidence=0.8,
            priority="medium",
            data={"type": workout_type, "duration": duration}
        )
    
    def _create_program(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        goal = data.get("goal", "general_fitness")
        days_available = data.get("days_per_week", 3)
        
        programs = {
            "strength": f"{days_available}x/week - Compound lifts, progressive overload",
            "cardiovascular": f"{days_available}x/week - Mix of HIIT and steady state",
            "flexibility": f"{days_available}x/week - Daily stretching, yoga",
            "general_fitness": f"{days_available}x/week - Mix of strength and cardio"
        }
        
        return self.create_insight(
            insight_type="fitness_program",
            title=f"Fitness Program: {goal}",
            description=programs.get(goal, programs["general_fitness"]),
            confidence=0.8,
            priority="high",
            data={"goal": goal, "days": days_available}
        )
    
    def _adjust_program(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        plateau_weeks = data.get("weeks_stalled", 2)
        
        suggestions = [
            "Vary intensity (undulating periodization)",
            "Increase rest between sets",
            "Try progressive overload in different form",
            "Ensure adequate recovery and nutrition"
        ]
        
        return self.create_insight(
            insight_type="program_adjustment",
            title=f"Progress Plateau ({plateau_weeks} weeks)",
            description="Adjustments: " + " | ".join(suggestions[:2]),
            confidence=0.75,
            priority="medium",
            data={"weeks_stalled": plateau_weeks}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["workout_design", "progress_tracking", "program_adjustment"],
            "signal_types": ["workout_data", "fitness_goal", "progress_stalled"]
        }


class StressResilienceAnalystAgent(GovernorAgent):
    """
    Stress Resilience Analyst - Stress management
    
    Role: Governor
    Responsibilities: Monitor stress, enforce limits, maintain resilience
    """
    
    def __init__(self):
        super().__init__("stress_resilience_analyst", "Stress Resilience Analyst", "health")
        self.stress_threshold = 0.7
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "stress_indicator":
            return self._assess_stress(signal)
        elif signal_type == "burnout_risk":
            return self._evaluate_burnout(signal)
        elif signal_type == "resilience_check":
            return self._check_resilience(signal)
        
        return None
    
    def _assess_stress(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        stress_level = data.get("stress_level", 0.5)
        
        if stress_level > self.stress_threshold:
            return self.create_insight(
                insight_type="stress_alert",
                title=f"High Stress: {stress_level:.0%}",
                description="Stress exceeds threshold. Implement coping strategies.",
                confidence=0.85,
                priority="critical",
                data={"stress_level": stress_level}
            )
        
        return self.create_insight(
            insight_type="stress_normal",
            title=f"Stress Level: {stress_level:.0%}",
            description="Stress within normal range",
            confidence=0.85,
            priority="low",
            data={"stress_level": stress_level}
        )
    
    def _evaluate_burnout(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        risk_score = data.get("risk_score", 0)
        
        if risk_score > 0.7:
            return self.create_insight(
                insight_type="burnout_warning",
                title="Burnout Risk: HIGH",
                description="Immediate action required. Take break, reduce load.",
                confidence=0.9,
                priority="critical",
                data={"risk_score": risk_score}
            )
        elif risk_score > 0.5:
            return self.create_insight(
                insight_type="burnout_caution",
                title="Burnout Risk: Elevated",
                description="Monitor closely. Increase recovery time.",
                confidence=0.8,
                priority="high",
                data={"risk_score": risk_score}
            )
        
        return self.create_insight(
            insight_type="burnout_ok",
            title="Burnout Risk: Low",
            description="Stress levels manageable",
            confidence=0.8,
            priority="low",
            data={"risk_score": risk_score}
        )
    
    def _check_resilience(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        resilience_score = data.get("resilience_score", 0.5)
        
        if resilience_score < 0.4:
            return self.create_insight(
                insight_type="resilience_low",
                title="Low Resilience",
                description="Build resilience through: meditation, exercise, social connection",
                confidence=0.75,
                priority="high",
                data={"resilience_score": resilience_score}
            )
        
        return self.create_insight(
            insight_type="resilience_good",
            title="Good Resilience",
            description="Resilience score healthy",
            confidence=0.75,
            priority="low",
            data={"resilience_score": resilience_score}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "governor",
            "capabilities": ["stress_monitoring", "burnout_prevention", "resilience_assessment"],
            "signal_types": ["stress_indicator", "burnout_risk", "resilience_check"],
            "threshold": self.stress_threshold
        }


class HabitFormationCoachAgent(StrategistAgent):
    """
    Habit Formation Coach - Behavior change
    
    Role: Strategist
    Responsibilities: Design habits, track formation, provide coaching
    """
    
    def __init__(self):
        super().__init__("habit_formation_coach", "Habit Formation Coach", "health")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "habit_attempt":
            return self._design_habit(signal)
        elif signal_type == "habit_progress":
            return self._track_habit(signal)
        elif signal_type == "habit_failure":
            return self._analyze_failure(signal)
        
        return None
    
    def _design_habit(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        habit = data.get("habit", "")
        cue = data.get("cue", "morning routine")
        reward = data.get("reward", "coffee")
        
        return self.create_insight(
            insight_type="habit_design",
            title=f"Habit Design: {habit}",
            description=f"After {cue}, I will {habit}, then {reward}",
            confidence=0.8,
            priority="high",
            data={"habit": habit, "cue": cue, "reward": reward}
        )
    
    def _track_habit(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        streak = data.get("streak_days", 0)
        consistency = data.get("consistency", 0)
        
        if streak >= 21:
            status = "habit_formed"
            desc = f"Great! {streak} day streak - habit likely formed"
        elif streak >= 7:
            status = "building"
            desc = f"Good progress! Keep going for {21 - streak} more days"
        else:
            status = "early"
            desc = f"Starting strong. Aim for 7-day streak"
        
        return self.create_insight(
            insight_type="habit_progress",
            title=f"Habit Streak: {streak} days",
            description=desc,
            confidence=0.85,
            priority="medium",
            data={"streak": streak, "consistency": consistency}
        )
    
    def _analyze_failure(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        failed_habit = data.get("habit", "unknown")
        reason = data.get("reason", "unknown")
        
        solutions = {
            "forgot": "Add visual cue or reminder",
            "too_hard": "Simplify - make it easier",
            "no_time": "Attach to existing routine",
            "no_motivation": "Find stronger reward"
        }
        
        return self.create_insight(
            insight_type="habit_advice",
            title=f"Habit Failed: {failed_habit}",
            description=f"Reason: {reason}. Solution: {solutions.get(reason, 'Try again')}",
            confidence=0.7,
            priority="medium",
            data={"habit": failed_habit, "reason": reason}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["habit_design", "tracking", "behavior_coaching"],
            "signal_types": ["habit_attempt", "habit_progress", "habit_failure"]
        }


class PreventiveHealthMonitorAgent(ObserverAgent):
    """
    Preventive Health Monitor - Health monitoring
    
    Role: Observer
    Responsibilities: Monitor health metrics, detect anomalies, provide awareness
    """
    
    def __init__(self):
        super().__init__("preventive_health_monitor", "Preventive Health Monitor", "health")
        self.baseline_metrics = {}
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "vitals":
            return self._analyze_vitals(signal)
        elif signal_type == "screening_due":
            return self._check_screenings(signal)
        elif signal_type == "metric_anomaly":
            return self._detect_anomaly(signal)
        
        return None
    
    def _analyze_vitals(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        heart_rate = data.get("heart_rate", 70)
        blood_pressure = data.get("blood_pressure", "120/80")
        
        # Simple analysis
        if heart_rate > 100:
            return self.create_insight(
                insight_type="vitals_alert",
                title="Elevated Heart Rate",
                description=f"HR: {heart_rate} bpm - may indicate stress or condition",
                confidence=0.7,
                priority="high",
                data={"heart_rate": heart_rate}
            )
        
        return self.create_insight(
            insight_type="vitals_normal",
            title="Vitals Normal",
            description=f"HR: {heart_rate}, BP: {blood_pressure}",
            confidence=0.8,
            priority="low",
            data={"heart_rate": heart_rate, "blood_pressure": blood_pressure}
        )
    
    def _check_screenings(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        screening_type = data.get("type", "general")
        last_check = data.get("months_since", 0)
        recommended_interval = data.get("recommended_months", 12)
        
        if last_check >= recommended_interval:
            return self.create_insight(
                insight_type="screening_due",
                title=f"Screening Due: {screening_type}",
                description=f"Last check: {last_check} months ago. Recommended: every {recommended_interval} months",
                confidence=0.9,
                priority="high",
                data={"type": screening_type, "months": last_check}
            )
        
        return self.create_insight(
            insight_type="screening_ok",
            title=f"{screening_type} Screening Current",
            description=f"Next due in {recommended_interval - last_check} months",
            confidence=0.9,
            priority="low",
            data={}
        )
    
    def _detect_anomaly(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        metric = data.get("metric", "unknown")
        deviation = data.get("deviation_from_baseline", 0)
        
        if abs(deviation) > 0.2:
            return self.create_insight(
                insight_type="anomaly_detected",
                title=f"Anomaly: {metric}",
                description=f"Deviation: {deviation:+.0%} from baseline - monitor closely",
                confidence=0.75,
                priority="high",
                data={"metric": metric, "deviation": deviation}
            )
        
        return None
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "observer",
            "capabilities": ["vitals_monitoring", "screening_tracking", "anomaly_detection"],
            "signal_types": ["vitals", "screening_due", "metric_anomaly"]
        }
