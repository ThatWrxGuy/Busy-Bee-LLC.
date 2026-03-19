# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Audit Log system for governance and compliance.

Provides full audit trail: who, what, when, why.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import uuid

from busybee_contracts.tenant_context import TenantContext


class AuditEventType(str, Enum):
    """Types of audit events."""
    # Authentication
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_LOGIN_FAILED = "user.login_failed"
    
    # Tenant management
    TENANT_CREATED = "tenant.created"
    TENANT_UPDATED = "tenant.updated"
    
    # Connector management
    CONNECTOR_CONNECTED = "connector.connected"
    CONNECTOR_DISCONNECTED = "connector.disconnected"
    CONNECTOR_SYNC = "connector.sync"
    
    # Agent execution
    AGENT_EXECUTED = "agent.executed"
    AGENT_CREATED = "agent.created"
    AGENT_FAILED = "agent.failed"
    
    # Financial
    TRANSACTION_INITIATED = "transaction.initiated"
    TRANSACTION_APPROVED = "transaction.approved"
    TRANSACTION_REJECTED = "transaction.rejected"
    TRANSACTION_EXECUTED = "transaction.executed"
    
    # Data access
    DATA_READ = "data.read"
    DATA_WRITE = "data.write"
    DATA_EXPORTED = "data.exported"
    
    # Governance
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"
    
    # Settings
    SETTINGS_CHANGED = "settings.changed"


@dataclass
class AuditEvent:
    """An audit log entry."""
    event_id: str
    tenant_id: str
    user_id: str
    event_type: AuditEventType
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    resource_id: str | None = None
    resource_type: str | None = None
    action: str | None = None
    outcome: str = "success"
    error_message: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    
    # Lineage from tenant context
    workspace_id: str | None = None
    roles: list[str] = field(default_factory=list)
    
    # Reason for action (required for important actions)
    reason: str | None = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())


class AuditLog:
    """Audit log for tracking all system actions.
    
    Provides complete traceability for compliance and security.
    """
    
    def __init__(self) -> None:
        # In production, this would be a database
        # tenant_id -> list of AuditEvent
        self._events: dict[str, list[AuditEvent]] = {}

    def log(
        self,
        context: TenantContext,
        event_type: AuditEventType,
        action: str | None = None,
        resource_id: str | None = None,
        resource_type: str | None = None,
        metadata: dict[str, Any] | None = None,
        outcome: str = "success",
        error_message: str | None = None,
        reason: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> AuditEvent:
        """Log an audit event.
        
        Args:
            context: Tenant context
            event_type: Type of event
            action: Description of action
            resource_id: ID of affected resource
            resource_type: Type of resource
            metadata: Additional metadata
            outcome: Result of action
            error_message: Error message if failed
            reason: Reason for action
            ip_address: Client IP
            user_agent: Client user agent
            
        Returns:
            Created audit event
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            tenant_id=context.tenant_id or "personal",
            user_id=context.user_id or "system",
            event_type=event_type,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            outcome=outcome,
            error_message=error_message,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
            workspace_id=context.workspace_id,
            roles=list(context.roles) if context.roles else []
        )
        
        # Store event
        if event.tenant_id not in self._events:
            self._events[event.tenant_id] = []
        
        self._events[event.tenant_id].append(event)
        
        return event

    def get_events(
        self,
        tenant_id: str,
        event_type: AuditEventType | None = None,
        user_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100
    ) -> list[AuditEvent]:
        """Get audit events for a tenant.
        
        Args:
            tenant_id: Tenant ID
            event_type: Filter by event type
            user_id: Filter by user
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Max results
            
        Returns:
            List of audit events
        """
        events = self._events.get(tenant_id, [])
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # Sort by timestamp descending
        events = sorted(events, key=lambda e: e.timestamp, reverse=True)
        
        return events[:limit]

    def get_event(self, event_id: str, tenant_id: str) -> AuditEvent | None:
        """Get a specific audit event."""
        events = self._events.get(tenant_id, [])
        for event in events:
            if event.event_id == event_id:
                return event
        return None

    def get_user_activity(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 50
    ) -> list[AuditEvent]:
        """Get activity for a specific user."""
        events = self._events.get(tenant_id, [])
        user_events = [e for e in events if e.user_id == user_id]
        return sorted(user_events, key=lambda e: e.timestamp, reverse=True)[:limit]

    def get_resource_history(
        self,
        tenant_id: str,
        resource_id: str
    ) -> list[AuditEvent]:
        """Get history for a specific resource."""
        events = self._events.get(tenant_id, [])
        return sorted(
            [e for e in events if e.resource_id == resource_id],
            key=lambda e: e.timestamp,
            reverse=True
        )

    def count_events(
        self,
        tenant_id: str,
        event_type: AuditEventType | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None
    ) -> int:
        """Count events matching criteria."""
        events = self._events.get(tenant_id, [])
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        return len(events)

    def to_dict(self, event: AuditEvent) -> dict[str, Any]:
        """Convert event to dict for serialization."""
        return {
            "event_id": event.event_id,
            "tenant_id": event.tenant_id,
            "user_id": event.user_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "metadata": event.metadata,
            "resource_id": event.resource_id,
            "resource_type": event.resource_type,
            "action": event.action,
            "outcome": event.outcome,
            "error_message": event.error_message,
            "workspace_id": event.workspace_id,
            "roles": event.roles,
            "reason": event.reason,
        }


# Singleton instance
_audit_log: AuditLog | None = None


def get_audit_log() -> AuditLog:
    """Get the default audit log."""
    global _audit_log
    if _audit_log is None:
        _audit_log = AuditLog()
    return _audit_log


# Convenience function for logging
def log_audit(
    context: TenantContext,
    event_type: AuditEventType,
    action: str | None = None,
    **kwargs
) -> AuditEvent:
    """Log an audit event (convenience function)."""
    return get_audit_log().log(context, event_type, action, **kwargs)
