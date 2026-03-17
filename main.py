import subprocess
import argparse
import sys
#import pandas as pd
from pathlib import Path

################################################
# Füge hier deinen Dateipfad zum Datensatz ein #
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data"/ "survey_data.csv"
################################################

#df = pd.read_csv(DATA_PATH)
#columns = df.columns.tolist()

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="analysis")

# df
parser_df = subparsers.add_parser("df")

# chi_square
parser_chi = subparsers.add_parser("chi_square")
parser_chi.add_argument("var1")
parser_chi.add_argument("var2")

#for var in [args.var1, args.var2]:
#    if var not in columns:
#        print(f"Fehler: Variable '{var}' nicht im Datensatz gefunden!")
#        sys.exit(1)

# logit
parser_logit = subparsers.add_parser("logit")
parser_logit.add_argument("dependent_var")
parser_logit.add_argument("independent_vars", nargs="+")

# lin_reg
parser_lin_reg = subparsers.add_parser("lin_reg")
parser_lin_reg.add_argument("target_var")
parser_lin_reg.add_argument("predictor_vars", nargs="+")

# desccribe
parser_describe = subparsers.add_parser("describe")
parser_describe.add_argument("var1")

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

else:
    parser.print_help()
    sys.exit(1)

result = subprocess.run(command, capture_output=True, text=True)

#print("STDOUT:")
#print(result.stdout)

#print("STDERR:")
#print(result.stderr)

#print("Return code:", result.returncode)
if result.returncode != 0:
    print("Fehler beim Ausführen des R-Scripts:")
    print(result.stderr)
else:
    print(result.stdout)
