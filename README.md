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

Open a new R script and run the following commands (You can copy/paste them and run them one by one):

```R
install.packages("readr")
install.packages("dplyr")
install.packages("ggplot2")
install.packages("rmarkdown")
install.packages("knitr")
install.packages("psych")
install.packages("car")
install.packages("DescTools")
install.packages("tinytex")

tinytex::install_tinytex()
```

### 4. Prepare your data

The tool comes with two example-datasets to try it out.
---

When you want to add your own data, complete the following steps:

- Open the file `r-scripts\preparation_template.R`
- Import your dataset into the R-Script using the pre-written command. If you save your raw data in ```/data/raw/```, you only need minimal changes to the provided path!
- Add your desired data transformations in the designated section.
- Complete the output-path at the bottom. If you used the trick in step 2, you can use the import-path from above with small changes at the end: Replace ```raw``` with ```prepared``` and change the file-name to a recognizable name you like.
---

⚠️ Notes:

- The prepared dataset needs to be in the folder ```/data/prepared/``` for the program to find it!
- All locations, that need to be tampered with, are marked in the template!
- Don't forget to save the template in a separate file. If the analyses don't work properly, it's mostly due to improperly formatted variables in the dataset. Being able to quickly change the formatting is invaluable for a smooth workflow!


### 5. Done!

The tool is now ready to use 🎉

## 💻 Usage

Open `R_Tool.R` and select in the bottom right the dataset, you want to work with. After that, choose the desired analysis. 
If variables are needed for the selected type of analysis, dropdown-menus will appear, where you can select your variables.
Note, that the corresponding variable-type is written next to the variable-name, as not every analysis supports every type.
Finally, press `Execute analysis` and wait a few seconds for the output-PDF to appear.


## 📈 Supported Analyses

### 🔍 Overview

| Analysis | Description | Required Variables |
|---------|--------------|---------------------|
| `dataframe` | Overview of the dataframe | none |
| `describe` | Descriptive statistics | 1 variable |
| `describeBy` | Grouped descriptive statistics | 1 DV, 1 binary grouping variable |
| `chi-square` | Chi-square test | 2 variables |
| `logistic-regression` | Logistic regression | 1 IV, >= 1 DV |
| `linear-regression` | Linear regression | 1 IV, >= 1 DV |
| `anova` | ANOVA (one- or two-factor) | 1 DV, 1-2 IVs |
| `unpaired-t-test` | One-sample or unpaired two-sample t-test | 1 Variable and 1 Constant or 2 Variables |
| `paired-t-test` | Paired two-sample t-test | 2 Variables |
| `normality-test` | Normality assumption for the independent-samples t-test | 1 DV, 1 binary grouping variable |
| `welch-test` | Welch test for two unpaired samples with unequal variances | 1 DV, 1 binary grouping variable |
| `correlation` | Pearson's r, Kendall's tau, Spearman's rho | 2 numerical variables |
| `mann-whitney-u-test` | non-parametric Mann-Whitney-U-Test | 1 DV, 1 binary grouping variable |

### 📊 Details

`dataframe`
Displays an overview of the entire dataframe.

`describe`
Calculates basic descriptive statistics.

`describeBy`
Calculates grouped descriptive statistics. Mainly to check for equal variances.
If variances are about equal, perform `unpaired_ttest`, else perform `welch_test`.

`chi-square`
Performs a chi-square test between two variables.

`logistic-regression`
Performs a logistic regression analysis.

`linear-regression`
Performs a linear regression analysis.

`anova`
Performs an ANOVA including the required post-hoc tests:
- 1 IV -> one-way ANOVA, Cohen's f
- 2 IVs -> two-way ANOVA

`unpaired-t-test`
Performs a one-sample or unpaired two-sample t-test, depending on the number of variables given:
- 1 DV and 1 Constant -> one-sample t-test
- 2 Variables -> two-sample t-test for equal variances!!! If the variances are not equal, perform `welch_test`.

`paired-t-test`
Performs a paired two-sample t-test and also outputs the paired normality

`normality-test`
Performs a Shapiro-Wilk normality test on a numerical DV grouped by the grouping variable

`welch-test`
Performs a Welch test for two unpaired samples, while their variances are unequal.

`correlation`
Calculates Pearson's r, Kendall's tau and Spearman's rho and plots the two variables.

`mann-whitney-u-test`
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
