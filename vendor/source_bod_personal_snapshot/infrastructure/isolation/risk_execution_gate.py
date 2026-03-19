"""
Risk Execution Gate - Layer 5: Risk & Action Isolation
BB-ARCH-ISO-001: Agent & Engine Isolation Architecture

This module implements the execution gate that ensures all real-world actions
require proper approval before execution.

Directive: BB-ARCH-ISO-001
Layer: 5 - Risk & Action Isolation

The system must NEVER autonomously execute:
- Financial transactions
- Legal actions
- Contract commitments
- Medical actions
without explicit human approval.

Execution Pipeline:
Agent Recommendation -> Executive Council -> Risk Evaluation -> Human CEO Approval -> Action Engine
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import uuid
import logging

logger = logging.getLogger(__name__)


class ActionRiskLevel(Enum):
    """Risk levels for actions"""
    LOW = "low"           # Routine operations
    MEDIUM = "medium"     # Moderate risk
    HIGH = "high"        # High risk
    CRITICAL = "critical" # Critical risk - requires human approval


class ActionCategory(Enum):
    """Categories of actions"""
    FINANCIAL = "financial"
    LEGAL = "legal"
    MEDICAL = "medical"
    COMMUNICATION = "communication"
    DATA = "data"
    SYSTEM = "system"


class ApprovalStatus(Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class ApprovalStage(Enum):
    """Stages in the approval pipeline"""
    AGENT_RECOMMENDATION = "agent_recommendation"
    EXECUTIVE_COUNCIL = "executive_council"
    RISK_EVALUATION = "risk_evaluation"
    HUMAN_APPROVAL = "human_approval"
    ACTION_EXECUTION = "action_execution"


@dataclass
class ActionRequest:
    """
    Request for an action to be executed.
    
    Contains all information about the proposed action.
    """
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    agent_domain: str = ""
    action_type: str = ""
    action_category: ActionCategory = ActionCategory.DATA
    risk_level: ActionRiskLevel = ActionRiskLevel.LOW
    title: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    justification: str = ""
    expected_impact: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "agent_domain": self.agent_domain,
            "action_type": self.action_type,
            "action_category": self.action_category.value,
            "risk_level": self.risk_level.value,
            "title": self.title,
            "description": self.description,
            "parameters": self.parameters,
            "justification": self.justification,
            "expected_impact": self.expected_impact,
            "created_at": self.created_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None
        }


@dataclass
class ApprovalRequest:
    """
    Approval request in the execution pipeline.
    
    Tracks the progress through approval stages.
    """
    request: ActionRequest
    current_stage: ApprovalStage = ApprovalStage.AGENT_RECOMMENDATION
    status: ApprovalStatus = ApprovalStatus.PENDING
    
    # Stage-specific data
    executive_council_notes: str = ""
    risk_evaluation: Dict[str, Any] = field(default_factory=dict)
    
    # Approval tracking
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    denied_by: Optional[str] = None
    denied_at: Optional[datetime] = None
    denial_reason: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=1))
    
    def advance_stage(self, stage: ApprovalStage) -> None:
        """Advance to the next stage"""
        self.current_stage = stage
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "current_stage": self.current_stage.value,
            "status": self.status.value,
            "executive_council_notes": self.executive_council_notes,
            "risk_evaluation": self.risk_evaluation,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "denied_by": self.denied_by,
            "denied_at": self.denied_at.isoformat() if self.denied_at else None,
            "denial_reason": self.denial_reason,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }


class RiskEvaluator(ABC):
    """
    Abstract base class for risk evaluation.
    
    Implementations can provide custom risk assessment logic.
    """
    
    @abstractmethod
    def evaluate(self, request: ActionRequest) -> Dict[str, Any]:
        """
        Evaluate the risk of an action request.
        
        Returns a risk evaluation with:
        - risk_score: 0.0 - 1.0
        - risk_factors: List of risk factors
        - recommendations: Mitigation recommendations
        - requires_approval: Boolean
        """
        pass


class DefaultRiskEvaluator(RiskEvaluator):
    """
    Default risk evaluator implementation.
    
    Provides baseline risk evaluation based on action category and parameters.
    """
    
    # Actions that ALWAYS require human approval
    ALWAYS_REQUIRE_APPROVAL = {
        "execute_trade",
        "transfer_funds",
        "sign_contract",
        "send_legal_notice",
        "medical_prescription",
        "medical_procedure"
    }
    
    def evaluate(self, request: ActionRequest) -> Dict[str, Any]:
        """Evaluate risk based on action type and parameters"""
        
        risk_score = 0.0
        risk_factors = []
        recommendations = []
        
        # Check if action always requires approval
        if request.action_type in self.ALWAYS_REQUIRE_APPROVAL:
            risk_score = 1.0
            risk_factors.append(f"Action type '{request.action_type}' requires human approval")
            return {
                "risk_score": risk_score,
                "risk_level": ActionRiskLevel.CRITICAL,
                "risk_factors": risk_factors,
                "recommendations": ["Requires human CEO approval"],
                "requires_approval": True
            }
        
        # Evaluate based on category
        if request.action_category == ActionCategory.FINANCIAL:
            amount = request.parameters.get("amount", 0)
            if amount > 10000:
                risk_score = 0.8
                risk_factors.append(f"High financial amount: ${amount}")
                recommendations.append("Financial transactions over $10,000 require approval")
            elif amount > 1000:
                risk_score = 0.5
                risk_factors.append(f"Moderate financial amount: ${amount}")
            else:
                risk_score = 0.2
                
        elif request.action_category == ActionCategory.LEGAL:
            risk_score = 0.9
            risk_factors.append("Legal action category")
            recommendations.append("All legal actions require human approval")
            
        elif request.action_category == ActionCategory.MEDICAL:
            risk_score = 0.95
            risk_factors.append("Medical action category")
            recommendations.append("All medical actions require human approval")
            
        elif request.action_category == ActionCategory.COMMUNICATION:
            external = request.parameters.get("external", False)
            if external:
                risk_score = 0.4
                risk_factors.append("External communication")
                recommendations.append("External communications should be reviewed")
        
        # Determine if approval is required
        requires_approval = (
            risk_score >= 0.5 or
            request.risk_level in (ActionRiskLevel.HIGH, ActionRiskLevel.CRITICAL)
        )
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = ActionRiskLevel.CRITICAL
        elif risk_score >= 0.5:
            risk_level = ActionRiskLevel.HIGH
        elif risk_score >= 0.25:
            risk_level = ActionRiskLevel.MEDIUM
        else:
            risk_level = ActionRiskLevel.LOW
            
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "requires_approval": requires_approval
        }


class ExecutionGate:
    """
    Execution Gate - Layer 5: Risk & Action Isolation
    
    This is the final gate that controls whether actions can be executed.
    All real-world actions must pass through this gate.
    
    Execution Pipeline:
    1. Agent Recommendation
    2. Executive Council Review
    3. Risk Evaluation
    4. Human CEO Approval (for high-risk actions)
    5. Action Execution
    
    The system must NEVER autonomously execute critical actions
    without explicit human approval.
    """
    
    def __init__(self, risk_evaluator: Optional[RiskEvaluator] = None):
        self._risk_evaluator = risk_evaluator or DefaultRiskEvaluator()
        self._pending_requests: Dict[str, ApprovalRequest] = {}
        self._completed_requests: Dict[str, ApprovalRequest] = {}
        self._lock = threading.RLock()
        
        # Callbacks
        self._on_approval_callbacks: List[Callable[[ApprovalRequest], None]] = []
        self._on_denial_callbacks: List[Callable[[ApprovalRequest], None]] = []
        self._on_execution_callbacks: List[Callable[[ApprovalRequest], None]] = []
        
        # Action executors
        self._executors: Dict[str, Callable] = {}
        
    def register_executor(self, action_type: str, executor: Callable) -> None:
        """Register an executor for an action type"""
        self._executors[action_type] = executor
        logger.info(f"Registered executor for action type: {action_type}")
    
    def submit_request(self, request: ActionRequest) -> ApprovalRequest:
        """
        Submit an action request for approval.
        
        This starts the approval pipeline.
        """
        with self._lock:
            # Evaluate risk
            risk_evaluation = self._risk_evaluator.evaluate(request)
            
            # Create approval request
            approval = ApprovalRequest(
                request=request,
                risk_evaluation=risk_evaluation
            )
            
            # Determine starting stage based on risk
            if risk_evaluation.get("requires_approval"):
                approval.current_stage = ApprovalStage.EXECUTIVE_COUNCIL
            else:
                approval.current_stage = ApprovalStage.RISK_EVALUATION
                
            self._pending_requests[request.request_id] = approval
            
            logger.info(f"Submitted action request: {request.request_id} ({request.action_type})")
            return approval
    
    def advance_to_council(self, request_id: str, notes: str) -> bool:
        """Advance request to executive council review"""
        with self._lock:
            approval = self._pending_requests.get(request_id)
            if not approval:
                return False
                
            approval.executive_council_notes = notes
            approval.advance_stage(ApprovalStage.EXECUTIVE_COUNCIL)
            
            logger.info(f"Advanced request {request_id} to executive council")
            return True
    
    def advance_to_risk_evaluation(self, request_id: str) -> bool:
        """Advance request to risk evaluation"""
        with self._lock:
            approval = self._pending_requests.get(request_id)
            if not approval:
                return False
                
            # Re-evaluate risk
            risk_evaluation = self._risk_evaluator.evaluate(approval.request)
            approval.risk_evaluation = risk_evaluation
            approval.advance_stage(ApprovalStage.RISK_EVALUATION)
            
            logger.info(f"Advanced request {request_id} to risk evaluation")
            return True
    
    def request_human_approval(self, request_id: str) -> ApprovalRequest:
        """
        Request human CEO approval for a high-risk action.
        
        Returns the approval request that needs human action.
        """
        with self._lock:
            approval = self._pending_requests.get(request_id)
            if not approval:
                raise ValueError(f"Request not found: {request_id}")
                
            approval.advance_stage(ApprovalStage.HUMAN_APPROVAL)
            
            logger.info(f"Requesting human approval for {request_id}")
            return approval
    
    def approve(self, request_id: str, approved_by: str) -> bool:
        """
        Approve an action request.
        
        Can be called by:
        - Executive Council (for medium risk)
        - Human CEO (for high risk)
        """
        with self._lock:
            approval = self._pending_requests.get(request_id)
            if not approval:
                return False
                
            approval.status = ApprovalStatus.APPROVED
            approval.approved_by = approved_by
            approval.approved_at = datetime.now()
            approval.advance_stage(ApprovalStage.ACTION_EXECUTION)
            
            # Move to completed
            self._completed_requests[request_id] = approval
            
            # Trigger callbacks
            for callback in self._on_approval_callbacks:
                try:
                    callback(approval)
                except Exception as e:
                    logger.error(f"Approval callback error: {e}")
                    
            logger.info(f"Approved request {request_id} by {approved_by}")
            return True
    
    def deny(self, request_id: str, denied_by: str, reason: str) -> bool:
        """Deny an action request"""
        with self._lock:
            approval = self._pending_requests.get(request_id)
            if not approval:
                return False
                
            approval.status = ApprovalStatus.DENIED
            approval.denied_by = denied_by
            approval.denied_at = datetime.now()
            approval.denial_reason = reason
            
            # Move to completed
            self._completed_requests[request_id] = approval
            
            # Trigger callbacks
            for callback in self._on_denial_callbacks:
                try:
                    callback(approval)
                except Exception as e:
                    logger.error(f"Denial callback error: {e}")
                    
            logger.info(f"Denied request {request_id} by {denied_by}: {reason}")
            return True
    
    def execute(self, request_id: str) -> Any:
        """
        Execute an approved action.
        
        Only executes if the request has been approved.
        """
        with self._lock:
            approval = self._completed_requests.get(request_id)
            if not approval:
                raise ValueError(f"Request not found or not completed: {request_id}")
                
            if approval.status != ApprovalStatus.APPROVED:
                raise PermissionError(f"Request {request_id} is not approved for execution")
                
            # Get executor
            executor = self._executors.get(approval.request.action_type)
            if not executor:
                raise ValueError(f"No executor registered for action type: {approval.request.action_type}")
                
            # Execute
            result = executor(approval.request)
            
            # Trigger execution callbacks
            for callback in self._on_execution_callbacks:
                try:
                    callback(approval)
                except Exception as e:
                    logger.error(f"Execution callback error: {e}")
                    
            logger.info(f"Executed request {request_id}")
            return result
    
    def get_request_status(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get the status of a request"""
        if request_id in self._pending_requests:
            return self._pending_requests[request_id]
        return self._completed_requests.get(request_id)
    
    def get_pending_requests(self, stage: Optional[ApprovalStage] = None) -> List[ApprovalRequest]:
        """Get pending requests, optionally filtered by stage"""
        requests = list(self._pending_requests.values())
        if stage:
            requests = [r for r in requests if r.current_stage == stage]
        return requests
    
    def needs_human_approval(self, request_id: str) -> bool:
        """Check if a request needs human approval"""
        approval = self.get_request_status(request_id)
        if not approval:
            return False
            
        return (
            approval.request.risk_level in (ActionRiskLevel.HIGH, ActionRiskLevel.CRITICAL) or
            approval.risk_evaluation.get("requires_approval", False)
        )
    
    def register_approval_callback(self, callback: Callable[[ApprovalRequest], None]) -> None:
        """Register callback for approval events"""
        self._on_approval_callbacks.append(callback)
    
    def register_denial_callback(self, callback: Callable[[ApprovalRequest], None]) -> None:
        """Register callback for denial events"""
        self._on_denial_callbacks.append(callback)
    
    def register_execution_callback(self, callback: Callable[[ApprovalRequest], None]) -> None:
        """Register callback for execution events"""
        self._on_execution_callbacks.append(callback)


# Global execution gate instance
_global_execution_gate: Optional[ExecutionGate] = None


def get_execution_gate() -> ExecutionGate:
    """Get the global execution gate"""
    global _global_execution_gate
    if _global_execution_gate is None:
        _global_execution_gate = ExecutionGate()
    return _global_execution_gate


def reset_execution_gate() -> None:
    """Reset the global execution gate (for testing)"""
    global _global_execution_gate
    _global_execution_gate = None
