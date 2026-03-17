"""Tests for Properties API client — hits the real API to verify integration."""
import json

import pytest

from app.services.properties import properties_client


@pytest.mark.asyncio
class TestPropertiesClient:
    async def test_search_locations(self):
        result = await properties_client.search_locations(
            country_id="CL", search="las condes", location_type="commune"
        )
        data = json.loads(result)
        assert "locations" in data
        assert len(data["locations"]) > 0

        location = data["locations"][0]
        assert "keyName" in location
        assert "las-condes" in location["keyName"]
        assert location["type"] == "commune"

    async def test_search_locations_no_results(self):
        result = await properties_client.search_locations(
            country_id="CL", search="zzzznonexistent"
        )
        data = json.loads(result)
        assert "locations" in data
        assert len(data["locations"]) == 0

    async def test_list_properties(self):
        result = await properties_client.list_properties(
            location_key_name="cl/region-metropolitana/las-condes",
            property_type="APARTMENT",
            operation="SELL",
            page_limit=2,
        )
        data = json.loads(result)
        assert "properties" in data
        assert "pagination" in data
        assert len(data["properties"]) > 0

        prop = data["properties"][0]
        assert "id" in prop
        assert "title" in prop
        assert "price" in prop
        assert "features" in prop
        assert "location" in prop

    async def test_list_properties_with_filters(self):
        result = await properties_client.list_properties(
            location_key_name="cl/region-metropolitana/las-condes",
            property_type="APARTMENT",
            bedrooms_min=2,
            price_max=10000,
            currency_id="UF",
            page_limit=3,
        )
        data = json.loads(result)
        assert "properties" in data

    async def test_get_property_detail(self):
        # First get a property ID from the list
        list_result = await properties_client.list_properties(
            location_key_name="cl/region-metropolitana/las-condes",
            page_limit=1,
        )
        list_data = json.loads(list_result)
        property_id = str(list_data["properties"][0]["id"])

        # Now get the detail
        result = await properties_client.get_property_detail(property_id)
        data = json.loads(result)
        assert "property" in data

        prop = data["property"]
        assert "id" in prop
        assert "title" in prop
        assert "description" in prop
        assert "features" in prop
        assert "images" in prop
        assert "contact" in prop
