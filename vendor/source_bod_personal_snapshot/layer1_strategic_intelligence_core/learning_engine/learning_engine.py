"""
Learning Engine - Continuous improvement of decision quality
Part of Layer 1: Strategic Intelligence Core
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class Lesson:
    """A learned lesson from past decisions"""
    id: str
    title: str
    description: str
    category: str  # success, failure, observation
    domain: str
    key_insight: str
    action_items: List[str]
    created_at: datetime
    times_applied: int = 0
    success_rate: float = 0.0


@dataclass
class DecisionRecord:
    """Record of a decision made"""
    id: str
    decision_type: str
    context: Dict[str, Any]
    chosen_option: str
    alternative_options: List[str]
    outcome: Optional[str]  # success, failure, partial
    outcome_details: Dict[str, Any]
    lessons_learned: List[str]
    decided_at: datetime
    evaluated_at: Optional[datetime] = None


class LearningEngine:
    """
    Learning Engine enables continuous improvement of decision quality.
    
    Responsibilities:
    - Record decisions and outcomes
    - Extract lessons learned
    - Improve strategy recommendations
    """
    
    def __init__(self):
        self.lessons: List[Lesson] = []
        self.decisions: List[DecisionRecord] = []
        self.performance_by_domain: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"successes": 0, "failures": 0, "total": 0}
        )
    
    def record_decision(
        self,
        decision_type: str,
        context: Dict[str, Any],
        chosen_option: str,
        alternative_options: List[str],
        domain: str
    ) -> DecisionRecord:
        """Record a decision for future learning"""
        decision = DecisionRecord(
            id=f"dec_{len(self.decisions) + 1}_{datetime.now().timestamp()}",
            decision_type=decision_type,
            context=context,
            chosen_option=chosen_option,
            alternative_options=alternative_options,
            outcome=None,
            outcome_details={},
            lessons_learned=[],
            decided_at=datetime.now()
        )
        self.decisions.append(decision)
        
        # Update domain stats
        self.performance_by_domain[domain]["total"] += 1
        
        return decision
    
    def evaluate_decision(
        self,
        decision_id: str,
        outcome: str,
        outcome_details: Dict[str, Any]
    ) -> List[Lesson]:
        """Evaluate a decision and extract lessons"""
        decision = next((d for d in self.decisions if d.id == decision_id), None)
        
        if not decision:
            return []
        
        decision.outcome = outcome
        decision.outcome_details = outcome_details
        decision.evaluated_at = datetime.now()
        
        # Determine domain from context
        domain = decision.context.get("domain", "general")
        
        # Update performance stats
        if outcome == "success":
            self.performance_by_domain[domain]["successes"] += 1
        elif outcome == "failure":
            self.performance_by_domain[domain]["failures"] += 1
        
        # Generate lessons
        lessons = self._extract_lessons(decision)
        
        for lesson in lessons:
            self.lessons.append(lesson)
            decision.lessons_learned.append(lesson.id)
        
        return lessons
    
    def _extract_lessons(self, decision: DecisionRecord) -> List[Lesson]:
        """Extract lessons from a decision"""
        lessons = []
        
        if decision.outcome == "success":
            lesson = Lesson(
                id=f"lesson_{len(self.lessons) + 1}_{datetime.now().timestamp()}",
                title=f"Success: {decision.chosen_option}",
                description=f"Decision '{decision.decision_type}' with option '{decision.chosen_option}' succeeded.",
                category="success",
                domain=decision.context.get("domain", "general"),
                key_insight=f"The chosen option '{decision.chosen_option}' was effective.",
                action_items=["Document what worked", "Apply to similar contexts"],
                created_at=datetime.now()
            )
            lessons.append(lesson)
        
        elif decision.outcome == "failure":
            lesson = Lesson(
                id=f"lesson_{len(self.lessons) + 1}_{datetime.now().timestamp()}",
                title=f"Failure: {decision.chosen_option}",
                description=f"Decision '{decision.decision_type}' with option '{decision.chosen_option}' failed.",
                category="failure",
                domain=decision.context.get("domain", "general"),
                key_insight=f"The chosen option '{decision.chosen_option}' was not effective. Alternatives: {decision.alternative_options}",
                action_items=["Analyze why it failed", "Consider alternatives in future"],
                created_at=datetime.now()
            )
            lessons.append(lesson)
        
        return lessons
    
    def get_relevant_lessons(self, domain: str, limit: int = 5) -> List[Lesson]:
        """Get relevant lessons for a domain"""
        domain_lessons = [l for l in self.lessons if l.domain == domain]
        # Sort by success rate and times applied
        sorted_lessons = sorted(
            domain_lessons,
            key=lambda l: (l.success_rate, l.times_applied),
            reverse=True
        )
        return sorted_lessons[:limit]
    
    def get_performance_stats(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics"""
        if domain:
            stats = self.performance_by_domain.get(domain, {"successes": 0, "failures": 0, "total": 0})
            total = stats["total"]
            return {
                "domain": domain,
                "total_decisions": total,
                "successes": stats["successes"],
                "failures": stats["failures"],
                "success_rate": stats["successes"] / total if total > 0 else 0.0
            }
        
        return {
            domain: {
                "total": s["total"],
                "successes": s["successes"],
                "failures": s["failures"],
                "success_rate": s["successes"] / s["total"] if s["total"] > 0 else 0.0
            }
            for domain, s in self.performance_by_domain.items()
        }
    
    def apply_lesson(self, lesson_id: str) -> bool:
        """Mark a lesson as applied"""
        for lesson in self.lessons:
            if lesson.id == lesson_id:
                lesson.times_applied += 1
                return True
        return False
