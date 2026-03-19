"""
Priority Router - Routes and prioritizes tasks across domains
Part of Layer 2: Governance Layer
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Priority(Enum):
    """Priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskStatus(Enum):
    """Status of a task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """A prioritized task"""
    id: str
    title: str
    description: str
    domain: str
    priority: Priority
    status: TaskStatus
    assigned_to: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class PriorityRouter:
    """
    Priority Router routes and prioritizes tasks across domains.
    
    Responsibilities:
    - Prioritize tasks
    - Route to appropriate handlers
    - Manage dependencies
    - Balance workload
    """
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.domain_priorities: Dict[str, int] = {}  # domain -> priority weight
        self.task_queue: List[str] = []  # Task IDs in priority order
    
    def add_domain_priority(self, domain: str, weight: int):
        """Add priority weight for a domain"""
        self.domain_priorities[domain] = weight
    
    def create_task(
        self,
        title: str,
        description: str,
        domain: str,
        priority: Priority,
        estimated_hours: float = 0.0,
        due_date: Optional[datetime] = None,
        dependencies: Optional[List[str]] = None
    ) -> Task:
        """Create a new task"""
        task = Task(
            id=f"task_{len(self.tasks) + 1}_{datetime.now().timestamp()}",
            title=title,
            description=description,
            domain=domain,
            priority=priority,
            status=TaskStatus.PENDING,
            estimated_hours=estimated_hours,
            due_date=due_date,
            dependencies=dependencies or []
        )
        
        self.tasks.append(task)
        self._recalculate_queue()
        
        return task
    
    def update_task_priority(self, task_id: str, new_priority: Priority) -> Optional[Task]:
        """Update task priority"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        
        if not task:
            return None
        
        task.priority = new_priority
        self._recalculate_queue()
        
        return task
    
    def assign_task(self, task_id: str, assignee: str) -> Optional[Task]:
        """Assign a task to someone"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        
        if not task:
            return None
        
        # Check dependencies
        for dep_id in task.dependencies:
            dep_task = next((t for t in self.tasks if t.id == dep_id), None)
            if dep_task and dep_task.status != TaskStatus.COMPLETED:
                return None
        
        task.assigned_to = assignee
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
        
        self._recalculate_queue()
        
        return task
    
    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        
        # Check for dependent tasks that can now proceed
        dependent_tasks = [t for t in self.tasks if task_id in t.dependencies]
        for dep_task in dependent_tasks:
            # Check if all dependencies are met
            all_met = all(
                dt.status == TaskStatus.COMPLETED 
                for dt in self.tasks if dt.id in dep_task.dependencies
            )
            if all_met and dep_task.status == TaskStatus.PENDING:
                dep_task.status = TaskStatus.PENDING  # Ready to be picked up
        
        self._recalculate_queue()
        
        return task
    
    def block_task(self, task_id: str) -> Optional[Task]:
        """Block a task"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        
        if not task:
            return None
        
        task.status = TaskStatus.BLOCKED
        
        return task
    
    def _recalculate_queue(self):
        """Recalculate task queue based on priorities"""
        # Sort by: priority, domain weight, due date
        def sort_key(task: Task):
            domain_weight = self.domain_priorities.get(task.domain, 5)
            return (
                task.priority.value,
                domain_weight,
                task.due_date.timestamp() if task.due_date else float('inf')
            )
        
        sorted_tasks = sorted(self.tasks, key=sort_key)
        self.task_queue = [t.id for t in sorted_tasks]
    
    def get_next_task(self, domain: Optional[str] = None) -> Optional[Task]:
        """Get the next available task"""
        for task_id in self.task_queue:
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task and task.status == TaskStatus.PENDING:
                if domain is None or task.domain == domain:
                    return task
        return None
    
    def get_tasks_by_domain(self, domain: str) -> List[Task]:
        """Get all tasks for a domain"""
        return [t for t in self.tasks if t.domain == domain]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        return [t for t in self.tasks if t.status == status]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        now = datetime.now()
        return [
            t for t in self.tasks 
            if t.due_date and t.due_date < now and t.status != TaskStatus.COMPLETED
        ]
    
    def get_priority_summary(self) -> Dict[str, Any]:
        """Get priority summary"""
        return {
            "total_tasks": len(self.tasks),
            "by_status": {
                "pending": len([t for t in self.tasks if t.status == TaskStatus.PENDING]),
                "in_progress": len([t for t in self.tasks if t.status == TaskStatus.IN_PROGRESS]),
                "completed": len([t for t in self.tasks if t.status == TaskStatus.COMPLETED]),
                "blocked": len([t for t in self.tasks if t.status == TaskStatus.BLOCKED])
            },
            "by_priority": {
                "critical": len([t for t in self.tasks if t.priority == Priority.CRITICAL]),
                "high": len([t for t in self.tasks if t.priority == Priority.HIGH]),
                "medium": len([t for t in self.tasks if t.priority == Priority.MEDIUM]),
                "low": len([t for t in self.tasks if t.priority == Priority.LOW])
            },
            "by_domain": {
                domain: len([t for t in self.tasks if t.domain == domain])
                for domain in set(t.domain for t in self.tasks)
            },
            "overdue": len(self.get_overdue_tasks())
        }
