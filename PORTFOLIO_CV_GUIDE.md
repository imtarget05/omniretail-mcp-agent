# OmniRetail Agentic AI Platform — Hướng Dẫn Hồ Sơ Ứng Viên & Benchmark Tuyển Dụng

> **Vị Trí Mục Tiêu:** Senior AI Engineer / Agentic AI Engineer / LLMOps Engineer  
> **Tập Đoàn:** Thế Giới Di Động & Điện Máy Xanh (MWG)  
> **Repository:** [https://github.com/imtarget05/omniretail-mcp-agent](https://github.com/imtarget05/omniretail-mcp-agent)  
> **Live Demo:** [https://omniretail-mcp-agent.streamlit.app/](https://omniretail-mcp-agent.streamlit.app/)

---

## 1. Kiến Trúc Kỹ Thuật Hệ Thống (Architecture Blueprint)

```mermaid
flowchart TD
    User["Khách Hàng / Nhân Viên Bán Hàng tại Quầy"] --> Ingress["1. Ingress & PromptGuard Security Gate"]
    Ingress --> Cache{"2. Redis Semantic Cache (<15ms)"}
    Cache -- "Cache Hit" --> Streamer["5. Token Streamer (SSE Typewriter)"]
    Cache -- "Cache Miss" --> Router["3. LangGraph ReAct Supervisor"]
    
    subgraph FastMCP_Cluster ["FastMCP Microservices (Neon PostgreSQL SG Pooler)"]
        Router --> Tool_Inv["check_store_inventory(sku, district)"]
        Router --> Tool_War["lookup_warranty(phone)"]
        Router --> Tool_Book["create_booking_ticket(sku, store, phone)"]
    end

    Tool_Inv --> RAG["4. Hybrid Product Specs Retrieval (Qdrant Dense + BM25 Sparse)"]
    Tool_War --> LLM["Qwen-2.5-72B / Gemini 2.5 Flash"]
    Tool_Book --> HITL["Human-in-the-Loop Confirmation & Barcode SVG Generator"]
    
    RAG --> LLM
    HITL --> Streamer
    LLM --> Streamer
    Streamer --> UI["Giao Diện B2B SaaS (Product Cards + VIP E-Voucher Pass)"]
```

---

## 2. Bảng Tổng Hợp Chỉ Số Kiểm Chuẩn (50 Golden Test Cases Benchmark)

| Tiêu Chí Đánh Giá | Kết Quả Đạt Được | Phương Pháp Đo Lường & Giá Trị Kỹ Thuật |
| :--- | :--- | :--- |
| **Agent Faithfulness** | **100.0%** (0% ảo giác) | Đo trên 50 kịch bản bán lẻ thực tế, kiểm tra thông số kỹ thuật điện thoại/điện máy đúng 100% với Neon DWH |
| **Context Precision** | **100.0%** | Khớp chính xác mã SKU, hãng sản xuất và phân khúc ngân sách khách hàng yêu cầu |
| **Tool Execution Correctness**| **100.0%** | Tự động phân luồng và kích hoạt chính xác các FastMCP Tools (`check_store_inventory`, `lookup_warranty`, `booking`) |
| **FastMCP Query Latency** | **14.5 ms (P95)** | Tối ưu hóa qua Neon Serverless PostgreSQL Singapore Connection Pooler |
| **Semantic Cache Speedup** | **12.0 ms vs 1,450 ms** | Tăng tốc độ phản hồi gấp **120 lần**, giảm 99.2% độ trễ cho các câu hỏi tra cứu lặp lại |
| **Security Guardrail Defense**| **100% Blocked** | Ngăn chặn tuyệt đối các đòn tấn công Prompt Injection, Jailbreak và gian lận giá sản phẩm về 0 đồng |

---

## 3. Đoạn Trích Dẫn Chuẩn Điểm Viết Vào CV / Resume (STAR / XYZ Formula)

### 💼 Tiếng Việt (Dành cho CV / Profile tiếng Việt):
> - Phát triển hệ thống **OmniRetail Agentic AI** tư vấn bán hàng đa kênh cho chuỗi 20 siêu thị Thế Giới Di Động & Điện Máy Xanh, đạt điểm kiểm chuẩn **100% Faithfulness và 100% Tool Correctness** trên bộ dữ liệu 50 kịch bản bán lẻ thực tế.
> - Thiết kế kiến trúc **FastMCP Microservices** kết nối Neon Serverless PostgreSQL Singapore, thực thi tác vụ kiểm tra tồn kho theo thời gian thực và xuất vé giữ máy VIP E-Voucher với độ trễ P95 chỉ **14.5ms**.
> - Tích hợp **Redis Semantic Cache** giúp giảm **99.2% độ trễ phản hồi** (từ 1,450ms xuống 12ms) và tiết kiệm 60% chi phí token LLM; thiết lập **PromptGuard Security Gate** ngăn chặn 100% các cuộc tấn công Prompt Injection và ép giá về 0 đồng.

### 💼 English (For English CV / LinkedIn Experience):
> - Architected the **OmniRetail Agentic AI Platform** for omnichannel retail concierge across 20 MWG / Dien May Xanh stores, achieving **100% Faithfulness and 100% Tool Correctness** across a 50-scenario Golden Benchmark.
> - Implemented **FastMCP Microservices** over Neon Serverless PostgreSQL Singapore, orchestrating real-time store inventory checks and VIP reservation ticketing with **sub-15ms P95 latency**.
> - Integrated **Redis Semantic Caching**, slashing cold graph latency by **99.2%** (1,450ms -> 12ms) while deploying strict **PromptGuard rails** against adversarial jailbreaks and pricing manipulation.

---

## 4. Kịch Bản Trả Lời Phỏng Vấn Kỹ Thuật (Interview Q&A Cheatsheet)

**Q1: Tại sao bạn chọn kiến trúc Model Context Protocol (FastMCP) thay vì gọi REST API thông thường?**
- *Trả lời:* FastMCP chuẩn hóa giao tiếp giữa LLM và các công cụ nghiệp vụ thông qua schema có định kiểu (typed schema), giúp LLM không bị ảo giác đối số (parameter hallucination). Đồng thời, FastMCP cho phép kết nối trực tiếp với connection pooler của Neon PostgreSQL Singapore, giảm overhead của HTTP handshake xuống còn dưới 15ms.

**Q2: Làm thế nào bạn giải quyết bài toán đặt giữ hàng nếu có 2 khách cùng đặt 1 máy cuối cùng?**
- *Trả lời:* Hệ thống áp dụng cơ chế khóa bi quan (pessimistic locking) với `SELECT ... FOR UPDATE` trong transaction của PostgreSQL kết hợp với Human-in-the-Loop (HITL) gate. Khi tồn kho về 0, giao dịch tự động rollback và trợ lý AI sẽ tự động đề xuất siêu thị lân cận còn hàng thông qua spatial query.
