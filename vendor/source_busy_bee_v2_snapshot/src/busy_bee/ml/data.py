from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    return pd.read_csv(csv_path)


def validate_training_data(df: pd.DataFrame, target_column: str) -> None:
    if df.empty:
        raise ValueError("Training data is empty")
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found")
    if df[target_column].isnull().any():
        raise ValueError("Target column contains missing values")


def split_features_target(df: pd.DataFrame, target_column: str):
    return df.drop(columns=[target_column]), df[target_column]


def detect_feature_types(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    return numeric, categorical
