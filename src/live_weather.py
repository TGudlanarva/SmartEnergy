import requests


# Hyderabad coordinates
latitude = 17.3850
longitude = 78.4867


# Open-Meteo forecast API
url = "https://api.open-meteo.com/v1/forecast"


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


print("Getting tomorrow's weather forecast...")


response = requests.get(
    url,
    params=params,
    timeout=30
)

response.raise_for_status()

data = response.json()


# Tomorrow is index 1
tomorrow = 1

date = data["daily"]["time"][tomorrow]

temperature = data["daily"][
    "temperature_2m_mean"
][tomorrow]

humidity = data["daily"][
    "relative_humidity_2m_mean"
][tomorrow]

rainfall = data["daily"][
    "precipitation_sum"
][tomorrow]

wind_speed = data["daily"][
    "wind_speed_10m_mean"
][tomorrow]


print("\n===== TOMORROW'S WEATHER =====")

print("Date:", date)

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
    "Wind Speed:",
    wind_speed,
    "km/h"
)