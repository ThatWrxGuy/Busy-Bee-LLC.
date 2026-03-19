"""
Capital Deployment Coordinator - Manages capital allocation
Part of Layer 2: Governance Layer
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AllocationStatus(Enum):
    """Status of capital allocation"""
    PROPOSED = "proposed"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    RETURNED = "returned"
    FAILED = "failed"


@dataclass
class CapitalAllocation:
    """A capital allocation"""
    id: str
    domain: str
    purpose: str
    amount: float
    currency: str = "USD"
    status: AllocationStatus = AllocationStatus.PROPOSED
    expected_return: Optional[float] = None
    actual_return: Optional[float] = None
    risk_level: str = "medium"
    timeline_months: int = 12
    deployed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CapitalBudget:
    """Capital budget for a period"""
    id: str
    period: str  # e.g., "2024-Q1"
    total_budget: float
    allocated: float = 0.0
    reserved: float = 0.0
    available: float = 0.0
    allocations: List[str] = field(default_factory=list)  # allocation IDs


class CapitalDeploymentCoordinator:
    """
    Capital Deployment Coordinator manages capital allocation.
    
    Responsibilities:
    - Track capital budgets
    - Allocate capital to domains
    - Monitor returns
    - Rebalance portfolios
    """
    
    def __init__(self, total_capital: float = 0.0):
        self.total_capital = total_capital
        self.allocations: List[CapitalAllocation] = []
        self.budgets: List[CapitalBudget] = []
        self.allocation_history: List[Dict[str, Any]] = []
    
    def set_total_capital(self, amount: float):
        """Set total available capital"""
        self.total_capital = amount
    
    def create_budget(self, period: str, total_budget: float) -> CapitalBudget:
        """Create a new budget period"""
        budget = CapitalBudget(
            id=f"budget_{len(self.budgets) + 1}_{datetime.now().timestamp()}",
            period=period,
            total_budget=total_budget,
            available=total_budget
        )
        self.budgets.append(budget)
        return budget
    
    def propose_allocation(
        self,
        domain: str,
        purpose: str,
        amount: float,
        expected_return: Optional[float] = None,
        risk_level: str = "medium",
        timeline_months: int = 12
    ) -> Optional[CapitalAllocation]:
        """Propose a capital allocation"""
        # Check available capital
        available = self.get_available_capital()
        
        if amount > available:
            return None
        
        allocation = CapitalAllocation(
            id=f"alloc_{len(self.allocations) + 1}_{datetime.now().timestamp()}",
            domain=domain,
            purpose=purpose,
            amount=amount,
            expected_return=expected_return,
            risk_level=risk_level,
            timeline_months=timeline_months
        )
        
        self.allocations.append(allocation)
        return allocation
    
    def approve_allocation(self, allocation_id: str) -> Optional[CapitalAllocation]:
        """Approve a capital allocation"""
        allocation = next((a for a in self.allocations if a.id == allocation_id), None)
        
        if not allocation:
            return None
        
        if allocation.status != AllocationStatus.PROPOSED:
            return None
        
        allocation.status = AllocationStatus.APPROVED
        
        self.allocation_history.append({
            "allocation_id": allocation_id,
            "action": "approved",
            "timestamp": datetime.now().isoformat()
        })
        
        return allocation
    
    def deploy_allocation(self, allocation_id: str) -> Optional[CapitalAllocation]:
        """Deploy approved capital"""
        allocation = next((a for a in self.allocations if a.id == allocation_id), None)
        
        if not allocation or allocation.status != AllocationStatus.APPROVED:
            return None
        
        allocation.status = AllocationStatus.DEPLOYED
        allocation.deployed_at = datetime.now()
        
        self.allocation_history.append({
            "allocation_id": allocation_id,
            "action": "deployed",
            "timestamp": datetime.now().isoformat()
        })
        
        return allocation
    
    def record_return(self, allocation_id: str, actual_return: float) -> Optional[CapitalAllocation]:
        """Record actual return on allocation"""
        allocation = next((a for a in self.allocations if a.id == allocation_id), None)
        
        if not allocation or allocation.status != AllocationStatus.DEPLOYED:
            return None
        
        allocation.actual_return = actual_return
        
        if actual_return > 0:
            allocation.status = AllocationStatus.RETURNED
        
        self.allocation_history.append({
            "allocation_id": allocation_id,
            "action": "return_recorded",
            "actual_return": actual_return,
            "timestamp": datetime.now().isoformat()
        })
        
        return allocation
    
    def get_available_capital(self) -> float:
        """Get currently available capital"""
        allocated = sum(
            a.amount for a in self.allocations 
            if a.status in [AllocationStatus.APPROVED, AllocationStatus.DEPLOYED]
        )
        return self.total_capital - allocated
    
    def get_domain_allocation(self, domain: str) -> Dict[str, Any]:
        """Get allocation summary for a domain"""
        domain_allocations = [a for a in self.allocations if a.domain == domain]
        
        return {
            "domain": domain,
            "total_allocated": sum(a.amount for a in domain_allocations),
            "deployed": sum(a.amount for a in domain_allocations if a.status == AllocationStatus.DEPLOYED),
            "pending": len([a for a in domain_allocations if a.status == AllocationStatus.PROPOSED]),
            "approved": len([a for a in domain_allocations if a.status == AllocationStatus.APPROVED]),
            "allocations": [
                {
                    "id": a.id,
                    "purpose": a.purpose,
                    "amount": a.amount,
                    "status": a.status.value,
                    "expected_return": a.expected_return,
                    "actual_return": a.actual_return
                }
                for a in domain_allocations
            ]
        }
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get overall portfolio summary"""
        total_allocated = sum(a.amount for a in self.allocations)
        total_deployed = sum(a.amount for a in self.allocations if a.status == AllocationStatus.DEPLOYED)
        total_returned = sum(
            a.actual_return for a in self.allocations 
            if a.actual_return is not None
        )
        
        # By domain
        by_domain = {}
        for a in self.allocations:
            if a.domain not in by_domain:
                by_domain[a.domain] = {"allocated": 0, "deployed": 0}
            by_domain[a.domain]["allocated"] += a.amount
            if a.status == AllocationStatus.DEPLOYED:
                by_domain[a.domain]["deployed"] += a.amount
        
        return {
            "total_capital": self.total_capital,
            "available": self.get_available_capital(),
            "total_allocated": total_allocated,
            "total_deployed": total_deployed,
            "total_returned": total_returned,
            "roi": (total_returned / total_deployed * 100) if total_deployed > 0 else 0,
            "by_domain": by_domain,
            "summary_generated_at": datetime.now().isoformat()
        }
