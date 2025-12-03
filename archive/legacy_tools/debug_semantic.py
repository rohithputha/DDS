from pymongo import MongoClient
import weaviate
import ollama

def debug_semantic():
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client.yelp_data
    
    lat = 34.426679
    long = -119.711197
    radius = 5000
    
    mongo_query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [long, lat]
                },
                "$maxDistance": radius
            }
        }
    }
    businesses = list(db.businesses.find(mongo_query, {"business_id": 1, "name": 1}).limit(10))
    print(f"Found {len(businesses)} businesses near location.")
    if not businesses:
        return

    business_ids = [b["business_id"] for b in businesses]
    print(f"Sample Business IDs: {business_ids}")

    w_client = weaviate.connect_to_local(port=8080, grpc_port=50051)
    reviews = w_client.collections.get("Review")
    
    print("\nChecking if these businesses have reviews in Weaviate...")
    from weaviate.classes.query import Filter
    
    for bid in business_ids:
        sample = reviews.query.fetch_objects(
            limit=1,
            filters=Filter.by_property("business_id").equal(bid),
            include_vector=True
        )
        if sample.objects:
            obj = sample.objects[0]
            print(f"Business {bid} sample review: {obj.properties['text'][:50]}...")
            if obj.vector:
                vec = obj.vector['default']
                print(f"  Vector length: {len(vec)}")
                print(f"  First 5 elements: {vec[:5]}")
                if all(v == 0 for v in vec):
                    print("  WARNING: VECTOR IS ALL ZEROS!")
            else:
                print("  NO VECTOR FOUND!")
        
        count = reviews.aggregate.over_all(
            filters=Filter.by_property("business_id").equal(bid),
            total_count=True
        ).total_count
        print(f"Business {bid}: {count} reviews")

    print("\nTrying Vector Search for 'good'...")
    response = ollama.embed(model='all-minilm', input='good')
    vector = response['embeddings'][0]
    print(f"Query vector first 5: {vector[:5]}")

    print("Searching Review collection WITHOUT filter...")
    result_no_filter = reviews.query.near_vector(
        near_vector=vector,
        limit=5,
        return_metadata=["distance"]
    )
    print(f"Found {len(result_no_filter.objects)} results (no filter).")
    for obj in result_no_filter.objects:
        print(f"- {obj.properties['text'][:50]}... (Dist: {obj.metadata.distance})")
    
    print("Searching Review collection WITH filter...")
    result = reviews.query.near_vector(
        near_vector=vector,
        limit=5,
        filters=Filter.by_property("business_id").contains_any(business_ids),
        return_metadata=["distance"]
    )
    
    print(f"Found {len(result.objects)} results (with filter).")
    for obj in result.objects:
        print(f"- {obj.properties['text'][:50]}... (Dist: {obj.metadata.distance})")

    w_client.close()
    mongo_client.close()

if __name__ == "__main__":
    debug_semantic()
