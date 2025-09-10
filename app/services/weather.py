"""Simple weather service."""

import json
from datetime import UTC, datetime, timedelta

from app.schemas.weather import Location, WeatherDataPoint, WeatherForecast


class WeatherService:
    """Simple weather service that loads JSON data.
    This won't look like this in a prod setup, here it's just reading from the json file.
    """

    def __init__(self):
        """Load weather data from JSON file."""
        with open("weather-forecast.json") as f:
            self.data = json.load(f)

    async def get_forecast(
        self,
        lat: float,
        lon: float,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> WeatherForecast:
        """Get weather forecast with optional time filtering."""

        # Create location from JSON
        location = Location(
            lat=self.data["location"]["lat"], lon=self.data["location"]["lon"]
        )

        # Convert all forecast points
        forecast_points = []
        for point in self.data["forecast"]:
            # Parse the timestamp string to datetime
            timestamp_str = point["timestamp"]
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

            # Apply time filtering if specified
            if from_time is not None and to_time is not None:
                # Ensure comparison datetimes are timezone-aware
                if from_time.tzinfo is None:
                    from_time = from_time.replace(tzinfo=UTC)
                if to_time.tzinfo is None:
                    to_time = to_time.replace(tzinfo=UTC)

                # Skip if outside time range
                if not (from_time <= timestamp <= to_time):
                    continue

            forecast_point = WeatherDataPoint(
                timestamp=timestamp,
                wind_speed=point["wind_speed"],
                wave_height=point["wave_height"],
                wave_period=point["wave_period"],
            )
            forecast_points.append(forecast_point)

        return WeatherForecast(location=location, forecast=forecast_points)

    async def get_12_hour_forecast(self, lat: float, lon: float) -> WeatherForecast:
        """Get 12-hour forecast from current time."""
        now = datetime.now(UTC)
        end_time = now + timedelta(hours=12)
        return await self.get_forecast(lat, lon, now, end_time)


# Create global instance
weather_service = WeatherService()
