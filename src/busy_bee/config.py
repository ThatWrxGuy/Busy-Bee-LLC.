from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    name: str
    env: str = "dev"
    random_state: int = 42
    log_level: str = "INFO"


class ApiConfig(BaseModel):
    title: str
    version: str


class DataConfig(BaseModel):
    train_path: str
    target_column: str
    test_size: float = Field(gt=0, lt=1)


class ModelConfig(BaseModel):
    type: str
    params: dict[str, Any]


class ArtifactConfig(BaseModel):
    model_dir: str
    model_file: str
    metrics_file: str
    registry_file: str


class GovernanceConfig(BaseModel):
    require_human_approval_for_financial_execution: bool = True
    audit_enabled: bool = True


class StrategicCycleConfig(BaseModel):
    enabled: bool = True
    max_recommendations: int = 5


class Settings(BaseModel):
    app: AppConfig
    api: ApiConfig
    data: DataConfig
    model: ModelConfig
    artifacts: ArtifactConfig
    governance: GovernanceConfig
    strategic_cycle: StrategicCycleConfig


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BUSY_BEE_", env_file=".env", extra="ignore")

    env: str = "dev"
    config: str = "configs/base.yaml"
    log_level: str = "INFO"


def load_settings(config_path: str | Path | None = None) -> Settings:
    env_settings = EnvSettings()
    path = Path(config_path or env_settings.config)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    settings = Settings.model_validate(raw)
    settings.app.log_level = env_settings.log_level or settings.app.log_level
    settings.app.env = env_settings.env or settings.app.env
    return settings
