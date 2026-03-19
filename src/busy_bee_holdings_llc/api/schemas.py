# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""API Schemas for OpenHands (Backend) and Base44 (Frontend) coordination.

These schemas define the contract between backend and frontend.
Backend defines schema → frontend consumes.
Strict versioning of API responses.
No UI logic in backend.
No business logic in frontend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from enum import Enum


# ==================== Authentication ====================

class AuthProvider(str, Enum):
    """Supported authentication providers."""
    CLERK = "clerk"
    AUTH0 = "auth0"
    SUPABASE = "supabase"
    INTERNAL = "internal"


@dataclass
class LoginRequest:
    """Login request."""
    provider: AuthProvider = AuthProvider.INTERNAL
    email: str | None = None
    password: str | None = None
    token: str | None = None  # For OAuth


@dataclass
class LoginResponse:
    """Login response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: str | None = None
    user: "UserInfo" | None = None


@dataclass
class UserInfo:
    """User information."""
    user_id: str
    email: str
    name: str | None = None
    avatar_url: str | None = None
    tenant_id: str | None = None
    roles: list[str] = field(default_factory=list)
    plan_tier: str = "free"


@dataclass
class SignupRequest:
    """Signup request."""
    email: str
    password: str
    name: str
    provider: AuthProvider = AuthProvider.INTERNAL


# ==================== Tenant ====================

@dataclass
class TenantInfo:
    """Tenant information."""
    tenant_id: str
    plan_tier: str
    created_at: datetime
    user_count: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantContextResponse:
    """Tenant context response."""
    tenant_id: str
    user_id: str
    workspace_id: str | None = None
    roles: list[str]
    permissions: list[str]
    plan_tier: str


# ==================== Dashboard ====================

@dataclass
class DashboardResponse:
    """Dashboard API response.
    
    This is the main endpoint for the executive dashboard.
    """
    tenant_id: str
    generated_at: datetime
    domains: dict[str, "DomainSummaryDTO"]
    alerts: list["AlertDTO"]
    opportunities: list["OpportunityDTO"]
    approvals: list["ApprovalDTO"]
    overall_status: str
    health_score: int
    connectors: dict[str, str]


@dataclass
class DomainSummaryDTO:
    """Domain summary for dashboard."""
    domain: str
    status: str
    last_update: datetime | None
    metrics: dict[str, Any]
    alerts: list[str]
    opportunities: list[str]


@dataclass
class AlertDTO:
    """Alert for dashboard."""
    id: str
    severity: str  # critical, warning, info
    domain: str
    message: str
    timestamp: datetime
    action_required: bool


@dataclass
class OpportunityDTO:
    """Opportunity for dashboard."""
    id: str
    domain: str
    title: str
    description: str
    potential_impact: str
    recommended_action: str
    timestamp: datetime


@dataclass
class ApprovalDTO:
    """Approval request for dashboard."""
    request_id: str
    action_id: str
    domain: str
    risk_level: str
    description: str
    requested_by: str
    requested_at: datetime
    details: dict[str, Any]


# ==================== Connectors ====================

@dataclass
class ConnectorDefinitionDTO:
    """Connector definition for API."""
    name: str
    display_name: str
    domain: str
    auth_type: str
    required_scopes: list[str]
    description: str
    icon: str
    documentation_url: str


@dataclass
class ConnectorStatusResponse:
    """Connector status response."""
    connector_name: str
    status: str  # active, expired, error, syncing, disconnected
    connected: bool = False
    expires_at: datetime | None = None
    last_synced: datetime | None = None
    error_message: str | None = None


@dataclass
class ConnectConnectorRequest:
    """Request to connect a connector."""
    connector_name: str
    credentials: dict[str, str]  # Encrypted on wire
    scopes: list[str] | None = None


@dataclass
class ConnectorListResponse:
    """List of available and connected connectors."""
    available: list[ConnectorDefinitionDTO]
    connected: list[ConnectorStatusResponse]


# ==================== Onboarding ====================

@dataclass
class OnboardingRequest:
    """Onboarding request."""
    selected_domains: list[str]  # finance, health, career, etc.
    profile: "UserProfileDTO"


@dataclass
class UserProfileDTO:
    """User profile for onboarding."""
    name: str
    goals: list[str] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)


@dataclass
class OnboardingResponse:
    """Onboarding response."""
    tenant_id: str
    activated_domains: list[str]
    suggested_connectors: list[str]
    next_steps: list[str]


# ==================== Approval Actions ====================

@dataclass
class ApprovalActionRequest:
    """Request to approve or reject an action."""
    request_id: str
    action: str  # approve or reject
    reason: str | None = None


@dataclass
class ApprovalActionResponse:
    """Response to approval action."""
    request_id: str
    status: str  # approved, rejected
    resolved_at: datetime
    resolved_by: str


# ==================== API Response Wrappers ====================

@dataclass
class APIResponse:
    """Generic API response wrapper."""
    success: bool
    data: Any | None = None
    error: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class PaginatedResponse:
    """Paginated response."""
    items: list[Any]
    total: int
    page: int
    page_size: int
    has_more: bool


# ==================== WebSocket Events ====================

class WSEventType(str, Enum):
    """WebSocket event types."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_PROGRESS = "execution_progress"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    APPROVAL_REQUESTED = "approval_requested"
    ALERT = "alert"


@dataclass
class WSMessage:
    """WebSocket message."""
    event_type: WSEventType
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
