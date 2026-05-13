args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
output_name <- args[2]
summary_function <- args[3]
na_rm <- args[4] == "true"
group_vars_raw <- args[5]

target_vars <- args[6:length(args)]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

if (!requireNamespace("tidyverse", quietly = TRUE)) {
  stop("Package 'tidyverse' not installed.")
}

library(tidyverse)

source(file.path("r-scripts", "prepare_data.R"))

df <- prepare_data(data_path)

group_vars <- if (group_vars_raw == "" || group_vars_raw == "none") {
  character(0)
} else {
  strsplit(group_vars_raw, ",")[[1]]
}

if (length(target_vars) == 1 && is.na(target_vars)) {
  target_vars <- character(0)
}

missing_targets <- setdiff(target_vars, names(df))
if (length(missing_targets) > 0) {
  stop(paste("Unknown target variable(s):", paste(missing_targets, collapse = ", ")))
}

missing_groups <- setdiff(group_vars, names(df))
if (length(missing_groups) > 0) {
  stop(paste("Unknown grouping variable(s):", paste(missing_groups, collapse = ", ")))
}

allowed_functions <- c(
  "mean", "median", "sd", "min", "max", "sum", "n", "n_distinct"
)

if (!summary_function %in% allowed_functions) {
  stop(paste("Unknown summary function:", summary_function))
}

if (length(group_vars) > 0) {
  df <- df %>%
    group_by(across(all_of(group_vars)))
}

if (summary_function == "n") {
  df_summary <- df %>%
    summarise(n = n(), .groups = "drop")
  
} else if (summary_function == "n_distinct") {
  df_summary <- df %>%
    summarise(
      across(
        all_of(target_vars),
        n_distinct,
        .names = "{.col}_n_distinct"
      ),
      .groups = "drop"
    )
  
} else {
  non_numeric <- target_vars[!sapply(df[target_vars], is.numeric)]
  
  if (length(non_numeric) > 0) {
    stop(paste(
      "These variables must be numeric for this summary function:",
      paste(non_numeric, collapse = ", ")
    ))
  }
  
  fn <- match.fun(summary_function)
  
  df_summary <- df %>%
    summarise(
      across(
        all_of(target_vars),
        ~ fn(.x, na.rm = na_rm),
        .names = paste0("{.col}_", summary_function)
      ),
      .groups = "drop"
    )
}

output_path <- file.path(
  project_dir,
  "data",
  "prepared",
  paste0(output_name, ".rds")
)

saveRDS(df_summary, output_path)