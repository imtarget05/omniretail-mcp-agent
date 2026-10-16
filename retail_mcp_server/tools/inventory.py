"""
Tool 1: check_store_inventory
Checks current physical inventory for a product SKU across stores or within a specific district.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from retail_mcp_server.db import get_db_cursor

class InventoryItem(BaseModel):
    store_id: str
    store_name: str
    district: str
    address: str
    stock_quantity: int
    store_price: float
    status: str

class InventoryCheckResponse(BaseModel):
    sku: str
    product_name: str
    total_available_stock: int
    matched_stores: List[InventoryItem]

def check_store_inventory(sku: str, district: Optional[str] = None) -> Dict[str, Any]:
    """
    Check stock availability for a given product SKU in stores (optionally filtered by district).
    """
    with get_db_cursor() as cur:
        # Get product info
        cur.execute("SELECT sku, name, base_price FROM retail_products WHERE sku = %s;", (sku,))
        prod = cur.fetchone()
        if not prod:
            return {
                "error": f"Không tìm thấy sản phẩm có mã SKU: {sku}",
                "sku": sku,
                "total_available_stock": 0,
                "matched_stores": []
            }

        # Query inventory
        if district:
            query = """
                SELECT i.store_id, s.name as store_name, s.district, s.address, i.stock_quantity, i.store_price
                FROM retail_inventory i
                JOIN retail_stores s ON i.store_id = s.store_id
                WHERE i.sku = %s AND (s.district ILIKE %s OR s.name ILIKE %s)
                ORDER BY i.stock_quantity DESC;
            """
            cur.execute(query, (sku, f"%{district}%", f"%{district}%"))
        else:
            query = """
                SELECT i.store_id, s.name as store_name, s.district, s.address, i.stock_quantity, i.store_price
                FROM retail_inventory i
                JOIN retail_stores s ON i.store_id = s.store_id
                WHERE i.sku = %s
                ORDER BY i.stock_quantity DESC;
            """
            cur.execute(query, (sku,))
        
        rows = cur.fetchall()
        total_stock = sum(r["stock_quantity"] for r in rows)
        stores_list = []
        for r in rows:
            stores_list.append({
                "store_id": r["store_id"],
                "store_name": r["store_name"],
                "district": r["district"],
                "address": r["address"],
                "stock_quantity": r["stock_quantity"],
                "store_price": float(r["store_price"]),
                "status": "CÒN HÀNG" if r["stock_quantity"] > 0 else "HẾT HÀNG"
            })

        return {
            "sku": prod["sku"],
            "product_name": prod["name"],
            "total_available_stock": total_stock,
            "matched_stores": stores_list
        }
