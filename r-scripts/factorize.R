args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
levels_raw <- args[2]
labels_raw <- args[3]
selected_vars <- args[4:length(args)]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

if (!requireNamespace("tidyverse", quietly = TRUE)) {
  stop("Package 'tidyverse' not installed.")
}

library(tidyverse)

source(file.path(project_dir, "r-scripts", "prepare_data.R"))

output_dir <- file.path(project_dir, "data/prepared")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

df <- prepare_data(data_path)

levels_vec <- strsplit(levels_raw, ",")[[1]] |> trimws()
labels_vec <- strsplit(labels_raw, ",")[[1]] |> trimws()

if (length(levels_vec) != length(labels_vec)) {
  stop("Number of levels and labels must be identical.")
}

for (var in selected_vars) {
  df[[var]] <- factor(
    df[[var]],
    levels = levels_vec,
    labels = labels_vec
  )
}

saveRDS(df, file = data_path)
