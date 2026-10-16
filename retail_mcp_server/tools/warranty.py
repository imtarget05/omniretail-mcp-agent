"""
Tool 2: lookup_warranty
Looks up warranty history, active policies, and expiry dates for a customer by phone number.
"""

from typing import Dict, Any, List
from retail_mcp_server.db import get_db_cursor

def lookup_warranty(phone: str) -> Dict[str, Any]:
    """
    Lookup warranty and purchase records by customer phone number.
    """
    clean_phone = phone.strip().replace(" ", "").replace(".", "")
    with get_db_cursor() as cur:
        query = """
            SELECT w.warranty_id, w.customer_name, w.sku, p.name as product_name,
                   w.purchase_date, w.expiry_date, w.status
            FROM retail_warranties w
            LEFT JOIN retail_products p ON w.sku = p.sku
            WHERE w.phone = %s OR w.phone LIKE %s
            ORDER BY w.expiry_date DESC;
        """
        cur.execute(query, (clean_phone, f"%{clean_phone}%"))
        rows = cur.fetchall()

        if not rows:
            return {
                "phone": clean_phone,
                "found": False,
                "message": f"Không tìm thấy dữ liệu bảo hành nào cho số điện thoại {clean_phone}.",
                "records": []
            }

        records = []
        for r in rows:
            records.append({
                "warranty_id": r["warranty_id"],
                "customer_name": r["customer_name"],
                "sku": r["sku"],
                "product_name": r["product_name"] or "Sản phẩm điện tử",
                "purchase_date": str(r["purchase_date"]),
                "expiry_date": str(r["expiry_date"]),
                "status": r["status"]
            })

        return {
            "phone": clean_phone,
            "found": True,
            "total_items": len(records),
            "records": records
        }
