"""
Data Ingestion Pipeline for OmniRetail MCP Agent
1. Creates PostgreSQL schemas and seeds 520 products, 20 stores, and store inventories.
2. Chunks product specs with MarkdownTableAwareChunker.
3. Generates Dense & Sparse vectors and uploads to Qdrant collection `omniretail_products`.
"""

import os
import json
import time
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models

from markdown_chunker import MarkdownTableAwareChunker
from seed_generator import main as generate_seeds, OUTPUT_FILE as SEED_JSON_PATH

PG_HOST = os.environ.get("POSTGRES_HOST", "localhost")
PG_PORT = int(os.environ.get("POSTGRES_PORT", "5433"))
PG_USER = os.environ.get("POSTGRES_USER", "retail_admin")
PG_PASS = os.environ.get("POSTGRES_PASSWORD", "retail_password")
PG_DB = os.environ.get("POSTGRES_DB", "retail_ecosystem")

QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", "6333"))
COLLECTION_NAME = "omniretail_products"

def wait_for_postgres(retries=15, delay=2):
    print(f"Connecting to PostgreSQL at {PG_HOST}:{PG_PORT}...")
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASS, dbname=PG_DB
            )
            print("✅ PostgreSQL connected successfully.")
            return conn
        except Exception as e:
            print(f"Waiting for Postgres... ({i+1}/{retries}) - {e}")
            time.sleep(delay)
    raise RuntimeError("Failed to connect to PostgreSQL after retries.")

def init_postgres_schema(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS retail_stores (
            store_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            district VARCHAR(100) NOT NULL,
            address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS retail_products (
            sku VARCHAR(100) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL,
            brand VARCHAR(100) NOT NULL,
            base_price NUMERIC(15, 2) NOT NULL,
            warranty_months INT DEFAULT 12,
            description TEXT,
            specs_markdown TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS retail_inventory (
            inventory_id SERIAL PRIMARY KEY,
            sku VARCHAR(100) REFERENCES retail_products(sku) ON DELETE CASCADE,
            store_id VARCHAR(50) REFERENCES retail_stores(store_id) ON DELETE CASCADE,
            stock_quantity INT NOT NULL DEFAULT 0,
            store_price NUMERIC(15, 2) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(sku, store_id)
        );

        CREATE TABLE IF NOT EXISTS retail_warranties (
            warranty_id SERIAL PRIMARY KEY,
            phone VARCHAR(20) NOT NULL,
            customer_name VARCHAR(150),
            sku VARCHAR(100) REFERENCES retail_products(sku),
            purchase_date DATE NOT NULL,
            expiry_date DATE NOT NULL,
            status VARCHAR(50) DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS retail_booking_tickets (
            ticket_id VARCHAR(50) PRIMARY KEY,
            sku VARCHAR(100) REFERENCES retail_products(sku),
            store_id VARCHAR(50) REFERENCES retail_stores(store_id),
            customer_name VARCHAR(150) NOT NULL,
            customer_phone VARCHAR(20) NOT NULL,
            delivery_time VARCHAR(100),
            status VARCHAR(50) DEFAULT 'CONFIRMED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
    print("✅ PostgreSQL retail schema initialized.")

def seed_postgres_data(conn, data):
    with conn.cursor() as cur:
        # Stores
        store_records = [(s["store_id"], s["name"], s["district"], s["address"]) for s in data["stores"]]
        execute_values(cur, """
            INSERT INTO retail_stores (store_id, name, district, address)
            VALUES %s ON CONFLICT (store_id) DO UPDATE SET name = EXCLUDED.name, address = EXCLUDED.address;
        """, store_records)

        # Products
        prod_records = [
            (p["sku"], p["name"], p["category"], p["brand"], p["base_price"], p["warranty_months"], p["description"], p["specs_markdown"])
            for p in data["products"]
        ]
        execute_values(cur, """
            INSERT INTO retail_products (sku, name, category, brand, base_price, warranty_months, description, specs_markdown)
            VALUES %s ON CONFLICT (sku) DO NOTHING;
        """, prod_records)

        # Inventory
        inv_records = [(inv["sku"], inv["store_id"], inv["stock_quantity"], inv["store_price"]) for inv in data["inventory"]]
        execute_values(cur, """
            INSERT INTO retail_inventory (sku, store_id, stock_quantity, store_price)
            VALUES %s ON CONFLICT (sku, store_id) DO UPDATE SET stock_quantity = EXCLUDED.stock_quantity;
        """, inv_records)

        # Warranties
        war_records = [
            (w["phone"], w["customer_name"], w["sku"], w["purchase_date"], w["expiry_date"], w["status"])
            for w in data["warranties"]
        ]
        execute_values(cur, """
            INSERT INTO retail_warranties (phone, customer_name, sku, purchase_date, expiry_date, status)
            VALUES %s;
        """, war_records)

        conn.commit()
    print(f"✅ Loaded {len(data['stores'])} stores, {len(data['products'])} products, {len(data['inventory'])} inventory lines into PostgreSQL.")

def ingest_into_qdrant(data):
    print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    from fastembed import TextEmbedding, SparseTextEmbedding
    print("Initializing local FastEmbed models (Dense: BAAI/bge-small-en-v1.5 & Sparse: BM25)...")
    dense_model = TextEmbedding("BAAI/bge-small-en-v1.5")
    sparse_model = SparseTextEmbedding("Qdrant/bm25")

    vector_size = 384  # bge-small-en-v1.5 embedding size

    # Recreate collection
    print(f"Setting up Qdrant collection `{COLLECTION_NAME}` with Hybrid Search...")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
        },
        sparse_vectors_config={
            "sparse": models.SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
        }
    )

    chunker = MarkdownTableAwareChunker()
    all_chunks = []
    for p in data["products"]:
        chunks = chunker.chunk_product(p)
        all_chunks.extend(chunks)

    print(f"Generated {len(all_chunks)} table-aware markdown chunks. Computing embeddings...")
    texts = [c["text"] for c in all_chunks]
    dense_embeddings = list(dense_model.embed(texts))
    sparse_embeddings = list(sparse_model.embed(texts))

    points = []
    for i, chunk in enumerate(all_chunks):
        sparse_vec = sparse_embeddings[i]
        point = models.PointStruct(
            id=i,
            vector={
                "dense": dense_embeddings[i].tolist(),
                "sparse": models.SparseVector(
                    indices=sparse_vec.indices.tolist(),
                    values=sparse_vec.values.tolist()
                )
            },
            payload={
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                **chunk["metadata"]
            }
        )
        points.append(point)

    # Upload in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        print(f"  Uploaded chunks {i} - {i+len(batch)} / {len(points)}")

    print(f"✅ Successfully ingested {len(points)} chunks into Qdrant collection `{COLLECTION_NAME}` with Dense + Sparse BM25!")

def main():
    if not SEED_JSON_PATH.exists():
        generate_seeds()

    with open(SEED_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Postgres Ingestion
    conn = wait_for_postgres()
    init_postgres_schema(conn)
    seed_postgres_data(conn, data)
    conn.close()

    # 2. Qdrant Ingestion
    ingest_into_qdrant(data)
    print("\n🎉 ALL DATA PREPARATION COMPLETE FOR PROJECT 1!")

if __name__ == "__main__":
    main()
