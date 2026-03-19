"""
Infrastructure Layer
"""

from .memory_engine.memory_engine import MemoryEngine, MemoryEntry
from .signal_system.signal_system import SignalSystem, Signal, SignalRoute, SignalPriority, SignalStatus

# Isolation Architecture - BB-ARCH-ISO-001
from .isolation import (
    # Layer 1: Cognitive Isolation
    AgentSandbox,
    AgentSandboxRegistry,
    AgentContext,
    AgentOutput,
    AgentDomain,
    get_agent_registry,
    
    # Layer 2: Data & Memory Isolation
    MemoryScopeManager,
    MemoryScope,
    get_memory_manager,
    
    # Layer 3: Tool & Permission Isolation
    PermissionRegistry,
    ToolGatekeeper,
    ToolRiskLevel,
    get_tool_gatekeeper,
    
    # Layer 4: Runtime Execution Isolation
    RuntimeIsolator,
    EngineConfig,
    EngineType,
    get_runtime_isolator,
    
    # Layer 5: Risk & Action Isolation
    ExecutionGate,
    ActionRequest,
    ActionRiskLevel,
    ActionCategory,
    get_execution_gate,
    
    # Shared Intelligence Fabric
    SharedIntelligenceFabric,
    EventType,
    get_shared_intelligence_fabric,
)

# Container Runtime Architecture - BB-ARCH-ISO-002
from .runtime import (
    # Agent Orchestrator
    AgentOrchestrator,
    SandboxRuntime,
    DevelopmentSandbox,
    AgentConfig,
    AgentContainer,
    AgentHealth,
    AgentStatus,
    RuntimeMode,
    get_agent_orchestrator,
    
    # Capability Token Service
    CapabilityTokenService,
    CapabilityRegistry,
    Capability,
    CapabilityToken,
    CapabilityScope,
    get_capability_token_service,
    
    # Resource Governor
    ResourceGovernor,
    ResourceLimit,
    ResourceType,
    AgentResources,
    ExecutionTimer,
    ResourceLimitExceeded,
    get_resource_governor,
)


__all__ = [
    # Memory Engine
    "MemoryEngine",
    "MemoryEntry",
    
    # Signal System
    "SignalSystem",
    "Signal",
    "SignalRoute",
    "SignalPriority",
    "SignalStatus",
    
    # Isolation Architecture - BB-ARCH-ISO-001
    "AgentSandbox",
    "AgentSandboxRegistry",
    "AgentContext",
    "AgentOutput",
    "AgentDomain",
    "get_agent_registry",
    "MemoryScopeManager",
    "MemoryScope",
    "get_memory_manager",
    "PermissionRegistry",
    "ToolGatekeeper",
    "ToolRiskLevel",
    "get_tool_gatekeeper",
    "RuntimeIsolator",
    "EngineConfig",
    "EngineType",
    "get_runtime_isolator",
    "ExecutionGate",
    "ActionRequest",
    "ActionRiskLevel",
    "ActionCategory",
    "get_execution_gate",
    "SharedIntelligenceFabric",
    "EventType",
    "get_shared_intelligence_fabric",
    
    # Container Runtime Architecture - BB-ARCH-ISO-002
    "AgentOrchestrator",
    "SandboxRuntime",
    "DevelopmentSandbox",
    "AgentConfig",
    "AgentContainer",
    "AgentHealth",
    "AgentStatus",
    "RuntimeMode",
    "get_agent_orchestrator",
    "CapabilityTokenService",
    "CapabilityRegistry",
    "Capability",
    "CapabilityToken",
    "CapabilityScope",
    "get_capability_token_service",
    "ResourceGovernor",
    "ResourceLimit",
    "ResourceType",
    "AgentResources",
    "ExecutionTimer",
    "ResourceLimitExceeded",
    "get_resource_governor",
]
