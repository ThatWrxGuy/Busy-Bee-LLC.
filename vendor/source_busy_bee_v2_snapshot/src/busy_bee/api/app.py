from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException

from busy_bee.config import load_settings
from busy_bee.exceptions import ApprovalRequiredError, ArtifactNotFoundError
from busy_bee.logging_config import configure_logging
from busy_bee.observability.health import readiness
from busy_bee.orchestration.strategic_cycle import StrategicCycleOrchestrator
from busy_bee.schemas.inference import CustomerFeatures
from busy_bee.services.approvals import ApprovalService
from busy_bee.services.predictor import PredictorService


def create_app() -> FastAPI:
    settings = load_settings()
    configure_logging(settings.app.log_level)

    app = FastAPI(title=settings.api.title, version=settings.api.version)
    model_path = str(Path(settings.artifacts.model_dir) / settings.artifacts.model_file)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> dict[str, str]:
        return readiness(model_path)

    @app.post("/predict")
    def predict(payload: CustomerFeatures) -> dict[str, object]:
        try:
            predictor = PredictorService(model_path)
            prediction = predictor.predict_one(payload)
            return {"prediction": prediction}
        except ArtifactNotFoundError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.get("/briefs/latest")
    def latest_brief() -> dict[str, object]:
        brief = StrategicCycleOrchestrator().run_cycle()
        return brief.model_dump()

    @app.post("/governance/finance/execute")
    def finance_execute(approved: bool = False) -> dict[str, str]:
        try:
            ApprovalService(
                settings.governance.require_human_approval_for_financial_execution
            ).assert_execution_allowed("finance", approved=approved)
            return {"status": "execution_allowed"}
        except ApprovalRequiredError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    return app
