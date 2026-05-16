args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
main_lab <- args[2]
x_lab <- args[3]
y_lab <- args[4]
flip <- args[5] == "true"
show_outliers <- args[6] == "true"
show_points <- args[7] == "true"
show_mean <- args[8] == "true"
show_notches <- args[9] == "true"
show_n <- args[10] == "true"
color_by_group <- args[11] == "true"
sort_groups <- args[12] == "true"
group_var <- args[13]
facet_var <- args[14]
weight_var <- args[15]
var_y <- args[16]


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
if (!requireNamespace("scales", quietly = TRUE)) {
  stop("Package 'scales' not installed.")
}

library(tidyverse)
library(rmarkdown)
library(scales)

source(file.path("r-scripts", "prepare_data.R"))

df <- prepare_data(data_path)

if (group_var != "" && sort_groups) {
  df[[group_var]] <- reorder(df[[group_var]], df[[var_y]], median, na.rm = TRUE)
}

aes_base <- aes(
  x = if (group_var != "") .data[[group_var]] else factor("All"),
  y = .data[[var_y]]
)

p <- ggplot(df, aes_base)

if (weight_var != "") {
  p <- p + aes(weight = .data[[weight_var]])
}

if (color_by_group && group_var != "") {
  p <- p + aes(fill = .data[[group_var]])
}

p <- p +
  geom_boxplot(
    notch = show_notches,
    outlier.shape = if (show_outliers) 19 else NA
  )

if (show_points) {
  p <- p +
    geom_jitter(
      width = 0.15,
      alpha = 0.4,
      size = 1.8
    )
}

if (show_mean) {
  p <- p +
    stat_summary(
      fun = mean,
      geom = "point",
      shape = 23,
      size = 3,
      fill = "white",
      na.rm = TRUE
    )
}

if (show_n && group_var != "") {
  n_df <- df |>
    group_by(.data[[group_var]]) |>
    summarise(n = n(), .groups = "drop")
#filter(!is.na(.data[[var_y]]))
  p <- p +
    geom_text(
      data = n_df,
      aes(
        x = .data[[group_var]],
        y = -Inf,
        label = paste0("n = ", n)
      ),
      inherit.aes = FALSE,
      vjust = -0.5
    )
}

if (facet_var != "") {
  p <- p + facet_wrap(vars(.data[[facet_var]]))
}

if (flip) {
  p <- p + coord_flip()
}

if (is.numeric(df[[var_y]])) {
  p <- p +
    scale_y_continuous(labels = label_number(big.mark = ".", decimal.mark = ","))
}

p <- p +
  labs(
    title = main_lab,
    x = if (x_lab != "") x_lab else if (group_var != "") group_var else "",
    y = if (y_lab != "") y_lab else var_y,
    fill = group_var
  ) +
  theme_minimal()

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

plot_path <- file.path(output_dir, paste0("boxplot_", var_y, ".png"))
report_file <- file.path(output_dir, paste0("boxplot_", var_y, ".pdf"))

ggsave(
  filename = plot_path,
  plot = p,
  width = 8,
  height = 5
)

dataset_name <- basename(data_path)

rmarkdown::render(
  input = file.path(project_dir, "templates", "plot_report.Rmd"),
  output_file = report_file,
  params = list(
    plot_title = paste("Boxplot of", var_y),
    dataset_name = dataset_name,
    variable_x = "",
    variable_y = var_y,
    plot_type = "Boxplot",
    description_text = paste(
      "This boxplot shows the variable",
      var_y,
      "in the selected dataset."
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