args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
jitter <- args[2] == "true"
main_lab <- args[3]
x_lab <- args[4]
y_lab <- args[5]
group_var <- args[6]
var_x <- args[7]
var_y <- args[8]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

if (!requireNamespace("ggplot2", quietly = TRUE)) {
  stop("Package 'ggplot2' not installed.")
}
if (!requireNamespace("rmarkdown", quietly = TRUE)) {
  stop("Package 'rmarkdown' not installed.")
}

library(tidyverse)
library(rmarkdown)
library(scales)

source(file.path("r-scripts", "prepare_data.R"))

df <- prepare_data(data_path)

if (group_var != "") {
  plot <- ggplot(
    df,
    aes(
      x=.data[[var_x]],
      y=.data[[var_y]],
      color=.data[[group_var]]
    )
  ) +
    labs(
      x=x_lab,
      y=y_lab,
      title=main_lab,
      color=group_var
    )
} else {
  plot <- ggplot(
    df,
    aes(
      x=.data[[var_x]],
      y=.data[[var_y]], 
    )
  ) +
    labs(
      x=x_lab,
      y=y_lab,
      title=main_lab
    )
}

if (jitter) {
  plot <- plot +
    geom_jitter()
} else {
  plot <- plot +
    geom_point()
}

if (is.numeric(df[[var_x]])) {
  plot <- plot +
    scale_x_continuous(labels = label_number(big.mark = ".", decimal.mark = ","))
}

if (is.numeric(df[[var_y]])) {
  plot <- plot +
    scale_y_continuous(labels = label_number(big.mark = ".", decimal.mark = ","))
}

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

plot_path <- file.path(output_dir, paste0("scatterplot_", var_x, "_by_", var_y, ".png"))
report_file <- file.path(output_dir, paste0("scatterplot_", var_x, "_by_", var_y, ".pdf"))

ggsave(
  filename = plot_path,
  plot = plot,
  width = 8,
  height = 5
)

dataset_name <- basename(data_path)

rmarkdown::render(
  input = file.path(project_dir, "templates", "plot_report.Rmd"),
  output_file = report_file,
  params = list(
    plot_title = paste("Scatterplot of", var_x, "_by_", var_y),
    dataset_name = dataset_name,
    variable_x = var_x,
    variable_y = var_y,
    plot_type = "Scatterplot",
    description_text = paste(
      "This scatterplot shows the variable",
      var_x,
      "by",
      var_y,
      "."
    ),
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