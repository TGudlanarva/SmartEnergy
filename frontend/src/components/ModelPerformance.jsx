import React, { useEffect, useState } from "react"

function BarGraph({
  title,
  values,
  maxValue,
  suffix = "",
  decimals = 2,
}) {
  return (
    <div style={styles.graphCard}>
      <h3 style={styles.graphTitle}>{title}</h3>

      <div style={styles.graphArea}>
        {values.map((item) => {
          const height =
            (item.value / maxValue) * 180

          return (
            <div
              key={item.label}
              style={styles.barColumn}
            >
              <div style={styles.valueLabel}>
  {item.value < 1 ? item.value.toFixed(5) : item.value.toFixed(decimals)}
  {suffix}
 </div>

              <div style={styles.barWrapper}>
                <div
                  style={{
                    ...styles.bar,
                    height: `${height}px`,
                  }}
                />
              </div>

              <div style={styles.barLabel}>
                {item.label}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function ModelPerformance() {
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const fetchModelPerformance = async () => {
      try {
        setLoading(true)
        setError("")

        console.log(
          "MODEL PERFORMANCE REQUEST: /api/model-performance"
        )

       const API_BASE_URL = "/api"
const response = await fetch(
  `${API_BASE_URL}/model-performance`
)

        console.log(
          "MODEL PERFORMANCE STATUS:",
          response.status
        )

        if (!response.ok) {
          const text = await response.text()

          throw new Error(
            text ||
              `Server returned ${response.status}`
          )
        }

        const data = await response.json()

        console.log(
          "MODEL PERFORMANCE DATA:",
          data
        )

        if (
          !data ||
          !Array.isArray(data.models)
        ) {
          throw new Error(
            "Invalid model performance data received."
          )
        }

        if (data.models.length < 2) {
          throw new Error(
            "Insufficient model performance data received."
          )
        }

        setModels(data.models)
      } catch (err) {
        console.error(
          "MODEL PERFORMANCE ERROR:",
          err
        )

        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchModelPerformance()
  }, [])

  // --------------------------------------------------
  // Loading
  // --------------------------------------------------

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingCard}>
          <div style={styles.loadingIcon}>
            ⚙️
          </div>

          <h2 style={styles.loadingTitle}>
            Loading Model Performance
          </h2>

          <p style={styles.loadingText}>
            Fetching model evaluation results from
            the SmartEnergy API...
          </p>
        </div>
      </div>
    )
  }

  // --------------------------------------------------
  // Error
  // --------------------------------------------------

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.errorCard}>
          <div style={styles.errorIcon}>
            ⚠️
          </div>

          <div>
            <h2 style={styles.errorTitle}>
              Unable to Load Model Performance
            </h2>

            <p style={styles.errorText}>
              {error}
            </p>

            <p style={styles.errorHint}>
              Make sure the FastAPI backend is
              running on port 8000.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // --------------------------------------------------
  // Model data
  // --------------------------------------------------

  const baseline = models.find(
    (model) =>
      model.name ===
      "Baseline Random Forest"
  ) || models[0]

  const weatherAware =
    models.find(
      (model) =>
        model.name ===
        "Weather-Aware Random Forest"
    ) || models[1]

  // --------------------------------------------------
  // Improvements
  // --------------------------------------------------

  const maeImprovement =
    ((baseline.mae -
      weatherAware.mae) /
      baseline.mae) *
    100

  const rmseImprovement =
    ((baseline.rmse -
      weatherAware.rmse) /
      baseline.rmse) *
    100

  const r2Improvement =
    ((weatherAware.r2 -
      baseline.r2) /
      baseline.r2) *
    100

  return (
    <div style={styles.container}>

      {/* ==================================================
          HEADER
      ================================================== */}

      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>
            Model Performance
          </h2>

          <p style={styles.subtitle}>
            Comparison of the baseline and
            weather-aware Random Forest models
          </p>
        </div>

        <div style={styles.badge}>
          ✓ Weather-Aware Model
        </div>
      </div>


      {/* ==================================================
          API STATUS
      ================================================== */}

      <div style={styles.apiStatus}>
        <span style={styles.apiDot}></span>

        <span>
          Model metrics loaded from FastAPI
        </span>
      </div>


      {/* ==================================================
          METRIC CARDS
      ================================================== */}

      <div style={styles.metricsGrid}>

        {/* MAE */}

        <div style={styles.metricCard}>
          <div style={styles.metricTitle}>
            MAE
          </div>

          <div style={styles.metricValues}>
            <span>
              {baseline.mae.toFixed(4)}
            </span>

            <span>
              →
            </span>

            <strong>
              {weatherAware.mae.toFixed(4)}
            </strong>
          </div>

          <div style={styles.improvement}>
            ↓ {maeImprovement.toFixed(2)}%
            improvement
          </div>

          <p style={styles.metricDescription}>
            Mean Absolute Error — lower is better
          </p>
        </div>


        {/* RMSE */}

        <div style={styles.metricCard}>
          <div style={styles.metricTitle}>
            RMSE
          </div>

          <div style={styles.metricValues}>
            <span>
              {baseline.rmse.toFixed(4)}
            </span>

            <span>
              →
            </span>

            <strong>
              {weatherAware.rmse.toFixed(4)}
            </strong>
          </div>

          <div style={styles.improvement}>
            ↓ {rmseImprovement.toFixed(2)}%
            improvement
          </div>

          <p style={styles.metricDescription}>
            Root Mean Squared Error — lower is
            better
          </p>
        </div>


        {/* R2 */}

        <div style={styles.metricCard}>
          <div style={styles.metricTitle}>
            R² SCORE
          </div>

          <div style={styles.metricValues}>
            <span>
              {baseline.r2.toFixed(5)}
            </span>

            <span>
              →
            </span>

            <strong>
              {weatherAware.r2.toFixed(5)}
            </strong>
          </div>

          <div style={styles.improvement}>
            ↑ {r2Improvement.toFixed(2)}%
            improvement
          </div>

          <p style={styles.metricDescription}>
            Coefficient of determination —
            higher is better
          </p>
        </div>

      </div>


      {/* ==================================================
          GRAPHS
      ================================================== */}

      <div style={styles.graphGrid}>

        <BarGraph
  title="R² Score Comparison"
  values={[
    {
      label: "Baseline",
      value: baseline.r2,
    },
    {
      label: "Weather-Aware",
      value: weatherAware.r2,
    },
  ]}
  maxValue={1}
  decimals={5}
/>


        <BarGraph
          title="RMSE Comparison"
          values={[
            {
              label: "Baseline",
              value: baseline.rmse,
            },
            {
              label: "Weather-Aware",
              value: weatherAware.rmse,
            },
          ]}
          maxValue={12}
        />


        <BarGraph
          title="R² Score Comparison"
          values={[
            {
              label: "Baseline",
              value: baseline.r2,
            },
            {
              label: "Weather-Aware",
              value: weatherAware.r2,
            },
          ]}
          maxValue={1}
        />

      </div>


      {/* ==================================================
          MODEL COMPARISON TABLE
      ================================================== */}

      <div style={styles.tableCard}>

        <h3 style={styles.sectionTitle}>
          Detailed Comparison
        </h3>

        <div style={styles.tableWrapper}>
          <table style={styles.table}>

            <thead>
              <tr>
                <th style={styles.th}>
                  Model
                </th>

                <th style={styles.th}>
                  MAE
                </th>

                <th style={styles.th}>
                  RMSE
                </th>

                <th style={styles.th}>
                  R² Score
                </th>
              </tr>
            </thead>


            <tbody>

              {models.map((model) => (
                <tr key={model.name}>

                  <td style={styles.td}>
                    <strong>
                      {model.name}
                    </strong>
                  </td>

                  <td style={styles.td}>
                    {Number(
                      model.mae
                    ).toFixed(4)}
                  </td>

                  <td style={styles.td}>
                    {Number(
                      model.rmse
                    ).toFixed(4)}
                  </td>

                  <td style={styles.td}>
                    {Number(
                      model.r2
                    ).toFixed(5)}
                  </td>

                </tr>
              ))}

            </tbody>

          </table>
        </div>
      </div>


      {/* ==================================================
          CONCLUSION
      ================================================== */}

      <div style={styles.conclusion}>

        <div style={styles.conclusionIcon}>
          🏆
        </div>

        <div>

          <h3 style={styles.conclusionTitle}>
            Weather-Aware Model Performs Better
          </h3>

          <p style={styles.conclusionText}>
            Adding temperature, humidity,
            rainfall, and wind speed improved
            the model's prediction performance
            compared with the baseline Random
            Forest model.
          </p>

        </div>

      </div>


      {/* ==================================================
          MODEL INFORMATION
      ================================================== */}

      <div style={styles.infoCard}>

        <h3 style={styles.sectionTitle}>
          Model Information
        </h3>

        <div style={styles.infoGrid}>

          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>
              Algorithm
            </span>

            <strong>
              Random Forest
            </strong>
          </div>


          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>
              Baseline Model
            </span>

            <strong>
              Consumption + Time Features
            </strong>
          </div>


          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>
              Weather Model
            </span>

            <strong>
              Consumption + Time + Weather
            </strong>
          </div>


          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>
              Weather Features
            </span>

            <strong>
              Temperature, Humidity,
              Rainfall, Wind Speed
            </strong>
          </div>

        </div>

      </div>


      {/* ==================================================
          METRIC EXPLANATION
      ================================================== */}

      <div style={styles.explanationCard}>

        <h3 style={styles.sectionTitle}>
          What do these metrics mean?
        </h3>


        <div style={styles.explanationGrid}>

          {/* MAE */}

          <div style={styles.explanationItem}>

            <div style={styles.explanationIcon}>
              📏
            </div>

            <strong>
              MAE
            </strong>

            <p>
              Mean Absolute Error measures the
              average absolute difference between
              the actual electricity demand and the
              predicted demand.
            </p>

          </div>


          {/* RMSE */}

          <div style={styles.explanationItem}>

            <div style={styles.explanationIcon}>
              📐
            </div>

            <strong>
              RMSE
            </strong>

            <p>
              Root Mean Squared Error measures
              prediction error while giving more
              importance to larger errors.
            </p>

          </div>


          {/* R2 */}

          <div style={styles.explanationItem}>

            <div style={styles.explanationIcon}>
              📊
            </div>

            <strong>
              R² Score
            </strong>

            <p>
              R² Score shows how well the model
              explains the variation in electricity
              demand. A value closer to 1 indicates
              better performance.
            </p>

          </div>

        </div>

      </div>

    </div>
  )
}


/* ======================================================
   STYLES
====================================================== */

const styles = {

  container: {
    width: "100%",
    maxWidth: "1200px",
    margin: "0 auto",
    padding: "30px",
    boxSizing: "border-box",
  },


  /* HEADER */

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "20px",
    marginBottom: "20px",
    flexWrap: "wrap",
  },

  title: {
    margin: 0,
    fontSize: "30px",
    fontWeight: "700",
  },

  subtitle: {
    marginTop: "8px",
    color: "#64748b",
    fontSize: "15px",
    lineHeight: "1.5",
  },

  badge: {
    background: "#ecfdf5",
    color: "#047857",
    padding: "10px 16px",
    borderRadius: "20px",
    fontWeight: "600",
    fontSize: "14px",
  },


  /* API STATUS */

  apiStatus: {
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    padding: "8px 12px",
    marginBottom: "22px",
    background: "#eff6ff",
    color: "#1d4ed8",
    borderRadius: "8px",
    fontSize: "12px",
    fontWeight: "600",
  },

  apiDot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: "#22c55e",
    display: "inline-block",
  },


  /* LOADING */

  loadingCard: {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "16px",
    padding: "50px 30px",
    textAlign: "center",
    boxShadow:
      "0 4px 15px rgba(0,0,0,0.05)",
  },

  loadingIcon: {
    fontSize: "36px",
    marginBottom: "15px",
  },

  loadingTitle: {
    margin: 0,
    fontSize: "22px",
  },

  loadingText: {
    color: "#64748b",
    marginTop: "8px",
  },


  /* ERROR */

  errorCard: {
    display: "flex",
    alignItems: "flex-start",
    gap: "16px",
    background: "#fef2f2",
    border: "1px solid #fecaca",
    borderRadius: "16px",
    padding: "24px",
  },

  errorIcon: {
    fontSize: "30px",
  },

  errorTitle: {
    margin: 0,
    color: "#991b1b",
  },

  errorText: {
    color: "#b91c1c",
    marginBottom: "5px",
  },

  errorHint: {
    color: "#7f1d1d",
    fontSize: "13px",
  },


  /* METRICS */

  metricsGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(250px, 1fr))",
    gap: "20px",
    marginBottom: "25px",
  },

  metricCard: {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "16px",
    padding: "22px",
    boxShadow:
      "0 4px 15px rgba(0,0,0,0.05)",
  },

  metricTitle: {
    fontSize: "13px",
    fontWeight: "700",
    color: "#64748b",
    letterSpacing: "1px",
  },

  metricValues: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    marginTop: "15px",
    fontSize: "24px",
  },

  improvement: {
    marginTop: "12px",
    color: "#059669",
    fontWeight: "700",
    fontSize: "14px",
  },

  metricDescription: {
    color: "#64748b",
    fontSize: "13px",
    marginBottom: 0,
    lineHeight: "1.5",
  },


  /* GRAPHS */

  graphGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(300px, 1fr))",
    gap: "20px",
    marginBottom: "25px",
  },

  graphCard: {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "16px",
    padding: "24px",
    boxShadow:
      "0 4px 15px rgba(0,0,0,0.05)",
  },

  graphTitle: {
    marginTop: 0,
    textAlign: "center",
    fontSize: "18px",
  },

  graphArea: {
    height: "270px",
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "center",
    gap: "55px",
    paddingTop: "20px",
  },

  barColumn: {
    height: "240px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "flex-end",
  },

  valueLabel: {
    fontSize: "13px",
    fontWeight: "700",
    marginBottom: "6px",
  },

  barWrapper: {
    height: "180px",
    display: "flex",
    alignItems: "flex-end",
  },

  bar: {
    width: "55px",
    minHeight: "5px",
    borderRadius: "8px 8px 0 0",
    background:
      "linear-gradient(180deg, #2563eb, #60a5fa)",
  },

  barLabel: {
    marginTop: "10px",
    fontSize: "12px",
    color: "#475569",
    textAlign: "center",
    maxWidth: "90px",
  },


  /* TABLE */

  tableCard: {
    background: "#ffffff",
    border: "1px solid #e2e8f0",
    borderRadius: "16px",
    padding: "24px",
    marginBottom: "25px",
    overflowX: "auto",
  },

  tableWrapper: {
    overflowX: "auto",
  },

  sectionTitle: {
    marginTop: 0,
    marginBottom: "20px",
    fontSize: "20px",
  },

  table: {
    width: "100%",
    borderCollapse: "collapse",
    minWidth: "600px",
  },

  th: {
    textAlign: "left",
    padding: "14px",
    background: "#f8fafc",
    borderBottom:
      "1px solid #e2e8f0",
    fontSize: "14px",
  },

  td: {
    padding: "14px",
    borderBottom:
      "1px solid #e2e8f0",
    fontSize: "14px",
  },


  /* CONCLUSION */

  conclusion: {
    display: "flex",
    alignItems: "flex-start",
    gap: "16px",
    background: "#f0fdf4",
    border: "1px solid #bbf7d0",
    borderRadius: "16px",
    padding: "22px",
    marginBottom: "25px",
  },

  conclusionIcon: {
    fontSize: "30px",
  },

  conclusionTitle: {
    margin: "0 0 8px",
    color: "#166534",
  },

  conclusionText: {
    margin: 0,
    color: "#166534",
    lineHeight: "1.6",
  },


  /* MODEL INFORMATION */

  infoCard: {
    background: "#ffffff",
    border:
      "1px solid #e2e8f0",
    borderRadius: "16px",
    padding: "24px",
    marginBottom: "25px",
  },

  infoGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(230px, 1fr))",
    gap: "15px",
  },

  infoItem: {
    display: "flex",
    flexDirection: "column",
    gap: "7px",
    padding: "16px",
    background: "#f8fafc",
    borderRadius: "12px",
  },

  infoLabel: {
    color: "#64748b",
    fontSize: "12px",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  },


  /* EXPLANATION */

  explanationCard: {
    background: "#f8fafc",
    borderRadius: "16px",
    padding: "24px",
    border:
      "1px solid #e2e8f0",
  },

  explanationGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "20px",
  },

  explanationItem: {
    color: "#475569",
    lineHeight: "1.6",
  },

  explanationIcon: {
    fontSize: "25px",
    marginBottom: "8px",
  },
}