from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"
    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    severity    = Column(String(50), nullable=False)
    status      = Column(String(50), default="open")
    source      = Column(String(100), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"
    id             = Column(Integer, primary_key=True, index=True)
    cpu_percent    = Column(Float, nullable=False)
    memory_percent = Column(Float, nullable=False)
    disk_percent   = Column(Float, nullable=False)
    recorded_at    = Column(DateTime, default=datetime.utcnow)
