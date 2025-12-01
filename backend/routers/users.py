"""
User endpoints for the FastAPI application.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
import uuid

from ..database import get_collection
from ..models import UserCreate, UserResponse, UserSearch

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a single user by ID."""
    try:
        collection = get_collection("users")
        
        user = collection.find_one({"user_id": user_id})
        
        if not user:
            try:
                user = collection.find_one({"_id": ObjectId(user_id)})
            except (InvalidId, ValueError):
                pass
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_id}")
        
        if "_id" in user:
            user["_id"] = str(user["_id"])
            user["id"] = user["_id"]
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")


@router.get("/search", response_model=List[UserResponse])
async def search_users(
    name: str = Query(None, description="Name to search for (optional)"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of results")
):
    """Search for users by name using case-insensitive regex."""
    try:
        collection = get_collection("users")
        
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        
        cursor = collection.find(query).limit(limit)
        results = list(cursor)
        
        if not results:
            return []
        
        users = []
        for doc in results:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
                doc["id"] = doc["_id"]
            users.append(UserResponse(**doc))
        
        return users
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching users: {str(e)}")


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Create a new user. Auto-generates user_id if not provided."""
    try:
        collection = get_collection("users")
        
        user_doc = user.model_dump(exclude_none=True)
        
        if not user_doc.get("user_id"):
            user_doc["user_id"] = str(uuid.uuid4()).replace("-", "")[:22]
        
        existing = collection.find_one({"user_id": user_doc["user_id"]})
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"User with user_id '{user_doc['user_id']}' already exists"
            )
        
        result = collection.insert_one(user_doc)
        inserted = collection.find_one({"_id": result.inserted_id})
        
        if not inserted:
            raise HTTPException(status_code=500, detail="Failed to retrieve created user")
        
        inserted["_id"] = str(inserted["_id"])
        inserted["id"] = inserted["_id"]
        
        return UserResponse(**inserted)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

