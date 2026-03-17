args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
dependent_var <- args[2]
independent_vars <- args[3:length(args)]

if (length(args) < 3) {
  stop("Zu wenige Argumente. Erwartet: data_path, dependent_var, mindestens eine independent_var")
}

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

source(file.path(script_dir, "prepare_data.R"))
source(file.path(script_dir, "render_report.R"))

df <- prepare_data(data_path)

all_vars <- c(dependent_var, independent_vars)

missing_vars <- setdiff(all_vars, names(df))
if (length(missing_vars) > 0) {
  stop(paste("Folgende Variablen fehlen im Datensatz:", paste(missing_vars, collapse = ", ")))
}

analysis_data <- df[, all_vars]
analysis_data <- na.omit(analysis_data)

if (nrow(analysis_data) == 0) {
  stop("Keine vollständigen Fälle nach dem Entfernen fehlender Werte.")
}

# Prüfen, ob die AV binär ist
unique_values <- sort(unique(analysis_data[[dependent_var]]))
if (!(length(unique_values) == 2 && all(unique_values %in% c(0, 1)))) {
  stop(paste(
    "Die abhängige Variable muss binär als 0/1 kodiert sein. Gefunden wurden:",
    paste(unique_values, collapse = ", ")
  ))
}

formula_text <- paste(dependent_var, "~", paste(independent_vars, collapse = " + "))
model_formula <- as.formula(formula_text)

model <- glm(
  formula = model_formula,
  data = analysis_data,
  family = binomial(link = "logit")
)

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

result_text <- paste(
  "Modellzusammenfassung:\n",
  paste(capture.output(print(model_formula)), collapse = "\n"),
  "\n\nOdds Ratios:\n",
  paste(capture.output(print(model)), collapse = "\n")
)

report_file <- file.path(output_dir, paste0("logit_model_", dependent_var, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Logistische Regression",
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
