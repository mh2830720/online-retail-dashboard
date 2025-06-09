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
11. [License](#license)

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
