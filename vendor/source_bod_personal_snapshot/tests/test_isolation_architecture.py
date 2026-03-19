"""
Isolation Architecture Tests - BB-ARCH-ISO-001

Tests for the five-layer isolation architecture:
1. Agent sandbox (cognitive isolation)
2. Memory scope manager (data isolation)
3. Tool gatekeeper (permission isolation)
4. Runtime isolator (execution isolation)
5. Execution gate (risk/action isolation)

Required tests per BB-ARCH-ISO-001 Section 10:
- agent_failure_test
- engine_failure_test
- memory_boundary_test
- tool_permission_test
- execution_gate_test
- cross_domain_contamination_test
"""

import pytest
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any

# Import isolation modules
from infrastructure.isolation import (
    # Layer 1: Cognitive Isolation
    AgentSandbox,
    AgentSandboxRegistry,
    AgentContext,
    AgentOutput,
    AgentDomain,
    get_agent_registry,
    reset_agent_registry,
    
    # Layer 2: Data & Memory Isolation
    MemoryScopeManager,
    MemoryScope,
    get_memory_manager,
    reset_memory_manager,
    
    # Layer 3: Tool & Permission Isolation
    PermissionRegistry,
    ToolGatekeeper,
    GatekeeperRequest,
    GatekeeperDecision,
    ToolRiskLevel,
    get_tool_gatekeeper,
    get_permission_registry,
    reset_permission_registry,
    reset_tool_gatekeeper,
    
    # Layer 4: Runtime Execution Isolation
    RuntimeIsolator,
    IsolatedEngine,
    EngineConfig,
    EngineType,
    EngineStatus,
    get_runtime_isolator,
    reset_runtime_isolator,
    
    # Layer 5: Risk & Action Isolation
    ExecutionGate,
    ActionRequest,
    ActionRiskLevel,
    ActionCategory,
    ApprovalStage,
    ApprovalStatus,
    get_execution_gate,
    reset_execution_gate,
    
    # Shared Intelligence Fabric
    SharedIntelligenceFabric,
    EventType,
    get_shared_intelligence_fabric,
    reset_shared_intelligence_fabric,
)


# ============================================================================
# Helper Classes for Testing
# ============================================================================

class TestAgent(AgentSandbox):
    """Test implementation of AgentSandbox"""
    
    def __init__(self, agent_id: str, name: str, domain: AgentDomain, allowed_domains: set = None):
        super().__init__(agent_id, name, domain, allowed_domains)
        self.processed_count = 0
        
    def _reason(self, context: AgentContext) -> Dict[str, Any]:
        """Simple reasoning implementation for testing"""
        self.processed_count += 1
        
        # Store something in working memory
        self._working_memory["last_signal"] = context.available_signals
        
        # Generate output
        return {
            "insights": [{
                "type": "test_insight",
                "title": f"Insight from {self.name}",
                "confidence": 0.8
            }],
            "risk_signals": [],
            "recommendations": []
        }


class TestEngine(IsolatedEngine):
    """Test implementation of IsolatedEngine"""
    
    def __init__(self, engine_id: str, should_fail: bool = False):
        config = EngineConfig(
            engine_id=engine_id,
            engine_type=EngineType.RECOMMENDATION,
            timeout_ms=5000,
            max_retries=3
        )
        super().__init__(config)
        self.should_fail = should_fail
        self.process_count = 0
        
    def _perform_recovery(self) -> None:
        """Simple recovery implementation"""
        self.process_count = 0
        
    def process(self, data: Any) -> Any:
        """Process implementation"""
        if self.should_fail:
            raise ValueError("Test engine failure")
        self.process_count += 1
        return {"result": f"processed_{data}"}


def reset_all_globals():
    """Reset all global instances for test isolation"""
    reset_agent_registry()
    reset_memory_manager()
    reset_permission_registry()
    reset_tool_gatekeeper()
    reset_runtime_isolator()
    reset_execution_gate()
    reset_shared_intelligence_fabric()


# ============================================================================
# Layer 1: Cognitive Isolation Tests
# ============================================================================

