# 📊 R Tool for Data Analysis

Thank you for using my small R tool!  
This tool helps you perform basic statistical analyses in the social sciences via a simple graphical interface.

---

## Project Goal

This tool is designed to reduce the technical barrier of working with R syntax for basic social science analyses. It is not intended to replace methodological understanding or the interpretation of results. Instead, it aims to support learning by making statistical workflows more accessible.

---

## 🚀 Installation

### 1. Required installations

Make sure that RStudio and Pandoc are installed on your system.
---

Download the ZIP-File and unpack it. You can find the File in the assets under the releases.

### 2. Install required packages

Open a new R script and run the following commands:

```R
install.packages("readr")
install.packages("dplyr")
install.packages("rmarkdown")
install.packages("knitr")
install.packages("psych")
install.packages("car")
install.packages("DescTools")
install.packages("tinytex")

tinytex::install_tinytex()
```

### 4. Prepare your data

The tool comes with an example-dataset to try it out. When you are ready, you can replace the `survey_data.csv` file with your own dataset. It is important to keep the exact file-name. Alternatively you can change the source in `main.py` to your dataset-name. The corresponding line is marked in the code.

Open the file `r-scripts\prepare_data.R` and add your desired data transformations in the designated section.

👉 Important:
Chain commands using the pipe operator:
```R
%>%
```

You can also used an already prepared dataset with this program. Just delete the example-mutations in `r-scripts\prepare_data.R` as well as the pipe-operator `%>%` in this line:
```R
df_clean <- df %>%
```


### 5. Done!

The tool is now ready to use 🎉

## 💻 Usage

Open `R_Tool.R` and select the desired analysis. 
If variables are needed for the selected type of analysis, dropdown-menus will appear, where you can select your variables.
Note, that the corresponding variable-type is written next to the variable-name, as not every analysis supports every type.
Finally, press `Execute analysis` and wait a few seconds for the output-PDF to appear.


## 📈 Supported Analyses

### 🔍 Overview

| Analysis | Description | Required Variables |
|---------|--------------|---------------------|
| `df` | Overview of the dataframe | none |
| `describe` | Descriptive statistics | 1 variable |
| `describeBy` | Grouped descriptive statistics | 1 DV, 1 binary grouping variable |
| `chi_square` | Chi-square test | 2 variables |
| `logit` | Logistic regression | 1 IV, >= 1 DV |
| `lin_reg` | Linear regression | 1 IV, >= 1 DV |
| `anova` | ANOVA (one- or two-factor) | 1 DV, 1-2 IVs |
| `unpaired_ttest` | One-sample or unpaired two-sample t-test | 1 Variable and 1 Constant or 2 Variables |
| `paired_ttest` | Paired two-sample t-test | 2 Variables |
| `norm_test` | Normality assumption for the independent-samples t-test | 1 DV, 1 binary grouping variable |
| `welch_test` | Welch test for two unpaired samples with unequal variances | 1 DV, 1 binary grouping variable |
| `correlation` | Pearson's r, Kendall's tau, Spearman's rho | 2 numerical variables |
| `mann_whitney_test` | non-parametric Mann-Whitney-U-Test | 1 DV, 1 binary grouping variable |

### 📊 Details

`df`
Displays an overview of the entire dataframe.

`describe`
Calculates basic descriptive statistics.

`describeBy`
Calculates grouped descriptive statistics. Mainly to check for equal variances.
If variances are about equal, perform `unpaired_ttest`, else perform `welch_test`.

`chi_square`
Performs a chi-square test between two variables.

`logit`
Performs a logistic regression analysis.

`lin_reg`
Performs a linear regression analysis.

`anova`
Performs an ANOVA including the required post-hoc tests:
- 1 IV -> one-way ANOVA, Cohen's f
- 2 IVs -> two-way ANOVA

`unpaired_ttest`
Performs a one-sample or unpaired two-sample t-test, depending on the number of variables given:
- 1 DV and 1 Constant -> one-sample t-test
- 2 Variables -> two-sample t-test for equal variances!!! If the variances are not equal, perform `welch_test`.

`paired_ttest`
Performs a paired two-sample t-test and also outputs the paired normality

`norm_test`
Performs a Shapiro-Wilk normality test on a numerical DV grouped by the grouping variable

`welch_test`
Performs a Welch test for two unpaired samples, while their variances are unequal.

`correlation`
Calculates Pearson's r, Kendall's tau and Spearman's rho and plots the two variables.

`mann_whitney_test`
Performs the non-parametric Mann-Whitney-U-Test.

## ⚠️ Notes

- Errors often occur due to improperly formatted variables.
- I'm no software engineer nor have I any background in programming. So please don't expect a perfectly written program. However, if you stumble upon mistakes or have ideas for improvement, please let me know and I'll do my best to implement your idea.

## 🛠️ Planned Features

- More functionality for the GUI
- Non-parametric statistical methods (e.g., Wilcoxon, Kruskal–Wallis)
- Effect size calculations (e.g., Cohen’s d, η², Cramér’s V)
- Enhanced data visualization (e.g., histograms, boxplots, scatter plots)
- Factor analysis (e.g., PCA, exploratory factor analysis)

## 📄 License

MIT License

See LICENSE.md
