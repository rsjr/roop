"""Base Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of items to return")


class PaginatedResponse(BaseSchema):
    """Paginated response wrapper."""
    
    items: list[Any] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    skip: int = Field(..., ge=0, description="Number of items skipped")
    limit: int = Field(..., ge=1, description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more items")
    
    @classmethod
    def create(
        cls,
        items: list[Any],
        total: int,
        skip: int,
        limit: int,
    ) -> "PaginatedResponse":
        """Create paginated response."""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total,
        )


class ErrorDetail(BaseSchema):
    """Error detail schema."""
    
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    field: str | None = Field(None, description="Field that caused the error")


class ErrorResponse(BaseSchema):
    """Error response schema."""
    
    error: bool = Field(True, description="Indicates this is an error response")
    message: str = Field(..., description="Main error message")
    details: list[ErrorDetail] | None = Field(None, description="Detailed error information")
    request_id: str | None = Field(None, description="Request ID for tracking")


class SuccessResponse(BaseSchema):
    """Success response schema."""
    
    success: bool = Field(True, description="Indicates successful operation")
    message: str = Field(..., description="Success message")
    data: Any | None = Field(None, description="Response data")