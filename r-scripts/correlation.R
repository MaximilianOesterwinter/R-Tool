args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
selected_method <- args[2]
var1 <- args[3]
var2 <- args[4]

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

analysis_data <- df[, c(var1, var2)]
analysis_data <- na.omit(analysis_data)

formula_text <- paste0(
  "df <- readRDS('", data_path, "')\n"
)
if (selected_method == "pearson") {
  result <- cor.test(analysis_data[[var1]], analysis_data[[var2]], method = "pearson")
  
  formula_text <- paste0(
    formula_text,
    "cor.test(df$", var1, ", df$", var2,", method = 'pearson')"
  )
  
  result_text <- paste0(
    "Pearson test:\n",
    paste(capture.output(print(result)), collapse = "\n")
  )
  
} else if (selected_method == "kendall") {
  result <- cor.test(analysis_data[[var1]], analysis_data[[var2]], method = "kendall")
  
  formula_text <- paste0(
    formula_text,
    "cor.test(df$", var1,", df$", var2,", method = 'kendall')"
  )
  result_text <- paste0(
    "Kendall test:\n",
    paste(capture.output(print(result)), collapse = "\n")
  )
  
} else if (selected_method == "spearman") {
  result <- cor.test(analysis_data[[var1]], analysis_data[[var2]], method = "spearman")
  
  formula_text <- paste0(
    formula_text,
    "cor.test(df$", var1,", df$", var2,", method = 'spearman')"
  )
  result_text <- paste0(
    "Spearman test:\n",
    paste(capture.output(print(result)), collapse = "\n")
  )
}

report_file <- file.path(output_dir, paste0("correlation_", var1, "_by_", var2, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Correlation",
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