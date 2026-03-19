"""
Runtime Architecture - BB-ARCH-ISO-002
Agent Sandbox & Container Runtime Architecture

This module implements the physical runtime isolation layer:

- Agent Orchestrator: Lifecycle management
- Sandbox Runtime: Execution environments
- Capability Token Service: Security model
- Resource Governor: Resource enforcement

Directive: BB-ARCH-ISO-002
"""

from .agent_orchestrator import (
    AgentOrchestrator,
    SandboxRuntime,
    DevelopmentSandbox,
    AgentConfig,
    AgentContainer,
    AgentHealth,
    AgentStatus,
    RuntimeMode,
    get_agent_orchestrator,
    reset_agent_orchestrator,
)

from .capability_token_service import (
    CapabilityTokenService,
    CapabilityRegistry,
    Capability,
    CapabilityToken,
    CapabilityScope,
    get_capability_token_service,
    reset_capability_token_service,
)

from .resource_governor import (
    ResourceGovernor,
    ResourceLimit,
    ResourceType,
    AgentResources,
    ExecutionTimer,
    ResourceLimitExceeded,
    get_resource_governor,
    reset_resource_governor,
)


__all__ = [
    # Agent Orchestrator
    "AgentOrchestrator",
    "SandboxRuntime",
    "DevelopmentSandbox",
    "AgentConfig",
    "AgentContainer",
    "AgentHealth",
    "AgentStatus",
    "RuntimeMode",
    "get_agent_orchestrator",
    "reset_agent_orchestrator",
    
    # Capability Token Service
    "CapabilityTokenService",
    "CapabilityRegistry",
    "Capability",
    "CapabilityToken",
    "CapabilityScope",
    "get_capability_token_service",
    "reset_capability_token_service",
    
    # Resource Governor
    "ResourceGovernor",
    "ResourceLimit",
    "ResourceType",
    "AgentResources",
    "ExecutionTimer",
    "ResourceLimitExceeded",
    "get_resource_governor",
    "reset_resource_governor",
]
