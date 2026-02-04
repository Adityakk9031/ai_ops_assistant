"""Weather API tool using OpenWeatherMap."""

import os
from typing import Dict, Any
from tools.base_tool import ToolInterface, ToolResponse


class WeatherTool(ToolInterface):
    """Tool for fetching weather data from OpenWeatherMap."""
    
    def __init__(self):
        super().__init__("WeatherTool")
        self.api_key = os.getenv("OPENWEATHER_KEY")
        if not self.api_key:
            self.logger.warning("OPENWEATHER_KEY not set")
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def call(self, args: Dict[str, Any]) -> ToolResponse:
        """
        Execute weather API operations.
        
        Supported operations:
        - current_weather: Get current weather for a city
        - forecast: Get weather forecast for a city
        
        Args:
            args: Dictionary with 'operation' and operation-specific parameters
            
        Returns:
            ToolResponse with weather data
        """
        operation = args.get("operation", "current_weather")
        
        try:
            if operation == "current_weather":
                return self._get_current_weather(
                    city=args.get("city", ""),
                    units=args.get("units", "metric")
                )
            elif operation == "forecast":
                return self._get_forecast(
                    city=args.get("city", ""),
                    units=args.get("units", "metric"),
                    cnt=args.get("cnt", 5)
                )
            else:
                return ToolResponse(ok=False, error=f"Unknown operation: {operation}")
        except Exception as e:
            return self._handle_error(e, f"Weather API error ({operation})")
    
    def _get_current_weather(self, city: str, units: str = "metric") -> ToolResponse:
        """Get current weather for a city."""
        if not city:
            return ToolResponse(ok=False, error="City parameter is required")
        
        if not self.api_key:
            return ToolResponse(ok=False, error="OPENWEATHER_KEY not configured")
        
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units
        }
        
        try:
            response = self._make_http_request("GET", url, params=params)
            data = response.json()
            
            weather_data = {
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "temperature": data.get("main", {}).get("temp"),
                "feels_like": data.get("main", {}).get("feels_like"),
                "temp_min": data.get("main", {}).get("temp_min"),
                "temp_max": data.get("main", {}).get("temp_max"),
                "humidity": data.get("main", {}).get("humidity"),
                "pressure": data.get("main", {}).get("pressure"),
                "conditions": data.get("weather", [{}])[0].get("main"),
                "description": data.get("weather", [{}])[0].get("description"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "clouds": data.get("clouds", {}).get("all"),
                "timestamp": data.get("dt"),
                "units": units
            }
            
            return ToolResponse(
                ok=True,
                status_code=response.status_code,
                data=weather_data
            )
        except Exception as e:
            if "404" in str(e):
                return ToolResponse(
                    ok=False,
                    status_code=404,
                    error=f"City '{city}' not found"
                )
            raise
    
    def _get_forecast(self, city: str, units: str = "metric", cnt: int = 5) -> ToolResponse:
        """Get weather forecast for a city."""
        if not city:
            return ToolResponse(ok=False, error="City parameter is required")
        
        if not self.api_key:
            return ToolResponse(ok=False, error="OPENWEATHER_KEY not configured")
        
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
            "cnt": min(cnt, 40)  # API max is 40
        }
        
        try:
            response = self._make_http_request("GET", url, params=params)
            data = response.json()
            
            forecasts = []
            for item in data.get("list", []):
                forecasts.append({
                    "timestamp": item.get("dt"),
                    "datetime": item.get("dt_txt"),
                    "temperature": item.get("main", {}).get("temp"),
                    "feels_like": item.get("main", {}).get("feels_like"),
                    "humidity": item.get("main", {}).get("humidity"),
                    "conditions": item.get("weather", [{}])[0].get("main"),
                    "description": item.get("weather", [{}])[0].get("description"),
                    "wind_speed": item.get("wind", {}).get("speed"),
                    "clouds": item.get("clouds", {}).get("all")
                })
            
            return ToolResponse(
                ok=True,
                status_code=response.status_code,
                data={
                    "city": data.get("city", {}).get("name"),
                    "country": data.get("city", {}).get("country"),
                    "forecasts": forecasts,
                    "units": units
                }
            )
        except Exception as e:
            if "404" in str(e):
                return ToolResponse(
                    ok=False,
                    status_code=404,
                    error=f"City '{city}' not found"
                )
            raise
