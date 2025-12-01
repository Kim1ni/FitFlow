from typing import Dict, Any, List

MOCK_USER_WARDROBE: Dict[str, Any] = {
    "user_123": {
        "measurements": {
            "waist": 32,
            "inseam": 30,
            "chest": 38,
            "shirt_size": "M"
        },
        "preferred_brands": ["Zara", "H&M", "Dockers"],
        "fit_history": [
            {"item": "Zara Trousers 32", "fit_rating": "perfect"},
            {"item": "H&M Shirt M", "fit_rating": "slightly_loose"}
        ]
    }
}

MOCK_VENDOR_INVENTORY: List[dict] = [
    {
        "item_id": "V001",
        "vendor_id": "vendor_A",
        "category": "trousers",
        "brand": "Dockers",
        "color": "black",
        "size_tag": "32",
        "measurements": {"waist": 33, "inseam": 29},
        "condition_score": 4,
        "price": 1200,
        "image_url": "https://example.com/dockers_trouser.jpg"
    },
    {
        "item_id": "V002",
        "vendor_id": "vendor_B",
        "category": "shirt",
        "brand": "Zara",
        "color": "blue",
        "size_tag": "M",
        "measurements": {"chest": 39, "length": 28},
        "condition_score": 5,
        "price": 800,
        "image_url": "https://example.com/zara_shirt.jpg"
    },
    {
        "item_id": "V003",
        "vendor_id": "vendor_A",
        "category": "trousers",
        "brand": "Levi's",
        "color": "blue",
        "size_tag": "32",
        "measurements": {"waist": 32, "inseam": 30},
        "condition_score": 3,
        "price": 1500,
        "image_url": "https://example.com/levis_jeans.jpg"
    },
    {
        "item_id": "V004",
        "vendor_id": "vendor_C",
        "category": "shoes",
        "brand": "Adidas",
        "color": "white",
        "size_tag": "10",
        "measurements": {"foot_length": 28},
        "condition_score": 4,
        "price": 4500,
        "image_url": "https://example.com/adidas_sneaker.jpg"
    },
    {
        "item_id": "V005",
        "vendor_id": "vendor_A",
        "category": "jacket",
        "brand": "The North Face",
        "color": "red",
        "size_tag": "L",
        "measurements": {"chest": 44, "sleeve": 35},
        "condition_score": 5,
        "price": 9900,
        "image_url": "https://example.com/tnf_jacket.jpg"
    },
    {
        "item_id": "V006",
        "vendor_id": "vendor_B",
        "category": "trousers",
        "brand": "Gap",
        "color": "khaki",
        "size_tag": "30x32",
        "measurements": {"waist": 31, "inseam": 32},
        "condition_score": 2,
        "price": 650,
        "image_url": "https://example.com/gap_chinos.jpg"
    },
    {
        "item_id": "V007",
        "vendor_id": "vendor_D",
        "category": "dress",
        "brand": "H&M",
        "color": "green",
        "size_tag": "S",
        "measurements": {"bust": 34, "length": 36},
        "condition_score": 4,
        "price": 1800,
        "image_url": "https://example.com/hm_dress.jpg"
    },
    {
        "item_id": "V008",
        "vendor_id": "vendor_C",
        "category": "shirt",
        "brand": "Uniqlo",
        "color": "white",
        "size_tag": "L",
        "measurements": {"chest": 42, "length": 29},
        "condition_score": 5,
        "price": 950,
        "image_url": "https://example.com/uniqlo_shirt.jpg"
    },
    {
        "item_id": "V009",
        "vendor_id": "vendor_A",
        "category": "shoes",
        "brand": "Nike",
        "color": "grey",
        "size_tag": "9.5",
        "measurements": {"foot_length": 27.5},
        "condition_score": 3,
        "price": 3800,
        "image_url": "https://example.com/nike_runners.jpg"
    },
    {
        "item_id": "V010",
        "vendor_id": "vendor_D",
        "category": "skirt",
        "brand": "ASOS",
        "color": "yellow",
        "size_tag": "XS",
        "measurements": {"waist": 25, "length": 18},
        "condition_score": 4,
        "price": 1100,
        "image_url": "https://example.com/asos_skirt.jpg"
    },
    {
        "item_id": "V011",
        "vendor_id": "vendor_B",
        "category": "trousers",
        "brand": "Levi's",
        "color": "black",
        "size_tag": "34x32",
        "measurements": {"waist": 34, "inseam": 32},
        "condition_score": 4,
        "price": 1800,
        "image_url": "https://example.com/levis_black_jeans.jpg"
    },
    {
        "item_id": "V012",
        "vendor_id": "vendor_C",
        "category": "jacket",
        "brand": "Columbia",
        "color": "blue",
        "size_tag": "M",
        "measurements": {"chest": 42, "sleeve": 34},
        "condition_score": 3,
        "price": 7200,
        "image_url": "https://example.com/columbia_jacket.jpg"
    },
    {
        "item_id": "V013",
        "vendor_id": "vendor_A",
        "category": "shirt",
        "brand": "Tommy Hilfiger",
        "color": "red",
        "size_tag": "S",
        "measurements": {"chest": 37, "length": 27},
        "condition_score": 5,
        "price": 1400,
        "image_url": "https://example.com/tommy_shirt.jpg"
    },
    {
        "item_id": "V014",
        "vendor_id": "vendor_D",
        "category": "shoes",
        "brand": "Vans",
        "color": "black",
        "size_tag": "7",
        "measurements": {"foot_length": 25},
        "condition_score": 2,
        "price": 2200,
        "image_url": "https://example.com/vans_shoes.jpg"
    },
    {
        "item_id": "V015",
        "vendor_id": "vendor_B",
        "category": "dress",
        "brand": "Mango",
        "color": "black",
        "size_tag": "M",
        "measurements": {"bust": 36, "length": 40},
        "condition_score": 4,
        "price": 3100,
        "image_url": "https://example.com/mango_dress.jpg"
    }
]
