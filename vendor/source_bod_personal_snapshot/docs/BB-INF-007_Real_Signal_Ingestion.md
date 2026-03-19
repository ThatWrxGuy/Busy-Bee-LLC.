# BB-INF-007: Real Signal Ingestion & Continuous Intelligence Cycle

## Directive Overview

| Field | Value |
|-------|-------|
| **Directive ID** | BB-INF-007 |
| **Title** | Real Signal Ingestion & Continuous Intelligence Cycle |
| **Class** | Infrastructure / Intelligence Pipeline |
| **Priority** | CRITICAL |
| **System Phase** | Busy Bee V1.75 Preparation |
| **Status** | ✅ Implemented |

---

## 1. Executive Purpose

Busy Bee previously operated with a sophisticated strategic reasoning architecture but relied on synthetic or static signals. This directive establishes:

- **Real Signal Ingestion Layer** - Connect to live data sources
- **Continuous Intelligence Cycle** - Autonomous strategic monitoring
- **Event-Driven Strategy** - Trigger strategy generation from real-world events

---

## 2. Strategic Objective

Transform Busy Bee from:

```
Strategic Reasoning System → Autonomous Life Intelligence System
```

Through integration of:
1. Live Signal Sources
2. Normalized Signal Pipelines
3. Continuous Monitoring Loops
4. Real-Time Executive Intelligence

---

## 3. Architectural Expansion

### New Layer Placement

```
External World
     │
     ▼
Signal Ingestion Layer   ← NEW
     │
     ▼
Signal Intelligence System
     │
     ▼
Strategy Engines
     │
     ▼
Executive Council
     │
     ▼
Reporting System
```

---

## 4. Implementation Components

### Signal Ingestion Layer (`/infrastructure/signal_ingestion/`)

| Component | Purpose |
|-----------|---------|
| `signal_connector_base.py` | Base interface for all connectors |
| `signal_connector_registry.py` | Manages connector lifecycle |
| `signal_normalizer.py` | Converts to canonical format |
| `signal_validator.py` | Validates signal quality |
| `signal_cache.py` | In-memory cache with TTL |
| `signal_health_monitor.py` | System health monitoring |
| `ingestion_manager.py` | Pipeline orchestration |

### Intelligence Cycle (`/infrastructure/intelligence_cycle/`)

| Component | Purpose |
|-----------|---------|
| `cycle_scheduler.py` | Schedule management (hourly/daily/weekly/monthly) |
| `signal_refresh_engine.py` | Signal collection and change detection |
| `strategy_trigger_engine.py` | Triggers strategy generation |
| `council_trigger_engine.py` | Triggers council review |
| `reporting_trigger_engine.py` | Triggers report generation |

---

## 5. Canonical Signal Model

All signals are normalized to this format:

```python
@dataclass
class CanonicalSignal:
    signal_id: str
    domain: SignalDomain  # finance, health, career, etc.
    source: str
    timestamp: datetime
    
    # Core metrics
    metric_name: str
    metric_value: Any
    unit: SignalUnit  # USD, percent, hours, etc.
    
    # Quality
    confidence: float  # 0.0 - 1.0
    
    # Organization
    tags: List[str]
    metadata: Dict[str, Any]
```

---

## 6. Supported Connector Categories

| Category | Examples |
|----------|----------|
| **Financial** | Bank APIs, brokerage accounts, crypto wallets |
| **Calendar** | Google Calendar, Apple Calendar |
| **Health** | Apple Health, Fitbit, Whoop |
| **Market** | Stock prices, macro indicators |
| **Productivity** | Notion, task managers |
| **Communication** | Email, messaging metrics |

---

## 7. Continuous Intelligence Cycle

Every cycle executes:

```
1. Collect Signals (from all connectors)
2. Normalize Signals (to canonical format)
3. Validate Signals (quality checks)
4. Store Signals (in cache)
5. Detect Significant Changes (threshold monitoring)
6. Trigger Strategy Generation (if conditions met)
7. Run Strategy Tournament (BB-INT-002A)
8. Executive Council Decision (if high priority)
9. Generate Executive Brief (reporting)
```

---

## 8. Cycle Scheduling

| Frequency | Purpose |
|-----------|---------|
| **Hourly** | Signal refresh |
| **Daily** | Strategic intelligence cycle |
| **Weekly** | Strategic review |
| **Monthly** | Macro planning |

---

## 9. Trigger System

### Strategy Triggers (Examples)

- **Debt Increase Alert**: `debt` increases by > $1000
- **Sleep Deficit Alert**: `sleep` drops below 6 hours
- **Market Movement Alert**: `market` changes > 5%
- **New Opportunity**: New `opportunity` signal detected

### Council Triggers

- Strategy tournament complete
- High priority signal detected
- Risk alert triggered
- Domain crisis detected
- Scheduled daily review

---

## 10. Usage Example

```python
from psip import PSIP
from psip import ConnectorConfig, ConnectorCategory

# Initialize PSIP with V1.75 capabilities
psip = PSIP(total_capital=100000)

# Add a connector (example)
config = ConnectorConfig(
    connector_id="my_bank",
    name="My Bank",
    category=ConnectorCategory.FINANCIAL,
    poll_interval=300
)
psip.ingestion_manager.register_connector(config)

# Connect and run ingestion
psip.ingestion_manager.connect_all()
result = psip.run_signal_ingestion()

# Run full intelligence cycle
cycle_result = psip.run_intelligence_cycle()

# Start continuous operation
psip.start_continuous_intelligence()

# Check system status
status = psip.get_system_status()
print(status["infrastructure"]["ingestion"]["health"])
```

---

## 11. Success Criteria ✅

- ✅ Live signals can be ingested via connectors
- ✅ Signals normalized into canonical format
- ✅ Intelligence cycles execute automatically via scheduler
- ✅ Strategy engines trigger from real-world events
- ✅ Executive briefs generated from live data

---

## 12. System Evolution

After BB-INF-007, Busy Bee transitions from:

```
Strategic Test System → Continuous Strategic Intelligence Platform
```

This establishes the foundation for:

```
Busy Bee V2: Autonomous Life Operating System
```

---

## 13. Related Directives

- **BB-INT-001**: Strategic Intelligence Engine
- **BB-INT-002A**: Advanced Strategy Tournament
- **BB-INF-008**: Life Signal Graph & Personal Digital Twin Engine (next)
