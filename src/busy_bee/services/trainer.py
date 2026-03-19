from __future__ import annotations

import json
import logging
from datetime import datetime, UTC
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

from busy_bee.config import Settings
from busy_bee.infrastructure.audit import AuditLogger
from busy_bee.infrastructure.model_registry import ModelRegistry
from busy_bee.ml.data import detect_feature_types, load_csv, split_features_target, validate_training_data
from busy_bee.ml.metrics import classification_metrics
from busy_bee.ml.pipeline import build_training_pipeline

logger = logging.getLogger(__name__)


class TrainerService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        artifact_dir = Path(settings.artifacts.model_dir)
        self.audit = AuditLogger(str(artifact_dir / "audit_log.jsonl"))
        self.registry = ModelRegistry(str(artifact_dir / settings.artifacts.registry_file))

    def run(self) -> dict:
        df = load_csv(self.settings.data.train_path)
        validate_training_data(df, self.settings.data.target_column)
        X, y = split_features_target(df, self.settings.data.target_column)
        numeric_features, categorical_features = detect_feature_types(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.settings.data.test_size,
            random_state=self.settings.app.random_state,
            stratify=y,
        )

        pipeline = build_training_pipeline(
            numeric_features,
            categorical_features,
            self.settings.model.type,
            self.settings.model.params,
        )
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        metrics = classification_metrics(y_test, y_pred)

        artifact_dir = Path(self.settings.artifacts.model_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        model_path = artifact_dir / self.settings.artifacts.model_file
        metrics_path = artifact_dir / self.settings.artifacts.metrics_file

        joblib.dump(pipeline, model_path)
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

        record = {
            "registered_at": datetime.now(UTC).isoformat(),
            "model_path": str(model_path),
            "metrics": metrics,
            "model_type": self.settings.model.type,
        }
        self.registry.register(record)
        self.audit.write("model_trained", record)
        logger.info("Training complete: %s", record)

        return {
            "model_path": str(model_path),
            "metrics_path": str(metrics_path),
            "metrics": metrics,
        }
