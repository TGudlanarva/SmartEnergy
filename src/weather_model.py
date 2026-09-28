import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. Load final smart energy dataset
# ==========================================

df = pd.read_csv(
    "data/smart_energy_dataset.csv"
)

df["Dates"] = pd.to_datetime(df["Dates"])


# ==========================================
# 2. Encode State
# ==========================================

df["State_Code"] = (
    df["State"].astype("category").cat.codes
)


# ==========================================
# 3. Sort chronologically
# ==========================================

df = df.sort_values("Dates")


# ==========================================
# 4. Define features
# ==========================================

features = [
    "State_Code",
    "Year",
    "Month",
    "Day",
    "Day_of_Week",

    "Previous_Day_Consumption",
    "Previous_7_Day_Consumption",
    "Rolling_7_Day_Average",

    "Temperature",
    "Humidity",
    "Rainfall",
    "Wind_Speed"
]


# ==========================================
# 5. Target
# ==========================================

target = "Consumption"


X = df[features]
y = df[target]


# ==========================================
# 6. Chronological train/test split
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
# 7. Create Random Forest
# ==========================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)


# ==========================================
# 8. Train
# ==========================================

print("\nTraining weather-aware model...")

model.fit(X_train, y_train)

print("Training completed!")


# ==========================================
# 9. Predictions
# ==========================================

y_pred = model.predict(X_test)


# ==========================================
# 10. Evaluation
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


print("\n===== WEATHER MODEL RESULTS =====")

print("MAE :", mae)
print("RMSE:", rmse)
print("R2  :", r2)


# ==========================================
# 11. Save model
# ==========================================

model_path = (
    "models/weather_energy_model.pkl"
)

joblib.dump(
    model,
    model_path
)

print("\nModel saved to:")
print(model_path)