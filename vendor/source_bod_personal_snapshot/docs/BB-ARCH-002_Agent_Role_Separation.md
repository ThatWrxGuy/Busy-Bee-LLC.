# BB-ARCH-002: Agent Role Separation Doctrine

**Directive ID:** BB-ARCH-002  
**Status:** Active  
**System:** Busy Bee / PSIP  
**Type:** Architectural Structure Doctrine  
**Priority:** High  
**Depends On:** BB-DOM-001, BB-MAP-001  

---

## 1. Purpose

This directive establishes the formal separation between two types of agents in the Busy Bee system:

1. **Analytical Modules** - Produce analysis and insights
2. **Strategic Agents** - Make decisions and propose strategies

This separation prevents "agent explosion" where too many voices create strategy chaos.

---

## 2. Two Types of Agents

### Strategic Agents (Decision Actors)

These agents participate in strategy generation, debate, and decisions.

**Characteristics:**
- Represent domain viewpoints
- Propose strategic recommendations
- Participate in cross-domain debate
- Synthesize evidence from modules

**Count:** 12-16 total (1-3 per domain)

### Analytical Modules (Signal Processors)

These agents perform analysis but do not propose strategies directly.

**Characteristics:**
- Detect patterns in signals
- Produce metrics and insights
- Monitor domain health
- Feed data to strategic agents

**Count:** ~39 (5-7 per domain)

---

## 3. Domain Structure

### Finance Domain

| Type | Agent | Role |
|------|-------|------|
| **Strategic** | Capital Allocation Strategist | Propose financial strategies |
| **Strategic** | Risk Governor | Veto risky strategies |
| **Module** | Investment Analyst | Analyze investment performance |
| **Module** | Cashflow Tracker | Monitor income/expenses |
| **Module** | Debt Analyzer | Track debt metrics |
| **Module** | Macro Monitor | Watch economic signals |

### Health Domain

| Type | Agent | Role |
|------|-------|------|
| **Strategic** | Health Optimization Strategist | Propose health strategies |
| **Strategic** | Recovery Governor | Enforce recovery limits |
| **Module** | Sleep Analyst | Analyze sleep patterns |
| **Module** | Stress Detector | Monitor stress signals |
| **Module** | Nutrition Tracker | Track dietary patterns |
| **Module** | Energy Monitor | Monitor energy levels |

### Career Domain

| Type | Agent | Role |
|------|-------|------|
| **Strategic** | Career Growth Strategist | Propose career strategies |
| **Strategic** | Opportunity Governor | Evaluate opportunities |
| **Module** | Skill Analyst | Track skill development |
| **Module** | Workload Monitor | Analyze workload patterns |
| **Module** | Performance Tracker | Monitor performance metrics |
| **Module** | Market Scanner | Watch job market signals |

### Relationships Domain

| Type | Agent | Role |
|------|-------|------|
| **Strategic** | Relationship Strategist | Propose relational strategies |
| **Strategic** | Social Stability Governor | Monitor relationship health |
| **Module** | Time Allocator | Track time with others |
| **Module** | Conflict Detector | Monitor conflict signals |
| **Module** | Connection Tracker | Track social connections |
| **Module** | Communication Analyst | Analyze communication patterns |

### Intelligence Domain

| Type | Agent | Role |
|------|-------|------|
| **Strategic** | Learning Strategist | Propose learning strategies |
| **Strategic** | Cognitive Load Governor | Prevent overload |
| **Module** | Knowledge Analyst | Track knowledge growth |
| **Module** | Research Scanner | Monitor research signals |
| **Module** | Creativity Monitor | Track creative output |
| **Module** | Bias Detector | Identify cognitive biases |

### Life Architecture Domain

| Type | Agent | Role |
|------|-------|------|
| **Strategic** | Life Strategy Architect | Propose life strategies |
| **Strategic** | Life Balance Governor | Enforce balance limits |
| **Module** | Time Analyzer | Analyze time allocation |
| **Module** | Routine Monitor | Track routine stability |
| **Module** | Lifestyle Tracker | Monitor lifestyle patterns |
| **Module** | Adventure Scanner | Look for experiences |

---

## 4. Information Flow

```
SIGNAL LAYER
    ↓
ANALYTICAL MODULES (~39)
    ↓ (produce insights)
DOMAIN STRATEGISTS (6)
    ↓ (propose strategies)
GOVERNORS (6)
    ↓ (approve/veto)
STRATEGIC INTELLIGENCE ENGINE
    ↓
EXECUTIVE COUNCIL
    ↓
CEO (User)
```

---

## 5. Rules of Separation

### Rule 1: Modules Don't Debate

Analytical modules produce output but do not participate in strategic debate.

### Rule 2: Strategists Synthesize

Strategic agents synthesize insights from multiple modules.

### Rule 3: Governors Check

Governors can reject strategies based on module-reported risks.

### Rule 4: Clear Interfaces

- Modules → Strategists: Insights and metrics
- Strategists → Council: Strategic recommendations
- Council → CEO: Final assessment

---

## 6. Agent Count Summary

| Category | Count | Description |
|----------|-------|-------------|
| Strategic Agents | 12 | 2 per domain (1 strategist + 1 governor) |
| Additional Strategists | 4 | Optional per domain for complex domains |
| Analytical Modules | ~39 | Signal processors |
| **Total Strategic Voice** | **12-16** | What council hears |
| **Total System** | **~55** | Complete agent count |

---

## 7. Benefits

### For Strategy Generation
- Clean debate between domain viewpoints
- No conflicting noise from raw signal analysis

### For Scalability
- Add new analytical modules without expanding strategic voice
- System complexity grows in analysis layer, not decision layer

### For Quality
- Strategists synthesize evidence rather than reacting to raw data
- Better recommendations from aggregated analysis

### For Governance
- Clear accountability (strategists own domain decisions)
- Clear safety (governors enforce limits)

---

## 8. Implementation Notes

### When Generating Strategies (BB-INT-001)

The Strategic Intelligence Engine should:
- Input: Domain Intelligence Reports (from Chief Officers)
- Not directly query analytical modules
- Trust Chief Officers to synthesize module insights

### When Running Debates

The debate should include:
- 6 Domain Strategists (one per domain)
- 6 Governors (one per domain)
- Total: 12 voices maximum

### When Monitoring Health

Analytical modules run continuously:
- Detect anomalies
- Update Chief Officers
- Alert Governors if thresholds crossed

---

## 9. Definition of Done

- [x] Strategic agents identified (12-16)
- [x] Analytical modules identified (~39)
- [x] Information flow defined
- [x] Rules of separation established
- [x] Domain structure documented

---

*BB-ARCH-002 - Agent Role Separation Doctrine*
*Last Updated: 2026-03-16*
