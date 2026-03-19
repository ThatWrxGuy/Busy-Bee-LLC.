# PSIP vs Busy Bee Architecture

## Boundary Diagram

```mermaid
flowchart TB
    subgraph Application["Busy Bee - Life Operating System"]
        direction TB
        A1[Chief Officers - 6]
        A2[Specialist Agents - 39+]
        A3[Domain Intelligence Reports]
        A4[Executive Council]
        A5[Executive Brief Generator]
    end
    
    subgraph Infrastructure["PSIP - Intelligence Infrastructure"]
        direction TB
        I1[Signal Architecture]
        I2[Signal Bus & Routing]
        I3[Validation & Normalization]
        I4[Strategic Intelligence Engine]
        I5[Reporting Pipeline]
        I6[Memory Engine]
        I7[Simulation Engine]
    end
    
    A1 -->|consumes| I2
    A2 -->|produces| I1
    A3 -->|feeds| I4
    A4 -->|coordinates| A3
    A5 -->|receives| A4
    
    I1 -->|provides data| A2
    I4 -->|strategic brain| A4
    I5 -->|delivers| A5
    
    style Application fill:#5f27cd,stroke:#333,stroke-width:2px,color:#fff
    style Infrastructure fill:#48dbfb,stroke:#333,stroke-width:2px
```

## What is PSIP?

**Personal Strategic Intelligence Platform**

The foundational intelligence infrastructure that powers Busy Bee.

| Component | Purpose |
|-----------|---------|
| Signal Architecture | Data ingestion, validation, routing |
| Strategic Intelligence Engine | Strategy brain |
| Reporting Pipeline | Intelligence flow |
| Memory Engine | Long-term learning |
| Simulation Engine | Outcome testing |

## What is Busy Bee?

**Life Operating System**

The application layer built on PSIP for personal life management.

| Component | Purpose |
|-----------|---------|
| Chief Officers | Domain leadership |
| Specialist Agents | Domain analysis |
| Executive Council | Cross-domain coordination |
| Executive Brief | User-facing output |

## Data Flow

```mermaid
sequenceDiagram
    participant User as CEO/User
    participant Brief as Executive Brief
    participant Council as Executive Council
    participant Chiefs as Chief Officers
    participant Agents as Specialist Agents
    participant Bus as Signal Bus
    participant PSIP as PSIP Infrastructure
    
    User->>Brief: Reviews guidance
    Brief->>Council: Receives summary
    Council->>Chiefs: Provides coordination
    Chiefs->>Agents: Directs analysis
    Agents->>Bus: Consumes signals
    Bus->>PSIP: Routes data
    PSIP-->>Bus: Processed signals
    Bus-->>Agents: Validated data
    Agents-->>Chiefs: Agent Insights
    Chiefs-->>Council: Domain Reports
    Council-->>Brief: Strategic Assessment
```

## Boundary Rules

### Busy Bee Handles
- Domain logic
- Agent implementations
- Chief Officer synthesis
- Council coordination
- User interaction

### PSIP Handles
- Signal processing
- Validation/Normalization
- Strategy computation
- Memory storage
- Simulation

### Rule
**Agents consume signals from PSIP; reports feed into PSIP strategic engines.**

---

*Diagram: BB-DIAG-001-06*
