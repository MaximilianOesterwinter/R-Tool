args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
binwidth <- as.numeric(args[2])
norm_dist <- args[3] == "true"
show_density <- args[4] == "true"
main_lab <- args[5]
x_lab <- args[6]
y_lab <- args[7]
var_x <- args[8]

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

if (show_density) {
  plot <- ggplot(df, aes(x=.data[[var_x]])) +
    geom_histogram(
      aes(y = after_stat(density)),
      binwidth = binwidth,
      fill = "steelblue",
      color = "white"
    )
  if (norm_dist) {
    x <- df[[var_x]]
    mu <- mean(x, na.rm=TRUE)
    sigma <- sd(x, na.rm=TRUE)
    plot <- plot +
      stat_function(
        fun=dnorm,
        args=list(mean=mu, sd=sigma)
      )
  }
} else {
  plot <- ggplot(df, aes(x=.data[[var_x]])) +
    geom_histogram(
      binwidth = binwidth,
      fill = "steelblue",
      color = "white"
    )
}

plot <- plot +
  labs(
    title = main_lab,
    x = x_lab,
    y = y_lab
  ) +
  theme_minimal()



output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

plot_path <- file.path(output_dir, paste0("histogram_", var_x, ".png"))
report_file <- file.path(output_dir, paste0("histogram_", var_x, ".pdf"))

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
    plot_title = paste("Histogram of", var_x),
    dataset_name = dataset_name,
    variable_x = var_x,
    variable_y = "",
    plot_type = "Histogram",
    description_text = paste(
      "This histogram shows the distribution of the variable",
      var_x,
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