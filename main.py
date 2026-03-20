import subprocess
import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data"/ "survey_data.csv"
                               ############
    # Enter your exact filename of the dataset here but keep the file-type
    ######################################################################

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="analysis")

# df
parser_df = subparsers.add_parser("df")

# chi_square
parser_chi = subparsers.add_parser("chi_square")
parser_chi.add_argument("var1")
parser_chi.add_argument("var2")

# logit
parser_logit = subparsers.add_parser("logit")
parser_logit.add_argument("dependent_var")
parser_logit.add_argument("independent_vars", nargs="+")

# lin_reg
parser_lin_reg = subparsers.add_parser("lin_reg")
parser_lin_reg.add_argument("target_var")
parser_lin_reg.add_argument("predictor_vars", nargs="+")

# describe
parser_describe = subparsers.add_parser("describe")
parser_describe.add_argument("var1")

# describeBy
parser_describeBy = subparsers.add_parser("describeBy")
parser_describeBy.add_argument("dependent_var")
parser_describeBy.add_argument("group_var")

# anova
parser_anova = subparsers.add_parser("anova")
parser_anova.add_argument("dependent_var")
parser_anova.add_argument("independent_vars", nargs="+")

# unpaired_ttest
parser_unpaired_ttest = subparsers.add_parser("unpaired_ttest")
parser_unpaired_ttest.add_argument("var1")
parser_unpaired_ttest.add_argument("var2_or_constant")

# paired_ttest
parser_paired_ttest = subparsers.add_parser("paired_ttest")
parser_paired_ttest.add_argument("var1")
parser_paired_ttest.add_argument("var2")

# norm_assumption_ttest
parser_norm_assumption_ttest = subparsers.add_parser("norm_ttest")
parser_norm_assumption_ttest.add_argument("dependent_var")
parser_norm_assumption_ttest.add_argument("group_var")

# welch_test
parser_welch_test = subparsers.add_parser("welch_test")
parser_welch_test.add_argument("dependent_var")
parser_welch_test.add_argument("group_var")

args = parser.parse_args()

if args.analysis == "df":
    command = [
        "Rscript",
        "r-scripts/dataframe.R",
        DATA_PATH
    ]

elif args.analysis == "chi_square":
    command = [
        "Rscript",
        "r-scripts/chi_square.R",
        DATA_PATH,
        args.var1,
        args.var2
    ]

elif args.analysis == "logit":
    command = [
        "Rscript",
        "r-scripts/logit_model.R",
        DATA_PATH,
        args.dependent_var
    ] + args.independent_vars

elif args.analysis == "lin_reg":
    command = [
        "Rscript",
        "r-scripts/lin_reg.R",
        DATA_PATH,
        args.target_var
    ] + args.predictor_vars

elif args.analysis == "describe":
    command = [
        "Rscript",
        "r-scripts/describe.R",
        DATA_PATH,
        args.var1
    ]

elif args.analysis == "describeBy":
    command = [
        "Rscript",
        "r-scripts/describeBy.R",
        DATA_PATH,
        args.dependent_var,
        args.group_var
    ]

elif args.analysis == "anova":
    command = [
        "Rscript",
        "r-scripts/anova.R",
        DATA_PATH,
        args.dependent_var
    ] + args.independent_vars

elif args.analysis == "unpaired_ttest":
    command = [
        "Rscript",
        "r-scripts/unpaired_ttest.R",
        DATA_PATH,
        args.var1,
        args.var2_or_constant
    ]

elif args.analysis == "paired_ttest":
    command = [
        "Rscript",
        "r-scripts/paired_ttest.R",
        DATA_PATH,
        args.var1,
        args.var2
    ]

elif args.analysis == "norm_ttest":
    command = [
        "Rscript",
        "r-scripts/norm_assumption_ttest.R",
        DATA_PATH,
        args.dependent_var,
        args.group_var
    ]

elif args.analysis == "welch_test":
    command = [
        "Rscript",
        "r-scripts/welch_test.R",
        DATA_PATH,
        args.dependent_var,
        args.group_var
    ]

else:
    parser.print_help()
    sys.exit(1)

result = subprocess.run(command, capture_output=True, text=True)

if result.returncode != 0:
    print("Error while executing the r-script:")
    print(result.stderr)
else:
    print(result.stdout)
