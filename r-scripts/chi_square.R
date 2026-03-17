args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
var1 <- args[2]
var2 <- args[3]

# Pfad des aktuell ausgeführten Skripts bestimmen
script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

source(file.path(script_dir, "prepare_data.R"))
source(file.path(script_dir, "render_report.R"))

df <- prepare_data(data_path)

# Nur die benötigten Variablen auswählen
analysis_data <- df[, c(var1, var2)]
analysis_data <- na.omit(analysis_data)

# Sicherheitshalber als Faktoren behandeln
analysis_data[[var1]] <- as.factor(analysis_data[[var1]])
analysis_data[[var2]] <- as.factor(analysis_data[[var2]])

tab <- table(analysis_data[[var1]], analysis_data[[var2]])
#print(tab)

test_result <- chisq.test(tab)
#print(test_result)

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

result_text <- paste(
  "Kreuztabelle:\n",
  paste(capture.output(print(tab)), collapse = "\n"),
  "\n\nChi-Quadrat-Test:\n",
  paste(capture.output(print(test_result)), collapse = "\n")
)

report_file <- file.path(output_dir, paste0("chi_quadrat_", var1, "_by_", var2, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Chi-Quadrat",
  formula_text = paste(var1, "~", var2),
  sample_size = as.character(nrow(analysis_data)),
  result_text = result_text,
  plot_path = ""
)

cat("PDF-Bericht gespeichert unter:\n")
cat(report_file, "\n")

if (nzchar(Sys.which("zathura"))) {
  system2("zathura", report_file, wait = FALSE)
  cat("PDF wird mit Zathura geöffnet.\n")
}