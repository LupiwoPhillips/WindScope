
from datetime import date

import httpx


BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
FUELHH_URL = f"{BASE_URL}/datasets/FUELHH/stream"
WINDFOR_URL = f"{BASE_URL}/datasets/WINDFOR/stream"


async def get_wind_actuals(
    start_date: date,
    end_date: date,
) -> list[dict]:
    """Fetch published FUELHH records and keep wind generation."""

    params = {
        "publishDateTimeFrom": f"{start_date.isoformat()}T00:00:00Z",
        "publishDateTimeTo": f"{end_date.isoformat()}T23:59:59Z",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(FUELHH_URL, params=params)
        response.raise_for_status()
        records = response.json()

    if not isinstance(records, list):
        raise ValueError("Unexpected response format from Elexon")

    wind_records = [
        record
        for record in records
        if record.get("fuelType") == "WIND"
    ]

    return wind_records

    
WINDFOR_URL = f"{BASE_URL}/datasets/WINDFOR/stream"


async def get_wind_forecasts(
    start_date: date,
    end_date: date,
) -> list[dict]:
    """Fetch wind forecast records published within a date range."""

    params = {
        "publishDateTimeFrom": f"{start_date.isoformat()}T00:00:00Z",
        "publishDateTimeTo": f"{end_date.isoformat()}T23:59:59Z",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(WINDFOR_URL, params=params)
        response.raise_for_status()
        records = response.json()

    if not isinstance(records, list):
        raise ValueError("Unexpected response format from Elexon")

    return records

