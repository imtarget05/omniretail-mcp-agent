"""
LangGraph State Definition for OmniRetail MCP Agent
"""

from typing import List, Dict, Any, Optional, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator

class RetailAgentState(TypedDict):
    messages: Annotated[List[Dict[str, Any]], operator.add]
    query: str
    intents: List[str]
    matched_skus: List[Dict[str, Any]]
    selected_sku: Optional[Dict[str, Any]]
    target_district: Optional[str]
    inventory_result: Optional[Dict[str, Any]]
    customer_phone: Optional[str]
    customer_name: Optional[str]
    delivery_time: Optional[str]
    booking_ticket: Optional[Dict[str, Any]]
    awaiting_confirmation: bool
    final_response: str
    tool_calls: Optional[List[Dict[str, Any]]]

