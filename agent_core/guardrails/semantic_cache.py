"""
Redis Semantic Cache (<50ms response for repeated retail queries)
Uses Cosine Similarity of fastembed dense vectors.
"""

import os
import json
import redis
import numpy as np
from typing import Optional, Tuple
from fastembed import TextEmbedding

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

class RetailSemanticCache:
    def __init__(self, similarity_threshold: float = 0.95):
        self.threshold = similarity_threshold
        try:
            self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
            self.r.ping()
            self.enabled = True
        except Exception:
            self.enabled = False
        self.embed_model = TextEmbedding("BAAI/bge-small-en-v1.5")

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def get(self, query: str) -> Optional[str]:
        if not self.enabled:
            return None
        try:
            query_vec = list(self.embed_model.embed([query]))[0]
            # Fetch all cached entries
            keys = self.r.keys("semantic_cache:*")
            best_sim = 0.0
            best_resp = None

            for k in keys:
                raw_data = self.r.get(k)
                if not raw_data:
                    continue
                entry = json.loads(raw_data.decode("utf-8"))
                cached_vec = np.array(entry["embedding"])
                sim = self._cosine_similarity(query_vec, cached_vec)
                if sim > best_sim:
                    best_sim = sim
                    best_resp = entry["response"]

            if best_sim >= self.threshold:
                print(f"⚡ Semantic Cache Hit! Cosine Similarity: {best_sim:.4f}")
                return best_resp
        except Exception as e:
            print(f"Semantic Cache read error: {e}")
        return None

    def set(self, query: str, response: str, ttl: int = 3600):
        if not self.enabled:
            return
        try:
            query_vec = list(self.embed_model.embed([query]))[0].tolist()
            cache_id = f"semantic_cache:{hash(query)}"
            data = {
                "query": query,
                "embedding": query_vec,
                "response": response
            }
            self.r.setex(cache_id, ttl, json.dumps(data, ensure_ascii=False))
        except Exception as e:
            print(f"Semantic Cache write error: {e}")
