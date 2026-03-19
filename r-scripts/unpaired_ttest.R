args <- commandArgs(trailingOnly = TRUE)

data_path <- args[1]
var1 <- args[2]
var2_or_constant <- args[3]

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", script_args[grep("^--file=", script_args)])
script_dir <- dirname(normalizePath(script_file))
project_dir <- dirname(script_dir)

source(file.path(script_dir, "prepare_data.R"))
source(file.path(script_dir, "render_report.R"))

output_dir <- file.path(project_dir, "output")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

df <- prepare_data(data_path)

auto_t_test <- function(df, var1, var2_or_constant) {
  
  var1_name <- var1
  
  if (!var1_name %in% names(df)) {
    stop(sprintf("Variable '%s' was not found in the dataset.", var1_name))
  }
  
  x <- df[[var1_name]]
  
  if (var2_or_constant %in% names(df)) {
    
    analysis_data <- na.omit(df[, c(var1_name, var2_or_constant)])
    x <- analysis_data[[var1_name]]
    y <- analysis_data[[var2_or_constant]]
    
    result <- t.test(x, y, alternative = "two.sided", paired = FALSE, var.equal = TRUE)
    
    result_text <- paste(
      "\n\nTwo-sample t-test:\n",
      paste(capture.output(print(result)), collapse = "\n"),
      sep = ""
    )
    
    report_file <- file.path(output_dir, paste0("Twosample_ttest_", var1, ".pdf"))
    
    formula_text <- paste0(
      "t.test(", var1_name, ", ", var2_or_constant,
      ", alternative = 'two.sided', paired = FALSE, var.equal = TRUE)"
    )
    
    render_report(
      template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
      output_file = report_file,
      analysis_title = "Two-sample t-test",
      formula_text = formula_text,
      sample_size = as.character(nrow(analysis_data)),
      result_text = result_text,
      plot_path = ""
    )
    
    cat("PDF saved in:\n")
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
    
  } else if (!is.na(suppressWarnings(as.numeric(var2_or_constant)))) {
    
    mu <- as.numeric(var2_or_constant)
    
    result <- t.test(x, mu = mu)
    
    result_text <- paste(
      "\n\nOne-sample t-test:\n",
      paste(capture.output(print(result)), collapse = "\n"),
      sep = ""
    )
    
    formula_text <- paste0(
      "t.test(", var1_name, ", mu = ", var2_or_constant, ")"
    )
    
    report_file <- file.path(output_dir, paste0("Onesample_ttest_", var1, ".pdf"))
    
    render_report(
      template_path = file.path(project_dir, "templates", "analysis_report.Rmd"),
      output_file = report_file,
      analysis_title = "One-sample t-test",
      formula_text = formula_text,
      sample_size = as.character(sum(!is.na(x))),
      result_text = result_text,
      plot_path = ""
    )
    
    cat("PDF saved in:\n")
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
    
  } else {
    stop(sprintf(
      "The second argument '%s' is neither a variable in the dataset nor a numeric constant.",
      var2_or_constant
    ))
  }
}

auto_t_test(df, var1, var2_or_constant)