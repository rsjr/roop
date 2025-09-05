"""Pydantic schemas for weather operations."""

from datetime import datetime
from typing import Optional

from pydantic import Field, validator

from app.schemas.base import BaseSchema, TimestampMixin


class LocationBase(BaseSchema):
    """Base location schema."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class WeatherDataPoint(BaseSchema):
    """Single weather data point."""
    
    timestamp: datetime = Field(..., description="Weather data timestamp")
    wind_speed: float = Field(..., ge=0, description="Wind speed in m/s")
    wave_height: float = Field(..., ge=0, description="Wave height in meters")
    wave_period: Optional[float] = Field(None, ge=0, description="Wave period in seconds")


class WeatherForecastRequest(LocationBase):
    """Request schema for weather forecast."""
    
    start_time: datetime = Field(..., description="Forecast start time")
    end_time: datetime = Field(..., description="Forecast end time")
    
    @validator("end_time")
    def validate_time_range(cls, v: datetime, values: dict) -> datetime:
        """Validate that end_time is after start_time."""
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class WeatherForecastResponse(LocationBase, TimestampMixin):
    """Response schema for weather forecast."""
    
    forecast_data: list[WeatherDataPoint] = Field(..., description="Weather forecast data points")
    source: str = Field(..., description="Data source")
    
    @property
    def data_point_count(self) -> int:
        """Number of data points in the forecast."""
        return len(self.forecast_data)
    
    @property
    def forecast_duration_hours(self) -> float:
        """Forecast duration in hours."""
        if len(self.forecast_data) < 2:
            return 0.0
        
        start = self.forecast_data[0].timestamp
        end = self.forecast_data[-1].timestamp
        return (end - start).total_seconds() / 3600


class ExternalWeatherResponse(BaseSchema):
    """Schema for external weather API response."""
    
    location: LocationBase = Field(..., description="Location coordinates")
    forecast: list[WeatherDataPoint] = Field(..., description="Forecast data")