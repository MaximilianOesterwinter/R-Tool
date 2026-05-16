from __future__ import annotations

import subprocess
from typing import Any

from r_tool.r_runner import RRunner


runner = RRunner()


def run_analysis(
    analysis: str,
    variables: list[str],
    dataset_name: str | None = None,
) -> subprocess.CompletedProcess[str]:
    args = build_analysis_args(analysis, variables)

    return runner.run_command(
        "analysis",
        analysis,
        dataset_name,
        *args,
    )


def run_plot(
    plot_type: str,
    variables: list[str],
    dataset_name: str | None = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    args = build_plot_args(plot_type, variables, **kwargs)

    return runner.run_command(
        "plots",
        plot_type,
        dataset_name,
        *args,
    )


def run_preparation(
    preparation: str,
    variables: list[str],
    dataset_name: str | None = None,
    levels: str = "",
    labels: str = "",
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    args = build_preparation_args(
        preparation,
        variables,
        levels=levels,
        labels=labels,
        **kwargs,
    )

    return runner.run_command(
        "preparation",
        preparation,
        dataset_name,
        *args,
    )


def get_variable_names(
    out_path: str,
    dataset_name: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return runner.get_variable_names(out_path, dataset_name)


def build_analysis_args(
    analysis: str,
    variables: list[str],
) -> list[str]:
    if analysis == "df":
        return []

    expected_lengths = {
        "chi_square": 2,
        "describe": 1,
        "describeBy": 2,
        "unpaired_ttest": 2,
        "paired_ttest": 2,
        "norm_test": 2,
        "welch_test": 2,
        "correlation": 2,
        "mann_whitney_test": 2,
    }

    if analysis in expected_lengths:
        require_variables(variables, expected_lengths[analysis], analysis)
        return variables

    if analysis in {"logit", "lin_reg", "anova"}:
        require_variables(variables, 2, analysis)
        return variables

    raise ValueError(f"Unknown analysis: {analysis}")


def build_plot_args(
    plot_type: str,
    variables: list[str],
    **kwargs: Any,
) -> list[str]:
    if plot_type == "boxplot":
        require_variables(variables, 1, plot_type)
        return [
            kwargs.get("main_lab", ""),
            kwargs.get("x_lab", ""),
            kwargs.get("y_lab", ""),
            bool_to_r(kwargs.get("flip", False)),
            bool_to_r(kwargs.get("show_outliers", False)),
            bool_to_r(kwargs.get("show_points", False)),
            bool_to_r(kwargs.get("show_mean", False)),
            bool_to_r(kwargs.get("show_notches", False)),
            bool_to_r(kwargs.get("show_n", False)),
            bool_to_r(kwargs.get("color_by_group", False)),
            bool_to_r(kwargs.get("sort_groups", False)),
            kwargs.get("group_var", ""),
            kwargs.get("facet_var", ""),
            kwargs.get("weight_var", ""),
            variables[0]
        ]

    if plot_type == "histogram":
        require_variables(variables, 1, plot_type)
        return [
            kwargs.get("binwidth", ""),
            bool_to_r(kwargs.get("norm", False)),
            bool_to_r(kwargs.get("show_density", False)),
            kwargs.get("main_lab", ""),
            kwargs.get("x_lab", ""),
            kwargs.get("y_lab", ""),
            variables[0]
        ]

    if plot_type == "scatterplot":
        require_variables(variables, 2, plot_type)
        return [
            bool_to_r(kwargs.get("jitter", False)),
            kwargs.get("main_lab", ""),
            kwargs.get("x_lab", ""),
            kwargs.get("y_lab", ""),
            kwargs.get("group_var", ""),
            variables[0],
            variables[1]
        ]

    if plot_type == "barplot":
        require_variables(variables, 1, plot_type)

        stat_identity = kwargs.get("stat_identity", False)

        if stat_identity:
            require_variables(variables, 2, plot_type)
        
        return [
            bool_to_r(kwargs.get("flip", False)),
            bool_to_r(kwargs.get("beside", False)),
            bool_to_r(kwargs.get("stat_identity", False)),
            kwargs.get("main_lab", ""),
            kwargs.get("x_lab", ""),
            kwargs.get("y_lab", ""),
            kwargs.get("group_var", ""),
            variables[0],
            variables[1] if len(variables) > 1 else ""
        ]

    raise ValueError(f"Unknown plot type: {plot_type}")


def build_preparation_args(
    preparation: str,
    variables: list[str],
    levels: str = "",
    labels: str = "",
    **kwargs: Any,
) -> list[str]:
    if preparation == "factorize":
        require_variables(variables, 1, preparation)
        return [levels, labels, *variables]

    if preparation == "subframe":
        require_variables(variables, 1, preparation)
        return [
            kwargs.get("subframe_name", ""),
            bool_to_r(kwargs.get("pivot_longer", False)),
            bool_to_r(kwargs.get("remove_na", False)),
            kwargs.get("names_to", ""),
            kwargs.get("values_to", ""),
            *variables,
        ]

    if preparation == "rename":
        rename_pairs = kwargs.get("rename_pairs", [])

        if not rename_pairs:
            raise ValueError("Rename requires at least one rename pair.")

        return list(rename_pairs)

    if preparation == "mutate":
        require_variables(variables, 1, preparation)

        base_args = [
            kwargs.get("new_var_name", ""),
            kwargs.get("mutate_operation", ""),
            kwargs.get("mutate_operator", ""),
            bool_to_r(kwargs.get("na_rm", False)),
            kwargs.get("reverse_min", ""),
            kwargs.get("reverse_max", ""),
        ]

        if kwargs.get("mutate_operation") == "recode":
            return [
                *base_args,
                kwargs.get("recode_else", ""),
                variables[0],
                *kwargs.get("recode_rules", []),
            ]

        return [
            *base_args,
            *variables,
        ]

    if preparation == "summarise":
        require_variables(variables, 1, preparation)

        group_vars = kwargs.get("group_vars", [])

        if isinstance(group_vars, list):
            group_vars = ",".join(group_vars)

        if group_vars is None:
            group_vars = ""

        return [
            kwargs.get("output_name", ""),
            kwargs.get("selected_function", ""),
            bool_to_r(kwargs.get("na_rm", False)),
            group_vars,
            *variables,
        ]

    raise ValueError(f"Unknown preparation method: {preparation}")


def require_variables(
    variables: list[str],
    minimum: int,
    command_name: str,
) -> None:
    if len(variables) < minimum:
        raise ValueError(
            f"{command_name} requires at least {minimum} variable(s)."
        )


def bool_to_r(value: Any) -> str:
    return str(bool(value)).lower()