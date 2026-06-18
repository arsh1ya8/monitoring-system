markdown# Cloud Infrastructure Monitoring & Incident Management System

A production-style infrastructure monitoring system built with Python, Docker, and open-source DevOps tools. Monitors CPU, memory, disk, and database health in real-time with automatic incident detection and alerting.

## What This Project Does
- Monitors CPU, memory, and disk usage in real-time
- Automatically detects threshold breaches and creates incidents
- Stores incident history in a SQL Server database
- Visualizes metrics in Grafana dashboards
- Exposes metrics to Prometheus for time-series storage
- CI/CD pipeline via GitHub Actions

## Tech Stack

| Technology | Purpose |
|---|---|
| Python FastAPI | REST API and monitoring application |
| Docker & Docker Compose | Containerization and orchestration |
| SQL Server | Incident and metrics storage |
| Prometheus | Metrics collection and alerting |
| Grafana | Real-time dashboards and visualization |
| GitHub Actions | CI/CD pipeline |

## Getting Started

### Prerequisites
- Docker Desktop
- WSL2 (Windows) or Linux/Mac

### Run Locally

1. Clone the repo
```bash
git clone https://github.com/arsh1ya8/monitoring-system.git
cd monitoring-system
```

2. Create .env file
DB_PASSWORD=YourStrongPassword123!
GRAFANA_PASSWORD=admin123

3. Start all services
```bash
docker compose up --build -d
```

4. Create the database
```bash
docker exec -it monitoring-sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "YourStrongPassword123!" -No -Q "CREATE DATABASE monitoringdb"
```

5. Restart the app
```bash
docker restart monitoring-app
```

## Access the Services

| Service | URL |
|---|---|
| Monitoring Dashboard | http://localhost:8000/dashboard |
| API Documentation | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

## Alert Thresholds

| Metric | Warning | Critical |
|---|---|---|
| CPU | 75% | 90% |
| Memory | 80% | 95% |
| Disk | 85% | 95% |

## CI/CD Pipeline
GitHub Actions automatically runs on every push:
1. Installs Python dependencies
2. Runs import tests
3. Builds Docker image

## Stage 2 (Coming Soon)
- Kubernetes deployment (AKS)
- Terraform infrastructure as code
- Azure cloud hosting
