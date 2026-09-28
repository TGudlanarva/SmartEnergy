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
# 5. Convert to long format
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
# 7. Sort by state and date
# ==========================================

df = df.sort_values(
    ["State", "Dates"]
).reset_index(drop=True)


# ==========================================
# 8. Create date features
# ==========================================

df["Year"] = df["Dates"].dt.year
df["Month"] = df["Dates"].dt.month
df["Day"] = df["Dates"].dt.day
df["Day_of_Week"] = df["Dates"].dt.dayofweek


# ==========================================
# 9. Create previous calendar day's demand
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


# ==========================================
# 10. Merge previous day's value
# ==========================================

df = df.merge(
    previous_day,
    on=["Dates", "State"],
    how="left"
)


# ==========================================
# 11. Remove rows without previous day
# ==========================================

df = df.dropna(
    subset=["Previous_Day_Consumption"]
)


# ==========================================
# 12. Display results
# ==========================================

print("===== TIME-SERIES DATASET =====")

print("\nShape:")
print(df.shape)

print("\nFirst 10 rows:")
print(
    df[
        [
            "Dates",
            "State",
            "Consumption",
            "Previous_Day_Consumption"
        ]
    ].head(10)
)

print("\nMissing previous-day values:")
print(
    df["Previous_Day_Consumption"].isnull().sum()
)