from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import requests


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "weather_energy_model_free.pkl"

DATA_PATH = BASE_DIR / "data" / "smart_energy_dataset.csv"


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="SmartEnergy API",
    description="Electricity Demand Forecasting API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# STATE COORDINATES
# =========================================================

STATE_COORDINATES = {

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

    "Haryana": (29.0588, 76.0856),

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

    "Uttarakhand": (30.0668, 79.0193),

    "West Bengal": (22.5726, 88.3639)
}


# =========================================================
# LOAD MODEL
# =========================================================

model_load_error = None

try:

    model = joblib.load(MODEL_PATH)

    print("Model loaded successfully.")

except Exception as e:

    model = None
    model_load_error = str(e)

    print("Model loading error:", e)


# =========================================================
# LOAD DATA
# =========================================================

try:

    df = pd.read_csv(DATA_PATH)

    df["Dates"] = pd.to_datetime(df["Dates"])

    print("Dataset loaded successfully.")

    print("Dataset shape:", df.shape)

except Exception as e:

    df = None

    print("Dataset loading error:", e)

# =========================================================
# STATE CODE MAPPING
# =========================================================

if df is not None and "State" in df.columns:

    state_list = sorted(
        df["State"].dropna().unique()
    )

    STATE_CODES = {
        state: index
        for index, state in enumerate(state_list)
    }

else:

    STATE_CODES = {}


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def home():

    return {
        "message": "SmartEnergy API is running!"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# STATES
# =========================================================

@app.get("/states")
def get_states():

    return {
        "states": sorted(
            list(STATE_CODES.keys())
        )
    }


# =========================================================
# GET WEATHER
# =========================================================

def get_weather(
    latitude,
    longitude,
    start_date,
    end_date
):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": ",".join([
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "precipitation_sum",
            "wind_speed_10m_mean"
        ]),

        "start_date": start_date,

        "end_date": end_date,

        "timezone": "auto"

    }


    response = requests.get(
        url,
        params=params,
        timeout=30
    )


    response.raise_for_status()


    return response.json()


# =========================================================
# PREDICT TOMORROW
# =========================================================

@app.get("/predict/{state}")
@app.get("/api/predict/{state}")
def predict_tomorrow(state: str):

    if model is None:

        raise HTTPException(
            status_code=500,
            detail=f"ML model could not be loaded: {model_load_error}"
        )


    if df is None:

        raise HTTPException(
            status_code=500,
            detail="Dataset could not be loaded."
        )


    if state not in STATE_CODES:

        raise HTTPException(
            status_code=404,
            detail=f"State '{state}' not found."
        )


    if state not in STATE_COORDINATES:

        raise HTTPException(
            status_code=404,
            detail=f"Coordinates not available for {state}."
        )


    # -----------------------------------------------------
    # STATE HISTORY
    # -----------------------------------------------------

    state_data = (
        df[df["State"] == state]
        .sort_values("Dates")
        .copy()
    )


    if len(state_data) < 8:

        raise HTTPException(
            status_code=400,
            detail="Not enough historical data."
        )


    # -----------------------------------------------------
    # HISTORICAL VALUES
    # -----------------------------------------------------

    previous_day = float(
        state_data.iloc[-1]["Consumption"]
    )


    previous_7_day = float(
        state_data.iloc[-8]["Consumption"]
    )


    rolling_average = float(
        state_data.iloc[-7:]["Consumption"].mean()
    )


    # -----------------------------------------------------
    # TOMORROW
    # -----------------------------------------------------

    prediction_date = (
        pd.Timestamp.now().normalize()
        + pd.Timedelta(days=1)
    )


    latitude, longitude = STATE_COORDINATES[state]


    weather_data = get_weather(

        latitude,

        longitude,

        prediction_date.strftime("%Y-%m-%d"),

        prediction_date.strftime("%Y-%m-%d")

    )


    daily = weather_data["daily"]


    temperature = float(
        daily["temperature_2m_mean"][0]
    )


    humidity = float(
        daily["relative_humidity_2m_mean"][0]
    )


    rainfall = float(
        daily["precipitation_sum"][0]
    )


    wind_speed = float(
        daily["wind_speed_10m_mean"][0]
    )


    # -----------------------------------------------------
    # MODEL INPUT
    # -----------------------------------------------------

    input_data = pd.DataFrame([{

        "State_Code":
            STATE_CODES[state],

        "Year":
            prediction_date.year,

        "Month":
            prediction_date.month,

        "Day":
            prediction_date.day,

        "Day_of_Week":
            prediction_date.dayofweek,

        "Previous_Day_Consumption":
            previous_day,

        "Previous_7_Day_Consumption":
            previous_7_day,

        "Rolling_7_Day_Average":
            rolling_average,

        "Temperature":
            temperature,

        "Humidity":
            humidity,

        "Rainfall":
            rainfall,

        "Wind_Speed":
            wind_speed

    }])


    prediction = float(
        model.predict(input_data)[0]
    )


    return {

        "state": state,

        "prediction_date":
            prediction_date.strftime("%Y-%m-%d"),

        "predicted_demand":
            round(prediction, 2),

        "unit": "MU",

        "weather": {

            "temperature":
                round(temperature, 1),

            "humidity":
                round(humidity, 1),

            "rainfall":
                round(rainfall, 1),

            "wind_speed":
                round(wind_speed, 1)

        }

    }


# =========================================================
# 7-DAY FORECAST
# =========================================================

