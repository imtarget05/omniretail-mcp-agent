# 🛒 OmniRetail MCP Agent — Thế Giới Di Động & Điện Máy Xanh (MWG)

[![Production Quality Gate](https://github.com/imtarget05/omniretail-mcp-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/imtarget05/omniretail-mcp-agent/actions)
[![Database](https://img.shields.io/badge/Database-Neon%20Serverless%20Postgres-00E599)](https://neon.tech)
[![FastMCP](https://img.shields.io/badge/Microservices-FastMCP%20v0.1-blue)](https://github.com/jlowin/fastmcp)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph%20v0.2-orange)](https://github.com/langchain-ai/langgraph)

> **Omni-channel Retail AI Agent with FastMCP Microservices, Hybrid Product Discovery, Input Guardrails, and Human-in-the-Loop Booking**.  
> Simulates the retail operation of **Thế Giới Di Động (Mobile World)** and **Điện Máy Xanh (Consumer Electronics)** across 20 stores in Ho Chi Minh City, Vietnam.

---

## 🌟 Key Highlights & Engineering Architecture

1. **Model Context Protocol (FastMCP) Microservices**:
   - `check_store_inventory(sku, district)`: Real-time stock querying across 20 HCMC stores.
   - `lookup_warranty(phone)`: Customer warranty lookup with purchase dates and active statuses.
   - `create_booking_ticket(customer_name, phone, sku, store_id)`: Generates official reservation tickets in ERP.
2. **LangGraph Stateful Multi-Agent Architecture**:
   - Cyclic graph with Memory checkpointer and Supervisor routing.
   - **Human-in-the-loop (HITL) Phone Confirmation**: Prevents accidental reservation or spam bookings by interrupting workflow for customer phone verification.
3. **Multi-layer Guardrails & Semantic Cache**:
   - **Input Guardrail**: AST and pattern-based detection stopping prompt injection and price manipulation.
   - **Redis Semantic Cache**: Cosine similarity caching with sub-50ms responses for repeated queries.
4. **100% Free Production Deployment (Decoupled from Local Machine)**:
   - Hosted on **Neon Serverless PostgreSQL (Singapore `aws-ap-southeast-1`)**.
   - Zero local machine dependence. 24/7 cloud availability.
   - **AI Evaluation Gate**: **100% score** on 50 golden test cases (Faithfulness, Precision, Tool Correctness).

---

## 🚀 Live Demo & Web App

- **Streamlit Web Application**: [https://omniretail-mcp.streamlit.app](https://omniretail-mcp.streamlit.app)
- **Database Endpoint**: Neon Serverless Postgres (Singapore)

---

## 📊 AI Evaluation Benchmark Results

| Metric | Target | Achieved Score | Status |
| :--- | :--- | :--- | :--- |
| **Faithfulness** | > 85.0% | **100.0%** | ✅ PASSED |
| **Context Precision** | > 85.0% | **100.0%** | ✅ PASSED |
| **Tool Correctness** | > 85.0% | **100.0%** | ✅ PASSED |
| **Overall Score** | > 85.0% | **100.0%** | 🏆 EXCELLENT |

---

## 🛠️ Local Development & Testing

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run automated tests
pytest tests/ -v

# 3. Run AI Evaluation Gate (50 test cases)
python evaluation/evaluate.py --threshold 0.85

# 4. Start Streamlit UI
streamlit run streamlit_app.py
```
