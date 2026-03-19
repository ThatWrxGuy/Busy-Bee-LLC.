"""
Runtime Architecture Tests - BB-ARCH-ISO-002

Tests for BB-ARCH-ISO-002 Agent Sandbox & Container Runtime Architecture:
- Agent Orchestrator
- Sandbox Runtime
- Capability Token Service
- Resource Governor
"""

import pytest
import time
import threading
from datetime import datetime, timedelta

from infrastructure.runtime import (
    AgentOrchestrator,
    DevelopmentSandbox,
    AgentConfig,
    AgentContainer,
    AgentHealth,
    AgentStatus,
    RuntimeMode,
    get_agent_orchestrator,
    reset_agent_orchestrator,
    
    CapabilityTokenService,
    CapabilityRegistry,
    CapabilityToken,
    get_capability_token_service,
    reset_capability_token_service,
    
    ResourceGovernor,
    ResourceLimit,
    ResourceType,
    AgentResources,
    ExecutionTimer,
    ResourceLimitExceeded,
    get_resource_governor,
    reset_resource_governor,
)


def reset_all():
    """Reset all global instances"""
    reset_agent_orchestrator()
    reset_capability_token_service()
    reset_resource_governor()


# ============================================================================
# Agent Orchestrator Tests
# ============================================================================

class TestAgentOrchestrator:
    """Tests for Agent Orchestrator"""
    
    def setup_method(self):
        reset_all()
        
    def test_create_agent_config(self):
        """Test agent configuration creation"""
        config = AgentConfig(
            agent_id="test_agent",
            name="Test Agent",
            domain="finance",
            runtime_mode=RuntimeMode.DEVELOPMENT
        )
        
        assert config.agent_id == "test_agent"
        assert config.name == "Test Agent"
        assert config.runtime_mode == RuntimeMode.DEVELOPMENT
        
    def test_start_agent(self):
        """Test starting an agent"""
        orchestrator = get_agent_orchestrator()
        
        config = AgentConfig(
            agent_id="finance_agent",
            name="Finance Agent",
            domain="finance"
        )
        orchestrator.register_agent_config(config)
        
        success = orchestrator.start_agent("finance_agent")
        
        assert success is True
        assert orchestrator.get_agent_status("finance_agent") == AgentStatus.RUNNING
        
    def test_stop_agent(self):
        """Test stopping an agent"""
        orchestrator = get_agent_orchestrator()
        
        config = AgentConfig(agent_id="test_agent", name="Test", domain="finance")
        orchestrator.register_agent_config(config)
        orchestrator.start_agent("test_agent")
        
        success = orchestrator.stop_agent("test_agent")
        
        assert success is True
        assert orchestrator.get_agent_status("test_agent") == AgentStatus.STOPPED
        
    def test_restart_agent(self):
        """Test restarting an agent"""
        orchestrator = get_agent_orchestrator()
        
        config = AgentConfig(agent_id="test_agent", name="Test", domain="finance")
        orchestrator.register_agent_config(config)
        orchestrator.start_agent("test_agent")
        
        success = orchestrator.restart_agent("test_agent")
        
        assert success is True
        
    def test_agent_health_monitoring(self):
        """Test agent health monitoring"""
        orchestrator = get_agent_orchestrator()
        
        config = AgentConfig(agent_id="test_agent", name="Test", domain="finance")
        orchestrator.register_agent_config(config)
        orchestrator.start_agent("test_agent")
        
        health = orchestrator.get_agent_health("test_agent")
        
        assert health is not None
        assert health.agent_id == "test_agent"
        
    def test_system_status(self):
        """Test system status"""
        orchestrator = get_agent_orchestrator()
        
        config = AgentConfig(agent_id="agent1", name="Agent 1", domain="finance")
        orchestrator.register_agent_config(config)
        orchestrator.start_agent("agent1")
        
        status = orchestrator.get_system_status()
        
        assert status["total_agents"] >= 1
        assert "running" in status


# ============================================================================
# Capability Token Service Tests
# ============================================================================

class TestCapabilityTokenService:
    """Tests for Capability Token Service"""
    
    def setup_method(self):
        reset_all()
        
    def test_capability_registry(self):
        """Test capability registry"""
        registry = CapabilityRegistry()
        
        cap = registry.get_capability("read_financial_data")
        
        assert cap is not None
        assert cap.name == "read_financial_data"
        
    def test_issue_token(self):
        """Test issuing capability token"""
        service = get_capability_token_service()
        
        token = service.issue_token(
            agent_id="finance_agent",
            capability_names=["read_financial_data", "publish_strategy"]
        )
        
        assert token is not None
        assert token.agent_id == "finance_agent"
        assert "read_financial_data" in token.capabilities
        
    def test_verify_token(self):
        """Test verifying token capabilities"""
        service = get_capability_token_service()
        
        token = service.issue_token(
            agent_id="finance_agent",
            capability_names=["read_financial_data"]
        )
        
        assert service.verify_token(token.token_id, "read_financial_data") is True
        assert service.verify_token(token.token_id, "execute_trade") is False
        
    def test_revoke_token(self):
        """Test revoking token"""
        service = get_capability_token_service()
        
        token = service.issue_token(
            agent_id="finance_agent",
            capability_names=["read_financial_data"]
        )
        
        success = service.revoke_token(token.token_id)
        
        assert success is True
        assert token.is_active is False
        
    def test_capability_requires_approval(self):
        """Test checking if capability requires approval"""
        registry = CapabilityRegistry()
        
        assert registry.requires_approval("execute_trade") is True
        assert registry.requires_approval("read_financial_data") is False


