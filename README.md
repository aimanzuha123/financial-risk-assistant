# AI-Powered Financial Risk & Collections Assistant

A complete, production-quality financial analytics and collections intervention platform. It automates Exploratory Data Analysis, constructs delinquency prediction models (Logistic Regression, Decision Trees, Random Forests), recommends personalized collections actions (SMS, Email, phone call, workout plans), and implements Responsible AI guidelines.

## Architecture

The application is structured into modular layers adhering to clean architecture:

- **Frontend:** React + Vite + Tailwind CSS + Recharts
- **Backend:** Python + FastAPI + Uvicorn + SQLite + Scikit-learn

```
financial-risk-assistant/
├── backend/                  # FastAPI REST endpoints
│   ├── api/                  # Sub-routers & Middlewares
│   ├── config/               # Settings & Path constants
│   ├── database/             # SQLite ORM models & session configurations
│   ├── services/             # Core engines: EDA, ML Pipeline, Reports, Collections
│   ├── utils/                # PDF Report Generators & CSV helpers
│   └── requirements.txt      # Python backend packages list
├── frontend/                 # React client application
│   ├── src/                  # Page routers, Zustand state store, client api
│   ├── tailwind.config.js    # Styling configurations
│   └── package.json          # Node modules list
└── docker-compose.yml        # Orchestration configurations
```

## Running the Application

### 1. Local Run (Recommended)

#### Backend Setup
Navigate to the `backend` folder, set up a virtual environment, and install dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# or: source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python main.py
```
*The backend API will run on http://localhost:8000.*

#### Generate Mock Data
Prior to uploading your custom CSV files, you can generate a demo dataset with:
```bash
python utils/generate_mock_data.py
```
This generates `sample_portfolio.csv` in `backend/data/uploads/`.

#### Frontend Setup
Open another terminal, navigate to the `frontend` folder, and launch:

```bash
cd frontend
npm install
npm run dev
```
*The client dashboard will run on http://localhost:5173.*

### 2. Run via Docker Compose
Build and run the entire ecosystem in containers:

```bash
docker-compose up --build
```
- Access Frontend: http://localhost
- Access Backend OpenAPI docs: http://localhost:8000/docs
