from datetime import datetime
from typing import Optional, List, Dict

from sqlmodel import SQLModel, Field, create_engine, Session, select

from fit_flow.models import Measurements


class UserProfile(SQLModel, table=True):
    """User's body measurements and preferences"""
    __tablename__ = "user_profiles"

    user_id: str = Field(primary_key=True)
    # Store measurements as JSON string (SQLite doesn't have a JSON type)
    measurements_json: str = Field(default="{}")
    preferred_brands_json: str = Field(default="[]")
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def measurements(self) -> Measurements:
        """Parse JSON to Pydantic model"""
        import json
        return Measurements(**json.loads(self.measurements_json))

    @property
    def preferred_brands(self) -> List[str]:
        """Parse JSON to list"""
        import json
        return json.loads(self.preferred_brands_json)


class WardrobeItem(SQLModel, table=True):
    """User's owned clothing items"""
    __tablename__ = "user_wardrobe"

    wardrobe_item_id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="user_profiles.user_id", index=True)
    name: str
    category: str = Field(index=True)
    brand: Optional[str] = None
    color: Optional[str] = None
    size_tag: Optional[str] = None
    measurements_json: Optional[str] = None
    fit_rating: str = "not_tried"  # perfect, good, loose, tight, not_tried
    condition_rating: int = Field(default=4, ge=1, le=5)
    image_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def measurements(self) -> Optional[Measurements]:
        """Parse JSON to Pydantic model"""
        import json
        if self.measurements_json:
            return Measurements(**json.loads(self.measurements_json))
        return None


class VendorItem(SQLModel, table=True):
    """Vendor marketplace inventory"""
    __tablename__ = "vendor_inventory"

    item_id: str = Field(primary_key=True)
    vendor_id: str = Field(index=True)
    category: str = Field(index=True)
    brand: Optional[str] = Field(default=None, index=True)
    color: Optional[str] = None
    size_tag: Optional[str] = None
    measurements_json: Optional[str] = None
    condition_score: int = Field(ge=1, le=5)
    price: float = Field(gt=0)
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def measurements(self) -> Optional[Measurements]:
        """Parse JSON to Pydantic model"""
        import json
        if self.measurements_json:
            return Measurements(**json.loads(self.measurements_json))
        return None

# Database setup
WARDROBE_DB_URL = "sqlite:///wardrobe.db"
engine = create_engine(WARDROBE_DB_URL, echo=False)

def init_wardrobe_db():
    """Create tables if they don't exist"""
    SQLModel.metadata.create_all(engine)
    print("✅ Database initialized")

def create_user_profile(
        user_id: str,
        measurements: Measurements,
        preferred_brands: List[str] = None
) -> Optional[UserProfile]:
    """
    Create a new user profile

    Args:
        user_id: Unique identifier for the user (e.g., "user_123")
        measurements: User's body measurements (e.g., height, weight, etc.)
        preferred_brands: List of preferred brands (e.g., ["Zara", "Dockers"])

    Returns:
        Optional[UserProfile]: User profile object if created successfully, None otherwise
    """
    user_profile = UserProfile(user_id=user_id, measurements=measurements, preferred_brands=preferred_brands or [])
    with Session(engine) as session:
        session.add(user_profile)
        session.commit()
        session.refresh(user_profile)
    return user_profile

def get_user_profile(user_id: str) -> Optional[Dict]:
    """
    Retrieve a user profile by ID

    Args:
        user_id: Unique identifier for our user

    Returns:
        Optional[Dict] which is more details about the user
    """
    with Session(engine) as session:
        profile = session.get(UserProfile, user_id)
        if not profile:
            return None

        return {
            "user_id": profile.user_id,
            "measurements": profile.measurements.model_dump(exclude_none=True),
            "preferred_brands": profile.preferred_brands,
            "created_at": profile.created_at.isoformat()
        }


