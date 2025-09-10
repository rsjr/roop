"""Wait on Weather (WoW) analysis service."""

from datetime import datetime, timedelta

from app.models.task import Task
from app.services.weather import weather_service


def wow_analysis(
    wave_height_series: list[float], task_duration: int, wave_height_limit: float
) -> tuple[list[bool], list[int]]:
    """
    Analyze wave height series to identify suitable windows for task execution.

    This is the core algorithm from the case study.

    Args:
        wave_height_series (list): List of wave height values
        task_duration (int): Required duration (number of consecutive data points)
        wave_height_limit (float): Maximum acceptable wave height

    Returns:
        tuple: (go_no_go_signals, start_indices)
        - go_no_go_signals: List of booleans indicating if conditions are met at each point
        - start_indices: List of indices where task can be started (beginning of valid windows)
    """
    n = len(wave_height_series)
    go_no_go_signals = []
    start_indices = []

    # Generate go/no-go signals for each data point
    for i in range(n):
        go_no_go_signals.append(wave_height_series[i] <= wave_height_limit)

    # Find valid start indices for task execution
    for i in range(n - task_duration + 1):
        # Check if the next task_duration points all satisfy the wave height limit
        valid_window = True
        for j in range(task_duration):
            if wave_height_series[i + j] > wave_height_limit:
                valid_window = False
                break

        if valid_window:
            start_indices.append(i)

    return go_no_go_signals, start_indices


class WoWAnalysisService:
    """Service for performing Wait on Weather analysis."""

    async def analyze_task(
        self, task: Task, lat: float, lon: float, forecast_hours: int = 12
    ) -> dict:
        """
        Perform WoW analysis for a specific task.

        Args:
            task: The task to analyze
            lat: Latitude for weather data
            lon: Longitude for weather data
            forecast_hours: Number of hours to analyze (default 12)

        Returns:
            Dictionary with analysis results
        """
        # Get weather forecast
        weather_forecast = await weather_service.get_forecast(lat, lon)

        # Extract wave height series from forecast
        wave_heights = [point.wave_height for point in weather_forecast.forecast]

        if not wave_heights:
            return {
                "task_id": task.id,
                "task_name": task.name,
                "can_proceed": False,
                "recommendation": "No weather data available",
                "analysis_time": datetime.utcnow().isoformat(),
                "forecast_data_points": 0,
                "operational_windows": [],
            }

        # Calculate task duration in data points (assuming 30-minute intervals)
        task_duration_points = max(1, int(task.duration_hours * 2))

        # Perform WoW analysis
        go_no_go_signals, start_indices = wow_analysis(
            wave_heights, task_duration_points, task.wave_height_limit
        )

        # Build operational windows
        operational_windows = []
        for start_idx in start_indices:
            if start_idx < len(weather_forecast.forecast):
                start_time = weather_forecast.forecast[start_idx].timestamp
                end_time = start_time + timedelta(hours=task.duration_hours)

                # Calculate window statistics
                window_wave_heights = wave_heights[
                    start_idx : start_idx + task_duration_points
                ]
                max_wave_height = max(window_wave_heights) if window_wave_heights else 0
                avg_wave_height = (
                    sum(window_wave_heights) / len(window_wave_heights)
                    if window_wave_heights
                    else 0
                )

                operational_windows.append(
                    {
                        "start_index": start_idx,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "duration_hours": task.duration_hours,
                        "max_wave_height": max_wave_height,
                        "avg_wave_height": round(avg_wave_height, 2),
                        "is_suitable": True,
                    }
                )

        # Generate recommendation
        can_proceed = len(start_indices) > 0

        if can_proceed:
            earliest_start = weather_forecast.forecast[start_indices[0]].timestamp
            recommendation = f"GO - {len(start_indices)} suitable weather window(s) found. Earliest start: {earliest_start.isoformat()}"
        else:
            recommendation = f"NO-GO - No suitable weather windows found. Wave height limit: {task.wave_height_limit}m"

        return {
            "task_id": task.id,
            "task_name": task.name,
            "task_duration_hours": task.duration_hours,
            "wave_height_limit": task.wave_height_limit,
            "can_proceed": can_proceed,
            "recommendation": recommendation,
            "analysis_time": datetime.utcnow().isoformat(),
            "forecast_data_points": len(wave_heights),
            "suitable_windows_count": len(start_indices),
            "operational_windows": operational_windows,
            "go_no_go_signals": go_no_go_signals,
            "weather_location": {
                "lat": weather_forecast.location.lat,
                "lon": weather_forecast.location.lon,
            },
        }


# Global WoW analysis service instance
wow_service = WoWAnalysisService()
