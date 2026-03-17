prepare_data <- function(path) {
  
  if (!requireNamespace("readr", quietly = TRUE)) {
    stop("Paket 'readr' ist nicht installiert.")
  }
  
  if (!requireNamespace("dplyr", quietly = TRUE)) {
    stop("Paket 'dplyr' ist nicht installiert.")
  }
  
  # Pakete laden:
  
  library(readr)
  library(dplyr)
  
  # Datensatz einlesen:
  
  df <- readr::read_csv(path, na = c("", "NA"), show_col_types = FALSE)
  df_clean <- df %>%
    
  #####################################
  # Oberhalb bitte nicht bearbeiten!!!#
  #####################################
  
  # Hier die gewünschte Aufbereitung vornehmen und die einzelnen Blöcke 
  # mit der Pipe %>% verbinden. 
  
  # Als Beispiel werden hier die kategorialen Variablen faktorisiert
    
    mutate(
      gender = factor(gender),
      education = factor(education, levels = c("Abitur", "Bachelor", "Master", "Promotion")),
      vote_intent = as.numeric(vote_intent)
    )
  
  ######################################
  # Unterhalb bitte nicht bearbeiten!!!#
  ######################################
  
  return(df_clean)
}

