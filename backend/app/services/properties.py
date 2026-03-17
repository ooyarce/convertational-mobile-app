import json
from typing import Any

import httpx

from app.config import settings


def _summarize_property(prop: dict) -> dict:
    """Extract only the fields the LLM needs to answer the user."""
    summary: dict[str, Any] = {}

    for key in ("id", "title", "type", "operation", "currency", "currencyId", "price", "offerPrice"):
        if key in prop and prop[key] is not None:
            summary[key] = prop[key]

    # Features (API returns nested features object)
    features = prop.get("features") or {}
    for key in ("bedrooms", "bathrooms", "halfBathrooms", "parkplaces",
                "warehouses", "buildSize", "lotSize", "coveredSpace",
                "floor", "orientation"):
        val = features.get(key) if features else prop.get(key)
        if val is not None:
            summary[key] = val

    # Fallback: flat fields (some API responses use flat structure)
    for key in ("surfaceTotal", "surfaceBuilt", "bedrooms", "bathrooms", "parkings"):
        if key in prop and prop[key] is not None and key not in summary:
            summary[key] = prop[key]

    # Location
    loc = prop.get("location") or {}
    if isinstance(loc, dict):
        parts = [loc.get("address"), loc.get("name"), loc.get("commune"),
                 loc.get("city"), loc.get("region")]
        location_str = ", ".join(p for p in parts if p)
        if location_str:
            summary["location"] = location_str

    # First image only
    images = prop.get("images") or []
    if images:
        summary["image"] = images[0] if isinstance(images[0], str) else images[0].get("url", "")

    # Public URL
    if prop.get("marketplaceUrl"):
        summary["url"] = prop["marketplaceUrl"]
    elif prop.get("publicUrl"):
        summary["url"] = prop["publicUrl"]

    return summary


def _summarize_property_detail(prop: dict) -> dict:
    """Summarize a single property detail, keeping description."""
    summary = _summarize_property(prop)

    for key in ("description", "address", "yearBuilt"):
        val = prop.get(key)
        if val:
            summary[key] = val

    # Features extras
    features = prop.get("features") or {}
    if features.get("constructionYears"):
        summary["constructionYears"] = features["constructionYears"]
    if features.get("others"):
        summary["otherFeatures"] = features["others"]

    # Contact info
    contact = prop.get("contact") or {}
    if contact:
        summary["contact"] = {k: v for k, v in contact.items() if v}

    return summary


class PropertiesClient:
    """HTTP client for the Properties API provided by Property Partners."""

    def __init__(self) -> None:
        self._base_url = settings.properties_api_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {settings.properties_api_token}",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=settings.request_timeout,
        )

    async def search_locations(
        self,
        country_id: str = "CL",
        search: str = "",
        location_type: str = "commune",
    ) -> str:
        """Search locations to get keyNames for property filtering."""
        params: dict[str, Any] = {"countryId": country_id, "search": search}
        if location_type:
            params["type"] = location_type

        async with self._client() as client:
            response = await client.get("/locations", params=params)
            response.raise_for_status()
            return json.dumps(response.json(), ensure_ascii=False)

    async def list_properties(
        self,
        location_key_name: str | None = None,
        property_type: str | None = None,
        operation: str | None = None,
        bedrooms_min: int | None = None,
        bathrooms_min: int | None = None,
        parkplaces_min: int | None = None,
        price_max: float | None = None,
        currency_id: str | None = None,
        build_size_min: float | None = None,
        sort: str | None = None,
        page: int = 1,
        page_limit: int = 5,
    ) -> str:
        """List properties with optional filters."""
        params: dict[str, Any] = {"page": page, "pageLimit": page_limit}

        if location_key_name:
            params["locationKeyName"] = location_key_name
        if property_type:
            params["type"] = property_type
        if operation:
            params["operation"] = operation
        if bedrooms_min is not None:
            params["bedroomsMin"] = bedrooms_min
        if bathrooms_min is not None:
            params["bathroomsMin"] = bathrooms_min
        if parkplaces_min is not None:
            params["parkplacesMin"] = parkplaces_min
        if price_max is not None:
            params["priceMax"] = price_max
        if currency_id:
            params["currencyId"] = currency_id
        if build_size_min is not None:
            params["buildSizeMin"] = build_size_min
        if sort:
            params["sort"] = sort

        async with self._client() as client:
            response = await client.get("/properties", params=params)
            response.raise_for_status()
            data = response.json()

        # Trim properties to essential fields to stay within LLM token limits
        # API returns { properties: [...], pagination: {...} }
        if isinstance(data, dict) and "properties" in data:
            pagination = data.get("pagination", {})
            data = {
                "properties": [_summarize_property(p) for p in data["properties"]],
                "total": pagination.get("total", 0),
                "page": pagination.get("page", page),
                "maxPages": pagination.get("maxPages", 1),
            }
        elif isinstance(data, dict) and "data" in data:
            data["data"] = [_summarize_property(p) for p in data["data"]]
            data = {
                "properties": data["data"],
                "total": data.get("total", 0),
                "page": data.get("page", page),
                "maxPages": data.get("maxPages", 1),
            }
        elif isinstance(data, list):
            data = {"properties": [_summarize_property(p) for p in data]}

        return json.dumps(data, ensure_ascii=False)

    async def get_property_detail(self, property_id: str) -> str:
        """Get full details of a specific property by ID."""
        async with self._client() as client:
            response = await client.get(f"/properties/{property_id}")
            response.raise_for_status()
            data = response.json()

        # API returns { property: {...}, success: bool }
        prop = data.get("property", data) if isinstance(data, dict) else data
        if isinstance(prop, dict):
            prop = _summarize_property_detail(prop)

        return json.dumps(prop, ensure_ascii=False)


properties_client = PropertiesClient()


# Fixed exchange rate: 1 UF = 40,000 CLP
UF_TO_CLP = 40_000


async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> str:
    """Convert between UF and CLP using a fixed rate (1 UF = 40,000 CLP)."""
    if from_currency == to_currency:
        return json.dumps({"amount": amount, "currency": to_currency})

    if from_currency == "CLP" and to_currency == "UF":
        converted = round(amount / UF_TO_CLP, 2)
    elif from_currency == "UF" and to_currency == "CLP":
        converted = round(amount * UF_TO_CLP, 0)
    else:
        return json.dumps({"error": f"Conversion {from_currency} → {to_currency} not supported"})

    return json.dumps({
        "original": {"amount": amount, "currency": from_currency},
        "converted": {"amount": converted, "currency": to_currency},
        "rate": f"1 UF = {UF_TO_CLP:,} CLP",
    }, ensure_ascii=False)
