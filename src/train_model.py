import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. Load dataset
# ==========================================

df = pd.read_csv(
    "data/Indias_Electricity_Consumption_Dataset.csv"
)

df = df.drop(columns=["Unnamed: 0"])

df["Dates"] = pd.to_datetime(df["Dates"])


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
    col for col in df.columns
    if col not in exclude_columns
]


# ==========================================
# 3. Convert wide → long
# ==========================================

df = df.melt(
    id_vars=["Dates"],
    value_vars=state_columns,
    var_name="State",
    value_name="Consumption"
)


# ==========================================
# 4. Remove missing values
# ==========================================

df = df.dropna(
    subset=["Consumption"]
)


# ==========================================
# 5. Sort by state and date
# ==========================================

df = df.sort_values(
    ["State", "Dates"]
).reset_index(drop=True)


# ==========================================
# 6. Date features
# ==========================================

df["Year"] = df["Dates"].dt.year
df["Month"] = df["Dates"].dt.month
df["Day"] = df["Dates"].dt.day
df["Day_of_Week"] = df["Dates"].dt.dayofweek


# ==========================================
# 7. Previous calendar day
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
# 8. Previous 7-day consumption
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
# 9. Rolling 7-day average
# ==========================================

df["Rolling_7_Day_Average"] = (
    df.groupby("State")["Consumption"]
      .transform(
          lambda x: x.shift(1).rolling(7).mean()
      )
)


# ==========================================
# 10. Remove rows without history
# ==========================================

df = df.dropna(
    subset=[
        "Previous_Day_Consumption",
        "Previous_7_Day_Consumption",
        "Rolling_7_Day_Average"
    ]
)


# ==========================================
# 11. Encode state
# ==========================================

df["State_Code"] = (
    df["State"].astype("category").cat.codes
)


# ==========================================
# 12. Sort chronologically
# ==========================================

df = df.sort_values("Dates")


# ==========================================
# 13. Features and target
# ==========================================

features = [
    "State_Code",
    "Year",
    "Month",
    "Day",
    "Day_of_Week",
    "Previous_Day_Consumption",
    "Previous_7_Day_Consumption",
    "Rolling_7_Day_Average"
]

X = df[features]

y = df["Consumption"]


# ==========================================
# 14. Chronological train/test split
# ==========================================

split_date = pd.Timestamp("2023-01-01")

train_mask = df["Dates"] < split_date
test_mask = df["Dates"] >= split_date

X_train = X[train_mask]
X_test = X[test_mask]

y_train = y[train_mask]
y_test = y[test_mask]


print("Training records:", len(X_train))
print("Testing records:", len(X_test))


# ==========================================
# 15. Create model
# ==========================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)


# ==========================================
# 16. Train
# ==========================================

print("\nTraining model...")

model.fit(X_train, y_train)

print("Training completed!")


# ==========================================
# 17. Predict
# ==========================================

y_pred = model.predict(X_test)


# ==========================================
# 18. Evaluate
# ==========================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = mean_squared_error(
    y_test,
    y_pred
) ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)


print("\n===== BASELINE MODEL RESULTS =====")

print("MAE :", mae)
print("RMSE:", rmse)
print("R2  :", r2)


# ==========================================
# 19. Save model
# ==========================================

model_path = "models/energy_demand_model.pkl"

joblib.dump(
    model,
    model_path
)

print("\nModel saved to:")
print(model_path)