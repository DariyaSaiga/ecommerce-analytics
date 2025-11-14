# EcomVision Analytics

## 📊 About the Company
EcomVision Analytics is a data-driven company specializing in e-commerce insights.  
Our mission is to analyze online retail data and provide valuable recommendations for business growth, customer satisfaction, and sales optimization.

---

## 🎯 Project Overview

This repository contains a comprehensive data analytics and monitoring solution for e-commerce platforms, divided into multiple assignments covering different aspects of data engineering and system monitoring.

### Projects Included:
1. **Assignment 1-2**: SQL Database Analysis & Visualization (PostgreSQL + Python)
2. **Assignment 3**: Interactive BI Dashboards (Apache Superset)
3. **Assignment 4**: Real-time Monitoring & Alerting (Prometheus + Grafana)

---

## 📁 Project Structure

```
ecommerce-analytics/
├── __pycache__/
├── 3d_visual/                      
├── charts/
├── config/
├── dashboards/
├── dataset/
├── exports/
├── results/
├── screenshots/
├── venv/                            
├── 3d_model.py                  
├── 3d_model_saved.py                
├── analytics.py
├── Assignment.code-workspace
├── chart_create.py
├── config.py
├── custom_exporter.py
├── database_promql.txt
├── dataset.zip
├── docker-compose.yml
├── Dragon 2.5_ply.ply               
├── ERdiagram.png
├── main.py
├── queries.sql
├── README.md
├── requirements.txt
└── superset_config.py
```

---

## 🗄️ Assignment 1-2: Database Analysis

### Description
Analysis of the Brazilian Olist E-Commerce dataset exploring customer behavior, orders, payments, reviews, sellers, and product categories.

### Features
- ✅ SQL queries for meaningful insights extraction
- ✅ Static visualizations (sales, revenue, delivery, reviews)
- ✅ Interactive Plotly graphs with sliders
- ✅ Excel exports with formatting and conditional rules
- ✅ Dynamic updates: new data automatically reflects in reports

### ER Diagram
![The ER diagram (ERD)](__ERdiagram.png__)

### How to Run

#### Prerequisites
```bash
# Install required packages
pip install psycopg2-binary pandas plotly openpyxl matplotlib
```

#### Setup Database
1. Ensure PostgreSQL is running
2. Create database `ecommerce`
3. Import CSV files into tables

#### Run Scripts
```bash
# Generate static charts → saves to charts/
python3 charts_static.py

# Run interactive analysis → exports to exports/sales_report.xlsx
python3 analytics.py
```

### Output Files
- **Static charts**: `charts/` folder (PNG files)
- **Excel reports**: `exports/sales_report.xlsx` (with conditional formatting)
- **Query results**: `results/` folder (CSV files)
- **Screenshots**: `screenshots/` folder

---

## 📈 Assignment 3: Apache Superset Dashboards

### Description
Interactive BI dashboards for real-time business intelligence and data exploration.

### Features
- ✅ Interactive filters and drill-downs
- ✅ Real-time data visualization
- ✅ Multi-dimensional analysis
- ✅ Export-ready dashboard configurations

### Dashboards
- Sales Overview Dashboard
- Customer Analytics Dashboard
- Product Performance Dashboard

### Dashboard Files
- Exported dashboard JSONs available in `assignment3/dashboards/`
- Screenshots in `assignment3/screenshots/`

---

## 🔥 Assignment 4: Prometheus + Grafana Monitoring

### Description
Comprehensive monitoring solution with three dashboards covering database performance, system resources, and external API metrics.

### Architecture
```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  Exporters  │────>│  Prometheus  │────>│ Grafana │
└─────────────┘     └──────────────┘     └─────────�┘
     │                                         │
     ├── PostgreSQL Exporter (port 9187)      │
     ├── Node Exporter (port 9100)            │
     └── Custom Exporter (port 8000)          │
                                               │
                                          Dashboards
```

### Dashboard 1: PostgreSQL Database Monitoring (30 points)

**Metrics Monitored:**
1. Database availability (`pg_up`)
2. Active connections
3. Database size (GB)
4. Uptime (hours)
5. Transactions per second (TPS)
6. Total tables count
7. Total rows across all tables
8. Connection usage percentage
9. Transaction rollbacks rate
10. Top 5 largest tables

