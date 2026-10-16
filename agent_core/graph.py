"""
Compiled LangGraph Multi-Agent Workflow for OmniRetail
Orchestrates Ingress, Input Guardrail, Redis Semantic Cache,
Supervisor, Hybrid Discovery, FastMCP Action, and HITL Booking with Checkpointing.
"""

import time
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agent_core.state import RetailAgentState
from agent_core.guardrails.prompt_guard import check_input_guardrail
from agent_core.guardrails.semantic_cache import RetailSemanticCache
from agent_core.nodes.supervisor import supervisor_router_node
from agent_core.nodes.hybrid_discovery import hybrid_discovery_node
from agent_core.nodes.mcp_client import mcp_action_node
from agent_core.nodes.hitl_reservation import hitl_booking_node

# Compile StateGraph
workflow = StateGraph(RetailAgentState)

workflow.add_node("supervisor", supervisor_router_node)
workflow.add_node("discovery", hybrid_discovery_node)
workflow.add_node("mcp_action", mcp_action_node)
workflow.add_node("hitl_booking", hitl_booking_node)

workflow.set_entry_point("supervisor")
workflow.add_edge("supervisor", "discovery")
workflow.add_edge("discovery", "mcp_action")
workflow.add_edge("mcp_action", "hitl_booking")
workflow.add_edge("hitl_booking", END)

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

semantic_cache = RetailSemanticCache()

def process_customer_query(
    query: str,
    thread_id: str = "default_thread",
    customer_phone: Optional[str] = None,
    bypass_cache: bool = False
) -> Dict[str, Any]:
    """
    Main entry point for processing customer chat queries.
    1. Input Guardrail: Checks for prompt injection or price manipulations.
    2. Redis Semantic Cache: Checks if identical/similar query is cached (<50ms).
    3. LangGraph Workflow: Executes stateful graph with memory checkpointer.
    """
    start_time = time.perf_counter()

    # 1. Guardrail Check
    t0 = time.perf_counter()
    is_safe, guard_msg = check_input_guardrail(query)
    guard_time = time.perf_counter() - t0

    if not is_safe:
        total_time = time.perf_counter() - start_time
        return {
            "response": guard_msg,
            "status": "BLOCKED_GUARDRAIL",
            "thread_id": thread_id,
            "telemetry": {
                "total_ms": round(total_time * 1000, 2),
                "guardrail_ms": round(guard_time * 1000, 2),
                "cache_ms": 0.0,
                "graph_ms": 0.0,
                "cache_hit": False,
                "guardrail_status": "TRIPPED"
            }
        }

    # 2. Semantic Cache Check (Bypassed if booking/phone is provided or bypass_cache is True)
    t1 = time.perf_counter()
    is_cache_hit = False
    if not bypass_cache and not customer_phone and not any(k in query.lower() for k in ["đặt", "giữ", "mua ngay"]):
        cached = semantic_cache.get(query)
        if cached:
            cache_time = time.perf_counter() - t1
            total_time = time.perf_counter() - start_time
            return {
                "response": cached,
                "status": "CACHE_HIT",
                "thread_id": thread_id,
                "telemetry": {
                    "total_ms": round(total_time * 1000, 2),
                    "guardrail_ms": round(guard_time * 1000, 2),
                    "cache_ms": round(cache_time * 1000, 2),
                    "graph_ms": 0.0,
                    "cache_hit": True,
                    "guardrail_status": "PASSED"
                }
            }
    cache_time = time.perf_counter() - t1

    # 3. LangGraph Execution
    t2 = time.perf_counter()
    initial_state: RetailAgentState = {
        "messages": [{"role": "user", "content": query}],
        "query": query,
        "intents": [],
        "matched_skus": [],
        "selected_sku": None,
        "target_district": None,
        "inventory_result": None,
        "customer_phone": customer_phone,
        "customer_name": "Khách hàng",
        "delivery_time": "Sáng mai 09:00",
        "booking_ticket": None,
        "awaiting_confirmation": False,
        "final_response": ""
    }

    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke(initial_state, config=config)
    graph_time = time.perf_counter() - t2

    response_text = result.get("final_response", "")

    # Save to semantic cache if not waiting for confirmation
    if not result.get("awaiting_confirmation") and not result.get("booking_ticket"):
        semantic_cache.set(query, response_text)

    total_time = time.perf_counter() - start_time

    return {
        "response": response_text,
        "final_response": response_text,
        "selected_sku": result.get("selected_sku"),
        "inventory": result.get("inventory_result"),
        "booking_ticket": result.get("booking_ticket"),
        "awaiting_confirmation": result.get("awaiting_confirmation"),
        "status": "SUCCESS",
        "thread_id": thread_id,
        "telemetry": {
            "total_ms": round(total_time * 1000, 2),
            "guardrail_ms": round(guard_time * 1000, 2),
            "cache_ms": round(cache_time * 1000, 2),
            "graph_ms": round(graph_time * 1000, 2),
            "cache_hit": False,
            "guardrail_status": "PASSED",
            "estimated_tokens": len(query.split()) + len(response_text.split())
        }
    }
