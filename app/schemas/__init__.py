"""Pydantic schemas for API request/response validation."""

from app.schemas.base import (
    BaseSchema,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
    SuccessResponse,
    TimestampMixin,
)
from app.schemas.task import (
    TaskBase,
    TaskCreate,
    TaskResponse,
    TaskScheduleResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.schemas.weather import (
    ExternalWeatherResponse,
    LocationBase,
    WeatherDataPoint,
    WeatherForecastRequest,
    WeatherForecastResponse,
)
from app.schemas.wow import (
    WoWAnalysisRequest,
    WoWAnalysisResult,
    WoWDecision,
    WoWOperationalWindow,
)

__all__ = [
    # Base schemas
    "BaseSchema",
    "TimestampMixin",
    "PaginationParams",
    "PaginatedResponse",
    "ErrorDetail",
    "ErrorResponse",
    "SuccessResponse",
    
    # Task schemas
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskStatusUpdate",
    "TaskResponse",
    "TaskScheduleResponse",
    
    # Weather schemas
    "LocationBase",
    "WeatherDataPoint",
    "WeatherForecastRequest",
    "WeatherForecastResponse",
    "ExternalWeatherResponse",
    
    # WoW analysis schemas
    "WoWAnalysisRequest",
    "WoWAnalysisResult",
    "WoWDecision",
    "WoWOperationalWindow",
]