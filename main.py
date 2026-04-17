from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from runtime_paths import BASE_DIR, get_rscript_path, build_subprocess_env

BASE_DIR = Path(BASE_DIR)
R_SCRIPTS_DIR = BASE_DIR / "r-scripts"
PREPARED_DATA_DIR = BASE_DIR / "data" / "prepared"
DEFAULT_DATASET = "example_1_prepared.csv"


def resolve_dataset_path(dataset_name: str | None) -> Path:
    if dataset_name:
        dataset_path = PREPARED_DATA_DIR / dataset_name
    else:
        dataset_path = PREPARED_DATA_DIR / DEFAULT_DATASET

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    if dataset_path.suffix.lower() != ".csv":
        raise ValueError("Only .csv datasets are supported.")

    return dataset_path


def run_r_script(script_name: str, dataset_name: str | None = None, *args: str) -> subprocess.CompletedProcess:
    rscript_path = get_rscript_path()
    script_path = R_SCRIPTS_DIR / script_name
    data_path = resolve_dataset_path(dataset_name)

    command = [rscript_path, str(script_path), str(data_path), *map(str, args)]

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=build_subprocess_env()
    )


def get_variable_names(out_path: str, dataset_name: str | None = None) -> subprocess.CompletedProcess:
    rscript_path = get_rscript_path()
    script_path = R_SCRIPTS_DIR / "get_variables.R"
    data_path = resolve_dataset_path(dataset_name)

    command = [rscript_path, str(script_path), str(data_path), str(out_path)]

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=build_subprocess_env()
    )


def run_analysis(analysis: str, variables: list[str], dataset_name: str | None = None) -> subprocess.CompletedProcess:
    if analysis == "df":
        return run_r_script("dataframe.R", dataset_name)

    if analysis == "chi_square":
        return run_r_script("chi_square.R", dataset_name, variables[0], variables[1])

    if analysis == "logit":
        return run_r_script("logit_model.R", dataset_name, variables[0], *variables[1:])

    if analysis == "lin_reg":
        return run_r_script("lin_reg.R", dataset_name, variables[0], *variables[1:])

    if analysis == "describe":
        return run_r_script("describe.R", dataset_name, variables[0])

    if analysis == "describeBy":
        return run_r_script("describeBy.R", dataset_name, variables[0], variables[1])

    if analysis == "anova":
        return run_r_script("anova.R", dataset_name, variables[0], *variables[1:])

    if analysis == "unpaired_ttest":
        return run_r_script("unpaired_ttest.R", dataset_name, variables[0], variables[1])

    if analysis == "paired_ttest":
        return run_r_script("paired_ttest.R", dataset_name, variables[0], variables[1])

    if analysis == "norm_test":
        return run_r_script("normality_test.R", dataset_name, variables[0], variables[1])

    if analysis == "welch_test":
        return run_r_script("welch_test.R", dataset_name, variables[0], variables[1])

    if analysis == "correlation":
        return run_r_script("correlation.R", dataset_name, variables[0], variables[1])

    if analysis == "mann_whitney_test":
        return run_r_script("mann_whitney_test.R", dataset_name, variables[0], variables[1])

    raise ValueError(f"Unknown analysis: {analysis}")


