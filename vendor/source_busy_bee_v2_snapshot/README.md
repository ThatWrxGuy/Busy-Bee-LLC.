# Busy Bee Starter Repo

Busy Bee is a **Personal Strategic Intelligence Platform** that combines:

- domain intelligence agents
- event-driven orchestration
- ML pipelines for prediction and prioritization
- human-in-the-loop approvals for real-world execution
- observability, audit logging, and deployable APIs

This starter repo is a production-oriented scaffold designed to help evolve Busy Bee into a real application with strong software boundaries.

## Core principles

1. **Human approval required** for real-world financial decisions.
2. **Domain-first architecture** across Finance, Health, Career, Relationships, Intelligence, and Life Architecture.
3. **ML as a subsystem**, not the whole product.
4. **Reproducible pipelines** for training, inference, and evaluation.
5. **Event-driven orchestration** with auditable workflows.
6. **Deployable from day one** with FastAPI + Docker.

## Included in this scaffold

- FastAPI app with health, readiness, prediction, and brief endpoints
- config-driven runtime
- sklearn ML training pipeline
- model registry metadata format
- orchestrator skeleton for strategic cycle execution
- human approval guardrails for execution layers
- audit logging and observability hooks
- Docker, Makefile, pytest, and CI starter

## High-level architecture

```text
User / Dashboard
      |
      v
API Layer (FastAPI)
      |
      v
Application Services
      |
      +--> Domain Intelligence Services
      +--> ML Services
      +--> Workflow / Approval Services
      +--> Strategic Orchestrator
      |
      v
Persistence / Artifacts / Event Log / Metrics
```

## Quick start

```bash
make install
make train
make test
make serve
```

The API will run at `http://localhost:8000`.

## Docker

```bash
docker build -t busy-bee:latest .
docker run -p 8000:8000 busy-bee:latest
```

## Important note

This repo is intentionally scaffolded to be meaningful immediately while leaving room for your larger Busy Bee roadmap:

- executive intelligence briefs
- domain deepening
- simulation / digital twin
- recommendation governance
- reliability and self-healing features
- runtime and scheduler architecture

## Recommended next implementation order

1. Wire real domain signal providers into `src/busy_bee/domain/`
2. Add persistence layer for events, actions, and approvals
3. Replace stub brief generation with domain scoring engine
4. Expand ML features beyond the starter churn-style example
5. Add auth, role boundaries, and UI integration
6. Add background scheduler once business logic is stable

