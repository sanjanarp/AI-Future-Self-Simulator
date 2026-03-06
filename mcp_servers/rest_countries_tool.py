"""
MCP Tool Server: REST Countries API (Free, no key required)

Provides country-level data for relocation and immigration decisions:
population, languages, currencies, region, timezones, etc.

API Docs: https://restcountries.com/
"""

import re
import aiohttp

from mcp_framework import MCPTool, MCPToolResult, registry


class RESTCountriesTool(MCPTool):
    """Fetches country data for relocation/immigration context."""

    @property
    def name(self) -> str:
        return "restcountries"

    @property
    def description(self) -> str:
        return "REST Countries API — population, languages, currencies, timezone data for any country"

    @property
    def categories(self) -> list[str]:
        return [
            "Cost of Living",
            "Immigration & Visa",
        ]

    @property
    def api_base_url(self) -> str:
        return "https://restcountries.com/v3.1"

    async def invoke(
        self,
        decision: str,
        context: str,
        session: aiohttp.ClientSession,
    ) -> list[MCPToolResult]:
        results = []
        countries = self._extract_countries(decision, context)

        if not countries:
            return results

        for country_name in countries[:2]:
            data = await self._fetch_country(country_name, session)
            if data:
                results.append(self._format_result(data))

        return results

    async def _fetch_country(self, name: str, session: aiohttp.ClientSession) -> dict | None:
        """Fetch country data from REST Countries API."""
        url = f"https://restcountries.com/v3.1/name/{name}"
        params = {"fields": "name,capital,population,languages,currencies,region,subregion,timezones,flags"}
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and isinstance(data, list):
                        return data[0]
        except Exception:
            pass
        return None

    def _format_result(self, data: dict) -> MCPToolResult:
        """Format country API response into a research result."""
        common_name = data.get("name", {}).get("common", "Unknown")
        official_name = data.get("name", {}).get("official", common_name)
        capital = ", ".join(data.get("capital", ["N/A"]))
        population = data.get("population", 0)
        pop_str = f"{population:,}" if population else "N/A"
        region = data.get("region", "N/A")
        subregion = data.get("subregion", "")

        # Languages
        languages = data.get("languages", {})
        lang_str = ", ".join(languages.values()) if languages else "N/A"

        # Currencies
        currencies = data.get("currencies", {})
        currency_parts = []
        for code, info in currencies.items():
            currency_parts.append(f"{info.get('name', code)} ({code})")
        currency_str = ", ".join(currency_parts) if currency_parts else "N/A"

        # Timezones
        timezones = data.get("timezones", [])
        tz_str = ", ".join(timezones[:3]) if timezones else "N/A"

        snippet = (
            f"{official_name} — Capital: {capital}. Population: {pop_str}. "
            f"Region: {region}{f' ({subregion})' if subregion else ''}. "
            f"Languages: {lang_str}. Currency: {currency_str}. "
            f"Timezones: {tz_str}."
        )

        return MCPToolResult(
            tool_name=self.name,
            category="Immigration & Visa" if "visa" in snippet.lower() or "immigra" in snippet.lower() else "Cost of Living",
            title=f"Country Profile: {common_name}",
            snippet=snippet,
            source_url=f"https://restcountries.com/",
            confidence=0.95,
            raw_data=data,
        )

    def _extract_countries(self, decision: str, context: str) -> list[str]:
        """Extract country names from the decision text."""
        text = f"{decision} {context}".lower()
        country_map = {
            "usa": "united states", "us": "united states", "america": "united states",
            "uk": "united kingdom", "britain": "united kingdom", "england": "united kingdom",
            "canada": "canada", "germany": "germany", "deutschland": "germany",
            "france": "france", "australia": "australia", "india": "india",
            "japan": "japan", "singapore": "singapore", "dubai": "united arab emirates",
            "uae": "united arab emirates", "netherlands": "netherlands", "holland": "netherlands",
            "sweden": "sweden", "norway": "norway", "denmark": "denmark",
            "switzerland": "switzerland", "ireland": "ireland", "spain": "spain",
            "portugal": "portugal", "italy": "italy", "new zealand": "new zealand",
            "south korea": "south korea", "korea": "south korea",
            "brazil": "brazil", "mexico": "mexico", "china": "china",
        }

        found = []
        for trigger, country in country_map.items():
            # Use word boundary matching to avoid false positives
            if re.search(rf"\b{re.escape(trigger)}\b", text):
                if country not in found:
                    found.append(country)

        return found


# Auto-register
registry.register(RESTCountriesTool())
