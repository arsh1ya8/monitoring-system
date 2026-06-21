import time
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Depends, Response, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler

from database import get_db, check_db_connection, engine, wait_for_db
from models import Base
from metrics import collect_metrics, check_thresholds, get_prometheus_metrics, request_counter
from incidents import create_incident, resolve_incident, get_all_incidents, save_metric_snapshot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def monitoring_job():
    from database import SessionLocal
    db = SessionLocal()
    try:
        metrics = collect_metrics()
        logger.info(f"Metrics - CPU: {metrics['cpu_percent']:.1f}% Memory: {metrics['memory_percent']:.1f}% Disk: {metrics['disk_percent']:.1f}%")
        alerts = check_thresholds(metrics)
        alerted_sources = set()
        for alert in alerts:
            create_incident(db=db, title=f"High {alert['resource'].upper()} Usage",
                description=alert["message"], severity=alert["severity"], source=alert["resource"])
            alerted_sources.add(alert["resource"])
            logger.warning(f"ALERT [{alert['severity'].upper()}]: {alert['message']}")
        for resource in ["cpu", "memory", "disk"]:
            if resource not in alerted_sources:
                resolved = resolve_incident(db, resource)
                if resolved:
                    logger.info(f"Incident resolved: {resolved.title}")
        db_healthy = check_db_connection()
        if not db_healthy:
            create_incident(db=db, title="Database Connection Failed",
                description="Cannot connect to SQL Server.", severity="critical", source="database")
        else:
            resolve_incident(db, "database")
        save_metric_snapshot(db, cpu=metrics["cpu_percent"],
            memory=metrics["memory_percent"], disk=metrics["disk_percent"])
    except Exception as e:
        logger.error(f"Monitoring job failed: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting monitoring system...")
    logger.info("Waiting for database to be ready...")
    wait_for_db(retries=15, delay=5)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready")
    monitoring_job()
    scheduler.add_job(monitoring_job, "interval", seconds=30)
    scheduler.start()
    logger.info("Background monitoring started")
    yield
    scheduler.shutdown()
    logger.info("Monitoring system stopped")

app = FastAPI(title="Cloud Infrastructure Monitoring System", version="1.0.0", lifespan=lifespan)

@app.middleware("http")
async def count_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    request_counter.labels(endpoint=request.url.path, status=str(response.status_code)).inc()
    return response

@app.get("/")
def root():
    return {"message": "Monitoring System is running", "dashboard": "/dashboard"}

@app.get("/health")
def health_check():
    db_healthy = check_db_connection()
    metrics = collect_metrics()
    if not db_healthy:
        overall = "unhealthy"
    elif metrics["cpu_percent"] > 90 or metrics["memory_percent"] > 95:
        overall = "degraded"
    else:
        overall = "healthy"
    return {"status": overall, "timestamp": datetime.utcnow().isoformat(),
        "checks": {"database": "up" if db_healthy else "down",
        "cpu_percent": metrics["cpu_percent"],
        "memory_percent": metrics["memory_percent"],
        "disk_percent": metrics["disk_percent"]}}

@app.get("/metrics")
def prometheus_metrics():
    data, content_type = get_prometheus_metrics()
    return Response(content=data, media_type=content_type)

@app.get("/api/metrics")
def current_metrics():
    return collect_metrics()

@app.get("/api/incidents")
def list_incidents(db: Session = Depends(get_db)):
    incidents = get_all_incidents(db)
    return [{"id": i.id, "title": i.title, "description": i.description,
        "severity": i.severity, "status": i.status, "source": i.source,
        "created_at": i.created_at.isoformat(),
        "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None}
        for i in incidents]

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Infrastructure Monitoring Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
        h1 { color: #38bdf8; }
        h2 { color: #94a3b8; border-bottom: 1px solid #334155; padding-bottom: 8px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px; }
        .card { background: #1e293b; border-radius: 8px; padding: 20px; border-left: 4px solid #38bdf8; }
        .card.warning { border-left-color: #f59e0b; }
        .card.critical { border-left-color: #ef4444; }
        .card.healthy { border-left-color: #22c55e; }
        .metric { font-size: 2.5rem; font-weight: bold; }
        .label { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }
        table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; }
        th { background: #334155; padding: 12px; text-align: left; color: #94a3b8; }
        td { padding: 12px; border-bottom: 1px solid #334155; }
        .badge-open { background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
        .badge-resolved { background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
        .badge-critical { background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
        .badge-warning { background: #f59e0b; color: black; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; }
    </style>
</head>
<body>
    <h1>Infrastructure Monitoring Dashboard</h1>
    <h2>System Metrics</h2>
    <div class="grid" id="metrics-grid">Loading...</div>
    <h2>Recent Incidents</h2>
    <table>
        <thead><tr><th>ID</th><th>Title</th><th>Severity</th><th>Status</th><th>Time</th></tr></thead>
        <tbody id="incidents-body"><tr><td colspan="5">Loading...</td></tr></tbody>
    </table>
    <script>
        async function loadMetrics() {
            try {
                const res = await fetch("/api/metrics");
                const data = await res.json();
                const cards = [
                    {label: "CPU Usage", value: data.cpu_percent},
                    {label: "Memory Usage", value: data.memory_percent},
                    {label: "Disk Usage", value: data.disk_percent}
                ];
                document.getElementById("metrics-grid").innerHTML = cards.map(c => {
                    const level = c.value >= 90 ? "critical" : c.value >= 75 ? "warning" : "healthy";
                    return `<div class="card ${level}"><div class="metric">${c.value.toFixed(1)}%</div><div class="label">${c.label}</div></div>`;
                }).join("");
            } catch(e) { document.getElementById("metrics-grid").innerHTML = "<p>Failed to load</p>"; }
        }
        async function loadIncidents() {
            try {
                const res = await fetch("/api/incidents");
                const data = await res.json();
                if (data.length === 0) {
                    document.getElementById("incidents-body").innerHTML = "<tr><td colspan='5'>No incidents - system healthy</td></tr>";
                    return;
                }
                document.getElementById("incidents-body").innerHTML = data.map(i =>
                    `<tr><td>#${i.id}</td><td>${i.title}<br><small style="color:#64748b">${i.description}</small></td>
                    <td><span class="badge-${i.severity}">${i.severity}</span></td>
                    <td><span class="badge-${i.status}">${i.status}</span></td>
                    <td>${new Date(i.created_at).toLocaleString()}</td></tr>`
                ).join("");
            } catch(e) { document.getElementById("incidents-body").innerHTML = "<tr><td colspan='5'>Failed to load</td></tr>"; }
        }
        loadMetrics();
        loadIncidents();
    </script>
</body>
</html>"""
    return HTMLResponse(content=html)
