import { useState, useEffect } from 'react'
import './App.css'

function UptimeBar({ serviceId }) {
  const [history, setHistory] = useState(null)

  useEffect(() => {
    fetch(`http://localhost:5000/api/services/${serviceId}/history?days=10`)
      .then(res => res.json())
      .then(data => setHistory(data))
  }, [serviceId])

  if (!history) return null

  return (
    <div className="uptime-block">
      <div className="uptime-header">
        <span className="metric-label">10-day uptime</span>
        <span className="metric-value">
          {history.uptime_pct !== null ? `${history.uptime_pct}%` : 'No data'}
        </span>
      </div>
      <div className="uptime-bar">
        {history.history.map((day, i) => (
          <div key={i} className={`uptime-segment ${day.status}`} title={day.date}></div>
        ))}
      </div>
    </div>
  )
}

function App() {
  const [services, setServices] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchData = () => {
    fetch('http://localhost:5000/api/services')
      .then(res => res.json())
      .then(data => {
        setServices(data)
        setLoading(false)
        setLastUpdated(new Date())
      })

    fetch('http://localhost:5000/api/alerts')
      .then(res => res.json())
      .then(data => setAlerts(data))
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <p className="loading">Loading...</p>

  const upCount = services.filter(s => s.status === 'up').length
  const downCount = services.filter(s => s.status === 'down').length
  const avgResponse = services.length
    ? Math.round(services.reduce((sum, s) => sum + s.response_time_ms, 0) / services.length)
    : 0

  const overallStatus = downCount === 0 ? 'up' : downCount === services.length ? 'down' : 'degraded'
  const overallLabel = { up: 'All operational', degraded: 'Partial outage', down: 'Major outage' }[overallStatus]

  return (
    <div className="dashboard">

      <nav className="navbar">
  <h1>API WatchTower</h1>
</nav>

      <div className="stats-row">
        <div className="stat-card">
          <p className="stat-label">Total APIs monitored</p>
          <p className="stat-value">{services.length}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">APIs up</p>
          <p className="stat-value up-text">{upCount}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">APIs down</p>
          <p className="stat-value down-text">{downCount}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Avg response time</p>
          <p className="stat-value">{avgResponse} ms</p>
        </div>
      </div>

      <section>
        <h2 className="section-title">Monitored APIs</h2>
        <div className="api-list">
          {services.map(service => (
            <div key={service.id} className="api-row">
              <div className="api-row-top">
                <div className="api-left">
                  <p className="api-name">{service.name}</p>
                  <p className="api-url">{service.url}</p>
                </div>

                <span className={`status-badge ${service.status}`}>
                  {service.status === 'up' ? 'Operational' : 'Down'}
                </span>

                <div className="api-right">
                  <div className="metric">
                    <p className="metric-label">Response time</p>
                    <p className="metric-value">{service.response_time_ms} ms</p>
                  </div>
                  <div className="metric">
                    <p className="metric-label">Last checked</p>
                    <p className="metric-value">Just now</p>
                  </div>
                </div>
              </div>

              <UptimeBar serviceId={service.id} />
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="section-title">Recent incidents</h2>
        <div className="incident-list">
          {alerts.length === 0 && <p className="no-data">No incidents recorded.</p>}
          {alerts.slice(0, 8).map(alert => (
            <div key={alert.id} className="incident-item">
              <div>
                <p className="incident-title">{alert.service_name} — service disruption</p>
                <p className="incident-message">{alert.message}</p>
              </div>
              <div className="incident-right">
                <span className="incident-badge">Logged</span>
                <p className="incident-time">{alert.triggered_at}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="footer">
        Auto-refreshing every 30 seconds
      </footer>

    </div>
  )
}

export default App