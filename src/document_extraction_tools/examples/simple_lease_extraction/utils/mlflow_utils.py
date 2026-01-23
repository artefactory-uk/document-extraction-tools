"""Utilities for configuring MLflow in the simple lease example."""

import mlflow


def setup_mlflow(experiment_name: str, tracking_uri: str) -> None:
    """Configure MLflow tracking and autologging for Gemini."""
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
