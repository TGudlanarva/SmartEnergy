import React, { useEffect, useRef, useState } from "react"
import ModelPerformance from "./components/ModelPerformance"
import "./App.css"

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api"

const states = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chandigarh",
  "Chhattisgarh",
  "Delhi",
  "Goa",
  "Gujarat",
  "HP",
  "Haryana",
  "J&K",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "MP",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Pondy",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "UP",
  "Uttarakhand",
  "West Bengal",
]

function App() {
  const [state, setState] = useState("Telangana")
  const [search, setSearch] = useState("Telangana")
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const [prediction, setPrediction] = useState(null)
  const [forecast, setForecast] = useState([])

  const [loading, setLoading] = useState(false)
  const [forecastLoading, setForecastLoading] = useState(false)

  const [error, setError] = useState("")

  const dropdownRef = useRef(null)

  // --------------------------------------------------
  // Close dropdown when clicking outside
  // --------------------------------------------------

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target)
      ) {
        setDropdownOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)

    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  // --------------------------------------------------
  // Filter states
  // --------------------------------------------------

  const filteredStates = states.filter((item) =>
    item.toLowerCase().includes(search.toLowerCase())
  )

  // --------------------------------------------------
  // Select state
  // --------------------------------------------------

  const selectState = (selectedState) => {
    setState(selectedState)
    setSearch(selectedState)
    setDropdownOpen(false)

    setPrediction(null)
    setForecast([])
    setError("")
  }

  // --------------------------------------------------
  // Predict tomorrow
  // --------------------------------------------------

  const predictDemand = async () => {
    setLoading(true)
    setError("")
    setPrediction(null)

    try {
      const url =
        `${API_BASE_URL}/predict/${encodeURIComponent(state)}`

      console.log("PREDICTION REQUEST:", url)

      const response = await fetch(url)

      console.log("PREDICTION STATUS:", response.status)

      if (!response.ok) {
        const text = await response.text()
        throw new Error(
          text || `Server returned ${response.status}`
        )
      }

      const data = await response.json()

      console.log("PREDICTION DATA:", data)

      setPrediction(data)
    } catch (err) {
      console.error("PREDICTION ERROR:", err)

      setError(
        `Prediction Error: ${err.message}`
      )
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------
  // Get 7-day forecast
  // --------------------------------------------------

  const getForecast = async () => {
    setForecastLoading(true)
    setError("")
    setForecast([])

    try {
      const url =
        `${API_BASE_URL}/forecast/7-days/${encodeURIComponent(state)}`

      console.log("FORECAST REQUEST:", url)

      const response = await fetch(url)

      console.log("FORECAST STATUS:", response.status)

      if (!response.ok) {
        const text = await response.text()

        throw new Error(
          text || `Server returned ${response.status}`
        )
      }

      const data = await response.json()

      console.log("FORECAST DATA:", data)

      if (!data || !Array.isArray(data.forecast)) {
        throw new Error(
          "Invalid forecast received from backend."
        )
      }

      if (data.forecast.length === 0) {
        throw new Error(
          "No forecast data received."
        )
      }

      console.log(
        "7 FORECAST DAYS RECEIVED:",
        data.forecast
      )

      setForecast(data.forecast)
    } catch (err) {
      console.error("FORECAST ERROR:", err)

      setError(
        `Forecast Error: ${err.message}`
      )
    } finally {
      setForecastLoading(false)
    }
  }

  // --------------------------------------------------
  // Date formatting
  // --------------------------------------------------

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString(
      "en-IN",
      {
        day: "numeric",
        month: "short",
        year: "numeric",
      }
    )
  }

  // --------------------------------------------------
  // Number calculations
  // --------------------------------------------------

  const demandValues = forecast.map((day) =>
    Number(day.predicted_demand)
  )

  const averageDemand =
    demandValues.length > 0
      ? (
          demandValues.reduce(
            (sum, value) => sum + value,
            0
          ) / demandValues.length
        ).toFixed(2)
      : null

  const highestDemand =
    demandValues.length > 0
      ? Math.max(...demandValues).toFixed(2)
      : null

  const lowestDemand =
    demandValues.length > 0
      ? Math.min(...demandValues).toFixed(2)
      : null

  // --------------------------------------------------
  // Simple SVG chart
  // No Recharts
  // --------------------------------------------------

  const createChartPoints = () => {
    if (forecast.length === 0) {
      return ""
    }

    const width = 900
    const height = 320

    const paddingLeft = 70
    const paddingRight = 30
    const paddingTop = 30
    const paddingBottom = 55

    const chartWidth =
      width - paddingLeft - paddingRight

    const chartHeight =
      height - paddingTop - paddingBottom

    const values = forecast.map((item) =>
      Number(item.predicted_demand)
    )

    const minValue = Math.min(...values)
    const maxValue = Math.max(...values)

    const range =
      maxValue - minValue === 0
        ? 1
        : maxValue - minValue

    return values
      .map((value, index) => {
        const x =
          paddingLeft +
          (index *
            chartWidth) /
            Math.max(values.length - 1, 1)

        const y =
          paddingTop +
          chartHeight -
          ((value - minValue) / range) *
            chartHeight

        return `${x},${y}`
      })
      .join(" ")
  }

  const chartPoints = createChartPoints()

  // --------------------------------------------------
  // Main UI
  // --------------------------------------------------

  return (
    <div style={styles.app}>

      {/* HEADER */}

      <header style={styles.header}>
        <div>
          <div style={styles.logo}>
            ⚡ SmartEnergy
          </div>

          <div style={styles.headerSubtitle}>
            Electricity Demand Forecasting System
          </div>
        </div>

        <div style={styles.headerBadge}>
          AI + Weather
        </div>
      </header>

      <main style={styles.container}>

        {/* CONTROL CARD */}

        <section style={styles.controlCard}>

          <div style={styles.cardHeader}>
            <div>
              <h2 style={styles.cardTitle}>
                Electricity Demand Forecast
              </h2>

              <p style={styles.description}>
                Select a state to predict electricity
                demand using machine learning and
                weather data.
              </p>
            </div>
          </div>

          <label style={styles.label}>
            Select State
          </label>

          <div
            ref={dropdownRef}
            style={styles.dropdown}
          >

            <div style={styles.searchBox}>
              <input
                type="text"
                value={search}
                placeholder="Search state..."
                onFocus={() =>
                  setDropdownOpen(true)
                }
                onChange={(event) => {
                  setSearch(event.target.value)
                  setDropdownOpen(true)
                }}
                style={styles.searchInput}
              />

              <button
                type="button"
                onClick={() =>
                  setDropdownOpen(!dropdownOpen)
                }
                style={styles.arrowButton}
              >
                {dropdownOpen ? "▲" : "▼"}
              </button>
            </div>

            {dropdownOpen && (
              <div style={styles.options}>

                {filteredStates.length > 0 ? (
                  filteredStates.map((item) => (
                    <div
                      key={item}
                      onClick={() =>
                        selectState(item)
                      }
                      style={{
                        ...styles.option,
                        ...(item === state
                          ? styles.selectedOption
                          : {}),
                      }}
                    >
                      <span>{item}</span>

                      {item === state && (
                        <span>✓</span>
                      )}
                    </div>
                  ))
                ) : (
                  <div style={styles.noResults}>
                    No state found
                  </div>
                )}

              </div>
            )}

          </div>

          {/* BUTTONS */}

          <div style={styles.buttonRow}>

            <button
              onClick={predictDemand}
              disabled={loading}
              style={{
                ...styles.primaryButton,
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading
                ? "Predicting..."
                : "Predict Tomorrow"}
            </button>

            <button
              onClick={getForecast}
              disabled={forecastLoading}
              style={{
                ...styles.secondaryButton,
                opacity:
                  forecastLoading ? 0.7 : 1,
              }}
            >
              {forecastLoading
                ? "Loading Forecast..."
                : "View 7-Day Forecast"}
            </button>

          </div>

        </section>

        {/* ERROR */}

        {error && (
          <div style={styles.errorBox}>
            ⚠️ {error}
          </div>
        )}

        {/* TOMORROW PREDICTION */}

        {prediction && (
          <section style={styles.section}>

            <div style={styles.sectionHeader}>
              <div>
                <div style={styles.sectionTitle}>
                  Tomorrow's Demand
                </div>

                <div style={styles.sectionSubtitle}>
                  {prediction.prediction_date}
                </div>
              </div>

              <div style={styles.stateBadge}>
                {prediction.state}
              </div>
            </div>

            <div style={styles.mainDemandCard}>

              <div style={styles.smallLabel}>
                Predicted Electricity Demand
              </div>

              <div style={styles.bigNumber}>
                {Number(
                  prediction.predicted_demand
                ).toFixed(2)}

                <span style={styles.unit}>
                  {prediction.unit}
                </span>
              </div>

            </div>

            <h3 style={styles.subHeading}>
              Tomorrow's Weather
            </h3>

            <div style={styles.weatherGrid}>

              <WeatherCard
                icon="🌡️"
                title="Temperature"
                value={`${prediction.weather.temperature} °C`}
              />

              <WeatherCard
                icon="💧"
                title="Humidity"
                value={`${prediction.weather.humidity} %`}
              />

              <WeatherCard
                icon="🌧️"
                title="Rainfall"
                value={`${prediction.weather.rainfall} mm`}
              />

              <WeatherCard
                icon="💨"
                title="Wind Speed"
                value={`${prediction.weather.wind_speed} km/h`}
              />

            </div>

          </section>
        )}

        {/* 7 DAY FORECAST */}

        {forecast.length > 0 && (
          <section style={styles.section}>

            <div style={styles.sectionHeader}>
              <div>
                <div style={styles.sectionTitle}>
                  7-Day Demand Forecast
                </div>

                <div style={styles.sectionSubtitle}>
                  {state}
                </div>
              </div>

              <div style={styles.stateBadge}>
                7 DAYS
              </div>
            </div>

            {/* SUMMARY */}

            <div style={styles.summaryGrid}>

              <SummaryCard
                title="Average Demand"
                value={averageDemand}
              />

              <SummaryCard
                title="Highest Demand"
                value={highestDemand}
              />

              <SummaryCard
                title="Lowest Demand"
                value={lowestDemand}
              />

            </div>

            {/* CHART */}

            <div style={styles.chartCard}>

              <div style={styles.chartHeader}>
                <div>
                  <h3 style={styles.chartTitle}>
                    Electricity Demand Trend
                  </h3>

                  <p style={styles.description}>
                    Predicted electricity demand
                    for the next 7 days
                  </p>
                </div>

                <div style={styles.chartUnit}>
                  MU
                </div>
              </div>

              <div style={styles.chartWrapper}>

                <svg
                  viewBox="0 0 900 320"
                  width="100%"
                  height="320"
                  preserveAspectRatio="none"
                >

                  {/* Horizontal grid lines */}

                  <line
                    x1="70"
                    y1="30"
                    x2="870"
                    y2="30"
                    stroke="#e5e7eb"
                  />

                  <line
                    x1="70"
                    y1="110"
                    x2="870"
                    y2="110"
                    stroke="#e5e7eb"
                  />

                  <line
                    x1="70"
                    y1="190"
                    x2="870"
                    y2="190"
                    stroke="#e5e7eb"
                  />

                  <line
                    x1="70"
                    y1="265"
                    x2="870"
                    y2="265"
                    stroke="#e5e7eb"
                  />

                  {/* Axis */}

                  <line
                    x1="70"
                    y1="30"
                    x2="70"
                    y2="265"
                    stroke="#9ca3af"
                  />

                  <line
                    x1="70"
                    y1="265"
                    x2="870"
                    y2="265"
                    stroke="#9ca3af"
                  />

                  {/* Demand line */}

                  {chartPoints && (
                    <polyline
                      points={chartPoints}
                      fill="none"
                      stroke="#2563eb"
                      strokeWidth="4"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  )}

                  {/* Data points */}

                  {forecast.map((day, index) => {

                    const width = 900
                    const height = 320

                    const paddingLeft = 70
                    const paddingRight = 30
                    const paddingTop = 30
                    const paddingBottom = 55

                    const chartWidth =
                      width -
                      paddingLeft -
                      paddingRight

                    const chartHeight =
                      height -
                      paddingTop -
                      paddingBottom

                    const values =
                      forecast.map((item) =>
                        Number(
                          item.predicted_demand
                        )
                      )

                    const minValue =
                      Math.min(...values)

                    const maxValue =
                      Math.max(...values)

                    const range =
                      maxValue - minValue === 0
                        ? 1
                        : maxValue - minValue

                    const x =
                      paddingLeft +
                      (index * chartWidth) /
                        Math.max(
                          forecast.length - 1,
                          1
                        )

                    const y =
                      paddingTop +
                      chartHeight -
                      ((Number(
                        day.predicted_demand
                      ) -
                        minValue) /
                        range) *
                        chartHeight

                    return (
                      <g key={day.date}>

                        <circle
                          cx={x}
                          cy={y}
                          r="6"
                          fill="#2563eb"
                        />

                        <text
                          x={x}
                          y="292"
                          textAnchor="middle"
                          fontSize="13"
                          fill="#374151"
                        >
                          {index === 0
                            ? "Tomorrow"
                            : new Date(
                                day.date
                              ).toLocaleDateString(
                                "en-IN",
                                {
                                  day: "numeric",
                                  month: "short",
                                }
                              )}
                        </text>

                      </g>
                    )
                  })}

                </svg>

              </div>

            </div>

            {/* DAILY FORECAST */}

            <h3 style={styles.subHeading}>
              Daily Forecast
            </h3>

            <div style={styles.forecastGrid}>

              {forecast.map((day, index) => (
                <div
                  key={day.date}
                  style={styles.forecastCard}
                >

                  <div style={styles.forecastDate}>
                    {index === 0
                      ? "Tomorrow"
                      : formatDate(day.date)}
                  </div>

                  <div style={styles.forecastDemand}>
                    {Number(
                      day.predicted_demand
                    ).toFixed(2)}

                    <span style={styles.forecastUnit}>
                      MU
                    </span>
                  </div>

                  <div style={styles.forecastWeather}>
                    <div>
                      🌡️{" "}
                      {day.weather.temperature}
                      °C
                    </div>

                    <div>
                      💧{" "}
                      {day.weather.humidity}
                      %
                    </div>

                    <div>
                      🌧️{" "}
                      {day.weather.rainfall}
                      mm
                    </div>

                    <div>
                      💨{" "}
                      {day.weather.wind_speed}
                      km/h
                    </div>
                  </div>

                </div>
              ))}

            </div>

            {/* TABLE */}

            <h3 style={styles.subHeading}>
              Detailed Forecast
            </h3>

            <div style={styles.tableWrapper}>

              <table style={styles.table}>

                <thead>
                  <tr>

                    <th style={styles.th}>
                      Date
                    </th>

                    <th style={styles.th}>
                      Demand
                    </th>

                    <th style={styles.th}>
                      Temperature
                    </th>

                    <th style={styles.th}>
                      Humidity
                    </th>

                    <th style={styles.th}>
                      Rainfall
                    </th>

                    <th style={styles.th}>
                      Wind
                    </th>

                  </tr>
                </thead>

                <tbody>

                  {forecast.map((day) => (
                    <tr key={day.date}>

                      <td style={styles.td}>
                        {formatDate(day.date)}
                      </td>

                      <td style={styles.tdStrong}>
                        {Number(
                          day.predicted_demand
                        ).toFixed(2)}{" "}
                        MU
                      </td>

                      <td style={styles.td}>
                        {day.weather.temperature} °C
                      </td>

                      <td style={styles.td}>
                        {day.weather.humidity} %
                      </td>

                      <td style={styles.td}>
                        {day.weather.rainfall} mm
                      </td>

                      <td style={styles.td}>
                        {day.weather.wind_speed} km/h
                      </td>

                    </tr>
                  ))}

                </tbody>

              </table>

            </div>

          </section>
               )}

        {/* MODEL PERFORMANCE */}

        <ModelPerformance />

      </main>

      <footer style={styles.footer}>
        SmartEnergy • Machine Learning +
        Weather-Based Demand Forecasting
      </footer>

    </div>
  )
}

// --------------------------------------------------
// Weather Card
// --------------------------------------------------

function WeatherCard({
  icon,
  title,
  value,
}) {
  return (
    <div style={styles.weatherCard}>

      <div style={styles.weatherIcon}>
        {icon}
      </div>

      <div style={styles.weatherTitle}>
        {title}
      </div>

      <div style={styles.weatherValue}>
        {value}
      </div>

    </div>
  )
}

// --------------------------------------------------
// Summary Card
// --------------------------------------------------

function SummaryCard({
  title,
  value,
}) {
  return (
    <div style={styles.summaryCard}>

      <div style={styles.summaryTitle}>
        {title}
      </div>

      <div style={styles.summaryValue}>
        {value}
        <span style={styles.summaryUnit}>
          MU
        </span>
      </div>

    </div>
  )
}

// --------------------------------------------------
// Styles
// --------------------------------------------------

const styles = {
  app: {
    minHeight: "100vh",
    background:
      "linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%)",
    color: "#111827",
    fontFamily:
      "Inter, Arial, Helvetica, sans-serif",
  },

  header: {
    minHeight: "90px",
    padding: "0 7%",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    background: "#111827",
    color: "white",
    boxSizing: "border-box",
  },

  logo: {
    fontSize: "28px",
    fontWeight: "800",
    letterSpacing: "-0.5px",
  },

  headerSubtitle: {
    marginTop: "5px",
    color: "#cbd5e1",
    fontSize: "14px",
  },

  headerBadge: {
    background: "#2563eb",
    padding: "9px 15px",
    borderRadius: "999px",
    fontSize: "13px",
    fontWeight: "700",
  },

  container: {
    width: "min(1180px, 92%)",
    margin: "0 auto",
    padding: "35px 0 60px",
  },

  controlCard: {
    background: "white",
    borderRadius: "20px",
    padding: "30px",
    boxShadow:
      "0 15px 45px rgba(15, 23, 42, 0.08)",
    border: "1px solid #e5e7eb",
  },

  cardHeader: {
    marginBottom: "25px",
  },

  cardTitle: {
    margin: "0",
    fontSize: "25px",
    fontWeight: "800",
  },

  description: {
    margin: "7px 0 0",
    color: "#64748b",
    fontSize: "14px",
    lineHeight: "1.6",
  },

  label: {
    display: "block",
    marginBottom: "8px",
    fontSize: "14px",
    fontWeight: "700",
    color: "#374151",
  },

  dropdown: {
    position: "relative",
    maxWidth: "500px",
  },

  searchBox: {
    display: "flex",
    alignItems: "center",
    border: "1px solid #cbd5e1",
    borderRadius: "12px",
    overflow: "hidden",
    background: "white",
  },

  searchInput: {
    width: "100%",
    padding: "14px",
    border: "none",
    outline: "none",
    fontSize: "15px",
    boxSizing: "border-box",
  },

  arrowButton: {
    border: "none",
    background: "white",
    padding: "0 15px",
    cursor: "pointer",
    color: "#475569",
  },

  options: {
    position: "absolute",
    zIndex: 100,
    width: "100%",
    maxHeight: "260px",
    overflowY: "auto",
    marginTop: "5px",
    background: "white",
    border: "1px solid #cbd5e1",
    borderRadius: "12px",
    boxShadow:
      "0 15px 30px rgba(0,0,0,0.12)",
  },

  option: {
    padding: "12px 15px",
    display: "flex",
    justifyContent: "space-between",
    cursor: "pointer",
    fontSize: "14px",
  },

  selectedOption: {
    background: "#eff6ff",
    color: "#2563eb",
    fontWeight: "700",
  },

  noResults: {
    padding: "15px",
    color: "#64748b",
  },

  buttonRow: {
    display: "flex",
    gap: "12px",
    marginTop: "25px",
    flexWrap: "wrap",
  },

  primaryButton: {
    border: "none",
    borderRadius: "12px",
    padding: "14px 22px",
    background: "#2563eb",
    color: "white",
    fontWeight: "700",
    fontSize: "14px",
    cursor: "pointer",
  },

  secondaryButton: {
    border: "1px solid #2563eb",
    borderRadius: "12px",
    padding: "14px 22px",
    background: "white",
    color: "#2563eb",
    fontWeight: "700",
    fontSize: "14px",
    cursor: "pointer",
  },

  errorBox: {
    marginTop: "20px",
    padding: "15px 18px",
    background: "#fef2f2",
    color: "#b91c1c",
    border: "1px solid #fecaca",
    borderRadius: "12px",
    fontWeight: "600",
  },

  section: {
    marginTop: "30px",
    background: "white",
    borderRadius: "20px",
    padding: "30px",
    boxShadow:
      "0 15px 45px rgba(15, 23, 42, 0.07)",
    border: "1px solid #e5e7eb",
  },

  sectionHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "20px",
    marginBottom: "25px",
  },

  sectionTitle: {
    fontSize: "24px",
    fontWeight: "800",
  },

  sectionSubtitle: {
    marginTop: "5px",
    color: "#64748b",
    fontSize: "14px",
  },

  stateBadge: {
    background: "#eff6ff",
    color: "#2563eb",
    padding: "8px 14px",
    borderRadius: "999px",
    fontSize: "12px",
    fontWeight: "800",
  },

  mainDemandCard: {
    padding: "30px",
    borderRadius: "18px",
    background:
      "linear-gradient(135deg, #1d4ed8, #2563eb)",
    color: "white",
    boxShadow:
      "0 15px 30px rgba(37, 99, 235, 0.25)",
  },

  smallLabel: {
    fontSize: "14px",
    opacity: 0.85,
  },

  bigNumber: {
    marginTop: "10px",
    fontSize: "48px",
    fontWeight: "900",
    letterSpacing: "-2px",
  },

  unit: {
    marginLeft: "10px",
    fontSize: "20px",
    fontWeight: "600",
  },

  subHeading: {
    marginTop: "30px",
    marginBottom: "16px",
    fontSize: "19px",
    fontWeight: "800",
  },

  weatherGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(190px, 1fr))",
    gap: "15px",
  },

  weatherCard: {
    padding: "20px",
    borderRadius: "16px",
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
  },

  weatherIcon: {
    fontSize: "28px",
  },

  weatherTitle: {
    marginTop: "12px",
    color: "#64748b",
    fontSize: "13px",
    fontWeight: "600",
  },

  weatherValue: {
    marginTop: "5px",
    fontSize: "20px",
    fontWeight: "800",
  },

  summaryGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "15px",
  },

  summaryCard: {
    padding: "22px",
    borderRadius: "16px",
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
  },

  summaryTitle: {
    color: "#64748b",
    fontSize: "13px",
    fontWeight: "600",
  },

  summaryValue: {
    marginTop: "8px",
    fontSize: "28px",
    fontWeight: "900",
    color: "#111827",
  },

  summaryUnit: {
    marginLeft: "6px",
    fontSize: "13px",
    color: "#64748b",
    fontWeight: "600",
  },

  chartCard: {
    marginTop: "25px",
    border: "1px solid #e2e8f0",
    borderRadius: "18px",
    overflow: "hidden",
  },

  chartHeader: {
    padding: "20px 22px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    borderBottom: "1px solid #e2e8f0",
  },

  chartTitle: {
    margin: 0,
    fontSize: "18px",
    fontWeight: "800",
  },

  chartUnit: {
    background: "#eff6ff",
    color: "#2563eb",
    fontWeight: "800",
    padding: "8px 12px",
    borderRadius: "8px",
  },

  chartWrapper: {
    width: "100%",
    overflowX: "auto",
    padding: "20px",
    boxSizing: "border-box",
  },

  forecastGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "15px",
  },

  forecastCard: {
    padding: "20px",
    borderRadius: "16px",
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    boxShadow:
      "0 5px 15px rgba(15, 23, 42, 0.04)",
  },

  forecastDate: {
    fontSize: "13px",
    color: "#64748b",
    fontWeight: "700",
  },

  forecastDemand: {
    marginTop: "12px",
    fontSize: "28px",
    fontWeight: "900",
    color: "#2563eb",
  },

  forecastUnit: {
    marginLeft: "5px",
    fontSize: "12px",
    color: "#64748b",
  },

  forecastWeather: {
    marginTop: "15px",
    display: "grid",
    gap: "7px",
    fontSize: "13px",
    color: "#475569",
  },

  tableWrapper: {
    overflowX: "auto",
    border:
      "1px solid #e2e8f0",
    borderRadius: "14px",
  },

  table: {
    width: "100%",
    borderCollapse: "collapse",
    minWidth: "750px",
  },

  th: {
    padding: "14px",
    background: "#f8fafc",
    color: "#475569",
    fontSize: "12px",
    textAlign: "left",
    borderBottom:
      "1px solid #e2e8f0",
  },

  td: {
    padding: "14px",
    fontSize: "13px",
    borderBottom:
      "1px solid #f1f5f9",
    color: "#475569",
  },

  tdStrong: {
    padding: "14px",
    fontSize: "13px",
    borderBottom:
      "1px solid #f1f5f9",
    color: "#111827",
    fontWeight: "800",
  },

  footer: {
    textAlign: "center",
    padding: "25px",
    color: "#64748b",
    fontSize: "13px",
  },
}

export default App