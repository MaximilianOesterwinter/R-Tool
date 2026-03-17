args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
target_var <- args[2]
predictor_vars <- args[3:length(args)]

if (length(args) < 3) {
  stop("Zu wenige Argumente. Erwartet: data_path, target_var, mindestens eine predictor_var")
}

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

source(file.path(script_dir, "prepare_data.R"))
source(file.path(script_dir, "render_report.R"))

df <- prepare_data(data_path)

all_vars <- c(target_var, predictor_vars)

missing_vars <- setdiff(all_vars, names(df))
if (length(missing_vars) > 0) {
  stop(paste("Folgende Variablen fehlen im Datensatz:", paste(missing_vars, collapse = ", ")))
}

analysis_data <- df[, all_vars]
analysis_data <- na.omit(analysis_data)

if (nrow(analysis_data) == 0) {
  stop("Keine vollständigen Fälle nach dem Entfernen fehlender Werte.")
}

# Prüfen, ob die Variablen metrisch sind
if (!all(sapply(df[all_vars], is.numeric))) {
  stop("Variablen müssen metrisch sein.")
}

# lineare Regression durchführen

formula_text <- paste(target_var, "~", paste(predictor_vars, collapse = " + "))
result <- lm(formula_text, data = df)

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

result_text <- paste(
  "Modellzusammenfassung:\n",
  paste(capture.output(print(formula_text)), collapse = "\n"),
  "\n\nOdds Ratios:\n",
  paste(capture.output(print(result)), collapse = "\n")
)

report_file <- file.path(output_dir, paste0("lin_reg_", target_var, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Lineare Regression",
  formula_text = paste(formula_text),
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

cat("\nVerwendete Formel:\n")
cat(formula_text, "\n")

cat("\nAnzahl vollständiger Fälle:\n")
cat(nrow(analysis_data), "\n")

cat("\nModellzusammenfassung:\n")
print(summary(result))

cat("\nOdds Ratios:\n")
print(exp(coef(result)))
