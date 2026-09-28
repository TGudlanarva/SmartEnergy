import requests
import pandas as pd
import time


# ==========================================
# State + representative city coordinates
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
# Date range
# ==========================================

start_date = "20130106"
end_date = "20240929"


# ==========================================
# NASA POWER API
# ==========================================

url = "https://power.larc.nasa.gov/api/temporal/daily/point"


all_weather = []


# ==========================================
# Download weather
# ==========================================

for state, coordinates in locations.items():

    latitude, longitude = coordinates

    print(f"\nDownloading weather for {state}...")

    params = {
        "parameters": "T2M,RH2M,PRECTOTCORR,WS10M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        weather = data["properties"]["parameter"]

        weather_df = pd.DataFrame(weather)

        weather_df.index = pd.to_datetime(
            weather_df.index,
            format="%Y%m%d"
        )

        weather_df = weather_df.reset_index()

        weather_df = weather_df.rename(
            columns={
                "index": "Dates",
                "T2M": "Temperature",
                "RH2M": "Humidity",
                "PRECTOTCORR": "Rainfall",
                "WS10M": "Wind_Speed"
            }
        )

        weather_df["State"] = state

        weather_df = weather_df[
            [
                "Dates",
                "State",
                "Temperature",
                "Humidity",
                "Rainfall",
                "Wind_Speed"
            ]
        ]

        all_weather.append(weather_df)

        print(
            f"Downloaded {len(weather_df)} records"
        )

    except Exception as e:

        print(
            f"ERROR downloading {state}: {e}"
        )

    # Small delay between requests
    time.sleep(1)


# ==========================================
# Combine all states
# ==========================================

if all_weather:

    final_weather = pd.concat(
        all_weather,
        ignore_index=True
    )

    final_weather = final_weather.sort_values(
        ["State", "Dates"]
    )

    output_path = "data/all_states_weather.csv"

    final_weather.to_csv(
        output_path,
        index=False
    )

    print("\n================================")
    print("DOWNLOAD COMPLETED")
    print("================================")

    print("\nShape:")
    print(final_weather.shape)

    print("\nNumber of states:")
    print(final_weather["State"].nunique())

    print("\nSaved to:")
    print(output_path)

else:

    print("\nNo weather data was downloaded.")