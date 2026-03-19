DIRECTIVE BB-FIN-022

Title: Tactical Intelligence Provider Framework & Multi-Strategy Brief Ingestion

Directive ID: BB-FIN-022
Title: Tactical Intelligence Provider Framework & Multi-Strategy Brief Ingestion
Priority: High
Domain: Finance / Intelligence / Reporting / Architecture
Status: Draft
Depends On:
- BB-FIN-021 (SPY 0DTE Trade Intelligence Integration)
- PSIP executive brief generation
- Existing tactical trade models
- Finance trade intelligence service

---

1. Purpose

Define a generalized framework for ingesting multiple tactical intelligence providers into the PSIP executive brief pipeline. This extends the SPY 0DTE integration pattern (BB-FIN-021) into a scalable architecture that can accommodate:

- Swing trade intelligence engines
- Sector rotation engines
- Options volatility engines
- Crypto tactical intelligence
- Macro event risk engines
- Custom third-party signal providers

The framework establishes:
- A common provider interface contract
- Normalized data schemas per provider type
- Priority-based ingestion rules
- Fallback and degradation strategies
- Extensible architecture for future providers

---

2. Strategic Intent

BB-FIN-021 demonstrated the first production integration of tactical intelligence into executive briefing. BB-FIN-022 generalizes that pattern into a reusable framework.

The executive brief must evolve from a static summary to a dynamic intelligence dashboard that:
- Aggregates multiple tactical sources in priority order
- Normalizes diverse intelligence formats into consistent schemas
- Resolves conflicts when providers disagree
- Maintains graceful degradation when providers are unavailable
- Preserves audit trail of intelligence provenance

This framework enables Busy Bee to operate as a true "Intelligence Operating System" rather than a collection of isolated tools.

---

3. Core Design Principle

All tactical intelligence providers must conform to a standard interface contract, regardless of their internal implementation.

```
TacticalIntelligenceProvider
├── get_current_intelligence() -> Optional[TacticalInsight]
├── get_provider_name() -> str
├── get_provider_priority() -> int
├── is_available() -> bool
├── get_confidence_range() -> (float, float)
└── get_supported_instruments() -> List[str]
```

This ensures:
- Plug-and-play provider addition
- Consistent normalization at the provider boundary
- Predictable brief enrichment behavior
- Testable provider interactions

---

4. Architecture Components

4.1 Provider Registry

A central registry tracks all available tactical intelligence providers.

```
ProviderRegistry
├── providers: Dict[str, TacticalIntelligenceProvider]
├── priority_order: List[str]
├── register(provider)
├── unregister(provider_name)
├── get_provider(name) -> TacticalIntelligenceProvider
├── get_all_providers() -> List[TacticalIntelligenceProvider]
└── get_providers_by_priority() -> List[TacticalIntelligenceProvider]
```

4.2 Intelligence Aggregator

The aggregator collects and normalizes intelligence from all registered providers.

```
IntelligenceAggregator
├── registry: ProviderRegistry
├── normalize_and_merge(intelligences) -> List[NormalizedInsight]
├── resolve_conflicts(insights) -> NormalizedInsight
├── filter_by_confidence(insights, threshold) -> List[NormalizedInsight]
└── get_top_insight(insights) -> Optional[NormalizedInsight]
```

4.3 Insight Normalizer

Converts provider-specific formats into the standard TacticalInsight schema.

```
InsightNormalizer
├── register_adapter(provider_name, adapter)
├── normalize(raw_insight, provider_name) -> NormalizedInsight
└── get_adapter(provider_name) -> NormalizationAdapter
```

---

5. Data Models

