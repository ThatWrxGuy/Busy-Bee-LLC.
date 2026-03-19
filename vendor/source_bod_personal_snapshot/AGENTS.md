# Busy Bee - Personal Life Operating System

## Overview

**Busy Bee** is your Personal Life Operating System - an AI-powered platform that helps you manage and optimize all aspects of your life.

**PSIP (Personal Strategic Intelligence Platform)** is the intelligence infrastructure that powers Busy Bee - the strategic reasoning layer, domain intelligence, and signal processing.

## Relationship

```
Busy Bee (Life OS)
    │
    ├── User Interface / Interaction Layer
    ├── Life Domain Applications
    │
    └── PSIP (Intelligence Infrastructure) ← We're building this
            │
            ├── Strategic Intelligence Core
            ├── Governance Layer  
            ├── Domain Intelligence (39 Agents)
            └── Signal Architecture
```

## BB-DOM-001: Domain Intelligence Expansion Framework

This project also implements **BB-DOM-001** - the Domain Intelligence Expansion Framework that standardizes domain architecture.

### Agent Roles (per BB-DOM-001)

| Role | Purpose | Count per Domain |
|------|---------|-----------------|
| **Observer** | Detect patterns, signals, anomalies | 1-2 |
| **Strategist** | Generate plans, recommendations | 3-4 |
| **Governor** | Ensure safety, alignment, discipline | 1 |

### Domain Specialist Agents (6 per domain)

#### Finance Domain
1. **Financial Planner** (Strategist) - Budgeting, saving strategies
2. **Investment Strategist** (Strategist) - Investment recommendations
3. **Risk Governor** (Governor) - Financial risk management
4. **Portfolio Architect** (Strategist) - Portfolio construction
5. **Macro Analyst** (Observer) - Economic monitoring
6. **Options Intelligence** (Strategist) - Alternative investments

#### Health Domain
1. **Sleep Recovery Advisor** (Strategist) - Sleep optimization
2. **Nutrition Strategist** (Strategist) - Dietary planning
3. **Fitness Programmer** (Strategist) - Exercise programming
4. **Stress Resilience Analyst** (Governor) - Stress management
5. **Habit Formation Coach** (Strategist) - Behavior change
6. **Preventive Health Monitor** (Observer) - Health monitoring

#### Career Domain
1. **Skill Development Strategist** (Strategist) - Career skill planning
2. **Opportunity Analyst** (Observer) - Job market opportunities
3. **Performance Coach** (Strategist) - Performance improvement
4. **Reputation Builder** (Strategist) - Personal branding
5. **Income Growth Planner** (Strategist) - Earning potential
6. **Decision Leverage Advisor** (Strategist) - Career decisions

#### Relationships Domain
1. **Partner Relationship Advisor** (Strategist) - Romantic relationship
2. **Family Dynamics Advisor** (Strategist) - Family management
3. **Social Network Strategist** (Strategist) - Social connections
4. **Conflict Resolution Coach** (Strategist) - Conflict management
5. **Communication Architect** (Strategist) - Communication strategies
6. **Trust & Alignment Monitor** (Governor) - Trust tracking

#### Intelligence Domain
1. **Knowledge Architect** (Strategist) - Knowledge management
2. **Decision Intelligence Analyst** (Strategist) - Decision support
3. **Research Strategist** (Strategist) - Research planning
4. **Learning Engineer** (Strategist) - Learning optimization
5. **Creativity Catalyst** (Strategist) - Creative thinking
6. **Signal Fusion Analyst** (Observer) - Signal integration

#### Life Architecture Domain
1. **Life Alignment Advisor** (Strategist) - Life purpose alignment
2. **Lifestyle Architect** (Strategist) - Lifestyle design
3. **Time Allocation Strategist** (Strategist) - Time management
4. **Adventure Planner** (Strategist) - Life experiences
5. **Environment Designer** (Strategist) - Living space optimization
6. **Momentum Coordinator** (Strategist) - Progress tracking
7. **Life Balance Governor** (Governor) - Life balance enforcement

## Architecture Compliance (per BB-DOM-001)

