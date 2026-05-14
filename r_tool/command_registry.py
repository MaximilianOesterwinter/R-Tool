from __future__ import annotations


COMMANDS: dict[str, dict[str, str]] = {
    "analysis": {
        "df": "dataframe.R",
        "chi_square": "chi_square.R",
        "logit": "logit_model.R",
        "lin_reg": "lin_reg.R",
        "describe": "describe.R",
        "describeBy": "describeBy.R",
        "anova": "anova.R",
        "unpaired_ttest": "unpaired_ttest.R",
        "paired_ttest": "paired_ttest.R",
        "norm_test": "normality_test.R",
        "welch_test": "welch_test.R",
        "correlation": "correlation.R",
        "mann_whitney_test": "mann_whitney_test.R",
    },
    "plots": {
        "histogram": "histogram.R",
        "boxplot": "boxplot.R",
        "boxplot_by_group": "boxplot_by_group.R",
        "scatterplot": "scatterplot.R",
        "barplot": "barplot.R",
        "lineplot": "lineplot.R",
    },
    "preparation": {
        "factorize": "factorize.R",
        "subframe": "subframe.R",
        "rename": "rename.R",
        "mutate": "mutate.R",
        "summarise": "summarise.R",
    },
    "utility": {
        "get_variables": "get_variables.R",
    },
}


def get_script_name(category: str, command: str) -> str:
    try:
        return COMMANDS[category][command]
    except KeyError:
        raise ValueError(f"Unknown command: {category}/{command}") from None