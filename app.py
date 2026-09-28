import streamlit as st
import pandas as pd
import joblib
import requests


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Energy",
    page_icon="⚡",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("⚡ Smart Energy")
st.subheader("Electricity Demand Forecasting")

st.write(
    "Predict electricity demand using historical "
    "consumption data and weather information."
)


# =========================================================
# STATE COORDINATES
# =========================================================

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
    "Kerala": (8.5241, 76.9368),
    "MP": (23.2599, 77.4126),
    "Maharashtra": (19.0760, 72.8777),
    "Manipur": (24.8170, 93.9368),
    "Meghalaya": (25.5788, 91.8933),
    "Mizoram": (23.7271, 92.7177),
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


# =========================================================
# LOAD MODEL
# =========================================================

@st.cache_resource
def load_model():

    return joblib.load(
        "models/weather_energy_model.pkl"
    )


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    data = pd.read_csv(
        "data/smart_energy_dataset.csv"
    )

    data["Dates"] = pd.to_datetime(
        data["Dates"]
    )

    return data


# =========================================================
# LOAD RESOURCES
# =========================================================

try:

    model = load_model()
    df = load_data()

except Exception as e:

    st.error(
        f"Unable to load the model or dataset: {e}"
    )

    st.stop()


# =========================================================
# STATE SELECTION
# =========================================================

states = sorted(
    df["State"].unique()
)

state = st.selectbox(
    "Select State",
    states
)


# =========================================================
# PREDICTION BUTTON
# =========================================================

predict_button = st.button(
    "⚡ Predict Tomorrow's Demand",
    use_container_width=True
)


# =========================================================
# MAIN PREDICTION
# =========================================================

