from __future__ import annotations
from ragops.config import get_settings


def log_query_run(metrics: dict, params: dict | None = None) -> None:
    settings = get_settings()
    if not settings.enable_mlflow:
        return
    try:
        import mlflow
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment("ragops-sentinel-baseline")
        with mlflow.start_run():
            for key, value in (params or {}).items():
                mlflow.log_param(key, value)
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, float(value))
    except Exception:
        # Logging failure must not break the query path.
        return
