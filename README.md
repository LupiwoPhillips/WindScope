# WindScope — UK Wind Forecast Analysis

## Overview
WindScope is a web application for evaluating UK wind generation forecasts against actual generation. It helps an energy utility assess forecast error when making day-ahead electricity purchasing decisions.

## Features
- Select a delivery date range.
- Compare hourly wind generation forecasts with actual generation.
- View Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and forecast bias.
- Visualise forecast and actual generation in a time-series chart.
- Retrieve national wind data from the Elexon BMRS API.

## Data Sources
- Actual generation: [Elexon FUELHH API](https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream)
- Wind forecasts: [Elexon WINDFOR API](https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream)

Only Elexon national wind generation data is used.

## Methodology
1. Retrieve half-hourly wind generation actuals and hourly wind forecasts.
2. Average the two half-hourly actual readings into an hourly value, using complete hours only.
3. For each delivery day, select the latest forecast published before 00:00 UTC on that day.
4. Match forecasts with actuals for the same delivery hour.
5. Calculate forecast error as forecast minus actual.

Metrics:
- **MAE:** average absolute forecast error.
- **RMSE:** square root of mean squared forecast error; larger errors receive more weight.
- **Bias:** average signed error. Positive bias indicates overforecasting; negative bias indicates underforecasting.

### Example results
For 1–7 January 2026, the current implementation returned 168 matched hourly intervals:
- MAE: 2,245.53 MW
- RMSE: 2,680.23 MW
- Bias: +1,743.43 MW

These are results for the selected period, not a guarantee of future accuracy.

## Technology
- Frontend: React, Vite, Recharts
- Backend: Python, FastAPI, HTTPX
- Tests: Python `unittest`
- Containerisation: Docker and Docker Compose

## Project Structure
```text
backend/
  app/
    main.py
    services/
      analysis.py
      elexon.py
  tests/
    test_analysis.py
  requirements.txt
  Dockerfile
frontend/
  src/
  package.json
  Dockerfile
  nginx.conf
docker-compose.yml
README.md
```

## Run Locally

### Backend
From the project root, open a terminal:

```bash
cd backend
py -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at `http://127.0.0.1:8000`. Interactive API documentation is available at `/docs`.

### Frontend
Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Run backend tests
From the project root, activate the backend virtual environment, then run:

```bash
cd backend
python -m unittest discover -s tests -v
```

### Docker
With Docker Desktop installed and running, use the project root:

```bash
docker compose up --build
```

The frontend should be available at `http://localhost:5173`, with the backend at `http://localhost:8000`.

## API Endpoints
- `GET /health` — health check
- `GET /actuals/wind` — wind generation actuals
- `GET /forecasts/wind` — wind forecasts
- `GET /analysis/wind/day-ahead` — forecast accuracy analysis

## Deployment
The intended deployment is a Vercel frontend and a container-hosted Python backend. The deployed frontend must use `VITE_API_BASE_URL` pointing to the backend URL, and backend CORS must allow the deployed frontend origin.

Deployment URLs will be added after deployment.

## Limitations
- The day-ahead decision point is represented by the latest forecast published before 00:00 UTC on the delivery day.
- The analysis measures forecast accuracy, not electricity procurement cost or the optimal purchasing strategy.
- Only matching intervals with complete hourly actuals are included.
- Results depend on the availability and quality of Elexon data.

## AI Assistance Disclosure
ChatGPT was used to assist with planning, explanations, code review, troubleshooting, and documentation. Implementation, execution, and validation were carried out by the developer, including testing against Elexon data and running the application and tests.