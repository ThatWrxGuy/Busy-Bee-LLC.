"""
PSIP - Personal Strategic Intelligence Platform

A comprehensive system implementing the PSIP-001 directive.

Architecture:
- Layer 1: Strategic Intelligence Core (Strategy Lab, Simulation Engine, etc.)
- Layer 2: Governance Layer (Executive Council, Risk Governor, etc.)
- Layer 3: Domain Intelligence Systems (Finance, Health, Career, etc.)
- Infrastructure: Memory Engine, Signal System
- Outputs: Executive Briefs, Domain Reports

This is the main entry point for the PSIP system.
"""

import logging
from enum import StrEnum
from typing import Any

# Module logger
logger = logging.getLogger(__name__)

# Module imports to avoid namespace pollution and name collisions
import layer1_strategic_intelligence_core as core
import layer2_governance_layer as governance
import layer3_domain_intelligence as domain
import infrastructure as infra
import outputs

from infrastructure.signal_ingestion import (
    SignalIngestionManager, IngestionResult, IngestionStatus,
    SignalConnectorRegistry, ConnectorConfig, ConnectorCategory,
    SignalNormalizer, CanonicalSignal, SignalDomain,
    SignalValidator, ValidationResult,
    SignalCache, get_signal_cache,
    SignalHealthMonitor, HealthStatus, get_health_monitor,
    get_ingestion_manager
)

from infrastructure.intelligence_cycle import (
    IntelligenceCycleManager, IntelligenceCycleResult,
    CycleScheduler, CycleSchedule, CycleExecution, CycleFrequency,
    SignalRefreshEngine, RefreshResult,
    StrategyTriggerEngine, TriggerResult,
    CouncilTriggerEngine, CouncilTriggerResult,
    ReportingTriggerEngine, ReportTriggerResult,
    get_intelligence_cycle_manager
)

from infrastructure.life_graph import (
    LifeSignalGraph, get_life_graph,
    GraphNode, GraphEdge, NodeType, Domain, InfluenceType,
    RelationshipEngine, get_relationship_engine,
    GraphBuilder, get_graph_builder,
    GraphQueryEngine, get_graph_query_engine
)

from infrastructure.digital_twin import (
    DigitalTwinModel, get_digital_twin,
    LeverageDiscoveryEngine, get_leverage_discovery_engine,
    LeverageOpportunity, LeverageResult
)

# BB-FIN-021: Finance Trade Intelligence
TRADE_INTELLIGENCE_AVAILABLE = False
try:
    from finance_trade_intelligence_service import (
        get_latest_spy0dte_trade_insight,
        build_trade_opportunity,
        build_trade_risk,
        build_trade_action,
        build_finance_trade_summary_appendix
    )
    TRADE_INTELLIGENCE_AVAILABLE = True
except Exception as e:
    logger.debug("Trade intelligence unavailable: %s", e)


