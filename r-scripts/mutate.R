args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
new_var_name <- args[2]
operation <- args[3]
operator <- args[4]
na_rm <- args[5] == "true"
reverse_min <- args[6]
reverse_max <- args[7]
selected_vars <- args[8:length(args)]

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

if (operation == "arithmetic") {
  if (length(selected_vars) != 2) {
    stop("Arithmetic requires exactly two variables.")
  }
  
  var1 <- selected_vars[1]
  var2 <- selected_vars[2]
  
  if (operator == "+") {
    df[[new_var_name]] <- df[[var1]] + df[[var2]]
  } else if (operator == "-") {
    df[[new_var_name]] <- df[[var1]] - df[[var2]]
  } else if (operator == "*") {
    df[[new_var_name]] <- df[[var1]] * df[[var2]]
  } else if (operator == "/") {
    df[[new_var_name]] <- df[[var1]] / df[[var2]]
  } else if (operator == "^") {
    df[[new_var_name]] <- df[[var1]] ^ df[[var2]]
  } else {
    stop("Unknown arithmetic operator.")
  }
} else if (operation == "row_mean") {
  df[[new_var_name]] <- rowMeans(
    df[selected_vars],
    na.rm = na_rm
  )
} else if (operation == "row_sum") {
  df[[new_var_name]] <- rowSums(
    df[selected_vars],
    na.rm = na_rm
  )
} else if (operation == "log") {
  if (length(selected_vars) != 1) {
    stop("Log transformation requires exactly one variable.")
  }
  
  df[[new_var_name]] <- log(df[[selected_vars[1]]])
} else if (operation == "z_standardize") {
  if (length(selected_vars) != 1) {
    stop("Z-standardization requires exactly one variable.")
  }
  
  df[[new_var_name]] <- as.numeric(scale(df[[selected_vars[1]]]))
} else if (operation == "reverse_scale") {
  if (length(selected_vars) != 1) {
    stop("Reverse scale requires exactly one variable.")
  }
  
  min_value <- as.numeric(reverse_min)
  max_value <- as.numeric(reverse_max)
  
  df[[new_var_name]] <- max_value + min_value - df[[selected_vars[1]]]
} else {
  stop("Unknown mutate operation.")
}

saveRDS(df, file = data_path)