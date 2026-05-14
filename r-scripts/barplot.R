args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
flip <- args[2] == "true"
beside <- args[3] == "true"
stat_identity <- args[4] == "true"
main_lab <- args[5]
x_lab <- args[6]
y_lab <- args[7]
group_var <- args[8]
var_x <- args[9]
var_y <- args[10]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

if (!requireNamespace("tidyverse", quietly = TRUE)) {
  stop("Package 'tidyverse' not installed.")
}
if (!requireNamespace("rmarkdown", quietly = TRUE)) {
  stop("Package 'rmarkdown' not installed.")
}

library(tidyverse)
library(rmarkdown)

source(file.path(project_dir, "r-scripts", "prepare_data.R"))

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

df <- prepare_data(data_path)

position_type <- if (beside && group_var != "") "dodge" else "stack"

if (stat_identity) {
  p <- ggplot(df, aes(
    x = .data[[var_x]],
    y = .data[[var_y]]
  ))
  
  if (group_var != "") {
    p <- p + aes(fill = .data[[group_var]])
  }
  
  p <- p + geom_col(
    width = 0.8,
    position = position_type
  )
  
} else {
  p <- ggplot(df, aes(
    x = .data[[var_x]]
  ))
  
  if (group_var != "") {
    p <- p + aes(fill = .data[[group_var]])
  }
  
  p <- p + geom_bar(
    width = 0.8,
    position = position_type
  )
}

if (flip) {
  p <- p + coord_flip()
}

safe_group <- if (group_var == "") "no_group" else group_var

plot_path <- file.path(
  output_dir,
  paste0("barplot_", var_x, "_by_", safe_group, "_", ".png")
)

report_file <- file.path(
  output_dir,
  paste0("barplot_", var_x, "_by_", safe_group, "_", ".pdf")
)

ggsave(
  filename = plot_path,
  plot = p,
  width = 8,
  height = 5
)

dataset_name <- basename(data_path)

description <- if (group_var == "") {
  paste(
    "This barplot shows the frequency distribution of the variable",
    var_x,
    "."
  )
} else {
  paste(
    "This barplot shows the frequency distribution of the variable",
    var_x,
    "grouped by",
    group_var,
    "."
  )
}

rmarkdown::render(
  input = file.path(project_dir, "templates", "plot_report.Rmd"),
  output_file = report_file,
  params = list(
    plot_title = main_lab,
    dataset_name = dataset_name,
    variable_x = var_x,
    variable_y = "",
    plot_type = "Barplot",
    description_text = description,
    plot_path = plot_path
  ),
  envir = new.env(parent = globalenv())
)

cat("Plot report created:\n")
cat(report_file, "\n")

open_pdf <- function(path) {
  sysname <- Sys.info()[["sysname"]]
  
  if (sysname == "Linux") {
    if (nzchar(Sys.which("zathura"))) {
      system2("zathura", path, wait = FALSE)
    } else {
      message("PDF was created: ", path)
    }
  } else if (sysname == "Windows") {
    shell.exec(normalizePath(path))
  } else if (sysname == "Darwin") {
    system2("open", path, wait = FALSE)
  } else {
    message("PDF was created: ", path)
  }
}

open_pdf(report_file)