class PSIP:
    """
    Personal Strategic Intelligence Platform
    
    Main class that orchestrates all PSIP components.
    
    This is a façade over the PSIP system. For production use, prefer
    create_psip() factory which handles dependency injection properly.
    """
    
    def __init__(
        self,
        total_capital: float = 100000,
        # Optional injected dependencies for testing
        domains: dict[str, domain.ChiefOfficer] | None = None,
        signal_system: infra.SignalSystem | None = None,
        memory: infra.MemoryEngine | None = None,
        executive_council: governance.ExecutiveCouncil | None = None,
        risk_governor: governance.RiskGovernor | None = None,
        brief_generator: outputs.ExecutiveBriefGenerator | None = None,
        intelligence_cycle: IntelligenceCycleManager | None = None,
    ):
        # Layer 1: Strategic Intelligence Core
        self.strategy_lab = core.StrategyLab()
        self.simulation_engine = core.SimulationEngine()
        self.edge_discovery = core.EdgeDiscoveryEngine()
        self.knowledge_graph = core.KnowledgeGraph()
        self.learning_engine = core.LearningEngine()
        self.scenario_planner = core.ScenarioPlanner()
        self.signal_fusion = core.SignalFusionEngine()
        
        # Layer 2: Governance Layer
        self.executive_council = executive_council or governance.ExecutiveCouncil()
        self.risk_governor = risk_governor or governance.RiskGovernor()
        self.execution_gate = governance.ExecutionGateManager()
        self.capital_coordinator = governance.CapitalDeploymentCoordinator(total_capital)
        self.priority_router = governance.PriorityRouter()
        
        # Layer 3: Domain Intelligence (use injected or build from DOMAIN_CONFIG)
        if domains is not None:
            self.domains = domains
        else:
            # Build domains from centralized DOMAIN_CONFIG
            self.domains = {
                domain_name.value: config.chief_class()
                for domain_name, config in DOMAIN_CONFIG.items()
            }
        
        # Infrastructure (use injected or create new)
        self.memory = memory or infra.MemoryEngine()
        self.signal_system = signal_system or infra.SignalSystem()
        
        # BB-INF-007: Signal Ingestion Layer
        self.ingestion_manager = get_ingestion_manager()
        self.signal_cache = get_signal_cache()
        self.health_monitor = get_health_monitor()
        
        # BB-INF-007: Intelligence Cycle
        self.intelligence_cycle = intelligence_cycle or get_intelligence_cycle_manager()
        
        # BB-INF-008: Life Signal Graph
        self.life_graph = get_life_graph()
        self.relationship_engine = get_relationship_engine()
        self.graph_builder = get_graph_builder()
        self.graph_query = get_graph_query_engine()
        
        # BB-INF-008: Digital Twin
        self.digital_twin = get_digital_twin()
        self.leverage_discovery = get_leverage_discovery_engine()
        
        # Outputs
        self.brief_generator = brief_generator or outputs.ExecutiveBriefGenerator()
        
        # Initialize governance from DOMAIN_CONFIG
        self._initialize_governance()
    
    def _initialize_governance(self) -> None:
        """Initialize governance layer from DOMAIN_CONFIG"""
        # Add council members and risk thresholds from centralized config
        for domain_name, config in DOMAIN_CONFIG.items():
            domain_key = domain_name.value
            
            # Use derived properties from DomainConfig
            self.executive_council.add_member(
                config.member_id,
                config.short_name,
                config.title,
                domain_key,
                config.governance.priority_weight,
            )
            
            # Add risk thresholds from governance config
            thresholds = config.governance
            self.risk_governor.add_threshold(
                domain_key, 
                thresholds.risk_threshold_high, 
                thresholds.risk_threshold_medium, 
                thresholds.risk_threshold_low
            )
            
            # Add domain priority (using fixed priority for now)
            self.priority_router.add_domain_priority(domain_key, 5)
    
    def process_signal(self, signal_data: dict[str, Any]) -> infra.Signal:
        """Process an incoming signal through the full pipeline"""
        # 1. Emit signal
        signal = self.signal_system.emit(
            source=signal_data.get("source", "unknown"),
            signal_type=signal_data.get("type", "general"),
            domain=signal_data.get("domain", "general"),
            payload=signal_data.get("payload", {}),
            priority=infra.SignalPriority.NORMAL
        )
        
        # 2. Store in memory (store normalized record, not raw input)
        self.memory.store(
            memory_type="signal",
            content={
                "id": signal.id,
                "source": signal.source,
                "signal_type": signal.signal_type,
                "domain": signal.domain,
                "payload": signal.payload,
            },
            domain=signal.domain,
            importance=signal_data.get("importance", 0.5)
        )
        
        return signal
    
    def analyze_domain(self, domain: str) -> dict[str, Any]:
        """Analyze a specific domain"""
        if domain not in self.domains:
            return {"error": "Domain not found"}
        
        chief = self.domains[domain]
        
        # Get signals for domain
        signals = self.signal_system.get_signals_by_domain(domain)
        
        # Convert to DomainSignal format using the mapper
        domain_signals = self._map_signals_to_domain(signals)
        
        # Analyze
        analysis = chief.analyze_signals(domain_signals)
        
        # Generate strategy
        strategy = chief.generate_strategy(analysis)
        
        return {
            "domain": domain,
            "analysis": analysis,
            "strategy": {
                "id": strategy.id,
                "title": strategy.title,
                "priority": strategy.priority,
                "action_items": strategy.action_items
            },
            "status": chief.get_domain_status()
        }
    
    def _map_signals_to_domain(self, signals: list[infra.Signal]) -> list[domain.DomainSignal]:
        """Map infrastructure signals to domain signals"""
        return [
            domain.DomainSignal(
                id=s.id,
                domain=s.domain,
                signal_type=s.signal_type,
                title=s.payload.get("title", ""),
                description=s.payload.get("description", ""),
                data=s.payload,
                strength=s.payload.get("strength", 0.5),
                confidence=s.payload.get("confidence", 0.5)
            )
            for s in signals
        ]
    
    def generate_executive_brief(self, include_trade_intelligence: bool = True) -> outputs.ExecutiveBrief:
        """Generate an executive brief
        
        Args:
            include_trade_intelligence: Whether to include SPY 0DTE trade intelligence
        """
        # Orchestrate the various steps
        self._refresh_domain_analyses()
        domain_reports = self._collect_domain_reports()
        strategy_status = self._build_strategy_status()
        risk_summary = self._build_risk_summary()

        # Apply trade intelligence if requested
        if include_trade_intelligence and TRADE_INTELLIGENCE_AVAILABLE:
            domain_reports, tactical_trade_insights = self._apply_trade_intelligence(domain_reports)
        else:
            tactical_trade_insights = []

        # Generate brief with trade intelligence
        brief = self.brief_generator.generate(
            domain_reports, 
            strategy_status, 
            risk_summary,
            tactical_trade_insights
        )
        
        return brief
    
    def _refresh_domain_analyses(self) -> None:
        """Analyze all domains to process signals into strategies"""
        for domain_key in self.domains.keys():
            self.analyze_domain(domain_key)
    
    def _collect_domain_reports(self) -> dict:
        """Collect reports from all domain chiefs"""
        reports = {}
        for domain_key, chief in self.domains.items():
            report = chief.create_report()
            reports[domain_key] = {
                "summary": f"{domain_key.capitalize()}: {chief.get_domain_status()}",
                "recommendations": [r for r in report.recommendations],
                "opportunities": chief.get_active_strategies(),
                "risks": []
            }
        return reports
    
    def _build_strategy_status(self) -> dict:
        """Build strategy status from all active strategies"""
        active_strategies = []
        for chief in self.domains.values():
            active_strategies.extend(chief.get_active_strategies())
        
        return {
            "active_strategies": [{"id": s.id, "title": s.title} for s in active_strategies]
        }
    
    def _build_risk_summary(self) -> dict:
        """Get risk summary from risk governor"""
        return self.risk_governor.get_risk_summary()
    
    def _apply_trade_intelligence(self, domain_reports: dict) -> tuple[dict, list]:
        """Apply trade intelligence to domain reports
        
        Returns:
            Tuple of (updated domain_reports, tactical_trade_insights)
        """
        tactical_trade_insights = []
        
        try:
            trade_insight = get_latest_spy0dte_trade_insight()
            if trade_insight:
                tactical_trade_insights = [trade_insight.to_dict()]
                
                # Enrich finance domain summary with trade intelligence
                if "finance" in domain_reports:
                    trade_summary = build_finance_trade_summary_appendix(trade_insight)
                    existing_summary = domain_reports["finance"].get("summary", "")
                    domain_reports["finance"]["summary"] = f"{existing_summary} {trade_summary}"
                
                # Add trade opportunity
                opportunity = build_trade_opportunity(trade_insight)
                if opportunity:
                    domain_reports["finance"].setdefault("trade_opportunities", []).append(opportunity)
                
                # Add trade risk
                risk = build_trade_risk(trade_insight)
                if risk:
                    domain_reports["finance"].setdefault("trade_risks", []).append(risk)
                
                # Add trade action
                action = build_trade_action(trade_insight)
                if action:
                    domain_reports["finance"].setdefault("trade_actions", []).append(action)
                    
        except Exception as e:
            # Graceful degradation - log warning but continue
            logger.warning("Trade intelligence unavailable: %s", e)
        
        return domain_reports, tactical_trade_insights
    
    def get_system_status(self) -> dict:
        """Get overall system status"""
        return {
            "layer1_strategic": {
                "hypotheses": len(self.strategy_lab.hypotheses),
                "simulations": len(self.simulation_engine.simulation_history),
                "edges": len(self.edge_discovery.edges),
                "knowledge_nodes": len(self.knowledge_graph.nodes),
                "lessons": len(self.learning_engine.lessons),
                "scenarios": len(self.scenario_planner.scenarios),
                "signals": len(self.signal_fusion.raw_signals)
            },
            "layer2_governance": {
                "council_members": len(self.executive_council.members),
                "pending_decisions": len(self.executive_council.get_pending_decisions()),
                "risks": self.risk_governor.get_risk_summary(),
                "gates": self.execution_gate.get_gate_summary(),
                "capital": self.capital_coordinator.get_portfolio_summary(),
                "tasks": self.priority_router.get_priority_summary()
            },
            "layer3_domains": {
                domain: chief.get_domain_status()
                for domain, chief in self.domains.items()
            },
            "infrastructure": {
                "memory": self.memory.get_stats(),
                "signals": self.signal_system.get_signal_summary(),
                # BB-INF-007: Signal Ingestion
                "ingestion": {
                    "manager": self.ingestion_manager.get_manager_status(),
                    "cache": self.signal_cache.get_stats(),
                    "health": self.health_monitor.get_health_summary()
                },
                # BB-INF-007: Intelligence Cycle
                "intelligence_cycle": self.intelligence_cycle.get_system_status()
            }
        }
    
    # ============== BB-INF-007: Signal Ingestion Methods ==============
    
    def run_signal_ingestion(self) -> dict:
        """Run a signal ingestion cycle"""
        result = self.ingestion_manager.run_ingestion_cycle()
        return {
            "status": result.status.value,
            "signals_collected": result.signals_collected,
            "signals_normalized": result.signals_normalized,
            "signals_validated": result.signals_validated,
            "signals_stored": result.signals_stored,
            "errors": result.errors,
            "duration_ms": result.duration_ms
        }
    
    def get_ingested_signals(self, domain: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """Get signals from the ingestion cache"""
        if domain:
            try:
                sig_domain = SignalDomain(domain)
                signals = self.ingestion_manager.get_signals_by_domain(sig_domain, limit)
            except ValueError:
                signals = self.ingestion_manager.get_all_signals(limit)
        else:
            signals = self.ingestion_manager.get_all_signals(limit)
        
        return [s.to_dict() for s in signals]
    
    def get_signal_health(self) -> dict:
        """Get signal ingestion health status"""
        return self.health_monitor.get_health_summary()
    
    # ============== BB-INF-007: Intelligence Cycle Methods ==============
    
    def run_intelligence_cycle(self) -> dict:
        """Run a complete intelligence cycle"""
        result = self.intelligence_cycle.run_full_cycle()
        return {
            "signals_processed": result.signals_processed,
            "strategies_triggered": result.strategies_triggered,
            "council_sessions": result.council_sessions,
            "reports_generated": result.reports_generated,
            "success": result.success,
            "errors": result.errors,
            "duration_ms": result.duration_ms
        }
    
    def start_continuous_intelligence(self) -> None:
        """Start continuous intelligence operation"""
        self.intelligence_cycle.start_continuous_operation()
    
    def stop_continuous_intelligence(self) -> None:
        """Stop continuous intelligence operation"""
        self.intelligence_cycle.stop_continuous_operation()
    
    def add_signal_trigger(
        self,
        trigger_id: str,
        domain: str,
        metric_pattern: str,
        threshold: float,
        comparison: str,
        severity: str = "medium"
    ) -> None:
        """Add a signal trigger for strategy generation"""
        self.intelligence_cycle.add_signal_trigger(
            trigger_id=trigger_id,
            domain=domain,
            metric_pattern=metric_pattern,
            threshold=threshold,
            comparison=comparison,
            severity=severity
        )
    
    # ============== BB-INF-008: Life Signal Graph Methods ==============
    
    def build_life_graph(self, signals: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Build the life signal graph from signals"""
        if signals is not None:
            result = self.graph_builder.build_from_signals(signals)
        else:
            result = self.graph_builder.full_build()
        
        return {
            "nodes_created": result.nodes_created,
            "edges_created": result.edges_created,
            "graph_summary": self.life_graph.get_graph_summary()
        }
    
    def get_life_graph_summary(self) -> dict[str, Any]:
        """Get summary of the life signal graph"""
        return self.life_graph.get_graph_summary()
    
    def query_life_graph(self, query_type: str, **kwargs: Any) -> dict[str, Any]:
        """Query the life graph"""
        if query_type == "leverage":
            leverage_points = self.graph_query.get_high_leverage_nodes(**kwargs)
            return {"leverage_points": [lp.to_dict() for lp in leverage_points]}
        elif query_type == "risks":
            risk_clusters = self.graph_query.get_risk_clusters()
            return {"risk_clusters": [rc.to_dict() for rc in risk_clusters]}
        elif query_type == "domain_health":
            # Use the already imported Domain from infrastructure.life_graph
            domain_key = kwargs.get("domain", "finance")
            return self.graph_query.get_domain_health(Domain(domain_key))
        elif query_type == "influence":
            return self.graph_query.get_cross_domain_influence()
        else:
            return {"error": f"Unknown query type: {query_type}"}
    
    # ============== BB-INF-008: Digital Twin Methods ==============
    
    def get_digital_twin_state(self) -> dict:
        """Get current digital twin state"""
        return self.digital_twin.get_current_state()
    
    def project_life(self, days: int = 90) -> dict:
        """Project life variables into the future"""
        return self.digital_twin.project(days)
    
    def simulate_scenario(
        self,
        scenario_name: str,
        changes: dict,
        days: int = 90
    ) -> dict:
        """Simulate a scenario with the digital twin"""
        return self.digital_twin.simulate_scenario(scenario_name, changes, days)
    
    def discover_leverage_opportunities(self, limit: int = 5) -> dict:
        """Discover high-leverage strategic opportunities"""
        result = self.leverage_discovery.discover_leverage_opportunities(
            current_state=self.digital_twin.get_current_state(),
            limit=limit
        )
        return result.to_dict()


# ============== Domain Configuration ==============


class DomainName(StrEnum):
    """Centralized domain names to avoid stringly-typed errors"""
    FINANCE = "finance"
    HEALTH = "health"
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    INTELLIGENCE = "intelligence"
    LIFE_ARCHITECTURE = "life_architecture"


# Import config models
from psip_config import DomainConfig, GovernanceConfig, RoleConfig, validate_domain_config


# Domain configuration centralized for governance setup
# Using typed DomainConfig dataclasses for immutability and type safety
DOMAIN_CONFIG: dict[DomainName, DomainConfig] = {
    DomainName.FINANCE: DomainConfig(
        name="finance",
        chief_class=domain.ChiefFinancialOfficer,
        governance=GovernanceConfig(
            priority_weight=1.0,
            risk_threshold_high=0.7,
            risk_threshold_medium=0.5,
            risk_threshold_low=0.6,
        ),
        description="Financial intelligence and strategic capital allocation domain.",
    ),
    DomainName.HEALTH: DomainConfig(
        name="health",
        chief_class=domain.ChiefHealthOfficer,
        governance=GovernanceConfig(
            priority_weight=1.0,
            risk_threshold_high=0.7,
            risk_threshold_medium=0.5,
            risk_threshold_low=0.6,
        ),
        description="Health and wellness intelligence domain.",
    ),
    DomainName.CAREER: DomainConfig(
        name="career",
        chief_class=domain.ChiefCareerOfficer,
        governance=GovernanceConfig(
            priority_weight=1.0,
            risk_threshold_high=0.7,
            risk_threshold_medium=0.5,
            risk_threshold_low=0.6,
        ),
        description="Career development and professional growth domain.",
    ),
    DomainName.RELATIONSHIPS: DomainConfig(
        name="relationships",
        chief_class=domain.ChiefRelationshipOfficer,
        governance=GovernanceConfig(
            priority_weight=1.0,
            risk_threshold_high=0.7,
            risk_threshold_medium=0.5,
            risk_threshold_low=0.6,
        ),
        description="Relationship intelligence and social dynamics domain.",
    ),
    DomainName.INTELLIGENCE: DomainConfig(
        name="intelligence",
        chief_class=domain.ChiefIntelligenceOfficer,
        governance=GovernanceConfig(
            priority_weight=1.0,
            risk_threshold_high=0.7,
            risk_threshold_medium=0.5,
            risk_threshold_low=0.6,
        ),
        description="Knowledge management and strategic intelligence domain.",
    ),
    DomainName.LIFE_ARCHITECTURE: DomainConfig(
        name="life_architecture",
        chief_class=domain.ChiefLifeArchitect,
        governance=GovernanceConfig(
            priority_weight=1.0,
            risk_threshold_high=0.7,
            risk_threshold_medium=0.5,
            risk_threshold_low=0.6,
        ),
        description="Life design and lifestyle optimization domain.",
    ),
}


def create_psip(
    total_capital: float = 100000,
    domains: dict[str, domain.ChiefOfficer] | None = None,
    signal_system: infra.SignalSystem | None = None,
    memory: infra.MemoryEngine | None = None,
    executive_council: governance.ExecutiveCouncil | None = None,
    risk_governor: governance.RiskGovernor | None = None,
    brief_generator: outputs.ExecutiveBriefGenerator | None = None,
    intelligence_cycle: IntelligenceCycleManager | None = None,
) -> PSIP:
    """
    Factory function to create a PSIP instance with proper dependency injection.
    
    This separates composition from behavior, making PSIP easier to test and evolve.
    
    Args:
        total_capital: Initial capital for the capital deployment coordinator
        domains: Optional dict of domain chief officers (injected for testing)
        signal_system: Optional signal system (injected for testing)
        memory: Optional memory engine (injected for testing)
        executive_council: Optional executive council (injected for testing)
        risk_governor: Optional risk governor (injected for testing)
        brief_generator: Optional brief generator (injected for testing)
        intelligence_cycle: Optional intelligence cycle manager (injected for testing)
    
    Returns:
        Configured PSIP instance
    """
    return PSIP(
        total_capital=total_capital,
        domains=domains,
        signal_system=signal_system,
        memory=memory,
        executive_council=executive_council,
        risk_governor=risk_governor,
        brief_generator=brief_generator,
        intelligence_cycle=intelligence_cycle,
    )


__all__ = [
    # Public API
    "PSIP",
    "create_psip",
    
    # Domain enum and config
    "DomainName",
    "DOMAIN_CONFIG",
    
    # Config models (from psip_config)
    "DomainConfig",
    "GovernanceConfig",
    "RoleConfig",
    "validate_domain_config",
    
    # Trade intelligence availability flag
    "TRADE_INTELLIGENCE_AVAILABLE",
]
