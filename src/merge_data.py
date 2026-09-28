import pandas as pd


# ==========================================
# 1. Load electricity data
# ==========================================

electricity = pd.read_csv(
    "data/Indias_Electricity_Consumption_Dataset.csv"
)

electricity = electricity.drop(
    columns=["Unnamed: 0"]
)

electricity["Dates"] = pd.to_datetime(
    electricity["Dates"]
)


# ==========================================
# 2. Select state columns
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
    col for col in electricity.columns
    if col not in exclude_columns
]


# ==========================================
# 3. Convert electricity to long format
# ==========================================

electricity = electricity.melt(
    id_vars=["Dates"],
    value_vars=state_columns,
    var_name="State",
    value_name="Consumption"
)


# ==========================================
# 4. Remove missing consumption
# ==========================================

electricity = electricity.dropna(
    subset=["Consumption"]
)


# ==========================================
# 5. Sort
# ==========================================

electricity = electricity.sort_values(
    ["State", "Dates"]
).reset_index(drop=True)


# ==========================================
# 6. Previous day consumption
# ==========================================

previous_day = electricity[
    ["Dates", "State", "Consumption"]
].copy()

previous_day["Dates"] = (
    previous_day["Dates"] +
    pd.Timedelta(days=1)
)

previous_day = previous_day.rename(
    columns={
        "Consumption":
        "Previous_Day_Consumption"
    }
)

electricity = electricity.merge(
    previous_day,
    on=["Dates", "State"],
    how="left"
)


# ==========================================
# 7. Previous 7-day consumption
# ==========================================

previous_week = electricity[
    ["Dates", "State", "Consumption"]
].copy()

previous_week["Dates"] = (
    previous_week["Dates"] +
    pd.Timedelta(days=7)
)

previous_week = previous_week.rename(
    columns={
        "Consumption":
        "Previous_7_Day_Consumption"
    }
)

electricity = electricity.merge(
    previous_week,
    on=["Dates", "State"],
    how="left"
)


# ==========================================
# 8. Rolling 7-day average
# ==========================================

electricity["Rolling_7_Day_Average"] = (
    electricity
    .groupby("State")["Consumption"]
    .transform(
        lambda x:
        x.shift(1).rolling(7).mean()
    )
)


# ==========================================
# 9. Date features
# ==========================================

electricity["Year"] = (
    electricity["Dates"].dt.year
)

electricity["Month"] = (
    electricity["Dates"].dt.month
)

electricity["Day"] = (
    electricity["Dates"].dt.day
)

electricity["Day_of_Week"] = (
    electricity["Dates"].dt.dayofweek
)


# ==========================================
# 10. Load weather data
# ==========================================

weather = pd.read_csv(
    "data/all_states_weather.csv"
)

weather["Dates"] = pd.to_datetime(
    weather["Dates"]
)


# ==========================================
# 11. Merge electricity + weather
# ==========================================

merged = electricity.merge(
    weather,
    on=["Dates", "State"],
    how="inner"
)


# ==========================================
# 12. Remove missing feature values
# ==========================================

merged = merged.dropna(
    subset=[
        "Previous_Day_Consumption",
        "Previous_7_Day_Consumption",
        "Rolling_7_Day_Average",
        "Temperature",
        "Humidity",
        "Rainfall",
        "Wind_Speed"
    ]
)


# ==========================================
# 13. Sort final dataset
# ==========================================

merged = merged.sort_values(
    ["State", "Dates"]
).reset_index(drop=True)


# ==========================================
# 14. Save final dataset
# ==========================================

output_path = (
    "data/smart_energy_dataset.csv"
)

merged.to_csv(
    output_path,
    index=False
)


# ==========================================
# 15. Display information
# ==========================================

print("================================")
print("SMART ENERGY DATASET")
print("================================")

print("\nShape:")
print(merged.shape)

print("\nColumns:")
print(merged.columns.tolist())

print("\nNumber of states:")
print(merged["State"].nunique())

print("\nMissing values:")
print(
    merged.isnull().sum()
)

print("\nFirst 5 rows:")
print(merged.head())

print("\nSaved to:")
print(output_path)