All domains now have **at least one Governor agent** as required:

| Domain | Observer | Strategist | Governor |
|--------|----------|------------|----------|
| **Finance** | Macro Analyst | Financial Planner, Investment Strategist, Portfolio Architect, Options Intelligence | Risk Governor |
| **Health** | Preventive Health Monitor | Sleep Recovery Advisor, Nutrition Strategist, Fitness Programmer, Habit Formation Coach | Stress Resilience Analyst |
| **Career** | Opportunity Analyst | Skill Development Strategist, Performance Coach, Reputation Builder, Income Growth Planner, Decision Leverage Advisor | **Career Risk Advisor** |
| **Relationships** | - | Partner Relationship Advisor, Family Dynamics Advisor, Social Network Strategist, Conflict Resolution Coach, Communication Architect | Trust & Alignment Monitor |
| **Intelligence** | Signal Fusion Analyst | Knowledge Architect, Decision Intelligence Analyst, Research Strategist, Learning Engineer, Creativity Catalyst | **Cognitive Bias Monitor** |
| **Life Architecture** | - | Life Alignment Advisor, Lifestyle Architect, Time Allocation Strategist, Adventure Planner, Environment Designer, Momentum Coordinator | **Life Balance Governor** |

**Total: 39 Specialist Agents** (36 + 3 Governors added for BB-DOM-001 compliance)

---

## BB-DOM-002: Domain Signal Architecture

Implemented signal architecture that powers intelligence across the platform.

### Signal Classes (Section 4)
- **External**: Market data, news, economic indicators
- **Behavioral**: User actions, spending, activity
- **System**: Internal metrics, portfolio performance
- **Derived**: Analyzed/computed insights

### Signal Flow (Section 6)
```
Source → Ingestion → Normalization → Validation → Classification → Global Signal Bus → Domain Routing → Analysis
```

### Global Signal Bus Features
- Decoupled signal distribution
- Cross-domain awareness (e.g., sleep debt → Health, Career, Life Architecture)
- Signal subscriptions for agents
- Priority-based routing
- Escalation to governors

### Derived Signals (Section 15)
- Financial Stress Score
- Burnout Probability
- Career Leverage Score
- Relationship Strain Index
- Life Balance Risk

### Implementation
```python
from infrastructure.signal_architecture import (
    SignalFactory, GlobalSignalBus, DerivedSignalEngine,
    SignalClass, SignalPriority, SignalDomain
)

# Create signal
factory = SignalFactory()
signal = factory.create_signal(
    signal_type='sleep_duration',
    signal_class=SignalClass.BEHAVIORAL,
    domain_targets=[SignalDomain.HEALTH],
    source='wearable',
    value=7.5,
    unit='hours',
    confidence=0.85
)

# Publish to bus
bus = GlobalSignalBus()
bus.publish(signal)
```

---

## BB-DOM-003: Domain Reporting & Executive Intelligence Doctrine

Implemented the complete intelligence reporting pipeline.

### Intelligence Product Hierarchy (Section 2)
| Level | Artifact | Producer |
|-------|----------|----------|
| 1 | Agent Insight | Specialist Agents |
| 2 | Governor Alert | Governor Agents |
| 3 | Domain Intelligence Report | Chief Officers |
| 4 | Council Strategic Assessment | Executive Council |
| 5 | Executive Brief | Busy Bee System |

### Intelligence Flow (Section 3)
```
Signals → Derived Signals → Agent Insights → Governor Alerts → Domain Reports → Council Assessment → Executive Brief
```

### Implementation
```python
from infrastructure.reporting import IntelligencePipeline, ExecutiveBrief

# Run full pipeline
pipeline = IntelligencePipeline()
brief = pipeline.run_full_pipeline(domain_data)
print(brief.format_brief())
```

---

## BB-INT-001: Strategic Intelligence Engine

The strategic brain that transforms Busy Bee from a reporting system into a true life strategy operating system.

