# 📊 AI-Powered Financial Risk & Collections Assistant

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

An end-to-end, production-grade financial analytics and automated collections intervention platform. The system processes loan portfolios to perform automated **Exploratory Data Analysis (EDA)**, construct **delinquency prediction models**, recommend personalized, compliant **collection strategies** (SMS, Email, Call, Workout Plans), and audit decisions using **Responsible AI fairness metrics**.

---

## 🎯 Key Features

* **Interactive EDA Dashboard:** Auto-analyzes uploaded credit portfolios, highlighting missing values, distribution anomalies, and correlations.
* **Risk Prediction Engine:** Train and compare machine learning models (Logistic Regression, Decision Trees, Random Forests) on custom credit portfolios.
* **Responsible AI Auditor:** Evaluates predictive models for bias across protected attributes (e.g., age, gender) using demographic parity and disparate impact ratios.
* **Intelligent Collections Dispatch:** Recommends optimal, automated intervention paths (SMS, Email, Phone Call, or customized Workout Plans) based on borrower risk level.
* **Executive PDF Report Generator:** Compile prediction audits and collection plans into downloadable, presentation-ready PDF reports.

---

## 🏗️ Architecture & Project Structure

The project follows a clean, modular architecture separating the frontend client application and backend API service:

```
financial-risk-assistant/
├── backend/                  # FastAPI Application Service
│   ├── api/                  # API Sub-routers, CORS configurations, & Middlewares
│   ├── config/               # Settings & Path constants
│   ├── database/             # SQLite ORM models & session configurations
│   ├── services/             # Core engines: EDA, ML Pipeline, Reports, Collections
│   ├── utils/                # PDF Report Generators & CSV helpers
│   └── requirements.txt      # Python backend packages list
├── frontend/                 # React SPA Client Application
│   ├── src/                  # Page components, Zustand store, client API
│   ├── tailwind.config.js    # Styling & Theme configurations
│   └── package.json          # Node modules list
└── docker-compose.yml        # Multi-container Orchestration configuration
```

---

## 🚀 Quick Start Guide

### Setup Method 1: Local Development (Recommended)

Make sure you have **Python 3.8+** and **Node.js 16+** installed on your system.

#### 1. Backend Setup (FastAPI)
Open your terminal and run:
```bash
# Navigate to the backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Generate mock dataset for testing
python utils/generate_mock_data.py

# Run the API server
python main.py
```
*The API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

#### 2. Frontend Setup (React)
Open a new terminal window and run:
```bash
# Navigate to the frontend directory
cd frontend

# Install packages
npm install

# Run the frontend dev server
npm run dev
```
*The client dashboard will run on [http://localhost:5173](http://localhost:5173).*

---

### Setup Method 2: Running via Docker Compose

To build and run the entire ecosystem (Frontend, Backend, and Database) in containers automatically:

```bash
# From the project root directory
docker-compose up --build -d
```

* **Frontend Dashboard:** [http://localhost](http://localhost)
* **Backend OpenAPI docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📊 Sample Dataset Format
If you wish to upload your own portfolio CSV file, ensure it has the following columns:
* `customer_id` (Text)
* `age` (Integer)
* `gender` (Text: `Male`/`Female`)
* `marital_status` (Text: `Single`/`Married`/`Divorced`)
* `annual_income` (Numeric)
* `credit_score` (Integer)
* `debt_to_income` (Numeric, e.g., 0.35)
* `days_past_due` (Integer)
* `outstanding_balance` (Numeric)
* `delinquent` (Binary target: `0` or `1`)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
