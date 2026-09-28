import pandas as pd
import joblib


# ==========================================
# 1. Load model
# ==========================================

model = joblib.load(
    "models/weather_energy_model.pkl"
)


# ==========================================
# 2. Load smart energy dataset
# ==========================================

df = pd.read_csv(
    "data/smart_energy_dataset.csv"
)

df["Dates"] = pd.to_datetime(df["Dates"])


# ==========================================
# 3. Create state mapping
# ==========================================

states = sorted(
    df["State"].unique()
)

state_mapping = {
    state: code
    for code, state in enumerate(states)
}


# ==========================================
# 4. Ask user for state
# ==========================================

print("\nAvailable states:")

for state in states:
    print("-", state)

state = input(
    "\nEnter state: "
)


if state not in state_mapping:

    print("Invalid state.")

    exit()


# ==========================================
# 5. Ask prediction date
# ==========================================

prediction_date = input(
    "Enter prediction date (YYYY-MM-DD): "
)

prediction_date = pd.to_datetime(
    prediction_date
)


# ==========================================
# 6. Get state's historical data
# ==========================================

state_data = df[
    df["State"] == state
].copy()

state_data = state_data.sort_values(
    "Dates"
)


# ==========================================
# 7. Find latest available data
# ==========================================

historical = state_data[
    state_data["Dates"] < prediction_date
]


if len(historical) == 0:

    print(
        "No historical data available."
    )

    exit()


# ==========================================
# 8. Get latest consumption
# ==========================================

latest = historical.iloc[-1]

previous_day = latest[
    "Consumption"
]


# ==========================================
# 9. Get consumption 7 days earlier
# ==========================================

seven_days_ago_date = (
    prediction_date -
    pd.Timedelta(days=7)
)

seven_day_data = state_data[
    state_data["Dates"] ==
    seven_days_ago_date
]


if len(seven_day_data) > 0:

    previous_7_day = (
        seven_day_data.iloc[0]["Consumption"]
    )

else:

    previous_7_day = (
        historical.tail(7)["Consumption"].mean()
    )


# ==========================================
# 10. Calculate 7-day average
# ==========================================

recent_data = historical.tail(7)

rolling_average = (
    recent_data["Consumption"].mean()
)


# ==========================================
# 11. Weather input
# ==========================================

temperature = float(
    input("Enter temperature (°C): ")
)

humidity = float(
    input("Enter humidity (%): ")
)

rainfall = float(
    input("Enter rainfall (mm): ")
)

wind_speed = float(
    input("Enter wind speed (m/s): ")
)


# ==========================================
# 12. Date features
# ==========================================

year = prediction_date.year

month = prediction_date.month

day = prediction_date.day

day_of_week = (
    prediction_date.dayofweek
)


# ==========================================
# 13. Create model input
# ==========================================

input_data = pd.DataFrame({

    "State_Code": [
        state_mapping[state]
    ],

    "Year": [year],

    "Month": [month],

    "Day": [day],

    "Day_of_Week": [
        day_of_week
    ],

    "Previous_Day_Consumption": [
        previous_day
    ],

    "Previous_7_Day_Consumption": [
        previous_7_day
    ],

    "Rolling_7_Day_Average": [
        rolling_average
    ],

    "Temperature": [
        temperature
    ],

    "Humidity": [
        humidity
    ],

    "Rainfall": [
        rainfall
    ],

    "Wind_Speed": [
        wind_speed
    ]
})


# ==========================================
# 14. Predict
# ==========================================

prediction = model.predict(
    input_data
)


# ==========================================
# 15. Display
# ==========================================

print("\n================================")
print("SMART ENERGY PREDICTION")
print("================================")

print("State:", state)

print(
    "Prediction date:",
    prediction_date.date()
)

print(
    "Previous consumption:",
    previous_day,
    "MU"
)

print(
    "7-day average:",
    round(rolling_average, 2),
    "MU"
)

print(
    "\nPredicted electricity demand:",
    round(prediction[0], 2),
    "MU"
)