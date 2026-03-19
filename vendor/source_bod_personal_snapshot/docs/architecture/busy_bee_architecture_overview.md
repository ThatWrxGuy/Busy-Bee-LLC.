# System Architecture Overview

## Busy Bee Full Stack Architecture

```mermaid
flowchart TD
    subgraph CEO["CEO - User"]
        direction LR
    end
    
    subgraph Council["Executive Council"]
        direction LR
    end
    
    subgraph Strategy["Strategic Intelligence Engine"]
        direction LR
    end
    
    subgraph Chiefs["Chief Officers - 6 Domains"]
        direction LR
        CFO[CFO]
        CHO[CHO]
        CCO[CCO]
        CRO[CRO]
        CIO[CIO]
        CLA[CLA]
    end
    
    subgraph Agents["Specialist Agents - 39+"]
        direction LR
    end
    
    subgraph Signals["Signal Intelligence Layer"]
        direction LR
    end
    
    CEO --> Council
    Council --> Strategy
    Strategy --> Chiefs
    Chiefs --> Agents
    Agents --> Signals
    
    style CEO fill:#ff6b6b,stroke:#333,stroke-width:2px
    style Council fill:#feca57,stroke:#333,stroke-width:2px
    style Strategy fill:#48dbfb,stroke:#333,stroke-width:2px
    style Chiefs fill:#1dd1a1,stroke:#333,stroke-width:2px
    style Agents fill:#5f27cd,stroke:#333,stroke-width:2px,color:#fff
    style Signals fill:#222f3e,stroke:#333,stroke-width:2px,color:#fff
```

## Quick Reference

| Layer | Components | Description |
|-------|------------|-------------|
| CEO | User | Final decision authority |
| Executive Council | 6 Chief Officers | Cross-domain coordination |
| Strategic Engine | 5 Sub-engines | Strategy brain |
| Chief Officers | CFO, CHO, CCO, CRO, CIO, CLA | Domain leadership |
| Specialist Agents | 39+ agents | Domain analysis |
| Signal Layer | Global Signal Bus | Data foundation |

---

*Diagram: BB-DIAG-001-01*
