from pydantic import BaseModel, Field
from typing import Optional, List

class Measurements(BaseModel):
    """Flexible measurements to handle shoes, pants, and shirts."""
    waist: Optional[float] = None
    inseam: Optional[float] = None
    chest: Optional[float] = None
    length: Optional[float] = None
    sleeve: Optional[float] = None
    bust: Optional[float] = None
    foot_length: Optional[float] = None
    shirt_size: Optional[str] = None # e.g., "M", "L"
    shoe_size: Optional[int] = None

class FitRecord(BaseModel):
    item: str
    fit_rating: str  # You could use an Enum here for "perfect", "loose", etc.

class UserWardrobe(BaseModel):
    measurements: Measurements
    preferred_brands: List[str] = []
    fit_history: List[FitRecord] = []

class InventoryItem(BaseModel):
    item_id: str
    vendor_id: str
    category: str
    brand: str
    color: str
    size_tag: str
    measurements: Measurements
    condition_score: int = Field(..., ge=1, le=5) # Enforce score between 1 and 5
    price: float = Field(..., gt=0) # Price must be positive
    image_url: str