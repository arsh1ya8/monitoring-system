# Cloud Infrastructure Monitoring & Incident Management System

A full-stack cloud-native monitoring system that tracks CPU, memory, and disk metrics in real time, automatically creates incidents when thresholds are breached, and displays everything on a live dashboard.

## Stage 1 - Local Stack (Complete)

### Tech Stack
- Python FastAPI
- SQL Server (pymssql)
- Prometheus
- Grafana
- Docker Compose
- GitHub Actions CI/CD

### Screenshots
![Dashboard](screenshots/infrastructure%20monitoring%20snapshot%20dashboard%20.jpg)
![Grafana](screenshots/infrastructure%20monitoring%20snapshot%20grafana%20.jpg)
![Prometheus](screenshots/infrastructure%20monitoring%20snapshot%20prometheus%20-%20Graph%20.jpg)
![GitHub Actions](screenshots/infrastructure%20monitoring%20snapshot%20github%20actions%20.jpg)

## Stage 2 - Azure AKS Deployment (Complete)

### Tech Stack
- Microsoft Azure
- Azure AKS (Kubernetes)
- Azure Container Registry
- Terraform (IaC)
- kubectl

### Live URLs
- Dashboard: http://48.211.151.56/dashboard
- Grafana: http://20.72.78.164

### What Terraform Provisions
- Azure Resource Group (monitoring-rg)
- AKS Cluster (monitoring-aks) - East US 2 - Standard_D2s_v3
- Azure Container Registry (monitoringregistry2024)

### Kubernetes Resources
- 4 Deployments: monitoring-app, sqlserver, prometheus, grafana
- 2 LoadBalancer Services (app + grafana)
- 2 ClusterIP Services (prometheus + sqlserver)
- 1 PersistentVolumeClaim: 5Gi for SQL Server

### Screenshots
![AKS Dashboard](screenshots/stage%202%20infrastructure%20monitoring%20dashboard%20on%20cloud.jpg)
![Grafana on AKS](screenshots/stage%202%20infrastructure%20monitoring%20snapshot%20grafana%20.jpg)
![Azure Resources](screenshots/stage%202%20infrastructure%20monitoring%20azure%20resource%20.jpg)