**PromQL Queries:**
```promql
# 1. Database Status
pg_up{instance="my_postgresql_db"}

# 2. Active Connections
pg_stat_database_numbackends{datname="ecommerce"}

# 3. Database Size (GB)
pg_database_size_bytes{datname="ecommerce"} / 1024 / 1024 / 1024

# 4. Uptime (hours)
(time() - process_start_time_seconds) / 3600

# 5. Transactions Per Second
rate(pg_stat_database_xact_commit{datname="ecommerce"}[5m])

# 6. Total Tables
count(pg_stat_user_tables_n_live_tup{datname="ecommerce"})

# 7. Total Rows
sum(pg_stat_user_tables_n_live_tup{datname="ecommerce"})

# 8. Connection Usage %
(sum(pg_stat_database_numbackends{datname="ecommerce"}) / 100) * 100

# 9. Rollback Rate
rate(pg_stat_database_xact_rollback{datname="ecommerce"}[5m])

# 10. Top 5 Tables
topk(5, pg_stat_user_tables_n_live_tup{datname="ecommerce"})
```

**Features:**
- ✅ Real-time database performance metrics
- ✅ Dashboard variable: database filter
- ✅ Alert: High connection usage (>80%)
- ✅ 10+ visualizations (Time series, Gauge, Stat, Bar chart)

---

### Dashboard 2: Node Exporter - System Monitoring (25 points)

**Metrics Monitored:**
1. CPU usage per core (%)
2. Load average (1m, 5m, 15m)
3. Memory: Total, Available, Used (GB)
4. RAM usage (%)
5. System uptime (hours)
6. Disk I/O: Read & Write (bytes/sec)
7. Network traffic: In/Out (Mbit/sec)
8. Context switches rate
9. Running processes count
10. File descriptor usage (%)

**PromQL Queries:**
```promql
# 1. CPU Usage per Core
100 - (rate(node_cpu_seconds_total{mode="idle"}[5m]) * 100)

# 2. Load Average
node_load1
node_load5
node_load15

# 3. RAM Usage %
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))

# 4. Memory Details (GB)
# Total
node_memory_MemTotal_bytes / 1024 / 1024 / 1024
# Available
node_memory_MemAvailable_bytes / 1024 / 1024 / 1024
# Used
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024 / 1024 / 1024

# 5. System Uptime (hours)
(time() - node_boot_time_seconds) / 3600

# 6. Disk I/O
# Read
rate(node_disk_read_bytes_total[5m])
# Write
rate(node_disk_written_bytes_total[5m])

# 7. Network Traffic (Mbit/sec)
# Incoming
rate(node_network_receive_bytes_total{device!="lo"}[5m]) * 8 / 1000000
# Outgoing
rate(node_network_transmit_bytes_total{device!="lo"}[5m]) * 8 / 1000000

# 8. Context Switches
rate(node_context_switches_total[5m])

# 9. Running Processes
node_procs_running

# 10. File Descriptors %
100 * (node_filefd_allocated / node_filefd_maximum)
```

**Features:**
- ✅ Real-time system resource monitoring
- ✅ Dashboard variable: instance filter
- ✅ Alert: High CPU usage (>80%)
- ✅ Load testing script included (`load_test.py`)
- ✅ Experiment: baseline → load → analysis documented

**Platform Notes (macOS):**
- CPU temperature and battery metrics are not available via standard Node Exporter on macOS
- These limitations are documented in the dashboard
- All other 8 metrics work correctly ✅

---

### Dashboard 3: Custom Exporter - Weather API (45 points)

**Description:**
Custom Python exporter collecting weather data from external API (OpenWeatherMap) for multiple cities in Kazakhstan.

**Metrics Monitored:**
1. Temperature (Celsius) - Astana
2. Average temperature (30min window)
3. Maximum pressure (1h window)
4. Average cloud cover (6h window)
5. API response time
6. Temperature by country (aggregated)
7. API status count (1h)
8. Average wind speed by city
9. Precipitation to temperature ratio
10. Top 3 warmest cities

**PromQL Queries:**
```promql
# 1. Current Temperature
weather_temperature_celsius{city="Astana"}

# 2. Average Temperature (30min)
avg_over_time(weather_temperature_celsius{city="Astana"}[30m])

# 3. Max Pressure (1h)
max_over_time(weather_pressure_hpa{city="Astana"}[1h])

# 4. Average Cloud Cover (6h)
avg_over_time(weather_cloud_cover_percent{city="Astana"}[6h])

# 5. API Response Time
avg_over_time(weather_api_response_time_seconds{city="Astana",country="Kazakhstan"}[5m])

# 6. Temperature by Country
sum(weather_temperature_celsius) by (country)

# 7. API Status Count
count_over_time(weather_api_status{city="Astana"}[1h])

# 8. Wind Speed by City
avg(weather_windspeed_kmh) by (city)

# 9. Precipitation/Temperature Ratio
avg_over_time(weather_precipitation_mm[6h]) / avg_over_time(weather_temperature_celsius[6h])

# 10. Top 3 Warmest Cities
topk(3, avg_over_time(weather_temperature_celsius[1h]))
```

