import React, { useState, useEffect } from 'react';
import {
    Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const API_BASE = 'http://127.0.0.1:8000/api';

const STATE_ICONS = {
    GREEN: '● [OK - NOMINAL]',
    AMBER: '▲ [WATCH]',
    ORANGE: '◆ [WARNING]',
    RED: '■ [CRITICAL EMERGENCY]',
    GRAY: '◌ [INSUFFICIENT DATA]'
};

export default function App() {
    const [data, setData] = useState(null);
    const [selectedMetric, setSelectedMetric] = useState('heart_rate_resting');
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
        if (name === 'scenario_a') setSelectedMetric('heart_rate_resting');
        if (name === 'scenario_b') setSelectedMetric('radiation_dose');
        if (name === 'scenario_c') setSelectedMetric('co2');
    };

    const toggleComms = async () => {
        const nextMode = data.online ? 'offline' : 'online';
        await fetch(`${API_BASE}/comms/${nextMode}`, { method: 'POST' });
        fetchState();
    };

    if (!data) return <div className="app-container"><div className="card"><h2>Connecting to Local Onboard Backend (Port 8000)...</h2></div></div>;

    const evt = data.active_event;
    const pb = data.playbook;
    const metricObs = data.observations.filter((o) => o.metric === selectedMetric && o.quality !== 'missing');

    const chartData = {
        labels: metricObs.map((o) => `Day ${o.context?.mission_day || 1}`),
        datasets: [{
            label: `${selectedMetric} (${metricObs[0]?.unit || ''})`,
            data: metricObs.map((o) => o.value),
            borderColor: '#38bdf8',
            tension: 0.2
        }]
    };

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
                        LINK: {data.online ? 'ONLINE' : 'OFFLINE (LOCAL AUTONOMY)'}
                    </span>
                    <span className="badge badge-outbox">
                        OUTBOX: {data.outbox_count} | DELIVERED: {data.delivered_count}
                    </span>
                </div>
            </div>

            <div className="judge-panel">
                <div style={{ marginBottom: '8px', fontWeight: 'bold' }}>JUDGE CONTROL PANEL (ILLUSTRATIVE THRESHOLDS)</div>
                <button className="btn btn-primary" onClick={() => triggerScenario('normal')}>Normal (GREEN)</button>
                <button className="btn btn-warning" onClick={() => triggerScenario('scenario_a')}>Scenario A: Gradual Deterioration (ORANGE)</button>
                <button className="btn btn-danger" onClick={() => triggerScenario('scenario_b')}>Scenario B: Radiation Event (RED)</button>
                <button className="btn btn-danger" onClick={() => triggerScenario('scenario_c')}>Scenario C: Cabin CO2 + Comms Loss</button>
                <button className="btn" onClick={() => triggerScenario('normal', 'heart_rate_resting', false)}>Kill HR Sensor (GRAY)</button>
                <button className="btn" onClick={() => triggerScenario('normal', '', true)}>1 Noisy Sample</button>
                <button className="btn" onClick={toggleComms}>Toggle Link ({data.online ? 'Go Offline' : 'Reconnect'})</button>
            </div>

            <div className="main-grid">
                <div className="col-left">
                    <div className="card" style={{ textAlign: 'center' }}>
                        <h2>Clickable 2D Body Map</h2>
                        <svg width="200" height="310" viewBox="0 0 200 310">
                            <rect x="10" y="10" width="180" height="290" rx="12" fill="none" stroke={fillRegion('cabin')} strokeWidth="4" className="body-region" onClick={() => setSelectedMetric('co2')} />
                            <circle cx="100" cy="60" r="22" fill={fillRegion('head')} className="body-region" onClick={() => setSelectedMetric('sleep_duration')} />
                            <rect x="68" y="90" width="64" height="65" rx="8" fill={fillRegion('chest')} className="body-region" onClick={() => setSelectedMetric('heart_rate_resting')} />
                            <rect x="74" y="162" width="52" height="45" rx="6" fill={fillRegion('abdomen')} className="body-region" onClick={() => setSelectedMetric('glucose')} />
                            <rect x="72" y="214" width="24" height="75" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => setSelectedMetric('exercise_completion')} />
                            <rect x="104" y="214" width="24" height="75" rx="6" fill={fillRegion('limbs')} className="body-region" onClick={() => setSelectedMetric('exercise_completion')} />
                        </svg>
                        <p style={{ fontSize: '0.85rem' }}>Click Head (Sleep), Chest (HR), Abdomen (Glucose), Legs (Exercise), or Border (Cabin CO2).</p>
                    </div>
                </div>

                <div className="col-center">
                    <div className={`alert-banner state-${evt.state}`}>
                        <h3>{STATE_ICONS[evt.state]} — {evt.state} ({evt.domain})</h3>
                        <p><strong>1. NEXT ACTION:</strong> {evt.explanation.next_action}</p>
                        <p><strong>2. WHAT CHANGED:</strong> {evt.explanation.what_changed}</p>
                        <p><strong>3. WHY IT MATTERS:</strong> {evt.explanation.why_it_matters}</p>
                        {pb && (
                            <div className="playbook-box">
                                <div><strong>Playbook:</strong> {pb.id} (v{pb.version}) [{pb.approval_status}]</div>
                                <div><strong>Action:</strong> {pb.initial_action}</div>
                                <div><strong>Escalation:</strong> {pb.escalation_condition}</div>
                            </div>
                        )}
                        <div style={{ marginTop: '8px', fontSize: '0.85rem' }}>
                            Tx: {evt.tx_status} | Delivery: {evt.delivery_status} | Ack: {evt.ack_status}
                        </div>
                    </div>

                    <div className="card">
                        <h2>Trend Chart: {selectedMetric}</h2>
                        <Line data={chartData} />
                    </div>
                </div>

                <div className="col-right">
                    <div className="card">
                        <h2>Adherence Gamification</h2>
                        <p>Check-In Streak: <strong>{streak} Days</strong></p>
                        <p>Exercise Plan Adherence: <strong>96%</strong></p>
                        <p style={{ fontSize: '0.8rem', marginTop: '6px' }}>Symptom reporting is neutral and never penalized.</p>
                    </div>

                    <div className="card">
                        <h2>Daily Crew Check-In</h2>
                        <div className="input-group">
                            <label>Mood (Non-Diagnostic)</label>
                            <select><option>Steady</option><option>Tired</option><option>Stressed</option></select>
                        </div>
                        <div className="input-group">
                            <label>Symptoms</label>
                            <select><option>None</option><option>Mild Headache</option><option>Visual Change (SANS)</option></select>
                        </div>
                        <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => setStreak(streak + 1)}>
                            Submit Check-In (+1 Streak)
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}