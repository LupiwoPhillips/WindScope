import unittest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from app.services.analysis import analyse_wind


class WindAnalysisTests(unittest.IsolatedAsyncioTestCase):
    async def test_latest_pre_delivery_forecast_and_metrics(self):
        delivery_date = date(2026, 1, 5)
        actuals = []
        forecasts = []

        for hour in range(24):
            start = datetime(
                2026, 1, 5, hour, 0, tzinfo=timezone.utc
            )

            # Two half-hour actuals average to 200 MW.
            for minute, generation in [(0, 100), (30, 300)]:
                interval = start + timedelta(minutes=minute)
                actuals.append({
                    "startTime": interval.isoformat().replace("+00:00", "Z"),
                    "generation": generation,
                    "fuelType": "WIND",
                    "publishTime": (
                        interval + timedelta(minutes=30)
                    ).isoformat().replace("+00:00", "Z"),
                })

            # Older forecast run: should not be selected.
            forecasts.append({
                "startTime": start.isoformat().replace("+00:00", "Z"),
                "publishTime": "2026-01-04T02:30:00Z",
                "generation": 9999,
            })

            # Latest forecast before delivery day: should be selected.
            forecasts.append({
                "startTime": start.isoformat().replace("+00:00", "Z"),
                "publishTime": "2026-01-04T22:30:00Z",
                "generation": 250,
            })

        with (
            patch(
                "app.services.analysis.get_wind_actuals",
                new=AsyncMock(return_value=actuals),
            ),
            patch(
                "app.services.analysis.get_wind_forecasts",
                new=AsyncMock(return_value=forecasts),
            ),
        ):
            result = await analyse_wind(delivery_date, delivery_date)

        self.assertEqual(result["matchedIntervals"], 24)
        self.assertEqual(result["metrics"]["maeMW"], 50.0)
        self.assertEqual(result["metrics"]["rmseMW"], 50.0)
        self.assertEqual(result["metrics"]["biasMW"], 50.0)
        self.assertEqual(result["records"][0]["forecastMW"], 250.0)
        self.assertEqual(result["records"][0]["actualMW"], 200.0)
        self.assertEqual(
            result["records"][0]["publishTime"],
            "2026-01-04T22:30:00Z",
        )

    async def test_incomplete_actual_hour_is_not_matched(self):
        delivery_date = date(2026, 1, 5)
        actuals = [{
            "startTime": "2026-01-05T00:00:00Z",
            "generation": 100,
            "fuelType": "WIND",
            "publishTime": "2026-01-05T00:30:00Z",
        }]

        forecasts = [{
            "startTime": "2026-01-05T00:00:00Z",
            "publishTime": "2026-01-04T22:30:00Z",
            "generation": 250,
        }]

        with (
            patch(
                "app.services.analysis.get_wind_actuals",
                new=AsyncMock(return_value=actuals),
            ),
            patch(
                "app.services.analysis.get_wind_forecasts",
                new=AsyncMock(return_value=forecasts),
            ),
        ):
            result = await analyse_wind(delivery_date, delivery_date)

        self.assertEqual(result["matchedIntervals"], 0)
        self.assertIsNone(result["metrics"])
        self.assertEqual(result["records"], [])


if __name__ == "__main__":
    unittest.main()
