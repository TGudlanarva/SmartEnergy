import pandas as pd
import joblib


# ==========================================
# 1. Load trained model
# ==========================================

model = joblib.load(
    "models/weather_energy_model.pkl"
)


# ==========================================
# 2. User inputs
# ==========================================

state = input("Enter state: ")

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

previous_day = float(
    input("Enter previous day consumption (MU): ")
)

previous_7_day = float(
    input("Enter consumption 7 days ago (MU): ")
)

rolling_average = float(
    input("Enter 7-day average consumption (MU): ")
)

date = input(
    "Enter prediction date (YYYY-MM-DD): "
)


# ==========================================
# 3. Convert date
# ==========================================

date = pd.to_datetime(date)

year = date.year
month = date.month
day = date.day
day_of_week = date.dayofweek


# ==========================================
# 4. State encoding
# ==========================================

state_mapping = {
    "Andhra Pradesh": 0,
    "Arunachal Pradesh": 1,
    "Assam": 2,
    "Bihar": 3,
    "Chandigarh": 4,
    "Chhattisgarh": 5,
    "Delhi": 6,
    "Goa": 7,
    "Gujarat": 8,
    "HP": 9,
    "Haryana": 10,
    "J&K": 11,
    "Jharkhand": 12,
    "Karnataka": 13,
    "Kerala": 14,
    "MP": 15,
    "Maharashtra": 16,
    "Manipur": 17,
    "Meghalaya": 18,
    "Mizoram": 19,
    "Nagaland": 20,
    "Odisha": 21,
    "Pondy": 22,
    "Punjab": 23,
    "Rajasthan": 24,
    "Sikkim": 25,
    "Tamil Nadu": 26,
    "Telangana": 27,
    "Tripura": 28,
    "UP": 29,
    "Uttarakhand": 30,
    "West Bengal": 31
}


if state not in state_mapping:

    print("\nInvalid state name.")

    print("Available states:")

    for name in state_mapping:
        print("-", name)

    exit()


state_code = state_mapping[state]


# ==========================================
# 5. Create input dataframe
# ==========================================

input_data = pd.DataFrame({

    "State_Code": [state_code],

    "Year": [year],

    "Month": [month],

    "Day": [day],

    "Day_of_Week": [day_of_week],

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
# 6. Make prediction
# ==========================================

prediction = model.predict(input_data)


# ==========================================
# 7. Display result
# ==========================================

print("\n================================")
print("SMART ENERGY PREDICTION")
print("================================")

print("State:", state)

print(
    "Predicted electricity consumption:",
    round(prediction[0], 2),
    "MU"
)