@app.get("/forecast/7-days/{state}")
@app.get("/api/forecast/7-days/{state}")
def forecast_seven_days(state: str):

    if model is None:

        raise HTTPException(
            status_code=500,
            detail="ML model could not be loaded."
        )


    if df is None:

        raise HTTPException(
            status_code=500,
            detail="Dataset could not be loaded."
        )


    if state not in STATE_CODES:

        raise HTTPException(
            status_code=404,
            detail=f"State '{state}' not found."
        )


    if state not in STATE_COORDINATES:

        raise HTTPException(
            status_code=404,
            detail=f"Coordinates not available for {state}."
        )


    # -----------------------------------------------------
    # STATE HISTORY
    # -----------------------------------------------------

    state_data = (
        df[df["State"] == state]
        .sort_values("Dates")
        .copy()
    )


    if len(state_data) < 8:

        raise HTTPException(
            status_code=400,
            detail="Not enough historical data."
        )


    # -----------------------------------------------------
    # LATEST HISTORICAL VALUES
    # -----------------------------------------------------

    consumption_history = (
        state_data["Consumption"]
        .astype(float)
        .tolist()
    )


    latest_historical_date = (
        state_data["Dates"].max()
    )


    # -----------------------------------------------------
    # FORECAST DATES
    # -----------------------------------------------------

    start_date = (
        pd.Timestamp.now().normalize()
        + pd.Timedelta(days=1)
    )


    end_date = (
        start_date
        + pd.Timedelta(days=6)
    )


    # -----------------------------------------------------
    # GET 7 DAYS WEATHER
    # -----------------------------------------------------

    latitude, longitude = STATE_COORDINATES[state]


    try:

        weather_data = get_weather(

            latitude,

            longitude,

            start_date.strftime("%Y-%m-%d"),

            end_date.strftime("%Y-%m-%d")

        )

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=f"Weather API error: {str(e)}"
        )


    daily = weather_data.get("daily")


    if daily is None:

        raise HTTPException(
            status_code=502,
            detail="Weather API returned no daily data."
        )


    # -----------------------------------------------------
    # CHECK WEATHER DATA
    # -----------------------------------------------------

    dates = daily.get("time", [])

    temperatures = daily.get(
        "temperature_2m_mean",
        []
    )

    humidities = daily.get(
        "relative_humidity_2m_mean",
        []
    )

    rainfalls = daily.get(
        "precipitation_sum",
        []
    )

    wind_speeds = daily.get(
        "wind_speed_10m_mean",
        []
    )


    if len(dates) < 7:

        raise HTTPException(
            status_code=502,
            detail="Weather API did not return 7 days of data."
        )


    # -----------------------------------------------------
    # RECURSIVE FORECAST
    # -----------------------------------------------------

    forecast = []


    simulated_history = (
        consumption_history.copy()
    )


    for i in range(7):

        forecast_date = (
            start_date
            + pd.Timedelta(days=i)
        )


        # -----------------------------------------------
        # LAG FEATURES
        # -----------------------------------------------

        previous_day = float(
            simulated_history[-1]
        )


        previous_7_day = float(
            simulated_history[-8]
        )


        rolling_average = float(
            sum(
                simulated_history[-7:]
            ) / 7
        )


        # -----------------------------------------------
        # WEATHER
        # -----------------------------------------------

        temperature = float(
            temperatures[i]
        )


        humidity = float(
            humidities[i]
        )


        rainfall = float(
            rainfalls[i]
        )


        wind_speed = float(
            wind_speeds[i]
        )


        # -----------------------------------------------
        # MODEL INPUT
        # -----------------------------------------------

        input_data = pd.DataFrame([{

            "State_Code":
                STATE_CODES[state],

            "Year":
                forecast_date.year,

            "Month":
                forecast_date.month,

            "Day":
                forecast_date.day,

            "Day_of_Week":
                forecast_date.dayofweek,

            "Previous_Day_Consumption":
                previous_day,

            "Previous_7_Day_Consumption":
                previous_7_day,

            "Rolling_7_Day_Average":
                rolling_average,

            "Temperature":
                temperature,

            "Humidity":
                humidity,

            "Rainfall":
                rainfall,

            "Wind_Speed":
                wind_speed

        }])


        # -----------------------------------------------
        # PREDICT
        # -----------------------------------------------

        predicted_demand = float(
            model.predict(input_data)[0]
        )


        predicted_demand = round(
            predicted_demand,
            2
        )


        # -----------------------------------------------
        # SAVE RESULT
        # -----------------------------------------------

        forecast.append({

            "date":
                forecast_date.strftime(
                    "%Y-%m-%d"
                ),

            "predicted_demand":
                predicted_demand,

            "unit":
                "MU",

            "weather": {

                "temperature":
                    round(
                        temperature,
                        1
                    ),

                "humidity":
                    round(
                        humidity,
                        1
                    ),

                "rainfall":
                    round(
                        rainfall,
                        1
                    ),

                "wind_speed":
                    round(
                        wind_speed,
                        1
                    )

            }

        })


        # -----------------------------------------------
        # IMPORTANT:
        # ADD PREDICTION TO HISTORY
        # -----------------------------------------------

        simulated_history.append(
            predicted_demand
        )


    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return {

        "state":
            state,

        "latest_historical_date":
            latest_historical_date.strftime(
                "%Y-%m-%d"
            ),

        "forecast_days":
            7,

        "forecast":
            forecast

    }
@app.get("/model-performance")
@app.get("/api/model-performance")
def model_performance():
    return {
        "models": [
            {
                "name": "Baseline Random Forest",
                "mae": 5.1145,
                "rmse": 10.1506,
                "r2": 0.99556
            },
            {
                "name": "Weather-Aware Random Forest",
                "mae": 4.8262,
                "rmse": 9.6026,
                "r2": 0.99603
            }
        ]
    }