5.1 Base Tactical Insight (Abstract)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class TacticalInsight(ABC):
    """Abstract base for all tactical intelligence"""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def instrument(self) -> str:
        pass
    
    @property
    @abstractmethod
    def market_bias(self) -> str:
        pass
    
    @property
    @abstractmethod
    def recommendation(self) -> str:
        pass
    
    @property
    @abstractmethod
    def confidence(self) -> float:
        pass
    
    @property
    @abstractmethod
    def risk_level(self) -> str:
        pass
    
    @property
    @abstractmethod
    def generated_at(self) -> datetime:
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass
```

5.2 Provider Interface Contract

```python
class TacticalIntelligenceProvider(ABC):
    """Contract for all tactical intelligence providers"""
    
    @abstractmethod
    def get_current_intelligence(self) -> Optional[TacticalInsight]:
        """Retrieve current intelligence from provider"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Unique identifier for this provider"""
        pass
    
    @abstractmethod
    def get_provider_priority(self) -> int:
        """Priority (1 = highest) for brief inclusion"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is currently reachable"""
        pass
    
    @abstractmethod
    def get_confidence_range(self) -> (float, float):
        """Return (min, max) confidence values this provider produces"""
        pass
    
    @abstractmethod
    def get_supported_instruments(self) -> List[str]:
        """List of instruments this provider monitors"""
        pass
```

5.3 Multi-Provider Brief Enrichment Request

```python
@dataclass
class BriefEnrichmentRequest:
    """Request to enrich executive brief with tactical intelligence"""
    include_providers: List[str] = None  # None = all available
    exclude_providers: List[str] = None
    min_confidence_threshold: float = 0.5
    max_providers: int = 3  # Limit providers for brief length
    instruments_filter: List[str] = None  # None = all instruments
    
    # Conflict resolution strategy
    resolution_strategy: str = "highest_confidence"  # or "priority_first", "ensemble"
```

5.4 Enriched Executive Brief (Extended)

The existing ExecutiveBrief model is extended to support multiple providers:

```python
@dataclass
class ExecutiveBrief:
    # ... existing fields ...
    
    # BB-FIN-022: Multi-provider tactical intelligence
    tactical_intelligence_providers: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    intelligence_aggregation_summary: Dict[str, Any] = field(default_factory=dict)
    cross_provider_conflicts: List[Dict[str, Any]] = field(default_factory=list)
```

---

6. Provider Implementation Patterns

6.1 SPY 0DTE Provider (Reference Implementation)

The existing SPY 0DTE service is refactored into a provider:

```python
class SPY0DTEProvider(TacticalIntelligenceProvider):
    """BB-FIN-021: SPY 0DTE tactical intelligence provider"""
    
    def __init__(self):
        self._name = "spy0dte_engine"
        self._priority = 1
    
    def get_provider_name(self) -> str:
        return self._name
    
    def get_provider_priority(self) -> int:
        return self._priority
    
    def is_available(self) -> bool:
        return get_spy0dte_engine_report() is not None
    
    def get_current_intelligence(self) -> Optional[TacticalInsight]:
        report = get_spy0dte_engine_report()
        if report is None:
            return None
        return map_spy0dte_to_tactical_insight(report)
    
    def get_confidence_range(self) -> (float, float):
        return (0.3, 0.95)
    
    def get_supported_instruments(self) -> List[str]:
        return ["SPY", "SPX"]
```

6.2 Future Provider Examples

#### Swing Trade Provider

```python
class SwingTradeProvider(TacticalIntelligenceProvider):
    """Multi-day swing trade recommendations"""
    
    def get_provider_name(self) -> str:
        return "swing_trade_engine"
    
    def get_provider_priority(self) -> int:
        return 2  # Lower priority than 0DTE
    
    # ... other interface methods ...
```

#### Sector Rotation Provider

```python
class SectorRotationProvider(TacticalIntelligenceProvider):
    """Sector allocation and rotation signals"""
    
    def get_provider_name(self) -> str:
        return "sector_rotation_engine"
    
    def get_provider_priority(self) -> int:
        return 3
    
    # ... other interface methods ...
```

#### Crypto Tactical Provider

```python
class CryptoTacticalProvider(TacticalIntelligenceProvider):
    """Cryptocurrency tactical signals"""
    
    def get_provider_name(self) -> str:
        return "crypto_tactical_engine"
    
    def get_provider_priority(self) -> int:
        return 4
    
    # ... other interface methods ...
