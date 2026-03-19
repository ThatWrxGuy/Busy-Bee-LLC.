"""
BB-ARCH-ISO-001 Usage Example

This example demonstrates how to use the five-layer isolation architecture.

Layers:
1. Agent Sandbox (Cognitive Isolation)
2. Memory Scope Manager (Data & Memory Isolation)
3. Tool Gatekeeper (Tool & Permission Isolation)
4. Runtime Isolator (Runtime Execution Isolation)
5. Execution Gate (Risk & Action Isolation)
"""

from infrastructure.isolation import (
    # Layer 1: Cognitive Isolation
    AgentSandbox,
    AgentSandboxRegistry,
    AgentContext,
    AgentDomain,
    get_agent_registry,
    
    # Layer 2: Memory Isolation
    MemoryScope,
    get_memory_manager,
    
    # Layer 3: Permission Isolation
    get_tool_gatekeeper,
    GatekeeperRequest,
    GatekeeperDecision,
    
    # Layer 4: Runtime Isolation
    RuntimeIsolator,
    IsolatedEngine,
    EngineConfig,
    EngineType,
    get_runtime_isolator,
    
    # Layer 5: Action Isolation
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


# ============================================================================
# Example 1: Agent Cognitive Isolation
# ============================================================================

class FinanceAgent(AgentSandbox):
    """Example finance agent"""
    
    def _reason(self, context: AgentContext) -> dict:
        # Analyze signals
        insights = []
        
        for signal in context.available_signals:
            if signal.get("type") == "market_data":
                insights.append({
                    "type": "market_analysis",
                    "title": "Market Opportunity Detected",
                    "confidence": 0.85,
                    "data": signal
                })
        
        return {
            "insights": insights,
            "risk_signals": [],
            "recommendations": [
                {
                    "action": "analyze_portfolio",
                    "priority": "high"
                }
            ]
        }


def example_agent_isolation():
    """Demonstrate agent cognitive isolation"""
    print("\n=== Example 1: Agent Cognitive Isolation ===\n")
    
    # Create agent
    finance_agent = FinanceAgent(
        agent_id="finance_strategist_1",
        name="Finance Strategist",
        domain=AgentDomain.FINANCE
    )
    
    # Register
    registry = get_agent_registry()
    registry.register(finance_agent)
    
    # Create context with signals
    context = AgentContext(
        agent_id="finance_strategist_1",
        domain=AgentDomain.FINANCE,
        available_signals=[
            {"id": "sig_1", "type": "market_data", "value": {"stocks": "AAPL", "price": 150}}
        ],
        domain_memory={},
        shared_intelligence={}
    )
    
    # Execute in sandbox
    output = finance_agent.execute(context)
    
    print(f"Agent: {output.agent_id}")
    print(f"Domain: {output.domain.value}")
    print(f"Insights generated: {len(output.insights)}")
    print(f"Execution time: {output.execution_time_ms:.2f}ms")
    print(f"✅ Agent isolation working - output is structured and bounded")


# ============================================================================
# Example 2: Memory Scope Isolation
# ============================================================================

def example_memory_isolation():
    """Demonstrate memory scope isolation"""
    print("\n=== Example 2: Memory Scope Isolation ===\n")
    
    memory = get_memory_manager()
    
    # Layer 2a: Agent Working Memory (private)
    memory.write(
        scope=MemoryScope.AGENT_WORKING,
        key="temp_analysis",
        value={"intermediate_result": 42},
        requester_id="agent_1"
    )
    
    # Layer 2b: Domain Memory (isolated by domain)
    memory.write(
        scope=MemoryScope.DOMAIN,
        key="portfolio",
        value={"stocks": ["AAPL", "GOOGL"]},
        requester_id="finance_agent",
        domain="finance"
    )
    
    # Layer 2c: Shared Strategic Memory (accessible by all)
    memory.write(
        scope=MemoryScope.SHARED_STRATEGIC,
        key="strategic_priority",
        value="financial_independence",
        requester_id="finance_agent"
    )
    
    # Layer 2d: Audit Memory (append-only)
    audit_entry = memory.audit_log(
        entry_type="recommendation",
        data={"action": "invest", "amount": 10000},
        actor_id="finance_strategist_1"
    )
    
    print(f"✅ Agent working memory: {memory.read(MemoryScope.AGENT_WORKING, 'temp_analysis', 'agent_1')}")
    print(f"✅ Domain memory (finance): {memory.read(MemoryScope.DOMAIN, 'portfolio', 'finance_agent', 'finance')}")
    print(f"✅ Shared memory accessible: {memory.read(MemoryScope.SHARED_STRATEGIC, 'strategic_priority', 'health_agent')}")
    print(f"✅ Audit entry created: {audit_entry.id[:20]}...")


# ============================================================================
# Example 3: Tool Permission Isolation
# ============================================================================

def example_tool_isolation():
    """Demonstrate tool permission isolation"""
    print("\n=== Example 3: Tool Permission Isolation ===\n")
    
    gatekeeper = get_tool_gatekeeper()
    
    # Check access to L1 tool (read-only)
    request_l1 = GatekeeperRequest(
        request_id="req_1",
        agent_id="finance_agent",
        agent_domain="finance",
        tool_id="read_market_data",
        parameters={}
    )
    response_l1 = gatekeeper.check_access(request_l1)
    
    # Check access to L5 tool (external action)
    request_l5 = GatekeeperRequest(
        request_id="req_2",
        agent_id="finance_agent",
        agent_domain="finance",
        tool_id="execute_trade",
        parameters={"symbol": "AAPL", "quantity": 100}
    )
    response_l5 = gatekeeper.check_access(request_l5)
    
    print(f"L1 tool (read_market_data): {response_l1.decision.value}")
    print(f"L5 tool (execute_trade): {response_l5.decision.value}")
    print(f"✅ Tool gatekeeper enforces risk-based access control")


# ============================================================================
# Example 4: Runtime Engine Isolation
# ============================================================================

class AnalysisEngine(IsolatedEngine):
    """Example analysis engine"""
    
    def _perform_recovery(self) -> None:
        print(f"  🔧 Recovering engine: {self.config.engine_id}")
    
    def process(self, data: dict) -> dict:
        return {"result": f"Analysis complete for {data.get('input', 'unknown')}"}


def example_runtime_isolation():
    """Demonstrate runtime engine isolation"""
    print("\n=== Example 4: Runtime Engine Isolation ===\n")
    
    isolator = get_runtime_isolator()
    
    # Create and register engine
    config = EngineConfig(
        engine_id="analysis_engine",
        engine_type=EngineType.RECOMMENDATION,
        timeout_ms=5000
    )
    engine = AnalysisEngine(config)
    isolator.register_engine(engine)
    
    # Execute through isolator
    result = isolator.execute_engine(
        "analysis_engine",
        engine.process,
        {"input": "portfolio"}
    )
    
    print(f"Engine result: {result}")
    print(f"System status: {isolator.get_system_status()}")
    print(f"✅ Runtime isolator provides fault containment")


# ============================================================================
# Example 5: Execution Gate
# ============================================================================

def example_execution_gate():
    """Demonstrate execution gate approval workflow"""
    print("\n=== Example 5: Execution Gate ===\n")
    
    gate = get_execution_gate()
    
    # Register executor
    def trade_executor(request):
        return {"status": "executed", "trade_id": "T12345"}
    
    gate.register_executor("execute_trade", trade_executor)
    
    # Submit high-risk action
    request = ActionRequest(
        agent_id="finance_strategist_1",
        agent_domain="finance",
        action_type="execute_trade",
        action_category=ActionCategory.FINANCIAL,
        risk_level=ActionRiskLevel.CRITICAL,
        title="Execute Trade",
        description="Buy 100 shares of AAPL",
        parameters={"symbol": "AAPL", "quantity": 100, "amount": 15000}
    )
    
    approval = gate.submit_request(request)
    print(f"Request submitted: {approval.request.request_id[:20]}...")
    print(f"Needs human approval: {gate.needs_human_approval(approval.request.request_id)}")
    
    # Approve and execute
    gate.approve(approval.request.request_id, "executive_council")
    result = gate.execute(approval.request.request_id)
    
    print(f"Execution result: {result}")
    print(f"✅ Execution gate ensures human approval for critical actions")


# ============================================================================
# Example 6: Shared Intelligence Fabric
# ============================================================================

def example_fabric():
    """Demonstrate shared intelligence fabric"""
    print("\n=== Example 6: Shared Intelligence Fabric ===\n")
    
    fabric = get_shared_intelligence_fabric()
    
    # Publish event
    fabric.publish_event(
        event_type=EventType.INSIGHT_GENERATED,
        source_agent_id="finance_strategist_1",
        source_domain="finance",
        payload={"insight": "Growth opportunity detected"}
    )
    
    # Register strategy
    fabric.register_strategy(
        strategy_id="strat_1",
        agent_id="finance_strategist_1",
        domain="finance",
        strategy_data={"type": "growth", "timeline": "12 months"}
    )
    
    # Add risk signal
    fabric.add_risk_signal(
        domain="finance",
        risk_type="market_volatility",
        severity="medium",
        description="Increased market volatility detected"
    )
    
    # Get aggregate risk
    risk = fabric.risk_engine.calculate_aggregate_risk()
    
    print(f"Strategy registry entries: {len(fabric.strategy_registry._strategies)}")
    print(f"Aggregate risk level: {risk['risk_level']}")
    print(f"✅ Fabric enables cross-domain intelligence sharing")


# ============================================================================
# Run All Examples
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("BB-ARCH-ISO-001: Agent & Engine Isolation Architecture")
    print("="*60)
    
    example_agent_isolation()
    example_memory_isolation()
    example_tool_isolation()
    example_runtime_isolation()
    example_execution_gate()
    example_fabric()
    
    print("\n" + "="*60)
    print("All examples completed successfully! ✅")
    print("="*60)
    print("""
Summary: The five-layer isolation architecture provides:
  1. Cognitive Isolation - Agents have bounded reasoning
  2. Memory Isolation - Strict memory access boundaries
  3. Tool Isolation - Risk-based permission enforcement
  4. Runtime Isolation - Engine fault containment
  5. Action Isolation - Human approval for critical actions
""")
