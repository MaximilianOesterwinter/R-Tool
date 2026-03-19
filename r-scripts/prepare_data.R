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
      gender = factor(gender),
      education = factor(education, levels = c("Abitur", "Bachelor", "Master", "Promotion")),
      vote_intent = as.numeric(vote_intent)
    )
  
  ################################
  # Don't edit below this line!!!#
  ################################
  
  return(df_clean)
}

