"""
MCP Tool Server: Open-Meteo Weather API (Free, no key required)

Provides current weather and climate data — useful for relocation
decisions where climate is a factor.

API Docs: https://open-meteo.com/en/docs
"""

import re
import aiohttp

from mcp_framework import MCPTool, MCPToolResult, registry


# City coordinates for common relocation targets
CITY_COORDS: dict[str, tuple[float, float]] = {
    "new york": (40.7128, -74.0060),
    "san francisco": (37.7749, -122.4194),
    "los angeles": (34.0522, -118.2437),
    "seattle": (47.6062, -122.3321),
    "austin": (30.2672, -97.7431),
    "denver": (39.7392, -104.9903),
    "chicago": (41.8781, -87.6298),
    "boston": (42.3601, -71.0589),
    "miami": (25.7617, -80.1918),
    "portland": (45.5152, -122.6784),
    "nashville": (36.1627, -86.7816),
    "atlanta": (33.7490, -84.3880),
    "london": (51.5074, -0.1278),
    "berlin": (52.5200, 13.4050),
    "paris": (48.8566, 2.3522),
    "amsterdam": (52.3676, 4.9041),
    "toronto": (43.6532, -79.3832),
    "vancouver": (49.2827, -123.1207),
    "singapore": (1.3521, 103.8198),
    "tokyo": (35.6762, 139.6503),
    "sydney": (-33.8688, 151.2093),
    "melbourne": (-37.8136, 144.9631),
    "dubai": (25.2048, 55.2708),
    "bangalore": (12.9716, 77.5946),
    "mumbai": (19.0760, 72.8777),
    "munich": (48.1351, 11.5820),
    "zurich": (47.3769, 8.5417),
    "dublin": (53.3498, -6.2603),
    "lisbon": (38.7223, -9.1393),
    "barcelona": (41.3874, 2.1686),
    "stockholm": (59.3293, 18.0686),
    "oslo": (59.9139, 10.7522),
    "copenhagen": (55.6761, 12.5683),
    "seoul": (37.5665, 126.9780),
    "raleigh": (35.7796, -78.6382),
    "salt lake city": (40.7608, -111.8910),
}


class OpenMeteoTool(MCPTool):
    """Fetches climate/weather data for relocation decisions."""

    @property
    def name(self) -> str:
        return "open_meteo"

    @property
    def description(self) -> str:
        return "Open-Meteo weather API — current conditions and climate averages for cities worldwide"

    @property
    def categories(self) -> list[str]:
        return [
            "Cost of Living",
        ]

    @property
    def api_base_url(self) -> str:
        return "https://api.open-meteo.com/v1"

    async def invoke(
        self,
        decision: str,
        context: str,
        session: aiohttp.ClientSession,
    ) -> list[MCPToolResult]:
        results = []
        cities = self._extract_cities(decision, context)

        if not cities:
            return results

        for city_name, (lat, lon) in cities[:2]:
            weather = await self._fetch_weather(lat, lon, session)
            if weather:
                results.append(self._format_result(city_name, weather))

        return results

    async def _fetch_weather(
        self,
        lat: float,
        lon: float,
        session: aiohttp.ClientSession,
    ) -> dict | None:
        """Fetch current weather from Open-Meteo API."""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,sunshine_duration",
            "timezone": "auto",
            "forecast_days": 7,
        }
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            pass
        return None

    def _format_result(self, city: str, data: dict) -> MCPToolResult:
        """Format weather data into a research result."""
        current = data.get("current", {})
        daily = data.get("daily", {})

        temp = current.get("temperature_2m", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        wind = current.get("wind_speed_10m", "N/A")

        # Calculate weekly averages from daily data
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])

        avg_high = round(sum(max_temps) / len(max_temps), 1) if max_temps else "N/A"
        avg_low = round(sum(min_temps) / len(min_temps), 1) if min_temps else "N/A"
        total_precip = round(sum(precip), 1) if precip else "N/A"

        # Convert to Fahrenheit for US context
        def c_to_f(c):
            return round(c * 9 / 5 + 32, 1) if isinstance(c, (int, float)) else c

        snippet = (
            f"Current: {c_to_f(temp)}°F ({temp}°C), "
            f"Humidity: {humidity}%, Wind: {wind} km/h. "
            f"7-day forecast avg high: {c_to_f(avg_high)}°F ({avg_high}°C), "
            f"avg low: {c_to_f(avg_low)}°F ({avg_low}°C). "
            f"7-day precipitation: {total_precip}mm."
        )

        return MCPToolResult(
            tool_name=self.name,
            category="Cost of Living",
            title=f"Weather & Climate: {city.title()}",
            snippet=snippet,
            source_url="https://open-meteo.com/",
            confidence=0.95,
            raw_data={"current": current},
        )

    def _extract_cities(self, decision: str, context: str) -> list[tuple[str, tuple[float, float]]]:
        """Extract city names that we have coordinates for."""
        text = f"{decision} {context}".lower()
        found = []
        for city, coords in CITY_COORDS.items():
            if city in text:
                found.append((city, coords))
        return found


# Auto-register
registry.register(OpenMeteoTool())
