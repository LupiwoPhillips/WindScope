
import asyncio
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from math import sqrt

from app.services.elexon import get_wind_actuals, get_wind_forecasts


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


async def analyse_wind(start_date: date, end_date: date) -> dict:
    # Actual records can be published just after their delivery interval.
    # Fetch one extra publication day, then filter by delivery date.
    actuals_task = get_wind_actuals(start_date, end_date + timedelta(days=1))

    # Day-ahead forecasts are published on the preceding calendar day.
    forecasts_task = get_wind_forecasts(
        start_date - timedelta(days=1),
        end_date - timedelta(days=1),
    )

    actual_records, forecast_records = await asyncio.gather(
        actuals_task, forecasts_task
    )

    # Group half-hourly actuals into hourly averages.
    actual_groups = defaultdict(list)

    for record in actual_records:
        start = parse_timestamp(record["startTime"])
        if start_date <= start.date() <= end_date:
            hour_start = start.replace(minute=0, second=0, microsecond=0)
            actual_groups[hour_start].append(float(record["generation"]))

    actual_hourly = {
        hour: sum(values) / len(values)
        for hour, values in actual_groups.items()
        if len(values) == 2
    }

    # For each delivery hour, retain the latest forecast published
    # before that delivery date began (00:00 UTC).
    latest_forecasts = {}

    for record in forecast_records:
        delivery_start = parse_timestamp(record["startTime"])
        published = parse_timestamp(record["publishTime"])

        if not (start_date <= delivery_start.date() <= end_date):
            continue

        cutoff = datetime.combine(
            delivery_start.date(), time.min, tzinfo=timezone.utc
        )

        if published >= cutoff:
            continue

        key = delivery_start
        previous = latest_forecasts.get(key)

        if previous is None or published > parse_timestamp(previous["publishTime"]):
            latest_forecasts[key] = record

    # Compare forecasts and actuals for matching hourly intervals.
    comparisons = []

    for hour, forecast in sorted(latest_forecasts.items()):
        if hour not in actual_hourly:
            continue

        forecast_mw = float(forecast["generation"])
        actual_mw = actual_hourly[hour]
        error = forecast_mw - actual_mw

        comparisons.append({
            "startTime": hour.isoformat(),
            "publishTime": forecast["publishTime"],
            "forecastMW": round(forecast_mw, 2),
            "actualMW": round(actual_mw, 2),
            "errorMW": round(error, 2),
            "absoluteErrorMW": round(abs(error), 2),
        })

    if not comparisons:
        return {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "decisionRule": "Latest forecast published before delivery day, 00:00 UTC",
            "matchedIntervals": 0,
            "metrics": None,
            "records": [],
        }

    errors = [item["errorMW"] for item in comparisons]
    absolute_errors = [abs(error) for error in errors]

    mae = sum(absolute_errors) / len(errors)
    rmse = sqrt(sum(error**2 for error in errors) / len(errors))
    bias = sum(errors) / len(errors)

    return {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "decisionRule": "Latest forecast published before delivery day, 00:00 UTC",
        "matchedIntervals": len(comparisons),
        "metrics": {
            "maeMW": round(mae, 2),
            "rmseMW": round(rmse, 2),
            "biasMW": round(bias, 2),
        },
        "records": comparisons,
    }
