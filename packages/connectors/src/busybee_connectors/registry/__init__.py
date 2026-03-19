# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Connector Registry.

Defines available connectors, their domains, auth types, and required scopes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConnectorDomain(str, Enum):
    """Domain categories for connectors."""
    FINANCE = "finance"
    HEALTH = "health"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    INTELLIGENCE = "intelligence"
    GENERAL = "general"


class AuthType(str, Enum):
    """Authentication types for connectors."""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC = "basic"
    CUSTOM = "custom"


class ConnectorStatus(str, Enum):
    """Health status of a connector."""
    ACTIVE = "active"
    EXPIRED = "expired"
    ERROR = "error"
    SYNCING = "syncing"
    DISCONNECTED = "disconnected"


@dataclass(frozen=True)
class ConnectorDefinition:
    """Definition of a connector."""
    name: str
    display_name: str
    domain: ConnectorDomain
    auth_type: AuthType
    required_scopes: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""
    icon: str = ""
    documentation_url: str = ""
    
    def __hash__(self) -> int:
        return hash(self.name)


# Registry of all available connectors
CONNECTOR_REGISTRY: dict[str, ConnectorDefinition] = {}


def register_connector(connector: ConnectorDefinition) -> None:
    """Register a connector in the global registry."""
    CONNECTOR_REGISTRY[connector.name] = connector


def get_connector(name: str) -> ConnectorDefinition | None:
    """Get a connector definition by name."""
    return CONNECTOR_REGISTRY.get(name)


def get_connectors_by_domain(domain: ConnectorDomain) -> list[ConnectorDefinition]:
    """Get all connectors for a domain."""
    return [
        c for c in CONNECTOR_REGISTRY.values()
        if c.domain == domain
    ]


def list_all_connectors() -> list[ConnectorDefinition]:
    """List all registered connectors."""
    return list(CONNECTOR_REGISTRY.values())


# Predefined connector definitions
# Finance Connectors
register_connector(ConnectorDefinition(
    name="plaid",
    display_name="Plaid",
    domain=ConnectorDomain.FINANCE,
    auth_type=AuthType.OAUTH2,
    required_scopes=("transactions", "accounts", "investments"),
    description="Connect bank accounts and credit cards",
    icon="🏦",
    documentation_url="https://plaid.com/docs/",
))

register_connector(ConnectorDefinition(
    name="yahoo_finance",
    display_name="Yahoo Finance",
    domain=ConnectorDomain.FINANCE,
    auth_type=AuthType.API_KEY,
    required_scopes=("quote", "chart", "news"),
    description="Real-time stock quotes and financial news",
    icon="📈",
    documentation_url="https://finance.yahoo.com/",
))

register_connector(ConnectorDefinition(
    name="alpaca",
    display_name="Alpaca",
    domain=ConnectorDomain.FINANCE,
    auth_type=AuthType.API_KEY,
    required_scopes=("account", "orders", "positions"),
    description="Commission-free trading API",
    icon="🔄",
    documentation_url="https://alpaca.markets/docs/",
))

# Health Connectors
register_connector(ConnectorDefinition(
    name="apple_health",
    display_name="Apple Health",
    domain=ConnectorDomain.HEALTH,
    auth_type=AuthType.OAUTH2,
    required_scopes=("heart_rate", "steps", "sleep", "workouts"),
    description="Health and fitness data from Apple Watch",
    icon="❤️",
    documentation_url="https://www.apple.com/health/",
))

register_connector(ConnectorDefinition(
    name="fitbit",
    display_name="Fitbit",
    domain=ConnectorDomain.HEALTH,
    auth_type=AuthType.OAUTH2,
    required_scopes=("activity", "heartrate", "sleep", "body"),
    description="Activity trackers and health data",
    icon="👟",
    documentation_url="https://dev.fitbit.com/",
))

# Career Connectors
register_connector(ConnectorDefinition(
    name="google_calendar",
    display_name="Google Calendar",
    domain=ConnectorDomain.CAREER,
    auth_type=AuthType.OAUTH2,
    required_scopes=("calendar", "events", "read"),
    description="Calendar events and scheduling",
    icon="📅",
    documentation_url="https://developers.google.com/calendar",
))

register_connector(ConnectorDefinition(
    name="google_gmail",
    display_name="Gmail",
    domain=ConnectorDomain.CAREER,
    auth_type=AuthType.OAUTH2,
    required_scopes=("mail.read", "mail.send"),
    description="Email integration",
    icon="📧",
    documentation_url="https://developers.google.com/gmail",
))

register_connector(ConnectorDefinition(
    name="slack",
    display_name="Slack",
    domain=ConnectorDomain.CAREER,
    auth_type=AuthType.OAUTH2,
    required_scopes=("channels", "messages", "users"),
    description="Team communication",
    icon="💬",
    documentation_url="https://api.slack.com/",
))

register_connector(ConnectorDefinition(
    name="linkedin",
    display_name="LinkedIn",
    domain=ConnectorDomain.CAREER,
    auth_type=AuthType.OAUTH2,
    required_scopes=("profile", "connections", "jobs"),
    description="Professional network integration",
    icon="💼",
    documentation_url="https://developer.linkedin.com/",
))
