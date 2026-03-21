args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
var1 <- args[2]
var2 <- args[3]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

source(file.path(script_dir, "prepare_data.R"))
source(file.path(script_dir, "render_report.R"))

df <- prepare_data(data_path)

analysis_data <- df[, c(var1, var2)]
analysis_data <- na.omit(analysis_data)

analysis_data[[var1]] <- as.factor(analysis_data[[var1]])
analysis_data[[var2]] <- as.factor(analysis_data[[var2]])

tab <- table(analysis_data[[var1]], analysis_data[[var2]])

test_result <- chisq.test(tab)

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

result_text <- paste(
  "Cross-table:\n",
  paste(capture.output(print(tab)), collapse = "\n"),
  "\n\nChi-square Test:\n",
  paste(capture.output(print(test_result)), collapse = "\n")
)

report_file <- file.path(output_dir, paste0("chi_quadrat_", var1, "_by_", var2, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Chi-square",
  formula_text = paste(var1, "~", var2),
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