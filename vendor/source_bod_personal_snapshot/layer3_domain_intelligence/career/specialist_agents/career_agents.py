"""
Career Domain Specialist Agents
Part of BB-DOM-001: Domain Intelligence Expansion Framework

Agents:
1. Skill Development Strategist (Strategist) - Career skill planning
2. Opportunity Analyst (Observer) - Job market opportunities
3. Performance Coach (Strategist) - Performance improvement
4. Reputation Builder (Strategist) - Personal branding
5. Income Growth Planner (Strategist) - Earning potential
6. Decision Leverage Advisor (Strategist) - Career decisions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from layer3_domain_intelligence.base_specialist_agent import (
    SpecialistAgent, ObserverAgent, StrategistAgent, GovernorAgent,
    AgentSignal, AgentInsight, AgentRole
)


# ============== CAREER AGENTS ==============

class SkillDevelopmentStrategistAgent(StrategistAgent):
    """
    Skill Development Strategist - Career skill planning
    
    Role: Strategist
    Responsibilities: Plan skill development, identify learning paths
    """
    
    def __init__(self):
        super().__init__("skill_development_strategist", "Skill Development Strategist", "career")
        self.in_demand_skills = ["AI/ML", "Cloud Computing", "Data Analysis", "Leadership", "Communication"]
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "skill_gap":
            return self._identify_skill_gaps(signal)
        elif signal_type == "learning_path":
            return self._plan_learning(signal)
        elif signal_type == "skill_acquired":
            return self._validate_skill(signal)
        
        return None
    
    def _identify_skill_gaps(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        current_skills = data.get("current_skills", [])
        target_role = data.get("target_role", "unknown")
        
        # Find gaps (simplified)
        relevant_skills = self.in_demand_skills[:3]  # Simplified
        gaps = [s for s in relevant_skills if s not in current_skills]
        
        if gaps:
            return self.create_insight(
                insight_type="skill_gap",
                title=f"Skill Gaps for {target_role}",
                description=f"Missing: {', '.join(gaps)}",
                confidence=0.8,
                priority="high",
                data={"gaps": gaps, "role": target_role}
            )
        
        return self.create_insight(
            insight_type="skill_gap_ok",
            title="Skills Current",
            description="Your skills align well with target role",
            confidence=0.8,
            priority="low",
            data={}
        )
    
    def _plan_learning(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        skill = data.get("skill", "")
        timeline = data.get("timeline_months", 6)
        
        return self.create_insight(
            insight_type="learning_plan",
            title=f"Learning Plan: {skill}",
            description=f"Recommended: {timeline//2} hours/week for {timeline} months",
            confidence=0.75,
            priority="medium",
            data={"skill": skill, "timeline": timeline}
        )
    
    def _validate_skill(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        skill = data.get("skill", "")
        proficiency = data.get("proficiency", 0.5)
        
        return self.create_insight(
            insight_type="skill_validated",
            title=f"Skill Acquired: {skill}",
            description=f"Proficiency: {proficiency:.0%} - Add to profile",
            confidence=0.9,
            priority="medium",
            data={"skill": skill, "proficiency": proficiency}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["skill_gap_analysis", "learning_planning", "skill_validation"],
            "signal_types": ["skill_gap", "learning_path", "skill_acquired"]
        }


class OpportunityAnalystAgent(ObserverAgent):
    """
    Opportunity Analyst - Job market opportunities
    
    Role: Observer
    Responsibilities: Monitor job market, detect opportunities, provide awareness
    """
    
    def __init__(self):
        super().__init__("opportunity_analyst", "Opportunity Analyst", "career")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "job_opening":
            return self._analyze_opportunity(signal)
        elif signal_type == "market_trend":
            return self._analyze_trend(signal)
        elif signal_type == "salary_benchmark":
            return self._analyze_salary(signal)
        
        return None
    
    def _analyze_opportunity(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        role = data.get("role", "Unknown")
        match_score = data.get("match_score", 0.5)
        
        if match_score > 0.8:
            return self.create_insight(
                insight_type="opportunity_strong",
                title=f"Strong Match: {role}",
                description=f"Match score: {match_score:.0%} - Apply recommended",
                confidence=0.85,
                priority="high",
                data={"role": role, "match": match_score}
            )
        
        return self.create_insight(
            insight_type="opportunity_moderate",
            title=f"Opportunity: {role}",
            description=f"Match score: {match_score:.0%} - Partial match",
            confidence=0.7,
            priority="medium",
            data={"role": role, "match": match_score}
        )
    
    def _analyze_trend(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        trend = data.get("trend", "")
        impact = data.get("impact", "neutral")
        
        return self.create_insight(
            insight_type="market_trend",
            title=f"Market Trend: {trend}",
            description=f"Impact: {impact}",
            confidence=0.75,
            priority="medium",
            data={"trend": trend, "impact": impact}
        )
    
    def _analyze_salary(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        role = data.get("role", "")
        salary_range = data.get("salary_range", (0, 0))
        
        return self.create_insight(
            insight_type="salary_benchmark",
            title=f"Salary: {role}",
            description=f"Range: \${salary_range[0]:,} - \${salary_range[1]:,}",
            confidence=0.8,
            priority="medium",
            data={"role": role, "range": salary_range}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "observer",
            "capabilities": ["opportunity_detection", "market_analysis", "salary_benchmarking"],
            "signal_types": ["job_opening", "market_trend", "salary_benchmark"]
        }


class PerformanceCoachAgent(StrategistAgent):
    """
    Performance Coach - Performance improvement
    
    Role: Strategist
    Responsibilities: Analyze performance, provide coaching recommendations
    """
    
    def __init__(self):
        super().__init__("performance_coach", "Performance Coach", "career")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "performance_review":
            return self._analyze_performance(signal)
        elif signal_type == "goal_setting":
            return self._set_goals(signal)
        elif signal_type == "improvement_area":
            return self._identify_improvement(signal)
        
        return None
    
    def _analyze_performance(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        rating = data.get("rating", 3)  # 1-5
        areas = data.get("strengths", [])
        
        feedback = f"Rating: {rating}/5. Strengths: {', '.join(areas[:2])}"
        
        return self.create_insight(
            insight_type="performance_analysis",
            title="Performance Review Analysis",
            description=feedback,
            confidence=0.85,
            priority="medium",
            data={"rating": rating, "strengths": areas}
        )
    
    def _set_goals(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        goals = data.get("goals", [])
        
        return self.create_insight(
            insight_type="goals_set",
            title="Performance Goals Set",
            description=f"Goals: {', '.join(goals[:3])}",
            confidence=0.8,
            priority="high",
            data={"goals": goals}
        )
    
    def _identify_improvement(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        area = data.get("area", "")
        current = data.get("current_level", 0)
        target = data.get("target_level", 5)
        
        return self.create_insight(
            insight_type="improvement_plan",
            title=f"Improve: {area}",
            description=f"Target: {target}/5 from {current}/5",
            confidence=0.75,
            priority="medium",
            data={"area": area, "current": current, "target": target}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["performance_analysis", "goal_setting", "coaching"],
            "signal_types": ["performance_review", "goal_setting", "improvement_area"]
        }


class ReputationBuilderAgent(StrategistAgent):
    """
    Reputation Builder - Personal branding
    
    Role: Strategist
    Responsibilities: Build professional reputation, increase visibility
    """
    
    def __init__(self):
        super().__init__("reputation_builder", "Reputation Builder", "career")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "visibility_check":
            return self._assess_visibility(signal)
        elif signal_type == "content_idea":
            return self._suggest_content(signal)
        elif signal_type == "network_growth":
            return self._plan_outreach(signal)
        
        return None
    
    def _assess_visibility(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        followers = data.get("followers", 0)
        engagement = data.get("engagement_rate", 0)
        
        if followers < 500:
            return self.create_insight(
                insight_type="visibility_low",
                title="Low Visibility",
                description="Focus on growing professional network",
                confidence=0.75,
                priority="high",
                data={"followers": followers}
            )
        
        return self.create_insight(
            insight_type="visibility_good",
            title="Good Visibility",
            description=f"Followers: {followers}, Engagement: {engagement:.1%}",
            confidence=0.8,
            priority="low",
            data={"followers": followers, "engagement": engagement}
        )
    
    def _suggest_content(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        topic = data.get("topic", "industry insight")
        
        return self.create_insight(
            insight_type="content_suggestion",
            title="Content Idea",
            description=f"Share: {topic} - builds thought leadership",
            confidence=0.7,
            priority="medium",
            data={"topic": topic}
        )
    
    def _plan_outreach(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        target_industry = data.get("target_industry", "tech")
        
        return self.create_insight(
            insight_type="outreach_plan",
            title="Network Growth Plan",
            description=f"Connect with {target_industry} leaders",
            confidence=0.7,
            priority="medium",
            data={"industry": target_industry}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["visibility_assessment", "content_strategy", "networking"],
            "signal_types": ["visibility_check", "content_idea", "network_growth"]
        }


class IncomeGrowthPlannerAgent(StrategistAgent):
    """
    Income Growth Planner - Earning potential
    
    Role: Strategist
    Responsibilities: Plan income growth, identify earning opportunities
    """
    
    def __init__(self):
        super().__init__("income_growth_planner", "Income Growth Planner", "career")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "income_opportunity":
            return self._plan_income_growth(signal)
        elif signal_type == "promotion_path":
            return self._plan_promotion(signal)
        elif signal_type == "side_income":
            return self._suggest_side_income(signal)
        
        return None
    
    def _plan_income_growth(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        current_income = data.get("current_income", 0)
        target_income = data.get("target_income", 0)
        
        growth_needed = target_income - current_income
        pct_growth = growth_needed / current_income if current_income > 0 else 0
        
        return self.create_insight(
            insight_type="income_plan",
            title="Income Growth Plan",
            description=f"Growth needed: ${growth_needed:,} ({pct_growth:.0%})",
            confidence=0.75,
            priority="high",
            data={"current": current_income, "target": target_income}
        )
    
    def _plan_promotion(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        current_level = data.get("current_level", "")
        target_level = data.get("target_level", "")
        
        timeline = data.get("timeline_months", 12)
        
        return self.create_insight(
            insight_type="promotion_plan",
            title=f"Promotion Path: {current_level} → {target_level}",
            description=f"Timeline: {timeline} months",
            confidence=0.8,
            priority="high",
            data={"current": current_level, "target": target_level, "timeline": timeline}
        )
    
    def _suggest_side_income(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        skills = data.get("skills", [])
        
        suggestions = []
        if "coding" in skills:
            suggestions.append("Freelance development")
        if "writing" in skills:
            suggestions.append("Content creation")
        
        return self.create_insight(
            insight_type="side_income",
            title="Side Income Options",
            description=f"Consider: {', '.join(suggestions) if suggestions else 'based on your skills'}",
            confidence=0.7,
            priority="medium",
            data={"suggestions": suggestions}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["income_planning", "promotion_strategy", "side_income"],
            "signal_types": ["income_opportunity", "promotion_path", "side_income"]
        }


class DecisionLeverageAdvisorAgent(StrategistAgent):
    """
    Decision Leverage Advisor - Career decisions
    
    Role: Strategist
    Responsibilities: Analyze career decisions, provide strategic advice
    """
    
    def __init__(self):
        super().__init__("decision_leverage_advisor", "Decision Leverage Advisor", "career")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "job_offer":
            return self._evaluate_offer(signal)
        elif signal_type == "career_crossroads":
            return self._analyze_options(signal)
        elif signal_type == "negotiation":
            return self._plan_negotiation(signal)
        
        return None
    
    def _evaluate_offer(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        offer_value = data.get("total_value", 0)
        current_value = data.get("current_value", 0)
        
        increase = (offer_value - current_value) / current_value if current_value > 0 else 0
        
        if increase > 0.2:
            verdict = "Strong offer - recommend accepting"
        elif increase > 0:
            verdict = "Acceptable - negotiate further if possible"
        else:
            verdict = "Below current - decline or counter"
        
        return self.create_insight(
            insight_type="offer_evaluation",
            title="Job Offer Evaluation",
            description=verdict,
            confidence=0.8,
            priority="high",
            data={"offer": offer_value, "current": current_value, "increase": increase}
        )
    
    def _analyze_options(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        options = data.get("options", [])
        
        return self.create_insight(
            insight_type="decision_analysis",
            title="Career Decision Analysis",
            description=f"Options: {', '.join(options)}",
            confidence=0.7,
            priority="high",
            data={"options": options}
        )
    
    def _plan_negotiation(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        target = data.get("target", "")
        
        return self.create_insight(
            insight_type="negotiation_plan",
            title="Negotiation Strategy",
            description=f"Target: {target}",
            confidence=0.75,
            priority="medium",
            data={"target": target}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["offer_evaluation", "decision_analysis", "negotiation"],
            "signal_types": ["job_offer", "career_crossroads", "negotiation"]
        }


# ============== CAREER GOVERNOR (ADDED) ==============

class CareerRiskAdvisorAgent(GovernorAgent):
    """
    Career Risk Advisor - Career risk management
    
    Role: Governor
    Responsibilities: Monitor career risks, ensure job security, detect burnout
    """
    
    def __init__(self):
        super().__init__("career_risk_advisor", "Career Risk Advisor", "career")
        self.risk_threshold = 0.6
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "job_security":
            return self._assess_job_security(signal)
        elif signal_type == "layoff_risk":
            return self._evaluate_layoff_risk(signal)
        elif signal_type == "skill_devaluation":
            return self._check_skill_risk(signal)
        
        return None
    
    def _assess_job_security(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        security_score = data.get("security_score", 0.7)
        
        if security_score < self.risk_threshold:
            return self.create_insight(
                insight_type="risk_alert",
                title="Job Security Warning",
                description=f"Security score: {security_score:.0%} - Consider backup options",
                confidence=0.85,
                priority="critical",
                data={"security_score": security_score}
            )
        
        return self.create_insight(
            insight_type="risk_clear",
            title="Job Security: Good",
            description=f"Security score: {security_score:.0%}",
            confidence=0.85,
            priority="low",
            data={"security_score": security_score}
        )
    
    def _evaluate_layoff_risk(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        company_risk = data.get("company_risk", 0.3)
        personal_performance = data.get("personal_performance", 0.7)
        
        layoff_risk = (company_risk * 0.6) + ((1 - personal_performance) * 0.4)
        
        if layoff_risk > 0.5:
            return self.create_insight(
                insight_type="layoff_risk",
                title="Elevated Layoff Risk",
                description=f"Risk: {layoff_risk:.0%} - Update resume, network actively",
                confidence=0.8,
                priority="high",
                data={"risk": layoff_risk}
            )
        
        return self.create_insight(
            insight_type="layoff_risk_low",
            title="Layoff Risk: Low",
            description=f"Risk: {layoff_risk:.0%} - Continue performing well",
            confidence=0.8,
            priority="low",
            data={"risk": layoff_risk}
        )
    
    def _check_skill_risk(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        skill = data.get("skill", "")
        demand_level = data.get("demand_level", 0.7)
        
        if demand_level < 0.4:
            return self.create_insight(
                insight_type="skill_devaluation",
                title=f"Skill Risk: {skill}",
                description="Low demand - upskill or pivot",
                confidence=0.75,
                priority="high",
                data={"skill": skill, "demand": demand_level}
            )
        
        return self.create_insight(
            insight_type="skill_value",
            title=f"Skill Value: {skill}",
            description=f"Demand: {demand_level:.0%} - Stable",
            confidence=0.75,
            priority="low",
            data={"skill": skill, "demand": demand_level}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "governor",
            "capabilities": ["job_security_assessment", "layoff_risk_evaluation", "skill_devaluation_detection"],
            "signal_types": ["job_security", "layoff_risk", "skill_devaluation"],
            "threshold": self.risk_threshold
        }