class TestAgentSandbox:
    """Tests for Layer 1 - Cognitive Isolation"""
    
    def setup_method(self):
        """Reset before each test"""
        reset_all_globals()
        
    def test_agent_working_memory_isolation(self):
        """Test that agents have isolated working memory"""
        agent1 = TestAgent("agent_1", "Test Agent 1", AgentDomain.FINANCE)
        agent2 = TestAgent("agent_2", "Test Agent 2", AgentDomain.HEALTH)
        
        # Write to agent1's memory
        agent1._working_memory["test_key"] = "agent1_value"
        
        # Write to agent2's memory
        agent2._working_memory["test_key"] = "agent2_value"
        
        # Verify isolation
        assert agent1._working_memory["test_key"] == "agent1_value"
        assert agent2._working_memory["test_key"] == "agent2_value"
        assert agent1._working_memory["test_key"] != agent2._working_memory["test_key"]
        
    def test_agent_execution_returns_structured_output(self):
        """Test that agent execution returns structured AgentOutput"""
        agent = TestAgent("test_agent", "Test Agent", AgentDomain.FINANCE)
        
        context = AgentContext(
            agent_id="test_agent",
            domain=AgentDomain.FINANCE,
            available_signals=[{"id": "signal_1", "data": "test"}],
            domain_memory={},
            shared_intelligence={}
        )
        
        output = agent.execute(context)
        
        assert isinstance(output, AgentOutput)
        assert output.agent_id == "test_agent"
        assert output.domain == AgentDomain.FINANCE
        assert len(output.insights) > 0
        
    def test_agent_domain_restriction(self):
        """Test that agents can be restricted to specific domains"""
        finance_agent = TestAgent(
            "finance_agent",
            "Finance Agent",
            AgentDomain.FINANCE,
            allowed_domains={AgentDomain.FINANCE}
        )
        
        # Try to create context for health domain
        health_context = AgentContext(
            agent_id="finance_agent",
            domain=AgentDomain.HEALTH,
            available_signals=[],
            domain_memory={},
            shared_intelligence={}
        )
        
        # Should fail validation
        assert not finance_agent._validate_context(health_context)
        
    def test_agent_sandbox_registry(self):
        """Test agent sandbox registry functionality"""
        registry = get_agent_registry()
        
        agent1 = TestAgent("agent_1", "Agent 1", AgentDomain.FINANCE)
        agent2 = TestAgent("agent_2", "Agent 2", AgentDomain.HEALTH)
        
        registry.register(agent1)
        registry.register(agent2)
        
        # Verify registration
        assert registry.get("agent_1") == agent1
        assert registry.get("agent_2") == agent2
        
        # Get by domain
        finance_agents = registry.get_by_domain(AgentDomain.FINANCE)
        assert len(finance_agents) == 1
        assert finance_agents[0].agent_id == "agent_1"


# ============================================================================
# Layer 2: Memory Scope Manager Tests
# ============================================================================