**Features:**
- ✅ Custom Python exporter (`custom_exporter.py`)
- ✅ Real-time weather data collection
- ✅ Multiple cities monitoring (Astana, Almaty, Shymkent, etc.)
- ✅ API performance tracking
- ✅ Dashboard variable: city filter
- ✅ Alert: API response time >2s or temperature extremes

---

## 🚀 Quick Start - Assignment 4

### Prerequisites
- Docker & Docker Compose
- Python 3.8+
- PostgreSQL (running locally or accessible)

### 1. Setup Infrastructure

```bash
# Navigate to assignment4 folder
cd assignment4

# Start all services
docker-compose up -d

# Verify containers are running
docker-compose ps
```

**Expected output:**
```
NAME                  STATUS
prometheus            Up
postgres_exporter     Up
node_exporter         Up
grafana              Up
```

### 2. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin / admin |
| PostgreSQL Metrics | http://localhost:9187/metrics | - |
| Node Metrics | http://localhost:9100/metrics | - |
| Custom Exporter | http://localhost:8000/metrics | - |

### 3. Import Dashboards

1. Open Grafana: http://localhost:3000
2. Login: `admin` / `admin`
3. **Dashboards** → **New** → **Import**
4. Upload JSON files from `assignment4/dashboards/`:
   - `dashboard_1_postgres.json`
   - `dashboard_2_node.json`
   - `dashboard_3_custom.json`
5. Select **Prometheus** as data source
6. Click **Import**

### 4. Start Custom Exporter

```bash
# Install dependencies
pip3 install prometheus-client requests

# Set your OpenWeatherMap API key
export OPENWEATHER_API_KEY="your_api_key_here"

# Run exporter
python3 scripts/custom_exporter.py
```

### 5. Verify Everything Works

```bash
# Check Prometheus targets
# Open: http://localhost:9090/targets
# All should be UP (green)

# Check metrics are collected
# Prometheus UI → Graph → Execute queries from PromQL sections above

# Check Grafana dashboards show data
# http://localhost:3000 → Browse dashboards
```

---

## 🧪 Testing & Validation

### Load Testing (Dashboard 2)

```bash
# Test CPU load
python3 scripts/load_test.py --type cpu --duration 300

# Test Memory load
python3 scripts/load_test.py --type memory --duration 300 --memory-size 2

# Test Disk I/O
python3 scripts/load_test.py --type disk --duration 300

# Test all (recommended)
python3 scripts/load_test.py --type all --duration 300
```

**Expected behavior:**
- CPU usage increases >80% → Alert triggers
- Memory usage increases by 2GB+
- Disk I/O shows activity spikes
- Network shows traffic when downloading test files

### Alert Verification

1. Navigate to **Alerting** → **Alert rules** in Grafana
2. Verify alert rules exist for all 3 dashboards
3. Run load test to trigger alerts
4. Observe status changes: Normal → Pending → Firing

---

## 📊 Dashboard Features

### All Dashboards Include:

✅ **Dashboard Variables (Filters)**
- PostgreSQL: database selector
- Node Exporter: instance/host selector  
- Custom: city selector

✅ **Real-time Updates**
- Refresh interval: 10 seconds
- Auto-updating metrics
- Live data streaming

✅ **Alerts Configured**
- Dashboard 1: High database connections (>80%)
- Dashboard 2: High CPU usage (>80%)
- Dashboard 3: API response time >2s

✅ **Multiple Visualization Types**
- Time series graphs
- Gauges
- Stats panels
- Bar charts
- Tables

---

## 🛠️ Tools & Technologies

### Databases & Storage
- PostgreSQL 14+
- Prometheus TSDB

### Monitoring Stack
- Prometheus 2.45+
- Grafana 10.0+
- PostgreSQL Exporter
- Node Exporter
- Custom Python Exporter

### Development
- Python 3.8+
- Docker & Docker Compose
- Apache Superset

### Python Libraries
```
psycopg2-binary
pandas
plotly
openpyxl
matplotlib
prometheus-client
requests
numpy (for load testing)
```

---

## 📝 Configuration Files

### Prometheus Configuration
**File:** `assignment4/config/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres_exporter:9187']

  - job_name: 'node'
    static_configs:
      - targets: ['node_exporter:9100']

  - job_name: 'weather_api'
    static_configs:
      - targets: ['host.docker.internal:8000']
```

### Docker Compose Services

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"

  postgres_exporter:
    image: prometheuscommunity/postgres-exporter:latest
    ports:
      - "9187:9187"
    environment:
      DATA_SOURCE_NAME: "postgresql://user:pass@host:5432/ecommerce"

  node_exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
