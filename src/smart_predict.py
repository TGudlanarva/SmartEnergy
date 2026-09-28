import pandas as pd
import joblib
import requests


# ==========================================
# 1. State coordinates
# ==========================================

locations = {
    "Andhra Pradesh": (16.5062, 80.6480),
    "Arunachal Pradesh": (27.0844, 93.6053),
    "Assam": (26.1445, 91.7362),
    "Bihar": (25.5941, 85.1376),
    "Chandigarh": (30.7333, 76.7794),
    "Chhattisgarh": (21.2514, 81.6296),
    "Delhi": (28.6139, 77.2090),
    "Goa": (15.4909, 73.8278),
    "Gujarat": (23.0225, 72.5714),
    "HP": (31.1048, 77.1734),
    "Haryana": (30.3782, 76.7767),
    "J&K": (34.0837, 74.7973),
    "Jharkhand": (23.3441, 85.3096),
    "Karnataka": (12.9716, 77.5946),
    "Kerala": (8.5241, 76.9366),
    "MP": (23.2599, 77.4126),
    "Maharashtra": (19.0760, 72.8777),
    "Manipur": (24.8170, 93.9368),
    "Meghalaya": (25.5788, 91.8933),
    "Mizoram": (23.7271, 92.7176),
    "Nagaland": (25.6751, 94.1086),
    "Odisha": (20.2961, 85.8245),
    "Pondy": (11.9416, 79.8083),
    "Punjab": (30.9010, 75.8573),
    "Rajasthan": (26.9124, 75.7873),
    "Sikkim": (27.3389, 88.6065),
    "Tamil Nadu": (13.0827, 80.2707),
    "Telangana": (17.3850, 78.4867),
    "Tripura": (23.8315, 91.2868),
    "UP": (26.8467, 80.9462),
    "Uttarakhand": (30.3165, 78.0322),
    "West Bengal": (22.5726, 88.3639)
}


# ==========================================
# 2. Load trained model
# ==========================================

model = joblib.load(
    "models/weather_energy_model.pkl"
)


# ==========================================
# 3. Load electricity data
# ==========================================

df = pd.read_csv(
    "data/smart_energy_dataset.csv"
)

df["Dates"] = pd.to_datetime(
    df["Dates"]
)


# ==========================================
# 4. State mapping
# ==========================================

states = sorted(
    df["State"].unique()
)

state_mapping = {
    state: code
    for code, state in enumerate(states)
}


# ==========================================
# 5. Select state
# ==========================================

print("\nAvailable states:\n")

for state in states:
    print("-", state)

state = input(
    "\nEnter state: "
).strip()


if state not in locations:

    print("\nInvalid state name.")

    exit()


# ==========================================
# 6. Tomorrow's date
# ==========================================

prediction_date = (
    pd.Timestamp.today().normalize()
    + pd.Timedelta(days=1)
)

print(
    "\nPrediction date:",
    prediction_date.date()
)


# ==========================================
# 7. Historical electricity
# ==========================================

state_data = df[
    df["State"] == state
].copy()

state_data = state_data.sort_values(
    "Dates"
)

historical = state_data[
    state_data["Dates"] < prediction_date
]


if len(historical) < 7:

    print(
        "Not enough historical data."
    )

    exit()


# ==========================================
# 8. Previous day consumption
# ==========================================

previous_day = (
    historical.iloc[-1]["Consumption"]
)


# ==========================================
# 9. Consumption 7 days ago
# ==========================================

seven_days_ago = (
    prediction_date -
    pd.Timedelta(days=7)
)

seven_day_record = state_data[
    state_data["Dates"] == seven_days_ago
]


if len(seven_day_record) > 0:

    previous_7_day = (
        seven_day_record.iloc[0]
        ["Consumption"]
    )

else:

    previous_7_day = (
        historical.tail(7)
        ["Consumption"]
        .mean()
    )


# ==========================================
# 10. Seven-day average
# ==========================================

rolling_average = (
    historical.tail(7)
    ["Consumption"]
    .mean()
)


# ==========================================
# 11. Get state coordinates
# ==========================================

latitude, longitude = locations[state]


# ==========================================
# 12. Get tomorrow's weather
# ==========================================

print(
    "\nGetting tomorrow's weather..."
)

weather_url = (
    "https://api.open-meteo.com/v1/forecast"
)

params = {

    "latitude": latitude,

    "longitude": longitude,

    "daily": (
        "temperature_2m_mean,"
        "relative_humidity_2m_mean,"
        "precipitation_sum,"
        "wind_speed_10m_mean"
    ),

    "forecast_days": 2,

    "timezone": "Asia/Kolkata"
}


response = requests.get(
    weather_url,
    params=params,
    timeout=30
)

response.raise_for_status()

weather_data = response.json()

tomorrow = 1


weather_date = (
    weather_data["daily"]["time"]
    [tomorrow]
)

temperature = (
    weather_data["daily"]
    ["temperature_2m_mean"]
    [tomorrow]
)

humidity = (
    weather_data["daily"]
    ["relative_humidity_2m_mean"]
    [tomorrow]
)

rainfall = (
    weather_data["daily"]
    ["precipitation_sum"]
    [tomorrow]
)

wind_speed = (
    weather_data["daily"]
    ["wind_speed_10m_mean"]
    [tomorrow]
)


# ==========================================
# 13. Date features
# ==========================================

year = prediction_date.year

month = prediction_date.month

day = prediction_date.day

day_of_week = (
    prediction_date.dayofweek
)


# ==========================================
# 14. Create model input
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
# 15. Make prediction
# ==========================================

prediction = model.predict(
    input_data
)


# ==========================================
# 16. Display result
# ==========================================

print("\n================================")
print("       SMART ENERGY")
print("   DEMAND PREDICTION")
print("================================")

print(
    "\nState:",
    state
)

print(
    "Prediction date:",
    weather_date
)

print("\nTomorrow's weather:")

print(
    "Temperature:",
    temperature,
    "°C"
)

print(
    "Humidity:",
    humidity,
    "%"
)

print(
    "Rainfall:",
    rainfall,
    "mm"
)

print(
    "Wind speed:",
    wind_speed,
    "km/h"
)

print("\nHistorical demand:")

print(
    "Previous day:",
    round(previous_day, 2),
    "MU"
)

print(
    "7-day average:",
    round(rolling_average, 2),
    "MU"
)

print(
    "\n⚡ PREDICTED ELECTRICITY DEMAND:"
)

print(
    round(prediction[0], 2),
    "MU"
)

print("\n================================")