# ============================================================================
# Resource Governor Tests
# ============================================================================

class TestResourceGovernor:
    """Tests for Resource Governor"""
    
    def setup_method(self):
        reset_all()
        
    def test_set_limits(self):
        """Test setting resource limits"""
        governor = get_resource_governor()
        
        limits = {
            ResourceType.CPU: ResourceLimit(ResourceType.CPU, 25.0, "%"),
            ResourceType.MEMORY: ResourceLimit(ResourceType.MEMORY, 1024.0, "MB")
        }
        
        governor.set_limits("test_agent", limits)
        
        agent_limits = governor.get_limits("test_agent")
        
        assert ResourceType.CPU in agent_limits
        assert agent_limits[ResourceType.CPU].limit == 25.0
        
    def test_check_limits_ok(self):
        """Test checking limits when within bounds"""
        governor = get_resource_governor()
        
        governor.update_usage("test_agent", cpu_percent=10.0, memory_mb=100.0)
        
        result = governor.check_limits("test_agent")
        
        assert result["status"] == "ok"
        
    def test_check_limits_violation(self):
        """Test checking limits when exceeded"""
        governor = get_resource_governor()
        
        governor.update_usage("test_agent", cpu_percent=50.0, memory_mb=1000.0)
        
        result = governor.check_limits("test_agent")
        
        assert result["status"] == "violation"
        assert len(result["violations"]) > 0
        
    def test_execution_timer(self):
        """Test execution timer context manager"""
        governor = get_resource_governor()
        
        with ExecutionTimer(governor, "test_agent", max_seconds=2.0):
            time.sleep(0.1)
            
        usage = governor.get_usage("test_agent")
        
        assert usage is not None
        assert usage.execution_time_seconds > 0
        
    def test_execution_timer_exceeded(self):
        """Test execution timer when limit exceeded"""
        governor = get_resource_governor()
        
        with pytest.raises(ResourceLimitExceeded):
            with ExecutionTimer(governor, "test_agent", max_seconds=0.1):
                time.sleep(0.2)
                
    def test_system_summary(self):
        """Test system resource summary"""
        governor = get_resource_governor()
        
        governor.update_usage("agent1", cpu_percent=10.0, memory_mb=100.0)
        governor.update_usage("agent2", cpu_percent=20.0, memory_mb=200.0)
        
        summary = governor.get_system_summary()
        
        assert summary["total_agents"] == 2
        assert summary["total_cpu_percent"] == 30.0
        assert summary["total_memory_mb"] == 300.0


# ============================================================================
# Integration Tests
# ============================================================================

class TestRuntimeIntegration:
    """Integration tests for runtime architecture"""
    
    def setup_method(self):
        reset_all()
        
    def test_agent_with_capabilities(self):
        """Test agent with capability tokens"""
        # Start agent
        orchestrator = get_agent_orchestrator()
        config = AgentConfig(
            agent_id="finance_agent",
            name="Finance Agent",
            domain="finance"
        )
        orchestrator.register_agent_config(config)
        orchestrator.start_agent("finance_agent")
        
        # Issue capabilities
        service = get_capability_token_service()
        token = service.issue_token(
            agent_id="finance_agent",
            capability_names=["read_financial_data", "publish_strategy"]
        )
        
        # Verify capabilities
        assert service.verify_token(token.token_id, "read_financial_data") is True
        
    def test_agent_with_resource_limits(self):
        """Test agent with resource limits"""
        orchestrator = get_agent_orchestrator()
        governor = get_resource_governor()
        
        # Configure agent with custom limits
        config = AgentConfig(
            agent_id="test_agent",
            name="Test Agent",
            domain="finance",
            max_cpu_percent=30.0,
            max_memory_mb=1024.0
        )
        orchestrator.register_agent_config(config)
        orchestrator.start_agent("test_agent")
        
        # Set custom limits
        limits = {
            ResourceType.CPU: ResourceLimit(ResourceType.CPU, 30.0, "%"),
            ResourceType.MEMORY: ResourceLimit(ResourceType.MEMORY, 1024.0, "MB")
        }
        governor.set_limits("test_agent", limits)
        
        # Verify limits
        agent_limits = governor.get_limits("test_agent")
        assert agent_limits[ResourceType.CPU].limit == 30.0
        
    def test_full_runtime_lifecycle(self):
        """Test complete agent lifecycle"""
        orchestrator = get_agent_orchestrator()
        service = get_capability_token_service()
        governor = get_resource_governor()
        
        # Create and start agent
        config = AgentConfig(
            agent_id="lifecycle_agent",
            name="Lifecycle Agent",
            domain="health"
        )
        orchestrator.register_agent_config(config)
        orchestrator.start_agent("lifecycle_agent")
        
        # Issue token
        token = service.issue_token(
            agent_id="lifecycle_agent",
            capability_names=["read_health_data"]
        )
        
        # Update resources
        governor.update_usage(
            "lifecycle_agent",
            cpu_percent=5.0,
            memory_mb=50.0,
            execution_time_seconds=0.5
        )
        
        # Check health
        health = orchestrator.get_agent_health("lifecycle_agent")
        assert health.status == AgentStatus.RUNNING
        
        # Stop agent
        orchestrator.stop_agent("lifecycle_agent")
        assert orchestrator.get_agent_status("lifecycle_agent") == AgentStatus.STOPPED
        
        # Revoke tokens
        service.revoke_all_agent_tokens("lifecycle_agent")
        assert len(service.get_agent_tokens("lifecycle_agent")) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
