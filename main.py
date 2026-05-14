from __future__ import annotations

import argparse
import sys

from r_tool.commands import (
    get_variable_names,
    run_analysis,
    run_plot,
    run_preparation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        default=None,
        help="RDS filename inside ./data/prepared/",
    )

    subparsers = parser.add_subparsers(dest="mode")

    build_utility_parser(subparsers)
    build_analysis_parser(subparsers)
    build_plot_parser(subparsers)
    build_preparation_parser(subparsers)

    return parser


def build_utility_parser(subparsers) -> None:
    utility_parser = subparsers.add_parser("utility")
    utility_subparsers = utility_parser.add_subparsers(dest="utility")

    get_variables_parser = utility_subparsers.add_parser("get_variables")
    get_variables_parser.add_argument("out_path")


def build_analysis_parser(subparsers) -> None:
    analysis_parser = subparsers.add_parser("analysis")
    analysis_subparsers = analysis_parser.add_subparsers(dest="analysis")

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

    parser_unpaired = analysis_subparsers.add_parser("unpaired_ttest")
    parser_unpaired.add_argument("var1")
    parser_unpaired.add_argument("var2_or_constant")

    parser_paired = analysis_subparsers.add_parser("paired_ttest")
    parser_paired.add_argument("var1")
    parser_paired.add_argument("var2")

    parser_norm = analysis_subparsers.add_parser("norm_test")
    parser_norm.add_argument("dependent_var")
    parser_norm.add_argument("group_var")

    parser_welch = analysis_subparsers.add_parser("welch_test")
    parser_welch.add_argument("dependent_var")
    parser_welch.add_argument("group_var")

    parser_corr = analysis_subparsers.add_parser("correlation")
    parser_corr.add_argument("var1")
    parser_corr.add_argument("var2")

    parser_mann = analysis_subparsers.add_parser("mann_whitney_test")
    parser_mann.add_argument("dependent_var")
    parser_mann.add_argument("group_var")


def build_plot_parser(subparsers) -> None:
    plot_parser = subparsers.add_parser("plot")
    plot_subparsers = plot_parser.add_subparsers(dest="plot")

    parser_hist = plot_subparsers.add_parser("histogram")
    parser_hist.add_argument("var1")

    parser_box = plot_subparsers.add_parser("boxplot")
    parser_box.add_argument("var1")

    parser_box_group = plot_subparsers.add_parser("boxplot_by_group")
    parser_box_group.add_argument("var1")
    parser_box_group.add_argument("group_var")

    parser_scatter = plot_subparsers.add_parser("scatterplot")
    parser_scatter.add_argument("var1")
    parser_scatter.add_argument("var2")

    parser_bar = plot_subparsers.add_parser("barplot")
    parser_bar.add_argument("var1")
    parser_bar.add_argument("var2", nargs="?", default="")
    parser_bar.add_argument("--stat-identity", action="store_true")
    add_plot_label_args(parser_bar)

    parser_bar_group = plot_subparsers.add_parser("barplot_by_group")
    parser_bar_group.add_argument("var1")
    parser_bar_group.add_argument("group_var")

    parser_line = plot_subparsers.add_parser("lineplot")
    parser_line.add_argument("x_var")
    parser_line.add_argument("y_var")

def add_plot_label_args(parser) -> None:
    parser.add_argument("--flip", action="store_true")
    parser.add_argument("--beside", action="store_true")
    parser.add_argument("--main-lab", default="")
    parser.add_argument("--x-lab", default="")
    parser.add_argument("--y-lab", default="")
    parser.add_argument("--group-var", default="")


