# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Connector Health Monitor.

Monitors connector status: active, expired, error, syncing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from busybee_contracts.tenant_context import TenantContext


class ConnectorHealthStatus(str, Enum):
    """Health status of a connector."""
    ACTIVE = "active"
    EXPIRED = "expired"
    ERROR = "error"
    SYNCING = "syncing"
    DISCONNECTED = "disconnected"


@dataclass
class ConnectorHealthRecord:
    """Health record for a connector."""
    connector_name: str
    tenant_id: str
    status: ConnectorHealthStatus
    last_check: datetime
    last_success: datetime | None = None
    last_error: str | None = None
    error_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ConnectorHealthMonitor:
    """Monitors health of tenant connectors.
    
    Tracks status, errors, and sync state for all connector connections.
    """

    def __init__(self) -> None:
        # tenant_id -> connector_name -> ConnectorHealthRecord
        self._records: dict[str, dict[str, ConnectorHealthRecord]] = {}

    def record_check(
        self,
        context: TenantContext,
        connector_name: str,
        status: ConnectorHealthStatus,
        error: str | None = None
    ) -> None:
        """Record a health check result."""
        if not context.tenant_id:
            return

        if context.tenant_id not in self._records:
            self._records[context.tenant_id] = {}

        records = self._records[context.tenant_id]
        
        if connector_name in records:
            record = records[connector_name]
            record.status = status
            record.last_check = datetime.utcnow()
            if status == ConnectorHealthStatus.ACTIVE:
                record.last_success = datetime.utcnow()
                record.error_count = 0
                record.last_error = None
            elif status == ConnectorHealthStatus.ERROR:
                record.error_count += 1
                record.last_error = error
        else:
            records[connector_name] = ConnectorHealthRecord(
                connector_name=connector_name,
                tenant_id=context.tenant_id,
                status=status,
                last_check=datetime.utcnow(),
                last_success=datetime.utcnow() if status == ConnectorHealthStatus.ACTIVE else None,
                last_error=error,
                error_count=1 if status == ConnectorHealthStatus.ERROR else 0
            )

    def get_status(
        self,
        context: TenantContext,
        connector_name: str
    ) -> ConnectorHealthStatus:
        """Get current health status for a connector."""
        if not context.tenant_id:
            return ConnectorHealthStatus.DISCONNECTED

        records = self._records.get(context.tenant_id, {})
        record = records.get(connector_name)
        
        if record is None:
            return ConnectorHealthStatus.DISCONNECTED

        return record.status

    def get_all_statuses(
        self,
        context: TenantContext
    ) -> dict[str, ConnectorHealthStatus]:
        """Get all connector statuses for a tenant."""
        if not context.tenant_id:
            return {}

        records = self._records.get(context.tenant_id, {})
        return {
            name: record.status
            for name, record in records.items()
        }

    def get_health_record(
        self,
        context: TenantContext,
        connector_name: str
    ) -> ConnectorHealthRecord | None:
        """Get full health record for a connector."""
        if not context.tenant_id:
            return None

        return self._records.get(context.tenant_id, {}).get(connector_name)

    def get_records_for_tenant(
        self,
        tenant_id: str
    ) -> list[ConnectorHealthRecord]:
        """Get all health records for a tenant."""
        records = self._records.get(tenant_id, {})
        return list(records.values())

    def clear_record(
        self,
        context: TenantContext,
        connector_name: str
    ) -> bool:
        """Clear health record for a connector."""
        if not context.tenant_id:
            return False

        records = self._records.get(context.tenant_id, {})
        if connector_name in records:
            del records[connector_name]
            return True
        return False


# Singleton instance
_health_monitor: ConnectorHealthMonitor | None = None


def get_health_monitor() -> ConnectorHealthMonitor:
    """Get the default health monitor."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = ConnectorHealthMonitor()
    return _health_monitor