### Core Capabilities (Section 5)
- **Strategy Generation**: Generate candidate strategies from domain intelligence
- **Scenario Simulation**: Project outcomes across time horizons (Immediate, Near-Term, Mid-Term, Long-Term)
- **Strategic Debate**: Preserve domain disagreement, identify conflicts
- **Leverage Discovery**: Find high-leverage actions with compound benefits
- **Alignment Scoring**: Evaluate against goals, constraints, governance

### Architecture (Section 4)
```
CEO
 │
Executive Brief
 │
Executive Council
 │
Strategic Intelligence Engine   ← BB-INT-001
 │
Domain Intelligence Reports
 │
Chief Officers + 39 Agents
 │
Signal Architecture
```

### Implementation
```python
from infrastructure.strategic_intelligence import StrategicIntelligenceEngine

engine = StrategicIntelligenceEngine()
output = engine.process(
    domain_reports=reports,
    user_goals=['Financial independence'],
    constraints=['Limited time']
)
print(output.format_assessment())
```

---

### Layer 1: Strategic Intelligence Core
- **Strategy Lab**: Generates and evaluates strategic hypotheses
- **Simulation Engine**: Digital testing ground for strategies
- **Edge Discovery Engine**: Identifies emerging opportunities
- **Knowledge Graph**: Stores and manages strategic knowledge
- **Learning Engine**: Continuous improvement of decision quality
- **Scenario Planner**: Plans and evaluates strategic scenarios
- **Signal Fusion Engine**: Fuses signals from multiple sources

### Layer 2: Governance Layer
- **Executive Council**: Strategic coordination and decision-making
- **Risk Governor**: Enforces risk management policies
- **Execution Gate**: Approves and controls strategy execution
- **Capital Deployment Coordinator**: Manages capital allocation
- **Priority Router**: Routes and prioritizes tasks

### Layer 3: Domain Intelligence Systems
- **Finance**: Chief Financial Officer + 4 specialist agents
- **Health**: Chief Health Officer + 4 specialist agents
- **Career**: Chief Career Officer + 4 specialist agents
- **Relationships**: Chief Relationship Officer + 4 specialist agents
- **Intelligence**: Chief Intelligence Officer + 4 specialist agents
- **Life Architecture**: Chief Life Architect + 4 specialist agents

## Usage

```python
from psip import PSIP

# Initialize PSIP with total capital
psip = PSIP(total_capital=100000)

# Process a signal
signal = psip.process_signal({
    "source": "finance_api",
    "type": "investment_opportunity",
    "domain": "finance",
    "payload": {
        "title": "New Investment Opportunity",
        "description": "Diversified portfolio option",
        "strength": 0.7
    }
})

# Analyze a domain
analysis = psip.analyze_domain("finance")

# Generate executive brief
brief = psip.generate_executive_brief()

# Get system status
status = psip.get_system_status()
```

## Key Concepts

### Intelligence Pipeline
All strategic reasoning follows: Signals → Detection → Analysis → Strategy Generation → Simulation → Risk Evaluation → Council Review → Executive Brief

### Agent Doctrine
- Agents are stateless reasoning units
- Domain specialists that generate analysis
- Cannot access infrastructure directly
- All state flows through Memory Engine and Signal System

### Governance
- CEO (user) has final authority
- Executive Council handles strategic coordination
- Chief Officers lead domains
- Agents provide analysis only - cannot execute decisions

## Project Structure

```
BOD-personal/
├── layer1_strategic_intelligence_core/
│   ├── strategy_lab/
│   ├── simulation_engine/
│   ├── edge_discovery_engine/
│   ├── knowledge_graph/
│   ├── learning_engine/
│   ├── scenario_planner/
│   └── signal_fusion_engine/
├── layer2_governance_layer/
│   ├── executive_council/
│   ├── risk_governor/
│   ├── execution_gate/
│   ├── capital_deployment_coordinator/
│   └── priority_router/
├── layer3_domain_intelligence/
│   ├── finance/
│   ├── health/
│   ├── career/
│   ├── relationships/
│   ├── intelligence/
│   └── life_architecture/
├── infrastructure/
│   ├── memory_engine/
│   └── signal_system/
├── outputs/
│   └── executive_briefs/
└── psip.py
```
