library(psych)
library(car)

args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
dependent_var <- args[2]
independent_vars <- args[3:length(args)]

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

if (!is.numeric(analysis_data[[dependent_var]])) {
  stop("Die abhängige Variable muss numerisch sein.")
}

for (v in independent_vars) {
  analysis_data[[v]] <- as.factor(analysis_data[[v]])
}

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

plot_path <- ""

if (length(independent_vars) == 1) {
  group_var <- independent_vars[1]
  
  description <- psych::describeBy(analysis_data[[dependent_var]], analysis_data[[group_var]])
  
  model_formula <- as.formula(paste(dependent_var, "~", group_var))
  anova_test <- aov(model_formula, data = analysis_data)
  
  t_test <- pairwise.t.test(
    x = analysis_data[[dependent_var]],
    g = analysis_data[[group_var]],
    p.adjust.method = "bonferroni"
  )
  
  plot_path <- file.path(output_dir, paste0("boxplot_", dependent_var, "_by_", group_var, ".png"))
  png(plot_path, width = 1000, height = 700)
  boxplot(model_formula, data = analysis_data,
          main = paste("Boxplot von", dependent_var, "nach", group_var),
          xlab = group_var, ylab = dependent_var)
  dev.off()
  
  formula_text <- paste(
    "describeBy(", dependent_var, ", ", group_var, ")\n",
    "aov(", dependent_var, " ~ ", group_var, ")\n",
    "pairwise.t.test(", dependent_var, ", ", group_var, ", p.adjust.method='bonferroni')",
    sep = ""
  )
  
  result_text <- paste(
    "Deskriptive Statistik:\n",
    paste(capture.output(print(description)), collapse = "\n"),
    "\n\nANOVA:\n",
    paste(capture.output(print(summary(anova_test))), collapse = "\n"),
    "\n\nPost-hoc-Tests:\n",
    paste(capture.output(print(t_test)), collapse = "\n"),
    sep = ""
  )
}

if (length(independent_vars) == 2) {
  rhs_main <- paste(independent_vars, collapse = " + ")
  rhs_interaction <- paste(independent_vars, collapse = " * ")
  
  description <- psych::describeBy(
    analysis_data[[dependent_var]],
    interaction(analysis_data[[independent_vars[1]]], analysis_data[[independent_vars[2]]])
  )
  
  levene_formula <- as.formula(paste(dependent_var, "~", rhs_interaction))
  levene <- car::leveneTest(levene_formula, data = analysis_data)
  
  model_formula <- as.formula(paste(dependent_var, "~", rhs_interaction))
  anova_test <- aov(model_formula, data = analysis_data)
  
  plot_path <- file.path(output_dir, paste0("qqplot_", dependent_var, ".png"))
  png(plot_path, width = 1000, height = 700)
  plot(anova_test, which = 2)
  dev.off()
  
  formula_text <- paste(
    "describeBy(", dependent_var, ", interaction(", paste(independent_vars, collapse = ", "), "))\n",
    "leveneTest(", dependent_var, " ~ ", rhs_interaction, ")\n",
    "aov(", dependent_var, " ~ ", rhs_interaction, ")\n",
    "plot(anova_test, which = 2)",
    sep = ""
  )
  
  result_text <- paste(
    "Deskriptive Statistik:\n",
    paste(capture.output(print(description)), collapse = "\n"),
    "\n\nLevene-Test:\n",
    paste(capture.output(print(levene)), collapse = "\n"),
    "\n\nANOVA:\n",
    paste(capture.output(print(summary(anova_test))), collapse = "\n"),
    sep = ""
  )
}

report_file <- file.path(output_dir, paste0("anova_", dependent_var, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "ANOVA",
  formula_text = formula_text,
  sample_size = as.character(nrow(analysis_data)),
  result_text = result_text,
  plot_path = plot_path
)

cat("PDF-Bericht gespeichert unter:\n")
cat(report_file, "\n")

open_pdf <- function(path) {
  sysname <- Sys.info()[["sysname"]]
  
  if (sysname == "Linux") {
    if (nzchar(Sys.which("zathura"))) {
      system2("zathura", path, wait = FALSE)
    } else {
      message("PDF wurde erstellt: ", path)
    }
  } else if (sysname == "Windows") {
    shell.exec(normalizePath(path))
  } else if (sysname == "Darwin") {
    system2("open", path, wait = FALSE)
  } else {
    message("PDF wurde erstellt: ", path)
  }
}

open_pdf(report_file)