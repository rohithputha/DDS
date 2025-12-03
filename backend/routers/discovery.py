
from fastapi import APIRouter
from bson import json_util
import json

from ..database import get_collection, get_database, get_users_collection
from ..config import READ_PREFERENCE


router = APIRouter()


def parse_json(data):
    return json.loads(json_util.dumps(data))


@router.get("/search/location")
def search_by_location(lat: float, long: float, radius_meters: int = 5000):

    businesses = get_collection("businesses", read_preference=READ_PREFERENCE)

    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [long, lat],
                },
                "$maxDistance": radius_meters,
            }
        }
    }

    results = list(businesses.find(query).limit(20))
    return parse_json(results)


@router.get("/business/{business_id}/reviews")
def get_business_reviews(business_id: str):

    db = get_database()
    reviews_col = db["reviews"].with_options(read_preference=READ_PREFERENCE)
    users_col = get_users_collection("users", read_preference=READ_PREFERENCE)

    reviews = list(
        reviews_col.find(
            {"business_id": business_id},
            {"text": 1, "stars": 1, "user_id": 1, "date": 1},
        )
        .sort("date", -1)
        .limit(50)
    )

    if not reviews:
        return []

    user_ids = list({r.get("user_id") for r in reviews if r.get("user_id")})

    users_map = {}
    if user_ids:
        try:
            users = list(
                users_col.find(
                    {"user_id": {"$in": user_ids}},
                    {"user_id": 1, "name": 1},
                )
            )
            users_map = {u["user_id"]: u for u in users}
        except Exception as e:  
            print(f"Error fetching users: {e}")

    enriched_reviews = []
    for r in reviews:
        user = users_map.get(r.get("user_id"))
        review_data = {
            "text": r.get("text"),
            "stars": r.get("stars"),
            "date": r.get("date"),
            "user_details": {
                "name": user.get("name", "Unknown User")
            }
            if user
            else {"name": "Unknown User"},
        }
        enriched_reviews.append(review_data)

    return parse_json(enriched_reviews)


@router.get("/business/{business_id}")
def get_business_details(business_id: str):
    """Get a single business document by `business_id`."""
    businesses = get_collection("businesses", read_preference=READ_PREFERENCE)
    business = businesses.find_one({"business_id": business_id})
    if not business:
        return {}
    return parse_json(business)


