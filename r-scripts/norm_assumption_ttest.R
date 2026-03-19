args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
dependent_var <- args[2]
group_var <- args[3]

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

analysis_data <- na.omit(df[, c(dependent_var, group_var)])

if (length(unique(analysis_data[[group_var]])) != 2) {
  stop("The grouping variable must have exactly 2 levels.")
}

groups <- split(analysis_data[[dependent_var]], analysis_data[[group_var]])
normality_results <- lapply(groups, shapiro.test)

result_text <- paste(
  sapply(names(normality_results), function(g) {
    res <- normality_results[[g]]
    paste0(
      "Group ", g,
      ": W = ", round(res$statistic, 3),
      ", p = ", round(res$p.value, 3)
    )
  }),
  collapse = "\n"
)

formula_text <- paste0(
  "analysis_data <- na.omit(df[, c(", dependent_var, ", ", group_var, ")])\n",
  "groups <- split(analysis_data[[", dependent_var, "]], analysis_data[[", group_var, "]])\n",
  "normality_results <- lapply(groups, shapiro.test)"
)

report_file <- file.path(output_dir, paste0("Norm_assumption_ttest_", dependent_var, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Normality assumption for the independent-samples t-test",
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