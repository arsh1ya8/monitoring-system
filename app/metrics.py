import psutil
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST

cpu_gauge    = Gauge("app_cpu_usage_percent",    "Current CPU usage in percent")
memory_gauge = Gauge("app_memory_usage_percent", "Current memory usage in percent")
disk_gauge   = Gauge("app_disk_usage_percent",   "Current disk usage in percent")

incident_counter = Counter("app_incidents_total",     "Total number of incidents created")
alert_counter    = Counter("app_alerts_total",        "Total number of alerts fired", ["severity"])
request_counter  = Counter("app_http_requests_total", "Total HTTP requests", ["endpoint", "status"])

THRESHOLDS = {
    "cpu":    {"warning": 75.0, "critical": 90.0},
    "memory": {"warning": 80.0, "critical": 95.0},
    "disk":   {"warning": 85.0, "critical": 95.0},
}

def collect_metrics() -> dict:
    cpu    = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk   = psutil.disk_usage("/").percent

    cpu_gauge.set(cpu)
    memory_gauge.set(memory)
    disk_gauge.set(disk)

    return {
        "cpu_percent":    cpu,
        "memory_percent": memory,
        "disk_percent":   disk,
    }

def check_thresholds(metrics: dict) -> list:
    alerts = []
    checks = [
        ("cpu",    metrics["cpu_percent"],    "CPU"),
        ("memory", metrics["memory_percent"], "Memory"),
        ("disk",   metrics["disk_percent"],   "Disk"),
    ]
    for resource, value, label in checks:
        thresholds = THRESHOLDS[resource]
        if value >= thresholds["critical"]:
            severity = "critical"
        elif value >= thresholds["warning"]:
            severity = "warning"
        else:
            continue
        alerts.append({
            "resource": resource,
            "value":    value,
            "severity": severity,
            "message":  f"{label} usage is at {value:.1f}%",
        })
        alert_counter.labels(severity=severity).inc()
    return alerts

def get_prometheus_metrics():
    return generate_latest(), CONTENT_TYPE_LATEST
