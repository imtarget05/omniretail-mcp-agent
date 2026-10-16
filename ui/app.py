"""
Chainlit UI for OmniRetail MCP Agent
Visualizes transparent tool execution, Qdrant Hybrid Search, FastMCP invocations,
and Human-in-the-Loop booking confirmation.
"""

import chainlit as cl
from agent_core.graph import process_customer_query

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("thread_id", f"user_{cl.context.session.id}")
    cl.user_session.set("pending_phone", False)

    welcome_msg = (
        "👋 Chào mừng quý khách đến với **OmniRetail AI Assistant**!\n\n"
        "Hệ thống đa tác vụ mô phỏng chuỗi bán lẻ **Thế Giới Di Động & Điện Máy Xanh**:\n"
        "- 🔍 **Hybrid AI Search (Qdrant)**: Tra cứu sản phẩm & thông số kỹ thuật chi tiết.\n"
        "- ⚡ **FastMCP Microservice**: Kiểm tra tồn kho thực tế & bảo hành theo thời gian thực.\n"
        "- 🛡️ **Human-in-the-loop**: Tự động tạm dừng để bạn xác nhận số điện thoại trước khi xuất mã giữ hàng.\n\n"
        "💡 *Ví dụ bạn có thể hỏi*: 'Mình muốn mua máy lạnh Daikin Inverter 1.5 HP dưới 13 triệu, kiểm tra giúp mình cửa hàng Điện Máy Xanh ở Quận 9 còn hàng không và đặt lịch giao sáng mai nhé.'"
    )
    await cl.Message(content=welcome_msg).send()

@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")
    pending_phone = cl.user_session.get("pending_phone")

    # Step 1: Ingress & Guardrails
    async with cl.Step(name="🛡️ Ingress & Semantic Cache", type="run") as step1:
        step1.output = "Kiểm tra Prompt Injection & Redis Cosine Similarity Cache..."

    # Step 2: Hybrid Search & Qdrant
    async with cl.Step(name="🔍 Qdrant Hybrid Discovery & Reranking", type="tool") as step2:
        step2.output = "Tìm kiếm kết hợp Dense Vector (bge-m3) + Sparse BM25 và Cross-Encoder Reranker..."

    # Process query
    customer_phone = message.content.strip() if pending_phone else None
    result = process_customer_query(
        query=message.content,
        thread_id=thread_id,
        customer_phone=customer_phone
    )

    # Step 3: FastMCP Action
    if result.get("inventory"):
        async with cl.Step(name="📞 FastMCP Client (check_store_inventory)", type="tool") as step3:
            step3.output = f"Gọi FastMCP Server truy vấn tồn kho PostgreSQL: {result['inventory']}"

    # Check if awaiting confirmation
    if result.get("awaiting_confirmation"):
        cl.user_session.set("pending_phone", True)
    elif result.get("booking_ticket"):
        cl.user_session.set("pending_phone", False)
        async with cl.Step(name="🔒 FastMCP Write Action (create_booking_ticket)", type="tool") as step4:
            step4.output = f"Đã xuất vé giữ hàng: {result['booking_ticket'].get('ticket_id')}"

    # Final response
    await cl.Message(content=result.get("response", "Đã xử lý xong yêu cầu.")).send()
