args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
new_var_name <- args[2]
operation <- args[3]
operator <- args[4]
na_rm <- args[5] == "true"
reverse_min <- args[6]
reverse_max <- args[7]
if (operation == "recode"){
  recode_else <- args[8]
  selected_vars <- args[9]
  recode_rules <- args[10:length(args)]
} else {
  selected_vars <- args[8:length(args)]
}

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
} else if (operation == "recode") {
  if (length(selected_vars) != 1) {
    stop("Recode requires exactly one source variable.")
  }
  
  source_var <- selected_vars[1]
  
  result <- rep(NA_character_, nrow(df))
  
  for (rule in recode_rules) {
    parts <- strsplit(rule, "\\|")[[1]]
    
    operator <- parts[1]
    compare_value_raw <- parts[2]
    result_value <- parts[3]
    
    source_values <- df[[source_var]]
    
    compare_value <- suppressWarnings(as.numeric(compare_value_raw))
    
    if (!is.na(compare_value) && is.numeric(source_values)) {
      compare_to <- compare_value
    } else {
      compare_to <- compare_value_raw
    }
    
    if (operator == "==") {
      condition <- source_values == compare_to
    } else if (operator == "!=") {
      condition <- source_values != compare_to
    } else if (operator == ">") {
      condition <- source_values > compare_to
    } else if (operator == ">=") {
      condition <- source_values >= compare_to
    } else if (operator == "<") {
      condition <- source_values < compare_to
    } else if (operator == "<=") {
      condition <- source_values <= compare_to
    } else {
      stop("Unknown recode operator.")
    }
    
    result[condition & is.na(result)] <- result_value
  }
  
  if (recode_else != "") {
    result[is.na(result)] <- recode_else
  }
  
  df[[new_var_name]] <- result
} else {
  stop("Unknown mutate operation.")
}

saveRDS(df, file = data_path)