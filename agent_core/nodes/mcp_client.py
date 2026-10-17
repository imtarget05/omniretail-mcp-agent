"""
Action Node: FastMCP Client Tool Calling
Invokes FastMCP Server tools (check_store_inventory or lookup_warranty)
"""

import time
from typing import Dict, Any, List
from retail_mcp_server.tools.inventory import check_store_inventory
from retail_mcp_server.tools.warranty import lookup_warranty
from agent_core.state import RetailAgentState

def mcp_action_node(state: RetailAgentState) -> Dict[str, Any]:
    intents = state.get("intents", [])
    selected_sku = state.get("selected_sku")
    district = state.get("target_district")
    phone = state.get("customer_phone")
    tool_calls: List[Dict[str, Any]] = list(state.get("tool_calls") or [])

    inventory_res = None
    warranty_res = None

    if "inventory_check" in intents or "booking_reservation" in intents:
        sku_id = selected_sku["sku"] if selected_sku else "ATKF35XVMV"
        print(f"📞 MCP Client invoking: check_store_inventory(sku='{sku_id}', district='{district}')")
        t0 = time.perf_counter()
        inventory_res = check_store_inventory(sku=sku_id, district=district)
        dur_ms = round((time.perf_counter() - t0) * 1000, 1)
        tool_calls.append({
            "tool": "check_store_inventory",
            "args": f"sku='{sku_id}', district='{district}'" if district else f"sku='{sku_id}'",
            "latency_ms": dur_ms,
            "target": "Neon PostgreSQL (SG)",
            "status": "SUCCESS"
        })

    if "warranty_lookup" in intents and phone:
        print(f"📞 MCP Client invoking: lookup_warranty(phone='{phone}')")
        t0 = time.perf_counter()
        warranty_res = lookup_warranty(phone=phone)
        dur_ms = round((time.perf_counter() - t0) * 1000, 1)
        tool_calls.append({
            "tool": "lookup_warranty",
            "args": f"phone='{phone}'",
            "latency_ms": dur_ms,
            "target": "Neon PostgreSQL (SG)",
            "status": "FOUND" if warranty_res.get("found") else "NOT_FOUND"
        })

    return {
        "inventory_result": inventory_res,
        "tool_calls": tool_calls
    }

