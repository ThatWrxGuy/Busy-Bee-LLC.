"""
Intelligence Domain Specialist Agents
Part of BB-DOM-001: Domain Intelligence Expansion Framework

Agents:
1. Knowledge Architect (Strategist) - Knowledge management
2. Decision Intelligence Analyst (Strategist) - Decision support
3. Research Strategist (Strategist) - Research planning
4. Learning Engineer (Strategist) - Learning optimization
5. Creativity Catalyst (Strategist) - Creative thinking
6. Signal Fusion Analyst (Observer) - Signal integration
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from layer3_domain_intelligence.base_specialist_agent import (
    SpecialistAgent, ObserverAgent, StrategistAgent, GovernorAgent,
    AgentSignal, AgentInsight, AgentRole
)


# ============== INTELLIGENCE AGENTS ==============

class KnowledgeArchitectAgent(StrategistAgent):
    """
    Knowledge Architect - Knowledge management
    
    Role: Strategist
    Responsibilities: Organize knowledge, design knowledge structures
    """
    
    def __init__(self):
        super().__init__("knowledge_architect", "Knowledge Architect", "intelligence")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "new_knowledge":
            return self._organize_knowledge(signal)
        elif signal_type == "knowledge_gap":
            return self._identify_gaps(signal)
        elif signal_type == "knowledge_review":
            return self._review_structure(signal)
        
        return None
    
    def _organize_knowledge(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        topic = data.get("topic", "")
        
        return self.create_insight(
            insight_type="organization_plan",
            title=f"Knowledge Structure: {topic}",
            description=f"Create framework for organizing {topic} knowledge",
            confidence=0.8,
            priority="medium",
            data={"topic": topic}
        )
    
    def _identify_gaps(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        domain = data.get("domain", "")
        gaps = data.get("gaps", [])
        
        return self.create_insight(
            insight_type="gap_identification",
            title=f"Knowledge Gaps: {domain}",
            description=f"Gaps identified: {', '.join(gaps[:3])}",
            confidence=0.75,
            priority="high",
            data={"domain": domain, "gaps": gaps}
        )
    
    def _review_structure(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        last_review = data.get("months_since_review", 0)
        
        if last_review > 6:
            return self.create_insight(
                insight_type="review_needed",
                title="Knowledge Review Due",
                description=f"Last review: {last_review} months ago",
                confidence=0.8,
                priority="medium",
                data={"months": last_review}
            )
        
        return self.create_insight(
            insight_type="review_current",
            title="Knowledge Structure Current",
            description="Recent review - structure up to date",
            confidence=0.8,
            priority="low",
            data={}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["knowledge_organization", "gap_identification", "structure_design"],
            "signal_types": ["new_knowledge", "knowledge_gap", "knowledge_review"]
        }


class DecisionIntelligenceAnalystAgent(StrategistAgent):
    """
    Decision Intelligence Analyst - Decision support
    
    Role: Strategist
    Responsibilities: Analyze decisions, provide frameworks, evaluate outcomes
    """
    
    def __init__(self):
        super().__init__("decision_intelligence_analyst", "Decision Intelligence Analyst", "intelligence")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "decision_needed":
            return self._analyze_decision(signal)
        elif signal_type == "decision_made":
            return self._track_decision(signal)
        elif signal_type == "decision_outcome":
            return self._evaluate_outcome(signal)
        
        return None
    
    def _analyze_decision(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        decision = data.get("decision", "")
        options = data.get("options", [])
        
        framework = "Decision Matrix: Impact × Probability × Reversibility"
        
        return self.create_insight(
            insight_type="decision_framework",
            title=f"Decision: {decision}",
            description=f"Options: {', '.join(options[:3])} | Framework: {framework}",
            confidence=0.8,
            priority="high",
            data={"decision": decision, "options": options}
        )
    
    def _track_decision(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        decision = data.get("decision", "")
        
        return self.create_insight(
            insight_type="decision_tracked",
            title=f"Decision Tracked: {decision}",
            description="Monitoring for outcome evaluation",
            confidence=0.9,
            priority="low",
            data={"decision": decision}
        )
    
    def _evaluate_outcome(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        decision = data.get("decision", "")
        outcome = data.get("outcome", "")
        expected = data.get("expected", "")
        
        if outcome == expected:
            verdict = "Outcome as expected"
        else:
            verdict = f"Outcome differs: expected {expected}, got {outcome}"
        
        return self.create_insight(
            insight_type="outcome_evaluation",
            title=f"Decision Outcome: {decision}",
            description=verdict,
            confidence=0.85,
            priority="medium",
            data={"decision": decision, "outcome": outcome}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["decision_analysis", "framework_provision", "outcome_tracking"],
            "signal_types": ["decision_needed", "decision_made", "decision_outcome"]
        }


class ResearchStrategistAgent(StrategistAgent):
    """
    Research Strategist - Research planning
    
    Role: Strategist
    Responsibilities: Plan research, identify sources, structure inquiries
    """
    
    def __init__(self):
        super().__init__("research_strategist", "Research Strategist", "intelligence")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "research_question":
            return self._plan_research(signal)
        elif signal_type == "source_needed":
            return self._identify_sources(signal)
        elif signal_type == "research_progress":
            return self._track_progress(signal)
        
        return None
    
    def _plan_research(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        question = data.get("question", "")
        
        return self.create_insight(
            insight_type="research_plan",
            title=f"Research: {question}",
            description="Define hypothesis → Gather data → Analyze → Conclude",
            confidence=0.8,
            priority="high",
            data={"question": question}
        )
    
    def _identify_sources(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        topic = data.get("topic", "")
        
        sources = [
            "Academic databases (Google Scholar)",
            "Industry reports",
            "Expert interviews",
            "Primary research"
        ]
        
        return self.create_insight(
            insight_type="source_identification",
            title=f"Sources for: {topic}",
            description=f"Recommended: {', '.join(sources[:2])}",
            confidence=0.75,
            priority="medium",
            data={"sources": sources}
        )
    
    def _track_progress(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        progress = data.get("progress_pct", 0)
        
        return self.create_insight(
            insight_type="progress_tracking",
            title="Research Progress",
            description=f"Complete: {progress:.0%}",
            confidence=0.9,
            priority="low",
            data={"progress": progress}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["research_planning", "source_identification", "progress_tracking"],
            "signal_types": ["research_question", "source_needed", "research_progress"]
        }


class LearningEngineerAgent(StrategistAgent):
    """
    Learning Engineer - Learning optimization
    
    Role: Strategist
    Responsibilities: Optimize learning, design learning paths
    """
    
    def __init__(self):
        super().__init__("learning_engineer", "Learning Engineer", "intelligence")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "learning_goal":
            return self._design_path(signal)
        elif signal_type == "learning_method":
            return self._optimize_method(signal)
        elif signal_type == "learning_blocker":
            return self._address_blocker(signal)
        
        return None
    
    def _design_path(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        topic = data.get("topic", "")
        level = data.get("current_level", "beginner")
        
        return self.create_insight(
            insight_type="learning_path",
            title=f"Learning Path: {topic}",
            description=f"From {level} → intermediate → advanced",
            confidence=0.8,
            priority="high",
            data={"topic": topic, "level": level}
        )
    
    def _optimize_method(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        topic = data.get("topic", "")
        learning_style = data.get("style", "visual")
        
        methods = {
            "visual": "Diagrams, videos, charts",
            "auditory": "Podcasts, lectures, discussions",
            "kinesthetic": "Projects, hands-on practice",
            "reading": "Books, articles, notes"
        }
        
        return self.create_insight(
            insight_type="method_optimization",
            title=f"Learning Method: {learning_style.title()}",
            description=f"For {topic}: {methods.get(learning_style, methods['reading'])}",
            confidence=0.75,
            priority="medium",
            data={"style": learning_style}
        )
    
    def _address_blocker(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        blocker = data.get("blocker", "time")
        
        solutions = {
            "time": "Block dedicated learning time",
            "motivation": "Set micro-goals with rewards",
            "understanding": "Find alternative explanations",
            "resources": "Seek different learning materials"
        }
        
        return self.create_insight(
            insight_type="blocker_solution",
            title=f"Learning Blocker: {blocker}",
            description=solutions.get(blocker, "Break down into smaller steps"),
            confidence=0.7,
            priority="high",
            data={"blocker": blocker}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["path_design", "method_optimization", "blocker_resolution"],
            "signal_types": ["learning_goal", "learning_method", "learning_blocker"]
        }


class CreativityCatalystAgent(StrategistAgent):
    """
    Creativity Catalyst - Creative thinking
    
    Role: Strategist
    Responsibilities: Stimulate creativity, generate ideas, overcome blocks
    """
    
    def __init__(self):
        super().__init__("creativity_catalyst", "Creativity Catalyst", "intelligence")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "creative_block":
            return self._unblock_creativity(signal)
        elif signal_type == "ideation":
            return self._generate_ideas(signal)
        elif signal_type == "innovation":
            return self._foster_innovation(signal)
        
        return None
    
    def _unblock_creativity(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        
        techniques = [
            "Take a walk",
            "Change environment",
            "Free writing for 10 minutes",
            "Look at unrelated creative work"
        ]
        
        return self.create_insight(
            insight_type="unblock_technique",
            title="Creative Block",
            description="Try: " + techniques[0],
            confidence=0.75,
            priority="high",
            data={"techniques": techniques}
        )
    
    def _generate_ideas(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        problem = data.get("problem", "")
        
        return self.create_insight(
            insight_type="ideation",
            title=f"Ideation: {problem}",
            description="Use SCAMPER: Substitute, Combine, Adapt, Modify, Put, Eliminate, Reverse",
            confidence=0.7,
            priority="medium",
            data={"problem": problem}
        )
    
    def _foster_innovation(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        
        return self.create_insight(
            insight_type="innovation_foster",
            title="Innovation Opportunities",
            description="Cross-pollinate ideas from other fields",
            confidence=0.7,
            priority="medium",
            data={}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "strategist",
            "capabilities": ["creative_unblocking", "idea_generation", "innovation_fostering"],
            "signal_types": ["creative_block", "ideation", "innovation"]
        }


class SignalFusionAnalystAgent(ObserverAgent):
    """
    Signal Fusion Analyst - Signal integration
    
    Role: Observer
    Responsibilities: Integrate signals, find patterns, synthesize insights
    """
    
    def __init__(self):
        super().__init__("signal_fusion_analyst", "Signal Fusion Analyst", "intelligence")
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "multiple_signals":
            return self._fuse_signals(signal)
        elif signal_type == "pattern_detected":
            return self._analyze_pattern(signal)
        elif signal_type == "synthesis_needed":
            return self._synthesize(signal)
        
        return None
    
    def _fuse_signals(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        signal_count = data.get("signal_count", 0)
        
        return self.create_insight(
            insight_type="signal_fusion",
            title=f"Fusing {signal_count} Signals",
            description="Combining signals for higher confidence insight",
            confidence=0.8,
            priority="medium",
            data={"count": signal_count}
        )
    
    def _analyze_pattern(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        pattern = data.get("pattern", "")
        significance = data.get("significance", 0.5)
        
        return self.create_insight(
            insight_type="pattern_analysis",
            title=f"Pattern: {pattern}",
            description=f"Significance: {significance:.0%}",
            confidence=0.75,
            priority="high" if significance > 0.7 else "medium",
            data={"pattern": pattern, "significance": significance}
        )
    
    def _synthesize(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        sources = data.get("sources", [])
        
        return self.create_insight(
            insight_type="synthesis",
            title="Insight Synthesis",
            description=f"Synthesized from {len(sources)} sources",
            confidence=0.85,
            priority="medium",
            data={"sources": sources}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "observer",
            "capabilities": ["signal_integration", "pattern_detection", "insight_synthesis"],
            "signal_types": ["multiple_signals", "pattern_detected", "synthesis_needed"]
        }


# ============== INTELLIGENCE GOVERNOR (ADDED) ==============

class CognitiveBiasMonitorAgent(GovernorAgent):
    """
    Cognitive Bias Monitor - Decision quality assurance
    
    Role: Governor
    Responsibilities: Detect cognitive biases, ensure sound reasoning, maintain decision quality
    """
    
    def __init__(self):
        super().__init__("cognitive_bias_monitor", "Cognitive Bias Monitor", "intelligence")
        self.biases_to_monitor = [
            "confirmation_bias",
            "availability_bias",
            "anchoring_bias",
            "overconfidence",
            "loss_aversion"
        ]
    
    def process(self, signal: AgentSignal) -> Optional[AgentInsight]:
        signal_type = signal.signal_type
        
        if signal_type == "decision_analysis":
            return self._analyze_decision_bias(signal)
        elif signal_type == "reasoning_pattern":
            return self._detect_bias_pattern(signal)
        elif signal_type == "belief_update":
            return self._check_belief_update(signal)
        
        return None
    
    def _analyze_decision_bias(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        decision = data.get("decision", "")
        biases_detected = data.get("biases", [])
        
        if biases_detected:
            return self.create_insight(
                insight_type="bias_detected",
                title=f"Bias in Decision: {decision}",
                description=f"Detected: {', '.join(biases_detected[:2])}",
                confidence=0.8,
                priority="high",
                data={"decision": decision, "biases": biases_detected}
            )
        
        return self.create_insight(
            insight_type="bias_clear",
            title=f"Decision Quality: {decision}",
            description="No significant biases detected",
            confidence=0.8,
            priority="low",
            data={"decision": decision}
        )
    
    def _detect_bias_pattern(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        bias_type = data.get("bias_type", "")
        frequency = data.get("frequency", 0)
        
        if frequency > 0.3:
            return self.create_insight(
                insight_type="bias_pattern",
                title=f"Recurring Bias: {bias_type}",
                description=f"Detected in {frequency:.0%} of recent decisions",
                confidence=0.85,
                priority="high",
                data={"bias": bias_type, "frequency": frequency}
            )
        
        return self.create_insight(
            insight_type="bias_pattern_clear",
            title="No Recurring Biases",
            description="Decision patterns appear sound",
            confidence=0.8,
            priority="low",
            data={}
        )
    
    def _check_belief_update(self, signal: AgentSignal) -> AgentInsight:
        data = signal.data
        belief = data.get("belief", "")
        evidence_considered = data.get("evidence_considered", False)
        
        if not evidence_considered:
            return self.create_insight(
                insight_type="update_warning",
                title=f"Belief Update: {belief}",
                description="Consider new evidence before updating belief",
                confidence=0.75,
                priority="medium",
                data={"belief": belief, "evidence": False}
            )
        
        return self.create_insight(
            insight_type="update_good",
            title=f"Belief Update: {belief}",
            description="Evidence-based belief update",
            confidence=0.85,
            priority="low",
            data={"belief": belief, "evidence": True}
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "role": "governor",
            "capabilities": ["bias_detection", "reasoning_audit", "decision_quality_assurance"],
            "signal_types": ["decision_analysis", "reasoning_pattern", "belief_update"],
            "biases_monitored": self.biases_to_monitor
        }
