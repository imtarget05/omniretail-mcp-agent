"""
Tool 3: create_booking_ticket
Creates a verified product reservation ticket in PostgreSQL with stock reservation.
"""

import uuid
from typing import Dict, Any, Optional
from retail_mcp_server.db import get_db_cursor

def create_booking_ticket(
    sku: str,
    store_id: str,
    customer_name: str,
    customer_phone: str,
    delivery_time: Optional[str] = "Trong vòng 24 giờ"
) -> Dict[str, Any]:
    """
    Creates a confirmed booking reservation ticket for customer pickup at a store.
    """
    clean_phone = customer_phone.strip().replace(" ", "")
    ticket_id = f"BK-{uuid.uuid4().hex[:8].upper()}"

    with get_db_cursor() as cur:
        # Check product
        cur.execute("SELECT sku, name, base_price FROM retail_products WHERE sku = %s;", (sku,))
        prod = cur.fetchone()
        if not prod:
            return {"success": False, "error": f"Mã sản phẩm {sku} không tồn tại trên hệ thống."}

        # Check store and inventory
        cur.execute("""
            SELECT s.store_id, s.name as store_name, s.address, s.district, i.stock_quantity
            FROM retail_stores s
            LEFT JOIN retail_inventory i ON s.store_id = i.store_id AND i.sku = %s
            WHERE s.store_id = %s;
        """, (sku, store_id))
        store_inv = cur.fetchone()

        if not store_inv:
            return {"success": False, "error": f"Không tìm thấy cửa hàng có mã {store_id}."}

        current_qty = store_inv["stock_quantity"] or 0
        if current_qty <= 0:
            return {
                "success": False,
                "error": f"Sản phẩm {prod['name']} tại cửa hàng {store_inv['store_name']} tạm thời đã hết hàng."
            }

        # Deduct stock by 1
        cur.execute("""
            UPDATE retail_inventory
            SET stock_quantity = stock_quantity - 1, updated_at = CURRENT_TIMESTAMP
            WHERE sku = %s AND store_id = %s;
        """, (sku, store_id))

        # Insert booking ticket
        cur.execute("""
            INSERT INTO retail_booking_tickets (ticket_id, sku, store_id, customer_name, customer_phone, delivery_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'CONFIRMED');
        """, (ticket_id, sku, store_id, customer_name, clean_phone, delivery_time))

        return {
            "success": True,
            "ticket_id": ticket_id,
            "sku": prod["sku"],
            "product_name": prod["name"],
            "price": float(prod["base_price"]),
            "store_name": store_inv["store_name"],
            "store_address": store_inv["address"],
            "district": store_inv["district"],
            "customer_name": customer_name,
            "customer_phone": clean_phone,
            "pickup_time": delivery_time,
            "status": "CONFIRMED",
            "message": f"Đặt giữ hàng thành công! Mã phiếu giữ hàng của quý khách là {ticket_id}."
        }
