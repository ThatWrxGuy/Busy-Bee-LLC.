"""
Executive Council - Strategic coordination and decision-making
Part of Layer 2: Governance Layer
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DecisionPriority(Enum):
    """Priority levels for decisions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DecisionStatus(Enum):
    """Status of a decision"""
    PENDING = "pending"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


@dataclass
class CouncilMember:
    """A member of the Executive Council"""
    id: str
    name: str
    role: str  # Chief Officer title
    domain: str
    vote_weight: float = 1.0


@dataclass
class CouncilDecision:
    """A decision made by the Executive Council"""
    id: str
    title: str
    description: str
    domain: str
    priority: DecisionPriority
    status: DecisionStatus
    proponent: str  # Who proposed it
    votes: Dict[str, str]  # member_id -> vote (approve/reject/abstain)
    discussion_points: List[str]
    conditions: List[str]  # Conditions for approval
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


class ExecutiveCouncil:
    """
    Executive Council provides strategic coordination.
    
    Responsibilities:
    - Coordinate between domains
    - Make strategic decisions
    - Resolve conflicts
    - Approve capital allocation
    """
    
    def __init__(self):
        self.members: List[CouncilMember] = []
        self.decisions: List[CouncilDecision] = []
        self.pending_items: List[Dict[str, Any]] = []
    
    def add_member(self, member_id: str, name: str, role: str, domain: str, vote_weight: float = 1.0):
        """Add a member to the Executive Council"""
        member = CouncilMember(
            id=member_id,
            name=name,
            role=role,
            domain=domain,
            vote_weight=vote_weight
        )
        self.members.append(member)
    
    def submit_decision(
        self,
        title: str,
        description: str,
        domain: str,
        priority: DecisionPriority,
        proponent: str,
        conditions: Optional[List[str]] = None
    ) -> CouncilDecision:
        """Submit a decision for Council review"""
        decision = CouncilDecision(
            id=f"council_{len(self.decisions) + 1}_{datetime.now().timestamp()}",
            title=title,
            description=description,
            domain=domain,
            priority=priority,
            status=DecisionStatus.PENDING,
            proponent=proponent,
            votes={},
            discussion_points=[],
            conditions=conditions or [],
            created_at=datetime.now()
        )
        self.decisions.append(decision)
        return decision
    
    def cast_vote(self, decision_id: str, member_id: str, vote: str) -> bool:
        """Cast a vote on a decision"""
        decision = next((d for d in self.decisions if d.id == decision_id), None)
        member = next((m for m in self.members if m.id == member_id), None)
        
        if not decision or not member:
            return False
        
        if vote not in ["approve", "reject", "abstain"]:
            return False
        
        decision.votes[member_id] = vote
        return True
    
    def finalize_decision(self, decision_id: str) -> Dict[str, Any]:
        """Finalize a decision based on votes"""
        decision = next((d for d in self.decisions if d.id == decision_id), None)
        
        if not decision:
            return {"error": "Decision not found"}
        
        # Calculate weighted votes
        weighted_approves = 0
        weighted_rejects = 0
        
        for member_id, vote in decision.votes.items():
            member = next((m for m in self.members if m.id == member_id), None)
            if member:
                if vote == "approve":
                    weighted_approves += member.vote_weight
                elif vote == "reject":
                    weighted_rejects += member.vote_weight
        
        # Determine outcome
        total_weight = sum(m.vote_weight for m in self.members)
        approve_ratio = weighted_approves / total_weight if total_weight > 0 else 0
        
        if approve_ratio >= 0.5:
            decision.status = DecisionStatus.APPROVED
            decision.approved_at = datetime.now()
        else:
            decision.status = DecisionStatus.REJECTED
            decision.rejected_at = datetime.now()
        
        return {
            "decision_id": decision_id,
            "status": decision.status.value,
            "approve_weight": weighted_approves,
            "reject_weight": weighted_rejects,
            "approve_ratio": approve_ratio,
            "finalized_at": datetime.now().isoformat()
        }
    
    def add_discussion_point(self, decision_id: str, point: str) -> bool:
        """Add a discussion point to a decision"""
        decision = next((d for d in self.decisions if d.id == decision_id), None)
        
        if not decision:
            return False
        
        decision.discussion_points.append(point)
        return True
    
    def get_pending_decisions(self) -> List[CouncilDecision]:
        """Get all pending decisions"""
        return [d for d in self.decisions if d.status == DecisionStatus.PENDING]
    
    def get_decisions_by_domain(self, domain: str) -> List[CouncilDecision]:
        """Get all decisions for a domain"""
        return [d for d in self.decisions if d.domain == domain]
    
    def get_council_stats(self) -> Dict[str, Any]:
        """Get Council statistics"""
        return {
            "total_members": len(self.members),
            "total_decisions": len(self.decisions),
            "pending": len(self.get_pending_decisions()),
            "approved": len([d for d in self.decisions if d.status == DecisionStatus.APPROVED]),
            "rejected": len([d for d in self.decisions if d.status == DecisionStatus.REJECTED]),
            "members": [
                {"id": m.id, "name": m.name, "role": m.role, "domain": m.domain}
                for m in self.members
            ]
        }
