from __future__ import annotations

import subprocess
from pathlib import Path

from r_tool.command_registry import get_script_name
from r_tool.config import R_SCRIPTS_DIR, build_subprocess_env, get_rscript_path
from r_tool.dataset import resolve_dataset_path


class RRunner:
    def run_script(
        self,
        script_name: str,
        dataset_name: str | None = None,
        *args: str,
    ) -> subprocess.CompletedProcess[str]:
        rscript_path = get_rscript_path()
        script_path = R_SCRIPTS_DIR / script_name
        dataset_path = resolve_dataset_path(dataset_name)

        if not script_path.exists():
            raise FileNotFoundError(f"R script not found: {script_path}")

        command = [
            rscript_path,
            str(script_path),
            str(dataset_path),
            *map(str, args),
        ]

        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=build_subprocess_env(),
            check=False,
        )

    def run_command(
        self,
        category: str,
        command: str,
        dataset_name: str | None = None,
        *args: str,
    ) -> subprocess.CompletedProcess[str]:
        script_name = get_script_name(category, command)

        return self.run_script(
            script_name,
            dataset_name,
            *args,
        )

    def get_variable_names(
        self,
        out_path: str | Path,
        dataset_name: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return self.run_command(
            "utility",
            "get_variables",
            dataset_name,
            str(out_path),
        )