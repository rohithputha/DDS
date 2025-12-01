from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Review(BaseModel):
    business_id: str
    user_id: str
    stars: float
    text: str
    date: str  # YYYY-MM-DD HH:MM:SS

class Business(BaseModel):
    business_id: str
    name: str
    address: str
    city: str
    state: str
    postal_code: str
    latitude: float
    longitude: float
    stars: float
    review_count: int
    is_open: int
    attributes: Optional[dict] = None
    categories: Optional[str] = None
    hours: Optional[dict] = None

class User(BaseModel):
    user_id: str
    name: str
    review_count: int
    yelping_since: str
    useful: int
    funny: int
    cool: int
    elite: str
    friends: str
    fans: int
    average_stars: float