```

---

7. Intelligence Aggregation Rules

7.1 Priority-Based Collection

Providers are queried in priority order:
1. Collect from priority 1 providers first
2. Continue to priority 2, 3, etc. until max_providers reached
3. Skip unavailable providers (graceful degradation)

7.2 Conflict Resolution Strategies

When multiple providers offer conflicting intelligence:

| Strategy | Behavior |
|----------|----------|
| `highest_confidence` | Use insight with highest confidence score |
| `priority_first` | Use insight from highest priority provider |
| `ensemble` | Combine insights weighted by confidence and priority |
| `explicit_override` | Use provider-specific override rules |

7.3 Confidence Normalization

Different providers use different confidence scales. Normalize to 0-1:

| Provider | Raw Range | Normalization |
|----------|-----------|---------------|
| SPY 0DTE | 0.3-0.95 | Pass-through |
| Swing Trade | 1-10 | Divide by 10 |
| Sector Rotation | 0-100 | Divide by 100 |

---

8. Integration with Executive Brief

8.1 Brief Generation Flow (Updated)

```
1. Generate base executive brief (domains, strategies)
2. Initialize IntelligenceAggregator with ProviderRegistry
3. For each provider in priority order:
   a. Check is_available()
   b. Call get_current_intelligence()
   c. Normalize to standard schema
   d. Add to aggregated insights
4. Apply conflict resolution
5. Map aggregated insights to brief sections:
   - Opportunities
   - Risks
   - Actions
   - Dedicated tactical section
6. Add provider metadata
7. Return enriched brief
```

8.2 Brief Enrichment Functions

```python
def enrich_brief_with_multi_provider_intelligence(
    brief: ExecutiveBrief,
    request: BriefEnrichmentRequest
) -> ExecutiveBrief:
    """Enrich executive brief with multi-provider tactical intelligence"""
    
    aggregator = IntelligenceAggregator()
    
    # Collect intelligences
    intelligences = aggregator.collect_all(request)
    
    # Resolve conflicts
    resolved = aggregator.resolve_conflicts(intelligences, request.resolution_strategy)
    
    # Add to brief sections
    brief = _map_to_opportunities(brief, resolved)
    brief = _map_to_risks(brief, resolved)
    brief = _map_to_actions(brief, resolved)
    brief = _add_tactical_section(brief, resolved)
    
    # Add metadata
    brief.tactical_intelligence_providers = _build_provider_metadata(resolved)
    brief.intelligence_aggregation_summary = _build_summary(resolved)
    brief.cross_provider_conflicts = _identify_conflicts(resolved)
    
    return brief
```

---

9. Configuration

9.1 Provider Registration

```python
# config/tactical_intelligence_providers.py

PROVIDER_CONFIG = {
    "spy0dte_engine": {
        "enabled": True,
        "priority": 1,
        "min_confidence": 0.5,
        "instruments": ["SPY", "SPX"],
        "auto_include": True
    },
    "swing_trade_engine": {
        "enabled": False,  # Not yet implemented
        "priority": 2,
        "min_confidence": 0.6,
        "instruments": ["QQQ", "IWM", "AAPL", "MSFT"],
        "auto_include": False
    },
    "sector_rotation_engine": {
        "enabled": False,
        "priority": 3,
        "min_confidence": 0.55,
        "instruments": ["XLF", "XLK", "XLE", "XLV"],
        "auto_include": False
    }
}

# Default enrichment request
DEFAULT_ENRICHMENT_REQUEST = BriefEnrichmentRequest(
    max_providers=3,
    min_confidence_threshold=0.5,
    resolution_strategy="highest_confidence"
)
```

9.2 Environment Variables

```bash
# Enable/disable providers
SPY0DTE_PROVIDER_ENABLED=true
SWING_TRADE_PROVIDER_ENABLED=false
SECTOR_ROTATION_PROVIDER_ENABLED=false

# Priority overrides
PROVIDER_PRIORITY_SPY0DTE=1
PROVIDER_PRIORITY_SWING=2

