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

library(rmarkdown)

source(file.path("r-scripts", "prepare_data.R"))

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

df <- prepare_data(data_path)

analysis_data <- na.omit(df[, c(var1, var2)])

plot_path <- file.path(output_dir, paste0("barplot_", var1, "_by_", var2, ".png"))
report_file <- file.path(output_dir, paste0("barplot_", var1, "_by_", var2, ".pdf"))
png(plot_path, width = 1000, height = 700)
plot(analysis_data[[var1]], analysis_data[[var2]], type="b",
     xlab=var1, ylab=var2, main=paste(var2, "per", var1),
     col="darkblue", col.axis="darkblue",
     col.main="darkblue", col.lab="darkblue")
dev.off()

dataset_name <- basename(data_path)

rmarkdown::render(
  input = file.path(project_dir, "templates", "plot_report.Rmd"),
  output_file = report_file,
  params = list(
    plot_title = paste("Lineplot of", var2, "in range of", var1),
    dataset_name = dataset_name,
    variable_x = var1,
    variable_y = var2,
    plot_type = "Lineplot",
    description_text = paste(
      "This Lineplot shows the development of the variable",
      var2,
      "in range of",
      var1
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