"""Weather models for marine operations."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class WeatherForecast(Base, TimestampMixin):
    """Weather forecast data model."""

    __tablename__ = "weather_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Location
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    # Forecast timestamp
    forecast_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Weather parameters
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False)  # m/s
    wave_height: Mapped[float] = mapped_column(Float, nullable=False)  # meters
    wave_period: Mapped[float | None] = mapped_column(Float, nullable=True)  # seconds

    # Data source
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="external_api")

    def __repr__(self) -> str:
        """String representation of weather forecast."""
        return (
            f"<WeatherForecast("
            f"lat={self.latitude}, "
            f"lon={self.longitude}, "
            f"time={self.forecast_time}, "
            f"wave_height={self.wave_height}m, "
            f"wind_speed={self.wind_speed}"
            f")>"
        )
