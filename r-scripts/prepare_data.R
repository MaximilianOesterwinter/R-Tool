prepare_data <- function(path, sheet = 1) {
  ext <- tolower(tools::file_ext(path))
  
  df <- readRDS(path)
  
  return(df)
}