"""
Human-in-the-loop (HITL) & Write Operation Safety Node
Handles safe reservation booking with explicit customer phone confirmation,
warranty lookups, and dynamic sales consultation synthesis.
"""

from typing import Dict, Any
from retail_mcp_server.tools.booking import create_booking_ticket
from retail_mcp_server.tools.warranty import lookup_warranty
from agent_core.state import RetailAgentState
from agent_core.retail_advisor import generate_dynamic_retail_consultation

def hitl_booking_node(state: RetailAgentState) -> Dict[str, Any]:
    intents = state.get("intents", [])
    query = state.get("query", "")
    selected_sku = state.get("selected_sku")
    matched_skus = state.get("matched_skus", [])
    inv_res = state.get("inventory_result")
    customer_phone = state.get("customer_phone")
    delivery_time = state.get("delivery_time") or "Sáng mai 09:00"

    # 1. Handle Warranty Lookup directly
    if "warranty_lookup" in intents:
        war_data = lookup_warranty(phone=customer_phone or "0901234567")
        if war_data.get("found"):
            items_str = "\n".join([
                f"- **{r['product_name']}** (SKU: `{r['sku']}`):\n"
                f"  • Hạn bảo hành: `{r['expiry_date']}` ({r['status']})\n"
                f"  • Điểm tiếp nhận: Siêu thị ĐMX toàn quốc hoặc Hotline 1800.1065"
                for r in war_data.get("records", [])
            ])
            msg = (
                f"🛡️ **KẾT QUẢ TRA CỨU BẢO HÀNH CHÍNH HÃNG (MWG)**\n\n"
                f"Dạ hệ thống Điện Máy Xanh tra cứu thông tin bảo hành cho số điện thoại `{customer_phone or '0901234567'}`:\n\n"
                f"{items_str}\n\n"
                f"📌 *Quý khách cần hỗ trợ kỹ thuật tận nhà, vui lòng liên hệ tổng đài miễn phí 1800.1065 hoặc mang thiết bị đến siêu thị gần nhất ạ!*"
            )
        else:
            msg = f"Dạ số điện thoại `{customer_phone}` hiện chưa ghi nhận lịch sử mua hàng hoặc hợp đồng bảo hành nào trên hệ thống ERP của Thế Giới Di Động & Điện Máy Xanh ạ."
        return {
            "awaiting_confirmation": False,
            "final_response": msg,
            "response": msg
        }

    # 2. Handle Booking Reservation
    if "booking_reservation" in intents:
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
                f"Dạ mẫu **{sku_name}** (Giá: **{sku_price}**) hiện đang có sẵn **{stock_qty} máy** "
                f"tại **{store_name}**.\n\n"
                f"⚠️ **Xác nhận đặt giữ hàng (HITL Gate)**: Thao tác này sẽ tạm khóa máy trên hệ thống kho ERP của siêu thị. "
                f"Anh/chị vui lòng cung cấp **Số điện thoại nhận hàng** để em xuất Mã Phiếu Giữ Máy (E-Voucher) và gửi SMS xác nhận nhé!"
            )
            return {
                "awaiting_confirmation": True,
                "final_response": msg,
                "response": msg
            }

        # Customer confirmed phone -> Execute FastMCP booking tool!
        print(f"🔒 Executing Write Operation via MCP: create_booking_ticket for {customer_phone} at {store_id}")
        booking_res = create_booking_ticket(
            sku=sku_code,
            store_id=store_id,
            customer_name=state.get("customer_name") or "Khách hàng VIP MWG",
            customer_phone=customer_phone,
            delivery_time=delivery_time
        )

        ticket_id = booking_res.get("ticket_id", "BK-SUCCESS")
        confirm_msg = (
            f"🎉 **ĐẶT GIỮ HÀNG THÀNH CÔNG (E-VOUCHER VIP)!**\n\n"
            f"- **Mã phiếu giữ chỗ**: `{ticket_id}`\n"
            f"- **Sản phẩm**: **{sku_name}** (Mã SKU: `{sku_code}`)\n"
            f"- **Giá niêm yết ưu đãi**: {sku_price}\n"
            f"- **Siêu thị nhận máy**: {store_name} ({best_store.get('address', '') if best_store else ''})\n"
            f"- **Số điện thoại đăng ký**: `{customer_phone}`\n"
            f"- **Hạn nhận máy**: {delivery_time}\n\n"
            f"Hệ thống đã gửi tin nhắn SMS xác thực tới số `{customer_phone}`. Khi tới siêu thị, anh/chị chỉ cần đưa mã `{ticket_id}` cho nhân viên để nhận máy ngay ạ!"
        )

        return {
            "booking_ticket": booking_res,
            "awaiting_confirmation": False,
            "final_response": confirm_msg,
            "response": confirm_msg
        }

    # 3. Product Discovery & General Retail Consultation (Dynamic Generative Reasoning)
    consultation_msg = generate_dynamic_retail_consultation(
        user_query=query,
        selected_sku=selected_sku,
        matched_skus=matched_skus,
        inventory_res=inv_res,
        customer_phone=customer_phone
    )

    return {
        "awaiting_confirmation": False,
        "final_response": consultation_msg,
        "response": consultation_msg
    }
