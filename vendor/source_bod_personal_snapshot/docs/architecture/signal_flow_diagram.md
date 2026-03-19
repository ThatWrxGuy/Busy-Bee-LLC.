# Signal Flow Diagram

## Signal Architecture (BB-DOM-002)

```mermaid
flowchart TD
    subgraph Sources["Signal Sources"]
        direction TB
        External[External Signals]
        Behavioral[Behavioral Signals]
        System[System Signals]
        Derived[Derived Signals]
    end
    
    subgraph Bus["Global Signal Bus"]
        Validation[Validation]
        Normalization[Normalization]
        Routing[Routing]
    end
    
    subgraph Consumption["Signal Consumers"]
        Agents[Specialist Agents]
        Chiefs[Chief Officers]
        Engines[Strategic Engines]
    end
    
    External --> Validation
    Behavioral --> Validation
    System --> Validation
    Derived --> Validation
    
    Validation --> Normalization
    Normalization --> Routing
    
    Routing --> Agents
    Routing --> Chiefs
    Routing --> Engines
    
    style Sources fill:#ff9ff3,stroke:#333
    style Bus fill:#48dbfb,stroke:#333,stroke-width:2px
    style Consumption fill:#1dd1a1,stroke:#333
```

## Signal Classes

| Class | Description | Examples |
|-------|-------------|----------|
| **External** | Environment data | Market prices, news, weather |
| **Behavioral** | User actions | Spending, sleep, exercise |
| **System** | Internal metrics | Portfolio, risk scores |
| **Derived** | Computed insights | Burnout probability, stress |

## Signal Flow

1. **Sources** emit raw signals
2. **Validation** checks schema and required fields
3. **Normalization** standardizes units and values
4. **Routing** sends to appropriate domains
5. **Consumers** process signals for insights

## Cross-Domain Routing

```mermaid
flowchart LR
    subgraph Primary["Primary Routing"]
        F1[Finance Signals] --> Finance
    end
    
    subgraph Secondary["Secondary Routing"]
        Sleep[Health Signal] --> Health
        Sleep --> Career
        Sleep --> LifeArch
    end
    
    subgraph Global["Global Routing"]
        Crisis[Critical Signal] --> All[All Domains]
    end
    
    style Primary fill:#c8d6e5,stroke:#333
    style Secondary fill:#feca57,stroke:#333
    style Global fill:#ff6b6b,stroke:#333,color:#fff
```

### Routing Types

- **Primary:** Signal goes to owning domain
- **Secondary:** Signal relevant to related domains (e.g., sleep affects health, career, life)
- **Global:** Critical signals route to all domains (e.g., liquidity crisis, burnout)

---

*Diagram: BB-DIAG-001-04*
