"""Tests for the convert_currency function."""
import json

import pytest

from app.services.properties import convert_currency


@pytest.mark.asyncio
class TestConvertCurrency:
    async def test_clp_to_uf(self):
        """2,000,000 CLP should convert to 50 UF."""
        result = json.loads(await convert_currency(2_000_000, "CLP", "UF"))
        assert result["converted"]["amount"] == 50.0
        assert result["converted"]["currency"] == "UF"
        assert result["original"]["amount"] == 2_000_000
        assert result["original"]["currency"] == "CLP"

    async def test_uf_to_clp(self):
        """100 UF should convert to 4,000,000 CLP."""
        result = json.loads(await convert_currency(100, "UF", "CLP"))
        assert result["converted"]["amount"] == 4_000_000
        assert result["converted"]["currency"] == "CLP"

    async def test_same_currency_noop(self):
        """Converting UF to UF returns the same amount."""
        result = json.loads(await convert_currency(500, "UF", "UF"))
        assert result["amount"] == 500
        assert result["currency"] == "UF"

    async def test_same_currency_clp(self):
        """Converting CLP to CLP returns the same amount."""
        result = json.loads(await convert_currency(1_000_000, "CLP", "CLP"))
        assert result["amount"] == 1_000_000
        assert result["currency"] == "CLP"

    async def test_small_clp_to_uf(self):
        """40,000 CLP = 1 UF exactly."""
        result = json.loads(await convert_currency(40_000, "CLP", "UF"))
        assert result["converted"]["amount"] == 1.0

    async def test_fractional_uf(self):
        """60,000 CLP = 1.5 UF."""
        result = json.loads(await convert_currency(60_000, "CLP", "UF"))
        assert result["converted"]["amount"] == 1.5

    async def test_unsupported_conversion(self):
        """Unsupported currency pair returns error."""
        result = json.loads(await convert_currency(100, "USD", "UF"))
        assert "error" in result

    async def test_zero_amount(self):
        """Zero converts to zero."""
        result = json.loads(await convert_currency(0, "CLP", "UF"))
        assert result["converted"]["amount"] == 0.0

    async def test_rate_included(self):
        """Result includes the exchange rate used."""
        result = json.loads(await convert_currency(1_000_000, "CLP", "UF"))
        assert "rate" in result
        assert "40" in result["rate"]
