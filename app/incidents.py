from datetime import datetime
from sqlalchemy.orm import Session
from models import Incident, MetricSnapshot
from metrics import incident_counter

def create_incident(db: Session, title: str, description: str, severity: str, source: str) -> Incident:
    existing = (
        db.query(Incident)
        .filter(Incident.source == source, Incident.status == "open")
        .first()
    )
    if existing:
        return existing

    incident = Incident(
        title=title,
        description=description,
        severity=severity,
        status="open",
        source=source,
        created_at=datetime.utcnow(),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    incident_counter.inc()
    return incident

def resolve_incident(db: Session, source: str):
    incident = (
        db.query(Incident)
        .filter(Incident.source == source, Incident.status == "open")
        .first()
    )
    if not incident:
        return None
    incident.status      = "resolved"
    incident.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident

def get_all_incidents(db: Session, limit: int = 50) -> list:
    return (
        db.query(Incident)
        .order_by(Incident.created_at.desc())
        .limit(limit)
        .all()
    )

def save_metric_snapshot(db: Session, cpu: float, memory: float, disk: float):
    snapshot = MetricSnapshot(
        cpu_percent=cpu,
        memory_percent=memory,
        disk_percent=disk,
        recorded_at=datetime.utcnow(),
    )
    db.add(snapshot)
    db.commit()
