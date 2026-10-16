"""
Table-Aware Markdown Chunker for OmniRetail Products
Ensures technical specification tables (| col | col |) are preserved intact
and never cut across chunk boundaries.
"""

from typing import List, Dict, Any
import re

class MarkdownTableAwareChunker:
    def __init__(self, max_chunk_size: int = 1200, overlap: int = 150):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_product(self, product: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Creates semantic chunks for a product preserving the markdown table intact.
        """
        sku = product["sku"]
        name = product["name"]
        cat = product["category"]
        brand = product["brand"]
        price = product["base_price"]
        desc = product.get("description", "")
        specs_md = product.get("specs_markdown", "")

        header_context = (
            f"# {name}\n"
            f"- Mã SKU: {sku}\n"
            f"- Thương hiệu: {brand}\n"
            f"- Danh mục: {cat}\n"
            f"- Giá niêm yết: {price:,} VNĐ\n\n"
        )

        # Primary Chunk: Full product overview + complete spec table
        primary_text = f"{header_context}## Mô tả sản phẩm\n{desc}\n\n## Thông số kỹ thuật\n{specs_md}"
        
        chunks = []
        if len(primary_text) <= self.max_chunk_size:
            chunks.append({
                "chunk_id": f"{sku}_c0",
                "text": primary_text,
                "metadata": {
                    "sku": sku,
                    "name": name,
                    "category": cat,
                    "brand": brand,
                    "price": price,
                    "chunk_type": "full_product_card"
                }
            })
        else:
            # Chunk 1: Header + Description
            chunk1_text = f"{header_context}## Mô tả sản phẩm\n{desc}"
            chunks.append({
                "chunk_id": f"{sku}_c0",
                "text": chunk1_text,
                "metadata": {
                    "sku": sku,
                    "name": name,
                    "category": cat,
                    "brand": brand,
                    "price": price,
                    "chunk_type": "description"
                }
            })

            # Chunk 2: Header + Complete Spec Table (Table is kept 100% intact)
            chunk2_text = f"# Thông số kỹ thuật: {name} (SKU: {sku})\n\n{specs_md}"
            chunks.append({
                "chunk_id": f"{sku}_c1",
                "text": chunk2_text,
                "metadata": {
                    "sku": sku,
                    "name": name,
                    "category": cat,
                    "brand": brand,
                    "price": price,
                    "chunk_type": "specifications_table"
                }
            })

        return chunks