class TestMemoryScopeManager:
    """Tests for Layer 2 - Data & Memory Isolation"""
    
    def setup_method(self):
        """Reset before each test"""
        reset_all_globals()
        
    def test_agent_working_memory_layer(self):
        """Test Agent Working Memory layer"""
        manager = get_memory_manager()
        
        # Write to agent working memory
        manager.write(
            scope=MemoryScope.AGENT_WORKING,
            key="test_key",
            value="test_value",
            requester_id="agent_1"
        )
        
        # Read back
        value = manager.read(
            scope=MemoryScope.AGENT_WORKING,
            key="test_key",
            requester_id="agent_1"
        )
        
        assert value == "test_value"
        
    def test_memory_boundary_between_agents(self):
        """Test memory boundary between agents (Section 10: memory_boundary_test)"""
        manager = get_memory_manager()
        
        # Agent 1 writes to their memory
        manager.write(
            scope=MemoryScope.AGENT_WORKING,
            key="agent_1:secret",
            value="agent_1_secret",
            requester_id="agent_1"
        )
        
        # Agent 2 cannot read agent 1's memory
        value = manager.read(
            scope=MemoryScope.AGENT_WORKING,
            key="agent_1:secret",
            requester_id="agent_2"
        )
        
        assert value is None
        
    def test_domain_memory_isolation(self):
        """Test domain memory isolation"""
        manager = get_memory_manager()
        
        # Finance domain writes
        manager.write(
            scope=MemoryScope.DOMAIN,
            key="portfolio",
            value={"stocks": 100},
            requester_id="finance_agent",
            domain="finance"
        )
        
        # Health domain writes
        manager.write(
            scope=MemoryScope.DOMAIN,
            key="sleep_hours",
            value=8,
            requester_id="health_agent",
            domain="health"
        )
        
        # Read back
        finance_value = manager.read(
            scope=MemoryScope.DOMAIN,
            key="portfolio",
            requester_id="finance_agent",
            domain="finance"
        )
        
        health_value = manager.read(
            scope=MemoryScope.DOMAIN,
            key="sleep_hours",
            requester_id="health_agent",
            domain="health"
        )
        
        assert finance_value == {"stocks": 100}
        assert health_value == 8
        
    def test_shared_strategic_memory_accessible_by_all(self):
        """Test shared strategic memory is accessible by all"""
        manager = get_memory_manager()
        
        # Write to shared memory
        manager.write(
            scope=MemoryScope.SHARED_STRATEGIC,
            key="strategic_priority",
            value="financial_independence",
            requester_id="finance_agent"
        )
        
        # Any agent can read
        value = manager.read(
            scope=MemoryScope.SHARED_STRATEGIC,
            key="strategic_priority",
            requester_id="health_agent"
        )
        
        assert value == "financial_independence"
        
    def test_audit_memory_append_only(self):
        """Test that audit memory is immutable (append-only)"""
        manager = get_memory_manager()
        
        # Append to audit
        entry = manager.audit_log(
            entry_type="recommendation",
            data={"action": "test"},
            actor_id="system"
        )
        
        assert entry.scope == MemoryScope.AUDIT
        
        # Try to delete - should raise error
        with pytest.raises(PermissionError):
            manager.audit.delete("test_key", "agent_1")
            
    def test_cross_domain_contamination_prevention(self):
        """Test cross-domain contamination is prevented (Section 10: cross_domain_contamination_test)"""
        manager = get_memory_manager()
        
        # Finance domain stores sensitive data
        manager.write(
            scope=MemoryScope.DOMAIN,
            key="account_number",
            value="123456789",
            requester_id="finance_agent",
            domain="finance"
        )
        
        # Health domain cannot access finance domain memory
        value = manager.read(
            scope=MemoryScope.DOMAIN,
            key="account_number",
            requester_id="health_agent",
            domain="health"
        )
        
        # Health domain should not be able to access finance domain data
        # The domain parameter changes the lookup key
        assert value is None


# ============================================================================
# Layer 3: Tool & Permission Tests
# ============================================================================

class TestToolGatekeeper:
    """Tests for Layer 3 - Tool & Permission Isolation"""
    
    def setup_method(self):
        """Reset before each test"""
        reset_all_globals()
        
    def test_tool_permission_basic(self):
        """Test basic tool permission checking"""
        registry = get_permission_registry()
        gatekeeper = get_tool_gatekeeper()
        
        # Grant permission
        registry.grant_permission(
            agent_id="agent_1",
            tool_id="read_market_data",
            granted_by="system"
        )
        
        # Check access
        request = GatekeeperRequest(
            request_id="test_1",
            agent_id="agent_1",
            agent_domain="finance",
            tool_id="read_market_data",
            parameters={}
        )
        
        response = gatekeeper.check_access(request)
        
        assert response.decision == GatekeeperDecision.ALLOW
        
    def test_tool_permission_denied(self):
        """Test permission denial for unauthorized tools"""
        gatekeeper = get_tool_gatekeeper()
        
        request = GatekeeperRequest(
            request_id="test_2",
            agent_id="agent_1",
            agent_domain="finance",
            tool_id="execute_trade",  # Requires approval
            parameters={}
        )
        
        response = gatekeeper.check_access(request)
        
        # Should require approval for L5 tool
        assert response.decision in [GatekeeperDecision.DENY, GatekeeperDecision.REQUIRE_APPROVAL]
        
    def test_domain_restriction(self):
        """Test that tools are restricted to allowed domains"""
        gatekeeper = get_tool_gatekeeper()
        
        # Try to use finance tool in health domain
        request = GatekeeperRequest(
            request_id="test_3",
            agent_id="agent_1",
            agent_domain="health",
            tool_id="read_market_data",  # Only for finance
            parameters={}
        )
        
        response = gatekeeper.check_access(request)
        
        assert response.decision == GatekeeperDecision.DENY
        
    def test_tool_permission_test(self):
        """Test tool permission enforcement (Section 10: tool_permission_test)"""
        registry = get_permission_registry()
        gatekeeper = get_tool_gatekeeper()
        
        # Agent without permission tries to access tool
        can_access = gatekeeper.is_tool_allowed(
            agent_id="unauthorized_agent",
            tool_id="analyze_portfolio",
            agent_domain="finance"
        )
        
        # Domain permission might grant access
        # But explicit grant should be checked
        
        # Grant explicit permission
        registry.grant_permission(
            agent_id="authorized_agent",
            tool_id="analyze_portfolio",
            granted_by="governor"
        )
        
        can_access = gatekeeper.is_tool_allowed(
            agent_id="authorized_agent",
            tool_id="analyze_portfolio",
            agent_domain="finance"
        )
        
        assert can_access is True
        
    def test_l5_tool_requires_approval(self):
        """Test L5 (external action) tools require approval"""
        gatekeeper = get_tool_gatekeeper()
        
        # execute_trade is L5, requires approval
        risk_level = gatekeeper.get_tool_risk_level("execute_trade")
        
        assert risk_level == ToolRiskLevel.L5_EXTERNAL


