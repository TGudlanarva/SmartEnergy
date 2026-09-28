import pandas as pd
import numpy as np
import joblib
import requests
from datetime import timedelta


# --------------------------------------------------
# 1. LOAD MODEL AND DATA
# --------------------------------------------------

model = joblib.load("models/weather_energy_model.pkl")

data = pd.read_csv("data/smart_energy_dataset.csv")
data["Dates"] = pd.to_datetime(data["Dates"])


# --------------------------------------------------
# 2. STATE COORDINATES
# --------------------------------------------------

STATE_COORDINATES = {
    "Andhra Pradesh": (16.5062, 80.6480),
    "Arunachal Pradesh": (27.0844, 93.6053),
    "Assam": (26.1445, 91.7362),
    "Bihar": (25.5941, 85.1376),
    "Chhattisgarh": (21.2514, 81.6296),
    "Delhi": (28.6139, 77.2090),
    "Goa": (15.4909, 73.8278),
    "Gujarat": (23.0225, 72.5714),
    "Haryana": (29.0588, 76.0856),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Jammu and Kashmir": (34.0837, 74.7973),
    "Jharkhand": (23.3441, 85.3096),
    "Karnataka": (12.9716, 77.5946),
    "Kerala": (8.5241, 76.9366),
    "Madhya Pradesh": (23.2599, 77.4126),
    "Maharashtra": (19.0760, 72.8777),
    "Manipur": (24.8170, 93.9368),
    "Meghalaya": (25.5788, 91.8933),
    "Mizoram": (23.1645, 92.9376),
    "Nagaland": (25.6751, 94.1086),
    "Odisha": (20.2961, 85.8245),
    "Punjab": (30.9010, 75.8573),
    "Rajasthan": (26.9124, 75.7873),
    "Sikkim": (27.3389, 88.6065),
    "Tamil Nadu": (13.0827, 80.2707),
    "Telangana": (17.3850, 78.4867),
    "Tripura": (23.8315, 91.2868),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Uttarakhand": (30.0668, 79.0193),
    "West Bengal": (22.5726, 88.3639),
}


# --------------------------------------------------
# 3. STATE CODE
# --------------------------------------------------

states = sorted(data["State"].unique())

state_codes = {
    state: i
    for i, state in enumerate(states)
}


# --------------------------------------------------
# 4. SELECT STATE
# --------------------------------------------------

print("\nAvailable states:")
for state in states:
    print("-", state)

state = input("\nEnter state: ").strip()

if state not in state_codes:
    print("Invalid state name.")
    exit()

if state not in STATE_COORDINATES:
    print("Coordinates not available for this state.")
    exit()


# --------------------------------------------------
# 5. GET LATEST HISTORICAL CONSUMPTION
# --------------------------------------------------

state_data = data[data["State"] == state].sort_values("Dates")

state_data = state_data.dropna(
    subset=[
        "Consumption",
        "Previous_Day_Consumption",
        "Previous_7_Day_Consumption",
        "Rolling_7_Day_Average"
    ]
)

latest_date = state_data["Dates"].max()

latest_rows = state_data.tail(7)

historical_consumption = list(
    latest_rows["Consumption"].values
)

print("\nLatest historical date:", latest_date.date())


# --------------------------------------------------
# 6. GET 7 DAYS OF FUTURE WEATHER
# --------------------------------------------------

latitude, longitude = STATE_COORDINATES[state]

url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": latitude,
    "longitude": longitude,

    # We need today + next 7 days
    "forecast_days": 8,

    "daily": ",".join([
        "temperature_2m_mean",
        "relative_humidity_2m_mean",
        "precipitation_sum",
        "wind_speed_10m_mean"
    ]),

    "timezone": "Asia/Kolkata"
}

response = requests.get(url, params=params)

if response.status_code != 200:
    print("Weather API error:", response.status_code)
    exit()

weather = response.json()["daily"]


# --------------------------------------------------
# 7. CREATE 7-DAY FORECAST
# --------------------------------------------------

predictions = []

current_history = historical_consumption.copy()

for i in range(1, 8):

    prediction_date = pd.to_datetime(
        weather["time"][i]
    )

    # ----------------------------------------------
    # Historical lag features
    # ----------------------------------------------

    previous_day = current_history[-1]

    previous_7_day = current_history[-7]

    rolling_7_day_average = np.mean(
        current_history[-7:]
    )


    # ----------------------------------------------
    # Weather features
    # ----------------------------------------------

    temperature = weather[
        "temperature_2m_mean"
    ][i]

    humidity = weather[
        "relative_humidity_2m_mean"
    ][i]

    rainfall = weather[
        "precipitation_sum"
    ][i]

    wind_speed = weather[
        "wind_speed_10m_mean"
    ][i]


    # ----------------------------------------------
    # Date features
    # ----------------------------------------------

    year = prediction_date.year
    month = prediction_date.month
    day = prediction_date.day
    day_of_week = prediction_date.dayofweek


    # ----------------------------------------------
    # Create model input
    # ----------------------------------------------

    input_data = pd.DataFrame([{

        "State_Code": state_codes[state],

        "Year": year,

        "Month": month,

        "Day": day,

        "Day_of_Week": day_of_week,

        "Previous_Day_Consumption": previous_day,

        "Previous_7_Day_Consumption": previous_7_day,

        "Rolling_7_Day_Average": rolling_7_day_average,

        "Temperature": temperature,

        "Humidity": humidity,

        "Rainfall": rainfall,

        "Wind_Speed": wind_speed

    }])


    # ----------------------------------------------
    # Predict
    # ----------------------------------------------

    prediction = model.predict(input_data)[0]

    prediction = max(0, prediction)


    # ----------------------------------------------
    # Store prediction
    # ----------------------------------------------

    predictions.append({

        "Date": prediction_date.date(),

        "Predicted_Consumption_MU": round(
            prediction, 2
        ),

        "Temperature_C": round(
            temperature, 2
        ),

        "Humidity_%": round(
            humidity, 2
        ),

        "Rainfall_mm": round(
            rainfall, 2
        ),

        "Wind_Speed_kmh": round(
            wind_speed, 2
        )

    })


    # ----------------------------------------------
    # IMPORTANT:
    # Add today's prediction to history.
    #
    # This allows the next day's prediction
    # to use today's predicted consumption.
    # ----------------------------------------------

    current_history.append(prediction)


# --------------------------------------------------
# 8. DISPLAY RESULTS
# --------------------------------------------------

forecast_df = pd.DataFrame(predictions)

print("\n")
print("=" * 70)
print("7-DAY ELECTRICITY DEMAND FORECAST")
print("=" * 70)

print("\nState:", state)

print("\n")

print(
    forecast_df.to_string(index=False)
)

print("\n")
print("=" * 70)