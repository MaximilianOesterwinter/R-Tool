# 📊 R Tool for Data Analysis

Thank you for using my small R tool!  
This tool helps you perform basic statistical analyses in the social sciences via a simple command-line interface.

---

## Project Goal

This tool is designed to reduce the technical barrier of working with R syntax for basic social science analyses. It is not intended to replace methodological understanding or the interpretation of results. Instead, it aims to support learning by making statistical workflows more accessible.

---

## 🚀 Installation

### 1. Required installations

Make sure that RStudio, Git and Python are installed on your system.
Add Rscript.exe, Python and Pandoc to your PATH.

- Rscript.exe is usually found in `C:\Program Files\R\R-4.x.x\bin`.
- Python can be automatically added to the PATH during installation.
- The path to Pandoc can by found by running the following command in R:
```R
Sys.getenv("RSTUDIO_PANDOC")
```

Navigate to the folder where you want to install the program using the explorer.
Right-click inside this folder and click "Open in Terminal".
Once in the terminal, run the following command:
```Bash
git clone https://github.com/MaximilianOesterwinter/R-Tool.git
```

---

### 2. Install required packages

Open a new R script and run the following commands:

```r
install.packages("readr")
install.packages("dplyr")
install.packages("rmarkdown")
install.packages("knitr")
install.packages("psych")
install.packages("car")
install.packages("tinytex")

tinytex::install_tinytex()
```
### 3. Verify installation

Open the console (PowerShell or CMD) and run:

```Bash
Rscript --version
python --version
pandoc --version
```

If everything is installed correctly, the console will display the installed version of `Rscript`, `python` and `pandoc`.

### 4. Prepare your data

Open the file `r-scripts\prepare_data.R` and add your desired data transformations in the designated section.

👉 Important:
Chain commands using the pipe operator:
```R
%>%
```

### 5. Done!

The tool is now ready to use 🎉

## 💻 Usage

The program is currently in **alpha stage** and is therefore controlled via the command line. To use it reliably, just open the console via the explorer while inside the programs directory.

### Basic command structure:

```Bash
python main.py ANALYSIS VARIABLE_1 VARIABLE_2
```

### 🧠 Explanation

| Component | Description |
|-------------|-----------|
| `python`/`py`| Starts the programm |
| `main.py` | Main script |
| `ANALYSIS` | Desired analysis |
| `VARIABLE` | Variables from your dataset |

### 📌 Example

```Bash
python main.py chi_square gender vote_intent
```

## 📈 Supported Analyses

### 🔍 Overview

| Analysis | Description | Required Variables |
|---------|--------------|---------------------|
| `df` | Overview of the dataframe | none |
| `describe` | Descriptive statistics | 1 variable |
| `chi_square` | Chi-square test | 2 variables |
| `logit` | Logistic regression | 1 IV, >= 1 DV |
| `lin_reg` | Linear regression | 1 IV, >= 1 DV |
| `anova` | ANOVA (one- or two-factor) | 1 DV, 1-2 IVs |

### 📊 Details

`df`
Displays an overview of the entire dataframe.

`describe`
Calculates basic descriptive statistics.

`chi_square`
Performs a chi-square test between two variables.

`logit`
Performs a logistic regression analysis.

`lin_reg`
Performs a linear regression analysis.

`anova`
Performs an ANOVA including the required post-hoc tests:
- 1 IV -> one-way ANOVA
- 2 IVs -> two-way ANOVA

## ⚠️ Notes

- Make sure to use the **exact variable** names (including case sensitivity).
- The tool is currently **CLI-based** (no graphical interface).
- Errors often occur due to incorrectly named or improperly formatted variables.

## 🛠️ Planned Features

- GUI (graphical user interface)
- Extended statistical tests
## 📄 Lizenz

MIT License

See LICENSE.md
