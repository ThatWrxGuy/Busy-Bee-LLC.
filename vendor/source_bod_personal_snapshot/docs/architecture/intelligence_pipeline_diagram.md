# Intelligence Pipeline Diagram

## Reporting Flow (BB-DOM-003)

```mermaid
flowchart TD
    subgraph Input["Intelligence Input"]
        Signals[Signals]
    end
    
    subgraph Layer1["Level 1: Agent Insights"]
        AI[Agent Insights]
    end
    
    subgraph Layer2["Level 2: Governor Alerts"]
        GA[Governor Alerts]
    end
    
    subgraph Layer3["Level 3: Domain Reports"]
        DR[Domain Intelligence Reports]
    end
    
    subgraph Layer4["Level 4: Council Assessment"]
        CA[Council Strategic Assessment]
    end
    
    subgraph Layer5["Level 5: Executive Brief"]
        EB[Executive Brief]
    end
    
    Signals --> AI
    AI --> GA
    GA --> DR
    DR --> CA
    CA --> EB
    
    style Input fill:#ff9ff3,stroke:#333
    style Layer1 fill:#48dbfb,stroke:#333
    style Layer2 fill:#feca57,stroke:#333
    style Layer3 fill:#1dd1a1,stroke:#333
    style Layer4 fill:#5f27cd,stroke:#333,color:#fff
    style Layer5 fill:#ff6b6b,stroke:#333,color:#fff
```

## Pipeline Stages

| Level | Artifact | Producer | Description |
|-------|----------|----------|-------------|
| 1 | Agent Insights | Specialist Agents | Domain-specific analysis |
| 2 | Governor Alerts | Governor Agents | Risk/violation warnings |
| 3 | Domain Reports | Chief Officers | Domain synthesis |
| 4 | Council Assessment | Executive Council | Cross-domain coordination |
| 5 | Executive Brief | System | CEO-ready summary |

## Strategic Intelligence Flow

```mermaid
flowchart TD
    subgraph Inputs["Inputs"]
        DR[Domain Reports]
        GA[Governor Alerts]
        Goals[User Goals]
        Constraints[Constraints]
    end
    
    subgraph Engines["Strategic Intelligence Engine"]
        SG[Strategy Generation]
        SS[Scenario Simulation]
        SB[Strategic Debate]
        LD[Leverage Discovery]
        AE[Alignment Engine]
    end
    
    subgraph Outputs["Outputs"]
        SIO[Strategic Intelligence Output]
        Paths[Ranked Paths]
        Actions[Recommended Actions]
    end
    
    Inputs --> Engines
    Engines --> SIO
    SIO --> Paths
    Paths --> Actions
    
    style Inputs fill:#ff9ff3,stroke:#333
    style Engines fill:#48dbfb,stroke:#333,stroke-width:2px
    style Outputs fill:#1dd1a1,stroke:#333
```

### Time Horizons

| Horizon | Duration | Focus |
|---------|-----------|-------|
| **Immediate** | 1-14 days | Urgent actions |
| **Near-Term** | 1-12 weeks | Tactical planning |
| **Mid-Term** | 3-12 months | Strategic initiatives |
| **Long-Term** | 1-5 years | Life architecture |

---

*Diagram: BB-DIAG-001-05*
