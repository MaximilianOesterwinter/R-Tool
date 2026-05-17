library(psych)

args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
summary_function <- args[2] == "true"
sd_function <- args[3] == "true"
variance_function <- args[4] == "true"
skew_function <- args[5] == "true"
kurtosis_function <- args[6] == "true"
normality_function <- args[7] == "true"
na_rm_function <- args[8] == "true"
group_var <- args[9]
var1 <- args[10]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

source(file.path(script_dir, "prepare_data.R"))
source(file.path(script_dir, "render_report.R"))

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

df <- prepare_data(data_path)
formula_text <- paste0("df <- readRDS(", data_path, ")\n")
result_text <- paste(
  "Results:\n"
)

x <- df[[var1]]

if (na_rm_function) {
  x <- x[!is.na(x)]
}

if (summary_function) {
  summary <- summary(x)
  formula_text <- paste0(
    formula_text,
    "\nsummary(df$", var1, ")\n"
  )
  result_text <- paste(
    result_text,
    "\nSummary:",
    paste(capture.output(print(summary)), collapse = "\n")
  )
}

if (sd_function) {
  standard_deviance <- sd(x)
  formula_text <- paste0(
    formula_text,
    "\nsd(df$", var1, ")\n"
  )
  result_text <- paste(
    result_text,
    "\nStandard deviance:\n",
    paste(capture.output(print(standard_deviance)), collapse = "\n")
  )
}

if (variance_function) {
  variance <- var(x)
  formula_text <- paste0(
    formula_text,
    "\nvar(df$", var1, ")\n"
  )
  result_text <- paste(
    result_text,
    "\nVariance:\n",
    paste(capture.output(print(variance)), collapse = "\n")
  )
}

if (skew_function) {
  skew <- skew(x)
  formula_text <- paste0(
    formula_text,
    "\nskew(df$", var1, ")\n"
  )
  result_text <- paste(
    result_text,
    "\nSkew:\n",
    paste(capture.output(print(skew)), collapse = "\n")
  )
}

if (kurtosis_function) {
  kurtosis <- kurtosi(x)
  formula_text <- paste0(
    formula_text,
    "\nkurtosi(df$", var1, ")\n"
  )
  result_text <- paste(
    result_text,
    "\nCurtosis:\n",
    paste(capture.output(print(kurtosis)), collapse = "\n")
  )
}

if (normality_function) {
  normality <- shapiro.test(x)
  formula_text <- paste0(
    formula_text,
    "\nshapiro.test(df$", var1, ")\n"
  )
  result_text <- paste(
    result_text,
    "\nNormality distribution:\n",
    paste(capture.output(print(normality)), collapse = "\n")
  )
}

if (group_var != "") {
  grouped_description <- describeBy(x, df[[group_var]])
  formula_text <- paste0(
    formula_text,
    "\ndescribeBy(df$", var1, ", df$", group_var, ")\n"
  )
  result_text <- paste(
    result_text,
    "\nGrouped description:\n",
    paste(capture.output(print(grouped_description)), collapse = "\n")
  )
}

report_file <- file.path(output_dir, paste0("describe_", var1, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Descriptive statistics",
  formula_text = formula_text,
  sample_size = as.character(length(x)),
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
