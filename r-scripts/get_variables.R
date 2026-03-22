args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
out_path <- args[2]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))

source(file.path(script_dir, "prepare_data.R"))

df <- prepare_data(data_path)

# Funktion zur Typbestimmung
get_var_type <- function(x) {
  if (is.factor(x)) {
    return("factor")
  } else if (is.character(x)) {
    return("categorical")
  } else if (is.numeric(x)) {
    return("numerical")
  } else if (inherits(x, "Date")) {
    return("date")
  } else {
    return(class(x)[1])
  }
}

vars <- colnames(df)

# Named list: name -> type
var_info <- setNames(
  lapply(df, get_var_type),
  vars
)

jsonlite::write_json(var_info, out_path, auto_unbox = TRUE)

