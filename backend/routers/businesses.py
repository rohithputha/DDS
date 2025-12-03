
from fastapi import APIRouter, HTTPException, Query
from typing import List
from bson import ObjectId
from bson.errors import InvalidId

from ..database import get_collection
from ..models import (
    BusinessCreate,
    BusinessResponse,
    BusinessSearchByLocation,
    BusinessSearchByRegion,
    LocationPoint
)
from ..utils import validate_state

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("/search/location", response_model=List[BusinessResponse])
async def search_businesses_by_location(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius: float = Query(default=5.0, ge=0.1, le=100, description="Radius in kilometers"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of results")
):
    try:
        collection = get_collection("businesses")
        
        radius_meters = radius * 1000
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "distanceField": "distance",
                    "spherical": True,
                    "maxDistance": radius_meters
                }
            },
            {
                "$addFields": {
                    "distance": {"$divide": ["$distance", 1000]}
                }
            },
            {
                "$limit": limit
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        
        businesses = []
        for doc in results:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
                doc["id"] = doc["_id"]
            businesses.append(BusinessResponse(**doc))
        
        return businesses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching businesses: {str(e)}")


@router.get("/search/region", response_model=List[BusinessResponse])
async def search_businesses_by_region(
    state: str = Query(..., min_length=2, max_length=2, description="Two-letter state code"),
    city: str = Query(None, description="City name (optional)"),
    category: str = Query(None, description="Category filter (optional)"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of results")
):
    try:
        if not validate_state(state):
            raise HTTPException(status_code=400, detail=f"Invalid state code: {state}")
        
        collection = get_collection("businesses")
        
        query = {"state": state.upper()}
        
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        
        if category:
            query["categories"] = {"$regex": category, "$options": "i"}
        cursor = collection.find(query).limit(limit)
        results = list(cursor)
        
        if not results:
            return []
        
        businesses = []
        for doc in results:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
                doc["id"] = doc["_id"]
            businesses.append(BusinessResponse(**doc))
        
        return businesses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching businesses: {str(e)}")


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: str):
    try:
        collection = get_collection("businesses")
        
        business = collection.find_one({"business_id": business_id})
        
        if not business:
            try:
                business = collection.find_one({"_id": ObjectId(business_id)})
            except (InvalidId, ValueError):
                pass
        
        if not business:
            raise HTTPException(status_code=404, detail=f"Business not found: {business_id}")
        
        if "_id" in business:
            business["_id"] = str(business["_id"])
            business["id"] = business["_id"]
        
        return BusinessResponse(**business)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving business: {str(e)}")


@router.post("", response_model=BusinessResponse, status_code=201)
async def create_business(business: BusinessCreate):
    try:
        if not validate_state(business.state):
            raise HTTPException(status_code=400, detail=f"Invalid state code: {business.state}")
        
        collection = get_collection("businesses")
        
        location = LocationPoint(
            type="Point",
            coordinates=[business.longitude, business.latitude]
        )
        
        business_doc = business.model_dump(exclude_none=True)
        business_doc["location"] = location.model_dump()
        
        result = collection.insert_one(business_doc)
        inserted = collection.find_one({"_id": result.inserted_id})
        
        if not inserted:
            raise HTTPException(status_code=500, detail="Failed to retrieve created business")
        
        inserted["_id"] = str(inserted["_id"])
        inserted["id"] = inserted["_id"]
        
        return BusinessResponse(**inserted)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating business: {str(e)}")