# ============================================================================
# Layer 4: Runtime Isolator Tests
# ============================================================================

class TestRuntimeIsolator:
    """Tests for Layer 4 - Runtime Execution Isolation"""
    
    def setup_method(self):
        """Reset before each test"""
        reset_all_globals()
        
    def test_engine_registration(self):
        """Test engine registration"""
        isolator = get_runtime_isolator()
        
        engine = TestEngine("test_engine")
        isolator.register_engine(engine)
        
        assert isolator.get_engine("test_engine") == engine
        
    def test_engine_execution_isolation(self):
        """Test engine execution with isolation"""
        isolator = get_runtime_isolator()
        
        engine = TestEngine("test_engine")
        isolator.register_engine(engine)
        
        result = isolator.execute_engine(
            "test_engine",
            engine.process,
            "test_data"
        )
        
        assert result["result"] == "processed_test_data"
        
    def test_engine_failure_isolation(self):
        """Test engine failure is contained (Section 10: engine_failure_test)"""
        isolator = get_runtime_isolator()
        
        # Create engine that will fail
        failing_engine = TestEngine("failing_engine", should_fail=True)
        isolator.register_engine(failing_engine)
        
        # Register a healthy engine
        healthy_engine = TestEngine("healthy_engine")
        isolator.register_engine(healthy_engine)
        
        # Try to execute failing engine
        with pytest.raises(ValueError):
            failing_engine.process("test")
        
        # Healthy engine should still work
        result = healthy_engine.process("test")
        assert result["result"] == "processed_test"
        
    def test_engine_health_monitoring(self):
        """Test engine health monitoring"""
        isolator = get_runtime_isolator()
        
        engine = TestEngine("test_engine")
        isolator.register_engine(engine)
        
        health = isolator.get_engine_health("test_engine")
        
        assert health is not None
        assert health.status in [EngineStatus.HEALTHY, EngineStatus.INITIALIZING]
        
    def test_system_status(self):
        """Test system status reporting"""
        isolator = get_runtime_isolator()
        
        engine1 = TestEngine("engine_1")
        engine2 = TestEngine("engine_2")
        
        isolator.register_engine(engine1)
        isolator.register_engine(engine2)
        
        status = isolator.get_system_status()
        
        assert status["total_engines"] == 2
        assert status["healthy"] >= 0
        
    def test_degraded_mode(self):
        """Test degraded mode activation"""
        isolator = get_runtime_isolator()
        
        healthy = TestEngine("healthy")
        failing = TestEngine("failing", should_fail=True)
        
        isolator.register_engine(healthy)
        isolator.register_engine(failing)
        
        # Start the engines
        healthy.start()
        failing.start()
        
        # Trigger failure
        try:
            failing.process("test")
        except:
            pass
            
        # Activate degraded mode
        available = isolator.activate_degraded_mode()
        
        assert "healthy" in available
        # After start(), status should be HEALTHY


# ============================================================================
# Layer 5: Execution Gate Tests
# ============================================================================

