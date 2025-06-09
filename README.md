# 🛒 Online Retail Dashboard

A Streamlit-powered sales dashboard for the [Online Retail](https://archive.ics.uci.edu/ml/datasets/Online+Retail) dataset, backed by PostgreSQL and Redis, containerized with Docker Compose.

---

## 🚀 Table of Contents

1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Tech Stack](#tech-stack)  
4. [Prerequisites](#prerequisites)  
5. [Getting Started](#getting-started)  
   - [Clone the repo](#clone-the-repo)  
   - [Configuration](#configuration)  
   - [Build & Run with Docker Compose](#build--run-with-docker-compose)  
6. [Project Structure](#project-structure)  
7. [Data Initialization](#data-initialization)  
8. [Usage](#usage)  
9. [Troubleshooting](#troubleshooting)  
10. [Contributing](#contributing)  

---

## 📝 Project Overview

This dashboard ingests transactional data from the Online Retail CSV, loads it into PostgreSQL (with staging tables, fact and dimension tables, materialized views), uses Redis for caching, and surfaces interactive analytics via Streamlit:

- **Daily sales summary**
- **7-day trend charts**
- **RFM customer segmentation**
- **Geographic revenue map**

---

## ⭐ Features

- 📊 **Sales Overview**: Min/max date selector, daily totals, and trend lines  
- 🔄 **Materialized Views**: Fast precomputed aggregates (`mv_daily_sales`)  
- 🛠️ **Caching**: Redis cache for repeated queries  
- 🗺️ **Country Insights**: Top-selling markets visualization  
- 🚀 **Containerized**: Single `docker-compose up --build`  

---

## 🛠 Tech Stack

- **Python 3.11** & [Streamlit](https://streamlit.io/)  
- **PostgreSQL 14** (Alpine) with initialization scripts  
- **Redis 6** for caching  
- **Docker Compose** for orchestration  
- **Pandas**, **SQLAlchemy**, **Altair**  

---

## 📋 Prerequisites

- Docker & Docker Desktop (Mac, Windows, or Linux)  
- Git (for cloning and version control)  

---

## 🏁 Getting Started

### Clone the repo

```bash
git clone https://github.com/mh2830720/online-retail-dashboard.git
cd online-retail-dashboard
```
### Add your CSV
Copy your OnlineRetail.csv into the db/init/ directory so that Postgres can load it on startup.

### Clean up previous data (only if re‐running initialization):

```bash
docker compose down -v
```
### Build & launch everything

```bash
docker compose up --build
```
### Open the dashboard
Navigate to http://localhost:8501 in your browser.

## 📂 Project Structure
.
├── README.md                 # ← this file
├── app.py                    # Streamlit dashboard code
├── Dockerfile                # Defines the Python app image
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Orchestrates app, db, redis
└── db
    └── init                  # SQL scripts auto‐run by Postgres
        ├── 01-create-tables.sql
        ├── 02-load-orders.sql
        ├── 03-create-mv.sql
        ├── 04-create-order-items.sql
        └── 05-create-dim-customer.sql

## 🔄 Data Initialization
On container startup, PostgreSQL executes each .sql in db/init/ in alphanumeric order:

- 01-create-tables.sql

     Defines staging (orders_stage) and final fact (fact_order) tables.

- 02-load-orders.sql

     Sets client_encoding = 'LATIN1'

     COPY OnlineRetail.csv into orders_stage

     INSERT transformed rows into fact_order

- 03-create-mv.sql

     Drops, creates, and refreshes the mv_daily_sales materialized view.

- 04-create-order-items.sql

     (If you supply OnlineRetailItems.csv) stages item‐level data and builds fact_order_item.

- 05-create-dim-customer.sql

     Builds dim_customer dimension from either orders_stage or fact_order.
##💡 Usage
- Date Picker: Select any date between first & last sale to view that day’s metrics.

- 7-Day Trend: See the trailing‐week sales chart.

- RFM Segmentation: Review customer Recency, Frequency, Monetary metrics.

- Geo Sales: Visualize revenue by customer country.

## 🐞 Troubleshooting

- No data in mv_daily_sales

     Ensure 02-load-orders.sql ran successfully—check for encoding or parsing errors.

     Re-initialize with docker compose down -v && docker compose up --build.

- CSV encoding errors

     Confirm your CSV uses Latin-1 or adjust the COPY encoding clause.

- Windows Docker “pipe” error

     Run Docker Desktop as Administrator or enable WSL2 integration.

- SSH / GitHub auth failures

     Accept GitHub’s host key when prompted, and add your public key to your GitHub account.
## 🤝 Contributing
1. Fork this repository.

2. Branch your feature:

```bash
git checkout -b feature/awesome-new-feature
```
3. Commit your changes & push:
```bash
git add .
git commit -m "Add awesome new feature"
git push origin feature/awesome-new-feature
```
4. Open a Pull Request.
