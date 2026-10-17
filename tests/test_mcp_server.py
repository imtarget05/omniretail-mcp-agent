"""
Unit Tests for FastMCP Retail Tools
"""

import pytest
from retail_mcp_server.tools.inventory import check_store_inventory
from retail_mcp_server.tools.warranty import lookup_warranty
from retail_mcp_server.tools.booking import create_booking_ticket
from retail_mcp_server.db import get_db_cursor

@pytest.fixture(autouse=True)
def ensure_test_inventory():
    """Ensure test SKU has stock before test and restores it afterwards"""
    with get_db_cursor() as cur:
        cur.execute("UPDATE retail_inventory SET stock_quantity = 10 WHERE sku = 'ATKF35XVMV' AND store_id = 'DMX_Q9_01';")
    yield
    with get_db_cursor() as cur:
        cur.execute("UPDATE retail_inventory SET stock_quantity = 10 WHERE sku = 'ATKF35XVMV' AND store_id = 'DMX_Q9_01';")

def test_check_store_inventory_valid_sku():
    res = check_store_inventory(sku="ATKF35XVMV", district="Quận 9")
    assert res["sku"] == "ATKF35XVMV"
    assert "matched_stores" in res
    assert len(res["matched_stores"]) > 0
    # Store in Q9 should have units
    q9_store = next((s for s in res["matched_stores"] if s["store_id"] == "DMX_Q9_01"), None)
    assert q9_store is not None
    assert q9_store["stock_quantity"] >= 0

def test_lookup_warranty_valid():
    res = lookup_warranty("0901234567")
    assert res["found"] is True
    assert len(res["records"]) > 0

def test_lookup_warranty_not_found():
    res = lookup_warranty("0999999999")
    assert res["found"] is False
    assert len(res["records"]) == 0

def test_create_booking_ticket():
    res = create_booking_ticket(
        sku="ATKF35XVMV",
        store_id="DMX_Q9_01",
        customer_name="Test User",
        customer_phone="0911223344",
        delivery_time="Sáng mai"
    )
    assert res["success"] is True
    assert res["ticket_id"].startswith("BK-")
    assert res["status"] == "CONFIRMED"

