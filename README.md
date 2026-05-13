# 📊 R Tool for Data Analysis

Thank you for using my small R tool!  
This tool helps you perform basic statistical analyses in the social sciences via a simple graphical interface.

---

## Project Goal

R-Tool is a graphical user interface for R that is primarily intended as 
a support tool for students working with empirical social science data. 
The program aims to reduce syntactic barriers in R without automating 
the analytical process itself. Instead of replacing methodological reasoning,
R-Tool is designed to simplify common workflows in data preparation,
statistical analysis and visualization so that users can focus more strongly 
on research design, variable selection, interpretation and methodological 
decision-making.

---
The project was developed in Python using tkinter for the graphical user 
interface, while the statistical operations themselves are executed through R 
scripts in the background. The application is especially aimed at students who 
are beginning to work with R and frequently struggle with syntax, object 
handling or data management.


## Supported Workflow

The program currently supports the following workflow:

- Select a dataset
- Prepare and manage variables
- Create subsets of datasets
- Factorize variables
- Rename variables
- Create new variables through mutate operations
- Run statistical analyses
- Generate plots

The preparation module has been expanded significantly and now allows several 
important data management operations directly through the GUI.

### "Subframe"

The “Subframe” function allows users to create a subset of a dataset by 
selecting only the variables needed for further analysis. The new subframe can 
be named freely by the user and is saved as a new `.rds` dataset in the 
`prepared` data directory. Optionally, the selected variables can be 
transformed into long format using `pivot_longer()`. Missing values can also be 
removed automatically during the creation of the subframe.

### "Factorize variables"

The “Factorize variables” function allows users to transform selected variables 
into factors directly inside the dataset. Users can define levels and labels 
manually through the GUI. The transformation is performed in-place, meaning 
that the existing dataset is updated instead of creating unnecessary copies of 
the data.

### "Rename variables"

The “Rename variables” function allows users to rename variables directly 
through the graphical interface. This is especially useful when working with 
larger datasets containing cryptic or automatically generated variable names. 
Variables are selected from dropdown menus displaying both variable names and 
their data types. The dataset is updated in-place after renaming.

### "Mutate variables"

The “Mutate variables” function introduces several common data transformation 
workflows frequently used in social science research. Instead of requiring 
users to write R syntax manually, the GUI generates the necessary mutate 
operations automatically.

Currently supported mutate operations include:

- Arithmetic operations between variables (+, -, *, /, ^)
- Row means
- Row sums
- Log transformations
- Z-standardization
- Reverse scaling
- Recode / case_when operations

The `row mean` and `row sum` functions allow users to create indices or
additive scales from multiple variables while optionally removing missing
values.

The `reverse scale` function allows users to reverse Likert-type scales by 
specifying the minimum and maximum scale values.

The `recode / case_when` functionality allows users to create new categorical 
variables through conditional logic directly in the GUI. Users can define 
multiple recode rules using comparison operators such as ==, !=, >, >=, < and 
<=.

### "Create summary dataset"

This function reduces the number of variables in the new subframe by summarising the selected variables. It also includes the option to group the new dataframe by a grouping variable or to remove all missing values. This is important for some of the currently included summary-functions. These include:

- Mean
- Median
- Standard deviation
- Minimum
- Maximum
- Sum
- Observations
- Distinct observations

---

Examples of possible workflows include:

- Creating additive democracy indices
- Reverse coding survey items
- Building age categories
- Creating dummy variables
- Renaming variables before analysis
- Constructing smaller analysis-ready datasets

## Limits

The program deliberately does not provide automated interpretations of 
statistical results and does not decide which analytical methods should be 
used. The goal is to support methodological learning rather than replacing it 
through automation or AI-generated analyses.


## 🚀 Installation

### 1. Required installations

Make sure that RStudio and Pandoc are installed on your system.

---

Download the ZIP-File and unpack it. You can find the File in the assets under the releases.

### 2. Install required packages

Open a new R script and run the following commands (You can copy/paste them and run them one by one):

```R
install.packages("tidyverse")
install.packages("rmarkdown")
install.packages("knitr")
install.packages("psych")
install.packages("car")
install.packages("DescTools")
install.packages("readxl")
install.packages("tinytex")

tinytex::install_tinytex()
```

### 4. Prepare your data

