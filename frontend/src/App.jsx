
import { useEffect, useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './App.css'

const INITIAL_START = '2026-01-01'
const INITIAL_END = '2026-01-07'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

function formatMW(value) {
  if (value == null || !Number.isFinite(Number(value))) return '—'
  return `${Math.round(Number(value)).toLocaleString('en-GB')} MW`
}

function formatMetric(value) {
  if (value == null || !Number.isFinite(Number(value))) return '—'
  return `${Math.round(Number(value)).toLocaleString('en-GB')} MW`
}

function formatTime(value) {
  return new Date(value).toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short',
  })
}

function App() {
  const [startDate, setStartDate] = useState(INITIAL_START)
  const [endDate, setEndDate] = useState(INITIAL_END)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function loadAnalysis(event) {
    event?.preventDefault()

    if (startDate > endDate) {
      setError('The start date must be on or before the end date.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      })

      const response = await fetch(
        `${API_BASE_URL}/analysis/wind/day-ahead?${params.toString()}`,
      )

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || `Request failed (${response.status})`)
      }

      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err.message || 'Could not load wind forecast analysis.')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAnalysis()
    // Load the initial January 2026 analysis once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const records = (data?.records ?? []).map((record) => ({
    ...record,
    chartTime: new Date(record.startTime).toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'UTC',
    }),
  }))

  const metrics = [
    {
      label: 'Mean absolute error',
      value: formatMetric(data?.metrics?.maeMW),
      description: 'Average size of forecast errors',
    },
    {
      label: 'Root mean squared error',
      value: formatMetric(data?.metrics?.rmseMW),
      description: 'Penalises larger errors more heavily',
    },
    {
      label: 'Forecast bias',
      value: formatMetric(data?.metrics?.biasMW),
      description:
        data?.metrics?.biasMW == null
          ? 'Forecast minus actual generation'
          : Number(data.metrics.biasMW) > 0
            ? 'Forecasts overestimated generation on average'
            : Number(data.metrics.biasMW) < 0
              ? 'Forecasts underestimated generation on average'
              : 'Forecasts matched actuals on average',
    },
  ]

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="WindScope home">
          <span className="brand-mark">W</span>
          <span>WindScope</span>
        </a>
        <span className="topbar-label">UK POWER MARKET · ANALYTICS</span>
      </header>

      <section className="intro">
        <p className="eyebrow">DAY-AHEAD DECISION SUPPORT</p>
        <h1>Wind forecast performance</h1>
        <p className="intro-copy">
          Compare predicted wind generation with actual output to understand
          forecast errors ahead of electricity purchasing decisions.
        </p>
      </section>

      <section className="filter-panel">
        <form className="date-form" onSubmit={loadAnalysis}>
          <label>
            Start date
            <input
              type="date"
              value={startDate}
              max="2026-01-31"
              min="2026-01-01"
              onChange={(event) => setStartDate(event.target.value)}
              required
            />
          </label>
          <label>
            End date
            <input
              type="date"
              value={endDate}
              max="2026-01-31"
              min="2026-01-01"
              onChange={(event) => setEndDate(event.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? 'Loading…' : 'Analyse period'}
          </button>
        </form>
        <p className="filter-note">
          Historical delivery dates · January 2026 · National wind generation
        </p>
      </section>

      {error && (
        <div className="error-message" role="alert">
          <strong>Unable to load analysis</strong>
          <p>{error}</p>
          <button type="button" onClick={() => loadAnalysis()} disabled={loading}>
            Try again
          </button>
        </div>
      )}

      {loading && !data && (
        <p className="loading-message">Loading wind generation data…</p>
      )}

      {data && (
        <>
          <section className="metrics-grid" aria-label="Forecast accuracy metrics">
            {metrics.map((metric) => (
              <article className="metric-card" key={metric.label}>
                <p className="metric-label">{metric.label}</p>
                <p className="metric-value">{metric.value}</p>
                <p className="metric-description">{metric.description}</p>
              </article>
            ))}
          </section>

          <section className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">GENERATION COMPARISON</p>
                <h2>Forecast vs actual</h2>
              </div>
              <span className="interval-count">
                {data.matchedIntervals} matched hours
              </span>
            </div>

            {records.length > 0 ? (
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={records}
                    margin={{ top: 12, right: 16, left: 12, bottom: 8 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5eaf0" />
                    <XAxis
                      dataKey="chartTime"
                      tick={{ fontSize: 11, fill: '#64748b' }}
                      minTickGap={36}
                    />
                    <YAxis
                      tickFormatter={(value) => `${Math.round(value / 1000)}k`}
                      tick={{ fontSize: 11, fill: '#64748b' }}
                      width={48}
                    />
                    <Tooltip
                      labelFormatter={(_, payload) =>
                        payload?.[0]?.payload?.startTime
                          ? formatTime(payload[0].payload.startTime)
                          : ''
                      }
                      formatter={(value, name) => [
                        formatMW(value),
                        name === 'forecastMW' ? 'Forecast' : 'Actual',
                      ]}
                    />
                    <Line
                      type="monotone"
                      dataKey="forecastMW"
                      name="Forecast"
                      stroke="#2563eb"
                      strokeWidth={2}
                      dot={false}
                      connectNulls={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="actualMW"
                      name="Actual"
                      stroke="#0f9f75"
                      strokeWidth={2}
                      dot={false}
                      connectNulls={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="empty-message">
                No matched hourly records are available for this period.
              </p>
            )}

            <div className="chart-legend">
              <span><i className="legend-dot forecast-dot" /> Forecast</span>
              <span><i className="legend-dot actual-dot" /> Actual generation</span>
            </div>
          </section>

          <section className="panel details-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">METHODOLOGY</p>
                <h2>How to read these results</h2>
              </div>
            </div>
            <div className="method-grid">
              <div>
                <h3>Decision-time forecast</h3>
                <p>{data.decisionRule}. This is the analysis assumption used to avoid using forecasts published after the decision point.</p>
              </div>
              <div>
                <h3>Mean absolute error (MAE)</h3>
                <p>The average absolute difference between forecast and actual generation. Lower is better.</p>
              </div>
              <div>
                <h3>Root mean squared error (RMSE)</h3>
                <p>Gives larger misses more influence than MAE. Lower is better.</p>
              </div>
              <div>
                <h3>Forecast bias</h3>
                <p>Forecast minus actual generation. Positive values indicate overforecasting; negative values indicate underforecasting.</p>
              </div>
            </div>
            <p className="caveat">
              This dashboard evaluates wind generation forecast accuracy. It does
              not calculate the final electricity purchase volume, which also
              depends on demand forecasts, other generation sources, and the
              utility’s trading position.
            </p>
          </section>
        </>
      )}

      <footer className="footer">
        <span>WindScope · Elexon BMRS data</span>
        <span>All timestamps shown in UTC</span>
      </footer>
    </main>
  )
}

export default App
