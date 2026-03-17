args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
var1 <- args[2]

# Pfad des aktuell ausgeführten Skripts bestimmen
script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

source(file.path(script_dir, "prepare_data.R"))
source(file.path(script_dir, "render_report.R"))

df <- prepare_data(data_path)

analysis_data <- df[[var1]]
analysis_data <- na.omit(analysis_data)



if (length(args) > 2) {
  stop("Zu viele Argumente. Diese Funktion behandelt nur eine Variable!")
}

summary <- summary(analysis_data)
standard_deviance <- sd(analysis_data)
variance <- var(analysis_data)
#skew <- skew(var1)
#curtosis <- kurtosi(var1)

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

result_text <- paste(
  "Summary:\n",
  paste(capture.output(print(summary)), collapse = "\n"),
  "\n\nStandardabweichung:\n",
  paste(capture.output(print(standard_deviance)), collapse = "\n"),
  "\n\nVarianz:\n",
  paste(capture.output(print(variance)), collapse = "\n")
  #"\n\nSchiefe:\n",
  #paste(capture.output(print(skew)), collapse = "\n"),
  #"\n\nWölbung:\n",
  #paste(capture.output(print(curtosis)), collapse = "\n")
)

report_file <- file.path(output_dir, paste0("describe", var1, ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Deskriptive Statistik",
  formula_text = paste("summary, sd, var(", var1, ")"),
  sample_size = as.character(nrow(analysis_data)),
  result_text = result_text,
  plot_path = ""
)

cat("PDF-Bericht gespeichert unter:\n")
cat(report_file, "\n")

open_pdf <- function(path) {
  sysname <- Sys.info()[["sysname"]]
  
  if (sysname == "Linux") {
    if (nzchar(Sys.which("zathura"))) {
      system2("zathura", path, wait = FALSE)
    } else {
      message("PDF wurde erstellt: ", path)
    }
  } else if (sysname == "Windows") {
    shell.exec(normalizePath(path))
  } else if (sysname == "Darwin") {
    system2("open", path, wait = FALSE)
  } else {
    message("PDF wurde erstellt: ", path)
  }
}

open_pdf(report_file)
