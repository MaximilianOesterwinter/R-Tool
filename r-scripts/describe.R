library(psych)

args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
var1 <- args[2]

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

analysis_data <- df[[var1]]
analysis_data <- na.omit(analysis_data)

plot_path <- ""

if (length(args) > 2) {
  stop("Too many arguments. This function only uses one variable!")
}

summary <- summary(analysis_data)
standard_deviance <- sd(analysis_data)
variance <- var(analysis_data)
skew <- skew(analysis_data)
curtosis <- kurtosi(analysis_data)
normality <- shapiro.test(analysis_data)

plot_path <- file.path(output_dir, paste0("qqline_", var1, ".png"))
png(plot_path, width = 1000, height = 700)
analysis_data_z <- scale(analysis_data)
qqnorm(analysis_data_z)
qqline(analysis_data_z)
dev.off()

result_text <- paste(
  "Summary:\n",
  paste(capture.output(print(summary)), collapse = "\n"),
  "\n\nStandard deviation:\n",
  paste(capture.output(print(standard_deviance)), collapse = "\n"),
  "\n\nVariance:\n",
  paste(capture.output(print(variance)), collapse = "\n"),
  "\n\nSkew:\n",
  paste(capture.output(print(skew)), collapse = "\n"),
  "\n\nCurtosis:\n",
  paste(capture.output(print(curtosis)), collapse = "\n"),
  "\n\nNormality:\n",
  paste(capture.output(print(normality)), collapse = "\n")
)

report_file <- file.path(output_dir, paste0("describe_", var1, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Descriptive statistics",
formula_text = paste("summary(", var1, "), sd(", var1, "), var(", var1, "), skew(", var1, "), kurtosi(", var1, "), 
                       shapiro.test(", var1, "), analysis_data_z <- scale(df[[", var1,"]]), qqnorm(analysis_data_z), qqline(analysis_data_z)"),
  sample_size = as.character(nrow(analysis_data)),
  result_text = result_text,
  plot_path = plot_path
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
