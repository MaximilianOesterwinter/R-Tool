args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
flip <- args[2] == "true"
beside <- args[3] == "true"
main_lab <- args[4]
x_lab <- args[5]
y_lab <- args[6]
group_var <- args[7]
var_y <- args[8]
var_x <- args[9]

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

library(rmarkdown)
library(tidyverse)

source(file.path("r-scripts", "prepare_data.R"))

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

df <- prepare_data(data_path)

if (var_x == "" || var_y == "") {
  stop("Column chart requires both an x variable and a y variable.")
}

position_type <- if (beside) "dodge" else "stack"

if (group_var == "") {
  plot <- ggplot(df, aes(x = .data[[var_x]], y = .data[[var_y]])) +
    geom_col()
} else {
  plot <- ggplot(
    df,
    aes(
      x = .data[[var_x]],
      y = .data[[var_y]],
      fill = .data[[group_var]]
    )
  ) +
    geom_col(position = position_type)
}

plot <- plot +
  labs(
    title = main_lab,
    x = x_lab,
    y = y_lab,
    fill = group_var
  ) +
  theme_minimal()

if (flip) {
  plot <- plot + coord_flip()
}

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

plot_path <- file.path(output_dir, paste0("columnchart_", var_x, "_", var_y, ".png"))
report_file <- file.path(output_dir, paste0("columnchart_", var_x, "_", var_y, ".pdf"))

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
    plot_title = main_lab,
    dataset_name = dataset_name,
    variable_x = var_x,
    variable_y = var_y,
    plot_type = "Column chart",
    description_text = paste(
      "This column chart shows",
      var_y,
      "by",
      var_x,
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