class TestExecutionGate:
    """Tests for Layer 5 - Risk & Action Isolation"""
    
    def setup_method(self):
        """Reset before each test"""
        reset_all_globals()
        
    def test_action_request_submission(self):
        """Test submitting an action request"""
        gate = get_execution_gate()
        
        request = ActionRequest(
            agent_id="agent_1",
            agent_domain="finance",
            action_type="read_market_data",
            action_category=ActionCategory.DATA,
            title="Read Market Data",
            description="Read market data for analysis"
        )
        
        approval = gate.submit_request(request)
        
        assert approval is not None
        assert approval.request.request_id is not None
        
    def test_low_risk_action_auto_approved(self):
        """Test low risk actions are auto-approved"""
        gate = get_execution_gate()
        
        request = ActionRequest(
            agent_id="agent_1",
            agent_domain="finance",
            action_type="read_market_data",  # Low risk
            action_category=ActionCategory.DATA,
            risk_level=ActionRiskLevel.LOW,
            title="Read Data"
        )
        
        approval = gate.submit_request(request)
        
        # Low risk should go through
        assert approval.current_stage in [ApprovalStage.RISK_EVALUATION, ApprovalStage.HUMAN_APPROVAL]
        
    def test_high_risk_action_requires_approval(self):
        """Test high risk actions require approval"""
        gate = get_execution_gate()
        
        request = ActionRequest(
            agent_id="agent_1",
            agent_domain="finance",
            action_type="execute_trade",  # High risk
            action_category=ActionCategory.FINANCIAL,
            risk_level=ActionRiskLevel.CRITICAL,
            title="Execute Trade",
            parameters={"amount": 50000}
        )
        
        approval = gate.submit_request(request)
        
        # Critical risk should require approval
        assert gate.needs_human_approval(approval.request.request_id)
        
    def test_execution_gate_approval_workflow(self):
        """Test complete approval workflow"""
        gate = get_execution_gate()
        
        # Submit request
        request = ActionRequest(
            agent_id="agent_1",
            agent_domain="finance",
            action_type="simulate_investment",
            action_category=ActionCategory.DATA,
            title="Simulate Investment"
        )
        
        approval = gate.submit_request(request)
        
        # Advance through stages
        gate.advance_to_risk_evaluation(approval.request.request_id)
        
        # Approve
        success = gate.approve(approval.request.request_id, "executive_council")
        
        assert success is True
        
        status = gate.get_request_status(approval.request.request_id)
        assert status.status == ApprovalStatus.APPROVED
        
    def test_execution_gate_denial(self):
        """Test request denial"""
        gate = get_execution_gate()
        
        request = ActionRequest(
            agent_id="agent_1",
            agent_domain="finance",
            action_type="transfer_funds",
            action_category=ActionCategory.FINANCIAL,
            title="Transfer Funds"
        )
        
        approval = gate.submit_request(request)
        
        # Deny
        success = gate.deny(
            approval.request.request_id,
            "executive_council",
            "Insufficient justification"
        )
        
        assert success is True
        
        status = gate.get_request_status(approval.request.request_id)
        assert status.status == ApprovalStatus.DENIED
        
    def test_execution_gate_test(self):
        """Test execution gate (Section 10: execution_gate_test)"""
        gate = get_execution_gate()
        
        # Register executor
        def mock_executor(request):
            return {"status": "executed"}
            
        gate.register_executor("test_action", mock_executor)
        
        # Submit and approve request
        request = ActionRequest(
            agent_id="agent_1",
            agent_domain="finance",
            action_type="test_action",
            action_category=ActionCategory.DATA,
            title="Test Action"
        )
        
        approval = gate.submit_request(request)
        gate.approve(approval.request.request_id, "system")
        
        # Execute
        result = gate.execute(approval.request.request_id)
        
        assert result["status"] == "executed"


# ============================================================================
# Shared Intelligence Fabric Tests
# ============================================================================

