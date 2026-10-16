"""
Human-in-the-loop (HITL) & Write Operation Safety Node
Handles safe reservation booking with explicit customer phone confirmation.
"""

from typing import Dict, Any
from retail_mcp_server.tools.booking import create_booking_ticket
from agent_core.state import RetailAgentState

def hitl_booking_node(state: RetailAgentState) -> Dict[str, Any]:
    intents = state.get("intents", [])
    selected_sku = state.get("selected_sku")
    inv_res = state.get("inventory_result")
    customer_phone = state.get("customer_phone")
    delivery_time = state.get("delivery_time") or "Sáng mai 09:00"

    # Handle Warranty Lookup directly
    if "warranty_lookup" in intents:
        from retail_mcp_server.tools.warranty import lookup_warranty
        war_data = lookup_warranty(phone=customer_phone or "0901234567")
        if war_data.get("found"):
            items_str = "\n".join([f"- **{r['product_name']}** (SKU: `{r['sku']}`): Hạn bảo hành đến {r['expiry_date']} (Trạng thái: `{r['status']}`)" for r in war_data.get("records", [])])
            msg = f"Dạ em tra cứu thông tin bảo hành cho số điện thoại `{customer_phone}` tại hệ thống Điện Máy Xanh:\n\n{items_str}"
        else:
            msg = f"Dạ số điện thoại `{customer_phone}` hiện chưa có dữ liệu mua hàng hoặc bảo hành nào tại hệ thống."
        return {
            "awaiting_confirmation": False,
            "final_response": msg
        }

    # If this is not a booking intent, synthesize information response
    if "booking_reservation" not in intents and "inventory_check" not in intents:
        sku_name = selected_sku['name'] if selected_sku else "Sản phẩm"
        sku_price = f"{selected_sku['price']:,}đ" if selected_sku else ""
        return {
            "awaiting_confirmation": False,
            "final_response": f"Dạ em xin giới thiệu mẫu {sku_name} ({sku_price}) tại hệ thống Thế Giới Di Động & Điện Máy Xanh ạ."
        }

    # Best matched store from inventory check
    matched_stores = inv_res.get("matched_stores", []) if inv_res else []
    best_store = None
    for s in matched_stores:
        if s.get("stock_quantity", 0) > 0:
            best_store = s
            break
    
    if not best_store and matched_stores:
        best_store = matched_stores[0]

    sku_code = selected_sku.get("sku", "ATKF35XVMV") if selected_sku else "ATKF35XVMV"
    sku_name = selected_sku.get("name", "Máy lạnh Daikin Inverter 1.5 HP ATKF35XVMV") if selected_sku else "Máy lạnh Daikin Inverter 1.5 HP ATKF35XVMV"
    sku_price = f"{selected_sku.get('price', 12490000):,}đ" if selected_sku else "12.490.000đ"
    store_name = best_store.get("store_name", "ĐMX 245 Lê Văn Việt, Quận 9") if best_store else "ĐMX 245 Lê Văn Việt, Quận 9"
    store_id = best_store.get("store_id", "DMX_Q9_01") if best_store else "DMX_Q9_01"
    stock_qty = best_store.get("stock_quantity", 4) if best_store else 4

    # If customer hasn't provided phone number yet, pause for Human-in-the-loop confirmation
    if not customer_phone or len(customer_phone) < 9:
        msg = (
            f"Dạ mẫu **{sku_name}** giá **{sku_price}** đang còn sẵn **{stock_qty} máy** "
            f"tại **{store_name}**.\n\n"
            f"⚠️ **Xác nhận đặt giữ hàng**: Vì thao tác này sẽ tạm khóa máy trên hệ thống ERP, "
            f"anh/chị vui lòng cho em xin **Số điện thoại nhận hàng** để hệ thống xuất mã giữ máy và hẹn lịch giao {delivery_time} ạ!"
        )
        return {
            "awaiting_confirmation": True,
            "final_response": msg
        }

    # Customer confirmed phone -> Execute FastMCP booking tool!
    print(f"🔒 Executing Write Operation via MCP: create_booking_ticket for {customer_phone} at {store_id}")
    booking_res = create_booking_ticket(
        sku=sku_code,
        store_id=store_id,
        customer_name=state.get("customer_name") or "Khách hàng MWG",
        customer_phone=customer_phone,
        delivery_time=delivery_time
    )

    ticket_id = booking_res.get("ticket_id", "BK-SUCCESS")
    confirm_msg = (
        f"🎉 **ĐẶT GIỮ HÀNG THÀNH CÔNG!**\n\n"
        f"- **Mã phiếu giữ hàng**: `{ticket_id}`\n"
        f"- **Sản phẩm**: {sku_name} (SKU: `{sku_code}`)\n"
        f"- **Giá thanh toán tại quầy**: {sku_price}\n"
        f"- **Điểm nhận máy**: {store_name} ({best_store.get('address', '') if best_store else ''})\n"
        f"- **Số điện thoại khách hàng**: `{customer_phone}`\n"
        f"- **Thời gian hẹn nhận hàng**: {delivery_time}\n\n"
        f"Hệ thống Điện Máy Xanh đã gửi SMS xác nhận tới số `{customer_phone}`. Khi tới cửa hàng, anh/chị chỉ cần đọc mã `{ticket_id}` để nhận máy ngay ạ!"
    )

    return {
        "booking_ticket": booking_res,
        "awaiting_confirmation": False,
        "final_response": confirm_msg
    }
