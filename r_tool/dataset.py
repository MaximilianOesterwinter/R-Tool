from __future__ import annotations

from pathlib import Path

from r_tool.config import DEFAULT_DATASET, PREPARED_DATA_DIR


def resolve_dataset_path(dataset_name: str | None) -> Path:
    if dataset_name:
        dataset_path = PREPARED_DATA_DIR / dataset_name
    else:
        dataset_path = PREPARED_DATA_DIR / DEFAULT_DATASET

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    if dataset_path.suffix.lower() != ".rds":
        raise ValueError("Only .rds datasets are supported.")

    return dataset_path