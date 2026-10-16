"""
Supervisor / Router Node: Multi-Intent Query Decomposition
Decomposes user queries into sequential or parallel intents:
- 'product_discovery': Search catalog/specs
- 'inventory_check': Check physical stock by district/store
- 'warranty_lookup': Check warranty by phone number
- 'booking_reservation': Create booking ticket
"""

import re
from typing import Dict, Any
from agent_core.state import RetailAgentState

def supervisor_router_node(state: RetailAgentState) -> Dict[str, Any]:
    query = state.get("query", "").lower()
    intents = []
    target_district = None

    # District extraction
    districts = ["quận 9", "q9", "quận 1", "q1", "bình thạnh", "tân bình", "thủ đức", "gò vấp", "quận 7", "quận 3", "quận 10", "phú nhuận"]
    for d in districts:
        if d in query:
            target_district = "Quận 9" if d in ["quận 9", "q9"] else d.title()
            break

    # Phone extraction
    phones = re.findall(r"0\d{9}", query)
    customer_phone = phones[0] if phones else state.get("customer_phone")

    # Intent classification
    if any(k in query for k in ["bảo hành", "tra cứu máy", "hết hạn bảo hành"]):
        intents.append("warranty_lookup")
    elif any(k in query for k in ["mua", "tìm", "tư vấn", "máy lạnh", "điện thoại", "tủ lạnh", "máy giặt", "tivi", "daikin", "panasonic", "iphone"]):
        intents.append("product_discovery")

    if "warranty_lookup" not in intents and any(k in query for k in ["còn hàng", "có sẵn", "còn máy", "kiểm tra", "ở đâu còn", "quận", "khu vực", "chi nhánh", "cửa hàng", "kho"]):
        intents.append("inventory_check")

    if any(k in query for k in ["đặt", "giữ hàng", "giao", "lấy máy", "chốt", "khóa máy"]):
        intents.append("booking_reservation")

    if not intents:
        intents.append("product_discovery")

    return {
        "intents": intents,
        "target_district": target_district,
        "customer_phone": customer_phone
    }
