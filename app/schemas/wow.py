"""Pydantic schemas for Wait on Weather (WoW) analysis."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampMixin
from app.schemas.weather import LocationBase, WeatherDataPoint


class WoWAnalysisRequest(LocationBase):
    """Request schema for Wait on Weather analysis."""
    
    task_id: int = Field(..., description="Task ID to analyze")
    forecast_hours: int = Field(
        default=12, 
        ge=1, 
        le=168, 
        description="Number of hours to analyze"
    )
    start_time: Optional[datetime] = Field(
        None, 
        description="Analysis start time (defaults to current time)"
    )


class WoWOperationalWindow(BaseSchema):
    """Operational window within WoW analysis."""
    
    start_index: int = Field(..., description="Start index in weather data")
    start_time: datetime = Field(..., description="Window start time")
    duration_hours: float = Field(..., description="Window duration in hours")
    end_time: datetime = Field(..., description="Window end time")
    
    # Weather conditions during window
    max_wave_height: float = Field(..., description="Maximum wave height in window")
    avg_wave_height: float = Field(..., description="Average wave height in window")
    
    # Suitability
    is_suitable: bool = Field(..., description="Whether window meets all constraints")


class WoWDecision(BaseSchema):
    """WoW analysis decision."""
    
    can_proceed: bool = Field(..., description="Whether task can proceed")
    recommendation: str = Field(..., description="Human-readable recommendation")
    
    # Timing recommendations
    earliest_start: Optional[datetime] = Field(None, description="Earliest safe start time")
    recommended_start: Optional[datetime] = Field(None, description="Recommended start time")


class WoWAnalysisResult(BaseSchema, TimestampMixin):
    """Complete WoW analysis result."""
    
    # Request parameters
    task_id: int = Field(..., description="Analyzed task ID")
    task_name: str = Field(..., description="Task name")
    location: LocationBase = Field(..., description="Analysis location")
    analysis_period_start: datetime = Field(..., description="Analysis period start")
    analysis_period_end: datetime = Field(..., description="Analysis period end")
    
    # Task parameters
    task_duration_hours: float = Field(..., description="Task duration in hours")
    wave_height_limit: float = Field(..., description="Task wave height limit")
    
    # Analysis results
    decision: WoWDecision = Field(..., description="Analysis decision")
    operational_windows: list[WoWOperationalWindow] = Field(
        default_factory=list, 
        description="Identified operational windows"
    )
    
    # Analysis metadata
    total_data_points: int = Field(..., description="Total weather data points analyzed")
    suitable_windows_count: int = Field(..., description="Number of suitable operational windows")
    go_no_go_signals: list[bool] = Field(..., description="Go/no-go signal for each data point")