```

---

## 📸 Screenshots & Evidence

All project deliverables include screenshots demonstrating:

### Assignment 1-2
- SQL query execution in terminal
- CSV export results
- Static charts (matplotlib)
- Interactive Plotly visualizations
- Excel exports with formatting

### Assignment 3
- Apache Superset dashboards
- Interactive filters and drill-downs
- Dashboard configurations

### Assignment 4
- Prometheus targets (all UP)
- PromQL query execution
- Grafana dashboard panels
- Alert rules and statuses
- Load testing results (baseline → load → recovery)
- Dashboard variables in action

**Location:** `screenshots/` folders in respective assignment directories

---

## 🔍 Validation Checklist

### Assignment 4 Requirements ✅

#### Dashboard 1 - PostgreSQL (30 points)
- [x] 10 PromQL queries created
- [x] 60%+ queries use functions (rate, sum, count, time, topk)
- [x] All queries tested in Prometheus
- [x] Metrics collected for 1-5 hours
- [x] 10+ visualizations, 4+ types
- [x] Dashboard variable configured (database filter)
- [x] Alert added (high connections)
- [x] Real-time updates (10s refresh)
- [x] JSON exported to GitHub

#### Dashboard 2 - Node Exporter (25 points)
- [x] 10 required metrics implemented
- [x] 60%+ queries use functions
- [x] All queries tested
- [x] Load experiment conducted (baseline → load → analysis)
- [x] 10+ visualizations, 4+ types
- [x] Dashboard variable configured (instance filter)
- [x] Alert added (high CPU)
- [x] macOS limitations documented
- [x] JSON exported to GitHub

#### Dashboard 3 - Custom Exporter (45 points)
- [x] Custom Python exporter developed
- [x] 10+ custom metrics implemented
- [x] External API integration (OpenWeatherMap)
- [x] Update frequency: 20 seconds
- [x] 10+ PromQL queries with functions
- [x] 10+ visualizations, 4+ types
- [x] Dashboard variable configured (city filter)
- [x] Alert added (API performance)
- [x] JSON and code exported to GitHub

---

---

## 🆕 Assignment 5 — 3D Visualization & Geometry Processing (Open3D)

This assignment adds a full 3D processing pipeline based on **Open3D**, using a real triangulated mesh model (`Dragon 2.5_ply.ply`).  
The final script performs all visualization steps interactively and **automatically saves PNG images** for each stage into the `3d_visual/` directory.

### ✅ What was implemented

A complete 7-step 3D geometry workflow:

1. **Mesh Loading & Visualization**  
   - Loads the `.ply` model  
   - Prints mesh info (vertices, triangles, normals)  
   - Displays the original mesh and saves a screenshot  

2. **Mesh → Point Cloud Conversion**  
   - Uniform sampling of ~15,000 points  
   - Point normal estimation  
   - Visualization + PNG output  

3. **Poisson Surface Reconstruction**  
   - Generates a watertight reconstructed mesh  
   - Removes low-density artifacts  
   - Crops to bounding box  
   - Saves visualization  

4. **Voxelization**  
   - Adaptive voxel size selection (auto-tuned from bounding box)  
   - Converts voxel grid into small cube meshes for clear rendering  
   - Saves voxel visualization  

5. **Adding a Slicing Plane**  
   - Thin red plane positioned near model center  
   - Used for clipping in next step  
   - Saves visualization  

6. **Clipping by Plane**  
   - Removes all points on one side of the plane  
   - Produces a clipped point cloud  
   - Saves visualization  

7. **Color Gradient & Geometric Extremes**  
   - Applies a height-based (Z-axis) color gradient  
   - Finds lowest & highest points  
   - Marks them with blue/red spheres  
   - Saves final visualization  

### 📁 Files Added

- `3d_model_saved.py` — final script with automatic screenshot saving  
- `Dragon 2.5_ply.ply` — 3D model used in the assignment  
- `3d_visual/step1_*.png ... step7_*.png` — output images for all steps  

### ▶️ How to Run

```bash
pip install open3d numpy
python3 3d_model_saved.py

---

## 🤝 Contributing

This is an academic project for demonstration purposes.  
For questions or suggestions, please contact the repository owner.

---

## 📄 License

This project is created for educational purposes as part of university coursework.

---

## 👤 Author

**Student Name:** [Your Name]  
**Course:** Data Engineering / Business Intelligence  
**University:** [Your University]  
**Year:** 2024-2025

---

## 🙏 Acknowledgments

- **Dataset:** Brazilian E-Commerce Public Dataset by Olist (Kaggle)
- **Tools:** PostgreSQL, Prometheus, Grafana, Apache Superset
- **Technologies:** Docker, Python, SQL

---

## 📚 Additional Resources

### Documentation Links
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter)
- [Node Exporter](https://github.com/prometheus/node_exporter)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)

### Dataset Information
- [Olist E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

**Last Updated:** November 2024  
**Version:** 1.0.0  
**Status:** ✅ All assignments completed and validated