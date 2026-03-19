# Executive Hierarchy Diagram

## Organizational Structure

```mermaid
flowchart TD
    subgraph CEO["CEO - User"]
        direction LR
    end
    
    subgraph Council["Executive Council"]
        direction LR
    end
    
    subgraph Domains["Chief Officers - 6 Domains"]
        direction TB
        CFO[Chief Financial Officer]
        CHO[Chief Health Officer]
        CCO[Chief Career Officer]
        CRO[Chief Relationship Officer]
        CIO[Chief Intelligence Officer]
        CLA[Chief Life Architect]
    end
    
    CEO --> Council
    Council --> CFO
    Council --> CHO
    Council --> CCO
    Council --> CRO
    Council --> CIO
    Council --> CLA
    
    style CEO fill:#ff6b6b,stroke:#333,stroke-width:3px
    style Council fill:#feca57,stroke:#333,stroke-width:3px
    style Domains fill:#1dd1a1,stroke:#333,stroke-width:2px
    style CFO fill:#48dbfb,stroke:#333
    style CHO fill:#48dbfb,stroke:#333
    style CCO fill:#48dbfb,stroke:#333
    style CRO fill:#48dbfb,stroke:#333
    style CIO fill:#48dbfb,stroke:#333
    style CLA fill:#48dbfb,stroke:#333
```

## Council Composition

| Officer | Domain | Primary Responsibility |
|---------|--------|----------------------|
| CFO | Finance | Capital allocation strategy |
| CHO | Health | Wellness strategy |
| CCO | Career | Career growth strategy |
| CRO | Relationships | Relational strategy |
| CIO | Intelligence | Knowledge strategy |
| CLA | Life Architecture | Life design strategy |

## Authority Flow

1. **CEO** - Final decision authority
2. **Executive Council** - Strategic coordination
3. **Chief Officers** - Domain leadership
4. **Specialist Agents** - Analysis and recommendations

---

*Diagram: BB-DIAG-001-02*
