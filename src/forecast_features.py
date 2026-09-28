import pandas as pd


# ==========================================
# 1. Load dataset
# ==========================================

df = pd.read_csv(
    "data/Indias_Electricity_Consumption_Dataset.csv"
)


# ==========================================
# 2. Remove unnecessary column
# ==========================================

df = df.drop(columns=["Unnamed: 0"])


# ==========================================
# 3. Convert Dates
# ==========================================

df["Dates"] = pd.to_datetime(df["Dates"])


# ==========================================
# 4. Select state columns
# ==========================================

exclude_columns = [
    "Dates",
    "Total Consumption",
    "DVC",
    "Essar steel",
    "DD",
    "DNH"
]

state_columns = [
    col for col in df.columns
    if col not in exclude_columns
]


# ==========================================
# 5. Convert wide → long
# ==========================================

df = df.melt(
    id_vars=["Dates"],
    value_vars=state_columns,
    var_name="State",
    value_name="Consumption"
)


# ==========================================
# 6. Remove missing consumption
# ==========================================

df = df.dropna(
    subset=["Consumption"]
)


# ==========================================
# 7. Sort
# ==========================================

df = df.sort_values(
    ["State", "Dates"]
).reset_index(drop=True)


# ==========================================
# 8. Date features
# ==========================================

df["Year"] = df["Dates"].dt.year
df["Month"] = df["Dates"].dt.month
df["Day"] = df["Dates"].dt.day
df["Day_of_Week"] = df["Dates"].dt.dayofweek


# ==========================================
# 9. Previous calendar day
# ==========================================

previous_day = df[
    ["Dates", "State", "Consumption"]
].copy()

previous_day["Dates"] = (
    previous_day["Dates"] +
    pd.Timedelta(days=1)
)

previous_day = previous_day.rename(
    columns={
        "Consumption": "Previous_Day_Consumption"
    }
)

df = df.merge(
    previous_day,
    on=["Dates", "State"],
    how="left"
)


# ==========================================
# 10. Previous 7-day consumption
# ==========================================

previous_week = df[
    ["Dates", "State", "Consumption"]
].copy()

previous_week["Dates"] = (
    previous_week["Dates"] +
    pd.Timedelta(days=7)
)

previous_week = previous_week.rename(
    columns={
        "Consumption": "Previous_7_Day_Consumption"
    }
)

df = df.merge(
    previous_week,
    on=["Dates", "State"],
    how="left"
)


# ==========================================
# 11. 7-day rolling average
# ==========================================

df["Rolling_7_Day_Average"] = (
    df.groupby("State")["Consumption"]
      .transform(
          lambda x: x.shift(1).rolling(7).mean()
      )
)


# ==========================================
# 12. Remove rows without enough history
# ==========================================

df = df.dropna(
    subset=[
        "Previous_Day_Consumption",
        "Previous_7_Day_Consumption",
        "Rolling_7_Day_Average"
    ]
)


# ==========================================
# 13. Display results
# ==========================================

print("===== FORECASTING DATASET =====")

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 10 rows:")

print(
    df[
        [
            "Dates",
            "State",
            "Consumption",
            "Previous_Day_Consumption",
            "Previous_7_Day_Consumption",
            "Rolling_7_Day_Average"
        ]
    ].head(10)
)

print("\nMissing values:")

print(
    df[
        [
            "Previous_Day_Consumption",
            "Previous_7_Day_Consumption",
            "Rolling_7_Day_Average"
        ]
    ].isnull().sum()
)