def add_wardrobe_item(
        name: str,
        category: str,
        brand: Optional[str] = None,
        color: Optional[str] = None,
        size_tag: Optional[str] = None,
        measurements: Optional[Measurements] = None,
        fit_rating: str = "not_tried",
        condition_rating: int = 4,
        image_url: Optional[str] = None,
        notes: Optional[str] = None
) -> str:
    """
    Add item to wardrobe. Returns wardrobe_item_id

    Args:
        name: Name of the item
        category: Category of the wardrobe item
        brand:
        color:
        size_tag:
        measurements:
        fit_rating:
        condition_rating:
        image_url:
        notes:
    """
    import uuid

    with Session(engine) as session:
        wardrobe_item_id = f"W{uuid.uuid4().hex[:8].upper()}"

        item = WardrobeItem(
            wardrobe_item_id=wardrobe_item_id,
            user_id=f"item-{uuid.uuid4().hex[:8].upper()}",
            name=name,
            category=category.lower(),
            brand=brand,
            color=color,
            size_tag=size_tag,
            measurements_json=measurements.model_dump_json() if measurements else None,
            fit_rating=fit_rating,
            condition_rating=condition_rating,
            image_url=image_url,
            notes=notes
        )

        session.add(item)
        session.commit()
        return wardrobe_item_id


def get_user_wardrobe(user_id: str, category: Optional[str] = None) -> List[Dict]:
    """
    Get user's wardrobe items

    Args:
        user_id: unique identifier for the user
        category: clothes categories. e.g., shirts, trousers
    """
    with Session(engine) as session:
        statement = select(WardrobeItem).where(WardrobeItem.user_id == user_id)

        if category:
            statement = statement.where(WardrobeItem.category == category.lower())

        statement = statement.order_by(WardrobeItem.created_at.desc())
        items = session.exec(statement).all()

        # Convert to dicts
        result = []
        for item in items:
            item_dict = {
                "wardrobe_item_id": item.wardrobe_item_id,
                "user_id": item.user_id,
                "name": item.name,
                "category": item.category,
                "brand": item.brand,
                "color": item.color,
                "size_tag": item.size_tag,
                "measurements": item.measurements.model_dump(exclude_none=True) if item.measurements else None,
                "fit_rating": item.fit_rating,
                "condition_rating": item.condition_rating,
                "image_url": item.image_url,
                "notes": item.notes,
                "created_at": item.created_at.isoformat()
            }
            result.append(item_dict)

        return result


def delete_wardrobe_item(user_id: str, wardrobe_item_id: str) -> bool:
    """
    Delete wardrobe item

    Args:
        user_id: unique_identifier for the user
        wardrobe_item_id: unique identifier for the wardrobe item.
    """
    with Session(engine) as session:
        item = session.get(WardrobeItem, wardrobe_item_id)
        if item and item.user_id == user_id:
            session.delete(item)
            session.commit()
            return True
        return False


# ==================== VENDOR INVENTORY OPERATIONS ====================

def add_vendor_item(
        item_id: str,
        vendor_id: str,
        category: str,
        brand: Optional[str] = None,
        color: Optional[str] = None,
        size_tag: Optional[str] = None,
        measurements: Optional[Measurements] = None,
        condition_score: int = 4,
        price: float = 0,
        image_url: Optional[str] = None
) -> bool:
    """
    Add vendor item

    Args:
        item_id: unique identifier of the clothing.
        vendor_id: unique identifier of the vendor of the clothing.
        category: clothing category. E.g., Trousers, Shirts
        brand: Clothing brand if any.
        color: Color of clothing.
        size_tag: Size of the clothing.
        measurements: Clothing measurements as per the user's wardrobe.
        condition_score: How good the clothing is despite being second-hand.
        price: Clothing price in Kenyan Shillings
        image_url: Image URL is any.
    """
    with Session(engine) as session:
        # Check if exists
        existing = session.get(VendorItem, item_id)
        if existing:
            return False

        item = VendorItem(
            item_id=item_id,
            vendor_id=vendor_id,
            category=category.lower(),
            brand=brand,
            color=color,
            size_tag=size_tag,
            measurements_json=measurements.model_dump_json() if measurements else None,
            condition_score=condition_score,
            price=price,
            image_url=image_url
        )

        session.add(item)
        session.commit()
        return True


