library(readr)
library(dplyr)

df <- read_csv(
  #Replace the example with the absolute path to your dataframe:
  "/home/YourName/workspace/RTool/data/raw/example_1.csv",
  na = c("", "NA"),
  show_col_types = FALSE
)

df_prepared <- df %>%
  # Perform the desired transformations here and connect them with the pipe-operator %>%.
  # The following transformations are examples and won't work with your dataframe!!
  rename_with(trimws) %>%
  distinct() %>%
  filter(!is.na(id)) %>%
  mutate(
    id = as.integer(id),
    age = as.numeric(age),
    income = as.numeric(income),
    satisfaction = as.numeric(satisfaction),
    recommendation_score = as.numeric(recommendation_score),
    support_tickets_last_12m = as.integer(support_tickets_last_12m),
    weekly_usage_hours = as.numeric(weekly_usage_hours),
    tenure_months = as.integer(tenure_months),
    
    gender = factor(gender, levels = c("male", "female")),
    education = factor(education, levels = c("highschool", "bachelor", "master", "phd")),
    used_product = factor(used_product, levels = c("no", "yes")),
    region = factor(region, levels = c("urban", "suburban", "rural")),
    subscription_plan = factor(subscription_plan, levels = c("basic", "standard", "premium")),
    churn_risk = factor(churn_risk, levels = c("low", "medium", "high"))
  )


write_csv(df_prepared,
          #Replace the example with the correct absolute output-path.
          #You should only have to replace the last folder and the file-name from the input-path, you typed in earlier!
          #It is important, that you save the file in .../RTool/data/prepared/!!
          "/home/YourName/workspace/RTool/data/prepared/example_1_prepared.csv",
          na = ""
)
