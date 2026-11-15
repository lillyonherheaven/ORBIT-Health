from pathlib import Path

# 1. تجهيز صفحة الواجهة التفاعلية الكاملة (React + Chart.js) لتعمل مباشرة بدون npm build
html_ui = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ORBIT Health v2 | Astronaut Decision Support</title>
  <link rel="stylesheet" href="/src/styles.css" />
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect, useRef } = React;
    const API_BASE = 'http://127.0.0.1:8000/api';

    const STATE_ICONS = {
      GREEN: '● [OK - NOMINAL]',
      AMBER: '▲ [WATCH]',
      ORANGE: '◆ [WARNING]',
      RED: '■ [CRITICAL EMERGENCY]',
      GRAY: '◌ [INSUFFICIENT DATA]'
    };

    const REGION_INFO = {
      head: { label: 'Head, Eyes (SANS) & Sleep', metrics: ['sleep_duration', 'mood', 'temperature'] },
      chest: { label: 'Heart, Chest & Cardiovascular', metrics: ['heart_rate_resting', 'spo2', 'respiratory_rate'] },
      abdomen: { label: 'Metabolic & Nutrition', metrics: ['glucose'] },
      limbs: { label: 'Bone, Muscle & Exercise', metrics: ['exercise_completion'] },
      cabin: { label: 'Whole-Body Radiation & Cabin Environment', metrics: ['co2', 'radiation_dose'] }
    };

    function TrendChart({ labels, values, label }) {
      const canvasRef = useRef(null);
      const chartRef = useRef(null);

      useEffect(() => {
        if (!canvasRef.current) return;
        if (chartRef.current) chartRef.current.destroy();

        chartRef.current = new Chart(canvasRef.current, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [{
              label: label,
              data: values,
              borderColor: '#38bdf8',
              backgroundColor: 'rgba(56, 189, 248, 0.2)',
              tension: 0.25,
              pointRadius: 5,
              fill: true
            }]
          },
          options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#f8fafc' } } },
            scales: {
              x: { ticks: { color: '#cbd5e1' }, grid: { color: '#1e293b' } },
              y: { ticks: { color: '#cbd5e1' }, grid: { color: '#1e293b' } }
            }
          }
        });

        return () => { if (chartRef.current) chartRef.current.destroy(); };
      }, [labels.join(','), values.join(','), label]);

      return <canvas ref={canvasRef} height="120"></canvas>;
    }

    function App() {
      const [data, setData] = useState(null);
      const [selectedRegion, setSelectedRegion] = useState('chest');
      const [selectedMetric, setSelectedMetric] = useState('heart_rate_resting');
      const [showEvidence, setShowEvidence] = useState(false);
      const [streak, setStreak] = useState(5);

      const fetchState = async () => {
        try {
          const res = await fetch(`${API_BASE}/state`);
          setData(await res.json());
        } catch (e) {
          console.error(e);
        }
      };

      useEffect(() => { fetchState(); }, []);

      const triggerScenario = async (name, missing = '', noisy = false) => {
        const q = new URLSearchParams({ missing_sensor: missing, noisy: String(noisy) }).toString();
        const res = await fetch(`${API_BASE}/scenario/${name}?${q}`, { method: 'POST' });
        setData(await res.json());
        if (name === 'scenario_a') { setSelectedRegion('chest'); setSelectedMetric('heart_rate_resting'); }
        if (name === 'scenario_b') { setSelectedRegion('cabin'); setSelectedMetric('radiation_dose'); }
        if (name === 'scenario_c') { setSelectedRegion('cabin'); setSelectedMetric('co2'); }
      };

      const toggleComms = async () => {
        const nextMode = data.online ? 'offline' : 'online';
        await fetch(`${API_BASE}/comms/${nextMode}`, { method: 'POST' });
        fetchState();
      };

      if (!data) return <div className="app-container"><div className="card"><h2>Loading ORBIT Health v2...</h2></div></div>;

      const evt = data.active_event;
      const pb = data.playbook;
      const metricObs = data.observations.filter((o) => o.metric === selectedMetric && o.quality !== 'missing');

      const fillRegion = (r) => {
        if (evt.state === 'GRAY') return '#64748b';
        if (evt.state === 'RED' && r === 'cabin') return '#ef4444';
        if (evt.state === 'ORANGE' && r !== 'cabin') return '#f97316';
        return '#10b981';
      };

      return (
        <div className="app-container">
          <div className="top-bar">
            <div className="top-bar-title">ORBIT HEALTH v2 | MISSION DAY 086 | ASTRONAUT A01</div>
            <div className="top-bar-status">
              <span className={`badge ${data.online ? 'badge-online' : 'badge-offline'}`}>
                LINK: {data.online ? 'ONLINE (SYNCHRONIZED)' : 'OFFLINE (LOCAL AUTONOMY)'}
              </span>
              <span className="badge badge-outbox">
                OUTBOX QUEUE: {data.outbox_count} | DELIVERED: {data.delivered_count}
              </span>
            </div>
          </div>

          <div className="judge-panel">
            <div style={{ marginBottom: '8px', fontWeight: 'bold', color: '#c7d2fe' }}>
              JUDGE CONTROL PANEL (LIVE ENGINE & FAULT INJECTION — ALL THRESHOLDS ILLUSTRATIVE)
            </div>
            <button className="btn btn-primary" onClick={() => triggerScenario('normal')}>Reset Normal (GREEN)</button>
            <button className="btn btn-warning" onClick={() => triggerScenario('scenario_a')}>Scenario A: Gradual Deterioration (ORANGE)</button>
            <button className="btn btn-danger" onClick={() => triggerScenario('scenario_b')}>Scenario B: Radiation Event (RED Override)</button>
            <button className="btn btn-danger" onClick={() => triggerScenario('scenario_c')}>Scenario C: Cabin CO2 + Comms Loss</button>
            <button className="btn" onClick={() => triggerScenario('normal', 'heart_rate_resting', false)}>Kill HR Sensor (GRAY State)</button>
            <button className="btn" onClick={() => triggerScenario('normal', '', true)}>Inject 1 Noisy Sample</button>
            <button className="btn" onClick={toggleComms}>Toggle Earth Link ({data.online ? 'Go Offline' : 'Reconnect & Flush'})</button>
          </div>

          <div className="main-grid">
            <div className="col-left">
              <div className="card" style={{ textAlign: 'center' }}>
                <h2>Clickable 2D Body & Habitat Map</h2>
                <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: '8px' }}>
                  Click any region to open domain metrics, trends & playbooks
                </p>
                <svg width="210" height="320" viewBox="0 0 210 320">
                  <rect x="8" y="8" width="194" height="304" rx="12" fill="none" stroke={fillRegion('cabin')} strokeWidth="4" strokeDasharray="6,4" className="body-region" onClick={() => { setSelectedRegion('cabin'); setSelectedMetric('co2'); }} />
                  <text x="105" y="26" fill="#cbd5e1" fontSize="10" textAnchor="middle">CABIN & RADIATION</text>

                  <circle cx="105" cy="65" r="22" fill={fillRegion('head')} className="body-region" onClick={() => { setSelectedRegion('head'); setSelectedMetric('sleep_duration'); }} />
                  <text x="105" y="69" fill="#0f172a" fontSize="10" fontWeight="bold" textAnchor="middle">HEAD</text>

                  <rect x="72" y="95" width="66" height="64" rx="8" fill={fillRegion('chest')} className="body-region" onClick={() => { setSelectedRegion('chest'); setSelectedMetric('heart_rate_resting'); }} />
                  <text x="105" y="130" fill="#0f172a" fontSize="10" fontWeight="bold" textAnchor="middle">HEART/CHEST</text>

                  <rect x="78" y="166" width="54" height="44" rx="6" fill={fillRegion('abdomen')} className="body-region" onClick={() => { setSelectedRegion('abdomen'); setSelectedMetric('glucose'); }} />
                  <text x="105" y="192" fill="#0f172a" fontSize="9" fontWeight="bold" textAnchor="middle">METABOLIC</text>

                  <rect x="42" y="98" width="24" height="88" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => { setSelectedRegion('limbs'); setSelectedMetric('exercise_completion'); }} />
                  <rect x="144" y="98" width="24" height="88" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => { setSelectedRegion('limbs'); setSelectedMetric('exercise_completion'); }} />
                  <rect x="76" y="216" width="25" height="80" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => { setSelectedRegion('limbs'); setSelectedMetric('exercise_completion'); }} />
                  <rect x="109" y="216" width="25" height="80" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => { setSelectedRegion('limbs'); setSelectedMetric('exercise_completion'); }} />
                </svg>
                <div style={{ marginTop: '8px', padding: '8px', background: '#1e293b', borderRadius: '6px' }}>
                  <strong>Region:</strong> {REGION_INFO[selectedRegion].label}
                </div>
              </div>
            </div>

            <div className="col-center">
              <div className={`alert-banner state-${evt.state}`}>
                <h3 style={{ marginBottom: '8px' }}>{STATE_ICONS[evt.state]} — STATE: {evt.state} ({evt.domain.toUpperCase()})</h3>
                <p style={{ marginBottom: '6px' }}><strong>1. NEXT ACTION:</strong> {evt.explanation.next_action}</p>
                <p style={{ marginBottom: '6px' }}><strong>2. WHAT CHANGED:</strong> {evt.explanation.what_changed}</p>
                <p style={{ marginBottom: '6px' }}><strong>3. WHY IT MATTERS:</strong> {evt.explanation.why_it_matters}</p>

                {pb && (
                  <div className="playbook-box">
                    <div><strong>Playbook:</strong> {pb.id} (v{pb.version}) | <strong>Status:</strong> {pb.approval_status}</div>
                    <div><strong>Action:</strong> {pb.initial_action}</div>
                    <div><strong>Escalation:</strong> {pb.escalation_condition}</div>
                  </div>
                )}

                <div style={{ marginTop: '10px', fontSize: '0.85rem' }}>
                  <span><strong>Tx:</strong> {evt.tx_status} | <strong>Delivery:</strong> {evt.delivery_status} | <strong>Medical Ack:</strong> {evt.ack_status}</span>
                  <button className="btn" style={{ marginLeft: '10px', padding: '4px 8px', fontSize: '0.78rem' }} onClick={() => setShowEvidence(!showEvidence)}>
                    {showEvidence ? 'Hide Evidence' : 'Show Evidence & Quality'}
                  </button>
                </div>

                {showEvidence && (
                  <div className="playbook-box" style={{ fontSize: '0.82rem' }}>
                    <div><strong>Rules Triggered:</strong> {evt.rules_triggered.join(', ') || 'Nominal'}</div>
                    <div><strong>Completeness:</strong> {(evt.data_quality.completeness * 100).toFixed(0)}% | <strong>Confidence:</strong> {evt.data_quality.confidence}</div>
                  </div>
                )}
              </div>

              <div className="card">
                <h2>Trend vs. Personal Baseline: {selectedMetric}</h2>
                <div style={{ marginBottom: '8px' }}>
                  {['heart_rate_resting', 'sleep_duration', 'exercise_completion', 'glucose', 'spo2', 'co2', 'radiation_dose'].map((m) => (
                    <button key={m} className="btn" style={{ padding: '4px 8px', fontSize: '0.75rem' }} onClick={() => setSelectedMetric(m)}>
                      {m}
                    </button>
                  ))}
                </div>
                <TrendChart
                  labels={metricObs.map((o) => `Day ${o.context?.mission_day || 1}`)}
                  values={metricObs.map((o) => o.value)}
                  label={`${selectedMetric} (${metricObs[0]?.unit || ''})`}
                />
              </div>
            </div>

            <div className="col-right">
              <div className="card">
                <h2>Adherence Engagement</h2>
                <p>Daily Check-In Streak: <strong>{streak} Mission Days</strong></p>
                <p>Exercise Plan Adherence: <strong>96% Completed</strong></p>
                <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '6px' }}>
                  Symptom reporting is neutral and never penalized.
                </p>
              </div>

              <div className="card">
                <h2>Voluntary Daily Crew Check-In</h2>
                <div className="input-group">
                  <label>Restedness</label>
                  <select><option>Well Rested</option><option>Moderately Tired</option><option>Exhausted</option></select>
                </div>
                <div className="input-group">
                  <label>Mood Check-In (Non-Diagnostic)</label>
                  <select><option>Steady / Positive</option><option>Neutral</option><option>Stressed</option></select>
                </div>
                <div className="input-group">
                  <label>Symptoms (Neutral Reporting)</label>
                  <select><option>No new symptoms</option><option>Mild Headache</option><option>Visual Focus Change (SANS)</option></select>
                </div>
                <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => setStreak(streak + 1)}>
                  Save Local Check-In (+1 Adherence Streak)
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
"""

Path("frontend/index.html").write_text(html_ui, encoding="utf-8")

# 2. ربط الواجهة مباشرة بالسيرفر (FastAPI) لتفتح على نفس البورت 8000
main_py = """from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router

app = FastAPI(title="ORBIT Health v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/src", StaticFiles(directory=str(frontend_dir / "src")), name="src")

@app.get("/")
def serve_ui():
    return FileResponse(str(frontend_dir / "index.html"))

@app.get("/health")
def health_check():
    return {"status": "ok", "mode": "offline-first", "thresholds": "ILLUSTRATIVE"}
"""

Path("backend/app/main.py").write_text(main_py, encoding="utf-8")
print("Direct UI configured! Open http://127.0.0.1:8000 in your browser!")