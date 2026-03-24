prepare_data <- function(path) {
  
  if (!requireNamespace("readr", quietly = TRUE)) {
    stop("Package 'readr' not installed.")
  }
  
  if (!requireNamespace("dplyr", quietly = TRUE)) {
    stop("Package 'dplyr' not installed.")
  }
  
  library(readr)
  library(dplyr)
  
  df <- readr::read_csv(path, na = c("", "NA"), show_col_types = FALSE)
  df_clean <- df %>%
    
  ################################
  # Don't edit above this line!!!#
  ################################
  
  # Paste your desired data transformations here and
  # chain them with the pipe operator %>% 
  
  # As part of the included example-dataset the categorial variables are factorised.
  # You can savely delete the mutate() operator
    
    mutate(
      gender = factor(gender, levels = c("male", "female")),
      education = factor(education, levels = c("highscool", "Bachelor", "Master", "phd")),
      region = factor(region, levels = c("north", "east", "south", "west")),
      smoker_status = factor(smoker_status, levels = c("non_smoker", "former", "smoker")),
      has_children = factor(has_children),
      is_employed = factor(is_employed),
      owns_home = factor(owns_home)
      
    )
  
  ################################
  # Don't edit below this line!!!#
  ################################
  
  return(df_clean)
}

export_variable_names <- function(path, out_path = "variables.json") {
  df <- prepare_data(path)
  vars <- colnames(df)
  jsonlite::write_json(vars, out_path)
}

