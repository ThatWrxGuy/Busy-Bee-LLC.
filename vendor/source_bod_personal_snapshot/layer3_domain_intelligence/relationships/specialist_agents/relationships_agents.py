"""
Relationships Domain Specialist Agents
Part of BB-DOM-001: Domain Intelligence Expansion Framework

Agents:
1. Partner Relationship Advisor (Strategist) - Romantic relationship guidance
2. Family Dynamics Advisor (Strategist) - Family relationship management
3. Social Network Strategist (Strategist) - Social connections
4. Conflict Resolution Coach (Strategist) - Conflict management
5. Communication Architect (Strategist) - Communication strategies
6. Trust & Alignment Monitor (Governor) - Trust and alignment tracking
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from layer3_domain_intelligence.base_specialist_agent import (
    SpecialistAgent, ObserverAgent, StrategistAgent, GovernorAgent,
    AgentSignal, AgentInsight, AgentRole
)


# ============== RELATIONSHIPS AGENTS ==============

class PartnerRelationshipAdvisorAgent(StrategistAgent):
    """
    Partner Relationship Advisor - Romantic relationship guidance
    
    Role: Strategist
    Responsibilities: Provide relationship advice, plan quality time
    """
    
    def __init__(self):
        super().__init__("partner_relationship_advisor", "Partner Relationship Advisor", "relationships")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "relationship_check":
            return self._check_relationship_health(signal)
        elif signal_type == "quality_time":
            return self._plan_quality_time(signal)
        elif signal_type == "date_idea":
            return self._suggest_date(signal)
        
        return None
    
    def _check_relationship_health(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        satisfaction = data.get("satisfaction", 0.7)
        
        if satisfaction > 0.8:
            return self.create_insight(
                insight_type="relationship_health",
                title="Relationship: Thriving",
                description=f"Satisfaction: {satisfaction:.0%} - Great connection!",
                confidence=0.85,
                priority="low",
                data={"satisfaction": satisfaction}
            )
        elif satisfaction > 0.6:
            return self.create_insight(
                insight_type="relationship_health",
                title="Relationship: Good",
                description=f"Satisfaction: {satisfaction:.0%} - Room for growth",
                confidence=0.8,
                priority="medium",
                data={"satisfaction": satisfaction}
            )
        
        return self.create_insight(
            insight_type="relationship_alert",
            title="Relationship: Needs Attention",
            description=f"Satisfaction: {satisfaction:.0%} - Prioritize quality time and communication",
            confidence=0.85,
            priority="high",
            data={"satisfaction": satisfaction}
        )
    
    def _plan_quality_time(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        frequency = data.get("frequency_per_week", 0)
        
        if frequency < 2:
            return self.create_insight(
                insight_type="quality_time_plan",
                title="Increase Quality Time",
                description="Aim for at least 2 dedicated date nights per week",
                confidence=0.8,
                priority="high",
                data={"frequency": frequency, "recommended": 2}
            )
        
        return self.create_insight(
            insight_type="quality_time_ok",
            title="Quality Time: Good",
            description=f"{frequency} sessions/week - healthy amount",
            confidence=0.8,
            priority="low",
            data={"frequency": frequency}
        )
    
    def _suggest_date(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        budget = data.get("budget", "moderate")
        
        ideas = {
            "low": ["Picnic in park", "Movie night at home", "Cooking together"],
            "moderate": ["Restaurant dinner", "Bowling", "Wine tasting"],
            "high": ["Weekend getaway", "Concert tickets", "Cooking class"]
        }
        
        suggestions = ideas.get(budget, ideas["moderate"])
        
        return self.create_insight(
            insight_type="date_suggestion",
            title="Date Ideas",
            description=f"Budget: {budget} - Try: {suggestions[0]}",
            confidence=0.75,
            priority="low",
            data={"suggestions": suggestions, "budget": budget}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["relationship_health", "quality_time_planning", "date_ideas"],
            "signal_types": ["relationship_check", "quality_time", "date_idea"]
        }


class FamilyDynamicsAdvisorAgent(StrategistAgent):
    """
    Family Dynamics Advisor - Family relationship management
    
    Role: Strategist
    Responsibilities: Manage family relationships, plan family activities
    """
    
    def __init__(self):
        super().__init__("family_dynamics_advisor", "Family Dynamics Advisor", "relationships")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "family_check":
            return self._assess_family_dynamics(signal)
        elif signal_type == "family_activity":
            return self._plan_activity(signal)
        elif signal_type == "family_conflict":
            return self._address_conflict(signal)
        
        return None
    
    def _assess_family_dynamics(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        contact_frequency = data.get("contact_frequency", "weekly")
        
        return self.create_insight(
            insight_type="family_health",
            title="Family Dynamics Assessment",
            description=f"Contact: {contact_frequency}",
            confidence=0.75,
            priority="medium",
            data={"contact": contact_frequency}
        )
    
    def _plan_activity(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        family_members = data.get("family_members", [])
        
        activity = "Family game night" if len(family_members) > 2 else "One-on-one time"
        
        return self.create_insight(
            insight_type="activity_plan",
            title="Family Activity",
            description=f"Recommended: {activity}",
            confidence=0.7,
            priority="medium",
            data={"activity": activity, "members": family_members}
        )
    
    def _address_conflict(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        issue = data.get("issue", "")
        
        return self.create_insight(
            insight_type="conflict_advice",
            title="Family Conflict Resolution",
            description=f"Address with empathy: {issue}",
            confidence=0.7,
            priority="high",
            data={"issue": issue}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["family_assessment", "activity_planning", "conflict_advice"],
            "signal_types": ["family_check", "family_activity", "family_conflict"]
        }


class SocialNetworkStrategistAgent(StrategistAgent):
    """
    Social Network Strategist - Social connections
    
    Role: Strategist
    Responsibilities: Build and maintain social network
    """
    
    def __init__(self):
        super().__init__("social_network_strategist", "Social Network Strategist", "relationships")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "network_health":
            return self._assess_network(signal)
        elif signal_type == "new_connection":
            return self._follow_up_connection(signal)
        elif signal_type == "social_goal":
            return self._set_social_goals(signal)
        
        return None
    
    def _assess_network(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        close_friends = data.get("close_friends", 0)
        acquaintances = data.get("acquaintances", 0)
        
        if close_friends < 3:
            return self.create_insight(
                insight_type="network_alert",
                title="Network Needs Growth",
                description=f"Close friends: {close_friends} - aim for 3-5",
                confidence=0.8,
                priority="high",
                data={"close": close_friends, "acquaintances": acquaintances}
            )
        
        return self.create_insight(
            insight_type="network_healthy",
            title="Social Network: Healthy",
            description=f"Close: {close_friends}, Acquaintances: {acquaintances}",
            confidence=0.8,
            priority="low",
            data={"close": close_friends}
        )
    
    def _follow_up_connection(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        person = data.get("person", "new contact")
        context = data.get("context", "professional")
        
        action = f"Follow up with {person} - {context} connection"
        
        return self.create_insight(
            insight_type="connection_action",
            title="New Connection",
            description=action,
            confidence=0.75,
            priority="medium",
            data={"person": person}
        )
    
    def _set_social_goals(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        goal = data.get("goal", "expand")
        
        goals = {
            "expand": "Add 1 new meaningful connection per month",
            "deepen": "Schedule monthly catch-ups with close friends",
            "maintain": "Weekly social interactions"
        }
        
        return self.create_insight(
            insight_type="social_goal",
            title="Social Goal Set",
            description=goals.get(goal, "Maintain connections"),
            confidence=0.75,
            priority="medium",
            data={"goal": goal}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["network_assessment", "connection_planning", "goal_setting"],
            "signal_types": ["network_health", "new_connection", "social_goal"]
        }


class ConflictResolutionCoachAgent(StrategistAgent):
    """
    Conflict Resolution Coach - Conflict management
    
    Role: Strategist
    Responsibilities: Mediate conflicts, provide resolution strategies
    """
    
    def __init__(self):
        super().__init__("conflict_resolution_coach", "Conflict Resolution Coach", "relationships")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "conflict_emerging":
            return self._identify_conflict(signal)
        elif signal_type == "conflict_active":
            return self._resolve_conflict(signal)
        elif signal_type == "post_conflict":
            return self._facilitate_recovery(signal)
        
        return None
    
    def _identify_conflict(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        parties = data.get("parties", [])
        issue = data.get("issue", "")
        
        return self.create_insight(
            insight_type="conflict_identified",
            title="Conflict Emerging",
            description=f"Between {', '.join(parties)}: {issue}",
            confidence=0.75,
            priority="high",
            data={"parties": parties, "issue": issue}
        )
    
    def _resolve_conflict(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        
        steps = [
            "1. Listen to understand each perspective",
            "2. Find common ground",
            "3. Propose compromise",
            "4. Agree on moving forward"
        ]
        
        return self.create_insight(
            insight_type="resolution_strategy",
            title="Conflict Resolution Steps",
            description=" | ".join(steps),
            confidence=0.8,
            priority="high",
            data={"steps": steps}
        )
    
    def _facilitate_recovery(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        resolved = data.get("resolved", False)
        
        if resolved:
            return self.create_insight(
                insight_type="recovery_plan",
                title="Post-Conflict Recovery",
                description="Schedule positive interaction to rebuild trust",
                confidence=0.8,
                priority="medium",
                data={"resolved": True}
            )
        
        return self.create_insight(
            insight_type="still_working",
            title="Conflict Resolution In Progress",
            description="Continue dialogue - resolution takes time",
            confidence=0.7,
            priority="medium",
            data={"resolved": False}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["conflict_identification", "resolution_planning", "recovery"],
            "signal_types": ["conflict_emerging", "conflict_active", "post_conflict"]
        }


class CommunicationArchitectAgent(StrategistAgent):
    """
    Communication Architect - Communication strategies
    
    Role: Strategist
    Responsibilities: Design communication strategies, improve dialogue
    """
    
    def __init__(self):
        super().__init__("communication_architect", "Communication Architect", "relationships")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "communication_style":
            return self._analyze_style(signal)
        elif signal_type == "difficult_conversation":
            return self._plan_conversation(signal)
        elif signal_type == "feedback":
            return self._structure_feedback(signal)
        
        return None
    
    def _analyze_style(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        style = data.get("style", "direct")
        
        tips = {
            "direct": "Be clear and concise - avoid hints",
            "indirect": "Use context and nuance - be patient",
            "analytical": "Focus on facts - avoid emotional language",
            "expressive": "Show enthusiasm - be expressive"
        }
        
        return self.create_insight(
            insight_type="style_analysis",
            title=f"Communication Style: {style.title()}",
            description=f"Tip: {tips.get(style, 'Find common ground')}",
            confidence=0.75,
            priority="medium",
            data={"style": style}
        )
    
    def _plan_conversation(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        topic = data.get("topic", "")
        
        return self.create_insight(
            insight_type="conversation_plan",
            title=f"Difficult Conversation: {topic}",
            description="Use 'I feel' statements, stay calm, focus on resolution",
            confidence=0.8,
            priority="high",
            data={"topic": topic}
        )
    
    def _structure_feedback(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        recipient = data.get("recipient", "")
        
        framework = "Situation → Behavior → Impact → Request"
        
        return self.create_insight(
            insight_type="feedback_framework",
            title=f"Feedback for {recipient}",
            description=f"Use: {framework}",
            confidence=0.85,
            priority="medium",
            data={"framework": framework}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["style_analysis", "conversation_planning", "feedback_structuring"],
            "signal_types": ["communication_style", "difficult_conversation", "feedback"]
        }


class TrustAlignmentMonitorAgent(GovernorAgent):
    """
    Trust & Alignment Monitor - Trust and alignment tracking
    
    Role: Governor
    Responsibilities: Monitor trust levels, ensure alignment, detect drift
    """
    
    def __init__(self):
        super().__init__("trust_alignment_monitor", "Trust & Alignment Monitor", "relationships")
        self.trust_threshold = 0.6
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "trust_check":
            return self._assess_trust(signal)
        elif signal_type == "alignment_check":
            return self._check_alignment(signal)
        elif signal_type == "trust_violation":
            return self._handle_violation(signal)
        
        return None
    
    def _assess_trust(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        trust_level = data.get("trust_level", 0.7)
        
        if trust_level < self.trust_threshold:
            return self.create_insight(
                insight_type="trust_alert",
                title="Trust Below Threshold",
                description=f"Trust: {trust_level:.0%} - Address issues proactively",
                confidence=0.85,
                priority="critical",
                data={"trust_level": trust_level}
            )
        
        return self.create_insight(
            insight_type="trust_healthy",
            title="Trust: Healthy",
            description=f"Trust: {trust_level:.0%} - Relationship strong",
            confidence=0.85,
            priority="low",
            data={"trust_level": trust_level}
        )
    
    def _check_alignment(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        values_aligned = data.get("values_aligned", True)
        goals_aligned = data.get("goals_aligned", True)
        
        if not values_aligned:
            return self.create_insight(
                insight_type="alignment_issue",
                title="Values Misaligned",
                description="Core values differ - discuss priorities",
                confidence=0.8,
                priority="high",
                data={"values_aligned": False}
            )
        
        if not goals_aligned:
            return self.create_insight(
                insight_type="alignment_issue",
                title="Goals Need Discussion",
                description="Life goals may differ - clarify expectations",
                confidence=0.75,
                priority="medium",
                data={"goals_aligned": False}
            )
        
        return self.create_insight(
            insight_type="alignment_good",
            title="Alignment: Strong",
            description="Values and goals well-aligned",
            confidence=0.8,
            priority="low",
            data={}
        )
    
    def _handle_violation(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        violation = data.get("violation_type", "trust breach")
        
        return self.create_insight(
            insight_type="violation_response",
            title=f"Trust Violation: {violation}",
            description="Acknowledge, discuss impact, rebuild through consistent action",
            confidence=0.8,
            priority="critical",
            data={"violation": violation}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "governor",
            "capabilities": ["trust_assessment", "alignment_monitoring", "violation_response"],
            "signal_types": ["trust_check", "alignment_check", "trust_violation"],
            "threshold": self.trust_threshold
        }
