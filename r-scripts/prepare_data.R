prepare_data <- function(path) {
  if (!requireNamespace("readr", quietly = TRUE)) {
    stop("Package 'readr' not installed.")
  }
  
  df <- readr::read_csv(
    path,
    na = c("", "NA"),
    show_col_types = FALSE
  )
  
  return(df)
}