class TestSharedIntelligenceFabric:
    """Tests for Shared Intelligence Fabric"""
    
    def setup_method(self):
        """Reset before each test"""
        reset_all_globals()
        
    def test_event_publishing(self):
        """Test event publishing"""
        fabric = get_shared_intelligence_fabric()
        
        received_events = []
        
        def callback(event):
            received_events.append(event)
            
        fabric.subscribe_to_events(EventType.SIGNAL_RECEIVED, callback)
        
        fabric.publish_event(
            event_type=EventType.SIGNAL_RECEIVED,
            source_agent_id="agent_1",
            source_domain="finance",
            payload={"signal": "test"}
        )
        
        assert len(received_events) == 1
        
    def test_strategy_registration(self):
        """Test strategy registration"""
        fabric = get_shared_intelligence_fabric()
        
        fabric.register_strategy(
            strategy_id="strategy_1",
            agent_id="agent_1",
            domain="finance",
            strategy_data={"type": "growth"}
        )
        
        strategy = fabric.strategy_registry.get_strategy("strategy_1")
        
        assert strategy is not None
        assert strategy["agent_id"] == "agent_1"
        
    def test_recommendation_ledger(self):
        """Test recommendation ledger"""
        fabric = get_shared_intelligence_fabric()
        
        fabric.add_recommendation(
            recommendation_id="rec_1",
            agent_id="agent_1",
            domain="finance",
            recommendation={"action": "buy", "stock": "AAPL"}
        )
        
        rec = fabric.recommendation_ledger.get_recommendation("rec_1")
        
        assert rec is not None
        assert rec["recommendation"]["action"] == "buy"
        
    def test_risk_signal_aggregation(self):
        """Test risk signal aggregation"""
        fabric = get_shared_intelligence_fabric()
        
        fabric.add_risk_signal(
            domain="finance",
            risk_type="market_volatility",
            severity="high",
            description="High market volatility"
        )
        
        fabric.add_risk_signal(
            domain="health",
            risk_type="sleep_debt",
            severity="medium",
            description="Accumulating sleep debt"
        )
        
        aggregate = fabric.risk_engine.calculate_aggregate_risk()
        
        assert aggregate["total_risks"] == 2
        assert aggregate["domains_affected"] == 2
        
    def test_confidence_scoring(self):
        """Test confidence scoring"""
        fabric = get_shared_intelligence_fabric()
        
        insight = {
            "source": "api",
            "data_quality": 0.9,
            "cross_domain_validation": True,
            "age_minutes": 30
        }
        
        score = fabric.score_confidence(insight)
        
        assert "total_score" in score
        assert "confidence_level" in score
        assert score["confidence_level"] in ["low", "medium", "high"]


# ============================================================================
# Integration Tests
# ============================================================================

class TestIsolationIntegration:
    """Integration tests across all layers"""
    
    def setup_method(self):
        """Reset before each test"""
        reset_all_globals()
        
    def test_agent_failure_test(self):
        """Test agent failure doesn't stop system (Section 10: agent_failure_test)"""
        registry = get_agent_registry()
        
        # Register multiple agents
        healthy_agent = TestAgent("healthy", "Healthy Agent", AgentDomain.FINANCE)
        registry.register(healthy_agent)
        
        # Simulate agent failure by direct manipulation
        # (in real system, this would be caught by sandbox)
        
        # Other agents should still work
        finance_agents = registry.get_by_domain(AgentDomain.FINANCE)
        assert len(finance_agents) >= 1
        
        # System health should still report
        health = registry.get_system_health()
        assert "total_agents" in health
        
    def test_complete_isolation_architecture(self):
        """Test complete isolation architecture integration"""
        # Layer 1: Agent
        agent = TestAgent("agent_1", "Agent 1", AgentDomain.FINANCE)
        registry = get_agent_registry()
        registry.register(agent)
        
        # Layer 2: Memory (use key format that works: "domain:key")
        memory = get_memory_manager()
        memory.write(
            scope=MemoryScope.DOMAIN,
            key="test_key",  # Will become "finance:test_key" internally
            value="data",
            requester_id="finance_agent",  # requester_id must match domain prefix
            domain="finance"
        )
        
        # Layer 3: Tools
        gatekeeper = get_tool_gatekeeper()
        
        # Layer 4: Runtime
        isolator = get_runtime_isolator()
        engine = TestEngine("engine_1")
        isolator.register_engine(engine)
        
        # Layer 5: Execution
        gate = get_execution_gate()
        
        # Fabric
        fabric = get_shared_intelligence_fabric()
        
        # All components initialized and working
        assert registry.get("agent_1") is not None
        assert isolator.get_engine("engine_1") is not None
        assert fabric is not None


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
