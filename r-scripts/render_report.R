render_report <- function(template_path,
                          output_file,
                          analysis_title,
                          formula_text,
                          sample_size,
                          result_text,
                          plot_path = "") {

  if (!requireNamespace("rmarkdown", quietly = TRUE)) {
    stop("Paket 'rmarkdown' ist nicht installiert.")
  }

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
    quiet = FALSE
  )
}