def search_vendor_inventory(
        category: Optional[str] = None,
        brand: Optional[str] = None,
        max_price: Optional[float] = None,
        color: Optional[str] = None,
        min_condition: int = 3
) -> List[Dict]:
    """
    Search vendor inventory

    Args:
        category: Category of clothes. E.g., Trousers, Shirt
        brand: Brand of clothes if any.
        max_price: Maximum price of the clothes specified by the user.
        color: Color of the clothes.
        min_condition: Wearability or how good the clothing still is.
    """
    with Session(engine) as session:
        statement = select(VendorItem).where(VendorItem.condition_score >= min_condition)

        if category:
            statement = statement.where(VendorItem.category == category.lower())
        if brand:
            statement = statement.where(VendorItem.brand == brand)
        if color:
            statement = statement.where(VendorItem.color == color.lower())
        if max_price is not None:
            statement = statement.where(VendorItem.price <= max_price)

        statement = statement.order_by(VendorItem.created_at.desc())
        items = session.exec(statement).all()

        # Convert to dicts
        result = []
        for item in items:
            item_dict = {
                "item_id": item.item_id,
                "vendor_id": item.vendor_id,
                "category": item.category,
                "brand": item.brand,
                "color": item.color,
                "size_tag": item.size_tag,
                "measurements": item.measurements.model_dump(exclude_none=True) if item.measurements else None,
                "condition_score": item.condition_score,
                "price": item.price,
                "image_url": item.image_url,
                "created_at": item.created_at.isoformat()
            }
            result.append(item_dict)

        return result


def get_item_by_id(item_id: str) -> Optional[Dict]:
    """Get a single vendor item"""
    with Session(engine) as session:
        item = session.get(VendorItem, item_id)
        if not item:
            return None

        return {
            "item_id": item.item_id,
            "vendor_id": item.vendor_id,
            "category": item.category,
            "brand": item.brand,
            "color": item.color,
            "size_tag": item.size_tag,
            "measurements": item.measurements.model_dump(exclude_none=True) if item.measurements else None,
            "condition_score": item.condition_score,
            "price": item.price,
            "image_url": item.image_url,
            "created_at": item.created_at.isoformat()
        }


# ==================== IN-MEMORY CACHE ====================

class InventoryCache:
    """Fast O(1) lookup for vendor items"""

    def __init__(self):
        self._cache: Dict[str, Dict] = {}

    def refresh(self):
        """Reload cache from a database"""
        with Session(engine) as session:
            items = session.exec(select(VendorItem)).all()
            self._cache = {}

            for item in items:
                self._cache[item.item_id] = {
                    "item_id": item.item_id,
                    "vendor_id": item.vendor_id,
                    "category": item.category,
                    "brand": item.brand,
                    "color": item.color,
                    "size_tag": item.size_tag,
                    "measurements": item.measurements.model_dump(exclude_none=True) if item.measurements else None,
                    "condition_score": item.condition_score,
                    "price": item.price,
                    "image_url": item.image_url
                }

    def get(self, item_id: str) -> Optional[Dict]:
        """Fast lookup by ID"""
        if not self._cache:
            self.refresh()
        return self._cache.get(item_id)


_inventory_cache = InventoryCache()


def get_item_details_fast(item_id: str) -> Optional[Dict]:
    """Fast cached lookup"""
    return _inventory_cache.get(item_id)


# ==================== SEED DATA ====================

def seed_database():
    """Populate with test data"""
    # Create user profile
    create_user_profile(
        "user_123",
        Measurements(waist=32, inseam=30, chest=38, shirt_size="M"),
        ["Zara", "H&M", "Dockers"]
    )

    # Add wardrobe items
    add_wardrobe_item(
        "user_123", "Black Zara Trousers", "trousers",
        brand="Zara", color="black", size_tag="32",
        measurements=Measurements(waist=32, inseam=30),
        fit_rating="perfect", condition_rating=4
    )

    add_wardrobe_item(
        "user_123", "Blue H&M Shirt", "shirt",
        brand="H&M", color="blue", size_tag="M",
        measurements=Measurements(chest=39, length=28),
        fit_rating="slightly_loose", condition_rating=5
    )

    # Add vendor items
    vendor_items = [
        ("V001", "vendor_A", "trousers", "Dockers", "black", "32", Measurements(waist=33, inseam=29), 4, 1200),
        ("V002", "vendor_B", "shirt", "Zara", "blue", "M", Measurements(chest=39, length=28), 5, 800),
        ("V003", "vendor_A", "trousers", "Levi's", "blue", "32", Measurements(waist=32, inseam=30), 3, 1500),
        ("V004", "vendor_C", "shoes", "Adidas", "white", "10", Measurements(foot_length=28), 4, 4500),
    ]

    for item_id, vendor_id, category, brand, color, size_tag, measurements, condition, price in vendor_items:
        add_vendor_item(item_id, vendor_id, category, brand, color, size_tag, measurements, condition, price)

    # Refresh cache
    _inventory_cache.refresh()

    print("✅ Database seeded with test data")


if __name__ == "__main__":
    init_wardrobe_db()
    seed_database()