from __future__ import annotations

import subprocess
import argparse
import sys
from pathlib import Path

from runtime_paths import BASE_DIR, get_rscript_path, build_subprocess_env

PREPARED_DATA_DIR = BASE_DIR / "data" / "prepared"
DEFAULT_DATASET = "survey_data_prepared.csv"

R_SCRIPTS_DIR = BASE_DIR / "r-scripts"


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

    raise ValueError(f"Unbekannte Analyse: {analysis}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=None, help="CSV filename inside ./data/prepared/")

    subparsers = parser.add_subparsers(dest="analysis")

    parser_get_variables = subparsers.add_parser("get_variables")
    parser_get_variables.add_argument("out_path")

    subparsers.add_parser("df")

    parser_chi = subparsers.add_parser("chi_square")
    parser_chi.add_argument("var1")
    parser_chi.add_argument("var2")

    parser_logit = subparsers.add_parser("logit")
    parser_logit.add_argument("dependent_var")
    parser_logit.add_argument("independent_vars", nargs="+")

    parser_lin_reg = subparsers.add_parser("lin_reg")
    parser_lin_reg.add_argument("target_var")
    parser_lin_reg.add_argument("predictor_vars", nargs="+")

    parser_describe = subparsers.add_parser("describe")
    parser_describe.add_argument("var1")

    parser_describeBy = subparsers.add_parser("describeBy")
    parser_describeBy.add_argument("dependent_var")
    parser_describeBy.add_argument("group_var")

    parser_anova = subparsers.add_parser("anova")
    parser_anova.add_argument("dependent_var")
    parser_anova.add_argument("independent_vars", nargs="+")

    parser_unpaired_ttest = subparsers.add_parser("unpaired_ttest")
    parser_unpaired_ttest.add_argument("var1")
    parser_unpaired_ttest.add_argument("var2_or_constant")

    parser_paired_ttest = subparsers.add_parser("paired_ttest")
    parser_paired_ttest.add_argument("var1")
    parser_paired_ttest.add_argument("var2")

    parser_norm_assumption_ttest = subparsers.add_parser("norm_test")
    parser_norm_assumption_ttest.add_argument("dependent_var")
    parser_norm_assumption_ttest.add_argument("group_var")

    parser_welch_test = subparsers.add_parser("welch_test")
    parser_welch_test.add_argument("dependent_var")
    parser_welch_test.add_argument("group_var")

    parser_correlation = subparsers.add_parser("correlation")
    parser_correlation.add_argument("var1")
    parser_correlation.add_argument("var2")

    parser_mann_whitney_test = subparsers.add_parser("mann_whitney_test")
    parser_mann_whitney_test.add_argument("dependent_var")
    parser_mann_whitney_test.add_argument("group_var")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.analysis:
        parser.print_help()
        return 1

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

    if result.returncode != 0:
        print("Error while executing the r-script:")
        print(result.stderr)
        return result.returncode

    print(result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())