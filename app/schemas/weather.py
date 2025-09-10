"""Weather data schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class Location(BaseModel):
    """Geographic location."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class WeatherDataPoint(BaseModel):
    """Single weather forecast data point."""

    timestamp: datetime = Field(..., description="Forecast timestamp")
    wind_speed: float = Field(..., ge=0, description="Wind speed in m/s")
    wave_height: float = Field(..., ge=0, description="Wave height in meters")
    wave_period: float = Field(..., ge=0, description="Wave period in seconds")


class WeatherForecast(BaseModel):
    """Complete weather forecast response."""

    location: Location = Field(..., description="Forecast location")
    forecast: list[WeatherDataPoint] = Field(..., description="Forecast data points")


class WeatherRequest(BaseModel):
    """Weather forecast request."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    from_time: datetime | None = Field(None, description="Start time (defaults to now)")
    to_time: datetime | None = Field(
        None, description="End time (defaults to +12 hours)"
    )
