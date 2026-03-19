"""
Isolation Architecture - BB-ARCH-ISO-001
Agent & Engine Isolation Architecture

This module implements the five-layer isolation architecture for Busy Bee:

Layer 1 - Cognitive Isolation (agent_sandbox.py)
    - Agent reasoning boundaries
    - Structured input/output interfaces
    - Agent registry and health monitoring

Layer 2 - Data & Memory Isolation (memory_scope_manager.py)
    - Agent Working Memory
    - Domain Memory
    - Shared Strategic Memory
    - Immutable Audit Memory

Layer 3 - Tool & Permission Isolation (permission_registry.py, tool_gatekeeper.py)
    - Permission registry
    - Tool gatekeeper
    - Risk level enforcement

Layer 4 - Runtime Execution Isolation (runtime_isolator.py)
    - Engine isolation
    - Fault containment
    - Graceful degradation

Layer 5 - Risk & Action Isolation (risk_execution_gate.py)
    - Execution gate
    - Approval pipeline
    - Human-in-the-loop controls

Shared Intelligence Fabric (shared_intelligence_fabric.py)
    - Event Bus
    - Strategy Registry
    - Recommendation Ledger
    - Confidence Scoring
    - Risk Aggregation
"""

from .agent_sandbox import (
    AgentSandbox,
    AgentSandboxRegistry,
    AgentContext,
    AgentOutput,
    AgentDomain,
    AgentType,
    get_agent_registry,
    reset_agent_registry,
)

from .memory_scope_manager import (
    MemoryScopeManager,
    MemoryScope,
    MemoryAccessLevel,
    MemoryEntry,
    get_memory_manager,
    reset_memory_manager,
)

from .permission_registry import (
    PermissionRegistry,
    ToolDefinition,
    ToolRiskLevel,
    PermissionStatus,
    get_permission_registry,
    reset_permission_registry,
)

from .tool_gatekeeper import (
    ToolGatekeeper,
    GatekeeperRequest,
    GatekeeperResponse,
    GatekeeperDecision,
    get_tool_gatekeeper,
    reset_tool_gatekeeper,
)

from .runtime_isolator import (
    RuntimeIsolator,
    IsolatedEngine,
    EngineConfig,
    EngineType,
    EngineStatus,
    EngineHealth,
    get_runtime_isolator,
    reset_runtime_isolator,
)

from .risk_execution_gate import (
    ExecutionGate,
    ActionRequest,
    ApprovalRequest,
    ActionRiskLevel,
    ActionCategory,
    ApprovalStatus,
    ApprovalStage,
    RiskEvaluator,
    DefaultRiskEvaluator,
    get_execution_gate,
    reset_execution_gate,
)

from .shared_intelligence_fabric import (
    SharedIntelligenceFabric,
    FabricEvent,
    EventType,
    EventBus,
    StrategyRegistry,
    RecommendationLedger,
    ConfidenceScorer,
    RiskAggregator,
    get_shared_intelligence_fabric,
    reset_shared_intelligence_fabric,
)


__all__ = [
    # Layer 1: Cognitive Isolation
    "AgentSandbox",
    "AgentSandboxRegistry",
    "AgentContext",
    "AgentOutput",
    "AgentDomain",
    "AgentType",
    "get_agent_registry",
    "reset_agent_registry",
    
    # Layer 2: Data & Memory Isolation
    "MemoryScopeManager",
    "MemoryScope",
    "MemoryAccessLevel",
    "MemoryEntry",
    "get_memory_manager",
    "reset_memory_manager",
    
    # Layer 3: Tool & Permission Isolation
    "PermissionRegistry",
    "ToolDefinition",
    "ToolRiskLevel",
    "PermissionStatus",
    "ToolGatekeeper",
    "GatekeeperRequest",
    "GatekeeperResponse",
    "GatekeeperDecision",
    "get_permission_registry",
    "reset_permission_registry",
    "get_tool_gatekeeper",
    "reset_tool_gatekeeper",
    
    # Layer 4: Runtime Execution Isolation
    "RuntimeIsolator",
    "IsolatedEngine",
    "EngineConfig",
    "EngineType",
    "EngineStatus",
    "EngineHealth",
    "get_runtime_isolator",
    "reset_runtime_isolator",
    
    # Layer 5: Risk & Action Isolation
    "ExecutionGate",
    "ActionRequest",
    "ApprovalRequest",
    "ActionRiskLevel",
    "ActionCategory",
    "ApprovalStatus",
    "ApprovalStage",
    "RiskEvaluator",
    "DefaultRiskEvaluator",
    "get_execution_gate",
    "reset_execution_gate",
    
    # Shared Intelligence Fabric
    "SharedIntelligenceFabric",
    "FabricEvent",
    "EventType",
    "EventBus",
    "StrategyRegistry",
    "RecommendationLedger",
    "ConfidenceScorer",
    "RiskAggregator",
    "get_shared_intelligence_fabric",
    "reset_shared_intelligence_fabric",
]