def run_plot(plot_type: str, variables: list[str], dataset_name: str | None = None) -> subprocess.CompletedProcess:
    if plot_type == "histogram":
        return run_r_script("histogram.R", dataset_name, variables[0])

    if plot_type == "boxplot":
        return run_r_script("boxplot.R", dataset_name, variables[0])

    if plot_type == "boxplot_by_group":
        return run_r_script("boxplot_by_group.R", dataset_name, variables[0], variables[1])

    if plot_type == "scatterplot":
        return run_r_script("scatterplot.R", dataset_name, variables[0], variables[1])

    if plot_type == "barplot":
        return run_r_script("barplot.R", dataset_name, variables[0])

    if plot_type == "barplot_by_group":
        return run_r_script("barplot_by_group.R", dataset_name, variables[0], variables[1])

    if plot_type == "lineplot":
        return run_r_script("lineplot.R", dataset_name, variables[0], variables[1])

    raise ValueError(f"Unknown plot type: {plot_type}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=None, help="CSV filename inside ./data/prepared/")

    subparsers = parser.add_subparsers(dest="mode")

    analysis_parser = subparsers.add_parser("analysis")
    analysis_subparsers = analysis_parser.add_subparsers(dest="analysis")

    parser_get_variables = analysis_subparsers.add_parser("get_variables")
    parser_get_variables.add_argument("out_path")

    analysis_subparsers.add_parser("df")

    parser_chi = analysis_subparsers.add_parser("chi_square")
    parser_chi.add_argument("var1")
    parser_chi.add_argument("var2")

    parser_logit = analysis_subparsers.add_parser("logit")
    parser_logit.add_argument("dependent_var")
    parser_logit.add_argument("independent_vars", nargs="+")

    parser_lin_reg = analysis_subparsers.add_parser("lin_reg")
    parser_lin_reg.add_argument("target_var")
    parser_lin_reg.add_argument("predictor_vars", nargs="+")

    parser_describe = analysis_subparsers.add_parser("describe")
    parser_describe.add_argument("var1")

    parser_describe_by = analysis_subparsers.add_parser("describeBy")
    parser_describe_by.add_argument("dependent_var")
    parser_describe_by.add_argument("group_var")

    parser_anova = analysis_subparsers.add_parser("anova")
    parser_anova.add_argument("dependent_var")
    parser_anova.add_argument("independent_vars", nargs="+")

    parser_unpaired_ttest = analysis_subparsers.add_parser("unpaired_ttest")
    parser_unpaired_ttest.add_argument("var1")
    parser_unpaired_ttest.add_argument("var2_or_constant")

    parser_paired_ttest = analysis_subparsers.add_parser("paired_ttest")
    parser_paired_ttest.add_argument("var1")
    parser_paired_ttest.add_argument("var2")

    parser_norm_test = analysis_subparsers.add_parser("norm_test")
    parser_norm_test.add_argument("dependent_var")
    parser_norm_test.add_argument("group_var")

    parser_welch_test = analysis_subparsers.add_parser("welch_test")
    parser_welch_test.add_argument("dependent_var")
    parser_welch_test.add_argument("group_var")

    parser_correlation = analysis_subparsers.add_parser("correlation")
    parser_correlation.add_argument("var1")
    parser_correlation.add_argument("var2")

    parser_mann_whitney = analysis_subparsers.add_parser("mann_whitney_test")
    parser_mann_whitney.add_argument("dependent_var")
    parser_mann_whitney.add_argument("group_var")

    plot_parser = subparsers.add_parser("plot")
    plot_subparsers = plot_parser.add_subparsers(dest="plot")

    parser_histogram = plot_subparsers.add_parser("histogram")
    parser_histogram.add_argument("var1")

    parser_boxplot = plot_subparsers.add_parser("boxplot")
    parser_boxplot.add_argument("var1")

    parser_boxplot_group = plot_subparsers.add_parser("boxplot_by_group")
    parser_boxplot_group.add_argument("var1")
    parser_boxplot_group.add_argument("group_var")

    parser_scatter = plot_subparsers.add_parser("scatterplot")
    parser_scatter.add_argument("var1")
    parser_scatter.add_argument("var2")

    parser_barplot = plot_subparsers.add_parser("barplot")
    parser_barplot.add_argument("var1")

    parser_barplot_group = plot_subparsers.add_parser("barplot_by_group")
    parser_barplot_group.add_argument("var1")
    parser_barplot_group.add_argument("group_var")

    parser_lineplot = plot_subparsers.add_parser("lineplot")
    parser_lineplot.add_argument("x_var")
    parser_lineplot.add_argument("y_var")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return 1

    if args.mode == "analysis":
        if args.analysis == "get_variables":
            result = get_variable_names(args.out_path, args.dataset)
        elif args.analysis == "df":
            result = run_analysis("df", [], args.dataset)
        elif args.analysis == "chi_square":
            result = run_analysis("chi_square", [args.var1, args.var2], args.dataset)
        elif args.analysis == "logit":
            result = run_analysis("logit", [args.dependent_var, *args.independent_vars], args.dataset)
        elif args.analysis == "lin_reg":
            result = run_analysis("lin_reg", [args.target_var, *args.predictor_vars], args.dataset)
        elif args.analysis == "describe":
            result = run_analysis("describe", [args.var1], args.dataset)
        elif args.analysis == "describeBy":
            result = run_analysis("describeBy", [args.dependent_var, args.group_var], args.dataset)
        elif args.analysis == "anova":
            result = run_analysis("anova", [args.dependent_var, *args.independent_vars], args.dataset)
        elif args.analysis == "unpaired_ttest":
            result = run_analysis("unpaired_ttest", [args.var1, args.var2_or_constant], args.dataset)
        elif args.analysis == "paired_ttest":
            result = run_analysis("paired_ttest", [args.var1, args.var2], args.dataset)
        elif args.analysis == "norm_test":
            result = run_analysis("norm_test", [args.dependent_var, args.group_var], args.dataset)
        elif args.analysis == "welch_test":
            result = run_analysis("welch_test", [args.dependent_var, args.group_var], args.dataset)
        elif args.analysis == "correlation":
            result = run_analysis("correlation", [args.var1, args.var2], args.dataset)
        elif args.analysis == "mann_whitney_test":
            result = run_analysis("mann_whitney_test", [args.dependent_var, args.group_var], args.dataset)
        else:
            parser.print_help()
            return 1

    elif args.mode == "plot":
        if args.plot == "histogram":
            result = run_plot("histogram", [args.var1], args.dataset)
        elif args.plot == "boxplot":
            result = run_plot("boxplot", [args.var1], args.dataset)
        elif args.plot == "boxplot_by_group":
            result = run_plot("boxplot_by_group", [args.var1, args.group_var], args.dataset)
        elif args.plot == "scatterplot":
            result = run_plot("scatterplot", [args.var1, args.var2], args.dataset)
        elif args.plot == "barplot":
            result = run_plot("barplot", [args.var1], args.dataset)
        elif args.plot == "barplot_by_group":
            result = run_plot("barplot_by_group", [args.var1, args.group_var], args.dataset)
        elif args.plot == "lineplot":
            result = run_plot("lineplot", [args.x_var, args.y_var], args.dataset)
        else:
            parser.print_help()
            return 1

    else:
        parser.print_help()
        return 1

    if result.returncode != 0:
        print("Error while executing the r-script:")
        print(result.stderr)
        return result.returncode

    print(result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())