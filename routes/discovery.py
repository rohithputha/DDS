from fastapi import APIRouter
from database import db_read, db_users
from bson import json_util
import json

router = APIRouter()

def parse_json(data):
    return json.loads(json_util.dumps(data))

@router.get("/search/location")
def search_by_location(lat: float, long: float, radius_meters: int = 5000):
    # Maps to the query shown in report [cite: 644]
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [long, lat]
                },
                "$maxDistance": radius_meters
            }
        }
    }
    # Use db_read (Secondary Preferred)
    results = list(db_read.businesses.find(query).limit(20))
    return parse_json(results)

@router.get("/business/{business_id}/reviews")
def get_business_reviews(business_id: str):
    # 1. Fetch reviews from Main DB
    reviews = list(db_read.reviews.find(
        {"business_id": business_id},
        {"text": 1, "stars": 1, "user_id": 1, "date": 1}
    ).sort("date", -1).limit(50)) # Limit to 50 for performance

    if not reviews:
        return []

    # 2. Collect User IDs
    user_ids = list(set([r.get("user_id") for r in reviews if r.get("user_id")]))

    # 3. Fetch User Details from Users Service
    users_map = {}
    if user_ids:
        try:
            users = list(db_users.users.find(
                {"user_id": {"$in": user_ids}},
                {"user_id": 1, "name": 1}
            ))
            users_map = {u["user_id"]: u for u in users}
        except Exception as e:
            print(f"Error fetching users: {e}")
            # Continue without user details if users service fails

    # 4. Merge Data
    enriched_reviews = []
    for r in reviews:
        user = users_map.get(r.get("user_id"))
        review_data = {
            "text": r.get("text"),
            "stars": r.get("stars"),
            "date": r.get("date"),
            "user_details": {"name": user.get("name", "Unknown User")} if user else {"name": "Unknown User"}
        }
        enriched_reviews.append(review_data)

    return parse_json(enriched_reviews)

@router.get("/business/{business_id}")
def get_business_details(business_id: str):
    business = db_read.businesses.find_one({"business_id": business_id})
    if not business:
        return {}
    return parse_json(business)