# Confidence thresholds
MIN_CONFIDENCE_THRESHOLD=0.5
```

---

10. Error Handling & Degradation

10.1 Provider-Level Failures

| Failure Mode | Handling |
|--------------|----------|
| Provider timeout | Skip provider, log warning, continue |
| Provider returns None | Treat as "no signal", skip |
| Provider throws exception | Catch, log error, skip provider |
| Provider malformed response | Log error, skip provider |

10.2 System-Level Failures

| Failure Mode | Handling |
|--------------|----------|
| All providers unavailable | Generate brief without tactical intelligence |
| Registry initialization fails | Fall back to BB-FIN-021 single-provider mode |
| Aggregation fails | Use highest-priority available provider only |

---

11. Testing Requirements

11.1 Unit Tests

- Provider interface compliance tests
- Normalization adapter tests
- Conflict resolution strategy tests
- Confidence normalization tests
- Provider priority ordering tests

11.2 Integration Tests

- Multi-provider brief generation
- Provider availability toggle
- Graceful degradation when all providers fail
- Cross-provider conflict detection

11.3 Test Examples

```python
def test_provider_registry_priority_order():
    registry = ProviderRegistry()
    registry.register(SPY0DTEProvider())  # Priority 1
    registry.register(SwingTradeProvider())  # Priority 2
    
    providers = registry.get_providers_by_priority()
    assert providers[0].get_provider_name() == "spy0dte_engine"
    assert providers[1].get_provider_name() == "swing_trade_engine"

def test_conflict_resolution_highest_confidence():
    insights = [
        MockInsight(confidence=0.7, provider="swing"),
        MockInsight(confidence=0.9, provider="spy0dte")
    ]
    
    resolved = resolve_conflicts(insights, "highest_confidence")
    assert resolved.provider == "spy0dte"

def test_graceful_degradation_no_providers():
    request = BriefEnrichmentRequest()
    brief = generate_executive_brief(enrichment_request=request)
    
    # Should not raise, should generate without tactical section
    assert brief is not None
    assert brief.tactical_intelligence_providers == {}
```

---

12. Acceptance Criteria

This directive is complete when:

1. ✅ ProviderRegistry can register and retrieve multiple providers
2. ✅ TacticalIntelligenceProvider interface is fully defined and documented
3. ✅ SPY 0DTE provider implements the interface (refactored from BB-FIN-021)
4. ✅ IntelligenceAggregator collects from multiple providers in priority order
5. ✅ Conflict resolution strategies are implemented and configurable
6. ✅ Executive brief generation supports multi-provider enrichment
7. ✅ Graceful degradation works when providers are unavailable
8. ✅ Configuration system supports enable/disable/priority per provider
9. ✅ Tests cover provider interface, aggregation, and conflict resolution
10. ✅ Documentation includes patterns for adding new providers

---

13. Migration Path

### Phase 1: Framework Infrastructure (This Directive)
- ProviderRegistry
- Provider interface contract
- IntelligenceAggregator
- Basic conflict resolution

### Phase 2: Provider Migration
- Refactor SPY 0DTE to implement TacticalIntelligenceProvider
- Register in ProviderRegistry with priority 1
- Update briefs_service to use aggregator

### Phase 3: Provider Expansion
- Add SwingTradeProvider (priority 2)
- Add SectorRotationProvider (priority 3)
- Add CryptoTacticalProvider (priority 4)

### Phase 4: Advanced Features
- Ensemble conflict resolution
- Provider performance tracking
- Auto-priority adjustment based on accuracy

---

14. Developer Handoff Summary

Implement a generalized tactical intelligence provider framework that:

1. Defines a `TacticalIntelligenceProvider` interface contract
2. Creates a `ProviderRegistry` for managing multiple providers
3. Implements an `IntelligenceAggregator` for collecting and normalizing insights
4. Supports configurable conflict resolution strategies
5. Maintains graceful degradation when providers are unavailable
6. Provides a clear pattern for adding new tactical engines
7. Updates the executive brief generation to leverage multi-provider intelligence

The SPY 0DTE provider from BB-FIN-021 becomes the reference implementation for this framework.

---

15. Future Extension Path

This framework positions Busy Bee for:

- **Multi-Asset Coverage**: SPY, options, sectors, crypto, forex
- **Confidence Calibration**: Historical accuracy tracking per provider
- **Adaptive Prioritization**: ML-based priority adjustment
- **Ensemble Intelligence**: Weighted combination of providers
- **Third-Party Integration**: Standardized adapters for external signals

The tactical intelligence layer becomes a first-class citizen in the Busy Bee architecture, enabling true "operating system" functionality for personal finance intelligence.
