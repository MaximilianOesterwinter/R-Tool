library(psych)
library(car)
library(DescTools)

args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
post_hoc <- args[2] == "true"
effect_size <- args[3] == "true"
levene_test <- args[4] == "true"
dependent_var <- args[5]
independent_vars <- args[6:length(args)]

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
  stop(paste("Following variables are missing in the dataset:", paste(missing_vars, collapse = ", ")))
}

analysis_data <- df[, all_vars]
analysis_data <- na.omit(analysis_data)

if (nrow(analysis_data) == 0) {
  stop("No cases left after excluding NAs.")
}

if (!is.numeric(analysis_data[[dependent_var]])) {
  stop("The dependent variable has to be numeric.")
}

for (v in independent_vars) {
  analysis_data[[v]] <- as.factor(analysis_data[[v]])
}

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

formula_text <- ""
result_text <- ""

if (length(independent_vars) == 1) {
  group_var <- independent_vars[1]

  model_formula <- as.formula(paste(dependent_var, "~", group_var))
  anova_test <- aov(model_formula, data = analysis_data)
  
  formula_text <- paste0(
    "df <- readRDS('", data_path, "')\n",
    "\nanova_test <- aov(", deparse(model_formula), ", data = df)\n"
  )
  
  result_text <- paste0(
    "\n\nANOVA:\n",
    paste(capture.output(print(summary(anova_test))), collapse = "\n")
  )
  
  if (effect_size) {
    eta <- EtaSq(anova_test)
    eta_sq <- eta[1, "eta.sq"]
    f <- sqrt(eta_sq / (1 - eta_sq))
    
    formula_text <- paste0(
      formula_text,
      "\neta <- EtaSq(anova_test)\n",
      "\neta_sq <- eta[1, 'eta.sq']\n",
      "\nsqrt(eta_sq / (1 - eta_sq))\n"
    )
    
    result_text <- paste(
      result_text,
      "\n\nEffect size Cohen's f:\n",
      paste(capture.output(print(f)), collapse = "\n")
    )
  }
  
  if (post_hoc) {
    t_test <- pairwise.t.test(
      x = analysis_data[[dependent_var]],
      g = analysis_data[[group_var]],
      p.adjust.method = "bonferroni"
    )
    
    t_output <- capture.output(print(t_test))
    t_output <- t_output[!grepl("^data:", trimws(t_output))]
    
    formula_text <- paste0(
      formula_text,
      "\npairwise.t.test(x=df$", dependent_var, ", g=df$", group_var, ", p.adjust.method='bonferroni')\n"
    )
    
    result_text <- paste(
      result_text,
      "\n\nPost-hoc tests:\n",
      paste(t_output, collapse = "\n")
    )
  }
} else if (length(independent_vars) == 2) {
  rhs_main <- paste(independent_vars, collapse = " + ")
  rhs_interaction <- paste(independent_vars, collapse = " * ")

  model_formula <- as.formula(paste(dependent_var, "~", rhs_interaction))
  anova_test <- aov(model_formula, data = analysis_data)
  
  formula_text <- paste0(
    "df <- readRDS('", data_path, "')\n",
    "\naov(", deparse(model_formula), ", data = df)\n"
  )
  result_text <- paste(
    "Results:\n",
    "\n\nANOVA:\n",
    paste(capture.output(print(summary(anova_test))), collapse = "\n")
  )
  
  if (levene_test) {
    levene_formula <- as.formula(paste(dependent_var, "~", rhs_interaction))
    levene <- car::leveneTest(levene_formula, data = analysis_data)
    
    formula_text <- paste0(
      formula_text,
      "\nleveneTest(", deparse(levene_formula), ", data = df)\n"
    )
    result_text <- paste(
      result_text,
      "\n\nLevene test:\n",
      paste(capture.output(print(levene)), collapse = "\n")
    )
  }


}

report_file <- file.path(output_dir, paste0("anova_", dependent_var, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "ANOVA",
  formula_text = formula_text,
  sample_size = as.character(nrow(analysis_data)),
  result_text = result_text,
  plot_path = ""
)

cat("PDF saved in:\n")
cat(report_file, "\n")

open_pdf <- function(path) {
  sysname <- Sys.info()[["sysname"]]
  
  if (sysname == "Linux") {
    if (nzchar(Sys.which("zathura"))) {
      system2("zathura", path, wait = FALSE)
    } else {
      message("PDF was created: ", path)
    }
  } else if (sysname == "Windows") {
    shell.exec(normalizePath(path))
  } else if (sysname == "Darwin") {
    system2("open", path, wait = FALSE)
  } else {
    message("PDF was created: ", path)
  }
}

open_pdf(report_file)