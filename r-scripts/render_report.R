render_report <- function(template_path,
                          output_file,
                          analysis_title,
                          formula_text,
                          sample_size,
                          result_text,
                          plot_path = "") {

  if (!requireNamespace("rmarkdown", quietly = TRUE)) {
    stop("Package 'rmarkdown' is not installed.")
  }

  if (!requireNamespace("knitr", quietly = TRUE)) {
    stop("Package 'knitr' is not installed.")
  }

  analysis_title <- sanitize_text_for_pdf(analysis_title)
  formula_text <- sanitize_text_for_pdf(formula_text)
  sample_size <- sanitize_text_for_pdf(sample_size)
  result_text <- sanitize_text_for_pdf(result_text)

  rmarkdown::render(
    input = template_path,
    output_file = output_file,
    params = list(
      analysis_title = analysis_title,
      formula_text = formula_text,
      sample_size = sample_size,
      result_text = result_text,
      plot_path = plot_path
    ),
    envir = new.env(parent = globalenv()),
    quiet = TRUE
  )
}

sanitize_text_for_pdf <- function(text) {
  text <- gsub("ℹ", "Info", text, fixed = TRUE)
  text <- gsub("✔", "OK", text, fixed = TRUE)
  text <- gsub("✖", "X", text, fixed = TRUE)
  text <- gsub("→", "->", text, fixed = TRUE)
  text <- gsub("≤", "<=", text, fixed = TRUE)
  text <- gsub("≥", ">=", text, fixed = TRUE)
  text <- gsub("−", "-", text, fixed = TRUE)
  text
}
