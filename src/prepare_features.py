import pandas as pd

# ==========================================
# 1. Load the electricity dataset
# ==========================================

df = pd.read_csv(
    "data/Indias_Electricity_Consumption_Dataset.csv"
)

# ==========================================
# 2. Remove unnecessary column
# ==========================================

df = df.drop(columns=["Unnamed: 0"])

# ==========================================
# 3. Convert date to datetime
# ==========================================

df["Dates"] = pd.to_datetime(df["Dates"])

# ==========================================
# 4. State columns
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
# 5. Convert wide format to long format
# ==========================================

df = df.melt(
    id_vars=["Dates"],
    value_vars=state_columns,
    var_name="State",
    value_name="Consumption"
)

# ==========================================
# 6. Remove missing consumption values
# ==========================================

df = df.dropna(subset=["Consumption"])

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
# 9. Create previous-day consumption
# ==========================================

df["Previous_Day_Consumption"] = (
    df.groupby("State")["Consumption"].shift(1)
)

# ==========================================
# 10. Remove rows without previous-day data
# ==========================================

df = df.dropna(
    subset=["Previous_Day_Consumption"]
)

# ==========================================
# 11. Display the final dataset
# ==========================================

print("===== FINAL DATASET =====")

print("Shape:")
print(df.shape)

print("\nFirst 10 rows:")
print(df.head(10))

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nNumber of states:")
print(df["State"].nunique())