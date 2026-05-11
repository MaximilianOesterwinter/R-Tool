from __future__ import annotations

import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()
CONFIG_PATH = BASE_DIR / "config.json"
DEFAULT_MINIMUM_R_VERSION = "4.4.3"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(config: dict) -> None:
    CONFIG_PATH.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _existing(paths: list[Path | str]) -> str | None:
    for p in paths:
        p = Path(p)
        if p.exists():
            return str(p)
    return None


def parse_version(version: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        return None
    return tuple(map(int, match.groups()))


def parse_r_folder_version(folder_name: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"R-(\d+)\.(\d+)\.(\d+)", folder_name.strip())
    if not match:
        return None
    return tuple(map(int, match.groups()))


def get_minimum_r_version() -> tuple[int, int, int]:
    cfg = load_config()

    configured = str(
        cfg.get("minimum_r_version", DEFAULT_MINIMUM_R_VERSION)
        ).strip()

    return tuple(map(int, configured.split(".")))


def find_windows_rscript(minimum_version: tuple[int, int, int]) -> str | None:
    r_root = Path(r"C:\Program Files\R")

    if not r_root.exists():
        return None

    candidates: list[tuple[tuple[int, int, int], Path]] = []

    for folder in r_root.iterdir():
        if not folder.is_dir():
            continue

        version = parse_r_folder_version(folder.name)
        if version is None:
            continue

        if version < minimum_version:
            continue

        rscript = folder / "bin" / "Rscript.exe"
        if rscript.exists():
            candidates.append((version, rscript))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return str(candidates[0][1])


def get_rscript_path() -> str:
    cfg = load_config()

    configured = cfg.get("rscript_path", "").strip()
    if configured and Path(configured).exists():
        return configured

    env_path = os.environ.get("RSCRIPT_PATH", "").strip()
    if env_path and Path(env_path).exists():
        return env_path

    found = shutil.which("Rscript")
    if found:
        return found

    system = platform.system()

    if system == "Windows":
        minimum_version = get_minimum_r_version()
        found = find_windows_rscript(minimum_version)
        if found:
            return found
    else:
        candidates = [
            Path("/usr/bin/Rscript"),
            Path("/usr/local/bin/Rscript"),
            Path("/opt/homebrew/bin/Rscript"),
        ]

        found = _existing(candidates)
        if found:
            return found

    raise FileNotFoundError(
        "Rscript not found.\n"
        "Please install R and optionally insert its path in config.json."
    )


def get_pandoc_path() -> str | None:
    cfg = load_config()

    configured = cfg.get("pandoc_path", "").strip()
    if configured and Path(configured).exists():
        return configured

    env_path = os.environ.get("PANDOC_PATH", "").strip()
    if env_path and Path(env_path).exists():
        return env_path

    rstudio_pandoc_dir = os.environ.get("RSTUDIO_PANDOC", "").strip()
    if rstudio_pandoc_dir:
        exe_name = "pandoc.exe" if platform.system() == "Windows" else "pandoc"
        candidate = Path(rstudio_pandoc_dir) / exe_name
        if candidate.exists():
            return str(candidate)

    found = shutil.which("pandoc")
    if found:
        return found

    system = platform.system()

    if system == "Windows":
        candidates = [
            Path(r"C:\Program Files\Pandoc\pandoc.exe"),
            Path.home() / "AppData" / "Local" / "Pandoc" / "pandoc.exe",
        ]
    else:
        candidates = [
            Path("/usr/bin/pandoc"),
            Path("/usr/local/bin/pandoc"),
        ]

    return _existing(candidates)


def build_subprocess_env() -> dict:
    env = os.environ.copy()

    pandoc_path = get_pandoc_path()
    if pandoc_path:
        pandoc_dir = str(Path(pandoc_path).parent)
        env["PATH"] = pandoc_dir + os.pathsep + env.get("PATH", "")
        env["RSTUDIO_PANDOC"] = pandoc_dir

    return env