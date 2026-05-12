args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
rename_pairs <- args[2:length(args)]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

if (!requireNamespace("tidyverse", quietly = TRUE)) {
  stop("Package 'tidyverse' not installed.")
}

library(tidyverse)

source(file.path(project_dir, "r-scripts", "prepare_data.R"))

df <- prepare_data(data_path)

for (pair in rename_pairs) {
  parts <- strsplit(pair, "=")[[1]]
  
  old_name <- parts[1]
  new_name <- parts[2]
  
  df <- df %>%
    rename(
      !!new_name := all_of(old_name)
    )
}

saveRDS(df, file = data_path)