if predict_button:

    try:

        with st.spinner(
            "Collecting data and generating predictions..."
        ):

            # =================================================
            # PREDICTION DATE
            # =================================================

            prediction_date = (
                pd.Timestamp.today().normalize()
                + pd.Timedelta(days=1)
            )


            # =================================================
            # STATE DATA
            # =================================================

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

                st.error(
                    "Not enough historical data for this state."
                )

                st.stop()


            # =================================================
            # PREVIOUS DAY CONSUMPTION
            # =================================================

            previous_day = float(
                historical.iloc[-1]["Consumption"]
            )


            # =================================================
            # CONSUMPTION 7 DAYS AGO
            # =================================================

            seven_days_ago = (
                prediction_date
                - pd.Timedelta(days=7)
            )


            seven_day_record = state_data[
                state_data["Dates"] == seven_days_ago
            ]


            if len(seven_day_record) > 0:

                previous_7_day = float(
                    seven_day_record.iloc[0]["Consumption"]
                )

            else:

                previous_7_day = float(
                    historical.tail(7)["Consumption"].mean()
                )


            # =================================================
            # 7-DAY AVERAGE
            # =================================================

            rolling_average = float(
                historical.tail(7)["Consumption"].mean()
            )


            # =================================================
            # STATE CODE
            # =================================================

            state_mapping = {
                s: i
                for i, s in enumerate(states)
            }

            state_code = state_mapping[state]


            # =================================================
            # LOCATION
            # =================================================

            latitude, longitude = locations[state]


            # =================================================
            # OPEN-METEO API
            #
            # Today + next 7 days = 8 days
            # =================================================

            weather_url = (
                "https://api.open-meteo.com/v1/forecast"
            )


            weather_params = {

                "latitude": latitude,

                "longitude": longitude,

                "daily": (
                    "temperature_2m_mean,"
                    "relative_humidity_2m_mean,"
                    "precipitation_sum,"
                    "wind_speed_10m_mean"
                ),

                "forecast_days": 8,

                "timezone": "Asia/Kolkata"
            }


            response = requests.get(
                weather_url,
                params=weather_params,
                timeout=30
            )


            response.raise_for_status()


            weather_data = response.json()


            # =================================================
            # TOMORROW'S WEATHER
            # =================================================

            tomorrow_index = 1


            temperature = float(
                weather_data["daily"]
                ["temperature_2m_mean"]
                [tomorrow_index]
            )


            humidity = float(
                weather_data["daily"]
                ["relative_humidity_2m_mean"]
                [tomorrow_index]
            )


            rainfall = float(
                weather_data["daily"]
                ["precipitation_sum"]
                [tomorrow_index]
            )


            wind_speed = float(
                weather_data["daily"]
                ["wind_speed_10m_mean"]
                [tomorrow_index]
            )


            # =================================================
            # DATE FEATURES
            # =================================================

            year = prediction_date.year
            month = prediction_date.month
            day = prediction_date.day
            day_of_week = prediction_date.dayofweek


            # =================================================
            # MODEL INPUT
            # =================================================

            input_data = pd.DataFrame({

                "State_Code": [
                    state_code
                ],

                "Year": [
                    year
                ],

                "Month": [
                    month
                ],

                "Day": [
                    day
                ],

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


            # =================================================
            # TOMORROW'S PREDICTION
            # =================================================

            prediction = float(
                model.predict(input_data)[0]
            )

            prediction = max(
                0,
                prediction
            )


            # =================================================
            # 7-DAY ELECTRICITY DEMAND FORECAST
            # =================================================

            # Start with the latest 7 actual values
            forecast_history = list(
                historical.tail(7)["Consumption"].values
            )


            demand_predictions = []


            # -------------------------------------------------
            # Forecast next 7 days
            # -------------------------------------------------

            for i in range(1, 8):

                forecast_date = pd.to_datetime(
                    weather_data["daily"]["time"][i]
                )


                # ---------------------------------------------
                # LAG FEATURES
                # ---------------------------------------------

                previous_day_forecast = float(
                    forecast_history[-1]
                )


                previous_7_day_forecast = float(
                    forecast_history[-7]
                )


                rolling_7_day_average_forecast = float(
                    pd.Series(
                        forecast_history[-7:]
                    ).mean()
                )


                # ---------------------------------------------
                # WEATHER
                # ---------------------------------------------

                forecast_temperature = float(
                    weather_data["daily"]
                    ["temperature_2m_mean"][i]
                )


                forecast_humidity = float(
                    weather_data["daily"]
                    ["relative_humidity_2m_mean"][i]
                )


                forecast_rainfall = float(
                    weather_data["daily"]
                    ["precipitation_sum"][i]
                )


                forecast_wind_speed = float(
                    weather_data["daily"]
                    ["wind_speed_10m_mean"][i]
                )


                # ---------------------------------------------
                # DATE FEATURES
                # ---------------------------------------------

                forecast_year = forecast_date.year
                forecast_month = forecast_date.month
                forecast_day = forecast_date.day
                forecast_day_of_week = (
                    forecast_date.dayofweek
                )


                # ---------------------------------------------
                # MODEL INPUT
                # ---------------------------------------------

                forecast_input = pd.DataFrame({

                    "State_Code": [
                        state_code
                    ],

                    "Year": [
                        forecast_year
                    ],

                    "Month": [
                        forecast_month
                    ],

                    "Day": [
                        forecast_day
                    ],

                    "Day_of_Week": [
                        forecast_day_of_week
                    ],

                    "Previous_Day_Consumption": [
                        previous_day_forecast
                    ],

                    "Previous_7_Day_Consumption": [
                        previous_7_day_forecast
                    ],

                    "Rolling_7_Day_Average": [
                        rolling_7_day_average_forecast
                    ],

                    "Temperature": [
                        forecast_temperature
                    ],

                    "Humidity": [
                        forecast_humidity
                    ],

                    "Rainfall": [
                        forecast_rainfall
                    ],

                    "Wind_Speed": [
                        forecast_wind_speed
                    ]
                })


                # ---------------------------------------------
                # PREDICT
                # ---------------------------------------------

                demand_prediction = float(
                    model.predict(forecast_input)[0]
                )


                demand_prediction = max(
                    0,
                    demand_prediction
                )


                # ---------------------------------------------
                # STORE RESULT
                # ---------------------------------------------

                demand_predictions.append({

                    "Date": forecast_date.date(),

                    "Predicted Demand (MU)": round(
                        demand_prediction,
                        2
                    ),

                    "Temperature (°C)": round(
                        forecast_temperature,
                        1
                    ),

                    "Rainfall (mm)": round(
                        forecast_rainfall,
                        2
                    ),

                    "Humidity (%)": round(
                        forecast_humidity,
                        0
                    ),

                    "Wind Speed (km/h)": round(
                        forecast_wind_speed,
                        1
                    )
                })


                # ---------------------------------------------
                # RECURSIVE FORECASTING
                #
                # Today's prediction becomes historical
                # input for the next day's prediction.
                # ---------------------------------------------

                forecast_history.append(
                    demand_prediction
                )


            # =================================================
            # CREATE FORECAST DATAFRAME
            # =================================================

            demand_forecast_df = pd.DataFrame(
                demand_predictions
            )


        # =====================================================
        # SUCCESS MESSAGE
        # =====================================================

        st.success(
            "Prediction completed successfully!"
        )


        st.divider()


        # =====================================================
        # STATE / PREDICTION
        # =====================================================

        st.header(
            f"⚡ {state}"
        )


        st.write(
            f"Prediction date: "
            f"**{prediction_date.date()}**"
        )


        # =====================================================
        # TOMORROW'S DEMAND
        # =====================================================

        st.metric(
            "Predicted Electricity Demand",
            f"{prediction:.2f} MU"
        )


        st.divider()


        # =====================================================
        # TOMORROW'S WEATHER
        # =====================================================

        st.subheader(
            "🌦️ Tomorrow's Weather Forecast"
        )


        weather_col1, weather_col2, weather_col3, weather_col4 = (
            st.columns(4)
        )


        with weather_col1:

            st.metric(
                "Temperature",
                f"{temperature:.1f} °C"
            )


        with weather_col2:

            st.metric(
                "Humidity",
                f"{humidity:.0f}%"
            )


        with weather_col3:

            st.metric(
                "Rainfall",
                f"{rainfall:.2f} mm"
            )


        with weather_col4:

            st.metric(
                "Wind Speed",
                f"{wind_speed:.1f} km/h"
            )


        st.divider()


        # =====================================================
        # HISTORICAL DEMAND
        # =====================================================

        st.subheader(
            "📊 Historical Demand"
        )


        history_col1, history_col2 = (
            st.columns(2)
        )


        with history_col1:

            st.metric(
                "Previous Day",
                f"{previous_day:.2f} MU"
            )


        with history_col2:

            st.metric(
                "7-Day Average",
                f"{rolling_average:.2f} MU"
            )


        st.write(
            "Latest available historical electricity demand"
        )


        recent_history = (
            historical
            .tail(30)
            .copy()
        )


        recent_history = recent_history.set_index(
            "Dates"
        )


        st.line_chart(
            recent_history["Consumption"]
        )


        st.divider()


        # =====================================================
        # 7-DAY ELECTRICITY DEMAND FORECAST
        # =====================================================

        st.subheader(
            "📈 7-Day Electricity Demand Forecast"
        )


        st.write(
            "Forecast for the next 7 days using "
            "weather conditions and recursive lag features."
        )


        # Display forecast table

        st.dataframe(
            demand_forecast_df,
            use_container_width=True,
            hide_index=True
        )


        # =====================================================
        # 7-DAY DEMAND FORECAST CHART
        # =====================================================

        st.write(
            "📈 Predicted Electricity Demand"
        )


        chart_data = (
            demand_forecast_df
            .set_index("Date")
            ["Predicted Demand (MU)"]
        )


        st.line_chart(
            chart_data
        )


        st.divider()


        # =====================================================
        # 7-DAY WEATHER FORECAST
        # =====================================================

        st.subheader(
            "📅 7-Day Weather Forecast"
        )


        # Index 0 is today.
        # We only want the next 7 days: 1 to 7.

        weather_dates = weather_data[
            "daily"
        ]["time"][1:8]


        weather_forecast_df = pd.DataFrame({

            "Date": weather_dates,

            "Temperature": weather_data[
                "daily"
            ]["temperature_2m_mean"][1:8],

            "Rainfall": weather_data[
                "daily"
            ]["precipitation_sum"][1:8],

            "Humidity": weather_data[
                "daily"
            ]["relative_humidity_2m_mean"][1:8],

            "Wind Speed": weather_data[
                "daily"
            ]["wind_speed_10m_mean"][1:8]

        })


        st.dataframe(
            weather_forecast_df,
            use_container_width=True,
            hide_index=True
        )


        st.divider()


        # =====================================================
        # MODEL INFORMATION
        # =====================================================

        st.subheader(
            "🤖 Model Information"
        )


        st.write(
            "The prediction is generated using a "
            "weather-aware Random Forest regression model."
        )


        st.write(
            "The model uses historical electricity "
            "consumption, time features and weather "
            "variables such as temperature, humidity, "
            "rainfall and wind speed."
        )


        st.write(
            "For the 7-day forecast, predictions are "
            "generated recursively so that each predicted "
            "day can be used as an input for the following day."
        )


    # =========================================================
    # ERROR HANDLING
    # =========================================================

    except requests.exceptions.RequestException as e:

        st.error(
            f"Weather API request failed: {e}"
        )


    except Exception as e:

        st.error(
            f"Prediction failed: {e}"
        )