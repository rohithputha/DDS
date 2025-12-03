
from fastapi import APIRouter, HTTPException, Query, Header
from typing import List, Optional
from datetime import datetime
from pymongo import WriteConcern
from pymongo.errors import PyMongoError

from ..database import get_collection, get_database, get_users_collection
from ..models import ReviewCreate, ReviewResponse, LocationPoint
from ..config import WRITE_CONCERN
from ..auth import get_current_user_optional

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/business/{business_id}", response_model=List[ReviewResponse])
async def get_reviews_by_business(
    business_id: str,
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(default=0, ge=0, description="Number of results to skip")
):
    try:
        reviews_collection = get_collection("reviews")
        users_collection = get_users_collection("users")
        
        cursor = reviews_collection.find({"business_id": business_id})
        cursor = cursor.sort("date", -1).skip(offset).limit(limit)
        reviews = list(cursor)
        
        if not reviews:
            return []
            
        user_ids = list({r.get("user_id") for r in reviews if r.get("user_id")})
        
        users_map = {}
        if user_ids:
            try:
                users = list(users_collection.find(
                    {"user_id": {"$in": user_ids}},
                    {"user_id": 1, "name": 1, "email": 1}
                ))
                users_map = {u["user_id"]: u for u in users}
            except Exception as e:
                print(f"Error fetching users: {e}")
        
        results = []
        for r in reviews:
            user = users_map.get(r.get("user_id"))
            
            user_data = {
                "user_id": r.get("user_id"),
                "name": "Unknown User",
                "email": None
            }
            
            if user:
                user_data["name"] = user.get("name", "Unknown User")
                user_data["email"] = user.get("email")
            
            r["user"] = user_data
            
            if "_id" in r:
                r["_id"] = str(r["_id"])
                r["id"] = r["_id"]
                
            results.append(ReviewResponse(**r))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving reviews: {str(e)}")


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    review: ReviewCreate,
    authorization: Optional[str] = Header(None)
):

    try:
        current_user = await get_current_user_optional(authorization)
        if current_user and current_user.user_id != review.user_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot create review for different user"
            )
        
        db = get_database()
        reviews_collection = get_collection("reviews")
        businesses_collection = get_collection("businesses")
        
        # Verify business exists
        business = businesses_collection.find_one({"business_id": review.business_id})
        if not business:
            raise HTTPException(status_code=404, detail=f"Business not found: {review.business_id}")
        
        # Verify user exists in users cluster
        users_collection = get_users_collection("users")
        user = users_collection.find_one({"user_id": review.user_id})
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {review.user_id}")
        
        # Prepare review document
        review_doc = review.model_dump(exclude_none=True)
        
        if "state" in business:
            review_doc["state"] = business["state"]
        if "location" in business:
            review_doc["location"] = business["location"]
        
        if not review_doc.get("date"):
            review_doc["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        client = db.client
        result = None
        with client.start_session() as session:
            with session.start_transaction(write_concern=WRITE_CONCERN):
                try:
                    # Insert review
                    result = reviews_collection.insert_one(review_doc, session=session)
                    
                    # Calculate new business aggregates
                    current_review_count = business.get("review_count", 0)
                    current_stars = business.get("stars", 0.0)
                    
                    new_review_count = current_review_count + 1
                    new_average_stars = ((current_stars * current_review_count) + review.stars) / new_review_count
                    
                    # Update business aggregates
                    businesses_collection.update_one(
                        {"business_id": review.business_id},
                        {
                            "$set": {
                                "review_count": new_review_count,
                                "stars": round(new_average_stars, 2)
                            }
                        },
                        session=session
                    )
                    
                    session.commit_transaction()
                    
                except PyMongoError as e:
                    session.abort_transaction()
                    raise HTTPException(
                        status_code=500,
                        detail=f"Transaction failed: {str(e)}"
                    )
        
        try:
            current_user_review_count = user.get("review_count", 0)
            users_collection.update_one(
                {"user_id": review.user_id},
                {
                    "$set": {
                        "review_count": current_user_review_count + 1
                    }
                }
            )
        except Exception as e:
            print(f"Warning: Failed to update user review_count: {str(e)}")
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create review")
        
        inserted = reviews_collection.find_one({"_id": result.inserted_id})
        
        if not inserted:
            raise HTTPException(status_code=500, detail="Failed to retrieve created review")
        
        inserted["_id"] = str(inserted["_id"])
        inserted["id"] = inserted["_id"]
        
        return ReviewResponse(**inserted)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating review: {str(e)}")


