from __future__ import annotations

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_base_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()

R_SCRIPTS_DIR = BASE_DIR / "r-scripts"
DATA_DIR = BASE_DIR / "data"
PREPARED_DATA_DIR = DATA_DIR / "prepared"

DEFAULT_DATASET = "murders_USA_2010.rds"


def get_rscript_path() -> str:
    configured_path = os.environ.get("R_TOOL_RSCRIPT")

    if configured_path:
        return configured_path

    return "Rscript"


def build_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    env["R_TOOL_BASE_DIR"] = str(BASE_DIR)
    return env