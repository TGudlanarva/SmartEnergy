import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load dataset
df = pd.read_csv("data/smart_energy_dataset.csv")
df["Dates"] = pd.to_datetime(df["Dates"])

# Encode states
df["State_Code"] = df["State"].astype("category").cat.codes

# Sort by date
df = df.sort_values("Dates")

# Features
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

target = "Consumption"

X = df[features]
y = df[target]

# Train/test split
split_date = pd.Timestamp("2023-01-01")

train_mask = df["Dates"] < split_date
test_mask = df["Dates"] >= split_date

X_train = X[train_mask]
X_test = X[test_mask]

y_train = y[train_mask]
y_test = y[test_mask]

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

# Smaller Random Forest for cloud deployment
model = RandomForestRegressor(
    n_estimators=25,
    max_depth=15,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

print("\nTraining smaller weather-aware model...")
model.fit(X_train, y_train)

print("Training completed!")

# Predictions
y_pred = model.predict(X_test)

# Metrics
mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("\n===== SMALL WEATHER MODEL RESULTS =====")
print("MAE :", mae)
print("RMSE:", rmse)
print("R2  :", r2)

# Save model
model_path = "models/weather_energy_model_free.pkl"

joblib.dump(model, model_path)

print("\nModel saved to:")
print(model_path)