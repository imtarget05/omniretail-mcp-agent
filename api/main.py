"""
FastAPI Gateway with Server-Sent Events (SSE) Streaming
for OmniRetail MCP Agent
Port: 8081
"""

import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from typing import Optional

from agent_core.graph import process_customer_query

app = FastAPI(title="OmniRetail MCP Agent Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    thread_id: Optional[str] = "session_default"
    customer_phone: Optional[str] = None

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "OmniRetail MCP Agent Gateway"}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    result = process_customer_query(
        query=req.query,
        thread_id=req.thread_id,
        customer_phone=req.customer_phone
    )
    return result

@app.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    """
    Streams reasoning steps and final response via Server-Sent Events (SSE).
    """
    async def event_generator():
        yield {
            "event": "step",
            "data": json.dumps({"step": "Ingress Guardrail & Semantic Cache", "status": "CHECKING"})
        }
        await asyncio.sleep(0.1)

        yield {
            "event": "step",
            "data": json.dumps({"step": "Supervisor Router", "status": "ANALYZING_INTENT"})
        }
        await asyncio.sleep(0.1)

        yield {
            "event": "step",
            "data": json.dumps({"step": "Qdrant Hybrid Discovery", "status": "SEARCHING_CATALOG"})
        }
        await asyncio.sleep(0.15)

        # Run core processing
        result = process_customer_query(
            query=req.query,
            thread_id=req.thread_id,
            customer_phone=req.customer_phone
        )

        yield {
            "event": "step",
            "data": json.dumps({"step": "FastMCP Action", "status": "EXECUTED", "inventory": result.get("inventory")})
        }
        await asyncio.sleep(0.1)

        yield {
            "event": "final",
            "data": json.dumps(result, ensure_ascii=False)
        }

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
