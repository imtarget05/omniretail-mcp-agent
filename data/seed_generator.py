"""
Synthetic Retail Dataset Generator for OmniRetail MCP Agent
Generates 500+ electronics, phones, and appliances with rich Markdown spec sheets,
20 HCMC stores across districts, and realistic initial inventory levels.
"""

import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent
OUTPUT_FILE = DATA_DIR / "retail_seed_data.json"

CATEGORIES = [
    ("may_lanh", "Máy lạnh / Điều hòa", ["Daikin", "Panasonic", "LG", "Toshiba", "Casper", "Aqua"]),
    ("dien_thoai", "Điện thoại di động", ["Apple", "Samsung", "Xiaomi", "Oppo", "Vivo", "Realme"]),
    ("tu_lanh", "Tủ lạnh", ["LG", "Samsung", "Panasonic", "Toshiba", "Sharp", "Hitachi"]),
    ("may_giat", "Máy giặt", ["LG", "Electrolux", "Toshiba", "Panasonic", "Samsung"]),
    ("tivi", "Tivi", ["Sony", "Samsung", "LG", "TCL", "Casper"])
]

STORES = [
    {"store_id": "DMX_Q9_01", "name": "Điện Máy Xanh 245 Lê Văn Việt", "district": "Quận 9", "address": "245 Lê Văn Việt, Tăng Nhơn Phú B, Quận 9"},
    {"store_id": "DMX_Q9_02", "name": "Điện Máy Xanh 416 Đỗ Xuân Hợp", "district": "Quận 9", "address": "416 Đỗ Xuân Hợp, Phước Long B, Quận 9"},
    {"store_id": "TGDD_Q1_01", "name": "Thế Giới Di Động 136 Nguyễn Thái Học", "district": "Quận 1", "address": "136 Nguyễn Thái Học, Cầu Ông Lãnh, Quận 1"},
    {"store_id": "TGDD_Q1_02", "name": "Thế Giới Di Động 70 Hai Bà Trưng", "district": "Quận 1", "address": "70 Hai Bà Trưng, Bến Nghé, Quận 1"},
    {"store_id": "DMX_BT_01", "name": "Điện Máy Xanh 52 Xô Viết Nghệ Tĩnh", "district": "Bình Thạnh", "address": "52 Xô Viết Nghệ Tĩnh, P.19, Bình Thạnh"},
    {"store_id": "DMX_BT_02", "name": "Điện Máy Xanh 366 Phan Văn Trị", "district": "Bình Thạnh", "address": "366 Phan Văn Trị, P.11, Bình Thạnh"},
    {"store_id": "TGDD_TB_01", "name": "Thế Giới Di Động 380 Cộng Hòa", "district": "Tân Bình", "address": "380 Cộng Hòa, P.13, Tân Bình"},
    {"store_id": "DMX_TB_01", "name": "Điện Máy Xanh 498 Hoàng Văn Thụ", "district": "Tân Bình", "address": "498 Hoàng Văn Thụ, P.4, Tân Bình"},
    {"store_id": "DMX_TD_01", "name": "Điện Máy Xanh 18 Võ Văn Ngân", "district": "Thủ Đức", "address": "18 Võ Văn Ngân, Linh Chiểu, Thủ Đức"},
    {"store_id": "TGDD_TD_01", "name": "Thế Giới Di Động 235 Kha Vạn Cân", "district": "Thủ Đức", "address": "235 Kha Vạn Cân, Hiệp Bình Chánh, Thủ Đức"},
    {"store_id": "DMX_GV_01", "name": "Điện Máy Xanh 170 Quang Trung", "district": "Gò Vấp", "address": "170 Quang Trung, P.10, Gò Vấp"},
    {"store_id": "TGDD_GV_01", "name": "Thế Giới Di Động 561 Phan Văn Trị", "district": "Gò Vấp", "address": "561 Phan Văn Trị, P.5, Gò Vấp"},
    {"store_id": "DMX_Q7_01", "name": "Điện Máy Xanh 468 Nguyễn Thị Thập", "district": "Quận 7", "address": "468 Nguyễn Thị Thập, Tân Quy, Quận 7"},
    {"store_id": "TGDD_Q7_01", "name": "Thế Giới Di Động 182 Huỳnh Tấn Phát", "district": "Quận 7", "address": "182 Huỳnh Tấn Phát, Tân Thuận Tây, Quận 7"},
    {"store_id": "DMX_Q3_01", "name": "Điện Máy Xanh 280 Nguyễn Đình Chiểu", "district": "Quận 3", "address": "280 Nguyễn Đình Chiểu, P.5, Quận 3"},
    {"store_id": "TGDD_Q3_01", "name": "Thế Giới Di Động 468 Cách Mạng Tháng 8", "district": "Quận 3", "address": "468 Cách Mạng Tháng 8, P.11, Quận 3"},
    {"store_id": "DMX_PN_01", "name": "Điện Máy Xanh 150 Phan Đăng Lưu", "district": "Phú Nhuận", "address": "150 Phan Đăng Lưu, P.3, Phú Nhuận"},
    {"store_id": "TGDD_PN_01", "name": "Thế Giới Di Động 80 Phan Xích Long", "district": "Phú Nhuận", "address": "80 Phan Xích Long, P.2, Phú Nhuận"},
    {"store_id": "DMX_Q10_01", "name": "Điện Máy Xanh 398 đường 3 Tháng 2", "district": "Quận 10", "address": "398 đường 3 Tháng 2, P.12, Quận 10"},
    {"store_id": "TGDD_Q10_01", "name": "Thế Giới Di Động 218 Trần Hưng Đạo", "district": "Quận 10", "address": "218 Trần Hưng Đạo, P.11, Quận 10"}
]

