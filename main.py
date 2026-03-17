import subprocess
import argparse
import sys
#import pandas as pd

################################################
# Füge hier deinen Dateipfad zum Datensatz ein #
DATA_PATH = "data/survey_data.csv"
################################################

#df = pd.read_csv(DATA_PATH)
#columns = df.columns.tolist()

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="analysis")

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
parser_logit = subparsers.add_parser("lin_reg")
parser_logit.add_argument("target_var")
parser_logit.add_argument("predictor_vars", nargs="+")


args = parser.parse_args()

if args.analysis == "chi_square":
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