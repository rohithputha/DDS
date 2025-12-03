
from fastapi import APIRouter, HTTPException

from ..database import get_collection
from ..config import READ_PREFERENCE

import weaviate
import ollama


router = APIRouter()


def get_weaviate_client():
    
    return weaviate.connect_to_local(
        port=8080,
        grpc_port=50051,
        headers={},
    )


@router.get("/search/semantic")
def search_semantic(
    query: str,
    lat: float,
    long: float,
    radius_meters: int = 5000,
):
  
    try:
        businesses = get_collection("businesses", read_preference=READ_PREFERENCE)

        mongo_query = {
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

        nearby_businesses = list(
            businesses.find(
                mongo_query,
                {
                    "business_id": 1,
                    "name": 1,
                    "city": 1,
                    "stars": 1,
                    "review_count": 1,
                    "categories": 1,
                    "address": 1,
                },
            )
        )

        if not nearby_businesses:
            return []

        business_ids = [b["business_id"] for b in nearby_businesses]
        business_map = {b["business_id"]: b for b in nearby_businesses}

        try:
            embedding_response = ollama.embed(model="all-minilm", input=query)
            vector = embedding_response["embeddings"][0]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama embedding failed: {str(e)}",
            )

        client = get_weaviate_client()
        try:
            reviews_collection = client.collections.get("Review")
            from weaviate.classes.query import Filter

            response = reviews_collection.query.near_vector(
                near_vector=vector,
                limit=20,
                filters=Filter.by_property("business_id").contains_any(business_ids),
                return_metadata=["distance"],
            )

            results = []
            for obj in response.objects:
                review_data = obj.properties
                bid = review_data.get("business_id")

                business_info = business_map.get(bid, {})

                results.append(
                    {
                        "review_text": review_data.get("text"),
                        "business_name": business_info.get("name"),
                        "business_city": business_info.get("city"),
                        "business_stars": business_info.get("stars"),
                        "business_review_count": business_info.get("review_count"),
                        "business_categories": business_info.get("categories"),
                        "business_id": bid,
                        "score": obj.metadata.distance,
                    }
                )

            return results

        finally:
            client.close()

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