# Anchor flagship items as per blueprint
FLAGSHIP_ITEMS = [
    {
        "sku": "ATKF35XVMV",
        "name": "Máy lạnh Daikin Inverter 1.5 HP ATKF35XVMV",
        "category": "may_lanh",
        "brand": "Daikin",
        "base_price": 12490000,
        "warranty_months": 24,
        "specs_markdown": (
            "| Tiêu chí | Thông số chi tiết |\n"
            "| :--- | :--- |\n"
            "| Công suất làm lạnh | 1.5 HP - 11.900 BTU |\n"
            "| Phạm vi hiệu quả | Từ 15 - 20m² (40 đến 60 m³) |\n"
            "| Tiêu thụ điện | 1.08 kW/h (5 sao, Hiệu suất năng lượng 5.38) |\n"
            "| Công nghệ tiết kiệm điện | Inverter, Mắt thần thông minh Econo |\n"
            "| Kháng khuẩn khử mùi | Phin lọc Enzyme Blue tích hợp lọc bụi mịn PM2.5 |\n"
            "| Chế độ gió | Tuỳ chỉnh điều khiển lên xuống tự động, trái phải tuỳ chỉnh tay |\n"
            "| Tiện ích | Làm lạnh nhanh Powerful, Chức năng chống ẩm mốc Mold Proof |"
        ),
        "description": "Máy lạnh Daikin Inverter 1.5 HP ATKF35XVMV làm lạnh cực nhanh, tiết kiệm điện êm ái, bảo vệ sức khỏe gia đình với phin lọc kép Enzyme Blue và PM2.5."
    },
    {
        "sku": "IPHONE-15-PRO-128",
        "name": "iPhone 15 Pro 128GB Titan Tự Nhiên",
        "category": "dien_thoai",
        "brand": "Apple",
        "base_price": 24990000,
        "warranty_months": 12,
        "specs_markdown": (
            "| Tiêu chí | Thông số chi tiết |\n"
            "| :--- | :--- |\n"
            "| Màn hình | Super Retina XDR OLED, 6.1 inch, 120Hz ProMotion |\n"
            "| Chip xử lý | Apple A17 Pro 6 nhân (3nm) |\n"
            "| Camera sau | Chính 48 MP & Phụ 12 MP, 12 MP (Zoom quang học 3x) |\n"
            "| Pin & Sạc | 3274 mAh, Sạc nhanh 20W, Cổng Type-C 10Gbps |\n"
            "| Chất liệu | Khung viền Titan chuẩn hàng không vũ trụ |"
        ),
        "description": "iPhone 15 Pro thiết kế titan siêu bền nhẹ, nút Tác Vụ đa năng, chip A17 Pro đột phá hiệu năng chiến game đỉnh cao."
    },
    {
        "sku": "LGF-B247JS",
        "name": "Tủ lạnh LG Inverter 649 Lít GR-B247JS",
        "category": "tu_lanh",
        "brand": "LG",
        "base_price": 16990000,
        "warranty_months": 24,
        "specs_markdown": "| Tiêu chí | Thông số |\n| Dung tích | 649 Lít Side by Side |\n| Công nghệ | Linear Inverter, Khử mùi Hygiene Fresh |",
        "description": "Tủ lạnh LG Side by Side dung tích lớn 649L sang trọng, tiết kiệm điện."
    }
]

