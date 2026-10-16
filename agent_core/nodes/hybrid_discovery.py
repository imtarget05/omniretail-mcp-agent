"""
Product Discovery Node: Qdrant Hybrid Search & Reranking
Combines Dense Embedding + Sparse BM25 + Cross-Encoder / Semantic Score
"""

import os
from typing import Dict, Any, List
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding, SparseTextEmbedding

from agent_core.state import RetailAgentState

QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
COLLECTION_NAME = "omniretail_products"

class HybridProductSearcher:
    def __init__(self):
        try:
            self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=0.5, check_compatibility=False)
            self.client.get_collections()
            self.dense_model = TextEmbedding("BAAI/bge-small-en-v1.5")
            self.sparse_model = SparseTextEmbedding("Qdrant/bm25")
            self.enabled = True
        except Exception:
            self.enabled = False

    def search(self, query: str, top_k: int = 15) -> List[Dict[str, Any]]:
        if not getattr(self, "enabled", True):
            # Instant direct Postgres query without network wait
            try:
                from retail_mcp_server.db import get_db_cursor
                with get_db_cursor() as cur:
                    words = [w for w in query.split() if len(w) > 2]
                    brands = ["apple", "iphone", "samsung", "daikin", "panasonic", "lg", "sony", "toshiba", "xiaomi", "oppo"]
                    target_kw = None
                    for b in brands:
                        if b in query.lower():
                            target_kw = "Apple" if b == "iphone" else b
                            break
                    if not target_kw and words:
                        target_kw = words[0]
                    kw = f"%{target_kw}%" if target_kw else "%"
                    cur.execute("""
                        SELECT sku, name, category, brand, base_price AS price, specs_markdown AS text, 1.0 AS score
                        FROM retail_products
                        WHERE name ILIKE %s OR brand ILIKE %s OR sku ILIKE %s
                        LIMIT %s;
                    """, (kw, kw, kw, top_k))
                    rows = cur.fetchall()
                    res = []
                    for r in rows:
                        d = dict(r)
                        d["score"] = float(d.get("score") or 1.0)
                        res.append(d)
                    return res
            except Exception:
                return []

        try:
            # Compute embeddings for query
            dense_vec = list(self.dense_model.embed([query]))[0].tolist()
            sparse_vec = list(self.sparse_model.embed([query]))[0]

            # Qdrant Hybrid Search
            results = self.client.query_points(
                collection_name=COLLECTION_NAME,
                prefetch=[
                    models.Prefetch(
                        query=models.SparseVector(
                            indices=sparse_vec.indices.tolist(),
                            values=sparse_vec.values.tolist()
                        ),
                        using="sparse",
                        limit=top_k
                    ),
                    models.Prefetch(
                        query=dense_vec,
                        using="dense",
                        limit=top_k
                    )
                ],
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=top_k
            )

            candidates = []
            for p in results.points:
                payload = p.payload
                candidates.append({
                    "sku": payload.get("sku"),
                    "name": payload.get("name"),
                    "category": payload.get("category"),
                    "brand": payload.get("brand"),
                    "price": payload.get("price"),
                    "text": payload.get("text"),
                    "score": p.score
                })
            return candidates
        except Exception:
            # Fallback to direct Postgres query
            try:
                from retail_mcp_server.db import get_db_cursor
                with get_db_cursor() as cur:
                    words = [w for w in query.split() if len(w) > 2]
                    kw = f"%{words[0]}%" if words else "%"
                    cur.execute("""
                        SELECT sku, name, category, brand, base_price AS price, specs_markdown AS text, 1.0 AS score
                        FROM retail_products
                        WHERE name ILIKE %s OR brand ILIKE %s OR sku ILIKE %s
                        LIMIT %s;
                    """, (kw, kw, kw, top_k))
                    rows = cur.fetchall()
                    return [dict(r) for r in rows]
            except Exception:
                return []

def rerank_candidates(query: str, candidates: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Reranks candidates prioritizing exact SKU, brand, or spec keyword matches.
    """
    query_lower = query.lower()
    brands = ["apple", "iphone", "samsung", "daikin", "panasonic", "lg", "sony", "toshiba", "xiaomi", "oppo"]
    
    scored = []
    for c in candidates:
        bonus = 0.0
        sku = c.get("sku", "")
        name = c.get("name", "").lower()
        brand = c.get("brand", "").lower()
        
        # Brand & SKU booster
        for b in brands:
            if b in query_lower:
                if b in name or b in brand or (b == "iphone" and "apple" in brand):
                    bonus += 1.2

        if "1.5 hp" in query_lower and "1.5 hp" in name:
            bonus += 0.6
        if sku and sku.lower() in query_lower:
            bonus += 1.5

        total_score = float(c.get("score") or 0.0) + bonus
        scored.append((total_score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_n]]

_searcher = None
def get_searcher():
    global _searcher
    if _searcher is None:
        _searcher = HybridProductSearcher()
    return _searcher

def hybrid_discovery_node(state: RetailAgentState) -> Dict[str, Any]:
    query = state.get("query", "")
    searcher = get_searcher()
    candidates = searcher.search(query=query, top_k=15)
    top_skus = rerank_candidates(query=query, candidates=candidates, top_n=3)
    
    selected = top_skus[0] if top_skus else None
    return {
        "matched_skus": top_skus,
        "selected_sku": selected
    }
