"""
Pydantic models for request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Business Models

class LocationPoint(BaseModel):
    """GeoJSON Point for location."""
    type: str = Field(default="Point")
    coordinates: List[float] = Field(..., description="[longitude, latitude]")


class BusinessCreate(BaseModel):
    """Model for creating a new business."""
    name: str
    address: str
    city: str
    state: str = Field(..., min_length=2, max_length=2, description="Two-letter state code")
    postal_code: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    categories: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    hours: Optional[Dict[str, str]] = None


class BusinessResponse(BaseModel):
    """Model for business response."""
    business_id: Optional[str] = None
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    name: str
    address: str
    city: str
    state: str
    postal_code: Optional[str] = None
    latitude: float
    longitude: float
    location: LocationPoint
    stars: Optional[float] = None
    review_count: Optional[int] = None
    is_open: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None
    categories: Optional[str] = None
    hours: Optional[Dict[str, str]] = None
    distance: Optional[float] = Field(None, description="Distance in km (for location searches)")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class BusinessSearchByLocation(BaseModel):
    """Query parameters for location-based search."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius: float = Field(default=5.0, ge=0.1, le=100, description="Radius in kilometers")
    limit: int = Field(default=20, ge=1, le=100)


class BusinessSearchByRegion(BaseModel):
    """Query parameters for region-based search."""
    state: str = Field(..., min_length=2, max_length=2, description="Two-letter state code")
    city: Optional[str] = None
    category: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)


# Review Models==

class ReviewCreate(BaseModel):
    """Model for creating a new review."""
    business_id: str
    user_id: str
    stars: float = Field(..., ge=1, le=5)
    text: str
    useful: int = Field(default=0, ge=0)
    funny: int = Field(default=0, ge=0)
    cool: int = Field(default=0, ge=0)
    date: Optional[str] = None


class UserInfo(BaseModel):
    """User information embedded in review response."""
    user_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None


class ReviewResponse(BaseModel):
    """Model for review response."""
    review_id: Optional[str] = None
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    business_id: str
    user_id: str
    stars: float
    useful: int
    funny: int
    cool: int
    text: str
    date: Optional[str] = None
    state: Optional[str] = None
    location: Optional[LocationPoint] = None
    user: Optional[UserInfo] = None  # Populated from $lookup

    model_config = {"populate_by_name": True}


# User Models

class UserCreate(BaseModel):
    """Model for creating a new user."""
    user_id: Optional[str] = None  # Auto-generate if not provided
    name: str
    email: str
    review_count: int = Field(default=0, ge=0)
    yelping_since: Optional[str] = None
    useful: int = Field(default=0, ge=0)
    funny: int = Field(default=0, ge=0)
    cool: int = Field(default=0, ge=0)
    fans: int = Field(default=0, ge=0)
    average_stars: Optional[float] = None


class UserResponse(BaseModel):
    """Model for user response."""
    user_id: str
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    name: str
    email: str
    review_count: Optional[int] = None
    yelping_since: Optional[str] = None
    useful: Optional[int] = None
    funny: Optional[int] = None
    cool: Optional[int] = None
    fans: Optional[int] = None
    average_stars: Optional[float] = None

    model_config = {"populate_by_name": True}


class UserSearch(BaseModel):
    """Query parameters for user search."""
    name: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)


class UserLogin(BaseModel):
    """Model for user login request."""
    user_id: str
    password: str


class LoginResponse(BaseModel):
    """Model for login response."""
    token: str
    user: UserResponse


