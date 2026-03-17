args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]

# Pfad des aktuell ausgeführten Skripts bestimmen
script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

source(file.path(script_dir, "prepare_data.R"))
source(file.path(script_dir, "render_report.R"))

df <- prepare_data(data_path)
df_size <- nrow(df)

head <- head(df)
str <- str(df)
summary <- summary(df)

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

result_text <- paste(
  "Summary:\n",
  paste(capture.output(print(summary)), collapse = "\n"),
  "\n\nHead:\n",
  paste(capture.output(print(head)), collapse = "\n"),
  "\n\nStr:\n",
  paste(capture.output(print(str)), collapse = "\n")
)


report_file <- file.path(output_dir, paste0("dataframe", ".pdf"))

render_report(
  template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
  output_file = report_file,
  analysis_title = "Überblick über den Dataframe",
  formula_text = paste("summary, str, head(df)"),
  sample_size = as.character(df_size),
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