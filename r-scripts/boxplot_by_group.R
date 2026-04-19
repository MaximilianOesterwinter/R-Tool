args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
var1 <- args[2]
var2 <- args[3]

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

library(ggplot2)
library(rmarkdown)

source(file.path("r-scripts", "prepare_data.R"))

df <- prepare_data(data_path)

plot <- ggplot(df, aes(y = .data[[var1]], x = .data[[var2]])) +
  geom_boxplot(fill = c("lightgreen", "steelblue"))

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

plot_path <- file.path(output_dir, paste0("boxplot_", var1, "_by_", var2, ".png"))
report_file <- file.path(output_dir, paste0("boxplot_", var1, "_by_", var2, ".pdf"))

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
    plot_title = paste("Boxplot of", var1, "_by_", var2),
    dataset_name = dataset_name,
    variable_x = var2,
    variable_y = var1,
    plot_type = "Boxplot by group",
    description_text = paste(
      "This boxplot shows the variable",
      var1,
      "grouped by",
      var2,
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