def generate_catalog(total_items=520):
    products = list(FLAGSHIP_ITEMS)
    existing_skus = {p["sku"] for p in products}

    modifiers = ["Inverter", "Pro", "Ultra", "Eco", "Smart", "Plus", "Air", "Max"]
    
    while len(products) < total_items:
        cat_key, cat_name, brands = random.choice(CATEGORIES)
        brand = random.choice(brands)
        mod = random.choice(modifiers)
        code = f"{brand[:3].upper()}-{random.randint(100, 999)}-{mod.upper()}"
        
        if code in existing_skus:
            continue
        existing_skus.add(code)

        if cat_key == "may_lanh":
            hp = random.choice([1.0, 1.5, 2.0, 2.5])
            name = f"Máy lạnh {brand} {mod} {hp} HP {code}"
            price = int(hp * 6500000 + random.randint(5, 40) * 100000)
            specs = (
                f"| Tiêu chí | Thông số chi tiết |\n"
                f"| :--- | :--- |\n"
                f"| Công suất | {hp} HP |\n"
                f"| Tiêu thụ điện | {round(hp * 0.75, 2)} kW/h |\n"
                f"| Công nghệ | Inverter tiết kiệm điện năng |\n"
                f"| Lọc khí | Kháng khuẩn ion Ag+ |"
            )
        elif cat_key == "dien_thoai":
            ram = random.choice([6, 8, 12])
            storage = random.choice([128, 256, 512])
            name = f"Điện thoại {brand} {mod} {code} ({ram}GB/{storage}GB)"
            price = random.randint(40, 280) * 100000
            specs = (
                f"| Tiêu chí | Thông số chi tiết |\n"
                f"| :--- | :--- |\n"
                f"| Màn hình | AMOLED Full HD+, 120Hz |\n"
                f"| RAM / Bộ nhớ | {ram}GB / {storage}GB |\n"
                f"| Pin | 5000 mAh, Sạc siêu nhanh 67W |"
            )
        elif cat_key == "tu_lanh":
            liters = random.choice([250, 320, 450, 600])
            name = f"Tủ lạnh {brand} Inverter {liters} Lít {code}"
            price = random.randint(70, 250) * 100000
            specs = (
                f"| Tiêu chí | Thông số chi tiết |\n"
                f"| :--- | :--- |\n"
                f"| Dung tích | {liters} Lít |\n"
                f"| Kiểu tủ | Ngăn đá trên / Side by Side |\n"
                f"| Công nghệ | Linear Inverter khử mùi than hoạt tính |"
            )
        else:
            name = f"{cat_name} {brand} {mod} cao cấp {code}"
            price = random.randint(50, 200) * 100000
            specs = f"| Tính năng | Thông số |\n| Tiết kiệm điện | Chuẩn 5 sao |\n| Bảo hành | 24 tháng |"

        products.append({
            "sku": code,
            "name": name,
            "category": cat_key,
            "brand": brand,
            "base_price": price,
            "warranty_months": random.choice([12, 24]),
            "specs_markdown": specs,
            "description": f"Sản phẩm {name} chính hãng phân phối tại Thế Giới Di Động và Điện Máy Xanh, bảo hành 1 đổi 1 trong 1 tháng đầu nếu lỗi kỹ thuật."
        })

    # Generate Store Inventory
    inventory = []
    for p in products:
        # Give Daikin ATKF35XVMV exact inventory as in blueprint: 4 units in DMX_Q9_01
        if p["sku"] == "ATKF35XVMV":
            for s in STORES:
                qty = 4 if s["store_id"] == "DMX_Q9_01" else random.randint(0, 5)
                inventory.append({
                    "sku": p["sku"],
                    "store_id": s["store_id"],
                    "stock_quantity": qty,
                    "store_price": p["base_price"]
                })
        else:
            for s in STORES:
                # 60% chance of having stock
                qty = random.randint(1, 8) if random.random() < 0.6 else 0
                inventory.append({
                    "sku": p["sku"],
                    "store_id": s["store_id"],
                    "stock_quantity": qty,
                    "store_price": p["base_price"]
                })

    # Sample Warranties
    sample_warranties = [
        {"phone": "0901234567", "customer_name": "Nguyễn Văn Tuấn", "sku": "ATKF35XVMV", "purchase_date": "2025-06-10", "expiry_date": "2027-06-10", "status": "ACTIVE"},
        {"phone": "0988776655", "customer_name": "Trần Thị Mai", "sku": "IPHONE-15-PRO-128", "purchase_date": "2025-10-01", "expiry_date": "2026-10-01", "status": "ACTIVE"},
        {"phone": "0912345678", "customer_name": "Lê Hoàng Nam", "sku": "LGF-B247JS", "purchase_date": "2024-01-15", "expiry_date": "2026-01-15", "status": "EXPIRED"}
    ]

    return {
        "products": products,
        "stores": STORES,
        "inventory": inventory,
        "warranties": sample_warranties
    }

def main():
    print("Generating 520 products and 20 store inventories...")
    data = generate_catalog()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated {len(data['products'])} products across {len(data['stores'])} stores saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