def build_preparation_parser(subparsers) -> None:
    prep_parser = subparsers.add_parser("preparation")
    prep_subparsers = prep_parser.add_subparsers(dest="preparation")

    parser_factorize = prep_subparsers.add_parser("factorize")
    parser_factorize.add_argument("variables", nargs="+")
    parser_factorize.add_argument("--levels", default="")
    parser_factorize.add_argument("--labels", default="")

    parser_subframe = prep_subparsers.add_parser("subframe")
    parser_subframe.add_argument("variables", nargs="+")
    parser_subframe.add_argument("--subframe-name", required=True)
    parser_subframe.add_argument("--pivot-longer", action="store_true")
    parser_subframe.add_argument("--remove-na", action="store_true")

    parser_rename = prep_subparsers.add_parser("rename")
    parser_rename.add_argument(
        "rename_pairs",
        nargs="+",
        help="Pairs expected by rename.R, e.g. old1 new1 old2 new2",
    )

    parser_mutate = prep_subparsers.add_parser("mutate")
    parser_mutate.add_argument("variables", nargs="+")
    parser_mutate.add_argument("--new-var-name", required=True)
    parser_mutate.add_argument("--mutate-operation", required=True)
    parser_mutate.add_argument("--mutate-operator", default="")
    parser_mutate.add_argument("--na-rm", action="store_true")
    parser_mutate.add_argument("--reverse-min", default="")
    parser_mutate.add_argument("--reverse-max", default="")
    parser_mutate.add_argument("--recode-else", default="")
    parser_mutate.add_argument("--recode-rules", nargs="*", default=[])

    parser_summarise = prep_subparsers.add_parser("summarise")
    parser_summarise.add_argument("variables", nargs="+")
    parser_summarise.add_argument("--output-name", required=True)
    parser_summarise.add_argument("--selected-function", required=True)
    parser_summarise.add_argument("--na-rm", action="store_true")
    parser_summarise.add_argument("--group-vars", nargs="*", default=[])


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        return 1

    try:
        result = dispatch(args)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if result.returncode != 0:
        print("Error while executing the R script:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return result.returncode

    print(result.stdout)
    return 0


def dispatch(args):
    if args.mode == "utility":
        if args.utility == "get_variables":
            return get_variable_names(args.out_path, args.dataset)

    if args.mode == "analysis":
        return dispatch_analysis(args)

    if args.mode == "plot":
        return dispatch_plot(args)

    if args.mode == "preparation":
        return dispatch_preparation(args)

    raise ValueError(f"Unknown mode: {args.mode}")


def dispatch_analysis(args):
    if args.analysis == "df":
        return run_analysis("df", [], args.dataset)

    if args.analysis == "chi_square":
        return run_analysis(
            "chi_square",
            [args.var1, args.var2],
            args.dataset,
        )

    if args.analysis == "logit":
        return run_analysis(
            "logit",
            [args.dependent_var, *args.independent_vars],
            args.dataset,
        )

    if args.analysis == "lin_reg":
        return run_analysis(
            "lin_reg",
            [args.target_var, *args.predictor_vars],
            args.dataset,
        )

    if args.analysis == "describe":
        return run_analysis(
            "describe",
            [args.var1],
            args.dataset,
        )

    if args.analysis == "describeBy":
        return run_analysis(
            "describeBy",
            [args.dependent_var, args.group_var],
            args.dataset,
        )

    if args.analysis == "anova":
        return run_analysis(
            "anova",
            [args.dependent_var, *args.independent_vars],
            args.dataset,
        )

    if args.analysis == "unpaired_ttest":
        return run_analysis(
            "unpaired_ttest",
            [args.var1, args.var2_or_constant],
            args.dataset,
        )

    if args.analysis == "paired_ttest":
        return run_analysis(
            "paired_ttest",
            [args.var1, args.var2],
            args.dataset,
        )

    if args.analysis == "norm_test":
        return run_analysis(
            "norm_test",
            [args.dependent_var, args.group_var],
            args.dataset,
        )

    if args.analysis == "welch_test":
        return run_analysis(
            "welch_test",
            [args.dependent_var, args.group_var],
            args.dataset,
        )

    if args.analysis == "correlation":
        return run_analysis(
            "correlation",
            [args.var1, args.var2],
            args.dataset,
        )

    if args.analysis == "mann_whitney_test":
        return run_analysis(
            "mann_whitney_test",
            [args.dependent_var, args.group_var],
            args.dataset,
        )

    raise ValueError(f"Unknown analysis: {args.analysis}")


def dispatch_plot(args):
    if args.plot == "histogram":
        return run_plot("histogram", [args.var1], args.dataset)

    if args.plot == "boxplot":
        return run_plot("boxplot", [args.var1], args.dataset)

    if args.plot == "boxplot_by_group":
        return run_plot(
            "boxplot_by_group",
            [args.var1, args.group_var],
            args.dataset,
        )

    if args.plot == "scatterplot":
        return run_plot(
            "scatterplot",
            [args.var1],
            args.dataset,
            jitter=args.jitter,
            main_lab=args.main_lab,
            x_lab=args.x_lab,
            y_lab=args.y_lab,
            group_var=args.group_var,
        )

    if args.plot == "barplot":
        return run_plot(
            "barplot",
            variables,
            args.dataset,
            flip=args.flip,
            beside=args.beside,
            stat_identity=args.stat_identity,
            main_lab=args.main_lab,
            x_lab=args.x_lab,
            y_lab=args.y_lab,
            group_var=args.group_var,
        )

    if args.plot == "lineplot":
        return run_plot(
            "lineplot",
            [args.x_var, args.y_var],
            args.dataset,
        )

    raise ValueError(f"Unknown plot type: {args.plot}")


def dispatch_preparation(args):
    if args.preparation == "factorize":
        return run_preparation(
            "factorize",
            args.variables,
            args.dataset,
            levels=args.levels,
            labels=args.labels,
        )

    if args.preparation == "subframe":
        return run_preparation(
            "subframe",
            args.variables,
            args.dataset,
            subframe_name=args.subframe_name,
            pivot_longer=args.pivot_longer,
            remove_na=args.remove_na,
        )

    if args.preparation == "rename":
        return run_preparation(
            "rename",
            [],
            args.dataset,
            rename_pairs=args.rename_pairs,
        )

    if args.preparation == "mutate":
        return run_preparation(
            "mutate",
            args.variables,
            args.dataset,
            new_var_name=args.new_var_name,
            mutate_operation=args.mutate_operation,
            mutate_operator=args.mutate_operator,
            na_rm=args.na_rm,
            reverse_min=args.reverse_min,
            reverse_max=args.reverse_max,
            recode_else=args.recode_else,
            recode_rules=args.recode_rules,
        )

    if args.preparation == "summarise":
        return run_preparation(
            "summarise",
            args.variables,
            args.dataset,
            output_name=args.output_name,
            selected_function=args.selected_function,
            na_rm=args.na_rm,
            group_vars=args.group_vars,
        )

    raise ValueError(f"Unknown preparation method: {args.preparation}")


if __name__ == "__main__":
    raise SystemExit(main())