The tool comes with one example-dataset to try it out.

---

When you want to add your own data, complete the following steps:

- Open the file `r-scripts\preparation_template.R`
- Import your dataset into the R-Script.
- Complete the output-path at the bottom.
- The template automatically saves your dataset as a `.rds` file in `/data/prepared/`
- If your dataset is already in `.rds` format, you can skip this step and directly save it into `/data/prepared/`.
---

⚠️ Notes:

- The prepared dataset needs to be in the folder ```/data/prepared/``` for the program to find it!
- All locations, that need to be tampered with, are marked in the template!


### 5. Done!

The tool is now ready to use 🎉

## 📈 Supported Analyses

### 🔍 Overview

| Analysis | Description | Required Variables |
|---------|--------------|---------------------|
| `Dataframe` | Overview of the dataframe | none |
| `Describe` | Descriptive statistics | 1 variable |
| `Describe By` | Grouped descriptive statistics | 1 DV, 1 binary grouping variable |
| `Chi Square` | Chi-square test | 2 variables |
| `Logit Model` | Logistic regression | 1 IV, >= 1 DV |
| `Linear Regression` | Linear regression | 1 IV, >= 1 DV |
| `ANOVA` | ANOVA (one- or two-factor) | 1 DV, 1-2 IVs |
| `Unpaired t-test` | One-sample or unpaired two-sample t-test | 1 Variable and 1 Constant or 2 Variables |
| `Paired t-test` | Paired two-sample t-test | 2 Variables |
| `Normality Test` | Normality assumption for the independent-samples t-test | 1 DV, 1 binary grouping variable |
| `Welch Test` | Welch test for two unpaired samples with unequal variances | 1 DV, 1 binary grouping variable |
| `Correlation` | Pearson's r, Kendall's tau, Spearman's rho | 2 numerical variables |
| `Mann-Whitney Test` | non-parametric Mann-Whitney-U-Test | 1 DV, 1 binary grouping variable |

### 📊 Details

`Dataframe`
Displays an overview of the entire dataframe.

`Describe`
Calculates basic descriptive statistics.

`Describe By`
Calculates grouped descriptive statistics. Mainly to check for equal variances.
If variances are about equal, perform `unpaired_ttest`, else perform `welch_test`.

`Chi Square`
Performs a chi-square test between two variables.

`Logit Model`
Performs a logistic regression analysis.

`Linear Regression`
Performs a linear regression analysis.

`ANOVA`
Performs an ANOVA including the required post-hoc tests:
- 1 IV -> one-way ANOVA, Cohen's f
- 2 IVs -> two-way ANOVA

`Unpaired t-test`
Performs a one-sample or unpaired two-sample t-test, depending on the number of variables given:
- 1 DV and 1 Constant -> one-sample t-test
- 2 Variables -> two-sample t-test for equal variances!!! If the variances are not equal, perform `welch_test`.

`Paired t-test`
Performs a paired two-sample t-test and also outputs the paired normality

`Normality Test`
Performs a Shapiro-Wilk normality test on a numerical DV grouped by the grouping variable

`Welch Test`
Performs a Welch test for two unpaired samples, while their variances are unequal.

`Correlation`
Calculates Pearson's r, Kendall's tau and Spearman's rho and plots the two variables.

`Mann-Whitney Test`
Performs the non-parametric Mann-Whitney-U-Test.

## 📈 Supported Plots

- Histogram (WIP)
- Boxplot (WIP)
- Boxplot by Group (WIP)
- Scatterplot (WIP)
- Barplot
- Barplot by Group (WIP)
- Lineplot (WIP)
- Column chart

## ⚠️ Notes

Datasets and generated files are stored locally. Statistical analyses and plots are executed through dedicated R scripts located in the r-scripts directory. The modular architecture makes it relatively easy to add new analysis methods, plotting functions or data preparation workflows in the future.

R-Tool is still under active development and new features are continuously being added.

## 🛠️ Planned Features

- More functionality for the GUI
- Non-parametric statistical methods (e.g., Wilcoxon, Kruskal–Wallis)
- Effect size calculations (e.g., Cohen’s d, η², Cramér’s V)
- Factor analysis (e.g., PCA, exploratory factor analysis)

## 📄 License

MIT License

See LICENSE.md
