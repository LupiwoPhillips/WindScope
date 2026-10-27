# WindScope — UK Wind Forecast Analysis

## Overview

WindScope is a web-based analytics application that evaluates UK wind generation forecasts against actual generation. It is designed to support an energy utility's day-ahead electricity purchasing decisions by making forecast performance measurable and transparent.

The application retrieves national wind generation data from the Elexon BMRS API, aligns forecasts with observed generation, and presents forecast accuracy metrics and time-series visualisations.

## Live Application

- **Frontend:** https://frontend-two-flax-sc1928rt0l.vercel.app/
- **Backend API:** https://windscope-dw6p.onrender.com
- **Interactive API documentation:** https://windscope-dw6p.onrender.com/docs
- **Source code:** https://github.com/LupiwoPhillips/WindScope

*Note: The backend is hosted on Render's free tier and may take a short time to respond after inactivity.*

## Business Objectives

The application addresses two key requirements:

1. **Forecast visibility:** Compare day-ahead wind generation forecasts with actual output for a selected delivery period.
2. **Forecast evaluation:** Quantify the difference between predicted and actual generation to help assess uncertainty in renewable energy supply.

The results provide evidence that can inform purchasing decisions. The application does not calculate optimal procurement volumes or electricity market costs.

## Features

- Select a delivery date range.
- Compare forecast and actual wind generation in a time-series chart.
- View Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and forecast bias.
- Inspect matched hourly forecast and actual generation records.
- Retrieve national wind generation data from Elexon.
- Access backend endpoints and interactive API documentation.

## Data Sources

The application uses Elexon BMRS data exclusively.

- **Actual generation:** [FUELHH API](https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream)
- **Wind generation forecasts:** [WINDFOR API](https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream)

Actual generation records are filtered to `fuelType == "WIND"`. Forecast records include delivery time, publication time, and forecast generation.

## Methodology

### 1. Retrieve the data

The backend retrieves actual wind generation and wind forecast records from the Elexon API for the requested period.

### 2. Prepare hourly actual generation

Actual generation is supplied at half-hourly resolution. The two half-hourly readings are averaged to produce an hourly actual value. Only hours containing both readings are retained.

### 3. Select the day-ahead forecast

For each delivery date, the application selects the latest forecast published before 00:00 UTC on that delivery date.

This represents a defined day-ahead decision cutoff. It is a modelling assumption for this analysis rather than a claim about every market participant's procurement deadline.

### 4. Match forecasts with actuals

Forecast and actual values are matched by delivery hour. Only intervals with both a selected forecast and a complete hourly actual are included in the evaluation.

### 5. Calculate forecast errors

Forecast error is defined as:

`Error = Forecast generation − Actual generation`

All generation values and errors are expressed in megawatts (MW).

### Accuracy metrics

- **Mean Absolute Error (MAE):** The average magnitude of forecast errors, ignoring their direction. Lower values indicate better average accuracy.
- **Root Mean Squared Error (RMSE):** The square root of the average squared error. This metric gives greater weight to large errors.
- **Bias:** The average signed error. Positive bias indicates that forecasts overestimated actual generation on average; negative bias indicates underestimation.

## Example Results — January 2026

For 1–7 January 2026, the application returned 168 matched hourly intervals.

| Metric | Result |
|---|---:|
| Matched hourly intervals | 168 |
| MAE | 2,245.53 MW |
| RMSE | 2,680.23 MW |
| Bias | +1,743.43 MW |

The positive bias indicates that forecast generation exceeded actual generation on average over the evaluated period. This is relevant to understanding forecast risk, but it does not independently determine the amount or cost of electricity that should be purchased.

These results describe the selected period and should not be interpreted as a guarantee of future forecast performance.

## Technology Stack

**Frontend**
- React
- Vite
- Recharts

**Backend**
- Python
- FastAPI
- HTTPX

**Testing and deployment**
- Python `unittest`
- Docker
- Docker Compose
- Vercel for the frontend
- Render for the backend API

## Project Structure

```text
WindScope/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── services/
│   │       ├── analysis.py
│   │       └── elexon.py
│   ├── tests/
│   │   └── test_analysis.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   ├── nginx.conf
│   └── vite.config.js
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Run Locally

### Prerequisites

- Python 3.13 or compatible Python 3 version
- Node.js and npm
- Git
- Docker Desktop, if running the containerised application

### Backend setup

From the project root, run:

```bash
cd backend
py -m venv .venv
```

Activate the environment in Git Bash on Windows:

```bash
source .venv/Scripts/activate
```

On macOS or Linux, use:

```bash
source .venv/bin/activate
```

Install dependencies and start the API:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend is available at `http://127.0.0.1:8000`.

Interactive API documentation: `http://127.0.0.1:8000/docs`.

### Frontend setup

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in a browser.

For local development, the Vite configuration proxies `/api` requests to the local backend. For a deployed frontend, configure the `VITE_API_BASE_URL` environment variable to point to the backend base URL.

### Run backend tests

From the project root:

```bash
cd backend
python -m unittest discover -s tests -v
```

### Run with Docker Compose

With Docker Desktop running, execute from the project root:

```bash
docker compose up --build
```

The frontend is exposed at `http://localhost:5173`, and the backend at `http://localhost:8000`.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| GET | `/actuals/wind` | Retrieve wind generation actuals |
| GET | `/forecasts/wind` | Retrieve wind forecasts |
| GET | `/analysis/wind/day-ahead` | Evaluate day-ahead forecast accuracy |

The analysis endpoint accepts `start_date` and `end_date` query parameters in `YYYY-MM-DD` format.

Example:

```text
/analysis/wind/day-ahead?start_date=2026-01-01&end_date=2026-01-07
```

## Deployment Configuration

The frontend is deployed on Vercel, and the Python API is deployed on Render.

The Vercel project uses:

- **Root directory:** `frontend`
- **Build command:** `npm run build`
- **Output directory:** `dist`
- **Environment variable:** `VITE_API_BASE_URL=https://windscope-dw6p.onrender.com`

The backend's CORS configuration allows requests from the deployed Vercel origin and local development origins.

## Limitations and Assumptions

- The analysis uses 00:00 UTC on the delivery date as the day-ahead forecast cutoff.
- Hourly actual generation is calculated by averaging two half-hourly readings.
- Incomplete actual hours and unmatched forecast intervals are excluded.
- Accuracy metrics describe the selected historical period; performance may differ across seasons and weather conditions.
- Forecast accuracy is not equivalent to procurement savings. Market prices, demand, other generation sources, and purchasing strategies are outside the scope of this application.
- Data availability and quality depend on the upstream Elexon service.

## AI Assistance Disclosure

ChatGPT was used as an AI development assistant to support planning, explanation of technical concepts, code review, troubleshooting, and documentation. The developer implemented and ran the application, validated the live API integration, executed tests, and verified the deployed dashboard.
