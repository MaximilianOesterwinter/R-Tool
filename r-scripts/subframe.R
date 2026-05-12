args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
subframe_name <- args[2]
use_pivot_longer <- args[3] == "true"
selected_vars <- args[4:length(args)]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

if (!requireNamespace("tidyverse", quietly = TRUE)) {
  stop("Package 'tidyverse' not installed.")
}

library(tidyverse)

source(file.path("r-scripts", "prepare_data.R"))

output_dir <- file.path(project_dir, "data/prepared/")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

df <- prepare_data(data_path)

df_subframe <- df %>%
  select(all_of(selected_vars))

if (use_pivot_longer){
  df_subframe <- df_subframe %>%
    pivot_longer(
      cols = everything(),
      names_to = "variable",
      values_to = "value"
    )
}

output_path <- file.path(
  output_dir,
  paste0(subframe_name, ".rds")
)
saveRDS(df_subframe, file = output_path)

