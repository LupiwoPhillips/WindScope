from datetime import date

from app.services.analysis import analyse_wind

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.services.elexon import get_wind_actuals, get_wind_forecasts

app = FastAPI(
    title="UK Wind Forecast Analysis",
    description="Analysis of UK wind generation forecasts and actuals.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "UK Wind Forecast Analysis API is running",
        "status": "ok",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}



@app.get("/forecasts/wind")
async def wind_forecasts(
    start_date: date = Query(..., description="First publication date"),
    end_date: date = Query(..., description="Last publication date"),
):
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date must be on or after start_date",
        )

    try:
        records = await get_wind_forecasts(start_date, end_date)
        return {
            "count": len(records),
            "records": records,
        }
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve data from Elexon",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@app.get("/analysis/wind/day-ahead")
async def day_ahead_wind_analysis(
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date must be on or after start_date",
        )

    try:
        return await analyse_wind(start_date, end_date)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve data from Elexon",
        ) from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unexpected data format returned by Elexon",
        ) from exc
