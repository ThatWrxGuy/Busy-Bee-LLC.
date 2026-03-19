"""
Execution Gate - Approves and controls strategy execution
Part of Layer 2: Governance Layer
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class GateStatus(Enum):
    """Status of the execution gate"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class GateStep(Enum):
    """Steps in the execution gate"""
    INITIAL_REVIEW = "initial_review"
    RISK_ASSESSMENT = "risk_assessment"
    RESOURCE_CHECK = "resource_check"
    STAKEHOLDER_APPROVAL = "stakeholder_approval"
    FINAL_APPROVAL = "final_approval"
    EXECUTION = "execution"
    MONITORING = "monitoring"


@dataclass
class ExecutionGate:
    """An execution gate for a strategy"""
    id: str
    strategy_id: str
    domain: str
    status: GateStatus
    current_step: GateStep
    steps_completed: List[GateStep]
    approvals: Dict[str, bool]  # step -> approved
    rejection_reason: Optional[str] = None
    blocked_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class GatePolicy:
    """Policy configuration for execution gates"""
    domain: str
    required_steps: List[GateStep]
    auto_approve_below_risk: float
    requires_ceo_approval_above: float


class ExecutionGateManager:
    """
    Execution Gate controls strategy execution.
    
    Responsibilities:
    - Review strategies before execution
    - Enforce approval workflows
    - Monitor execution
    - Block when necessary
    """
    
    def __init__(self):
        self.gates: List[ExecutionGate] = []
        self.policies: Dict[str, GatePolicy] = {}
        self.execution_results: List[Dict[str, Any]] = []
    
    def add_policy(
        self,
        domain: str,
        required_steps: List[GateStep],
        auto_approve_below_risk: float,
        requires_ceo_approval_above: float
    ):
        """Add a gate policy for a domain"""
        policy = GatePolicy(
            domain=domain,
            required_steps=required_steps,
            auto_approve_below_risk=auto_approve_below_risk,
            requires_ceo_approval_above=requires_ceo_approval_above
        )
        self.policies[domain] = policy
    
    def create_gate(
        self,
        strategy_id: str,
        domain: str,
        risk_score: float
    ) -> ExecutionGate:
        """Create an execution gate for a strategy"""
        policy = self.policies.get(domain)
        
        if policy and risk_score < policy.auto_approve_below_risk:
            # Auto-approve low risk
            gate = ExecutionGate(
                id=f"gate_{len(self.gates) + 1}_{datetime.now().timestamp()}",
                strategy_id=strategy_id,
                domain=domain,
                status=GateStatus.APPROVED,
                current_step=GateStep.FINAL_APPROVAL,
                steps_completed=policy.required_steps,
                approvals={step.value: True for step in policy.required_steps}
            )
        else:
            # Standard gate process
            first_step = policy.required_steps[0] if policy else GateStep.INITIAL_REVIEW
            gate = ExecutionGate(
                id=f"gate_{len(self.gates) + 1}_{datetime.now().timestamp()}",
                strategy_id=strategy_id,
                domain=domain,
                status=GateStatus.PENDING,
                current_step=first_step,
                steps_completed=[],
                approvals={}
            )
        
        self.gates.append(gate)
        return gate
    
    def advance_step(self, gate_id: str, approved: bool, notes: Optional[str] = None) -> Dict[str, Any]:
        """Advance the gate to the next step"""
        gate = next((g for g in self.gates if g.id == gate_id), None)
        
        if not gate:
            return {"error": "Gate not found"}
        
        if gate.status in [GateStatus.REJECTED, GateStatus.BLOCKED, GateStatus.COMPLETED]:
            return {"error": "Gate is not in active state"}
        
        # Record approval
        gate.approvals[gate.current_step.value] = approved
        
        if not approved:
            gate.status = GateStatus.REJECTED
            gate.rejection_reason = notes or "Rejected at " + gate.current_step.value
            gate.updated_at = datetime.now()
            return {
                "gate_id": gate_id,
                "status": "rejected",
                "reason": gate.rejection_reason
            }
        
        # Mark current step complete
        gate.steps_completed.append(gate.current_step)
        
        # Get next step
        policy = self.policies.get(gate.domain)
        if policy:
            try:
                current_idx = policy.required_steps.index(gate.current_step)
                if current_idx + 1 < len(policy.required_steps):
                    gate.current_step = policy.required_steps[current_idx + 1]
                else:
                    # All steps complete
                    gate.status = GateStatus.APPROVED
                    gate.completed_at = datetime.now()
            except ValueError:
                gate.current_step = GateStep.FINAL_APPROVAL
        else:
            # Default: move to next standard step
            next_steps = list(GateStep)
            try:
                current_idx = next_steps.index(gate.current_step)
                if current_idx + 1 < len(next_steps):
                    gate.current_step = next_steps[current_idx + 1]
            except ValueError:
                pass
        
        gate.updated_at = datetime.now()
        
        return {
            "gate_id": gate_id,
            "status": gate.status.value,
            "current_step": gate.current_step.value,
            "steps_completed": [s.value for s in gate.steps_completed]
        }
    
    def block_gate(self, gate_id: str, reason: str) -> Optional[ExecutionGate]:
        """Block a gate"""
        gate = next((g for g in self.gates if g.id == gate_id), None)
        
        if not gate:
            return None
        
        gate.status = GateStatus.BLOCKED
        gate.blocked_reason = reason
        gate.updated_at = datetime.now()
        
        return gate
    
    def unblock_gate(self, gate_id: str) -> Optional[ExecutionGate]:
        """Unblock a gate"""
        gate = next((g for g in self.gates if g.id == gate_id), None)
        
        if not gate or gate.status != GateStatus.BLOCKED:
            return None
        
        gate.status = GateStatus.PENDING
        gate.blocked_reason = None
        gate.updated_at = datetime.now()
        
        return gate
    
    def start_execution(self, gate_id: str) -> Optional[ExecutionGate]:
        """Start execution"""
        gate = next((g for g in self.gates if g.id == gate_id), None)
        
        if not gate or gate.status != GateStatus.APPROVED:
            return None
        
        gate.status = GateStatus.EXECUTING
        gate.current_step = GateStep.EXECUTION
        gate.updated_at = datetime.now()
        
        return gate
    
    def complete_execution(self, gate_id: str, result: Dict[str, Any]) -> Optional[ExecutionGate]:
        """Complete execution with results"""
        gate = next((g for g in self.gates if g.id == gate_id), None)
        
        if not gate or gate.status != GateStatus.EXECUTING:
            return None
        
        gate.status = GateStatus.COMPLETED
        gate.completed_at = datetime.now()
        gate.updated_at = datetime.now()
        
        self.execution_results.append({
            "gate_id": gate_id,
            "strategy_id": gate.strategy_id,
            "result": result,
            "completed_at": datetime.now().isoformat()
        })
        
        return gate
    
    def get_gate(self, gate_id: str) -> Optional[ExecutionGate]:
        """Get a gate by ID"""
        return next((g for g in self.gates if g.id == gate_id), None)
    
    def get_pending_gates(self) -> List[ExecutionGate]:
        """Get all pending gates"""
        return [g for g in self.gates if g.status == GateStatus.PENDING]
    
    def get_gate_summary(self) -> Dict[str, Any]:
        """Get gate summary"""
        return {
            "total_gates": len(self.gates),
            "by_status": {
                "pending": len([g for g in self.gates if g.status == GateStatus.PENDING]),
                "approved": len([g for g in self.gates if g.status == GateStatus.APPROVED]),
                "rejected": len([g for g in self.gates if g.status == GateStatus.REJECTED]),
                "blocked": len([g for g in self.gates if g.status == GateStatus.BLOCKED]),
                "executing": len([g for g in self.gates if g.status == GateStatus.EXECUTING]),
                "completed": len([g for g in self.gates if g.status == GateStatus.COMPLETED])
            }
        }
