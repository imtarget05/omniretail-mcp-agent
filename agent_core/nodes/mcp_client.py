"""
Action Node: FastMCP Client Tool Calling
Invokes FastMCP Server tools (check_store_inventory or lookup_warranty)
"""

from typing import Dict, Any
from retail_mcp_server.tools.inventory import check_store_inventory
from retail_mcp_server.tools.warranty import lookup_warranty
from agent_core.state import RetailAgentState

def mcp_action_node(state: RetailAgentState) -> Dict[str, Any]:
    intents = state.get("intents", [])
    selected_sku = state.get("selected_sku")
    district = state.get("target_district")
    phone = state.get("customer_phone")

    inventory_res = None
    warranty_res = None

    if "inventory_check" in intents or "booking_reservation" in intents:
        sku_id = selected_sku["sku"] if selected_sku else "ATKF35XVMV"
        print(f"📞 MCP Client invoking: check_store_inventory(sku='{sku_id}', district='{district}')")
        inventory_res = check_store_inventory(sku=sku_id, district=district)

    if "warranty_lookup" in intents and phone:
        print(f"📞 MCP Client invoking: lookup_warranty(phone='{phone}')")
        warranty_res = lookup_warranty(phone=phone)

    return {
        "inventory_result": inventory_res
    }
