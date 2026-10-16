"""
OmniRetail FastMCP Microservice Server
Standardized Model Context Protocol server exposing Retail ERP/POS tools:
1. check_store_inventory: Real-time inventory check by SKU and district.
2. lookup_warranty: Warranty policy & history lookup by phone number.
3. create_booking_ticket: Confirmed booking reservation ticket generation.
"""

from typing import Optional, Dict, Any
from fastmcp import FastMCP

from retail_mcp_server.tools.inventory import check_store_inventory as _check_inventory
from retail_mcp_server.tools.warranty import lookup_warranty as _lookup_warranty
from retail_mcp_server.tools.booking import create_booking_ticket as _create_booking

# Initialize FastMCP application
mcp = FastMCP("OmniRetail-ERP-MCP-Service")

@mcp.tool()
def check_store_inventory(sku: str, district: Optional[str] = None) -> Dict[str, Any]:
    """
    Kiểm tra số lượng hàng tồn kho thực tế của mã sản phẩm (SKU) tại các cửa hàng
    Điện Máy Xanh và Thế Giới Di Động (có thể lọc theo quận/huyện TP.HCM).
    
    Args:
        sku: Mã sản phẩm duy nhất (ví dụ: 'ATKF35XVMV', 'IPHONE-15-PRO-128').
        district: Tên quận/huyện cần kiểm tra (ví dụ: 'Quận 9', 'Bình Thạnh', 'Quận 1').
    """
    return _check_inventory(sku=sku, district=district)

@mcp.tool()
def lookup_warranty(phone: str) -> Dict[str, Any]:
    """
    Tra cứu lịch sử mua hàng, danh sách thiết bị và thời hạn bảo hành chính hãng
    của khách hàng qua số điện thoại đăng ký tại hệ thống Thế Giới Di Động / Điện Máy Xanh.
    
    Args:
        phone: Số điện thoại khách hàng (ví dụ: '0901234567').
    """
    return _lookup_warranty(phone=phone)

@mcp.tool()
def create_booking_ticket(
    sku: str,
    store_id: str,
    customer_name: str,
    customer_phone: str,
    delivery_time: Optional[str] = "Trong vòng 24 giờ"
) -> Dict[str, Any]:
    """
    Tạo phiếu đặt giữ hàng chính thức tại cửa hàng và trừ 1 đơn vị tồn kho trong ERP.
    Hành động này là Write Operation, cần có sự xác nhận của khách hàng trước khi gọi.
    
    Args:
        sku: Mã sản phẩm khách muốn giữ (ví dụ: 'ATKF35XVMV').
        store_id: Mã cửa hàng tiếp nhận (ví dụ: 'DMX_Q9_01').
        customer_name: Họ tên khách hàng (ví dụ: 'Nguyễn Văn A').
        customer_phone: Số điện thoại liên hệ (ví dụ: '0988776655').
        delivery_time: Thời gian hẹn nhận máy (ví dụ: '09:00 sáng mai').
    """
    return _create_booking(
        sku=sku,
        store_id=store_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        delivery_time=delivery_time
    )

if __name__ == "__main__":
    print("🚀 Starting OmniRetail FastMCP Server via stdio...")
    mcp.run()
